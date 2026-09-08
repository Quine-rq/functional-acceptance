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
