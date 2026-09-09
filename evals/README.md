# Development checks for Skill behavior

These prompts are development probes, not a hidden benchmark or a supported-platform claim. The current case asks for a plan from the controlled export sample's ordinary requirements, implementation, fixtures, and existing tests. Its expected output is **a usable plan**, not a claim that the exporter passed.

## Plan-only output-quality probe

Use `evals.json` for the same user request and output expectations in both configurations. Freeze the project inputs and Skill revision before dispatch. Give each run a fresh context, the same project material, available tools, and five-minute task budget. Explicitly load `SKILL.md` only in the with-Skill configuration. The baseline uses the same host without that Skill; do not weaken its request or remove project requirements/tests.

Run each configuration three times, alternating dispatch order and keeping every result. Limited concurrency may require paired waves; do not feed an earlier result into a later run. Save the original plan, exact prompt, input hashes, Skill identity, and run metadata. Have a separate evaluator judge the same output expectations against the source requirements. Missing evidence does not earn a pass.

The current expectations grade plan content: goal coverage, independent expected results, existing native checks, safe future execution prerequisites, and honest scope. They do **not** prove that the executor obeyed a no-execution instruction. That requires independently accessible complete tool-call traces; an agent's statement or an unchanged working tree is insufficient. Mark unavailable trace or usage data as unavailable, never as zero calls/tokens or verified safety.

The existing complete native suite and public expected results make this a relatively well-specified development case. It does not exercise the N01 variant where existing tests omit the final page. Explicit loading does not test natural discovery; this is not a new product execution, second-project reuse, human handoff, or proof of saved effort. Do not combine plan-content scores with the native test count or a general Skill success rate.

Generate a local comparison view from all retained plans and grades before changing the Skill. If both configurations perform equally, report that the case did not demonstrate added value. Do not manufacture a weaker baseline or tighten expectations after seeing outputs to create a win. Keep failed and inconclusive results visible; use different development cases before drawing a wider conclusion.

The [first six-plan comparison](results/2026-09-08-plan-only/README.md) is recorded with every plan and grade. It exposed an ambiguity in expectation 3 and did not establish practical added value. Keep that historical case unchanged; separate confirmed business failure from unavailable evidence in the next case.

## Native host smoke checks

[host-smoke.json](host-smoke.json) freezes five small requests for real host invocation: execution, plan-only, regression, a near-miss explanation and unavailable historical evidence. The [first native-host record](results/2026-09-08-host-smoke/README.md) includes complete normalized tool traces, retained failures and a targeted read-only correction. It is a once-per-case development smoke check, not the repeated baseline experiment described above.

## Risk-first intent guards

[risk-first-guards.json](risk-first-guards.json) contains three inline requests: a local export plan, an insufficient historical record, and an archive-delivery plan. They check that prioritizing independent failure paths does not introduce unrelated permission testing, block planning on missing credentials, or replace missing historical evidence with a new run.

Freeze the requests, expectations and both Skill packages before invocation. Use a fresh native context per request and package, the same model and tools, and a two-minute limit. Expose the target Skill through ordinary host discovery without adding its name to the request; keep non-selection and incomplete attempts in the results. Keep complete tool traces and inspect them for execution, writes and network activity: unchanged files alone do not establish read-only behavior. The coordinator may retain the response outside the executor's project; distinguish that from writes initiated by the executor.

Compare the candidate with the previous Skill once per request as a bounded regression guard. Grade the six expectations separately for each request, retaining the original text and evidence for each verdict. These content and intent checks do not measure successful export or delivery, cross-project execution, production benefit, or reliable natural selection rates. They complement—but cannot replace—repeated execution on a real application.

The [2026-09-09 known-case regression](results/2026-09-09-risk-first/README.md) records the 18-run application comparison and the separate six intent guards. The candidate reduced observed omissions, but a missed delivery deadline and slower observed means remain; this is not a supported-release or production-uplift claim.

## Incremental handoff controls

[Handoff controls](handoff/README.md) exercise observer isolation, an uncertain
write and interrupted execution with a synthetic native CLI. Command-boundary
snapshots distinguish records written before an action from final-report edits.
Keep host termination separate from worker termination; the first local hard-stop
attempts exposed a coordinator defect and do not qualify as complete interruption
evidence. These controls and read-only cold handoff reviews do not establish
unfamiliar-project benefit, successful recovery execution or human onboarding.

The [local development record](results/2026-09-09-incremental-handoff/README.md)
retains the invalid initial interruptions and corrected runs. Both versions
handled these controls; no added-value percentage was established.
