#!/usr/bin/env python3
"""Offline consistency checks and one explicit CSV mapping; never a runner."""

import argparse
import csv
import hashlib
import html
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys

VERSION = "0.1.0-dev"
MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_REFERENCES = 128


class InvalidMaterial(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidMaterial(message)


def fields(value, names, label):
    require(isinstance(value, dict), f"{label}: expected an object")
    require(set(value) == set(names.split()), f"{label}: missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 8000, f"{label}: expected bounded nonempty text")


def digest(value, label):
    require(isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value),
            f"{label}: expected lowercase SHA-256")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sequence(value, label, maximum=128):
    require(isinstance(value, list) and len(value) <= maximum, f"{label}: expected a bounded list")


def unique(items, label):
    require(len(items) == len(set(items)), f"{label}: duplicate identity")


def exclusion(value, label):
    fields(value, "reason source", label)
    text(value["reason"], label)
    text(value["source"], label)


def artifact(value, label):
    fields(value, "path sha256", label)
    text(value["path"], label)
    digest(value["sha256"], label)


def parse_json(data):
    def pairs(entries):
        result = {}
        for key, value in entries:
            require(key not in result, "JSON: duplicate key")
            result[key] = value
        return result

    def nonfinite(_):
        raise InvalidMaterial("JSON: nonfinite numbers are unsupported")

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=nonfinite)
        pending = [(value, 0)]
        visited = 0
        while pending:
            item, depth = pending.pop()
            visited += 1
            require(depth <= 64 and visited <= 65536, "JSON structure budget exceeded")
            if isinstance(item, str):
                item.encode("utf-8")
            elif isinstance(item, dict):
                pending.extend((part, depth + 1) for pair in item.items() for part in pair)
            elif isinstance(item, list):
                pending.extend((part, depth + 1) for part in item)
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise InvalidMaterial("invalid UTF-8 JSON (including duplicate keys or excessive nesting)") from error


def read_input(path):
    # No-follow/nonblocking prevents links and special files from becoming reads.
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_FILE, "input must be a bounded regular file")
            data = stream.read(MAX_FILE + 1)
        require(len(data) <= MAX_FILE, "input exceeds file budget")
        return data
    except OSError as error:
        raise InvalidMaterial("input file unavailable or unsafe") from error


class EvidenceReader:
    """Read each bounded artifact once; hash and parser use identical bytes."""

    def __init__(self, root):
        self.root = Path(root).resolve(strict=True)
        require(self.root.is_dir(), "evidence root must be a directory")
        self.cache = {}
        self.total = 0
        self.references = 0
        self.exhausted = False

    def read(self, reference):
        self.references += 1
        require(self.references <= MAX_REFERENCES, "evidence reference budget exceeded")
        require(not self.exhausted, "evidence byte budget exhausted")
        name = reference["path"]
        parts = PurePosixPath(name).parts
        require(name and not name.startswith("/") and "\\" not in name and all(ord(c) >= 32 for c in name) and
                parts and len(parts) <= 32 and all(p not in ("..", ".") for p in name.split("/")) and
                all(name.split("/")) and ":" not in name,
                "unsafe evidence path")
        require(PurePosixPath(name).suffix in {".json", ".csv", ".py", ".txt"}, "unsupported evidence extension")
        if name not in self.cache:
            directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                for part in parts[:-1]:
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    os.close(directory)
                    directory = child
                fd = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory)
                with os.fdopen(fd, "rb") as stream:
                    info = os.fstat(stream.fileno())
                    require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_FILE, "evidence must be a bounded regular file")
                    remaining = MAX_TOTAL - self.total
                    if info.st_size > remaining:
                        self.exhausted = True
                        raise InvalidMaterial("evidence byte budget exhausted")
                    data = stream.read(min(MAX_FILE + 1, remaining))
                    self.total += len(data)
                    require(os.fstat(stream.fileno()).st_size == len(data), "evidence changed or could not be read completely")
                require(len(data) <= MAX_FILE, "evidence exceeds file budget")
                self.cache[name] = data
            except OSError as error:
                raise InvalidMaterial("evidence unavailable or unsafe") from error
            finally:
                os.close(directory)
        data = self.cache[name]
        require(sha(data) == reference["sha256"], "evidence digest mismatch")
        return data


def validate_contract(contract):
    fields(contract, "schema_version journey target input_sha256 goals obligations scope", "contract")
    require(contract["schema_version"] == "m1", "unsupported contract schema")
    text(contract["journey"], "journey")
    fields(contract["target"], "id sha256", "target")
    text(contract["target"]["id"], "target id")
    digest(contract["target"]["sha256"], "target digest")
    digest(contract["input_sha256"], "input digest")
    fields(contract["scope"], "environment upstream claim", "scope")
    for value in contract["scope"].values():
        text(value, "scope")
    sequence(contract["obligations"], "obligations", 64)
    ids = []
    for obligation in contract["obligations"]:
        fields(obligation, "id expected required applicable exclusion mapping columns rows", "obligation")
        for key in ("id", "expected", "mapping"):
            text(obligation[key], key)
        ids.append(obligation["id"])
        require(type(obligation["required"]) is bool and type(obligation["applicable"]) is bool,
                "required and applicable must be booleans")
        if obligation["applicable"]:
            require(obligation["exclusion"] is None, "applicable obligation cannot have an exclusion")
        else:
            exclusion(obligation["exclusion"], "obligation exclusion")
        sequence(obligation["columns"], "columns", 128)
        require(obligation["columns"], "columns must be nonempty")
        for column in obligation["columns"]:
            text(column, "column")
        unique(obligation["columns"], "columns")
        sequence(obligation["rows"], "rows", 10000)
        for row in obligation["rows"]:
            require(isinstance(row, list) and len(row) == len(obligation["columns"]) and
                    all(isinstance(cell, str) and len(cell) <= 8000 for cell in row), "invalid expected row")
    unique(ids, "obligations")
    sequence(contract["goals"], "goals", 64)
    require(contract["goals"], "goals must be nonempty")
    goal_ids, routed = [], set()
    for goal in contract["goals"]:
        fields(goal, "id text source obligations gap exclusion", "goal")
        for key in ("id", "text", "source"):
            text(goal[key], f"goal {key}")
        goal_ids.append(goal["id"])
        sequence(goal["obligations"], "goal obligations", 64)
        require(all(isinstance(ref, str) and ref in ids for ref in goal["obligations"]), "unknown goal obligation")
        unique(goal["obligations"], "goal obligations")
        require(sum((bool(goal["obligations"]), goal["gap"] is not None, goal["exclusion"] is not None)) == 1,
                "goal needs exactly one routing choice")
        if goal["gap"] is not None:
            text(goal["gap"], "goal gap")
        if goal["exclusion"] is not None:
            exclusion(goal["exclusion"], "goal exclusion")
        routed.update(goal["obligations"])
    unique(goal_ids, "goals")
    require(routed == set(ids), "unrouted obligation")


def validate_run(run, obligation_ids):
    fields(run, "schema_version id contract_sha256 runtime input tool attempts execution_state cleanup retention", "run")
    require(run["schema_version"] == "m1", "unsupported run schema")
    text(run["id"], "run id")
    digest(run["contract_sha256"], "contract digest")
    artifact(run["runtime"], "runtime")
    artifact(run["input"], "input")
    fields(run["tool"], "name version", "tool")
    text(run["tool"]["name"], "tool name")
    text(run["tool"]["version"], "tool version")
    require(run["execution_state"] in ("completed", "interrupted", "unknown"), "unknown execution state")
    fields(run["cleanup"], "state details", "cleanup")
    require(run["cleanup"]["state"] in ("clean", "retained", "residual", "unknown"), "unknown cleanup state")
    text(run["cleanup"]["details"], "cleanup details")
    fields(run["retention"], "policy details", "retention")
    require(run["retention"]["policy"] == "until-owner-removes", "unsupported retention policy")
    text(run["retention"]["details"], "retention details")
    sequence(run["attempts"], "attempts", 32)
    attempt_ids = []
    for attempt in run["attempts"]:
        fields(attempt, "id execution observations", "attempt")
        text(attempt["id"], "attempt id")
        attempt_ids.append(attempt["id"])
        artifact(attempt["execution"], "execution record")
        sequence(attempt["observations"], "observations", 64)
        refs = []
        for observation in attempt["observations"]:
            fields(observation, "obligation_id artifact", "observation")
            require(isinstance(observation["obligation_id"], str) and observation["obligation_id"] in obligation_ids,
                    "unknown observation obligation")
            refs.append(observation["obligation_id"])
            artifact(observation["artifact"], "observation artifact")
        unique(refs, "observations per attempt")
    unique(attempt_ids, "attempts")


def process_record(reader, attempt, run, contract):
    record = parse_json(reader.read(attempt["execution"]))
    fields(record, "schema_version run_id attempt_id target_sha256 input_sha256 argv completed exit_code output stdout stderr", "process record")
    require(record["schema_version"] == "local-process/v1", "unsupported process record")
    require(record["run_id"] == run["id"] and record["attempt_id"] == attempt["id"], "foreign run or attempt")
    require(record["target_sha256"] == contract["target"]["sha256"] and
            record["input_sha256"] == contract["input_sha256"], "process target/input mismatch")
    sequence(record["argv"], "argv", 64)
    require(record["argv"] and all(isinstance(arg, str) and len(arg) <= 8000 for arg in record["argv"]), "invalid argv")
    require(type(record["completed"]) is bool and
            (record["exit_code"] is None or type(record["exit_code"]) is int), "invalid process termination")
    require(all(isinstance(record[key], str) and len(record[key]) <= MAX_FILE for key in ("stdout", "stderr")), "invalid process output")
    if record["output"] is not None:
        artifact(record["output"], "process output")
    require(record["completed"] and record["exit_code"] == 0, "native execution did not complete successfully")
    return record


def compare_csv(data, obligation):
    try:
        # No normalization, set comparison, row dropping, or type coercion.
        actual = list(csv.reader(io.StringIO(data.decode("utf-8"), newline=""), strict=True))
    except (UnicodeError, csv.Error):
        return "FAIL", "observed output is not valid UTF-8 CSV"
    expected = [obligation["columns"], *obligation["rows"]]
    if actual == expected:
        return "PASS", f"header and all {len(expected) - 1} expected rows match exactly"
    if not actual or actual[0] != expected[0]:
        return "FAIL", "observed CSV header differs from the frozen expectation"
    first = next((index for index, (left, right) in enumerate(zip(actual[1:], expected[1:]), 1) if left != right), None)
    detail = f"; first differing data row {first}" if first is not None else ""
    return "FAIL", f"CSV differs: expected {len(expected) - 1} data rows, observed {len(actual) - 1}{detail}"


def assess(contract, contract_bytes, run, root):
    validate_contract(contract)
    validate_run(run, {item["id"] for item in contract["obligations"]})
    reader = EvidenceReader(root)
    run_gaps = []
    if run["contract_sha256"] != sha(contract_bytes):
        run_gaps.append("frozen contract digest mismatch")
    for key, expected in (("runtime", contract["target"]["sha256"]), ("input", contract["input_sha256"])):
        try:
            require(run[key]["sha256"] == expected, f"{key} identity mismatch")
            reader.read(run[key])
        except InvalidMaterial as error:
            run_gaps.append(str(error))
    attempt_records = {}
    for attempt in run["attempts"]:
        try:
            attempt_records[attempt["id"]] = (process_record(reader, attempt, run, contract), None)
        except InvalidMaterial as error:
            attempt_records[attempt["id"]] = (None, str(error))
    results = []
    for obligation in contract["obligations"]:
        item = {"id": obligation["id"], "expected": obligation["expected"], "required": obligation["required"],
                "status": "UNVERIFIED", "reasons": [], "attempts": []}
        if not obligation["applicable"]:
            item.update(status="NOT_APPLICABLE", reasons=[obligation["exclusion"]["reason"]], exclusion=obligation["exclusion"])
            results.append(item)
            continue
        for attempt in run["attempts"]:
            record, record_error = attempt_records[attempt["id"]]
            observation = next((obs for obs in attempt["observations"] if obs["obligation_id"] == obligation["id"]), None)
            status, reason = "UNVERIFIED", "required observation missing"
            if run_gaps:
                reason = "; ".join(run_gaps)
            elif record_error:
                reason = record_error
            elif obligation["mapping"] != "csv-exact/v1":
                reason = "unsupported business mapping"
            elif observation is not None:
                try:
                    require(record["output"] is not None and observation["artifact"] == record["output"], "observation is not this attempt's output")
                    require(observation["artifact"]["path"].endswith(".csv"), "CSV mapping requires a CSV artifact")
                    status, reason = compare_csv(reader.read(observation["artifact"]), obligation)
                except InvalidMaterial as error:
                    reason = str(error)
            item["attempts"].append({"id": attempt["id"], "status": status, "reason": reason})
        states = [attempt["status"] for attempt in item["attempts"]]
        if "FAIL" in states:
            item["status"] = "FAIL"
        elif states and all(state == "PASS" for state in states):
            item["status"] = "PASS"
        item["reasons"] = [attempt["reason"] for attempt in item["attempts"]] or ["no native attempt recorded"]
        results.append(item)
    by_id = {item["id"]: item for item in results}
    goals = []
    for goal in contract["goals"]:
        status = "checked"
        if goal["gap"] is not None:
            status = "gap"
        elif goal["exclusion"] is not None:
            status = "excluded"
        elif any(by_id[ref]["status"] == "UNVERIFIED" or
                 any(a["status"] == "UNVERIFIED" for a in by_id[ref]["attempts"]) for ref in goal["obligations"]):
            status = "gap"
        goals.append({**goal, "status": status})
    required = [item for item in results if item["required"] and item["status"] != "NOT_APPLICABLE"]
    settled = run["execution_state"] == "completed" and run["cleanup"]["state"] in ("clean", "retained")
    coverage_gap = (bool(run_gaps) or not required or any(goal["status"] == "gap" for goal in goals) or
                    any(item["status"] == "UNVERIFIED" for item in required))
    partial = coverage_gap or not settled
    has_failure = any(item["status"] == "FAIL" for item in results)
    verdict = "FAIL" if has_failure else ("PASS" if not coverage_gap else "UNVERIFIED")
    return {"schema_version": "m1-report", "helper_version": VERSION, "run_id": run["id"],
            "journey": contract["journey"], "target": contract["target"], "scope": contract["scope"],
            "tool": run["tool"], "business_verdict": verdict, "qualified_pass": verdict == "PASS" and not partial,
            "completion": "partial" if partial else "complete",
            "material_status": "gaps" if run_gaps or any(item["status"] == "UNVERIFIED" or
                                any(a["status"] == "UNVERIFIED" for a in item["attempts"]) for item in results) else "checked",
            "execution_state": run["execution_state"], "cleanup": run["cleanup"], "retention": run["retention"],
            "material_usage": {"bytes_read": reader.total, "byte_limit": MAX_TOTAL, "references": reader.references},
            "goals": goals, "obligations": results, "attempts": [a["id"] for a in run["attempts"]], "gaps": run_gaps,
            "limitations": ["Checks consistency and the documented CSV comparison, not collector honesty or authorization.",
                            "Covers only submitted goals; cannot detect a user outcome omitted before contract creation.",
                            "This is a local CSV mapping, not a general production-readiness or deployment approval."]}


def escaped(value):
    value = html.escape(str(value), quote=True)
    for character in "\\`*_{}[]()#+-.!|":
        value = value.replace(character, "\\" + character)
    return value.replace("\r", " ").replace("\n", " ")


def markdown(report):
    lines = ["# Functional acceptance", "", f"Business: {report['business_verdict']} · Completion: {report['completion']}",
             "", f"Journey: {escaped(report['journey'])}", "", f"Run: {escaped(report['run_id'])}",
             "", f"Scope: {escaped(report['scope']['claim'])}", "", "## Obligations", ""]
    for item in report["obligations"]:
        lines.append(f"- {escaped(item['id'])}: {item['status']} — {escaped(item['expected'])}")
        for attempt in item["attempts"]:
            lines.append(f"  - {escaped(attempt['id'])}: {attempt['status']} — {escaped(attempt['reason'])}")
        if not item["attempts"]:
            lines.extend(f"  - {escaped(reason)}" for reason in item["reasons"])
    lines.extend(["", "## Original goals", ""])
    for goal in report["goals"]:
        detail = goal["gap"] or (goal["exclusion"]["reason"] if goal["exclusion"] else ", ".join(goal["obligations"]))
        lines.append(f"- {escaped(goal['id'])}: {goal['status']} — {escaped(goal['text'])}; {escaped(detail)}; source: {escaped(goal['source'])}")
    lines.extend(["", "## Execution and retention", "", f"Execution: {report['execution_state']}", "",
                  f"Cleanup: {report['cleanup']['state']} — {escaped(report['cleanup']['details'])}", "",
                  f"Retention: {escaped(report['retention']['details'])}", "", "## Limits", ""])
    lines.extend(f"- {escaped(limit)}" for limit in report["limitations"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--root", required=True, help="Explicit local evidence root")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", help="New report file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        contract_bytes = read_input(args.contract)
        report = assess(parse_json(contract_bytes), contract_bytes, parse_json(read_input(args.run)), args.root)
        rendered = markdown(report) if args.format == "markdown" else json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            # Buffer before publishing, create exclusively, and remove only our incomplete file.
            created = False
            try:
                with open(args.output, "x", encoding="utf-8", newline="\n") as stream:
                    created = True
                    stream.write(rendered)
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError:
                if created:
                    os.unlink(args.output)
                raise
        else:
            sys.stdout.write(rendered)
        return 1 if report["business_verdict"] == "FAIL" else (0 if report["qualified_pass"] else 2)
    except (InvalidMaterial, OSError, RecursionError, OverflowError) as error:
        # Do not echo raw input, filesystem paths, tokens, or tracebacks.
        message = str(error) if isinstance(error, InvalidMaterial) else "local input/output unavailable; no qualified report produced"
        sys.stdout.write(json.dumps({"material_status": "invalid", "error": message}) + "\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
