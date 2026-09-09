# Acceptance contract

Read when planning acceptance or before a fresh run/recheck. Fill this in the user's language using supplied requirements and inspected project material. Keep it in the conversation unless saving files is authorized; it is a human-readable checklist, not input to the CSV helper. Reuse existing project conventions when they cover these fields.

## Short template

```markdown
Goal: [who needs what result; original request and requirement source]
Mode: [plan / execute / regression recheck]
Target: [project/build, environment, input and test identity; unknowns labelled]

| ID | Required outcome and source | Actor / object / action or entrypoint | Preconditions / independent expectation | Observation / existing assertion | Order and reason / gap |
| --- | --- | --- | --- | --- | --- |
| O1 | … | … | … | … | … |

Scope: [authorized actions, data/paths and downstream effects; exclusions + user source]
Gaps: [obligation ID → missing rule, capability or authority; next safe step]
Budget and stop: [stop time, handoff reserve, scenario/probe limits; how owned work terminates]
Recovery and evidence: [how to inspect an uncertain write; run-owned output location
and what to retain/clean, or “conversation only; no execution”]
```

Account for every explicit result and constraint. One obligation is one independently verifiable claim: if one action can pass while another violates the promise, give them separate rows. Inspect the relevant entrypoints and assertions, not just test names. Mark a check proposed until observed. Expected results come from requirements or independent fixtures, not captured product output; a digest alone supplies no business expectation.

For example, “export every record without replacing existing files” has separate completeness and overwrite-rejection obligations. Comparing the complete output with a frozen fixture checks the first; a disposable pre-existing destination and its before/after contents can check the second. Observing one does not settle the other. Use only the obligations the actual request entails.

For private objects, distinguish discovery/listing, direct reading and changing state where those paths exist within scope. An absent list item or a denied modification cannot settle direct reading. Keep the test object alive, establish that its authorized owner can access it, then observe what the other authorized test identity actually receives. For preservation claims, include relevant content and relationships (such as ownership or attachments), not just object counts. Missing identities or unknown entrypoints remain named gaps; this method does not authorize extra access or a whole-product security audit.

The contract is ready when every requested outcome has checks or gaps, each check has an independent expectation and observation, and the first executable checks target the most consequential unknowns after necessary setup. A shared fixture is a dependency, not a reason to defer an independent check behind unrelated work. Missing execution access need not block a plan; for execution, retain blocked obligations while continuing ready checks within authority.
