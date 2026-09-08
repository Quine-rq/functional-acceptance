# Authorized native sqlite-utils onboarding pair

This is one candidate-versus-old-Skill comparison on a public unfamiliar project. Both native executors generated and ran their own project-native regression packs without coordinator-authored acceptance tests or synthetic fixtures. The complete transcripts, generated tests, commands, databases, exports, and reports are retained. This is scoped project evidence, not a supported release, causal benefit experiment, or external-human trial.

## Frozen inputs and startup

- Candidate repository HEAD: `7d94bb678efedaba57cf4301143041eb39a9c041`; installed package inventory digest `b6aa5770147511b8e6c0417c256635bf2547ccf2c5469d469b6a7209b64ae88b`.
- Old Skill: retained `work/functional-acceptance-ac8eda6`; installed package inventory digest `c260cc22e8615954c416b267b9cec7a23acd1794cb6c3381ca8c69f63a2da4a8`.
- Public sqlite-utils tracked source: `85b1be10c81d9dd3567e36faf8dd411e4a8789bd`; file-inventory digest `2dfff08ad5efb2894006f017b0c2279fdb0d03dc720d49b127e70d8391087d73`.
- Exact shared prompt: SHA-256 `e07383ed10412898bdc7ba9d32cfe290a47cb7bc2c97735b928c88dab820e7a6`, byte-identical to the original failed pair's prompt. Requirement SHA-256 `c5ac9e74c45fdd3972262646171dfe9608c92ae386c0436a6c2cc4e9dd141b8f`.
- Native CLI: 0.153.4. Existing native model/authentication defaults, no model override or credential/configuration changes. The coordinator separately verified default `gpt-6-astra`; raw task events do not independently attest a model build.
- Dependencies had already been provisioned by the coordinator: Python 3.14.4, SQLite 3.50.4, sqlite-utils distribution 4.2.1, pytest 9.1.1. Each actual runtime probe confirms the application loads this invocation's project copy, not the dependency environment's application source.
- Both children started under normal outer approval at `2026-09-08T07:43:41Z`; candidate `thread.started` after 255 ms and old Skill after 318 ms. Their internal `workspace-write` sandbox, `-a never`, disabled web search and eight-minute task budget remained in force; wrapper termination limit was ten minutes.
- `ANTHROPIC_*` environment variables were excluded from the child launch environment by key name. No values were read, recorded, or changed. Native model use employed existing host authentication.

## Actual result and cost

| Configuration | Native duration | Input tokens (cached included) | Cached input | Output tokens | Input + output | Actual native tests |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| candidate | 174.389 s | 299,517 | 263,680 | 7,720 | 307,237 | Two runs, each 5 pytest tests passed (3.12 s and 3.03 s) |
| old Skill | 256.507 s | 499,689 | 452,352 | 11,601 | 511,290 | Two runs, each 1 pytest test with 12 recorded checks passed (2.76 s and 2.81 s) |

Test counts use different decompositions and are not comparative coverage scores. The two native processes ended normally with exit 0; no timeout, manual prompt assistance, or post-start intervention occurred in this clean pair. `reruns: 0` in pair-result means no second model invocation per configuration; each model independently ran its own test pack twice.

Both traces show reads of the actually installed Skill and native-workflow reference, followed by inspection of project documentation/source/tests. Both generated synthetic contacts before executing their application commands. Both retain true subprocess CLI imports, later-process readback, raw JSON exports, visible duplicate-id refusal, all contacts unchanged after refusal, and unchanged unrelated data at the observed stage boundaries. `retained-evidence-audit.json` independently reopens the saved material and lists exact checks.

The candidate reviewed its own first passing run and corrected the test observer to explicitly close SQLite connections, then reran without changing business assertions. Its report explicitly corrects the first writer-state claim and keeps both runs. The old-Skill executor augmented actual SQLite-engine/UID recording and documentation before its second run. Their historical test/runner hashes therefore differ from their final pack where documented; upstream source hashes remain unchanged. Original authored code and modifications remain visible in raw events.

## Integrity, assets, and independent handoff

Every supplied source/test/configuration/requirement/Skill file remained byte-identical, all new project files are within `acceptance/` or `artifacts/`, and the original source stayed unchanged. See `metadata.json`, `inputs.json`, `pair-result.json`, and the retained audit. This content check does not assert all filesystem metadata or external environment was audited.

Candidate handoff: `with_skill/project/acceptance/README.md`, `run.py`, `test_onboarding.py`, `REPORT.md`; two run directories under its artifacts folder. Old-Skill handoff: `old_skill/project/acceptance/README.md`, `run.py`, `test_onboarding.py`, `pytest.ini`; `old_skill/project/artifacts/REPORT.md` and two run directories.

After both model invocations ended, a separate new native Codex task received a fresh source/pack copy with no project `.agents` or `.claude` directory. It was given the generated README and original requirement, not the original conversation, source answers, or correction guidance. It read the pack and ran the original entrypoint without edits, passed all five tests, reopened actual database/exports, and confirmed normal command termination. No Skill was read in its trace. Its 112 provided project files remained unchanged; no repair or retry was needed. See `../reuse-sqlite-independent-native/replay/`, particularly `project/artifacts/INDEPENDENT-REPLAY.md` and `metadata.json` (105.146 s; input 194,507 including cached 167,936; output 4,597; total 199,104).

The synthetic maintenance contract is frozen in `MAINTENANCE-REQUIREMENTS.md`; its independent run and final result are recorded separately under `../reuse-sqlite-independent-native/maintenance/`. Neither independent task is a human usability trial.

The separate maintenance native task ended normally at `2026-09-08T07:54:29.092Z`, after 239.367 s (input 630,122 including cached 580,224; output 10,168; input + output 640,290). It first ran the unchanged pack in its own copy (five passed in 3.12 s), then made one scoped patch and ran the maintained pack in a different fresh directory (five passed in 3.46 s). Only `acceptance/README.md` and `acceptance/test_onboarding.py` changed: 15 lines added / 5 removed across both files, 23 original assertions retained and two added. The upstream application, original run entrypoint, old report and both requirement files remained unchanged. Actual stored postal codes remained text (`00123`, `00000`, `75001`), and preferred names preserved null, empty string and Unicode text. An extra audit rejected five corrupted in-memory contact observations; those are comparator controls, not five application failures.

Maintenance's internal cost record starts at its first recorded discovery timestamp and ends at final validation (216.048 s). The wrapper's 239.367 s includes the complete native invocation and is the comparison figure; neither is a measurement of human labor. Its two native entrypoints totaled 7.739 s, with zero unexpected failures, zero corrective iterations and one acceptance edit patch. The coordinator's post-run read-only audit independently confirmed the unchanged protected files, new evidence scope, exact field values, required source identity and normal termination. See `../reuse-sqlite-independent-native/retained-handoff-audit.json` and the maintenance report. The coordinator also opened the final database through system sqlite3 in read-only mode; field storage types matched and integrity_check returned `ok`.

## Preparation, retained failures, and limits

The original pair in `../reuse-sqlite-onboarding-pair/` remains unchanged: it failed during native-host state/IPC initialization before model execution. Its missing token usage is unavailable, not zero.

The first authorized startup continuation in `../reuse-sqlite-onboarding-authorized-pair/` also remains intact. Both hosts started and inspected public local files, but the executor terminated them at 33.947 s / 33.957 s after noticing unnecessary inherited `ANTHROPIC_*` variables. Its separate notes disclose that operator intervention; no credential value read/transfer was observed and no acceptance files were generated. That pair is not counted as a completed comparison trial. All subsequent native launches filter these variable names.

This executor prepared/copy-checked wrappers and inputs, reviewed instructions and generated code, performed names-only environment diagnosis and normal-approval process termination, authored the approved maintenance requirement and a read-only retained-evidence audit, and wrote these notes. The executor did not write a substitute acceptance script or correct either native pack. Those preparation/review activities and the coordinator's earlier dependency setup are not included in native duration; they were not individually timed. Wrapper preparation timing covers only wrapper preparation.

One successful paired trial and one no-Skill replay support this prepared sqlite-utils CLI workflow only. They do not establish natural discovery, broad cold setup, old-Skill independent handoff, external-human reuse, defect/missing-evidence controls on this project, or long-term cost savings. The eight-minute prompt covers a prepared dependency environment, not a from-zero installation.

Normal command/connection termination is evidenced. Timeout, interruption and concurrent writers were not exercised here. Review found a candidate handoff limitation: its outer 180-second pytest timeout kills only pytest; an in-flight CLI could survive, and the README's reference to waiting for the CLI's own 20-second timeout is inaccurate because that watchdog lives in pytest. No such timeout occurred in these runs. Do not turn this normal-path handoff into a claim that failure cleanup is fully verified. The old pack uses a process-group kill for its overall timeout, but that branch likewise was not executed here.

All databases, exports, caches and raw evidence remain intentionally retained in run-owned locations. No repository edits, staging, commits, push, global migration, credential change or cleanup deletion occurred in this executor task.
