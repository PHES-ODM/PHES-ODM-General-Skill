# <img src="docs/img/ODM-logo.png" align="right" alt="" width="180"/> PHES-ODM General Skill

A [Claude Code](https://claude.com/claude-code) skill that makes Claude an
expert in the [Public Health Environmental Surveillance Open Data Model
(PHES-ODM)](https://docs.phes-odm.org). Ask it to look up ODM parts, onboard a
new team member, walk you through populating a table, validate a data file, or
map data from another surveillance format into ODM.

The skill is called **`phes-odm-general`** — the general-purpose ODM assistant,
as distinct from the task-specific ODM skills in the PHES-ODM organization.

---

## Contents

```text
PHES-ODM-General-Skill/
├── skills/
│   └── phes-odm-general/
│       ├── SKILL.md              # The skill itself: workflows and constraints
│       └── references/
│           ├── README.md         # What each reference file is and where it came from
│           ├── odm_v3.yaml       # LinkML schema for ODM v3
│           ├── odm_v2.yaml       # LinkML schema for ODM v2
│           ├── odm_v1.yaml       # LinkML schema for ODM v1 (legacy)
│           └── PHES-ODM-v3-Manuscript.pdf
├── .claude-plugin/
│   ├── plugin.json               # Claude Code plugin manifest
│   └── marketplace.json          # Marketplace listing, so the repo installs as a plugin
├── scripts/
│   └── check_skill_refs.py       # CI check: every ODM name in SKILL.md really exists
├── docs/
│   ├── TASK.md                   # Original project specification
│   └── PROBLEMS.md               # Log of problems found in use, and their fixes
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
```

---

## What the skill does

| Capability | What you get |
| --- | --- |
| **Look up ODM parts** | Search slots (columns), classes (tables), enumerations, and permissible values through the phes-odm-search MCP |
| **Onboard new users** | An explanation of the ODM, its versions, long vs. wide format, and the core `sites → samples → measures` flow |
| **Populate tables** | Step-by-step guidance for any ODM table: required vs. optional columns, formats, valid values, foreign keys, and a worked example |
| **Validate data** | Runs `odm-validate` over your CSV/Excel files and translates each error into a concrete fix |
| **Map other formats** | Runs `odm-map` to convert NWSS Reporting, PHA4GE, ODM v1, or ODM wide format into ODM v3 |

The focus is **ODM v2 and v3**. ODM v1 is legacy and is only discussed when you
explicitly ask about it.

Two rules are built into the skill and are worth knowing about, because they
are what keep its answers trustworthy:

- **Every example is validated before you see it.** The skill writes example
  data to a temporary file, runs `odm-validate` on it, and fixes it silently
  until it passes. Wide-format examples are the one exception, because
  `odm-validate` does not support wide tables.
- **Every ODM name is looked up, never recalled.** Table, column, and
  enumeration names come from the MCP or the bundled schemas — not from the
  model's memory — including in suggestions and hypotheticals. If a search
  finds nothing, the skill says so rather than inventing a plausible name.

---

## Installation

### Option A — as a plugin (recommended)

In Claude Code, add this repository as a plugin marketplace and install from
it:

```console
/plugin marketplace add PHES-ODM/PHES-ODM-General-Skill
/plugin install phes-odm-general@phes-odm
```

Updating later is `/plugin marketplace update phes-odm`.

### Option B — as a plain skill

Copy the skill directory into your skills folder — `~/.claude/skills/` to have
it available everywhere, or `.claude/skills/` inside a project to scope it to
that project:

```console
git clone https://github.com/PHES-ODM/PHES-ODM-General-Skill.git
cp -r PHES-ODM-General-Skill/skills/phes-odm-general ~/.claude/skills/
```

To track updates instead of copying, symlink it:

```console
ln -s "$(pwd)/PHES-ODM-General-Skill/skills/phes-odm-general" ~/.claude/skills/phes-odm-general
```

Either way, start a new Claude Code session afterwards — skills are discovered
at startup — and type `/phes-odm-general` to confirm it is available.

---

## Prerequisites

The skill works without any of these — it falls back to the bundled schemas and
says so — but it is far more useful with them installed.

### Required for lookups: phes-odm-search MCP

The [PHES-ODM Search MCP](https://github.com/PHES-ODM/PHES-ODM-Search-MCP)
provides embedding-based search over the ODM data dictionary. Install it, then
register it with Claude Code:

```console
claude mcp add phes-odm-search \
  --transport stdio \
  --env ODM_STORE=/absolute/path/to/PHES-ODM-Search-MCP/embeddings \
  -- /absolute/path/to/python3 -m odm_search_mcp.server
```

Claude Code does not pass a working directory to the server process, so
`ODM_STORE` must be an absolute path. Add `--scope project` to write the entry
to a shared `.mcp.json` instead of your personal config. See the [Search MCP
README](https://github.com/PHES-ODM/PHES-ODM-Search-MCP#readme) for the full
setup, including Claude Desktop and HTTP transport.

### Required for validation: odm-validate

[PHES-ODM-Validation](https://github.com/PHES-ODM/PHES-ODM-Validation) provides
the `odm-validate` command:

```console
pip install git+https://github.com/PHES-ODM/PHES-ODM-Validation.git
```

Supported ODM versions are `2.0.0`, `2.1.0`, `2.2.3`, and `3.0.1`.

### Required for mapping: odm-map

[PHES-ODM-Mapper](https://github.com/PHES-ODM/PHES-ODM-Mapper) provides the
`odm-map` command:

```console
pip install git+https://github.com/PHES-ODM/PHES-ODM-Mapper.git
```

> **Note:** the Mapper repository may be private, and it currently depends on
> LinkML-Map features that have not yet been released. Contact
> [phes_odm@ohri.ca](mailto:phes_odm@ohri.ca) if the install fails.

---

## Usage

Ask in plain language — the skill triggers on any ODM question — or invoke it
explicitly with `/phes-odm-general`:

```text
/phes-odm-general What is the collDT slot?
/phes-odm-general How do I populate the samples table?
/phes-odm-general What are the valid values for collType?
/phes-odm-general Validate wastewater-2026-q1.csv against ODM v3
/phes-odm-general Map this NWSS file to ODM v3
/phes-odm-general I'm new to the ODM, give me an overview
```

Two things make the answers work better:

- **Name your data files after their ODM tables** (`samples.csv`,
  `measures.csv`, or sheet tabs named the same way in an Excel workbook). Both
  `odm-validate` and `odm-map` identify tables by file name and will not
  recognize a file called `export_final.csv`.
- **Pass related tables together** when validating, so cross-table checks such
  as foreign keys can actually run.

---

## Development

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the
workflow, and [docs/PROBLEMS.md](docs/PROBLEMS.md) for problems found in real
use and how they were addressed.

The one check to know about: after editing `SKILL.md`, run

```console
pip install pyyaml
python scripts/check_skill_refs.py
```

It resolves every ODM identifier named in `SKILL.md` against the bundled LinkML
schemas and fails on anything that does not exist. This repository's most
common defect has been a plausible-sounding table or column name that the ODM
does not actually have; the checker is what catches it. It runs on every push
and pull request via [GitHub Actions](.github/workflows/checks.yml).

---

## Related repositories

| Repository | Purpose |
| --- | --- |
| [PHES-ODM-Search-MCP](https://github.com/PHES-ODM/PHES-ODM-Search-MCP) | MCP server for querying the ODM data dictionary |
| [PHES-ODM-Validation](https://github.com/PHES-ODM/PHES-ODM-Validation) | Validates data files against the ODM schema |
| [PHES-ODM-Mapper](https://github.com/PHES-ODM/PHES-ODM-Mapper) | Maps NWSS, PHA4GE, ODM v1, and ODM wide format into ODM v3 |
| [PHES-ODM-LinkMLGenerator](https://github.com/PHES-ODM/PHES-ODM-LinkMLGenerator) | Generates the LinkML schemas bundled in `references/` |
| [PHES-ODM-Doc](https://github.com/PHES-ODM/PHES-ODM-Doc) | Source for the documentation at docs.phes-odm.org |

---

## Documentation and support

- Full ODM documentation: <https://docs.phes-odm.org>
- Community discussion board: <https://odm.discourse.group>
- Questions about this repository: [phes_odm@ohri.ca](mailto:phes_odm@ohri.ca)

## License

Released under [CC BY 4.0](LICENSE). Copyright (c) 2026 Ottawa Hospital
Research Institute.
