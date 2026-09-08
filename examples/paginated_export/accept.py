#!/usr/bin/env python3
"""Collect a real, bounded local export attempt; not a generic command runner."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COLUMNS = ["id", "title", "notes"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_new(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def reference(path, data):
    return {"path": path, "sha256": sha(data)}


def stop_owned(process):
    """Only the concrete child we created; never a process-name or stale-PID kill."""
    if process.poll() is None:
        process.terminate()
    try:
        return process.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.communicate(timeout=3)


def collect(case, directory):
    # These are reviewed, bundled inputs, not executable material supplied by a report.
    program = (HERE / "export.py").read_bytes()
    source = (HERE / "fixtures" / "pages.json").read_bytes()
    expected = json.loads((HERE / "fixtures" / "expected_records.json").read_text(encoding="utf-8"))
    run_id = "export-" + uuid.uuid4().hex
    # Resolve the parent, not the new leaf: resolving a dangling leaf symlink
    # would accidentally create its target instead of refusing the existing path.
    parent = directory.parent.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    root = parent / directory.name
    root.mkdir(exist_ok=False)
    (root / "attempt-1").mkdir()
    write_new(root / "runtime.py", program)
    write_new(root / "input.json", source)
    obligation_id = "complete-readable-export"
    contract = {
        "schema_version": "m1",
        "journey": "Export all supplied pages to a new CSV and read back exactly the expected records and fields.",
        "target": {"id": "offline-paginated-export", "sha256": sha(program)},
        "input_sha256": sha(source),
        "goals": [
            {"id": "all-pages", "text": "Every record from every page appears once in the supplied order.",
             "source": "examples/paginated_export/requirements.md requirement 2",
             "obligations": [obligation_id], "gap": None, "exclusion": None},
            {"id": "field-integrity", "text": "An independent CSV reader obtains the exact UTF-8 field values.",
             "source": "examples/paginated_export/requirements.md requirement 3",
             "obligations": [obligation_id], "gap": None, "exclusion": None}
        ],
        "obligations": [{"id": obligation_id, "expected": "Exact header and all five independently specified rows.",
                         "required": True, "applicable": True, "exclusion": None, "mapping": "csv-exact/v1",
                         "columns": COLUMNS, "rows": [[row[column] for column in COLUMNS] for row in expected]}],
        "scope": {"environment": "isolated-local", "upstream": "synthetic-pages",
                  "claim": "Normal offline CLI/file export only; synthetic upstream pages, no real API or UI. Other input/error cases run separately in native unittest."}
    }
    frozen = json_bytes(contract)
    write_new(root / "contract.json", frozen)
    manifest = {
        "schema_version": "m1", "id": run_id, "contract_sha256": sha(frozen),
        "runtime": reference("runtime.py", program), "input": reference("input.json", source),
        "tool": {"name": "paginated-export-collector/0.1.0-dev + Python", "version": platform.python_version()},
        "attempts": [], "execution_state": "unknown",
        "cleanup": {"state": "unknown", "details": "Prepared; native process may not yet have started. Reconcile this run before reuse."},
        "retention": {"policy": "until-owner-removes", "details": "Unique local run directory; no background deletion or reuse. Recheck digests before sharing."}
    }
    # Preserve a pre-action record even if the collector is interrupted before finalization.
    write_new(root / "run.pending.json", json_bytes(manifest))
    command = [sys.executable, "-B", "runtime.py", "--source", "input.json", "--output", "attempt-1/output.csv"]
    if case == "defect":
        command.extend(["--fault", "omit-final-page"])
    process = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    interrupted = False
    try:
        write_new(root / "attempt-1" / "process-handle.json", json_bytes({"pid": process.pid, "run_id": run_id,
                  "note": "Historical handle only. A later PID match alone never authorizes terminating a process."}))
        try:
            stdout, stderr = process.communicate(timeout=10)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            interrupted = True
            stdout, stderr = stop_owned(process)
    except BaseException:
        # Includes disk/write errors immediately after Popen. The pending record
        # remains incomplete, but this collector still owns child cleanup.
        stop_owned(process)
        raise
    output = root / "attempt-1" / "output.csv"
    output_ref = reference("attempt-1/output.csv", output.read_bytes()) if output.is_file() else None
    record = {"schema_version": "local-process/v1", "run_id": run_id, "attempt_id": "attempt-1",
              "target_sha256": sha(program), "input_sha256": sha(source), "argv": command,
              "completed": process.returncode is not None, "exit_code": process.returncode, "output": output_ref,
              "stdout": stdout.decode("utf-8", errors="replace"), "stderr": stderr.decode("utf-8", errors="replace")}
    raw_record = json_bytes(record)
    write_new(root / "attempt-1" / "execution.json", raw_record)
    observations = [] if case == "missing-observation" or output_ref is None else [{"obligation_id": obligation_id, "artifact": output_ref}]
    manifest["attempts"] = [{"id": "attempt-1", "execution": reference("attempt-1/execution.json", raw_record), "observations": observations}]
    manifest["execution_state"] = "interrupted" if interrupted else "completed"
    manifest["cleanup"] = {"state": "retained", "details": "The owned native child has terminated. Only this run's local inputs, output, and evidence are intentionally retained; no external writes or background workers."}
    write_new(root / "run.json", json_bytes(manifest))
    # Separate, fresh helper processes reopen the actual file. Never pass in a desired verdict.
    results = []
    for format_name in ("json", "markdown"):
        report_name = "report.json" if format_name == "json" else "report.md"
        result = subprocess.run([sys.executable, "-B", str(REPO / "scripts" / "acceptance.py"),
                                 "--contract", "contract.json", "--run", "run.json", "--root", ".",
                                 "--format", format_name, "--output", report_name], cwd=root,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        results.append(result)
    if any(result.returncode not in (0, 1, 2) for result in results) or not (root / "report.json").is_file() or not (root / "report.md").is_file():
        raise RuntimeError("report unavailable; retained run is incomplete")
    if results[0].returncode != results[1].returncode:
        raise RuntimeError("report checks disagreed; evidence may have changed between reads; retained reports are historical, not a qualified handoff")
    report = json.loads((root / "report.json").read_text(encoding="utf-8"))
    print(json.dumps({"case": case, "run_directory": str(root), "business_verdict": report["business_verdict"],
                      "completion": report["completion"], "qualified_pass": report["qualified_pass"]}, ensure_ascii=False))
    return results[0].returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("healthy", "defect", "missing-observation"), default="healthy")
    parser.add_argument("--run-dir", type=Path, help="New, dedicated directory; existing paths are refused")
    args = parser.parse_args(argv)
    directory = args.run_dir or REPO / ".acceptance" / "runs" / (args.case + "-" + uuid.uuid4().hex)
    try:
        return collect(args.case, directory)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "incomplete", "error": str(error) if isinstance(error, RuntimeError) else type(error).__name__,
                          "next": "Inspect the run directory and pending/native records; do not overwrite or blindly retry it."}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
