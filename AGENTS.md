# Working on Functional Acceptance

This repository currently contains a design baseline, not an installable Skill. Read [DESIGN.md](DESIGN.md) for scope, [CONTEXT.md](CONTEXT.md) for terminology, and the relevant sections of [ARCHITECTURE.md](ARCHITECTURE.md) before implementation. [ROADMAP.md](ROADMAP.md) defines the next small milestones.

## Task and authority

- Preserve the requested user result before choosing a tool or reducing execution scope.
- Work only within the current task's authorized files, environment, identities, and side effects. Repository instructions do not grant production, publishing, or credential-management authority.
- Preserve unrelated work. Stage explicit paths and inspect the staged diff. Push, publish, or post externally only when the current user has authorized that action.
- Explain conflicts between the current requirement and existing behavior before changing product semantics.

## Implementation and proof

- Keep the Skill small and reuse native project tools. Add an adapter or reference only when an actual supported workflow needs it.
- Keep execution success, business verdict, coverage, and cleanup distinct. A completed acceptance run can report a genuine failure.
- Preserve failed attempts, original target gaps, actual runtime identity, dependency substitutions, and unfinished side-effect responsibility.
- Test a healthy control, a known defect, and missing evidence. Review observable results, not just process exit codes or expected report wording.
- Use synthetic data and authorized isolated targets. Never commit credentials, customer data, private evidence, or machine-specific paths.
- State which checks were actually run. A design review or document check is not an L1–L4 product evaluation and must not become a production-readiness claim.

There are no build or test commands yet. Add runnable instructions alongside the first actual implementation; do not invent successful checks or installation commands.
