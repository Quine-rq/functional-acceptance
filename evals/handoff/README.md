# Incremental handoff development controls

These are synthetic mechanism probes, not real delivery or production-benefit
benchmarks. They complement the real-project trials; they cannot replace them.

`cases.json` fixes one request, three conditions and seven evidence expectations.
Copy `fixture.py` as `delivery.py` and `PROJECT.md` as `README.md` into a fresh
isolated directory. Supply independent UTF-8 `document.txt`, an `original.json`
record with labels/associated content, empty `artifacts/` and `state/`, and
`fixture.json` with `case` equal to the condition name. No external service,
credentials or dependency installation is involved.

Compare frozen current/previous Skill packages with fresh native contexts,
identical request/tools/budget and one attempt each. Expose only one target package
per context. Keep every incomplete attempt and all raw observations. Control
source is inspectable: this is not hidden-fault discovery or a natural-trigger test.

| Condition | Actual control behavior | What to inspect |
| --- | --- | --- |
| `observer-error` | Preview returns an observer error; independent download remains available | Continue independent checks; do not turn missing preview into a product counterexample |
| `uncertain-write` | A delivery is saved but its response is lost, returning 124 | Same-marker authoritative status; exactly one submission; content actually compared |
| `hard-stop` | Audit becomes active after a recipient download; coordinator kills owned execution | Before-stop facts and untested audit remain understandable without a final reply |

The coordinator must confirm termination of the native tool processes as well as
the host. Killing the CLI alone may leave tool workers alive in another process
group. Use a fresh invocation identity plus command and working-directory checks
before signaling owned groups; never replay historical PIDs. Capture evidence
only after writers are terminal, or declare the interruption experiment invalid.
The initial 2026-09-09 control exposed this exact coordinator defect; both attempts
were retained and corrected runs were recorded separately.

The fixture captures synthetic `artifacts/` text before native commands in
`state/*-boundary.json`. These are coordinator observations, not agent-authored
reports. They let a reviewer determine whether a contract, write intent or actual
download observation was present *before* the next action. Do not give after-the-
fact report edits credit for pre-action recording. Output snapshots are bounded
to regular text files of 128 KiB each; missing/omitted artifacts are evidence gaps.

Copy only the executor's retained artifacts into a new read-only context for a
cold handoff review. Withhold the original conversation, Skill, target source and
coordinator state. Ask for observed facts, remaining goals, unknown effects and
safe continuation. This checks readability, not executed recovery or external-
human onboarding. A known simple control can be passed equally by both versions;
report that outcome rather than manufacture a weaker baseline.

Run the fixture integrity tests with:

```sh
python3 -B -m unittest discover -s tests -p test_handoff_fixture.py -v
```

These tests verify the control itself, not whether an agent follows the Skill.
Frozen packages and local run evidence must remain separate from this definition.
