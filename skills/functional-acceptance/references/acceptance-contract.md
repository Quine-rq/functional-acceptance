# Acceptance contract

Read when planning acceptance or before a fresh run/recheck. Fill this in the user's language using supplied requirements and inspected project material. Keep it in the conversation unless saving files is authorized; it is a human-readable checklist, not input to the CSV helper. Reuse existing project conventions when they cover these fields.

## Short template

```markdown
Goal: [who needs what result; original request and requirement source]
Mode: [plan / execute / regression recheck]
Target: [project/build, environment, input and test identity; unknowns labelled]

| ID | Required outcome and source | Scenario / precondition | Independent expected result | Existing assertion / observation + remaining check |
| --- | --- | --- | --- | --- |
| O1 | … | … | … | … |

Scope: [authorized actions, data/paths and downstream effects; exclusions + user source]
Gaps: [obligation ID → missing rule, capability or authority; next safe step]
Budget and stop: [time/scenarios/probes; how owned work terminates]
Recovery and evidence: [how to inspect an uncertain write; run-owned output location
and what to retain/clean, or “conversation only; no execution”]
```

Account for every explicit result and constraint; split independently verifiable obligations into separate rows. Mark a check proposed when no observation exists. A named test is not coverage until its assertion observes this outcome. Expected results need a source independent of what the implementation happened to produce; a digest alone supplies no business expectation.

For example, “export every record without replacing existing files” has separate completeness and overwrite-rejection obligations. Comparing the complete output with a frozen fixture checks the first; a disposable pre-existing destination and its before/after contents can check the second. Observing one does not settle the other. Use only the obligations the actual request entails.

The contract is ready when each requested outcome is mapped and each planned action has either the required scope/observation or an explicit gap. Missing execution access need not block a plan. For execution, continue safe independent checks within authority; preserve blocked obligations for the report.
