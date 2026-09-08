# Real bookmark acceptance, using linkding

This maintained native pack verifies one real browser → Django → SQLite journey.
It is a development example, not a universal browser adapter or an upstream fix.
It runs without an agent, the Skill, or the CSV helper. The original assisted
study and its failures remain [unchanged](../../evals/results/2026-09-08-linkding/README.md).

## Prepare once

Use a **fresh isolated clone**, never a production/development database. Review
these scripts before executing them. Keep the upstream MIT license. The pinned
source is `65813a75404b1319aca8b09700fadc0b15adabaf` from
[sissbruecker/linkding](https://github.com/sissbruecker/linkding).

Choose a new directory name; these commands refuse an existing destination:

```sh
git clone https://github.com/sissbruecker/linkding.git linkding-acceptance
cd linkding-acceptance
git checkout --detach 65813a75404b1319aca8b09700fadc0b15adabaf
```

In that clone, install the locked dependencies and build assets:

```sh
uv sync --frozen --python python3.14
npm ci --ignore-scripts --no-audit --no-fund
npm run build
```

Downloads require network permission. Python 3.14, the upstream locked Playwright
and a pre-existing Chrome/Chromium executable are needed. No browser is downloaded
and no shared browser profile is used. Use the clone's `.venv/bin/python` below.
The locally exercised platform is macOS; other OS/browser combinations must be
measured before claiming support.

Substitute absolute paths for `PACK`, `PROJECT`, and `BROWSER`:

```sh
.venv/bin/python /PACK/prepare.py --project /PROJECT
.venv/bin/python /PACK/accept.py --project /PROJECT --browser /BROWSER --case healthy
```

`PACK` is this directory; its Python files and `environment/` must stay together.
Preparation creates only a new `.acceptance-study/` with an isolated database,
two ordinary synthetic users and a local article. It refuses existing state,
including interrupted preparation, instead of replacing it. Inspect its receipt;
preserve partial state and use a fresh clone if preparation needs to be repeated.
Secrets remain in owner-only `private.json`; do not print or publish it.

## Frozen control expectations

Run one case at a time. Each invocation uses fresh URLs and a fresh evidence
directory. No case automatically retries the journey.

These are expected outcomes, not a claim that every retained run passed.
[Independent reruns](../../evals/results/2026-09-08-product-hardening/README.md)
also exposed intermittent confirmation/cleanup failures. Inspect those records
before relying on this development example as an unattended gate.

The current pack waits for the matching details navigation to finish before
interacting with its modal. It observes `turbo:load`, not a fixed delay. The retained
timing controls show why visible frame content alone was insufficient. This does
not certify early clicks during in-progress navigation or fix upstream behavior.

| Case | Expected result | What actually differs |
| --- | --- | --- |
| `healthy` | PASS / exit 0 | Save exact notes/tags, fresh login, actual server restart, role isolation, edit and targeted deletion; database agrees and baseline unchanged |
| `note-loss` | FAIL / exit 1 | Explicit runtime mutation clears bookmark notes before Django saves; fresh UI must expose loss. This is not an alleged upstream defect |
| `missing-observation` | UNVERIFIED / exit 2 | Required independent database observation immediately after server restart is deliberately withheld, even when UI and other steps succeed |
| `expired-session` | PASS / exit 0 | Browser session cookie removed; login required, then normal login recovers the exact existing object without another save |
| `lost-response` | PASS / exit 0 | Browser route forwards the real POST, then drops its response. Inspect the persisted object before any retry and recover it without resubmission |
| `unicode-notes` | PASS / exit 0 | Maintenance exercise: extend the original notes fixture with Chinese, quotes, emoji and another line; all the same persistence/isolation/edit checks must still hold |

Cookie removal tests loss of browser session, not every server-side token expiry
mechanism. Lost-response tests this specific completed POST boundary, not general
offline recovery. The note-loss signal runs only in the explicitly selected local
application process and does not edit upstream source. Every case retains the
effective runtime/mutation identity.

## Inspect the result

Read the new `.acceptance-study/artifacts/run-*/result.json`, `events.jsonl`,
complete `native-pack/` snapshot, pack/environment digests and screenshots together.
The server runs from the captured script. Settings, article, dependency locks and
static assets are fingerprinted; a changed source or environment blocks a qualified
result. This is run identity, not a hermetic capture of the OS or installed packages.
`business_verdict`,
`completion`, `obstacle_kind`, `execution_cleanup` and `data_cleanup` are separate. Only qualified
scoped PASS exits zero. A failed observation/assertion may leave later checks
UNVERIFIED. A test/locator/observer fault is not an automatic business defect.

Startup stdout/stderr are drained into bounded, owner-only `*.private.txt` logs.
Known test secrets are redacted; arbitrary logs are **not certified safe to share**.
These logs remain local. Truncation and log-drain errors are recorded. Evidence
publication failure keeps the handoff incomplete; a pending file is not a report.
Recognized Django debug 404/500 pages and login pages are omitted from screenshots
and body-text capture. Status and unchanged-object observations still establish
the authorization check. All other artifacts still need privacy review before sharing.
Unexpected exceptions retain a redacted owner-only `obstacle.private.txt` with the
exact failing operation. It is a local diagnostic, not a publishable evidence file.

The pack binds only `127.0.0.1:18741/18742`, refuses occupied ports, starts fresh
sandboxed Chrome profiles and stops its own process handles in `finally`. It also
handles SIGTERM; SIGKILL/power loss cannot guarantee cleanup. After a hard kill,
inspect recorded identities and actual listeners before doing anything else.
Never kill a process solely because an old PID appeared in a report.

Failure retains written bookmarks and evidence. Successful cleanup removes only
the current run's target/control, checking all prior bookmark rows are unchanged.
Synthetic users, sessions, unused tags and evidence remain. There is no blind
delete, resume, automatic resubmission or promise of an empty database.

## Handoff and maintenance

An independent executor should use this guide in another fresh clone, then compare
the exact outcome and process/object evidence—not just the command's exit code.
Record any missing instructions or author help before changing this guide.
Changing an expectation requires a reviewed requirement change; keep the old
contract and run history. The current pack pins upstream source and refuses a
different/modified revision, so a source upgrade requires review and new evidence.

Record-checking is not a live application test. Standard repository CI checks the
pack's verdict/IO contracts, not these host-dependent browser journeys. Results
and remaining release gates belong in the product-hardening report.
