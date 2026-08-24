#!/usr/bin/env python3
"""Check that everything SKILL.md claims about the ODM is actually true.

The recurring failure mode for this skill has been *plausible but wrong*
identifiers: a table, column, or enumeration value that reads like real ODM but
does not exist in the schema. A reader cannot tell the difference, and neither
can the model that later repeats it. This script closes that gap by resolving
every ODM identifier mentioned in ``SKILL.md`` against the bundled LinkML
schemas, and failing the build when one does not resolve.

It performs four checks:

1. **Repository layout** — the files a Claude Code skill/plugin repository needs
   are present.
2. **Manifest consistency** — the skill's frontmatter ``name``, its directory
   name, ``plugin.json``, and ``marketplace.json`` all agree.
3. **Dotted references** — every ``class.slot`` reference in SKILL.md (e.g.
   ``samples.siteID``) names a real class that really has that slot.
4. **Bare identifiers** — every remaining backticked token that looks like an
   ODM identifier resolves to a class, slot, enumeration, or enumeration value
   in at least one bundled schema.

Run from the repository root::

    python scripts/check_skill_refs.py

Exits 0 when every check passes, 1 otherwise. The only third-party dependency
is PyYAML.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a data problem
    sys.exit("PyYAML is required: pip install pyyaml")


# --- Repository paths -------------------------------------------------------
#
# Everything is resolved relative to this file so the script works from any
# working directory (CI checks it out anywhere).

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "phes-odm-general"
SKILL_DIR = REPO_ROOT / "skills" / SKILL_NAME
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"

# Schemas are keyed by the ODM version they describe, so error messages can say
# *which* versions an identifier was found in (or missing from).
SCHEMA_FILES = {
    "v1": REFERENCES_DIR / "odm_v1.yaml",
    "v2": REFERENCES_DIR / "odm_v2.yaml",
    "v3": REFERENCES_DIR / "odm_v3.yaml",
}

# Files that must exist for this to be a usable public skill repository.
REQUIRED_FILES = [
    Path("README.md"),
    Path("LICENSE"),
    Path("CONTRIBUTING.md"),
    Path("CODE_OF_CONDUCT.md"),
    Path("CHANGELOG.md"),
    Path(".gitignore"),
    Path(".claude-plugin/plugin.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("skills") / SKILL_NAME / "SKILL.md",
    Path("skills") / SKILL_NAME / "references" / "README.md",
]


# --- Tokens that are not ODM identifiers ------------------------------------
#
# SKILL.md legitimately backticks plenty of things that are not parts of the
# data model. Listing them explicitly (rather than loosening the identifier
# pattern) keeps the check strict: anything new and unrecognized is reported
# rather than silently ignored.

NON_ODM_TOKENS = {
    # CLI executables and MCP tool names.
    "odm-validate",
    "odm-map",
    "search_odm_parts",
    "get_class_slots",
    "get_enum_values",
    "list_part_types",
    "get_version",
    # MCP / LinkML keys quoted when explaining a tool response.
    "part_types",
    "top_n",
    "id",
    "slot_usage",
    "permissible_values",
    "identifier",
    "required",
    "pattern",
    "range",
    "title",
    "description",
    # Source-format and file-name literals used by odm-map.
    "nwss",
    "PHA4GE",
    "odm_wide",
    # Report/data formats and file extensions.
    "csv",
    "tsv",
    "txt",
    "json",
    "yaml",
    "xlsx",
}

# File extensions that make a dotted token a file name (`samples.csv`) rather
# than a `class.slot` reference. SKILL.md uses both shapes, and only the second
# is a claim about the schema.
FILE_EXTENSIONS = {"csv", "tsv", "txt", "json", "yaml", "yml", "xlsx", "md", "pdf"}

# An ODM identifier is camelCase or lowercase alphanumerics: no underscores,
# hyphens, dots, spaces, or angle brackets. Tokens failing this pattern are
# commands, paths, flags, placeholders, or version numbers, and are skipped.
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")

# Inline code spans: `like this`. Fenced blocks are stripped before matching so
# shell examples do not contribute tokens.
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
FENCED_BLOCK_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)

# A `class.slot` reference, e.g. `samples.siteID`.
DOTTED_REF_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)\.([A-Za-z][A-Za-z0-9]*)$")


@dataclass
class Schema:
    """The parts of one LinkML schema this checker needs.

    ``class_slots`` maps each class to its own column list, which is what makes
    the dotted-reference check possible: a slot existing *somewhere* in the ODM
    does not mean it exists on the table SKILL.md attached it to.
    """

    version: str
    classes: set[str] = field(default_factory=set)
    slots: set[str] = field(default_factory=set)
    enums: set[str] = field(default_factory=set)
    enum_values: set[str] = field(default_factory=set)
    class_slots: dict[str, set[str]] = field(default_factory=dict)

    def knows(self, name: str) -> bool:
        """True if ``name`` is any kind of part in this schema."""
        return (
            name in self.classes
            or name in self.slots
            or name in self.enums
            or name in self.enum_values
        )


def load_schema(version: str, path: Path) -> Schema:
    """Parse one LinkML YAML file into a :class:`Schema`."""
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    schema = Schema(version=version)
    schema.slots = set(raw.get("slots") or {})

    for enum_name, enum_def in (raw.get("enums") or {}).items():
        schema.enums.add(enum_name)
        schema.enum_values.update((enum_def or {}).get("permissible_values") or {})

    for class_name, class_def in (raw.get("classes") or {}).items():
        schema.classes.add(class_name)
        class_def = class_def or {}
        # `slots` is the column list; `slot_usage` carries the per-class
        # overrides. A class can constrain a slot it lists, so union both.
        own_slots = set(class_def.get("slots") or [])
        own_slots.update(class_def.get("slot_usage") or {})
        schema.class_slots[class_name] = own_slots
        # Slots declared only inside a class still count as real slots.
        schema.slots.update(own_slots)

    return schema


def read_skill_body(path: Path) -> tuple[dict[str, str], str]:
    """Split SKILL.md into its YAML frontmatter and its Markdown body.

    Frontmatter is parsed with a plain YAML load rather than by hand so a
    multi-line ``description`` behaves the way Claude Code will read it.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} does not start with YAML frontmatter")
    _, frontmatter_text, body = text.split("---\n", 2)
    frontmatter = yaml.safe_load(frontmatter_text) or {}
    return frontmatter, body


def extract_code_tokens(body: str) -> list[str]:
    """Return the inline-code tokens in ``body``, fenced blocks excluded.

    Fenced blocks hold shell transcripts and ASCII diagrams whose words are not
    claims about the schema, so removing them first avoids a pile of false
    positives that would only be silenced by growing the ignore list.
    """
    prose = FENCED_BLOCK_RE.sub("", body)
    return [match.group(1).strip() for match in INLINE_CODE_RE.finditer(prose)]


def check_layout(problems: list[str]) -> None:
    """Check 1 — the repository has the files a skill repo needs."""
    for relative in REQUIRED_FILES:
        if not (REPO_ROOT / relative).exists():
            problems.append(f"missing required file: {relative}")


def check_manifests(frontmatter: dict[str, str], problems: list[str]) -> None:
    """Check 2 — skill frontmatter and plugin manifests name the same skill."""
    import json

    name = frontmatter.get("name")
    if name != SKILL_NAME:
        problems.append(
            f"SKILL.md frontmatter name is {name!r}, "
            f"but the skill directory is {SKILL_NAME!r}"
        )
    if not frontmatter.get("description"):
        problems.append("SKILL.md frontmatter has no description")

    plugin_path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    if not (plugin_path.exists() and marketplace_path.exists()):
        return  # already reported by check_layout

    plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

    if plugin.get("name") != SKILL_NAME:
        problems.append(
            f"plugin.json name is {plugin.get('name')!r}, expected {SKILL_NAME!r}"
        )

    listed = {entry.get("name") for entry in marketplace.get("plugins") or []}
    if plugin.get("name") not in listed:
        problems.append(
            f"marketplace.json does not list the plugin {plugin.get('name')!r} "
            f"(lists: {sorted(listed)})"
        )

    for entry in marketplace.get("plugins") or []:
        if entry.get("name") == plugin.get("name") and entry.get(
            "version"
        ) != plugin.get("version"):
            problems.append(
                f"version mismatch: plugin.json {plugin.get('version')!r} vs "
                f"marketplace.json {entry.get('version')!r}"
            )


def check_references(
    tokens: list[str], schemas: dict[str, Schema], problems: list[str]
) -> int:
    """Checks 3 and 4 — resolve every ODM identifier against the schemas.

    Returns the number of tokens that were actually resolved, so the summary
    can distinguish "everything passed" from "nothing was checked" — a silently
    empty check would be indistinguishable from a clean run.
    """
    resolved = 0
    for token in dict.fromkeys(tokens):  # de-duplicate, keep document order
        if token in NON_ODM_TOKENS:
            continue

        # Check 3: `class.slot` must name a real slot on that real class.
        dotted = DOTTED_REF_RE.match(token)
        if dotted:
            class_name, slot_name = dotted.groups()
            if slot_name.lower() in FILE_EXTENSIONS:
                continue  # a file name such as `samples.csv`, not a slot
            hosts = [
                version
                for version, schema in schemas.items()
                if slot_name in schema.class_slots.get(class_name, set())
            ]
            if hosts:
                resolved += 1
            elif any(class_name in schema.classes for schema in schemas.values()):
                problems.append(
                    f"`{token}`: class {class_name!r} exists but has no slot "
                    f"{slot_name!r} in any bundled schema"
                )
            else:
                problems.append(f"`{token}`: no class named {class_name!r}")
            continue

        # Check 4: a bare identifier must be a part somewhere.
        if not IDENTIFIER_RE.match(token):
            continue  # a command, path, flag, placeholder, or version number

        if any(schema.knows(token) for schema in schemas.values()):
            resolved += 1
        else:
            problems.append(
                f"`{token}`: not a class, slot, enum, or enum value in any "
                f"bundled ODM schema (add it to NON_ODM_TOKENS if it is not "
                f"meant to be an ODM identifier)"
            )

    return resolved


def main() -> int:
    problems: list[str] = []

    check_layout(problems)

    missing_schemas = [str(p) for p in SCHEMA_FILES.values() if not p.exists()]
    if missing_schemas:
        problems.append(f"missing schema files: {', '.join(missing_schemas)}")
        _report(problems, 0)
        return 1

    schemas = {v: load_schema(v, p) for v, p in SCHEMA_FILES.items()}
    frontmatter, body = read_skill_body(SKILL_MD)

    check_manifests(frontmatter, problems)
    resolved = check_references(extract_code_tokens(body), schemas, problems)

    _report(problems, resolved)
    return 1 if problems else 0


def _report(problems: list[str], resolved: int) -> None:
    """Print the outcome in a shape that is readable in CI logs."""
    if problems:
        print(f"FAIL — {len(problems)} problem(s):\n")
        for problem in problems:
            print(f"  - {problem}")
        print()
    else:
        print(f"OK — {resolved} ODM identifier(s) in SKILL.md resolved cleanly.")


if __name__ == "__main__":
    sys.exit(main())
