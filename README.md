# Functional Acceptance

**Verify real user outcomes, not just successful tool calls.**

A stack-independent acceptance skill being designed for existing coding agents. It will use a project's own tools to check user journeys, distinguish evidence from assumptions, and leave reusable native regression checks.

> **Status: design baseline.** There is no installable Skill, runtime, release, or validated production capability yet. Design revision `v0.2` is a document version, not a software release. All product evaluations remain unexecuted.

[中文设计说明](DESIGN.md) · [Architecture](ARCHITECTURE.md) · [Evaluation plan](VALIDATION.md) · [Roadmap](ROADMAP.md)

## The problem

An upload can return success while its file cannot be retrieved. An export can exit with code `0` while omitting the last page. A UI can show saved state that disappears in a new process.

The intended workflow starts with the user's promised result, identifies what existing tests do not prove, and obtains the missing observations using authorized project tools.

## Intended workflow

1. Preserve the original request and its acceptance criteria before selecting tools.
2. Choose a bounded plan using the execution and observation capabilities actually available.
3. Run the relevant native checks and retain evidence tied to the correct target, identity, and attempt.
4. Report **PASS**, **FAIL**, **UNVERIFIED**, or **NOT_APPLICABLE** within an explicit scope.
5. Account for unfinished work and side effects, then hand over reusable native checks.

A completed acceptance run may find a real failure. Successful execution, complete coverage, business correctness, and safe cleanup are different facts.

## Scope

- The method is intended for Web, API, CLI, desktop, and mobile workflows; support will be claimed only for combinations actually tested.
- Existing agents and project tools do the execution. This is not a new agent runtime, test language, device cloud, or deployment platform.
- Mocked dependencies can prove the behavior actually tested, not the real storage or delivery they replace.
- Missing tools or evidence stay visible. A narrower test must not silently replace the original request.
- Test environments are the default. Installation or verification does not authorize production writes, code changes, pushes, or public comments.

## Start here

| Document | Purpose |
| --- | --- |
| [DESIGN.md](DESIGN.md) | Product definition, user experience, scope, and completion conditions |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Capability selection, evidence rules, budgets, recovery, and handoff |
| [VALIDATION.md](VALIDATION.md) | Planned counterexamples, strong baselines, natural invocation, and real-user evaluation |
| [CONTEXT.md](CONTEXT.md) | Shared domain terms |
| [DECISIONS.md](DECISIONS.md) | Design choices, source references, and unresolved questions |
| [ROADMAP.md](ROADMAP.md) | Small milestones with observable exit conditions |
| [AGENTS.md](AGENTS.md) | Working rules for coding agents contributing to this repository |

The detailed design is currently in Chinese. The evaluation plan contains 38 retained cases and nine additional scenario groups; these are specifications, not passed tests.

## Next milestone

Build a minimal workflow around one isolated, reproducible user journey. A paginated export is a candidate: the healthy version returns every expected record, a defective version reports success but drops data, and a missing-observation case remains unverified. The concrete sample and execution tool are not selected yet.

Do not install this repository as a working Skill yet. A documented installation path will be added after an actual package and supported execution combination have been verified.

## Feedback and licensing

Concrete user journeys, missing observations, and reproducible failure cases are useful feedback. Use synthetic data; do not post credentials, private logs, or customer information in public issues.

License selection is pending. No open-source license has been applied to this repository yet.
