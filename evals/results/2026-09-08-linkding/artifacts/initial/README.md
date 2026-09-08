# linkding functional acceptance — blocked execution

Target checkout: `65813a75404b1319aca8b09700fadc0b15adabaf`.
Evidence collected by the primary Codex executor on 2026-09-08 (UTC), using native Python 3.14.4. Authority and credential references: `../ENVIRONMENT.md`. Only owned artifacts were written; no product code, publication, installs, external services or existing browser profiles were used.

## Result

**The requested user outcome remains UNVERIFIED.** The first prerequisite process exited before an application or browser could start. One diagnostic probe reproduced an operating-system denial at `socket.bind(('127.0.0.1', 18742))`: `PermissionError: [Errno 1] Operation not permitted`. This is an observed execution-environment failure, not evidence of a linkding product defect. The current execution policy forbids privilege escalation; no escalation or alternative service was attempted.

| Obligation | Status | Evidence / gap |
|---|---|---|
| Normal browser login as ordinary accounts | UNVERIFIED | Browser never started |
| Invalid-URL visible feedback and correction in the same form | UNVERIFIED | No form interaction |
| Save private bookmark with exact tags and multiline notes | UNVERIFIED | No bookmark created |
| Retrieve exact bookmark after a completely fresh browser | UNVERIFIED | No browser session |
| Retrieve exact bookmark after actual server process restart | UNVERIFIED | Application never started |
| Other ordinary account cannot view exact private bookmark | UNVERIFIED | No authenticated isolation check |
| Other ordinary account cannot modify exact private bookmark | UNVERIFIED | No adversarial browser form submission |
| Edit and reopen persisted fields | UNVERIFIED | No edit performed |
| Delete target and verify absence | UNVERIFIED | No deletion performed |
| Unrelated bookmark remains intact after target deletion | UNVERIFIED | No control bookmark created |

No product checks passed or failed. No mocked unit tests or API successes were substituted. There are no browser screenshots because there was no browser observation.

## Attributable evidence and termination

- `run-20260908T051537050247Z/events.jsonl`: timestamped first attempt, checkout/script identity, synthetic inputs, owned PID and setup obstacle.
- `run-20260908T051537050247Z/result.json`: all eleven obligations UNVERIFIED; child article PID `65518` terminated with exit code `1`; port 18742 closed at final observation. Regression command itself exited `1`.
- `run-20260908T051537050247Z/diagnostic-1.txt`: retained diagnostic command, terminal traceback and exit status. This was the only diagnostic probe, not a second whole journey.
- `run-20260908T051537050247Z/executed_regression.py`: exact script from the first attempt, matching its logged SHA-256.
- `acceptance_regression.py`: handoff version, with safer debug-page evidence suppression, explicit early-child-exit logging and tag-order-independent control comparison. Syntax compilation passed; this revised version has **not** been executed. These artifact-only changes did not address or bypass the runtime denial.

All spawned work terminated. No application or browser processes were created; no bookmarks or other application data were written. No unresolved process/data cleanup from this attempt. Existing untracked `.agents/`, `skills-lock.json` and study environment were left alone.

## Native rerun

From this checkout, in an execution environment that permits the two authorized loopback listeners:

```sh
.venv/bin/python .acceptance-study/artifacts/acceptance_regression.py
```

Prerequisites remain exactly those in `../ENVIRONMENT.md`: installed locked dependencies, existing Chrome, migrated real study database, two ordinary accounts and local credentials, built assets, article fixture, ports 18741/18742 free. Do not weaken browser sandboxing or use an existing profile. The script does not install anything and refuses to take over an occupied port.

The regression starts and owns the real article/application subprocesses, uses sandboxed headless Chrome with new contexts and normal credential form login, keeps secrets in memory, restricts page HTTP requests to the two approved endpoints, and writes a new timestamped evidence directory. It does not use force-login, injected authentication cookies, a test database, metadata mocks, traces or raw database dumps.

The planned assertions freeze a unique URL, title, tags and multiline notes before saving; correlate the UI's exact bookmark ID across fresh browser launches and terminated/restarted application PIDs; attempt Bob's direct details/edit access and a real browser form POST to Alice's exact ID using Bob's own normal-login CSRF; reopen Alice's fields to detect unauthorized mutation; edit and reopen; delete through confirmation; then verify the separate control's fields are unchanged. Bob's POST intentionally changes only the form destination as an adversarial authorization test; the ordinary save/edit/delete path uses actual UI controls.

It stops on the first obstacle, preserves evidence and known IDs, and closes owned browser/server resources in `finally`. It never silently retries a journey. On a successful future run, the control bookmark is removed only after checking it survived target deletion. Unused run-specific tags may remain; on an interrupted future run, bookmarks identified in `result.json` may remain. Inspect those exact IDs through normal login before deciding on cleanup; do not rerun a failed write blindly or reset the database.

Limits: this is a prepared, syntax-checked native regression, **not a proven passing regression**. Its browser selectors and assertions still require first live execution. A future developer should inspect each result/evidence file and distinguish assertion counterexamples from harness/environment obstacles. No independent executor has followed the handoff. This scope also does not claim weak-network/concurrency/mobile-device acceptance or behavior against public websites; the article is explicitly synthetic real loopback HTTP.
