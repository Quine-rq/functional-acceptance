# Independent native handoff — healthy live run

This supplements the preparation-only record in `handoff-preparation.md`. It is an independent agent handoff, not human-user evidence. The author study and its outcomes were not read. The parent authorized one healthy run after reporting that ports 18741/18742 were free.

## Result and scope

The documented healthy journey ran once and exited 0 in 27.06 s (user 16.60 s, sys 5.91 s). Native result: business_verdict PASS, qualified_pass true, completion complete, obstacle_kind null, execution_cleanup stopped. All 24 recorded checks passed. No runtime fix, pack/source change, credential help, or journey retry was needed.

Command, from `<TASK_ROOT>/work/linkding-independent-handoff`:

```sh
/usr/bin/time -p .venv/bin/python <TASK_ROOT>/outputs/functional-acceptance/examples/linkding/accept.py --project <TASK_ROOT>/work/linkding-independent-handoff --browser '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' --case healthy
```

The command used scoped sandbox escalation to start the documented loopback services and fresh sandboxed Chrome. Authorization was already supplied; no automatic approval rejection occurred. Browser version recorded by the run: 152.0.7977.76; Python 3.14.4; source pin 65813a75404b1319aca8b09700fadc0b15adabaf.

Artifact directory: `.acceptance-study/artifacts/run-20260908T055443757097Z`. The safe derived checks are retained separately in `handoff-independent-observations.json`. Credentials and raw database contents were not printed. Native console event data was inspected programmatically and only derived facts were emitted.

## Independent evidence review

I read the result, pack identity, script snapshot identity, and all 112 persisted events. Persisted events matched the actual invocation's event output exactly. I re-compared raw field/object evidence instead of accepting only each stored PASS label:

- Invalid URL submission left the initial database baseline unchanged. The corrected URL fetched the expected local article metadata over real HTTP.
- The saved target was id 1, owned by the first ordinary synthetic account, shared=0, with the expected exact URL, multiline notes, and tags. Both new-browser and post-restart UI/independent database observations preserved this same object and its fields.
- The application actually changed PID from 75938 to 75995, with a stop/start pair and target id 1 correlated after restart.
- The second ordinary account's exact-id browser POST returned 404. Reopened owner UI and database evidence retained the original object unchanged.
- Edited notes and tags persisted. After deleting target id 1, control id 2 remained with its prior fields. After control cleanup the bookmark baseline was restored.
- Native event records show five fresh, sandboxed browser starts and five closes. All three owned service process starts have matching stop events. Three process-log records reported no drain errors or truncation; no unresolved-cleanup event occurred.

I visually inspected `server_restart_retrieval.png`, `bob-write-denied.png`, `unrelated-intact.png`, and `final-empty.png`. They show preserved multiline notes/tags after restart, the denied POST, the unaffected control, and the final empty bookmark list, respectively.

The executed regression SHA-256 equals the pre-run accept.py digest. Copied study_settings.py and article.html also match their pre-run pack inputs. `git status --short --untracked-files=no` remained empty after execution.

Final independent SQLite check (read-only):

```sh
sqlite3 -readonly .acceptance-study/db.sqlite3 "SELECT 'all_bookmarks=' || COUNT(*) FROM bookmarks_bookmark; SELECT 'target_and_control_remaining=' || COUNT(*) FROM bookmarks_bookmark WHERE id IN (1,2);"
```

Returned `all_bookmarks=0` and `target_and_control_remaining=0`. These counts agree with the initial empty baseline and final event observation. No authentication or session tables were inspected.

Final process observations:

```sh
lsof -nP -iTCP:18741 -iTCP:18742 -sTCP:LISTEN
ps -p 75936,75938,75995 -o pid=,ppid=,etime=,command=
```

The lsof command returned exit 1 with no listeners. The first ps observation was denied by the default sandbox (`operation not permitted: ps`, exit 127); the identical read-only command was rerun with scoped escalation and returned exit 1 with no processes. This was an observation permission retry, not a journey retry. No process was killed manually. Native browser close events were correlated; the report does not publish browser PID/profile identities, so it is not an independent OS-level proof for every browser descendant.

## Assistance, missing instructions, and limitations

The assignment supplied the already-pinned offline clone seed, dependency cache locations, Chrome path, and the shared-port hold/release. The README itself does not spell out the exact clone/checkout command or offline cache overrides. Preparation and execution did not require author assistance beyond those environment details and execution scheduling.

The one direct artifact inconsistency found is in screenshot filtering: `snap()` says it avoids Django debug error pages, but it excludes only `#traceback` / `#requestinfo`. The captured `bob-write-denied.png` is a Django DEBUG 404 page with request method/path, view identifier, and internal URL patterns. No credential is visible in the inspected screenshot. This does not invalidate the measured bookmark authorization behavior, but the broad no-debug-page-capture claim is unsupported and the artifact should not be treated as automatically safe to publish. No pack modification was made to hide this observation.

This single independent healthy run demonstrates the documented happy path plus its included validation/restart/isolation/edit/delete boundaries on this macOS/Chrome environment. It does not independently verify the four other named control cases, other platforms, hard-kill recovery, production deployment, or a human reader's ability to execute the guide unaided.

All synthetic state and artifacts are retained locally. The successful run removed its own target/control bookmarks through the UI. No source edit, commit, or push occurred.
