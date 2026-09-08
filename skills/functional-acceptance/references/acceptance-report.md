# Acceptance report

Read at handoff, including retained-history review. Fill from actual observations, in the user's language. Return in the conversation for read-only work; write files only within task authority. Use project-native reporting if it preserves these fields. This template is not the CSV helper's JSON schema.

## Short template

```markdown
Result: [business verdict; most important counterexample or uncertainty]
Requested goal: [original result and constraints]
Basis: [fresh run ID/attempts, runtime/input and environment OR retained record identity]

| Obligation | Verdict | Expected vs observed; evidence reference | Gap / blocker; next safe check and residual uncertainty |
| --- | --- | --- | --- |
| O1 | PASS / FAIL / UNVERIFIED / NOT_APPLICABLE | … | … |

Coverage: [which original obligations were checked, blocked or excluded + source]
Execution: [completed / interrupted / unknown / not run; owned handles if relevant]
Cleanup: [confirmed clean / retained evidence / residual / unknown; ownership and next step]
Replay: [native command + working directory, prerequisites, expected result,
runtime/input assumptions, evidence location, manual checks and cleanup limits;
pack status: draft / author-replayed / independently replayed / not produced]
```

Keep one row per contract obligation, including untouched and excluded ones. A partial check must name what remains unknown. Cite inspectable evidence for the same object/run; attribute retained claims when collection was not independently observed. Separate product failure, observer/test failure and environment gaps. Preserve failed attempts and any observer corrections, even when a later attempt passes.

Before handing over, reconcile the rows with the original request, not only the executed tests. Missing evidence cannot become PASS; missing tools cannot become NOT_APPLICABLE. If a proposed next step closes only one part, state the remainder. Historical review follows [historical evidence](historical-evidence.md); replay instructions describe a future check, not proof about the past.

Report file-writing failures and unknown writers as incomplete delivery/cleanup, even if some business facts are established. Share local evidence locations without exposing secrets or claiming automatic sanitization. A recipient should know what is established, what to do next, and who owns any residual work; a completed acceptance does not approve deployment.
