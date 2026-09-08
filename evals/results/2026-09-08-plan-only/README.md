# First plan-only comparison

Date: 2026-09-08. This is a **development-set plan-content probe**, not a complete host-behavior evaluation or evidence of product readiness. The practical benefit of the Skill remains unproven.

## What actually ran

Six fresh agent contexts received the same ordinary request, project requirements, implementation, native tests and three fixtures. Three were instructed to load the Skill; three used the same host without it. All inherited the parent model without an override and received the same five-minute task budget. Exact model/effort identifiers, usage and measured duration were not exposed.

The task was to propose acceptance checks while Python and filesystem prerequisites were unconfirmed, not to run the exporter or fix product code. Its inputs come from source commit `c26a86f`; the Skill SHA-256 and seven input hashes are in [results.json](results.json). Each agent was instructed to read only its allowed inputs and write its own plan. Dispatch order alternated across paired waves because concurrency was limited. No earlier output or grading feedback was supplied to later executors.

One independent agent graded all six plans against eight expectations frozen before outputs were reviewed. The primary agent checked the plans, the one disputed result and the score arithmetic. All outputs were retained; the Skill and scoring rules were not tuned during this probe.

Complete host tool-call traces were unavailable. Configuration names describe the assigned prompts, not independently proven Skill loading or tool isolation. Self-reported “did not execute” statements and unchanged input files do not establish zero unauthorized execution. No such safety score is reported; unavailable time/token values are not converted to zero or estimated from character counts.

## Results and the important caveat

| Assigned configuration | Run 1 | Run 2 | Run 3 |
| --- | --- | --- | --- |
| With Skill | [8/8](with_skill-1.md) | [8/8](with_skill-2.md) | [8/8](with_skill-3.md) |
| Without Skill | [8/8](without_skill-1.md) | [8/8](without_skill-2.md) | [7/8](without_skill-3.md) |

These are content-expectation counts per plan, **not feature pass rates**. Both groups preserved the main requirements, independent CSV expectations, native checks and execution prerequisites.

The single difference is wording in the third baseline plan: it groups a missing artifact with known defects as FAIL. Frozen expectation 3 instead requested UNVERIFIED for a missing CSV. However, that expectation did not distinguish **actually observing that the program failed to create its required file** from **not obtaining the necessary observation/evidence**. The former can support a business failure; the latter cannot. The grader retained the literal score and recorded this weakness in every evaluation. This difference does not establish that the Skill produces better acceptance decisions.

The third baseline plan also left the retention of independently re-readable CSV evidence less concrete than the other plans. This was noted qualitatively, not added as a new scoring rule. With-Skill plans were longer; reader usefulness and review effort have not been measured.

Published plans preserve their wording and line structure. Only the task-local absolute input-directory prefix has been replaced with `examples/paginated_export`. They are historical generated outputs: their execution claims are unverified, and their commands still require the stated future prerequisites. [results.json](results.json) retains all graded expectations, evidence and evaluation feedback.

## What this does not prove

- Natural discovery, near-miss routing or actual plan-only execution restraint: no complete tool trace was available, and the with-Skill path was explicit.
- Goal extraction from incomplete tests: this sample already publicly specifies the complete user requirements and native checks.
- A new CLI/product execution, second-project reuse, external human handoff, saved time or long-term usefulness.
- A general improvement from a one-case, three-repetition-per-group content score, particularly when the only difference depends on an ambiguous expectation.

## Next experiment

Before another iteration, define two separate cases for confirmed non-generation and unavailable evidence. Freeze their observable truth and correct decision boundaries before dispatch; do not reinterpret this run's scores. Obtain independently reviewable tool traces before scoring execution restraint. A separate ordinary-change case with incomplete existing tests can then test goal extraction without exposing a finished acceptance checklist.

Human review of these six plans remains pending. No Skill revision or release is justified solely by this small comparison.
