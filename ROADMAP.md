# Roadmap

Milestones are ordered by evidence, not dates. All runtime work and product evaluations are still pending.

## M0 — Public design baseline

- [x] Document the stack-independent product definition and bounded acceptance workflow.
- [x] Define target preservation, evidence qualification, safe stopping, and native handoff.
- [x] Specify counterexamples and fair with/without-Skill comparisons.
- [ ] Select a license before distributing an installable release.

The repository being public is not evidence that the Skill works.

## M1 — One usable vertical slice

- [ ] Choose one isolated sample with a known healthy state, a known defect, and independent expected results.
- [ ] Write a short Skill entrypoint and only the references required by that sample.
- [ ] Reuse an existing native execution tool; do not create a universal runner or action language.
- [ ] Implement and test the minimum evidence/report helper needed by the slice.
- [ ] Preserve every explicit user target as a check, a visible gap, or a sourced exclusion.

**Exit:** the healthy sample passes with valid evidence; the known defect produces a real counterexample; missing required observations remain unverified. Report the actual tool, target, and scope. Code compiling or tests exiting successfully is insufficient.

## M2 — Trust, interruption, and reusable assets

- [ ] Exercise the relevant false-green cases from the evaluation plan.
- [ ] Verify the actual execution target and any substituted dependencies.
- [ ] Preserve failed attempts and unfinished side-effect responsibility.
- [ ] Keep first-run evidence verifiable through a second run and normal cleanup, within its declared retention period.
- [ ] Produce a native regression entrypoint with explicit setup, cleanup, and manual-observation requirements.

**Exit:** another developer, without the original conversation or this Skill installed, can use the native checks from a clean state. Unknown background work cannot be reported as safely finished.

## M3 — Demonstrate useful reuse

- [ ] Test natural discovery, near-miss requests, and plan-only behavior.
- [ ] Compare against the same agent, tools, inputs, and budget without this Skill.
- [ ] Run on a second authorized project; changing entrypoints in the same demo is not cross-project reuse.
- [ ] Record initial setup, correction, review, and one subsequent change's maintenance effort.

**Exit:** publish the actual sample sizes, outcomes, limitations, and cumulative human effort. Do not infer long-term savings or universal compatibility from a few examples.

## M4 — Limited release

- [ ] Provide a verified install/uninstall path and an explicit tested support matrix.
- [ ] Exercise version pinning and compatibility with older materials.
- [ ] Publish a safe healthy/defective/insufficient-evidence demonstration.
- [ ] Resolve licensing, dependency attribution, and a responsible security-reporting route.
- [ ] Obtain authorization for the release.

**Exit:** release claims match the demonstrated scope. This is not an automatic approval for users to deploy their own products.
