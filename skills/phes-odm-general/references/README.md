# Reference files

Bundled reference material that [`../SKILL.md`](../SKILL.md) points Claude at.
These files are read **on demand** — none of them is loaded into context unless
the model decides it needs them — so their size is not a cost on every turn.

The skill still prefers the [phes-odm-search
MCP](https://github.com/PHES-ODM/PHES-ODM-Search-MCP) for interactive lookups.
These files are the fallback when the MCP is unavailable, and the source of
truth for details the MCP does not expose (such as the full YAML definition of
a class, or the design rationale behind ODM v3).

## Contents

| File | Size | Description |
| --- | --- | --- |
| `odm_v3.yaml` | ~840 KB | LinkML schema for ODM v3 — 27 classes, 295 slots, 181 enumerations, 3,620 permissible values |
| `odm_v2.yaml` | ~540 KB | LinkML schema for ODM v2 — 23 classes, 254 slots, 138 enumerations, 2,216 permissible values |
| `odm_v1.yaml` | ~60 KB | LinkML schema for ODM v1 (legacy) — 12 classes, 107 slots, 18 enumerations, 171 permissible values |
| `PHES-ODM-v3-Manuscript.pdf` | ~1.6 MB | Review paper describing ODM v3: rationale for new fields, design decisions, and changes from v2 |

## Reading the schemas

Each YAML file is a standard [LinkML](https://linkml.io/) schema. The parts of
it the skill cares about:

| Key | What it holds |
| --- | --- |
| `classes` | ODM tables, keyed by table name (`samples`, `measures`, `sites`, …) |
| `classes.<name>.slots` | The column list for that table, in schema order |
| `classes.<name>.slot_usage.<slot>` | Per-table detail for a column: `description`, `title`, `required`, `identifier`, `pattern`, `range` / `any_of` |
| `slots` | Global slot declarations shared across tables |
| `enums.<name>.permissible_values` | Controlled vocabularies, each value with a `title` and `description` |

Because a slot's `required` flag and range are set **per class** in
`slot_usage`, always read the class entry rather than the global `slots` entry
when answering "is this column required?".

These files are large enough that reading one whole is wasteful. Grep for the
class or slot name and read the surrounding lines instead:

```console
grep -n "^  samples:" -A 40 odm_v3.yaml
```

## Provenance and updating

The three YAML schemas are generated from the ODM Excel data dictionaries by
the [PHES-ODM
LinkMLGenerator](https://github.com/PHES-ODM/PHES-ODM-LinkMLGenerator). They
are **generated artifacts — do not hand-edit them.** To pick up a new ODM
release, regenerate the schema with that tool and copy the result here, then
run the reference checker from the repository root:

```console
python scripts/check_skill_refs.py
```

The checker confirms that every ODM identifier named in `SKILL.md` still exists
in these schemas, which is what catches a table or slot that a new ODM release
renamed or removed.

The schema IDs (`https://onto.phes-odm.org/odm/v3` and the v1/v2 equivalents)
identify which ODM version each file describes.

The manuscript PDF is a static reference copy and does not need regenerating.
