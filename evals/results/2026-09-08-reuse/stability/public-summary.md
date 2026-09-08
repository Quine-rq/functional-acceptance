# Independent repeated native regression

The retained native pack completed 12 of 12 full browser journeys with qualified PASS on the same prepared isolated linkding checkout. Three rounds each covered healthy, expired-session, lost-response, and Unicode notes. No journey was automatically retried and the pack was not changed during the experiment.

| Case | Runs | Observed outcome |
| --- | ---: | --- |
| Healthy | 3 | PASS / exit 0 |
| Expired session | 3 | PASS / exit 0; login recovered the same saved object |
| Lost response | 3 | PASS / exit 0; real POST returned 302 before response loss, one persisted object recovered without resubmission |
| Unicode notes | 3 | PASS / exit 0; exact text retained after browser and server restart and edit |
| Deliberate note loss | 1 | FAIL / exit 1; actual saved notes were empty; later obligations remain unverified |
| Withheld restart database observation | 1 | UNVERIFIED / exit 2 despite other successful steps |
| SIGTERM after browser start | 1 | UNVERIFIED / exit 2; owned execution stopped |
| Occupied application port | 1 | UNVERIFIED / exit 2; the probe listener remained alive until its owner closed it |

The 16-run batch ran from 2026-09-08 07:20:15 to 07:25:30 UTC. Full journeys took 20.171–29.529 seconds, mean 23.162 seconds. These are local run times, not human-effort or long-term reliability measurements.

Before that batch, native attempt `run-20260908T071832206438Z` failed during article-service startup because the sandbox denied loopback binding. Its native result is UNVERIFIED / exit 2; it never opened a browser or wrote a bookmark. The outer recorder also encountered `ps` permission denial before saving its independent native termination and stdout capture. Native events, receipt, source snapshots and private diagnostics remain intact. A normal-escalation followup found the recorded article PID absent and both ports free. This startup attempt is preserved separately and is not in the 12-journey stability denominator. The new batch used normal scoped permission escalation; it changed only the recorder output directory and a trailing blank line.

All 17 native attempts are retained. For the completed batch, final audit matched every original artifact hash, the event files against captured stdout, captured source against pack digests, native database observations against independently read synthetic bookmark/tag facts, and native exit codes against independently captured termination. There were 67 browser-start and 67 browser-close events. No recorded owned process remained at the final check, and ports 18741/18742 had no listener.

Data was not emptied. Previous bookmark IDs 3 and 12 and all 15 previous synthetic tags remained unchanged. New failed bookmark ID 47 was retained; successful runs removed only their own target and control. Final bookmark IDs are 3, 12, and 47. Tags increased from 15 to 29 because unused run tags are intentionally retained. The prepared `fa_alice` and `fa_bob` identities and existing credentials were reused; preparation was not rerun. Normal-login sessions are intentionally retained. Auth/session tables and session counts were not read, and no claim is made that those tables were unchanged or empty.

Observed runtime: pinned linkding `65813a75404b1319aca8b09700fadc0b15adabaf`, Python 3.14.4, Chrome 152.0.7977.76, macOS arm64; headless Chrome used fresh sandboxed profiles and loopback-only application routes. The tracked upstream source remained unchanged. Acceptance source repository HEAD was `ac8eda6e35b58583ae521f2989302c73dbb1d0fa`; the actual native script digest, rather than HEAD alone, identifies the executed pack:

- `accept.py`: `84a4b4fa488c4b9fad2e5148770e12e392110a9b2834ff08f443b5c12d8a3d26`
- `support.py`: `493cd346337bf278880c83026bc4f4eba781a5878578f510cbdf3389d837a4f9`
- `server.py`: `63b1b402def9a4fbcc477ff317bc1b41957695033d7498625bf24be9e6186863`

This measures repeated execution of a maintained native example on an already prepared host. It is not a clean-clone onboarding test, independent human handoff, production/mobile test, or evidence of causal Skill benefit. Three observations per healthy/recovery case are too few to establish a general reliability rate. Prior failures remain relevant and were not replaced by this batch.

Publication candidates are listed with original-byte hashes in `public-candidate-index.json`. Prefer each run's events, result, pack/environment digests and source snapshots. Normalize host-specific paths while retaining the original-byte hash mapping. Exclude credentials, databases, auth/session data, private startup/exception logs, private independent snapshots, and screenshots unless separately reviewed.
