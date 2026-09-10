#!/usr/bin/env python3
"""Run one reviewed command and retain an immutable evaluation ledger."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time


SCHEMA = "functional-acceptance-eval-invocation/v1"
ATTEMPT_ID = "attempt-1"
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
DEFAULT_TIMEOUT = 360.0
DEFAULT_CAPTURE_LIMIT = 1024 * 1024
MAX_CAPTURE_LIMIT = 16 * 1024 * 1024
TERMINATION_GRACE = 2.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def encode_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def stream_reader(stream, limit: int, result: dict) -> None:
    retained = bytearray()
    total = 0
    digest = hashlib.sha256()
    try:
        while True:
            chunk = stream.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            digest.update(chunk)
            if len(retained) < limit:
                retained.extend(chunk[: limit - len(retained)])
    except OSError as error:
        result["error"] = {"type": type(error).__name__, "message": "stream capture failed"}
    finally:
        stream.close()
        result.update(data=bytes(retained), total_bytes=total, sha256=digest.hexdigest())


def process_group_exists(group_id: int) -> bool:
    if os.name != "posix":
        return False
    try:
        os.killpg(group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def stop_owned_group(process: subprocess.Popen) -> list[str]:
    actions = []
    if os.name == "posix":
        group_id = process.pid
        if process_group_exists(group_id):
            try:
                os.killpg(group_id, signal.SIGTERM)
                actions.append("SIGTERM_PROCESS_GROUP")
            except ProcessLookupError:
                pass
            deadline = time.monotonic() + TERMINATION_GRACE
            while time.monotonic() < deadline:
                process.poll()  # Reap a terminated group leader before probing its group.
                if not process_group_exists(group_id):
                    break
                time.sleep(0.02)
            if process_group_exists(group_id):
                try:
                    os.killpg(group_id, signal.SIGKILL)
                    actions.append("SIGKILL_PROCESS_GROUP")
                except ProcessLookupError:
                    pass
    elif process.poll() is None:
        process.terminate()
        actions.append("TERMINATE_PROCESS")
        try:
            process.wait(timeout=TERMINATION_GRACE)
        except subprocess.TimeoutExpired:
            process.kill()
            actions.append("KILL_PROCESS")
    try:
        process.wait(timeout=TERMINATION_GRACE)
    except subprocess.TimeoutExpired:
        if process.poll() is None:
            process.kill()
            actions.append("KILL_PROCESS")
            process.wait(timeout=TERMINATION_GRACE)
    return actions


def capture_reference(path: str, result: dict) -> dict:
    data = result.get("data", b"")
    total = result.get("total_bytes", len(data))
    return {
        "path": path,
        "sha256": result.get("sha256", sha256(data)),
        "total_bytes": total,
        "retained_bytes": len(data),
        "truncated": total > len(data),
    }


def validate(args: argparse.Namespace) -> tuple[Path, Path, list[str]]:
    run_root = args.run_root
    if not run_root.exists() or not run_root.is_dir() or run_root.is_symlink():
        raise ValueError("run root must be an existing non-symlink directory")
    if not ID_PATTERN.fullmatch(args.run_id):
        raise ValueError("run id must contain only letters, digits, dot, underscore or hyphen")
    cwd = args.cwd.resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError("working directory must be a directory")
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("a command is required after --")
    if not 0.01 <= args.timeout_seconds <= 3600:
        raise ValueError("timeout must be between 0.01 and 3600 seconds")
    if not 1 <= args.max_capture_bytes <= MAX_CAPTURE_LIMIT:
        raise ValueError(f"capture limit must be between 1 and {MAX_CAPTURE_LIMIT} bytes")
    return run_root.resolve(), cwd, command


def runner_return_code(
    product_code: int | None,
    timed_out: bool,
    observer_error: dict | None,
    descendants_found: bool,
) -> int:
    if timed_out:
        return 124
    if observer_error is not None or product_code is None or descendants_found:
        return 125
    if product_code < 0:
        return min(255, 128 + abs(product_code))
    return min(255, product_code)


def execute(args: argparse.Namespace) -> int:
    run_root, cwd, command = validate(args)
    runner_bytes = Path(__file__).read_bytes()
    claim = {
        "schema_version": SCHEMA,
        "run_id": args.run_id,
        "attempt_id": ATTEMPT_ID,
        "runner_sha256": sha256(runner_bytes),
        "claimed_at": utc_now(),
        "rule": "This run root permits one harness-level product invocation.",
    }
    try:
        write_new(run_root / ".invocation-claim.json", encode_json(claim))
    except FileExistsError as error:
        raise RuntimeError("run root is already claimed; inspect it instead of retrying") from error

    attempt = run_root / ATTEMPT_ID
    attempt.mkdir(exist_ok=False)
    sync_directory(run_root)
    started_at = utc_now()
    started_ns = time.monotonic_ns()
    intent = {
        "schema_version": SCHEMA,
        "run_id": args.run_id,
        "attempt_id": ATTEMPT_ID,
        "cwd": str(cwd),
        "argv": command,
        "runner_sha256": claim["runner_sha256"],
        "started_at": started_at,
        "timeout_seconds": args.timeout_seconds,
        "max_capture_bytes_per_stream": args.max_capture_bytes,
        "state": "prepared",
    }
    write_new(attempt / "intent.json", encode_json(intent))

    process = None
    stdout_result: dict = {}
    stderr_result: dict = {}
    readers: list[threading.Thread] = []
    timed_out = False
    interrupted = False
    observer_error = None
    termination_actions: list[str] = []
    descendants_found = False

    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=os.name == "posix",
        )
        write_new(
            attempt / "process-handle.json",
            encode_json(
                {
                    "schema_version": SCHEMA,
                    "run_id": args.run_id,
                    "attempt_id": ATTEMPT_ID,
                    "pid": process.pid,
                    "recorded_at": utc_now(),
                    "note": "Historical owned handle; PID reuse never authorizes a later signal.",
                }
            ),
        )
        readers = [
            threading.Thread(
                target=stream_reader,
                args=(process.stdout, args.max_capture_bytes, stdout_result),
                daemon=True,
            ),
            threading.Thread(
                target=stream_reader,
                args=(process.stderr, args.max_capture_bytes, stderr_result),
                daemon=True,
            ),
        ]
        for reader in readers:
            reader.start()
        try:
            process.wait(timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            termination_actions.extend(stop_owned_group(process))
        except KeyboardInterrupt:
            interrupted = True
            termination_actions.extend(stop_owned_group(process))

        if not timed_out and not interrupted and process_group_exists(process.pid):
            descendants_found = True
            termination_actions.extend(stop_owned_group(process))
    except (OSError, subprocess.SubprocessError) as error:
        observer_error = {"type": type(error).__name__, "message": "product process did not start"}
        if process is not None:
            termination_actions.extend(stop_owned_group(process))

    for reader in readers:
        reader.join(timeout=TERMINATION_GRACE)
    capture_complete = all(not reader.is_alive() for reader in readers) and not any(
        result.get("error") for result in (stdout_result, stderr_result)
    )
    if not capture_complete and process is not None:
        for stream in (process.stdout, process.stderr):
            try:
                stream.close()
            except OSError:
                pass
        for reader in readers:
            reader.join(timeout=TERMINATION_GRACE)
        capture_complete = all(not reader.is_alive() for reader in readers) and not any(
            result.get("error") for result in (stdout_result, stderr_result)
        )
    if not capture_complete and observer_error is None:
        observer_error = {"type": "CaptureIncomplete", "message": "stdout or stderr capture did not complete"}

    write_new(attempt / "stdout.bin", stdout_result.get("data", b""))
    write_new(attempt / "stderr.bin", stderr_result.get("data", b""))
    ended_at = utc_now()
    product_code = process.returncode if process is not None else None
    code = 130 if interrupted else runner_return_code(
        product_code, timed_out, observer_error, descendants_found
    )
    if interrupted:
        closure_status = "interrupted"
    elif timed_out:
        closure_status = "timed_out"
    elif observer_error is not None:
        closure_status = "observer_error"
    elif descendants_found:
        closure_status = "descendant_cleanup_required"
    else:
        closure_status = "complete"
    execution = {
        "schema_version": SCHEMA,
        "run_id": args.run_id,
        "attempt_id": ATTEMPT_ID,
        "cwd": str(cwd),
        "argv": command,
        "runner_sha256": claim["runner_sha256"],
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": round((time.monotonic_ns() - started_ns) / 1_000_000, 3),
        "pid": process.pid if process is not None else None,
        "process_started": process is not None,
        "process_terminated": process is not None and process.poll() is not None and not process_group_exists(process.pid),
        "exit_code": product_code,
        "timed_out": timed_out,
        "interrupted": interrupted,
        "descendants_found_after_parent": descendants_found,
        "termination_actions": termination_actions,
        "capture_complete": capture_complete,
        "stdout": capture_reference("stdout.bin", stdout_result),
        "stderr": capture_reference("stderr.bin", stderr_result),
        "observer_error": observer_error,
        "invocation_count_for_run_root": 1 if process is not None else 0,
        "closure_status": closure_status,
        "runner_exit_code": code,
    }
    write_new(attempt / "execution.json", encode_json(execution))
    print(
        json.dumps(
            {
                "run_id": args.run_id,
                "attempt_id": ATTEMPT_ID,
                "runner_exit_code": code,
                "product_exit_code": product_code,
                "timed_out": timed_out,
                "record": str(attempt / "execution.json"),
            },
            ensure_ascii=False,
        )
    )
    return code


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True, help="Existing coordinator-owned directory")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-capture-bytes", type=int, default=DEFAULT_CAPTURE_LIMIT)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return execute(parse_args(argv))
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 125


if __name__ == "__main__":
    sys.exit(main())
