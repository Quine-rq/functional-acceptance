# Functional Acceptance

**Verify real user outcomes, not just successful tool calls.**

A stack-independent acceptance Skill for existing coding agents, under active development. It uses project-native tools to check user journeys, distinguish evidence from assumptions, and leave reusable native checks.

> **Status: experimental M1 source, not a release.** A Skill entrypoint, offline material helper, and controlled local CLI/CSV sample now exist. This does not establish cross-project usefulness, universal tool support, production readiness, or a verified installation channel. Design revision `v0.2` remains a historical document version.

[中文设计说明](DESIGN.md) · [Architecture](ARCHITECTURE.md) · [Evaluation plan](VALIDATION.md) · [Roadmap](ROADMAP.md)

## The problem

An upload can return success while its file cannot be retrieved. An export can exit with code `0` while omitting the last page. A UI can show saved state that disappears in a new process.

The intended workflow starts with the user's promised result, identifies what existing tests do not prove, and obtains the missing observations using authorized project tools.

## Try the controlled local workflow

Prerequisites: Python 3.10+ and a POSIX local filesystem supporting hard links and no-follow file access. The current observed combination is macOS + Python 3.14.4; other combinations are not yet claimed as tested. No package installation, account, network service, or Skill installation is needed for these commands.

From the repository root, each command creates its own unique directory under the repository's `.acceptance/runs/` (not the caller's current directory). Use `--run-dir NEW_DIRECTORY` to select another new dedicated location:

```sh
python3 -B examples/paginated_export/accept.py --case healthy
python3 -B examples/paginated_export/accept.py --case defect
python3 -B examples/paginated_export/accept.py --case missing-observation
```

| Controlled case | Export process | Acceptance result | Collector exit |
| --- | --- | --- | --- |
| Healthy | Writes all five records | PASS, complete | 0 |
| Final-page defect | Exits 0 but writes only four records | FAIL with a content counterexample, complete | 1 |
| Withheld observation | Writes a file but deliberately omits its required observation record | UNVERIFIED, partial | 2 |

The last two exit codes are intentional; do not chain these demonstration commands with `&&`. Missing-observation is an explicit evidence-gap experiment, not a claim that the exporter failed. Each retained run contains the frozen contract, executed program/input snapshots, native process record, CSV, and JSON/Markdown reports. No prior run is reused or deleted. Inspect the printed run directory; when no longer needed, remove only that explicitly identified directory with your normal file manager. Deleting evidence removes its future qualification.

Only the **offline synthetic pages → actual CLI process → actual local CSV file** boundary is exercised. There is no real upstream API, browser, database, or mobile device. The report's fixed scope covers normal all-page export and field integrity; input-error and file-safety behaviors have separate native tests.

## Workflow

1. Preserve the original request and its acceptance criteria before selecting tools.
2. Choose a bounded plan using the execution and observation capabilities actually available.
3. Run the relevant native checks and retain evidence tied to the correct target, identity, and attempt.
4. Report **PASS**, **FAIL**, **UNVERIFIED**, or **NOT_APPLICABLE** within an explicit scope.
5. Account for unfinished work and side effects, then hand over reusable native checks.

A completed acceptance run may find a real failure. Successful execution, complete coverage, business correctness, and safe cleanup are different facts.

## Scope

- The method is intended for Web, API, CLI, desktop, and mobile workflows; support will be claimed only for combinations actually tested.
- Existing agents and project tools do the execution. This is not a new agent runtime, test language, device cloud, or deployment platform.
- Mocked dependencies can prove the behavior actually tested, not the real storage or delivery they replace.
- Missing tools or evidence stay visible. A narrower test must not silently replace the original request.
- Test environments are the default. Installation or verification does not authorize production writes, code changes, pushes, or public comments.

## Start here

| Document | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Focused acceptance, recheck, and plan-only instructions |
| [Material format](references/material-format.md) | The one supported CSV mapping, bounded references, report semantics, and trust limits |
| [Native sample](examples/paginated_export/README.md) | Run and verify the sample without installing the Skill |
| [M1 plan](M1-PLAN.md) | This implementation's explicit scope and acceptance gates |
| [M1 results](M1-RESULTS.md) | Actual local checks, independent replay, corrected defects, source identities, and unverified scope |
| [DESIGN.md](DESIGN.md) | Product definition, user experience, scope, and completion conditions |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Capability selection, evidence rules, budgets, recovery, and handoff |
| [VALIDATION.md](VALIDATION.md) | Planned counterexamples, strong baselines, natural invocation, and real-user evaluation |
| [CONTEXT.md](CONTEXT.md) | Shared domain terms |
| [DECISIONS.md](DECISIONS.md) | Design choices, source references, and unresolved questions |
| [ROADMAP.md](ROADMAP.md) | Small milestones with observable exit conditions |
| [AGENTS.md](AGENTS.md) | Working rules for coding agents contributing to this repository |

The detailed design is currently in Chinese. Its 38 cases and nine additional scenario groups remain the larger evaluation plan, not a count of passing implementation tests.

## Development checks

```sh
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v
```

The first command tests the helper and collector. The second is a standalone native regression pack; it does not import the Skill or helper. Passing a test that detects an injected defect is not a PASS for the defective export.

[CI configuration](.github/workflows/checks.yml) uses read-only repository permissions and commit-pinned official checkout/Python actions to run these same checks on Ubuntu 24.04 with Python 3.10 and 3.14. A configured matrix is not itself a passed support claim; inspect the actual Actions result for the commit you use.

The helper never executes recorded commands or accepts an arbitrary supplied PASS. It reads a qualified CSV and compares its header and rows with the frozen expectation. Digests detect changed evidence; they do not authenticate the collector, prove authorization, or detect goals omitted before contract creation. Reports stay local and are not automatically safe to publish.

## Next milestone

Continue the trust and independent-handoff checks in [ROADMAP.md](ROADMAP.md), then evaluate a second authorized project and fair with/without-Skill comparisons. A verified install/uninstall path, license decision, and release remain separate gates. Do not treat this source checkout as a supported installable release.

## Feedback and licensing

Concrete user journeys, missing observations, and reproducible failure cases are useful feedback. Use synthetic data; do not post credentials, private logs, or customer information in public issues.

License selection is pending. No open-source license has been applied to this repository yet.
