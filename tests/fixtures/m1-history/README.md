# m1 compatibility fixtures

Generated on 2026-09-08 by the unmodified collector/exporter/helper from commit
`edc295c285da4550ec2fadca1e2f455d5be06fef`. These are new synthetic runs of an
older implementation, not recovered past production evidence. Before publication,
the current relocated helper rechecked each original run as PASS / FAIL /
UNVERIFIED and left every original material file unchanged.

For portable public fixtures, only `execution.argv[0]` was changed from the local
interpreter location to `python3`; its enclosing execution digest was recomputed
in `run.json`. `provenance.json` retains original and published file digests,
source identities and observed exit codes. CSV, runtime, input and contract bytes
were not normalized. The original local runs remain separate.

These fixtures guard the m1 reading contract. Tests do not execute the embedded
runtime or recorded commands, authenticate their collection, or claim a universal
schema migration. A fixture with missing/modified evidence must still fail
qualification. Unknown format versions stay unverified.
