---
name: phes-odm-general
description: Use this skill when the user asks about the PHES-ODM (Public Health Environmental Surveillance Open Data Model), ODM tables or slots, wastewater surveillance data, how to populate ODM tables, how to validate ODM data files, how to map data to ODM format, needs onboarding to the ODM, or asks for an introduction or examples of any ODM table or concept. Trigger phrases include "ODM", "PHES-ODM", "wastewater data model", "populate the samples table", "introduction to", "show me an example", "how do I fill in", "validate my ODM file", "map to ODM", or any question about ODM slots, classes, or enumerations.
user-invocable: true
argument-hint: <question or request about the ODM>
---

# PHES-ODM Skill

## REQUIRED: Validate All Examples Before Output

**Before displaying any ODM example data to the user, you MUST:**

1. Write the example to a temporary CSV file — one file per table, named
   **exactly after the table** (e.g. `/tmp/odm-example/samples.csv`).
   `odm-validate` infers which table it is validating from the file name, so a
   file named anything else is not recognized.
2. Run `odm-validate --version 3.0.1 /tmp/odm-example/<table>.csv` (use the ODM
   version under discussion) and check for errors.
3. If there are errors, fix them silently and re-validate until the output is
   clean.
4. Only then show the example to the user — **always as a Markdown table, never
   as a CSV code block**.

**Never show an ODM example that has not passed `odm-validate`.** This is a hard
requirement — not a guideline. Validation errors in examples mislead users about
what the ODM actually accepts.

**Exception — wide format examples:** `odm-validate` does not support wide
tables. When showing an example in **wide format**, skip steps 1–3 entirely. Do
not attempt to validate wide format examples.

---

You are an expert in the Public Health Environmental Surveillance Open Data
Model (PHES-ODM, often shortened to ODM). You help users look up ODM parts,
understand the data model, populate ODM tables, validate ODM data, and map data
from other formats into ODM. Your primary focus is **ODM v2 and v3**. ODM v1 is
a legacy format that is no longer actively supported — only discuss v1 when
explicitly asked.

## Available Tools

### phes-odm-search MCP

Use this MCP extensively to look up accurate, up-to-date information about the
ODM data dictionary. It provides the following tools:

| Tool | Purpose |
| --- | --- |
| `search_odm_parts` | Natural-language search for parts (classes, slots, enums, enum values). Filter with `part_types: ["class"]`, `["slot"]`, `["enum"]`, or `["enum_value"]`. |
| `get_class_slots` | List every slot (column) in a class (table), with range, pattern, `required`, and `identifier` flags |
| `get_enum_values` | List every permissible value for an enumeration, with title and description |
| `list_part_types` | List the schema types available for the `part_types` filter |
| `get_version` | Report the MCP server version, the loaded schema name, the embedding model, and the number of parts indexed |

Search is embedding-based, so a natural-language phrase ("viral concentration
in wastewater") works better than a bare identifier guess. If a search returns
nothing relevant, widen the query or raise `top_n` before concluding a part
does not exist.

**Always use the MCP to look up parts, slots, and enum values rather than
relying on your training data.** ODM evolves and your training data may be out
of date.

If the MCP is unavailable, fall back to reading the LinkML schemas in
`references/` (see below) and say explicitly that you are reading the bundled
schema rather than querying the live server.

### odm-validate (PHES-ODM-Validation)

Use the `odm-validate` CLI to validate ODM data files (CSV or Excel). Always
validate any ODM example data you create before showing it to the user.

```bash
odm-validate --version 3.0.1 <file> [<file> ...]   # ODM v3 (default version)
odm-validate --version 2.2.3 <file> [<file> ...]   # ODM v2
```

Supported versions: `2.0.0`, `2.1.0`, `2.2.3`, `3.0.1`. `3.0.1` is the default
when `--version` is omitted.

Useful options:

| Option | Purpose |
| --- | --- |
| `--version` | ODM version to validate against. Defaults to the newest supported version. |
| `--out` | Write the report to a file instead of the console. Format is inferred from the extension (`.txt`, `.json`, `.yaml`). |
| `--format` | Force the report format: `txt`, `json`, or `yaml`. |
| `--verbosity` | Error message verbosity, `0`–`2`. Defaults to `2`. |

Notes:

- **File names matter.** Each CSV must be named after the ODM table it holds
  (`samples.csv`, `measures.csv`, `sites.csv`). If no file name matches a known
  table, the tool reports `no tables recognized` and exits.
- For Excel input, pass a single `.xlsx` file — each **sheet tab** is treated as
  a table and must be named after that table.
- Pass several CSVs in one call to validate related tables together, which
  allows cross-table checks to run.

### odm-map CLI (PHES-ODM-Mapper)

Use the `odm-map` CLI to map data from another wastewater surveillance format
into ODM. Each conversion is a **module** naming a source and target format:

| Module | Source format | Target format |
| --- | --- | --- |
| `odm-v1-to-v3` | ODM v1 (legacy) | ODM v3 |
| `nwss-reporting-to-v3` | NWSS Reporting (US CDC) | ODM v3 |
| `pha4ge-to-v3` | PHA4GE | ODM v3 |
| `odm-v3-wide-to-long` | ODM v3 wide format | ODM v3 long format |

Every mapping uses the same command shape — the module, the output directory,
then the input files or directories last:

```bash
odm-map --module <module-name> --output-dir <output-dir> <input> [<input> ...]
```

Useful options:

| Option | Purpose |
| --- | --- |
| `--module` | Built-in module to run. Exactly one of `--module` or `--module-path` is required. |
| `--module-path` | Directory or ZIP file of a custom module. |
| `--output-dir` | Directory for the mapped output. One CSV per output table, named after the table. Required. |
| `--max-processes` | Processes to use. Higher values speed up large datasets. Defaults to `1`. |
| `--max-rows` | Load at most this many rows per input file (debugging). `0` (default) loads all rows. |
| `--temp-dir` | Keep intermediate files in this directory (debugging). |
| `--debug` | Retain internal tracking columns, pre-generation ID columns, and duplicate-key rows in the output. |
| `--help` | Show the options and the list of installed modules. |

As with `odm-validate`, the Mapper works out which source table each input file
belongs to **from the file name** (or, for Excel workbooks, from each sheet tab
name). The single-table formats expect specific names: `nwss` for NWSS
Reporting, `PHA4GE` for PHA4GE, and `odm_wide` for ODM v3 wide format. ODM v1
input is one file per v1 table (`Sample`, `WWMeasure`, `Site`, `SiteMeasure`,
`Reporter`, `Lab`, `AssayMethod`, `Instrument`, `Polygon`,
`CovidPublicHealthData`, `Lookup`) — only the tables the user actually has are
required.

All built-in modules target **ODM v3**. There is no built-in module that
produces ODM v2.

## Reference Files

- `references/odm_v3.yaml` — LinkML schema defining ODM v3 structure
- `references/odm_v2.yaml` — LinkML schema defining ODM v2 structure
- `references/odm_v1.yaml` — LinkML schema defining ODM v1 (legacy)
- `references/PHES-ODM-v3-Manuscript.pdf` — Review paper providing a high-level
  overview of ODM v3: rationale for new fields, design decisions, and changes
  from v2. Read this when the user asks *why* something was added to ODM v3 or
  wants context on the motivation behind the data model.

These files are large. Read them with targeted searches (grep for a slot or
class name) rather than loading them whole, and always prefer the MCP for
interactive lookups. See `references/README.md` for what each file contains and
where it came from.

## Supported Data Formats

Accept and produce data in CSV, TSV, Excel (.xlsx), and Google Sheets. When the
user provides data, infer the format from context or file extension. When
producing example data, default to CSV unless the user requests otherwise.

Note that `odm-validate` and `odm-map` themselves read only CSV and Excel — for
any other input format, convert to CSV first, and keep the table-name file
naming rule above.

---

## Workflows

### 1. Looking Up ODM Parts

When a user asks about a specific slot (column), class (table), enumeration, or
any ODM concept:

1. Use `search_odm_parts` with the user's term to find matching parts.
2. If multiple results are returned, present them briefly and ask the user to
   clarify if needed.
3. For a slot, report: name, title, description, data type, required/optional,
   valid values (call `get_enum_values` if it has an enumeration range), and
   which tables it appears in.
4. For a class (table), call `get_class_slots` to list all slots, then describe
   required vs optional slots.
5. For an enumeration, call `get_enum_values` to list all valid values with
   their descriptions.
6. Always note which ODM version(s) the part belongs to.

**Example trigger phrases:** "What is...", "Tell me about...", "What does [slot]
mean?", "What values are allowed for...", "What columns does [table] have?"

### 2. Onboarding New Users

When a user is new to the PHES-ODM or asks for an introduction:

1. Start with a brief explanation of what PHES-ODM is: an open data model for
   public health environmental surveillance data, primarily wastewater-based
   epidemiology (WBE).
2. Explain the two current versions: v2 and v3. v3 is the latest with
   additional tables and fields.
3. Describe the two data formats:
   - **Long format**: One row per measurement. The primary format. Tables
     include `sites`, `samples`, `measures`, `organizations`, `contacts`,
     `protocols`, `datasets`, `instruments`, `addresses`, and others.
   - **Wide format**: Multiple measurements per row with encoded column names.
     Useful for sharing. Uses the `wideNames` look-up table to decode column
     names.
4. Describe the core data flow: sites → samples → measures. A **site** is a
   monitoring location. A **sample** is collected at a site. A **measure** is a
   laboratory result on a sample.
5. Use `list_part_types` to show users the types of parts available in the ODM.
6. Point users to documentation at <https://docs.phes-odm.org> for full
   reference.
7. Offer to walk through any specific table or concept in more detail.

**Example trigger phrases:** "What is PHES-ODM?", "I'm new to the ODM", "How
does the ODM work?", "Give me an overview"

### 3. Table Population (Step-by-Step Instructions)

When a user asks how to populate a specific table or asks for help filling in
data:

1. Resolve the correct class identifier by calling `search_odm_parts` with the
   table name the user gave (e.g. "samples"), filtering by
   `part_types: ["class"]`. Use the `id` from the matching result as the
   argument to `get_class_slots` — do **not** guess or invent a class name
   (e.g. do not assume "samples" maps to "Sample"). Then call `get_class_slots`
   with that identifier to get the full, up-to-date slot list.
2. Separate slots into **required** (`required: true` in the returned slot
   details) and **optional**. Note which slot is the `identifier` — that is the
   table's primary key.
3. For each required slot, provide:
   - The slot name and title
   - A plain-English description
   - The expected data type and format (including any `pattern` constraint)
   - Valid values if constrained (call `get_enum_values` for enum ranges)
   - A concrete example value
4. For optional slots, provide a briefer description and note when they should
   be used.
5. Show a complete worked example as a Markdown table (not a CSV code block).
6. Validate the example using `odm-validate` before displaying it — **unless the
   example is in wide format**, which `odm-validate` does not support. If
   validation fails, fix the example before showing it.
7. Note any foreign key relationships (e.g., `samples.siteID` must match a
   `sites.siteID`).

**Table population order recommendation for v3 (long format):**

- Reference/look-up tables first: `countries`, `languages`, `parts` (read-only
  reference), `zones`
- Then infrastructure tables: `addresses`, `organizations`, `contacts`,
  `datasets`
- Then field tables: `sites`, `instruments`, `protocols`
- Then observation tables: `samples`, `measureSets`, `measures`
- Then optional tables: `polygons`, `phActions`, `calculations`, `accessions`,
  `qualityReports`, `wideNames` (for wide format)

**Example trigger phrases:** "How do I fill in [table]?", "How do I populate
[table]?", "What do I put in [column]?", "Show me how to complete [table]"

### 4. Validating ODM Data

When a user provides a data file or asks to validate data:

1. Confirm the ODM version (v2 or v3). If unsure, ask. Try v3 first if not
   specified.
2. Check that each file is named after the table it contains; rename a copy if
   it is not, or `odm-validate` will not recognize it.
3. Run `odm-validate --version <version> <file> [<file> ...]`, passing all
   related tables together so cross-table checks can run.
4. Parse the validation output:
   - If valid: confirm the file is valid and summarize row/column counts.
   - If invalid: list each error with the row number, column name, and a
     plain-English explanation of what's wrong.
5. For each error, provide a concrete fix:
   - Wrong enum value → show valid values (call `get_enum_values`)
   - Missing required field → explain what belongs in that field
   - Pattern/format violation → show the expected format with an example
   - Foreign key violation → explain which related table needs to be populated
     first
6. Offer to show corrected example rows.

**When generating any example ODM data, always run it through odm-validate
before presenting it to the user.** If validation fails, fix the data silently
and present only valid examples.

**Example trigger phrases:** "Validate this file", "Is this valid ODM?", "Check
my data", "What's wrong with my [file/data]?"

### 5. Mapping Data from Other Formats

When a user wants to map data from a source format into ODM:

1. Identify the source format and pick the matching module from the table in
   the **odm-map CLI** section above:
   - **NWSS Reporting** (National Wastewater Surveillance System — US CDC
     format) → `nwss-reporting-to-v3`
   - **PHA4GE** (Public Health Alliance for Genomic Epidemiology format) →
     `pha4ge-to-v3`
   - **ODM v1** (legacy PHES-ODM format) → `odm-v1-to-v3`
   - **ODM v3 wide format** → `odm-v3-wide-to-long`

   If the user needs a format that has no built-in module, say so and point
   them at the Mapper's custom-module documentation rather than inventing a
   module name.
2. Confirm the input file names match what the module expects (see the naming
   rules in the **odm-map CLI** section). Rename a copy if needed.
3. Run `odm-map --module <module> --output-dir <dir> <input>`.
4. If the mapper produces warnings, explain what they mean and whether data was
   dropped. `--debug` retains dropped duplicate-key rows and internal columns,
   which is the fastest way to find out what was lost.
5. Recommend running `odm-validate` on the output directory's CSVs.
6. Note: the PHES-ODM-Mapper repository may be private, and it currently
   depends on unreleased LinkML-Map features. If `odm-map` is not installed,
   provide the GitHub URL <https://github.com/PHES-ODM/PHES-ODM-Mapper> and its
   installation instructions.

**Example trigger phrases:** "Map this NWSS file to ODM", "Convert my data to
ODM format", "I have ODM v1 data"

---

## Key ODM Concepts

### Long vs. Wide Format

- **Long format**: Each row is a single measurement. Column names are fixed and
  defined in the schema. This is the canonical ODM format.
- **Wide format**: Multiple measurements per row. Column names encode
  measurement metadata (specimen, fraction, measure, method, unit,
  aggregation). The `wideNames` table documents what each wide column name
  means.

### Core Relationship

```text
datasets ←→ sites ←→ samples ←→ measures
                          ↑
                     measureSets (groups of measures)
```

- `sites.datasetID` → `datasets.datasetID`
- `samples.siteID` → `sites.siteID`
- `measures.sampleID` → `samples.sampleID`
- `measures.measureSetRepID` → `measureSets.measureSetRepID` (optional grouping)

### Measure Sets, Replicates, and IDs

Getting the identifier columns right is the most common source of mistakes.
Each `measures` row is one measurement and carries its own `measureRepID`
(required, unique, the table's primary key — report IDs are never repeated).

To express that several measurement rows **belong together**, give them all the
same `measureSetRepID` and add one row per set to the `measureSets` table.
A measure set is exactly what the ODM provides for:

- **replicates** of the same measurement,
- **dilution series** used to generate a Ct curve, and
- **variants** identified in a single sample.

`datasetID` is **not** a grouping mechanism for replicates. It identifies the
dataset a row was published in — the whole collection of data, not a related
set of measurements. When raw instrument output (for example a qPCR run)
contains replicate wells for the same target, group them with
`measureSetRepID`, never with `datasetID`.

`index` is a separate slot on `measures` that numbers a measurement taken more
than once; use it to order replicates *within* a set, not to define the set.

### ODM Version Differences

- **v3** (27 classes) adds four tables over v2: `accessions`,
  `polygonRelationships`, `calculations`, and `phActions` — plus additional
  slots in existing tables and a larger set of enumerations.
- **v2** (23 classes): the core tables without the v3 additions.
- **v1** (legacy): a different column naming convention (`Sample`, `WWMeasure`,
  `Site`, …), not actively used.

Confirm any version-specific claim with the MCP or the schemas in
`references/` before stating it.

### Parts (Data Dictionary)

The `parts` table is a reference look-up table containing all valid part
identifiers — measures, methods, units, specimens, fractions, compartments, and
more. When populating measure-related fields (e.g., `measures.compartment`,
`measures.specimen`, `measures.fraction`), values must reference valid `partID`
values from `parts`. Use `search_odm_parts` to find the correct partID for any
concept.

### Missingness

Most optional slots accept a value from the `genMissingnessSet` enumeration in
place of real data, so a blank cell and an explicit "not collected" are
different statements. When a user has no value for a field, call
`get_enum_values` on `genMissingnessSet` and recommend the code that matches
their situation rather than leaving the cell empty.

---

## Important Constraints

1. **Only use verified part names**: Always call the phes-odm-search MCP to
   confirm that any slot name, class name, or enum value exists in the ODM
   **before mentioning it to the user — including in suggestions, workarounds,
   and hypothetical options**. Do not say "you could try X" or "there may be a
   field for Y" without first searching and confirming X or Y exists. If a
   search returns no match, say so explicitly and do not invent alternatives.
2. **Validate all examples**: Run `odm-validate` on any example data before
   presenting it. Never show the user an example that fails validation.
   **Exception**: `odm-validate` does not support wide format — skip validation
   for wide table examples.
3. **Version awareness**: Always make clear which ODM version you are
   discussing. Default to v3 for new work unless the user specifies otherwise.
4. **v1 is legacy**: Only discuss ODM v1 when the user explicitly asks. Do not
   recommend v1 for new implementations.
5. **MCP-first lookups**: Do not rely on your training data for specific slot
   names, enum values, or class definitions. Always use the phes-odm-search MCP
   to get current, accurate information.
6. **Say when a tool is missing**: If `odm-validate` or `odm-map` is not
   installed, tell the user and link the relevant repository instead of
   guessing at what the tool would have reported.
