## What this changes

<!-- What will a user now get that they did not get before? -->

## Why

<!-- Link an issue, or describe the problem this fixes. If it fixes something
     recorded in docs/PROBLEMS.md, say which entry. -->

## Checklist

- [ ] Every ODM table, column, and enumeration value I added was looked up in
      the phes-odm-search MCP or the bundled schemas — none written from memory
- [ ] Any example data was validated with `odm-validate` (wide-format examples
      excepted, since the validator does not support them)
- [ ] `python scripts/check_skill_refs.py` passes
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] `docs/PROBLEMS.md` updated, if this fixes a problem logged there
