# Evaluation invocation ledger

Status: implemented development harness. It is not shipped inside the Skill.

## User problem

A reviewer cannot independently distinguish “the product command ran once” from an Agent-authored statement that it ran once. Terminal files prove final state, but they do not prove the invoked argv, working directory, exit code, timeout or whether a later probe replaced the first result.

## Boundary

The harness owns one coordinator-created run directory and one direct subprocess invocation. It receives reviewed argv as CLI arguments and never evaluates a shell string. An exclusive run claim is published before spawning, so a second or concurrent harness call for the same run is refused before product execution. Ledger files are created once with exclusive-create semantics; the runner never overwrites them. This is write-once behavior by the runner, not tamper-proof storage against a user who can edit the directory.

The ledger records:

- run and attempt identity;
- resolved working directory and exact argv;
- runner digest, UTC start/end and monotonic duration;
- child PID, termination path, timeout and exit code;
- bounded stdout/stderr prefixes with total byte counts, truncation flags and full-stream hashes.

The prepared intent remains alongside the terminal execution record. A crash after the exclusive claim is conservative: the run stays claimed and must be inspected rather than automatically retried.

## Non-goals

- It does not authorize a command, prove the caller used no other execution path, or authenticate Agent identity.
- It does not capture environment variables, credentials or arbitrary filesystem activity.
- One direct subprocess may create descendants; invocation count refers to harness-level product starts, not every process in the tree.
- It is evaluation instrumentation, not a universal workflow runner or a replacement for product-specific observations.

## Acceptance

1. A completed command has one write-once intent, process handle, bounded streams and terminal record.
2. A second or concurrent call for the same run cannot start the product.
3. Invalid setup fails before claiming the run.
4. Timeout terminates the owned process group and prevents a delayed descendant write in the controlled fixture.
5. Command-not-found leaves a terminal observer-failure record without claiming that a process started.
6. Captured output is bounded while total byte counts and truncation remain visible.
7. A zero-exit parent with a surviving owned descendant is cleaned up and reported as incomplete closure, not clean success.

## Usage

Create a fresh coordinator-owned directory for each evaluation cell, then pass the reviewed command as an argv vector after `--`:

```bash
mkdir -p /tmp/acceptance-run-001
python3 evals/harness/run_once.py \
  --run-root /tmp/acceptance-run-001 \
  --run-id run-001 \
  --cwd /path/to/fixture \
  --timeout-seconds 360 \
  -- command arg1 arg2
```

The run root contains `.invocation-claim.json` and `attempt-1/`. The attempt directory contains prepared `intent.json`, an optional `process-handle.json`, retained `stdout.bin` and `stderr.bin` prefixes, and terminal `execution.json`.

Exit codes preserve a normal product exit when execution closes cleanly. The harness uses `124` for timeout, `125` for refusal, observer failure or required descendant cleanup, and `130` for interruption. A product may independently return the same numeric code; `execution.json` records both codes and a `closure_status` to disambiguate them. A parent exit of zero is not clean success while an owned descendant remains alive.

## Verified fixture

The harness ran the pinned Cookiecutter safe-update fixture once, recorded product exit `0`, then refused a second invocation for the same run root before product start. The independent business assertions still reported the expected protected-config failure, demonstrating that a successful process exit is not treated as functional acceptance.
