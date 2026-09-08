# linkding: a real project, with author-assisted acceptance

**The complete bookmark journey passed in the final assisted run. The independent Skill invocation did not complete it.** Both outcomes matter: a real browser/application/database workflow is now demonstrated, but autonomous cross-project usefulness is not established.

中文摘要：在真实 linkding 项目中，已验证保存、重新登录、服务重启后找回、跨账号隔离、编辑和删除，并核对 SQLite 中的同一对象及未受影响的数据。独立 Skill 会话被本地端口权限阻断；后续由作者补充观察、修正回归脚本后跑通。不是零干预成功，不是生产可用性或通用适配证明。

## What actually ran

- Target: [sissbruecker/linkding](https://github.com/sissbruecker/linkding/tree/65813a75404b1319aca8b09700fadc0b15adabaf), commit `65813a75404b1319aca8b09700fadc0b15adabaf`. Both local checkouts retained unchanged tracked source.
- Skill: unchanged package from Functional Acceptance `4e4836ba70ad092b6751a4a0b2840db6b026c029`, installed locally for the independent invocation. The later native replay checkout had no project Skill installation; its Python script does not invoke a model or the CSV helper.
- Runtime: macOS, Python 3.14.4, Django 6.0.7, Playwright 1.62.0, Chrome 152.0.7977.76 with fresh profiles and browser sandbox enabled; Node 22.22.3 built the upstream frontend from its lockfile.
- Real components: normal username/password browser login, rendered forms, Django request handling, HTTP metadata parsing and SQLite persistence. Synthetic inputs: two ordinary accounts and a loopback-served article. No metadata mocks or forced login. Background jobs, external archiving, previews and favicons were disabled through isolated settings.

The [pre-execution plan](PLAN.md) fixes five business requirements. The native tests use attributed observations, not a new helper mapping. [Runtime inventory](runtime-inventory.json) records lockfile/build/settings digests; compiled-asset hashes were captured after execution, not as a pre-run snapshot.

## Final scoped result

Run [`052630285071Z`](artifacts/replay/assisted-run-20260908T052630285071Z/result.json), 05:26:30–05:27:20 UTC on 2026-09-08, took 50.473 seconds. Its 24 subchecks belong to **one journey**, not 24 independent samples. [Native events and database observations](artifacts/replay/assisted-run-20260908T052630285071Z/events.jsonl) and the [exact executed script](artifacts/replay/assisted-run-20260908T052630285071Z/executed_regression.py) support the following results.

| Requirement | Observed result | Verdict |
| --- | --- | --- |
| LD-1: invalid input, correction and save | `http://` produced a visible validation error without changing the database. Corrected URL loaded its exact local article metadata; bookmark `3` retained the intended title, tags, multiline notes and private ownership | PASS |
| LD-2: return after fresh browser and server restart | Normal login in fresh Chrome processes retrieved bookmark `3`. Application PID `68112` terminated before replacement PID `68173`; fields and SQLite row still matched | PASS |
| LD-3: edit persists without duplication | Bookmark `3` kept its ID, gained the intended edited title/notes/tags, and appeared exactly once for its URL in a new database connection | PASS |
| LD-4: other ordinary account denied | Bob's list/details did not expose the item. Direct edit GET and a browser form POST to exact ID `3` returned 404. Alice then reopened unchanged values, independently matched to SQLite | PASS |
| LD-5: delete only selected item | Confirmed deletion removed `3` from a fresh page and database read. Control `4` and historical baseline `1`/`2` stayed unchanged. Control `4` was removed only after that comparison | PASS |

Application and article process handles all reached terminal states and their ports were closed. Browser-close events were recorded. Final scoped cleanup removed this run's bookmarks `3`/`4`; it did **not** erase the database. Earlier attempts' bookmarks `1`/`2`, unused tags, synthetic accounts/sessions and evidence remain local. The first checkout separately retains its earlier two bookmarks. No raw database or login state is published.

Screenshots include [invalid input](artifacts/replay/assisted-run-20260908T052630285071Z/invalid-url.png), [denied browser POST](artifacts/replay/assisted-run-20260908T052630285071Z/bob-write-denied.png), and [retained baseline after cleanup](artifacts/replay/assisted-run-20260908T052630285071Z/final-empty.png). Some captures occur during CSS transitions; exact assertions and database observations, not screenshots alone, establish the result. The historical filename `final-empty` means this run's items are absent, not an empty database.

## Failure history — retained, not averaged away

| Attempt | What happened | Interpretation |
| --- | --- | --- |
| [CLI bootstrap](bootstrap.json) | A malformed per-invocation permission value was rejected before model execution | Setup error; no application acceptance |
| [Independent Codex invocation](independent.json) | Skill loaded, native regression drafted, article process exited on local socket-bind denial. One diagnostic reproduced the denial; no application or browser started | All 11 requested subchecks UNVERIFIED; the session correctly stopped without escalation or fabricated results |
| [Assisted 051822](artifacts/initial/assisted-run-20260908T051822687310Z/result.json) | Login/save/restart ran, then the generated reporter passed `status` twice when recording an HTTP observation | Harness defect, not a linkding defect. The prematurely assigned `other_account_no_view` PASS lacks its check event and is not treated as qualified evidence |
| [Assisted 052036](artifacts/replay/assisted-run-20260908T052036453688Z/result.json) | An author-added metadata check received a null title and recorded FAIL, but its response filter did not identify the article URL | Raw FAIL preserved; unqualified as a product counterexample because object correlation is missing. The exact selected response was not retained |
| [Assisted 052132](artifacts/replay/assisted-run-20260908T052132725841Z/result.json) | The revised filter could select a redirect before the JSON response; observation raised an error | Incomplete observation. A [focused browser diagnostic](artifacts/replay/metadata-diagnostic.json) confirmed the endpoint's 301 → 200 sequence and correct rendered article title; the exact failed response was not captured |
| [Assisted 052418](artifacts/replay/assisted-run-20260908T052418534182Z/result.json) | Save/restart/isolation/edit passed. The visibility assertion targeted a custom-element wrapper instead of its visible Confirm button | Harness visibility mismatch. The [screenshot](artifacts/replay/assisted-run-20260908T052418534182Z/obstacle.png) shows the button; deletion remained unverified |
| [Assisted 052630](artifacts/replay/assisted-run-20260908T052630285071Z/result.json) | Corrected reporter, exact final-response correlation and visible-button assertion; all five business requirements observed | One complete assisted journey; no upstream defect established |

There were five explicitly reviewed assisted journey attempts, not five passing runs, plus the one focused metadata diagnostic. Each had fresh run IDs and retained evidence; there was no automatic whole-journey retry. After the last partial run left bookmarks, the final test protected that exact baseline instead of deleting history to obtain an empty fixture.

## Assistance, cost and product learning

The author selected/inspected the project, installed 53 locked Python and 159 npm packages, built assets, wrote isolated settings/account preparation and supplied minimum environment instructions. Clone creation to independent dispatch took about 8 minutes 37 seconds, excluding earlier selection. The independent session took 180.502 seconds. Its reported usage was 447,863 input tokens, including 392,576 cached input tokens, and 8,058 output tokens; these are host-reported totals, not the whole study's usage or a cost estimate.

The author then added direct SQLite comparisons, metadata observation, runtime identity and cleanup checks, corrected generated and author-added harness errors, prepared a second checkout and reviewed the final evidence. Assisted execution/correction spanned about nine minutes, excluding later documentation/privacy review. There is no measured external-human labor time, no maintenance trial after an upstream change, and no savings claim.

Two fixes were needed in the model-generated handoff (report field collision and wrapper visibility). The author-added metadata observer also needed URL and redirect correction. The [reporter diagnostic](reporter-diagnostic.json) retains the reproduced collision. These costs are part of the result—not evidence that the Skill automatically produced a reliable regression on its first try.

The existing Skill already requires capability checks, exact object correlation and truthful gaps. This study did not demonstrate that adding more prose would fix host permissions or generated-test correctness, so the package was **not** expanded with a linkding adapter or another generic rule. The next useful gate is a prepared, authorized runtime and a fresh independent executor using the reviewed native handoff. Autonomous completion, external-human reuse and a fair with/without-Skill comparison remain pending.

## Reproduce, audit and limits

Use the [native replay guide](replay/README.md). It separates environment preparation from acceptance and does not require installing the Skill. The final script was executed after author corrections; a new external developer has not yet followed this published guide.

`files.json` lists original and exported digests. Local paths/session identifiers are normalized. One mixed command stdout containing private host Skill instructions is omitted from the public native trace, with its original hash and reason recorded; it is not an unredacted complete trace. Other captured instructions are historical study inputs, not new authority. Raw credentials, password hashes, databases, cookies and browser profiles are excluded. Hashes detect later changes; they do not authenticate collection or prove requirements were complete.

Run `python3 -B evals/results/2026-09-08-linkding/check_record.py` from the repository root to check the captured hashes, retained attempt count and final event/object consistency. This is a study-record check, not a live application test or an authenticity guarantee.

This is one project/version/browser and one bounded journey. It does not establish all linkding behavior, comprehensive security, concurrency, weak-network recovery, mobile compatibility, autonomous cross-project reliability, a controlled baseline, external-user usefulness or production readiness. The default repository CI tests the Skill/helper/package, not this host-dependent application journey.

linkding source excerpts and rendered application captures are attributed to Sascha Ißbrücker and contributors under the [upstream MIT license](LINKDING-LICENSE.txt). This attribution does not select a license for Functional Acceptance itself.
