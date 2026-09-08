# External-project study: linkding

Frozen before the first application journey. This is a bounded reuse study, not a benchmark or a release gate. Results will be recorded separately; this plan is not evidence of a pass.

## Business contract

1. **User problem:** a bookmark user needs to save a private item, find it after returning, update it, and remove it without affecting another user's data.
2. **Target and current truth:** the task requests a complete real-project journey. [linkding](https://github.com/sissbruecker/linkding) provides this bookmark workflow. Its source at `65813a75404b1319aca8b09700fadc0b15adabaf` uses Django forms, session authentication and SQLite persistence. These mechanisms were inspected; no browser acceptance has run yet.
3. **Invariants:** leave upstream tracked source unchanged; use ordinary synthetic accounts and an isolated database; exercise actual login, forms, metadata HTTP loading and persistence. Never substitute mocks or forced login for these observations. No upstream writes, production access or external archiving. Credentials and raw database/session material stay private.
4. **Chain:** browser login → invalid input with visible feedback → correct and save a loopback article with tags/notes → new browser session and server restart → retrieve and edit the same object → verify another ordinary account cannot access/change it → owner removes it → fresh observation confirms absence. Preserve an unrelated bookmark as a deletion-scope control.
5. **Success:** each required result below has attributable observations from this run. A missing stage remains unverified; a test or tool exit code alone is not acceptance.

## Required observations

| ID | User-observable result | Independent check |
| --- | --- | --- |
| LD-1 | Invalid URL is rejected visibly; correcting it allows a normal save | No invalid bookmark persisted; real saved URL, title, tags and notes agree with input |
| LD-2 | Saved item is retrievable after a fresh authenticated browser session and an actual server-process restart | Same bookmark ID and persisted values, with stopped/started server handles recorded |
| LD-3 | Editing updates that item; a fresh view shows changed values | Same ID, updated database fields and no duplicate |
| LD-4 | Another ordinary account cannot view or edit the private item | Denial for the exact existing object; owner can still retrieve it unchanged |
| LD-5 | Confirmed deletion removes only the selected item | Fresh UI and database read show absence; unrelated control remains |

This is one journey with related validation, persistence and ownership checks, not five independently sampled experiments. Report actual browser/runtime versions, input/source identities, attempts, failure history, execution termination and retained resources. Screenshots support selected states; assertions and database observations carry the exact comparisons.

## Method and limits

- Install the unchanged Skill from Functional Acceptance commit `4e4836b` into a fresh upstream clone, then invoke a fresh native Codex session with the user's outcome and minimum environment instructions. Do not supply a finished acceptance script or evaluator grades. This plan stays outside its workspace.
- Use the project's locked Python/JavaScript dependencies and native Playwright library, with an existing headless Chrome and a fresh browser context. Preparation is performed by the study author and counted as setup, not credited to the Skill.
- Use a loopback HTTP article as synthetic metadata input; the browser, Django application and SQLite database are real. Disable background tasks, archiving, favicons and previews through local test configuration. No external URL is needed for the journey.
- Give the task a 12-minute execution budget and at most two distinct diagnostic probes per obstacle; outer supervision is separately bounded. Retain failed attempts rather than silently restarting the study.
- The CSV helper is not a browser/database evidence interpreter and must not grade this study. Review native assertions, actual artifacts and traces instead.
- A generated regression script is only a handoff candidate until it has been independently replayed from the documented clean state without the Skill.
- Do not claim full linkding correctness, comprehensive authorization/security coverage, mobile support, production readiness, model superiority or time savings. No paired no-Skill baseline, independent human user or repeated sample is included.

## Preparation sources

- [Upstream development instructions](https://github.com/sissbruecker/linkding/tree/65813a75404b1319aca8b09700fadc0b15adabaf#development)
- [Configuration options](https://linkding.link/options/), checked against this checkout's settings and task scheduling code
- [Native upstream browser tests](https://github.com/sissbruecker/linkding/tree/65813a75404b1319aca8b09700fadc0b15adabaf/bookmarks/tests_e2e), which use forced login and mock some website metadata; those shortcuts are not used as proof of the full journey

Any later scope adjustment must be recorded in the results without rewriting these original requirements.
