# M2: report delivery and failure handoff

Date: 2026-09-08. Scope: a bounded part of M2, not completion of the milestone or a release. Helper version: `0.1.1-dev`; contract/report schemas remain `m1`/`m1-report`. Local checks used macOS and Python 3.14.4; the CI follow-up also ran the complete suite on an isolated Python 3.10.20.

## User problem and acceptance boundary

A developer needs to know whether an acceptance report was actually delivered, and where to resume inspection after an error. A file starting with PASS is not sufficient if it is truncated, or if report cleanup failed and that responsibility was hidden.

The chosen boundaries are the existing helper CLI with `--output`, its report files, and the collector's JSON summary. Business verdict rules, frozen expectations, existing paths, and prior run evidence must remain unchanged. No new runner, production access, automatic retry, or release approval is introduced.

## Reproduced defects and changes

| Before | After | Evidence |
| --- | --- | --- |
| Writing directly to the final report name could leave a partial Markdown file beginning `Business: PASS` when interrupted | Write and flush a same-directory temporary file, then publish without replacement; an unfinished temporary file is not a delivered report | A real helper child is paused after an actual report fragment is flushed, then killed by its parent; the old code failed, the changed code passes |
| An error after creating the default random run directory did not tell the user where its pending evidence was | Incomplete output identifies only the directory created by this invocation; refusal of an existing path explicitly claims no ownership | Real collector/exporter plus controlled file-write faults; old evidence remains byte-identical |
| Unexpected `RuntimeError` text could be copied into the collector's error summary | Only collector-authored report errors carry public messages; other errors expose their type | A synthetic secret sentinel in a controlled error does not appear in output |
| The first atomic-write implementation could publish a full report, fail to remove its temporary file, then have both helper errors hidden behind an apparent complete handoff | Helper diagnostics distinguish published output from incomplete cleanup; collector retains both results and reports partial/unqualified delivery while preserving business findings | Two actual helpers encounter a controlled unlink failure after publication; both healthy and defective export cases preserve reports and show the residual responsibility |

The last defect was found during independent review of this change, reproduced as a failing regression, and corrected before submission. Historical report bytes are not rewritten to conceal delivery failures.

## Executed local checks

| Command / check | Result | Boundary |
| --- | --- | --- |
| `python3 -B -m unittest discover -s tests -v` | 61 passed, no failures/errors/skips | 43 material checks, 9 collector checks, 4 controlled I/O probes, 5 report-publication checks |
| `python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v` | 23 passed, no failures/errors/skips | Standalone native exporter; no Skill/helper dependency |
| Fresh `healthy` demo | PASS, complete, exit 0 | Actual exporter and read-back CSV comparison |
| Fresh `defect` demo | FAIL, complete, exit 1 | Actual export omits the final record while its process exits 0 |
| Fresh `missing-observation` demo | UNVERIFIED, partial, exit 2 | Actual file exists; required observation is deliberately omitted |

Total: **84 unittest methods**, not 84 product evaluations. Some methods contain multiple subcases. New checks also cover concurrent report writers, partial ENOSPC writes, flush/fsync errors, and a subsequent explicit invocation after a handled failure.

The interruption test controls the file I/O boundary and proves that the actual fragment reached disk before sending SIGKILL to its owned process. It does not claim naturally occurring timing or power-loss testing. An initial file-size-limit experiment did not reliably pause before error cleanup; it was rejected as regression evidence, not counted as a successful defect reproduction.

Fault probes use synthetic material and isolated process/file boundaries. They do not mock the helper's verdict or supply desired answers in place of actual command results. Test temporary directories are cleaned after their owned processes stop. Fresh demo evidence remains in the ignored local run directories, independently of the earlier M1 evidence.

## Remote CI

The initial M1 source at `1eb78de` passed both Ubuntu 24.04 jobs, Python 3.10 and 3.14, in [run #1](https://github.com/Quine-rq/functional-acceptance/actions/runs/34182582017).

The first M2 commit `f30f6ba` exposed a test portability defect in [run #2](https://github.com/Quine-rq/functional-acceptance/actions/runs/34183395185): Python 3.14 passed; Python 3.10 failed both cleanup-probe subcases because the intended fault never fired. Its standalone job step was consequently skipped, not passed. Python 3.10's pathlib retains an earlier `os.unlink` binding, so replacing the module attribute after import did not intercept its removal calls.

The same failure was reproduced locally on Python 3.10.20 before changing the test. The corrected child-only probe uses the documented [`os.remove` audit event](https://docs.python.org/3.10/library/os.html#os.unlink), with the same actual-file/same-inode guard and failure assertions. It does not change product code, patch private pathlib internals, or skip older Python. Both complete suites then passed locally on Python 3.10.20 and 3.14.4: 61 + 23 methods per interpreter. Hosted verification of this follow-up remains pending until its own CI completes.

## Delivery and recovery limits

- `--output` protects the visibility of one completed file. Stdout redirection, power loss, and a two-report transaction are not made atomic.
- SIGKILL or an unavailable filesystem may leave a temporary file. It is not a qualified report and is not deleted by a background task. Inspect only the identified run-owned paths after the writer has stopped.
- A complete historical report can coexist with a later delivery error. Use the collector summary and `report-delivery.json` to identify incomplete handoff; resolve the residual and recheck instead of treating file presence as success.
- Existing files, directories, and links are never replaced. Independent concurrent report writers have one winner; the refused writer does not remove the winner's output.
- Cross-project usefulness, natural discovery, with/without-Skill comparisons, external human reuse, installation, licensing, and a supported release remain pending. Full M2 completion is not claimed.

The temporary-file behavior follows the Python [tempfile documentation](https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile), including its explicit SIGKILL cleanup limitation. The sample exporter already uses the same no-replacement publication approach; it remains independently runnable.
