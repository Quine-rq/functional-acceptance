# Functional Acceptance

[简体中文](README.zh-CN.md)

**The feature is built. Does it work for the user?**

Functional Acceptance is a skill for coding agents to verify features through real user flows. It guides the agent to check the promised result, show the evidence, and leave tests that can be run again.

For example: an export command reports success, but the CSV is missing the final record. Acceptance means opening the file and checking its contents—not stopping at exit code `0`.

> Development preview: runnable CLI/CSV and browser/database examples are available. This is experimental source, not a supported release.

## How it works

Start with the feature's requirements and the project you want checked. The Skill guides your coding agent through three steps:

1. **Define success.** Identify what the user needs to accomplish and what would prove it worked. Keep unclear requirements and missing access visible.
2. **Check the result.** Use the project's existing tools to run the flow and inspect the outcome. Focus on relevant failure and recovery cases as well as the happy path.
3. **Hand over the findings.** Report what passed, what failed, and what remains unverified, with evidence and instructions for repeating the checks.

The Skill provides the workflow; the agent and project tools perform the checks. It does not replace your test framework or approve a release. It maps requirements to actual assertions, distinguishes a product defect from a broken test, and keeps missing evidence visible. Start with the local export demo below, or follow the [maintained linkding example](examples/linkding/README.md) for a browser/database journey.

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

## Use with your coding agent

The development Skill is now a self-contained directory at [`skills/functional-acceptance/`](skills/functional-acceptance). It uses the Agent Skills format and ships no agent runtime. The optional CSV helper has separate Python/POSIX requirements; planning does not require it.

For a first installation into a project, see the [installation guide and measured coverage](INTEGRATIONS.md). It covers Codex, Claude Code, Cursor, GitHub Copilot and OpenCode installation targets using a pinned ecosystem installer, with local testing and explicit upgrade/removal precautions. **Installation checks are not proof of successful agent execution.**

Once your host has loaded the Skill, try: “Use functional-acceptance to plan how to verify this feature. Do not run the application yet.” Supply the feature's expected behavior and project location. Actual acceptance then uses that host's authorized project tools.

[Native follow-up checks](NATIVE-FOLLOWUP-RESULTS.md) now include Codex old/new-Skill comparisons, actual Claude Code read-only history reviews, and sqlite-utils onboarding followed by separate no-Skill replay and maintenance. Claude's latest explicitly loaded trials correctly kept insufficient history unverified; natural loading and healthy-history discrimination remain unproven. Codex still sometimes omits a required failure branch. These small studies do not establish a general advantage over the baseline. [Earlier failures and corrections](evals/results/2026-09-08-host-smoke/README.md) remain available.

## Compatibility and current limits

The workflow is designed to use tools already available in a project, rather than require a particular language or framework. Web, API, CLI, desktop, and mobile flows are intended applications—not a list of tested integrations.

The bundled example covers **synthetic pages → real Python process → local CSV file**. The report checks complete export and exact field values; input errors and file safety have separate tests.

The [sqlite-utils pack](examples/sqlite_utils/README.md) checks contact import, retrieval by another process, JSON export, duplicate-key rejection and unrelated-data preservation. A generated pack passed independent no-Skill replay; review then exposed and corrected a timeout that could leave a child writer alive. The reusable example includes that correction and separate process-lifecycle tests. Dependencies were prepared in advance; cold installation and external-human handoff are not demonstrated.

The [maintained linkding pack](examples/linkding/README.md) uses real browser login, a real server restart, private-account isolation, editing and scoped deletion, with independent SQLite observations. It includes note-loss, missing-observation, session-loss and lost-response controls, plus a Unicode maintenance exercise. It runs without the Skill or helper. [The hardening record](evals/results/2026-09-08-product-hardening/README.md) separates author runs, independent agent handoff and harness defects; the [original assisted study](evals/results/2026-09-08-linkding/README.md) is unchanged. This is a pinned native example, not a generic browser adapter or external-human usability proof. External services and mobile devices remain unverified.

The [M1 validation record](M1-RESULTS.md) documents the first 77 passing test methods and an independent agent's replay of the standalone sample. [M2 report-delivery checks](M2-RESULTS.md) brought the suite to 84 methods, including interruption, disk failures, and incomplete handoff. Current packaging and installation checks are tracked [separately](INTEGRATIONS.md). These results do not establish external-user usefulness, time savings, or production readiness. A supported release remains pending; cloning the source alone does not install the Skill.

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

Next release gates: reliable full-flow execution in a second host, external developers using their own projects, demonstrated benefit beyond the baseline, and license/security-support decisions. The [native follow-up](NATIVE-FOLLOWUP-RESULTS.md) explains the latest improvements and remaining failures. Passing local checks is not a supported-release claim.

## Feedback and licensing

Have a feature that looks successful but fails in actual use? Share its expected behavior and a small reproduction using synthetic data. Those cases are more useful at this stage than requests for broad platform support.

License selection is pending. No open-source license has been applied to this repository yet.
