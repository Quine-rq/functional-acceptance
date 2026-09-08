# Native follow-up record — 2026-09-08

This supplements, rather than replaces, earlier blocked and failed evaluations.
Read [the product results](../../../NATIVE-FOLLOWUP-RESULTS.md) for outcomes and
remaining gates. No result here is a release or production-readiness approval.

## Evidence groups

- `codex/`: frozen scenarios, separately versioned old/new comparisons, independently graded public outputs and retained synthetic CSV observations. Intermediate revisions and failures remain separate; `old_skill` is not a without-Skill baseline.
- `claude/`: all ten authorized calls, narrow independent grades, actual observable loading, normalized public tool/results and a client-estimated cost ledger. No healthy-history control or full execution journey is claimed.
- `sqlite/`: unfamiliar-project generation, fresh no-Skill replay and maintenance, original failed attempts, and the subsequent lifecycle RED/GREEN hardening. Supplied dependencies and coordinator-written synthetic requirements are disclosed.
- `checks/`: integrated local regression outputs and the startup-timing counterexample. These are distinct from native model grading.

## Authorization and privacy

The user authorized this round's native evaluation and commit/push to the existing
origin/main, later permitting up to USD 5 in Claude calls. The first Claude probe
had a USD 0.10 client threshold; follow-ups used USD 0.25 each. These are client
controls, not verified billing caps. No provider/global settings, release, account
permissions or production state were changed.

Claude's supplied key was passed through no-echo ephemeral stdin into child
environment variables for the official Anthropic endpoint, not stored in a key
file or included in prompts/argv. Processes ended and local references were
cleared; this does not revoke a credential disclosed in chat. Early Codex calls
inherited unrelated provider environment variables; no read/transmission was
observed. Subsequent children stripped them by name. An early sqlite pair was
operator-stopped and retained, not relabeled a model failure or secret leak.

Public transcripts omit model reasoning/thinking blocks, signatures and private
authentication diagnostics. Machine-specific paths are normalized; per-group
provenance records identify original and published hashes and transformations.
Retained output files preserve meaningful bytes such as CSV newlines. This is a
reviewed extract, not a claim that full raw traces are published.

## Recheck locally

```sh
python3 -B evals/results/2026-09-08-native-followup/check_record.py
```

The checker validates the bounded inventory, file digests and summary invariants.
It does not call a host, access credentials, run sqlite-utils, verify a billing
statement, authenticate historical collection or prove that a model will repeat
the same behavior. A modified or missing evidence file must fail this check.
