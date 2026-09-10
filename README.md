# Functional Acceptance

[简体中文](README.zh-CN.md)

**The feature is built. Does it work for the user?**

Functional Acceptance is a skill for coding agents to verify features through real user flows. It guides the agent to check the promised result, show the evidence, and leave tests that can be run again.

For example: an export command reports success, but the CSV is missing the final record. Acceptance means opening the file and checking its contents—not stopping at exit code `0`.

> Installable development preview, not a supported release. Start in an isolated test project. Released under the [MIT License](LICENSE).

## Start in your project

### 1. Install

Run from the project where you want to use the Skill. This uses the tested third-party installer (`skills@1.5.24`, Node 22.20+) and may fetch it and the repository over the network.

**Fresh installation only:** check `.agents/skills/functional-acceptance/` first (`.claude/skills/functional-acceptance/` for Claude Code). A same-name copy will be replaced, including local edits. Existing users should follow [the update guide](UPGRADING.md).

```sh
DO_NOT_TRACK=1 npx --yes skills@1.5.24 add Quine-rq/functional-acceptance --skill functional-acceptance --agent codex --copy --yes
```

For another agent, replace `codex` with `claude-code`, `cursor`, `github-copilot` or `opencode`. These are checked installation targets, not equal levels of behavioral support; see [the scope below](#compatibility-and-current-limits).

Reload your agent if needed and confirm it sees this project's `functional-acceptance` copy. If it does not, stop at [installation and discovery troubleshooting](INTEGRATIONS.md#verify-the-installed-copy). No global installation, new model account or runtime is included. This command follows the default branch; [pin a reviewed commit](INTEGRATIONS.md#pin-update-recover-and-remove) for a reproducible installation.

### 2. Ask for a user result

In the project you want checked, name the Skill and describe the expected behavior. For a project with a CSV export, for example:

> Use functional-acceptance to verify this project's CSV export: every expected record and field must be present, and an existing destination must not be overwritten. Use synthetic data and temporary test files only. Show the checks before running, then give evidence and a repeat command. Do not change product code.

Replace the export requirements with your own feature and constraints. The agent should use your existing project tools, not require you to fill out a schema. If a required tool, observation or permission is missing, it should explain the gap instead of claiming success.

For a read-only first try, say: “Use functional-acceptance to plan acceptance for this feature. Do not run commands or create files.” A complete plan is the result of that request; no credentials are needed just to plan.

### 3. Get a checkable result

Before running, expect a short [acceptance contract](skills/functional-acceptance/references/acceptance-contract.md): your original goal, each required check, its independent expectation, and authorized scope. Afterwards, expect an [acceptance report](skills/functional-acceptance/references/acceptance-report.md) with evidence and a way to repeat the checks.

Illustrative handoff—not an additional recorded test:

```text
Result: FAIL — export returned 0, but record r-005 is missing.
Completeness: FAIL — 4 records observed; 5 independently expected.
Existing destination: PASS — replacement refused; before/after bytes match.
Coverage: both requested checks observed. Execution: completed.
Cleanup: only identified test evidence retained; no active writer.
Replay: native command, working directory, fixture and evidence references attached.
```

An unobserved check should say **UNVERIFIED**, with its blocker and next safe step. A discovered defect is a useful acceptance result; it is not permission to fix or deploy. Templates are filled in the conversation by default, not mandatory project files. The runnable demo below supplies actual evidence rather than this illustrative text.

## Try the demo

The sample exports three pages of synthetic data into a real CSV file, then reads it back against five independently specified records. It includes a deliberate defect that drops the last page while still returning success.

No third-party packages, account, network connection, or Skill installation are needed. Run from the repository root with Python 3.10+ on a POSIX local filesystem supporting hard links and no-follow file access. The local demo checks have run on macOS with Python 3.10.20 and 3.14.4.

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

The Skill uses the Agent Skills format and tools already available in the project. It is not tied to a language or framework, but tools, permissions and observations still determine what can actually be verified. Planning requires no Python; the optional CSV helper has the separate Python/POSIX requirements above.

| Agent / environment | What has been checked | Still unverified |
| --- | --- | --- |
| Codex | Native execution, planning, retained-history review, regression trials and 12 repeated Cookiecutter runs | Benefit on natural, under-specified user requests and unfamiliar external use |
| Claude Code | Actual, explicitly loaded read-only history reviews | Natural loading, healthy-history discrimination and complete executing journeys |
| Cursor, GitHub Copilot, OpenCode | Project-local install, replacement and removal only | Native discovery and useful execution |
| Mobile devices / other remote services | Intended applications only | Real-device and service-specific acceptance |

These observations describe the revisions and environments in [the native record](NATIVE-FOLLOWUP-RESULTS.md) and [installation record](INTEGRATIONS.md), not a behavioral certification of later instruction changes. Broad compatibility, savings and production readiness remain unproven.

The bundled example covers **synthetic pages → real Python process → local CSV file**. The report checks complete export and exact field values; input errors and file safety have separate tests.

The [sqlite-utils pack](examples/sqlite_utils/README.md) checks import, independent retrieval, export, duplicate-key rejection and unrelated-data preservation. The [linkding pack](examples/linkding/README.md) checks a real browser/server/database journey, including persistence, account isolation and recovery. Both are native examples, not generic adapters. Setup assistance and corrections are recorded; neither establishes external-human cold onboarding.

Detailed attempts, including failures, stay in the [initial host study](evals/results/2026-09-08-host-smoke/README.md), [assisted linkding study](evals/results/2026-09-08-linkding/README.md), [hardening record](evals/results/2026-09-08-product-hardening/README.md) and [native follow-up](NATIVE-FOLLOWUP-RESULTS.md). Test counts are not evidence of user benefit.

### Safety and evidence limits

- Use authorized test environments. Acceptance does not grant permission to change product code, write to production, push commits, or publish comments.
- Missing tools or observations remain gaps. A mock proves only the behavior tested against it; a narrower test must not silently replace the user's original request.
- The helper directly compares the CSV with fixed expectations. It does not run commands from reports or accept a supplied PASS. File hashes detect changed evidence, not fabricated collection or requirements omitted from the start.
- Reports stay local and are not automatically sanitized. Review them before sharing; keep credentials, private logs, and customer data out of public issues.

See the [material format](skills/functional-acceptance/references/material-format.md) for supported checks and trust boundaries.

## Development checks

```sh
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_lifecycle.py -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_identity.py -v
```

The first command tests the helper, evidence collector, relocatable Skill package and native example's safety/report contracts. The second tests the exporter independently of the Skill and helper. The third and fourth check the SQLite pack's process lifecycle and pre-import guard with synthetic controls, not its business flow. These commands do not run the host-dependent linkding browser journey. A passing defect-detection test does not make that export correct.

[`EVALUATION-HARNESS.md`](EVALUATION-HARNESS.md) documents the development-only write-once invocation ledger used for repeated evals. Its runner is outside `skills/functional-acceptance`, is excluded from installed package bytes, and does not grant command authority. It records one reviewed subprocess and fails closed on timeout, observer failure, retry, or a surviving owned descendant.

Installer integration checks are development-only and need Node 22.20+:

```sh
npm --prefix integration ci --ignore-scripts --no-audit --no-fund
npm --prefix integration test
```

They exercise the pinned `skills` CLI in disposable projects. No agent login or global Skill installation is required. These npm dependencies are not part of the installed Skill.

Before replacing an existing installation, use the [staged update guide](UPGRADING.md)
and read-only local-change check. [Reuse and recovery results](REUSE-RESULTS.md)
record interrupted-copy recovery, older material compatibility and repeated browser
journeys. Previously blocked host and unfamiliar-project work is recorded separately in the [native follow-up](NATIVE-FOLLOWUP-RESULTS.md), preserving those earlier failures.

[CI](.github/workflows/checks.yml) runs the Python suites on Ubuntu 24.04 with Python 3.10 and 3.14, plus a separate Node 22.22.3 installation job, using read-only permissions and commit-pinned actions. All three jobs passed for integration source `f4b1ef9` ([run](https://github.com/Quine-rq/functional-acceptance/actions/runs/34185450287)); [earlier M2 results](M2-RESULTS.md#remote-ci) retain a previous failure and its correction. Check the run for the commit you use; an earlier green build does not validate later changes.

## Documentation and next steps

- **Explore the Skill:** [instructions](skills/functional-acceptance/SKILL.md), [sample guide](examples/paginated_export/README.md), [material format](skills/functional-acceptance/references/material-format.md).
- **See what is implemented:** [M1 scope](M1-PLAN.md), [M1 validation](M1-RESULTS.md), [M2 hardening](M2-RESULTS.md), [roadmap](ROADMAP.md).
- **Understand the design:** [product design](DESIGN.md), [architecture](ARCHITECTURE.md), [evaluation plan](VALIDATION.md). These detailed documents are in Chinese; planned evaluations are not passing test results.

Next release gates: reliable full-flow execution in a second host, external developers using their own projects, and demonstrated benefit beyond the baseline. The [external-developer pilot](evals/HUMAN-PILOT.md) explains how unfamiliar users can participate without sharing their project or raw evidence. The [native follow-up](NATIVE-FOLLOWUP-RESULTS.md) explains the latest improvements and remaining failures. Passing local checks is not a supported-release claim.

## Feedback and licensing

Have a feature that looks successful but fails in actual use? Share its expected behavior and a small reproduction using synthetic data. Those cases are more useful at this stage than requests for broad platform support.

This project is available under the [MIT License](LICENSE).
Read [SUPPORT.md](SUPPORT.md) for the preview's support boundary, [SECURITY.md](SECURITY.md) before reporting a vulnerability, and [CONTRIBUTING.md](CONTRIBUTING.md) before preparing a pull request.
