# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-08-24

First public release, prepared from the internal development repository.

### Added

- Claude Code plugin packaging: `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`, so the repository can be installed with
  `/plugin marketplace add PHES-ODM/PHES-ODM-General-Skill`.
- `scripts/check_skill_refs.py`, which resolves every ODM identifier named in
  `SKILL.md` against the bundled LinkML schemas, verifies each `class.slot`
  reference, and checks that the skill frontmatter and both plugin manifests
  agree. Wired into GitHub Actions on every push and pull request.
- `skills/phes-odm-general/references/README.md` documenting what each bundled
  schema contains, how to read a LinkML class entry, and how the schemas are
  regenerated.
- Skill guidance on **measure sets and replicates**: replicates, dilution
  series, and variants are grouped with `measureSetRepID`, never with
  `datasetID`. This addresses the QPCR pipeline problem recorded in
  [docs/PROBLEMS.md](docs/PROBLEMS.md).
- Skill guidance on **missingness**: recommend a `genMissingnessSet` value
  instead of leaving an optional cell blank.
- Skill documentation for the MCP's `get_version` tool, and instructions to
  fall back to the bundled schemas — and say so — when the MCP is unavailable.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE` (CC BY 4.0), GitHub issue
  and pull request templates, and this changelog.

### Changed

- Renamed the skill from `phes-odm` to `phes-odm-general` and moved it to
  `skills/phes-odm-general/`.
- Corrected the `odm-map` documentation, which described a command line the
  tool does not accept. The Mapper takes
  `--module <module> --output-dir <dir> <input>...`, not
  `--input/--from/--to/--output`, and its modules are `odm-v1-to-v3`,
  `nwss-reporting-to-v3`, `pha4ge-to-v3`, and `odm-v3-wide-to-long` — all of
  which target ODM v3. There is no built-in module producing ODM v2.
- Corrected and expanded the `odm-validate` documentation: the supported
  versions are `2.0.0`, `2.1.0`, `2.2.3`, and `3.0.1` (default `3.0.1`), the
  `--out`, `--format`, and `--verbosity` options are documented, and the skill
  now explains that tables are identified **by file name**, so example and
  input files must be named after their table.
- Made the validation requirement self-consistent: the mandatory pre-output
  validation step now passes `--version`, matching the documented command.
- Moved `TASK.md` and `PROBLEMS.md` into `docs/`.
- Rewrote `README.md` for a public audience: install as a plugin or as a plain
  skill, prerequisites with working install commands, and the file-naming rules
  that make `odm-validate` and `odm-map` work.

[Unreleased]: https://github.com/PHES-ODM/PHES-ODM-General-Skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PHES-ODM/PHES-ODM-General-Skill/releases/tag/v1.0.0
