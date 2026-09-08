# Functional Acceptance

[简体中文](README.zh-CN.md)

**The feature is built. Does it work for the user?**

Functional Acceptance is a skill for coding agents to verify features through real user flows. It guides the agent to check the promised result, show the evidence, and leave tests that can be run again.

For example: an export command reports success, but the CSV is missing the final record. Acceptance means opening the file and checking its contents—not stopping at exit code `0`.

> Early development: a working local CLI/CSV demo is available. This is experimental source, not a supported release.

## How it works

Start with the feature's requirements and the project you want checked. The Skill guides your coding agent through three steps:

1. **Define success.** Identify what the user needs to accomplish and what would prove it worked. Keep unclear requirements and missing access visible.
2. **Check the result.** Use the project's existing tools to run the flow and inspect the outcome. Focus on relevant failure and recovery cases as well as the happy path.
3. **Hand over the findings.** Report what passed, what failed, and what remains unverified, with evidence and instructions for repeating the checks.

The Skill provides the workflow; the agent and project tools perform the checks. It does not replace your test framework or approve a release. The implemented demo below covers one local export flow; other workflows still need validation.

## Try the demo

The sample exports three pages of synthetic data into a real CSV file, then reads it back against five independently specified records. It includes a deliberate defect that drops the last page while still returning success.

No third-party packages, account, network connection, or Skill installation are needed. Run from the repository root with Python 3.10+ on a POSIX local filesystem supporting hard links and no-follow file access. So far, the demo has been checked on macOS with Python 3.14.4.

```sh
python3 -B examples/paginated_export/accept.py --case healthy
python3 -B examples/paginated_export/accept.py --case defect
python3 -B examples/paginated_export/accept.py --case missing-observation
```

| Case | What happened | Acceptance result | Exit code |
| --- | --- | --- | --- |
| `healthy` | All five records and their fields match | PASS | 0 |
| `defect` | Export exits 0, but record `r-005` is missing | FAIL | 1 |
| `missing-observation` | File exists, but its required observation record is deliberately withheld | UNVERIFIED | 2 |

The last two exit codes are intentional; run the commands separately, not joined with `&&`. UNVERIFIED means evidence is missing, not that the exporter has failed. The report also records coverage and cleanup separately from the verdict.

### Inspect the evidence

Each command prints a new run directory under this repository's `.acceptance/runs/`. Open `report.md` there for the findings or `report.json` for structured results. The same directory contains the fixed expectations, executed program and input snapshots, process record, and `attempt-1/output.csv`.

If report delivery fails, the response stays incomplete and identifies the directory created by that invocation. Inspect `report-delivery.json` when present for report-writing or cleanup errors. An interrupted temporary file is not a finished report, and a retained historical PASS does not override an incomplete handoff.

Runs are kept separate and retained locally. To choose a location, add `--run-dir NEW_DIRECTORY`; existing run directories are refused. When you no longer need a run, remove only that identified directory with your file manager. Deleted evidence can no longer be rechecked.

Want to inspect the exporter without the Skill or report helper? Follow the [standalone sample guide](examples/paginated_export/README.md) (Chinese).

## Compatibility and current limits

The workflow is designed to use tools already available in a project, rather than require a particular language or framework. Web, API, CLI, desktop, and mobile flows are intended applications—not a list of tested integrations.

Today, the working example covers **synthetic pages → real Python process → local CSV file**. The report checks complete export and exact field values; input errors and file safety have separate tests. No real upstream API, browser, database, mobile device, or second project has been validated.

The [M1 validation record](M1-RESULTS.md) documents the first 77 passing test methods and an independent agent's replay of the standalone sample. [M2 report-delivery checks](M2-RESULTS.md) bring the local suite to 84 methods, including interruption, disk failures, and incomplete handoff. These results do not establish external-user usefulness, time savings, or production readiness. A verified installation path and a supported release are still pending; do not treat cloning the source as installing the Skill.

### Safety and evidence limits

- Use authorized test environments. Acceptance does not grant permission to change product code, write to production, push commits, or publish comments.
- Missing tools or observations remain gaps. A mock proves only the behavior tested against it; a narrower test must not silently replace the user's original request.
- The helper directly compares the CSV with fixed expectations. It does not run commands from reports or accept a supplied PASS. File hashes detect changed evidence, not fabricated collection or requirements omitted from the start.
- Reports stay local and are not automatically sanitized. Review them before sharing; keep credentials, private logs, and customer data out of public issues.

See the [material format](references/material-format.md) for supported checks and trust boundaries.

## Development checks

```sh
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v
```

The first command tests the helper and evidence collector. The second tests the exporter independently of the Skill and helper, including whether the deliberately broken export is caught. A passing defect-detection test does not make that export correct.

[CI](.github/workflows/checks.yml) runs these checks on Ubuntu 24.04 with Python 3.10 and 3.14, using read-only permissions and commit-pinned actions. Both jobs passed for M2 source `c26a86f` ([run #3](https://github.com/Quine-rq/functional-acceptance/actions/runs/34183660278)); the [validation record](M2-RESULTS.md#remote-ci) includes an earlier failure and its correction. Check the run for the commit you use; an earlier green build does not validate later changes.

## Documentation and next steps

- **Explore the Skill:** [instructions](SKILL.md), [sample guide](examples/paginated_export/README.md), [material format](references/material-format.md).
- **See what is implemented:** [M1 scope](M1-PLAN.md), [M1 validation](M1-RESULTS.md), [M2 hardening](M2-RESULTS.md), [roadmap](ROADMAP.md).
- **Understand the design:** [product design](DESIGN.md), [architecture](ARCHITECTURE.md), [evaluation plan](VALIDATION.md). These detailed documents are in Chinese; planned evaluations are not passing test results.

Next: strengthen failure and handoff checks, try a second authorized project, and compare the same agent's work with and without the Skill. These checks come before a supported release.

## Feedback and licensing

Have a feature that looks successful but fails in actual use? Share its expected behavior and a small reproduction using synthetic data. Those cases are more useful at this stage than requests for broad platform support.

License selection is pending. No open-source license has been applied to this repository yet.
