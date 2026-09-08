# Roadmap

Milestones are ordered by evidence, not dates. M1 now has a controlled local implementation; the broader product and release gates remain pending.

## M0 — Public design baseline

- [x] Document the stack-independent product definition and bounded acceptance workflow.
- [x] Define target preservation, evidence qualification, safe stopping, and native handoff.
- [x] Specify counterexamples and fair with/without-Skill comparisons.
- [ ] Select a license before distributing an installable release.

The repository being public is not evidence that the Skill works.

## M1 — One usable vertical slice

- [x] Choose one isolated sample with a known healthy state, a known defect, and independent expected results.
- [x] Write a short Skill entrypoint and only the references required by that sample.
- [x] Reuse an existing native execution tool; do not create a universal runner or action language.
- [x] Implement and test the minimum evidence/report helper needed by the slice.
- [x] Preserve every submitted explicit user target as a check, a visible gap, or a sourced exclusion; user-goal extraction still requires host evaluation.

**Exit:** the healthy sample passes with valid evidence; the known defect produces a real counterexample; missing required observations remain unverified. The implemented boundary is local synthetic pages → real Python CLI → local CSV. Code compiling or tests exiting successfully is insufficient; this is not external-project or production evidence.

## M2 — Trust, interruption, and reusable assets

- [ ] Exercise the relevant false-green cases from the evaluation plan.
- [x] Bind the local sample's actual executable/input snapshots and disclose its synthetic upstream; other target types remain pending.
- [x] Preserve registered failed attempts and incomplete local process responsibility; remote writes and resume behavior remain pending.
- [x] Keep first-run local evidence verifiable through a second run; owner removal invalidates qualification, with no background cleanup.
- [x] Produce and independently agent-replay a native regression entrypoint with explicit setup and cleanup, without the Skill/helper.
- [x] Publish complete local report files without replacement; exercise write interruption, disk failure, concurrent delivery, and explicit handoff of report-cleanup failures. See [M2 results](M2-RESULTS.md).

**Exit:** another developer, without the original conversation or this Skill installed, can use the native checks from a clean state. Unknown background work cannot be reported as safely finished.

The clean-directory replay so far used an independent agent, not an external human developer. M2 is partially covered; the full false-green matrix and external handoff are not declared complete.

## M3 — Demonstrate useful reuse

- [ ] Test natural discovery, near-miss requests, and plan-only behavior.
- [ ] Compare against the same agent, tools, inputs, and budget without this Skill.
- [x] Run on a second authorized project; changing entrypoints in the same demo is not cross-project reuse.
- [ ] Record initial setup, correction, review, and one subsequent change's maintenance effort.

**Exit:** publish the actual sample sizes, outcomes, limitations, and cumulative human effort. Do not infer long-term savings or universal compatibility from a few examples.

A [first paired plan-content probe](evals/results/2026-09-08-plan-only/README.md) retained three outputs per configuration and independent grades. Tool traces and usage were unavailable, and its only scoring difference depends on an ambiguous expectation. This does not complete the behavior/baseline gates above or establish practical benefit.

A [native Codex smoke check](evals/results/2026-09-08-host-smoke/README.md) now retains complete normalized traces and actual CSV evidence. Four initial requests met their expectations; a fifth created files during a read-only review. A narrow instruction correction passed one targeted recheck. This is not the required repeated experiment or a claim that all cases passed on the corrected revision.

The [linkding study](evals/results/2026-09-08-linkding/README.md) satisfies only scoped second-project execution: a real browser/Django/SQLite bookmark journey passed after author assistance and native-regression corrections. The independent Skill invocation stopped at a local permission gap. All failed attempts and setup/correction work are retained; autonomous reuse, external-human handoff, a fair baseline and maintenance effort remain unproven. M3's overall exit is not met.

Follow-up: [product hardening](PRODUCT-HARDENING-RESULTS.md) adds a maintained
native pack, independent agent replay, a Unicode fixture maintenance exercise,
real recovery controls and ten current-host paired behavior runs. Both paired
configurations have incomplete-coverage trials; installation did not always
produce invocation. These are scoped advances, not completion of the full
natural-trigger matrix, causal benefit experiment or external-human M3 exit.

## M4 — Limited release

- [ ] Provide a verified install/uninstall path and an explicit tested support matrix.
- [ ] Exercise version pinning and compatibility with older materials.
- [ ] Publish a safe healthy/defective/insufficient-evidence demonstration.
- [ ] Resolve licensing, dependency attribution, and a responsible security-reporting route.
- [ ] Obtain authorization for the release.

**Exit:** release claims match the demonstrated scope. This is not an automatic approval for users to deploy their own products.

Development progress: [portable package and integration checks](INTEGRATIONS.md) cover five installer targets and one Codex discovery probe. Actual multi-host invocation, interruption-safe upgrade evaluation, and supported-release qualification remain pending; the gate above is not yet marked complete.

Further [reuse and recovery work](REUSE-RESULTS.md) adds staged-copy interruption,
backup/rollback checks, exact execute-permission change detection, old m1 material
compatibility and twelve repeated browser recovery journeys. These cover only
the documented local boundaries. The new host matrix is incomplete after approval
rejection, and sqlite-utils stopped during host initialization; cold onboarding,
its maintenance handoff, second-host execution and external-human gates remain open.
