# Product hardening — implementation contract

> Historical plan note: the licensing and support items below were written for
> the 2026-09-08 baseline. The repository now uses the [MIT License](LICENSE)
> and publishes [security](SECURITY.md) and [support](SUPPORT.md) boundaries;
> private reporting has since been enabled and verified.

Started 2026-09-08 from `5ec62872eaef6509058b88dded031664beb940d1`.
This is the implementation plan, not evidence of completion.

## User result and invariants

An independent developer with an authorized test environment should be able to
ask their existing coding agent to verify a feature, understand any obstacle,
and reuse the resulting native checks after a change without the author's help.

Current evidence: a robust local CSV helper; limited Codex behavior probes; one
real linkding journey completed after author corrections. Target: a repeatable,
bounded development preview. No universal adapter, agent runtime or production
approval is being introduced. Existing CSV semantics and historical studies
remain unchanged. Product code, user data and publishing authority remain separate.

The complete chain is discovery → prerequisites → contract → native execution
→ independent observations → qualified verdict → stopped writers / retained
responsibility → independent replay → subsequent change.

## Work and exit checks

1. Improve the shipped workflow where the study exposed gaps: inspect coverage
   rather than count green tests; reuse native test frameworks; distinguish
   product counterexamples, harness faults and missing environment capability;
   leave an explicit handoff and revalidate it after changes.
2. Provide a maintained, study-specific linkding native pack outside the Skill.
   Refuse wrong revisions, unsafe/existing destinations and occupied ports;
   support an explicit browser path; keep safe startup diagnostics, run identity,
   failures and cleanup separate. Historical executed scripts remain untouched.
3. Exercise real browser/Django/SQLite controls: healthy journey, an explicitly
   seeded note-loss mutation, missing required observation, and relevant session/
   interrupted-response recovery. Freeze user expectations before execution.
   A seeded mutation is not a newly discovered upstream bug.
4. Independently replay the native pack from a fresh isolated environment without
   the Skill or original conversation. Repeat and preserve all attempts. Then
   change one requirement and measure the affected regression work.
5. Run actual second-host behavior if authenticated tools are available. Run
   paired Skill/baseline probes on ordinary requirements with incomplete existing
   tests, missing evidence and plan-only requests. Freeze inputs, retain tool
   traces and real artifacts; do not infer improvement from longer reports.
6. Run native/package checks, inspect privacy and failure paths, produce a review
   view and update truthful support/remaining-gate documentation. Commit only
   reviewed exact paths; no push or release under this request.

## Measurement and decision boundaries

Report implementation tests, model behavior, live application journeys and human
reuse separately. Execution helpers must not count their own errors as business
defects. A completed native command is not automatically a qualified acceptance.

Existing authenticated hosts may be used with task-local permission settings;
no model switch, global configuration change, credential installation or paid
subscription purchase. Test artifacts use synthetic data and remain local until
privacy review. Read-only probes create no project artifacts. Experiments are
bounded and retain failures rather than automatically retrying to obtain green.

External human recruitment, license selection, release authorization and proof of
net human savings cannot be supplied by pretending an agent is an outside user.
Unavailable conditions remain explicit release gates; unaffected work continues.

## Primary references checked

- [Agent Skills format](https://agentskills.io/specification): portable instructions
  and optional resources, not a supplied execution environment.
- [Playwright practices](https://playwright.dev/docs/best-practices): user-visible
  locators, waiting assertions, isolation and inspectable failure traces.
- [Agent evaluation](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
  repeat trials and judge environment outcomes, including the evaluation harness.
- [Claude programmatic use](https://code.claude.com/docs/en/headless) and
  [Codex non-interactive use](https://learn.chatgpt.com/zh-Hans/docs/non-interactive-mode):
  use native structured output with explicit least-privilege choices.

Patterns are referenced, not copied implementations. Findings and actual results
will be recorded separately after execution.
