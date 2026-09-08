# Design decisions and references

The original design baseline is revision v0.2. Decisions below constrain implementation; they are not evidence of competitive performance. Current implementation scope is tracked in [M1-PLAN.md](M1-PLAN.md) and [README.md](README.md).

## Keep the project a Skill

The host agent handles reasoning and tool calls. Existing project tools handle execution. A small local helper checks material consistency and renders results; it does not control every action or independently prove that supplied facts are true.

We considered a lightweight method package, a deterministic execution kernel, and a change-driven wrapper around existing tests. The current design combines the lightweight package with existing test reuse and minimum material constraints. A separate runtime, distributed action ledger, device cloud, and custom testing language are out of scope.

## Choose capabilities, not framework names

Start from the required user entrypoint and observations. Use an actual browser, request client, native command, or device when it can meet those requirements within authorization. Flutter/Android is a possible sample, not the product's admission criterion.

Skill format compatibility does not imply equivalent host tools, permissions, or verified execution support.

## Preserve targets and qualify claims

Keep original requested outcomes separate from the subset that can currently be executed. Every explicit outcome must have a check, a gap, or a sourced exclusion. Mock, stub, and replay boundaries limit what the resulting evidence proves.

Evidence is tied to the actual target, object, identity, attempt, and retention conditions. A hash can reveal changed material; it cannot prove truthful collection or recover an overwritten file.

## Version expectations separately from observations

**Status: implemented for the M1 local format.** Freeze the exact contract bytes for a run; changed requirements produce a new contract, while fixes and reruns produce new observations. Retaining both adds some bookkeeping but prevents historical failures from disappearing when expectations, artifacts, or attempts change.

This is not a general event-sourcing system. The experimental `m1` format is documented in [references/material-format.md](skills/functional-acceptance/references/material-format.md); unknown versions are rejected, and no migration or compatibility promise has been established.

## Keep ownership with the project

Regression assets use the project's native tools and document their prerequisites. Another developer should be able to use them without the original conversation or this Skill installed. Manual observations remain explicit; they do not silently become unattended checks.

## Source references

The following primary references informed the design. They are not a tested compatibility list or a claim that the project has run these tools.

- [Agent Skills specification](https://agentskills.io/specification): packaging and portable instruction format.
- [Agent Skills creation practices](https://agentskills.io/skill-creation/best-practices): focused instructions and behavior-based evaluation.
- [Playwright test agents](https://playwright.dev/docs/test-agents): existing planning, generation, and repair workflows.
- [Playwright API testing](https://playwright.dev/docs/api-testing): combining user-facing actions with resource observations.
- [Playwright retries](https://playwright.dev/docs/test-retries): preserving the distinction between first-run and retried outcomes.
- [Maestro Flutter support](https://docs.maestro.dev/get-started/supported-platform/flutter): a possible mobile execution combination with platform-specific prerequisites.
- [FinalRun test-and-fix Skill](https://github.com/droid-ash/finalrun-agent/blob/main/skills/finalrun-test-and-fix/SKILL.md): an existing workflow reference; this project's default scope keeps acceptance separate from repair.
- [Python unittest](https://docs.python.org/3/library/unittest.html) and [CSV](https://docs.python.org/3/library/csv.html): standard-library native regression checks and explicit CSV parsing in M1.
- [Official checkout](https://github.com/actions/checkout) and [setup-python](https://github.com/actions/setup-python): CI uses fixed v7 commit identities, read-only contents permission, and no persisted checkout credentials. CI setup does not publish reports, install the Skill, or deploy a target.

## Still unresolved

The first sample is offline paginated JSON exported through a native Python process to CSV. The upstream pages are synthetic. The material helper supports only `csv-exact/v1` with a bounded native process record; it is not a general executor or arbitrary-log adapter. Python standard-library `unittest`, subprocesses, and CSV parsing keep the native checks usable without the Skill.

The experimental install path now reuses a pinned Skills CLI with one self-contained directory; rationale, safety limits and actual checks are in [Agent integration](INTEGRATIONS.md). Node dependencies remain development-only. The old repository CLI forwards to the packaged helper so existing sample usage is preserved.

License, supported multi-host behavior, cross-project usefulness, and external user benefits remain unresolved. Next are the scoped trust checks and comparisons in [VALIDATION.md](VALIDATION.md), not an unqualified support list.
