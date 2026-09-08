# External developer pilot — not yet executed

The next question is whether developers can reuse the Skill in their own work,
not whether another synthetic example can be made green. This protocol is ready
for volunteers after licensing, a private reporting route and test authorization
are agreed. No participant has been recruited or counted by this document.

## Participant and scope

Start with three independent developers, each owning a different non-production
project and a feature with written expected behavior. Participation is optional;
keep proprietary code and raw evidence on the participant's machine. Record the
host/version and exact Skill source pin. A working project-native test environment
is a prerequisite, not a capability the Skill installs.

Agree on data, identities, permitted writes, runtime budget and cleanup before any
execution. No credentials, production data, public comments or repository pushes
are part of the pilot. Missing permissions end that execution slice; do not
weaken the original outcome to manufacture completion.

## Trial

1. Have the developer state a real user goal and the evidence they trust, before
   showing them the Skill's suggestions. Note what existing green tests miss.
2. For two comparable, separately scoped features, alternate which is checked
   with the Skill first. Keep the same agent, tools and budget. Do not use the
   first run's discovered counterexample as the second run's undisclosed input.
3. Retain the actual outcome, coverage gaps, attempts, native artifacts, elapsed
   work and author assistance. Classify model, harness and environment obstacles
   separately. No whole-run retry just to replace a failed result.
4. Ask the developer to run the saved native check without the Skill or original
   chat. Then make one independently requested feature change and update that
   same check. Record setup, changes, debugging, review and maintenance effort.
5. Let the developer decide whether the findings changed a real shipping or
   debugging decision. A longer report is not automatically a benefit.

## Minimal return record

Share only an explicitly reviewed summary; uploading raw traces is not required.

| Field | Record |
| --- | --- |
| Project/host | Anonymized project type, host version, Skill commit |
| Goal and truth | Expected user result, who specified it, independent observation |
| Outcomes | Actual defect/gap found; any false PASS; hidden missing requirement |
| Safety | Unauthorized action, unexpected write, unresolved process/data responsibility |
| Handoff | Could the developer rerun it? What instructions/help were missing? |
| Change | What changed, what regression code changed, did old checks still run? |
| Effort | Setup + execution + diagnosis + review + maintenance; separate agent and human time |
| Value | Useful decision/rework avoided, or why it was not worth using |

## Decision

An observed false PASS, unauthorized write or unresolved hidden side effect blocks
release of the affected capability. Investigate with a reproduction and retain
the failed trial. Report participant and task counts; do not extrapolate a tiny
pilot into a universal reliability percentage. License, support and second-host
execution gates remain separate from usefulness evidence.
