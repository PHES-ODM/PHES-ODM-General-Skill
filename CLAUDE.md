# PHES-ODM General Skill — project instructions

This repository *is* the `phes-odm-general` skill. Editing it means editing a
prompt that Claude will later follow, so the working rules below apply to any
session in this directory.

**At the start of every conversation, invoke the `phes-odm-general` skill via
the Skill tool before doing anything else.** The skill must be loaded so that
the session stays in sync with the current `SKILL.md` — otherwise you are
reasoning about a version of the skill that no longer exists.

If the skill is not installed locally, symlink it first:

```console
ln -s "$(pwd)/skills/phes-odm-general" ~/.claude/skills/phes-odm-general
```

## Layout

| Path | What it is |
| --- | --- |
| `skills/phes-odm-general/SKILL.md` | The skill: workflows, tool docs, constraints |
| `skills/phes-odm-general/references/` | Bundled LinkML schemas and the v3 manuscript, read on demand |
| `scripts/check_skill_refs.py` | Verifies every ODM name in `SKILL.md` against the schemas |
| `.claude-plugin/` | Plugin and marketplace manifests |
| `docs/` | Original spec (`TASK.md`) and the log of real-use problems (`PROBLEMS.md`) |

## Rules for changes here

1. **Never write an ODM name you have not verified.** Look up every table,
   column, and enumeration value with the phes-odm-search MCP, or find it in
   `references/odm_v3.yaml`. Plausible-but-wrong identifiers are this
   repository's recurring defect.
2. **Run the checker after touching `SKILL.md`:**
   `python scripts/check_skill_refs.py`. It must pass before the change is
   done.
3. **Validate example data** with `odm-validate` before it goes into any file,
   the same rule the skill itself follows. Wide-format examples cannot be
   validated.
4. **Verify tool documentation against the tool**, not from memory. The
   `odm-validate` and `odm-map` command lines documented in `SKILL.md` were
   both wrong once because they were written from assumption.
5. **Record changes** in `CHANGELOG.md` under `[Unreleased]`, and update
   `docs/PROBLEMS.md` when a change fixes a problem logged there.
6. Keep Markdown wrapped at 80 columns and lint-clean per `.markdownlint.json`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow.
