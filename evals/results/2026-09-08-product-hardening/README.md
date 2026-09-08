# Product-hardening evidence — 2026-09-08

This record separates Skill behavior, native application observations, harness
faults and external prerequisites. It is not a supported-release or human-benefit
claim. The [implementation contract](../../../PRODUCT-HARDENING.md) predates
the controls; [the results](../../../PRODUCT-HARDENING-RESULTS.md) give the
product-level conclusion. Earlier studies remain unchanged.

## Native application journey

Application: linkding commit `65813a75404b1319aca8b09700fadc0b15adabaf`, isolated
SQLite database, two ordinary synthetic accounts, local article, real sandboxed
Chrome 152.0.7977.76, Python 3.14.4 and locked application dependencies. No
production target or upstream code change. The `note-loss` case is a deliberately
injected pre-save signal, not an alleged upstream defect.

The [maintained pack](../../../examples/linkding/README.md) runs without the
Skill or CSV helper. It verifies UI fields and exact database objects, including
restart, account isolation and preservation of unrelated bookmark rows.

Author control matrix, after the debug-page/snapshot change and before the later
signal/diagnostic changes; all attempts are retained, not just these outcomes:

| Case | Actual result | Wall time |
| --- | --- | ---: |
| healthy | PASS / 0 | 24.896 s |
| note-loss | Expected FAIL / 1; saved notes actually empty | 6.727 s |
| missing-observation | Expected UNVERIFIED / 2 despite otherwise successful steps | 26.303 s |
| expired-session | PASS / 0; same object after normal login | 99.097 s |
| lost-response | PASS / 0; real POST 302 observed before response loss, one object and no resubmit | 39.607 s |
| unicode-notes | PASS / 0; exact Chinese/quotes/emoji/multiline notes after restart | 53.424 s |

See [controller results](controllers/hardening-controls-final/results.json),
[all native attempts](native-summary.json) and each run's captured script identity.
The earlier four-case author control run and initial healthy run are also kept.
Runtime variation, especially browser closing, remains a limitation; these are
not steady-state performance measurements.

### Independent handoff and the counterexample

An independent agent first prepared a fresh checkout and ran healthy once:
24 checks, 27.06 seconds, no pack/source correction. The assignment supplied an
offline clone seed, cached dependencies, browser path and port scheduling; it was
not a zero-assistance external-user installation. Its review discovered that the
original screenshot filter still captured a Django DEBUG 404 page. That unsafe
capture is not exported. The filter now omits recognized debug 404/500 and login
pages; authorization remains evidenced by HTTP status and unchanged objects.

A later independent matrix on the stop-safe candidate stopped at its first
unexpected result, as required:

| Case | Actual result | Wall time |
| --- | --- | ---: |
| healthy | PASS / 0 | 32.249 s |
| note-loss | Expected FAIL / 1 | 5.714 s |
| missing-observation | Expected UNVERIFIED / 2 | 50.795 s |
| expired-session | **Unexpected UNVERIFIED / 2: control cleanup timed out** | 90.329 s |
| lost-response / unicode-notes | Not executed in this matrix | — |

The expired-session run successfully reauthenticated and reopened the same object.
After permissions, editing and target deletion also passed, cleanup of control
id `9` timed out. Earlier failed bookmark id `5` was unchanged; target id `8` had
been deleted. Service processes stopped. This is incomplete data cleanup, not a
qualified journey PASS or evidence of a broken session feature. The old script
did not retain the exact failing locator, so the root cause of that intermittent
timeout is **not established**.

The current pack adds private redacted exception details, per-action receipts,
exact modal-object checks and one shared role-based confirmation sequence. Any
subsequent diagnostic recheck is recorded separately, never substituted for the
failure. A later successful run alone does not demonstrate the flake is eliminated.

The explicit diagnostic recheck subsequently produced:

| Case | Actual result | Wall time |
| --- | --- | ---: |
| expired-session | PASS / 0, same object recovered and baseline restored | 29.657 s |
| lost-response | PASS / 0, one object after response loss and baseline restored | 28.607 s |
| unicode-notes | **Unexpected UNVERIFIED / 2: Confirm disappeared before click** | 32.945 s |

Unicode values matched exactly in both UI and database after restart and editing.
The target `14` and control `15` remained because deletion was not completed;
earlier rows `5` and `9` were unchanged. The visible assertion passed, but the next
screenshot no longer contained Confirm and the click timed out. That establishes
an observation/click gap, not its cause or equivalence to the earlier timeout.
[Diagnostic records](independent/diagnostic-results.json) and
[the diagnostic report](independent/diagnostic-report.md) preserve all three runs.
One independent field was named `old_id5_and_id9_full_rows_preserved` but actually
compared the entire dataset with the baseline. Its false value is retained;
[the supplemental observation](independent/diagnostic-review.json) distinguishes
unchanged prior rows from incomplete cleanup instead of rewriting the raw label.

Read [independent results](independent/final-results.json),
[its report](independent/final-candidate-report.md) and
[the initial handoff](independent/handoff-live.md). The actual directory field is
`run_dir`; the lowercase business run id is not used as a filesystem path.

### Navigation readiness: a controlled timing counterexample

Ten bounded, non-destructive UI observations did not reproduce the disappearance.
A separate single-round observation did establish this actual sequence: the modal
was visible before frame completion, and `turbo:frame-load` was followed by a
promoted history visit, `turbo:before-cache`, render and finally the matching
`turbo:load`. Neither visible DOM, the changed URL nor frame completion alone was
a sufficient whole-visit boundary. The [frame contract](https://turbo.hotwired.dev/reference/frames)
and [event contract](https://turbo.hotwired.dev/reference/events) distinguish these
scopes; local observations establish the ordering in this pinned application.

The first three-round scheduling probe intercepted the next animation callback,
which turned out to update the progress bar. It **missed** the navigation stage
and did not reproduce the symptom. Its negative results are retained, not omitted.

A new bounded probe used the captured bundle hash and exact render callsite
(`bundle.js:19:11228`, callback `()=>e()`) to delay only that real callback by
150 ms. Other callbacks passed through. It did not synthesize, cancel or suppress
Turbo events. All three rounds recorded: Confirm appeared, the delayed navigation
resumed, the real `turbo:before-cache` ran, and the dropdown disappeared. This is
a controlled scheduling counterexample, **not proof of the original two natural
timeouts' cause**. It also does not establish that early-click behavior in upstream
linkding is fixed.

The candidate native regression now observes the matching `turbo:load`, with its
listener armed before the View click and released on success or failure. A missing
completion remains a timeout; no fixed sleep, invisible force-click, extra Delete
click or automatic journey retry was added. Four lifecycle tests were run failing
before implementation and passing afterward. The real timing probe, not mocked
page calls, is the behavioral regression seam.

Using the actual new helper with the **byte-identical timing injection**, all
three recheck rounds observed cache → matching load → helper return → Delete →
Confirm. Confirm remained visible throughout the same 450 ms observation window
and was then explicitly cancelled. This demonstrates the new wait handles this
controlled scheduling window; it does not certify every natural timing or fast
interaction during an unfinished navigation. See the
[timing recheck](diagnostics/raf-render-wait-recheck/result.json).

[Uninjected observations](diagnostics/handoff-ui-debug/result.json) ·
[readiness observation](diagnostics/readiness-contract-probe/report.md) ·
[missed scheduling probe](diagnostics/raf-scheduling-injection/result.json) ·
[controlled counterexample](diagnostics/raf-render-callsite-injection/report.md).

These probes logged in normally, which can write authentication sessions. They
did not click Confirm or send bookmark business writes; bookmark rows were checked
unchanged. “Read-only UI diagnosis” is not a claim of zero filesystem/session writes.

### Current candidate: full independent recheck

After the readiness change, the independent executor ran each complete journey
once, in sequence, without the artificial scheduling delay. It would stop at the
first unexpected result; no retries were used. All six matched their frozen
expectations, including the intentionally failing and unverified controls:

| Case | Actual result | Wall time |
| --- | --- | ---: |
| healthy | PASS / 0 | 16.350 s |
| note-loss | Expected FAIL / 1; counterexample id `18` retained | 4.685 s |
| missing-observation | Expected UNVERIFIED / 2 | 16.960 s |
| expired-session | PASS / 0 | 18.182 s |
| lost-response | PASS / 0 | 18.673 s |
| unicode-notes | PASS / 0 | 17.380 s |

Old bookmark rows and tag associations were unchanged. Completed cleanup removed
only each run's own target/control, except the deliberately retained note-loss
counterexample. The final retained IDs were `[5,9,14,15,18]`; this is not an empty
database or retroactive cleanup of failed runs. Process and data cleanup are
reported separately in [the final matrix](independent/readiness-final-results.json)
and [independent review](independent/readiness-final-report.md).
The [current Unicode confirmation screenshot](images/current-unicode-delete-confirmation.png)
shows the retained notes and actual Confirm button; exact fields and the final
deletion are established by the accompanying UI/database events, not pixels alone.

These are one-per-case rechecks of a pinned example, not a reliability percentage,
proof that every prior flake is eliminated, or validation of early clicks before
navigation finishes. Previous failed runs, the missed timing probe and all raw
observations remain available alongside these outcomes.

### Interrupted execution and report delivery

The first SIGTERM probe hung after the script threw `KeyboardInterrupt` inside a
synchronous Playwright call. Its supervisor terminated the owned process group
after 130.018 seconds; no final receipt was delivered. Read-only process/port
checks afterwards found no recorded services/listeners. This is retained as a
failure, not normal `finally` cleanup or proof about every browser descendant.

The fix records a signal and exits at explicit native-call boundaries, rather
than unwinding Playwright's dispatcher. The real failing probe and a regression
test were run before the change. A similar failure pattern is documented in
[Playwright's upstream issue](https://github.com/microsoft/playwright-python/issues/1150);
that report is precedent, not proof of a defect in every current Playwright version.

Corrected probes:

| Probe | Actual outcome |
| --- | --- |
| SIGTERM | 6.221 s, exit 2, UNVERIFIED/interrupted, owned services stopped |
| Existing pending receipt | 38.239 s, exit 2, no final result; the pre-existing pending bytes survive and owned services stop |
| Occupied application port | 0.397 s, environment/UNVERIFIED; no browser login, own article service stops, unowned listener survives |

[Failed probe](controllers/hardening-native-faults/results.json) ·
[corrected probes](controllers/hardening-native-faults-fixed/results.json).
This report does not certify SIGKILL, power-loss or every browser-descendant cleanup.

## Actual host behavior, not installer labels

The paired input contains an ordinary export requirement, a header-only smoke
test and a controlled `pages[:-1]` defect. Expected records are in a three-page
fixture. Neither host prompt is handed a desired verdict. Both configurations use
the same native Codex executable/version/default configuration, prompt and protected
input bytes, apart from the installed Skill. Separate fresh directories and raw
tool traces are retained. Each request asks for at most two minutes; an outer
180-second guard preserves timeout failures rather than retrying.

Current comparison: three coverage trials, one plan-only trial and one historical
review per configuration. A single old-Skill coverage run is kept separately.

| Observation | With Skill | Without Skill |
| --- | ---: | ---: |
| Correctly detected missing `r-005` from actual CSV | 3/3 | 3/3 |
| Entire graded request covered | 4/5 | 4/5 |
| Passed individual expectations | 22/23 | 21/23 |
| Actually read installed Skill body | 4/5 | No repo Skill installed |
| Mean native wall time, uneven five-case mix | 52.630 s | 46.478 s |

Both coverage trial-2 outputs omitted the live existing-output rejection check.
The Skill run disclosed that gap as UNVERIFIED; the baseline also omitted that
disclosure. All seven actual CSVs, including the old-Skill run, contain identical
147-byte content: the first four exact records, missing the fifth. Independent
grading parsed actual files and inspected complete traces; it did not grade
presence of the word FAIL or trust the final prose alone.

The installed historical-review run listed the Skill path but did not read its
body. Both history reviews stayed within their task's read-only boundary, but the
installed run is **not evidence of Skill activation**. The file manifest excludes
`.git`, `__pycache__` and empty directories; the harness created an empty Git repo
before the baseline snapshot. Do not claim all filesystem/global host activity
was absent.

[Descriptive benchmark](benchmark.json) · [per-run summary](behavior-summary.json) ·
[example with a disclosed gap](behavior/codex-coverage-with-v2/final.md) ·
[its independent grading](behavior/codex-coverage-with-v2/grading.json).
Final-message artifact links resolve from the corresponding retained `project/`
working directory, not this report's root. The example corpus and each tested
Skill copy are retained with the original inputs and actual artifacts.

Native input/output/cached token counters are kept; they are not output-character
estimates or currency costs. The benchmark corrects the supplied aggregator's
output-character fallback using those native counters. Inherited global settings
were not isolated, model identity was not emitted, some trials overlapped, and
the grader was an agent, not blinded human users. Tiny descriptive differences
do not establish better reliability, lower cost or useful time savings.

### Second host blocked

Claude Code 2.1.220 was actually invoked for both coverage configurations. Both
returned authentication 403 before task-tool execution. Its structured result
used subtype `success` **with `is_error: true` and process exit 1**; subtype alone
is not task success. [Privacy-reviewed receipts](host-blockers.json) retain that
distinction and raw-trace hashes. Private provider routing/migration text remains
local. No credentials were sent to a suggested new endpoint or migrated, and no
global configuration was changed. This host's task behavior remains unverified.

## Reproducibility, maintenance and privacy

- `behavior-manifest.json` and `native-manifest.json` retain original and exported
  SHA-256 values. Only task-root/home paths are normalized. CSV and selected PNG
  bytes are unchanged. This verifies retained bytes, not authentic collection.
- Complete executed native Python snapshots are retained on later runs. The
  initial version captured only the entrypoint bytes plus support-file hashes;
  do not pretend its missing historical helper bytes were reconstructed.
- The new Unicode exercise extends one notes fixture and reuses every persistence,
  isolation and deletion check without upstream source changes. It measures an
  author-controlled maintenance task, not a user's future change or net savings.
- Preparation required local dependency caches after initial default-cache and
  offline npm misses. No dependency upgrades were used to obtain green. Independent
  preparation and any supplied help are described in its preparation record.
- No reliable human-time accounting exists. Do not report execution seconds as
  total preparation, diagnosis, review or maintenance cost.
- Credentials, raw databases, process private logs, debug error captures and private
  exception dumps remain local. Selected images contain synthetic data only. The
  upstream [MIT notice](../2026-09-08-linkding/LINKDING-LICENSE.txt) applies to linkding
  material; this project's license decision is still pending.
- `harness/*.txt` captures the controller source with local paths normalized. It
  documents actual orchestration, not a portable Skill runtime or one-command
  provisioner. Use the maintained pack's guide for native replay.

## Recheck this record

```sh
python3 -B evals/results/2026-09-08-product-hardening/check_record.py
```

This verifies manifests, actual CSV fields, the stopped independent matrix and
preserved fault results. **It does not rerun a model or browser, turn an expected
record into a product PASS, or certify production readiness.** Ordinary CI runs
this consistency check; live host/browser trials still require an authorized
environment. External developers, second-host task execution, broader controls,
upgrade recovery, licensing and a security-reporting route remain release gates.
