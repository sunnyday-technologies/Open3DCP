# Example corrections — 15 September 2026

The RILEM and UF examples now preserve the source context needed to interpret each exported result. The earlier CSVs remain in each example's `history/` folder, marked as superseded. This correction does not change schema 1.8 or the frozen evidence reviewed in manuscript v1.2.

## RILEM mechanical example

The old nine-row export averaged incompatible bending methods, specimen scales and conditions. It cannot support the previous 32–55% comparison. The replacement contains 200 individual specimens, with no pooled means or effect estimates. Each result links to its source sample, full compound orientation, test geometry, method, age and condition. An inclusion ledger records all 292 candidate specimens and the reasons for 92 exclusions. Unsupported units are not interpreted, and parent print/material relationships are not guessed.

See the [source and correction details](rilem-tc304-ils-mech/SOURCE.md).

## UF mixture example

The extractor no longer interprets material-name cells as quantities, assigns every row to OPC/blended OPC, or assumes that every mechanical specimen was printed. The corrected excerpt contains 10 mixture/age records from 10 source rows. Original composition labels, quantities and blanks are retained in a 940-cell ledger. Complete ratios on a common mass basis can be normalized without an absolute dosage; this excerpt leaves composition unconverted because completeness and a common basis are not established. Missing values remain distinct from zero.

See the [source and correction details](uf-3dcp-mix/SOURCE.md).

## Submission and regression checks

The submission validator now reads the current schema version from the existing canonical version reader instead of warning against a hardcoded 1.6. Both 1.8 and 1.8.0 are recognized; older submissions receive a warning rather than an automatic rejection.

Regression checks cover source identity, incompatible test context, orientation, missingness, units, selection and version warnings. Both extractors reproduce their corrected files from fingerprinted, unchanged source files. Full source reproduction requires those separately downloaded source files; CI tests use fixtures and the committed ledgers.

An existing UCI reproduction check also failed on small floating-point serialization differences. The checker now permits at most eight units in the last binary place in schema REAL columns. Text, missing values, row order, column order and meaningful numerical changes still require an exact match. The UCI data itself is unchanged.
