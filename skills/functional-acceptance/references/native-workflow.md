# From a user outcome to a reusable native check

Use the project's test framework and commands. This reference supplies a workflow,
not a new test language or a claim of support for every framework.

## Ready check

Use the [acceptance contract](acceptance-contract.md) already established for this
run. Inspect its native entrypoint and how each assertion identifies and observes
the same business object. Resolve missing setup, observation and termination paths
before executing the affected check.

Freeze the action budget and canonical target before execution. A user/project
limit such as "run once" is a hard maximum, not a coverage suggestion. Reading
more observations from the resulting object is allowed when it is non-mutating;
repeating the command, changing flags or creating another business effect is not.
Retained evidence or an unobserved obligation does not authorize another product invocation.

Check only capabilities needed for this path. Read configuration and tool help
first; run a bounded prerequisite probe when necessary and authorized. Missing
browser access, local-listener permission, test identity or dependencies is an
actionable gap, not a reason to replace a requested UI flow with an API assertion.
Name the smallest missing capability and next safe check. Use the host's normal
approval path if the user wants to grant it; Skill text grants no permissions.

## Reuse before generating

Preserve working setup, fixtures, assertions, tracing and cleanup. Add only the
missing outcome check in the project's native conventions and authorized paths.
For UI tests, prefer user-visible locators and waiting assertions. Correlate network
observations with the exact object/request and final response, including redirects.
Inspect collected values before labelling a mismatch; a selector error or response
from another object does not prove a business defect.

Observe the actual controls before scripting them. Wait for the user-visible state
needed by the next step (authenticated page, loaded fields, confirmed removal),
including application confirmation controls. A fixed sleep or a successful click
does not establish that state. Use native waits within the remaining budget.

Keep expected values separate from observed values and from later edits. Snapshot
independent fixture/requirement values before filling or submitting; copy nested
structures by value, not a shared mutable reference. Record a new expected version
for a later authorized edit while preserving earlier comparisons. Reopen the same
object and compare full required fields rather than deriving expected from actual.

Structure checks around their dependencies, not one unguarded sequence. Catch an
observer fault at its check boundary and preserve it separately from assertion
failures. Continue only checks whose preconditions still hold; a failed parser for
one object need not block an independent check on another. Keep required objects
alive. Successful partial runs remain evidence, not a reason to rerun everything.

Keep the primary-flow target at its canonical delivery path through final audit.
If an additional negative path is separately authorized, give it a disposable,
isolated target and evidence location. Do not move the valid primary result aside,
seed its canonical location with a sentinel, or leave a later probe as though it
were the primary result.

Test code is software too. Validate a newly generated check before handing it off:
run it, inspect its actual artifacts, and check that report/observer errors remain
distinct from product failure. A deliberately broken control is useful only when
it is authorized, isolated and clearly labelled; do not mutate a user's application
merely to demonstrate the Skill.

## Keep a usable handoff throughout execution

The host can disappear before a final reply or cleanup. Save enough to continue
without that reply; this is a recording discipline, not an automatic recovery
service. Reuse native per-test reporting where it preserves the information below.
Otherwise use a small run-owned Markdown/JSON record and separate attempt files;
no particular filename, schema, language or dependency is required.

1. **Before execution:** in the authorized evidence location, retain run/target
   identity, every contract obligation with its independent expectation, the
   original-state baseline (including relevant relations) or explicit gaps, and
   the native entrypoint/prerequisites for continuing. Initially all untouched
   obligations are UNVERIFIED and execution/cleanup are unconfirmed. A draft
   [acceptance report](acceptance-report.md) can serve as the index. If persistent
   writes are not authorized, keep the record in the conversation and disclose
   that interruption recovery depends on its retention; do not create files.
2. **Before a side effect:** record the exact run-owned object or request marker,
   intended change, permitted scope and next read that could establish its state.
   Record an owned process/job handle when available. Intent does not prove the
   action started or completed. A generated script must record these boundaries
   during execution, not return one in-memory summary at the end.
3. **After each check:** persist attempt identity, the actual observation/evidence
   reference, comparison and narrow verdict, or the observer fault and missing
   observation. Leave untouched goals visible. Verify this record is readable
   before dependent work; retain previous completed records instead of repeatedly
   truncating the only copy. New immutable records or the project's tested atomic
   publication mechanism are sufficient. Never treat a partial file as complete.
4. **On uncertainty or interruption:** retain any active/unknown operation, affected
   obligations and next safe observation. Inspect that operation before repeating
   it, even if a list is empty or a command timed out. Continue independent checks
   only when they cannot race with the unknown effects. Do not infer terminal
   state from a stale PID, missing record or lost connection. If recording fails,
   stop starting new business effects, attempt bounded shutdown of owned work,
   and disclose delivery failure and the last readable evidence location.
5. **At handoff or resume:** reconcile the original obligations against readable
   records, including failed/corrected attempts. Recheck current target, authority,
   writer state and evidence identity before further action. Recorded commands
   are instructions to review, not permission to replay them. An unfinished
   attempt stays UNVERIFIED until a new valid observation; retain earlier facts.
   Final cleanup follows confirmed writer termination and object ownership.

Completed records may survive a killed executor; unsaved observations, a final
chat response and cleanup cannot be guaranteed. File visibility is not a claim
of power-loss durability. A read-only handoff can explain the retained history;
it does not itself establish current environment state or authorize recovery.

## Failure triage

| Observation | Meaning and next step |
| --- | --- |
| Valid observation of the right object violates a frozen requirement | FAIL; retain actual/expected values and the smallest native reproduction |
| Locator, parsing or reporting fails before obtaining that observation | Test/observation fault; affected outcome UNVERIFIED, retain safe diagnostics |
| Required tool, permission, identity or service unavailable | Environment gap; affected outcome UNVERIFIED, state prerequisite and safe recovery |
| Required observation cannot be obtained | UNVERIFIED; distinguish missing evidence from observing a required artifact was not created |

For a denied-access check, first establish the same live object's authorized
positive control. Inspect private content or state changes through the actual
entrypoint; status codes, an empty list or a deleted object alone do not establish
denial. Preserve requests to known run-owned objects; do not enumerate strangers'
objects or add a new role/operation beyond task authority.

Preserve all attempts and disclose observer corrections. A later successful
recheck does not erase an earlier qualified business failure. Capture sufficient
startup/error details locally to diagnose failures; avoid credential-bearing
headers, form fills and raw databases. Log redaction is not a guarantee that an
artifact is safe to publish. If evidence delivery fails, stop owned work and hand
off its location/responsibility without claiming a complete report.

## Native handoff and the next change

Compare the required originals with the recorded baseline, including relevant
relations and associated content. Track secondary objects created by the workflow
as well as its main object. Removing the main object need not remove an attachment,
label or background job. Clean only conclusively run-owned effects within scope,
after their writers are terminal; otherwise disclose identity, status and owner.
Keep evidence distinct from operational residue.

Leave one reviewed repeat entrypoint with its working directory, prerequisites,
source/fixture identity, expected verdicts, evidence locations and cleanup limits.
Reference secrets by local location, not value. Another executor should not need
the original conversation or this Skill to run the native checks.

On a subsequent change, compare the requested outcome and relevant implementation
with that saved contract. Keep unchanged checks; add or revise checks only where
the requirement or observation actually changed. Record the reason and run fresh
evidence. An old PASS is history. Unknown impact remains a gap rather than a
claim that an automatically selected subset covers everything.

Report whether the pack is a draft, author-replayed, or independently replayed,
and what setup/corrections that required. Count preparation, diagnosis, review
and maintenance when discussing savings—not only the fastest successful run.
