# Reproducing the RILEM ILS-mech excerpt

The source database is **not** committed here (it is 23.3 MB and we do not re-host it). To reproduce
`../rilem-tc304-ils-mech.open3dcp.csv`:

```bash
# 1) download the CC BY 4.0 SQLite from the DOI:
#    https://doi.org/10.5281/zenodo.12200570  -> 2024-06-21_openbis.db
# 2) regenerate the excerpt:
python build/extract.py /path/to/2024-06-21_openbis.db
```

`extract.py` denormalizes the `material_/print_/exp_flex_sample_props_view` tables for mixes 01, 13, 19,
aggregates per (mix × orientation) into mean / std-dev / n, maps RILEM U/V/W → Open3DCP X/Y/Z/CAST, and
writes the flat CSV. Values are real; the unit-inconsistent print travel-velocity field is omitted.

A turnkey `open3dcp-ingest` SQLite reader (so this joins the standard `convert` + reproduce-and-diff CI
path, like the UCI example) is a planned follow-up.
