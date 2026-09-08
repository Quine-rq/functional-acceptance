# M1 implementation boundary

Status: controlled local slice implemented and checked; actual results and limitations are in [M1-RESULTS.md](M1-RESULTS.md). This plan itself is not test evidence.

## User result

A developer must be able to distinguish a complete exported file from a command that reports success while losing the final page, and from a run whose file cannot be observed.

The first controlled sample is an offline paginated-response JSON input exported through a real Python CLI to a real CSV file. Its upstream pages are synthetic fixtures, not a live API. This proves only the observed local CLI/file workflow. It does not establish browser, remote-service, mobile, or cross-project support.

## Invariants and interfaces

- Freeze independent expected CSV columns and rows before execution. Preserve every requested goal, including gaps and sourced exclusions.
- Use the sample's existing native command and `unittest`; the Skill does not introduce an action language or general runner.
- The offline helper reads a contract, a run manifest, and bounded evidence under an explicit root. Its one supported business mapping is `csv-exact/v1`.
- A native process record binds the run, attempt, actual program/input digests, output reference, and command termination. The helper checks consistency and directly compares CSV content; it does not authenticate the collector or execute recorded commands.
- Keep PASS/FAIL/UNVERIFIED/NOT_APPLICABLE separate from coverage and cleanup. A valid failed attempt survives a later success. An absent observation is not a product defect.
- Use unique run directories, exclusive file creation, and synthetic data. Keep evidence local and out of Git; no default cleanup of previous runs, installation, production access, or release.

## Acceptance before submission

1. Healthy command creates all expected records, including escaped text, with valid evidence.
2. An explicitly injected final-page defect exits zero but produces a concrete missing-record counterexample.
3. Missing/corrupted/foreign-run evidence cannot produce a qualified PASS.
4. Native checks exercise empty/boundary/error paths and do not overwrite pre-existing user files.
5. A fresh run does not invalidate the first run's retained evidence.
6. An independent agent can follow the native handoff instructions without installing the Skill.
7. Skill structure validation and independent forward-testing are reported separately from helper tests and actual CLI execution.

Publishing development source is not a release. Licensing, cross-project reuse, natural discovery, fair baseline comparisons, and external human evaluation remain later gates in [ROADMAP.md](ROADMAP.md).
