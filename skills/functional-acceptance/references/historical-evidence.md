# Review retained history

Use only when the user asks what an earlier run established. Return the assessment in the conversation without running the target or creating evidence files. Attribute claims to the retained record unless independently observed. Fresh execution can investigate current behavior, but cannot establish a past result.

For every original obligation, identify the retained observation, verdict, missing evidence and what would remain unknown after the proposed next step. Match proof to the full claim:

| Historical claim | Observations needed together | Insufficient on its own |
| --- | --- | --- |
| Output preserves records, order and values | Complete historical output **and independently retained historical expected inputs** | Output alone, header/first/last rows, row count |
| Output was newly created rather than overwriting | Historical pre-run absence or equivalent creation provenance, linked to this run and output | The final file existing |
| Existing objects remained unchanged | Before/after content or content digests **for every object in the required scope** | One input file when the requirement covers existing files; timestamps |

These are claim-specific examples, not extra requirements for every feature. Use the equivalent independent expectation, object identity and historical observation for other flows.

Keep each obligation UNVERIFIED until its observations are sufficient together. Check proposed next steps against the same full claim: obtaining the output alone does not establish its expected contents or prove that unrelated objects were preserved. Name the residual gap instead of calling partial evidence sufficient. If required historical evidence no longer exists, say that the past claim cannot be established from the available record.

Hand off with the [acceptance report](acceptance-report.md), including retained-record identity, per-obligation findings and residual uncertainty. Mark execution “not run”; report historical execution/cleanup as attributed facts or unknown, not fresh confirmation.
