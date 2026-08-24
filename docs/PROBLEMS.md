# Problems found in use

Cases where the skill gave wrong or misleading guidance in real work, and what
was done about them. Entries stay here after they are fixed — a record of a
failure that testing did not catch is worth more than a clean page.

To add one, describe what you asked, what the skill did, and what it should
have done. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Fixed

### Replicates grouped by `datasetID` instead of `measureSetRepID`

**Found in:** PHES-ODM-QPCR-Pipeline, while writing the spec for populating the
ODM from raw qPCR instrument output.

**What happened:** the skill grouped raw replicate measurements by `datasetID`.
`datasetID` identifies the dataset a row was published in — the whole
collection — so replicates from one qPCR run ended up indistinguishable from
every other row in the same dataset.

**What it should have done:** group them with `measureSetRepID`, adding one row
per set to the `measureSets` table. Measure sets are exactly what the ODM
provides for replicates, dilution series used to build a Ct curve, and variants
identified in a single sample.

**Fix:** `SKILL.md` gained a "Measure Sets, Replicates, and IDs" section
stating this explicitly, including that `datasetID` is not a grouping
mechanism, and that `index` orders replicates *within* a set rather than
defining the set. The table population order was also corrected so
`measureSets` is populated before `measures`, which is the order the foreign
key requires.

### `odm-map` documented with a command line it does not accept

**What happened:** `SKILL.md` documented
`odm-map --input <file> --from <format> --to v3 --output <file>` with source
formats `nwss`, `pha4ge`, `odmv1`, `odmv2-wide`, `odmv3-wide`. None of those
flags or format names exist. Any user following that guidance got an error.

**Fix:** the documentation was rewritten from the Mapper's own reference. The
real shape is
`odm-map --module <module> --output-dir <dir> <input>...`, the modules are
`odm-v1-to-v3`, `nwss-reporting-to-v3`, `pha4ge-to-v3`, and
`odm-v3-wide-to-long`, and all of them target ODM v3 — there is no built-in
module producing ODM v2. `SKILL.md` also now records that the Mapper matches
input files to source tables by file name.

## Open

None currently.
