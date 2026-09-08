# Prepared sqlite-utils onboarding, independent replay and synthetic maintenance

Four completed native Codex tasks provide scoped evidence that the generated regression pack can be handed to a new executor without the Skill. The study used public sqlite-utils 4.2.1 source at `85b1be10c81d9dd3567e36faf8dd411e4a8789bd`, synthetic contacts and a dependency environment prepared before the tasks. No application source was changed.

The onboarding comparison is **one candidate versus one old-Skill invocation**, with the same frozen prompt, project snapshot, tools and budget. Candidate Skill revision was `7d94bb678efedaba57cf4301143041eb39a9c041`; the old package was `ac8eda6`. Neither invocation was given a prewritten acceptance test, fixture or command recipe. Both inspected native project entrypoints, created pytest packs, executed true CLI subprocesses and retained databases, raw outputs and reports.

Both configurations verified the same five requested outcomes: contact import with exact values, later-process readback, complete retained JSON export, visible duplicate-id refusal with existing contacts unchanged, and preservation of unrelated data. Candidate used five pytest tests; the old package used one pytest test containing twelve recorded checks. These counts are different decompositions, not comparative coverage scores. Both models reviewed and reran their own packs, preserving the original attempts.

| Completed native task | Whole invocation | Input tokens, cached included | Cached input | Output tokens | Input + output |
| --- | ---: | ---: | ---: | ---: | ---: |
| Candidate onboarding | 174.389 s | 299,517 | 263,680 | 7,720 | 307,237 |
| Old-Skill onboarding | 256.507 s | 499,689 | 452,352 | 11,601 | 511,290 |
| Independent no-Skill replay | 105.146 s | 194,507 | 167,936 | 4,597 | 199,104 |
| Independent no-Skill maintenance | 239.367 s | 630,122 | 580,224 | 10,168 | 640,290 |

Cached input is included in input tokens and must not be added again. The four completed tasks total 1,657,921 reported input-plus-output tokens. Earlier interrupted attempts have unavailable usage, so this is not total study usage or a monetary cost. Native durations exclude coordinator preparation, earlier dependency setup and later independent review; they are not human labor measurements.

The new replay task received a fresh source-and-pack copy without project Skill directories, the generated README and the original requirement. It ran the original entrypoint without editing any of the 112 provided files and observed five tests pass in 3.36 s. It also reopened the actual database and export, checked the six preservation boundaries and ten command termination records. No correction or retry was needed, and its trace contains no Skill-resource read.

A different new maintenance task received another fresh copy and a requirement frozen before execution. This was an evaluator-defined synthetic data-fidelity extension approved by the coordinator, not external user feedback: add explicit `postal_code` and `preferred_name` values, including a leading-zero string and both null and empty string. The task first reran the unchanged pack, then changed only the native test and README. All 23 previous assertions remained, two strict value/type assertions were added, and the maintained five-test pack passed. Actual SQLite observations preserved `"00123"` as text, null as null, and empty string as text. The application, runner, old report and requirement files were unchanged. One edit patch, no corrective iteration and no unexpected failed run were recorded.

The maintenance executor additionally tested its existing comparison helper against five corrupted in-memory observations. All were rejected. These are observer controls, not application defects, and do not replace a deliberately defective application or missing-evidence study.

All current invocations ended normally, and protected-file hashes and write scope were checked from retained material. Databases and evidence remain intentionally retained. The original host-initialization failure and a later operator-interrupted startup pair remain recorded separately; neither is relabeled as a completed comparison. Subsequent launches removed unnecessary third-party environment variables by name without reading or changing their values, and kept normal native sandbox and approval restrictions.

These results establish this prepared local CLI workflow and its agent-to-agent handoff. They do not establish from-zero dependency setup, natural Skill discovery, an old-Skill independent replay, external-human usability, long-term savings or general superiority from one pair. The no-Skill tasks are handoff tests using a generated pack, not no-Skill onboarding baselines.

A concrete handoff limitation remains: the candidate runner's overall timeout kills pytest without guaranteeing termination of an active CLI child. Its README's suggestion to wait for the CLI's own timeout is inaccurate because that watchdog is in pytest. Normal termination was observed here; timeout/interruption safety was not exercised and is not declared passed. No assertion was weakened or application changed to conceal this limitation.

Local evidence index: onboarding `EXECUTION-NOTES.md`, `pair-result.json`, `retained-evidence-audit.json` and both complete native traces; replay `project/artifacts/INDEPENDENT-REPLAY.md`; maintenance `project/artifacts/INDEPENDENT-MAINTENANCE.md`, `maintenance-session-20260908T075039Z/acceptance.diff`, `cost.json`, `final-validation.json`, `observer-controls.json`; combined handoff `retained-handoff-audit.json`. Public redistribution of raw material uses the project's normal path normalization and evidence curation.
