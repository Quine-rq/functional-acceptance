# M1 local validation record

Date: 2026-09-08. Scope: experimental development source, not a release. Local environment: macOS, Python 3.14.4, standard library, real subprocesses and local filesystem. The upstream paginated responses are synthetic fixtures. No remote API, browser, database, mobile device, production environment, or external human user was tested.

## What changed for the user

Before M1, this repository described acceptance but could not execute a sample. Now a developer can run a native export and obtain a scoped report that compares the actual CSV with an independently frozen expectation. A successful command can still be a failed user outcome; a missing observation remains a gap. The native regression pack can run without the Skill or material helper.

## Executed checks

| Check | Actual result | What it establishes |
| --- | --- | --- |
| `python3 -B -m unittest discover -s tests -v` | 54 passed, 0 failures/errors/skips | 43 material-CLI tests, 8 collector-CLI tests, 3 controlled I/O failure tests |
| `python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v` | 23 passed, 0 failures/errors/skips | Real native export, exact CSV content, empty/boundary/error input, exclusive output and same-name concurrency |
| Skill structure validator | Passed | Frontmatter/name/scaffold checks only; not behavioral proof |
| Workflow YAML inspection | Parsed; triggers, read-only permission and matrix checked | Configuration only, not a successful hosted CI run |

Total: **77 unittest methods**. Some methods include multiple subcases. This is not a count of the larger V01–V38/N01–N09 evaluation plan being passed.

The helper suite uses synthetic process records to isolate mechanical material rules. The three I/O tests disclose their controlled injection: a real slow owned child plus a failed handle write; individually permitted evidence files exceeding the cumulative budget; and real consecutive helper reads with a run-owned file moved between them. Those probes do not masquerade as normal exporter runs.

## Final three-case replay

After the code corrections, each collector command started a new native exporter and two fresh helper processes. Both report formats agreed:

| Case | Native result | Business verdict | Completion | Collector exit |
| --- | --- | --- | --- | --- |
| Healthy | Exit 0, all five expected records with exact field values | PASS | complete | 0 |
| `--fault omit-final-page` | Exit 0, four records; final `r-005` missing | FAIL | complete | 1 |
| Missing-observation experiment | Native file exists, required observation deliberately withheld | UNVERIFIED | partial | 2 |

Retained local run directory names are `healthy-fd2aeba605a74e778526fc5b995725b2`, `defect-820a44eddc584c9da7dd48cc57583a01`, and `missing-observation-be65eede517c47afbfe93bb580764cba` under the repository's ignored `.acceptance/runs/`. The manifests, raw native records, snapshots, CSV and both reports remain separate by run; they were not published. Follow [README.md](README.md) to generate fresh evidence. Digests are integrity references, not authenticated provenance.

## Independent use and replay

An independent agent explicitly loaded the Skill, read the sample's requirements and native entrypoint, and performed healthy/full-content, injected-defect, and empty-result checks. It independently identified the missing `r-005`. It did not test every error condition and kept those gaps explicit. This was **explicit loading**, not a natural-discovery evaluation.

That trial found stale root status text and insufficiently visible collector invocation. The root README now describes experimental M1 source and provides the three concrete commands plus `--run-dir` and retention behavior.

A separate fresh agent received only a clean copy of the native sample, with no original conversation, Skill, helper, or old run materials. Following its README, it ran 23 native tests with no failures/errors/skips, then created and read healthy (5 rows), defective (4 rows) and empty (0 data rows) CSVs. It removed only its explicitly created temporary files and empty directory; package contents were unchanged. Those removed manual files are not retained evidence. This establishes a bounded **agent replay**, not external-human reuse or a complete M2/L4 claim.

## Defects found during independent review

All four were reproduced before correction and rechecked after correction:

1. A process-handle write failed after child creation, leaving the owned child active. The entire post-start path now has bounded owned-process cleanup; incomplete pending material is not finalized.
2. Resolving a dangling run-directory symlink created its target. The collector now resolves only the parent and exclusively creates the new leaf; existing links and destinations are refused.
3. The cumulative evidence budget was checked after reading and could be exceeded by subsequent reads. File size and remaining budget are now checked before reads, reads are bounded, and exhausted material collection stops.
4. Evidence disappeared between the JSON and Markdown checks, but the collector still delivered the earlier PASS. Disagreeing checks now produce an incomplete exit while preserving both historical reports.

The symlink regression is retained in the collector black-box suite; the other three are retained in [tests/test_io_failures.py](tests/test_io_failures.py). Independent review reported no remaining reproduced blocker within its stated local scope. This is not a proof that no other defects exist.

## Executed source identities

These SHA-256 values identify the final local code/fixtures used by the three-case replay above:

```text
06c9f2d3a640aa078027a3191b4c17531633574f5d6c9386f2e9edc5013023a3  scripts/acceptance.py
b21efa345bcbadeb7a9a42c4edd0261a84f113ccd593349d53198360c48af6f3  examples/paginated_export/accept.py
2ba4954a1aad0a91e4c72a07616b73873a30144382766222fefa808c97de779c  examples/paginated_export/export.py
8b928221cc19848ef88905b5d4d4cc3bfeee6fd686782a87b5f274d3a3583d69  examples/paginated_export/fixtures/pages.json
1c3e572673aba569d887528e45513d36851207f3d40e5440042a4c56a40fdd86  examples/paginated_export/fixtures/expected_records.json
f2f917da7568bd3b69808e9bdb313707a767304de415f84e6840250c86ed6c89  SKILL.md
```

## Not established

Hosted CI execution is separate from local validation. The configured Ubuntu/Python matrix is not claimed as passed in this record. Python versions other than the observed local interpreter, other operating systems, install/uninstall, migration, natural discovery, fair with/without-Skill comparison, second-project reuse, external human effort savings, licensing, and a supported release remain pending. The helper cannot authenticate a dishonest collector, prove missing original goals were extracted, or validate arbitrary logs/visual observations. See [ROADMAP.md](ROADMAP.md) for the next gates.
