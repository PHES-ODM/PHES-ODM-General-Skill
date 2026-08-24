# PHES-ODM Skill — original specification

> **Historical document.** This is the specification the skill was originally
> built from, kept for context on why it works the way it does. It is not
> maintained as the skill evolves — [`SKILL.md`][skill] is the current
> definition of behaviour, and the [README](../README.md) is the current
> description of the repository. Where the two disagree, `SKILL.md` wins.
>
> [skill]: ../skills/phes-odm-general/SKILL.md

## Task Overview

The phes-odm skill should be an expert at PHES-ODM (Public Health Environmental
Surveillance Open Data Model, often shortened to ODM) and allow users to look
up parts in the ODM and ask general questions about the PHES-ODM. It should
also be able to give detailed step-by-step instructions on how to populate the
ODM using any of the tables available. It should also be good at providing
details to the user to help onboarding them onto the PHES-ODM. This is
particularly useful for new employees who are not yet familiar with the
PHES-ODM. The focus of the skill should be on ODM v2 and v3. ODM v1 is a legacy
format that is no longer supported.

## Relevant Repositories

There are several repositories that the skill should refer to. Each repository
should be able to be run or referenced by the skill to perform certain tasks.
If necessary, the repositories can be cloned into the skill. Below is a list of
these repositories:

1. **[PHES-ODM-Mapper](https://github.com/PHES-ODM/PHES-ODM-Mapper)**: This
   repository provides a tool to map from certain wastewater database formats
   to ODM. Source formats include NWSS, PHA4GE, ODM v1, and ODM v2/v3 wide
   format. When a user asks to map data from a source format this repository
   should be used.
2. **[PHES-ODM-Validation](https://github.com/PHES-ODM/PHES-ODM-Validation)**:
   This repository validates data that is in ODM format (v2 and v3). The skill
   should be able to validate data and provide instructions on how to fix data
   so that it is in valid ODM format. Whenever the skill provides examples of
   data in ODM format the examples should be validated before displaying them
   to the user.
3. **[PHES-ODM-Doc](https://github.com/PHES-ODM/PHES-ODM-Doc)**: This is the
   main documentation of the PHES-ODM. The repository is used to generate the
   documentation found at <https://docs.phes-odm.org>. It includes details about
   what the ODM is, how to use the ODM, long and wide ODM formats, and a
   detailed reference guide. It provides valuable information for onboarding
   people to the ODM and to provide additional details to those already
   familiar with the ODM.
4. **[PHES-ODM-Search-MCP](https://github.com/PHES-ODM/PHES-ODM-Search-MCP)**:
   This is the repository for the phes-odm-search MCP. In order to query
   information about the PHES-ODM data dictionary, the phes-odm-search MCP
   should be used. This MCP allows users to look up slots (columns), classes
   (tables), enumerations, and other related details about the ODM. This MCP
   should be used fairly extensively to gather details about the ODM.

## Supported File Formats

Most data should be provided in CSV, TSV, or Excel format. The skill should
also support other formats such as Google Sheets.

## Supported MCPs

As described above, the phes-odm-search MCP should be used for querying details
about the ODM and its structure.

## Relevant Files

- The LinkML schema at `skills/phes-odm-general/references/odm_v1.yaml`
  defines the structure of ODM v1.
- The LinkML schema at `skills/phes-odm-general/references/odm_v2.yaml`
  defines the structure of ODM v2.
- The LinkML schema at `skills/phes-odm-general/references/odm_v3.yaml`
  defines the structure of ODM v3.

## Important

Previously when creating this skill there were problems where tables and slots
listed in the reference files have been incorrect or invalid. When creating the
skill, make sure all tables/classes and slots/columns are actually present in
ODM, and that all example values are valid.
