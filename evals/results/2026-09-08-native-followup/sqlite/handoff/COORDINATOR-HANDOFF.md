# Handoff to final evidence review

All four completed native invocations are closed. The interrupted conversation did not require or cause any rerun. The maintenance process was confirmed from session 85895 and metadata: exit 0, no signal, no forced termination, 07:50:29.725Z–07:54:29.092Z.

## Actual gates

- Prepared unfamiliar-project onboarding: both candidate and old Skill independently generated usable tests and actual evidence from the frozen source/prompt; each retained two native test runs. This is one pair, and pre-provisioned dependencies remain part of the assistance disclosure.
- Candidate no-Skill replay: five tests passed unchanged, no repair/retry, every provided file unchanged, actual database/export reopened, ten commands normally terminated.
- Candidate no-Skill maintenance: separately frozen synthetic field requirement; original and maintained packs both passed five tests. Exactly README and test file changed (15 additions / 5 removals total), 23 old assertions retained, two added, no upstream or requirement change, no unexpected failures or corrective iteration.
- Final data: leading-zero postal codes remain SQLite text; preferred_name preserves null versus empty text; unrelated row unchanged; system sqlite3 read-only integrity_check returned ok in a coordinator post-run inspection.
- No Skill directory was copied to either handoff project, and neither trace contains a Skill-resource read. All newly created project files are under artifacts. Original source is still clean at the frozen HEAD.
- Timeout/interruption reliability remains unverified and has the concrete code issue below. External-human usability, general superiority, cold dependency setup and long-term savings remain open. Do not mark all M3 or release gates complete.

## Concrete finding retained, not repaired

Candidate `project/acceptance/run.py:29–36` starts pytest without a dedicated process group and, on 180-second timeout, calls `process.kill()` only on pytest. The CLI subprocess is spawned inside pytest at `test_onboarding.py:48`; its 20-second watchdog at lines 51–54 disappears when pytest is killed. Moreover its PID record is written only after it terminates (lines 56–57). An active writer could survive without a saved command PID. README line 46's suggestion to wait for the CLI's own 20-second timeout is therefore incorrect. No timeout was triggered in this study; all observed runs terminated normally. The maintenance task left this runner unchanged as required by its field-only contract. No assertion was weakened or generated pack corrected by the coordinator.

## Evidence entrypoints

- `../reuse-sqlite-onboarding-authorized-clean-pair/EXECUTION-NOTES.md`: full frozen-input, setup, interruption, native-result and caveat record.
- `../reuse-sqlite-onboarding-authorized-clean-pair/retained-evidence-audit.json`: post-run consistency checks of all four onboarding test runs.
- `retained-handoff-audit.json`: recomputed protection, scope, Skill-read absence and complete read/export/refusal/preservation checks for replay and both maintenance runs.
- `replay/project/artifacts/INDEPENDENT-REPLAY.md`: new executor's report; native `events.jsonl`, `metadata.json`, `timing.json`, prompt and final answer are directly under replay.
- `maintenance/project/artifacts/INDEPENDENT-MAINTENANCE.md`: new maintenance executor's report; native trace, metadata, timing, prompt and final answer are directly under maintenance.
- `maintenance/project/artifacts/maintenance-session-20260908T075039Z/`: original generated files, before/after hash inventories, acceptance.diff, actual baseline and maintenance wrapper records, verify.py and its recorded execution, verification.json, observer-controls.json, final-validation.json, cost.json and evidence-sha256.json.
- `maintenance/project/artifacts/onboarding-20260908T075108Z-5575dd08/`: maintenance executor's unchanged-pack baseline (5 passed, 3.12 s).
- `maintenance/project/artifacts/onboarding-20260908T075149Z-61dfd4e6/`: changed-field actual run (5 passed, 3.46 s), complete JSON/database/raw command artifacts.
- `PUBLIC-SUMMARY.md`: machine-path-free narrative prepared for the root's final curation. Raw reports still contain machine paths and should go through the existing evidence normalization workflow before a public repository commit.

## Cost to carry forward

Candidate onboarding: 174.389 s, 307,237 input+output tokens. Old onboarding: 256.507 s, 511,290. No-Skill replay: 105.146 s, 199,104. No-Skill maintenance: 239.367 s, 640,290. Cached input is already included. Total for these four completed native invocations: 1,657,921 input+output tokens; this excludes unavailable usage from interrupted/failed starts and is not a total study billing figure.

Maintenance's internal cost.json reports 216.048 s from its first discovery timestamp to final validation; use the 239.367 s native-wrapper measurement for total invocation cost. Baseline and maintenance entrypoints totaled 7.739 s; the remaining measured time includes model reading, patching, verification and reporting, not measured human labor. Coordinator setup, source/environment provisioning, reviews and this final curation are additional untimed effort.

No application/repository edits, staging, commit, push or cleanup deletion were performed by this task. All generated evidence and both earlier failed/interrupted pair directories remain retained. Root owns final grading, publication normalization and any authorized repository changes/push.
