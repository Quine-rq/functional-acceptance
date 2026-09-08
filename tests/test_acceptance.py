"""Black-box tests for the experimental m1 material-report CLI.

All evidence is synthetic. These tests exercise material consistency and CSV
comparison, not native collection authenticity or an end-to-end user workflow.
No implementation modules are imported and no fixture program is executed.
"""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI = PROJECT_ROOT / "skills" / "functional-acceptance" / "scripts" / "acceptance.py"
HEALTHY_CSV = b"id,name\n001,Alpha\n002,Beta\n003,Gamma\n"
MISSING_PAGE_CSV = b"id,name\n001,Alpha\n002,Beta\n"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class AcceptanceCLITests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="acceptance-cli-test-")
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "run"
        self.root.mkdir()
        self.contract_path = self.root / "contract.json"
        self.run_path = self.root / "run.json"
        program = b"# Synthetic runtime evidence; never execute from a report.\n"
        # The expected rows below are fixed independently of these input bytes
        # and of every observed CSV. No exporter computes the test oracle.
        input_data = b'{"pages":[[["001","Alpha"],["002","Beta"]],[["003","Gamma"]]]}\n'
        runtime = self.write_artifact("native.py", program)
        input_ref = self.write_artifact("pages.json", input_data)
        self.contract = {
            "schema_version": "m1",
            "journey": "The local CLI exports every expected row in page order.",
            "target": {"id": "local-export", "sha256": runtime["sha256"]},
            "input_sha256": input_ref["sha256"],
            "goals": [{
                "id": "all-pages",
                "text": "Receive every row, including the final page.",
                "source": "independently reviewed synthetic sample",
                "obligations": ["csv-complete"],
                "gap": None,
                "exclusion": None,
            }],
            "obligations": [{
                "id": "csv-complete",
                "expected": "Exact header and all three literal rows in order.",
                "required": True,
                "applicable": True,
                "exclusion": None,
                "mapping": "csv-exact/v1",
                "columns": ["id", "name"],
                "rows": [["001", "Alpha"], ["002", "Beta"], ["003", "Gamma"]],
            }],
            "scope": {
                "environment": "isolated-local",
                "upstream": "synthetic-pages",
                "claim": "Only the synthetic local CLI and CSV file are checked.",
            },
        }
        self.run = {
            "schema_version": "m1",
            "id": "run-001",
            "contract_sha256": "0" * 64,
            "runtime": runtime,
            "input": input_ref,
            "tool": {"name": "synthetic-process-record", "version": "1"},
            "attempts": [],
            "execution_state": "completed",
            "cleanup": {"state": "retained", "details": "Only run-owned evidence remains."},
            "retention": {"policy": "until-owner-removes", "details": "Independent run directory."},
        }
        self.records = {}
        self.add_attempt(HEALTHY_CSV)
        self.freeze()

    def write_artifact(self, name, data):
        destination = self.root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return {"path": name, "sha256": sha256(data)}

    def add_attempt(self, csv_data):
        number = len(self.run["attempts"]) + 1
        attempt_id = "attempt-{}".format(number)
        artifact = self.write_artifact("result-{}.csv".format(number), csv_data)
        record = {
            "schema_version": "local-process/v1",
            "run_id": self.run["id"],
            "attempt_id": attempt_id,
            "target_sha256": self.contract["target"]["sha256"],
            "input_sha256": self.contract["input_sha256"],
            "argv": ["python3", "native.py", "pages.json"],
            "completed": True,
            "exit_code": 0,
            "output": copy.deepcopy(artifact),
            "stdout": "Synthetic subprocess output; not a verdict.",
            "stderr": "",
        }
        self.records[attempt_id] = record
        execution = self.write_artifact("process-{}.json".format(number), json_bytes(record))
        self.run["attempts"].append({
            "id": attempt_id,
            "execution": execution,
            "observations": [{"obligation_id": "csv-complete", "artifact": artifact}],
        })
        return number - 1

    def refresh_record(self, index=0, **changes):
        attempt = self.run["attempts"][index]
        record = self.records[attempt["id"]]
        record.update(changes)
        attempt["execution"] = self.write_artifact(
            attempt["execution"]["path"], json_bytes(record)
        )

    def replace_csv(self, data, index=0):
        attempt = self.run["attempts"][index]
        observation = attempt["observations"][0]
        artifact = self.write_artifact(observation["artifact"]["path"], data)
        observation["artifact"] = artifact
        self.refresh_record(index, output=copy.deepcopy(artifact))

    def freeze(self):
        contract_data = json_bytes(self.contract)
        self.contract_path.write_bytes(contract_data)
        self.run["contract_sha256"] = sha256(contract_data)
        self.run_path.write_bytes(json_bytes(self.run))

    def invoke(self, *, save=True, output_format="json", output=None):
        if save:
            self.freeze()
        command = [
            sys.executable, str(CLI),
            "--contract", str(self.contract_path),
            "--run", str(self.run_path),
            "--root", str(self.root),
            "--format", output_format,
        ]
        if output is not None:
            command.extend(["--output", str(output)])
        return subprocess.run(
            command, cwd=self.workspace, text=True, capture_output=True,
            timeout=10, check=False,
        )

    def read_report(self, process):
        try:
            report = json.loads(process.stdout)
        except (ValueError, TypeError) as error:
            self.fail("Expected JSON report, got stdout={!r}, stderr={!r}: {}".format(
                process.stdout, process.stderr, error
            ))
        self.assertIsInstance(report, dict)
        return report

    def assert_outcome(self, process, verdict, *, code, completion, obligation_status=None):
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        report = self.read_report(process)
        self.assertEqual(report["business_verdict"], verdict, report)
        self.assertEqual(report["completion"], completion, report)
        if obligation_status is not None:
            obligations = {item["id"]: item for item in report["obligations"]}
            item = obligations["csv-complete"]
            self.assertEqual(item["status"], obligation_status, report)
            self.assertTrue({"id", "status", "reasons", "attempts"} <= item.keys())
        return report

    def assert_invalid(self, process):
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        report = self.read_report(process)
        self.assertEqual(report.get("material_status"), "invalid", report)
        self.assertTrue(report.get("error"), report)
        self.assertNotIn("Traceback", process.stdout + process.stderr)
        return report

    def assert_not_qualified(self, process):
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        report = self.read_report(process)
        if report.get("material_status") != "invalid":
            self.assertNotEqual(report.get("business_verdict"), "PASS", report)
        self.assertNotIn("Traceback", process.stdout + process.stderr)
        return report

    def test_healthy_csv_is_qualified_scoped_pass(self):
        report = self.assert_outcome(
            self.invoke(), "PASS", code=0, completion="complete", obligation_status="PASS"
        )
        self.assertTrue({
            "business_verdict", "completion", "cleanup", "goals", "obligations",
            "attempts", "material_status", "limitations",
        } <= report.keys())
        self.assertTrue(report["limitations"], "A report must retain provenance limitations.")

    def test_missing_final_page_is_a_completed_acceptance_with_business_failure(self):
        self.replace_csv(MISSING_PAGE_CSV)
        self.assert_outcome(
            self.invoke(), "FAIL", code=1, completion="complete", obligation_status="FAIL"
        )

    def test_exact_csv_mapping_does_not_normalize_away_counterexamples(self):
        cases = {
            "duplicate row": HEALTHY_CSV + b"003,Gamma\n",
            "reordered rows": b"id,name\n002,Beta\n001,Alpha\n003,Gamma\n",
            "numeric coercion": b"id,name\n1,Alpha\n2,Beta\n3,Gamma\n",
            "duplicate header": b"id,id\n001,Alpha\n002,Beta\n003,Gamma\n",
            "extra column": b"id,name\n001,Alpha,ignored\n002,Beta\n003,Gamma\n",
            "missing column": b"id,name\n001\n002,Beta\n003,Gamma\n",
        }
        for name, data in cases.items():
            with self.subTest(counterexample=name):
                self.replace_csv(data)
                self.assert_outcome(
                    self.invoke(), "FAIL", code=1, completion="complete", obligation_status="FAIL"
                )

    def test_duplicates_required_by_the_contract_are_not_deduplicated(self):
        self.contract["obligations"][0]["rows"].append(["003", "Gamma"])
        self.contract["obligations"][0]["expected"] = "The final literal row occurs twice."
        self.replace_csv(HEALTHY_CSV + b"003,Gamma\n")
        self.assert_outcome(
            self.invoke(), "PASS", code=0, completion="complete", obligation_status="PASS"
        )
        self.replace_csv(HEALTHY_CSV)
        self.assert_outcome(
            self.invoke(), "FAIL", code=1, completion="complete", obligation_status="FAIL"
        )

    def test_valid_csv_quoting_is_parsed_as_content_not_raw_lines(self):
        self.contract["obligations"][0]["rows"] = [
            ["001", "Alpha"], ["002", "Beta, B"], ["003", "Gamma\nG"],
        ]
        self.replace_csv(b'id,name\r\n001,Alpha\r\n002,"Beta, B"\r\n003,"Gamma\nG"\r\n')
        self.assert_outcome(
            self.invoke(), "PASS", code=0, completion="complete", obligation_status="PASS"
        )

    def test_malformed_observed_csv_is_a_counterexample_not_missing_evidence(self):
        for data in (b'id,name\n001,"unterminated\n', b"id,name\n001,\xff\n"):
            with self.subTest(data=data):
                self.replace_csv(data)
                self.assert_outcome(
                    self.invoke(), "FAIL", code=1, completion="complete", obligation_status="FAIL"
                )

    def test_explicitly_expected_empty_result_can_pass(self):
        self.contract["obligations"][0]["rows"] = []
        self.contract["obligations"][0]["expected"] = "Header only for an explicitly empty result."
        self.replace_csv(b"id,name\n")
        self.assert_outcome(
            self.invoke(), "PASS", code=0, completion="complete", obligation_status="PASS"
        )

    def test_missing_csv_remains_unverified(self):
        (self.root / "result-1.csv").unlink()
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )

    def test_modified_csv_cannot_use_its_previous_digest(self):
        (self.root / "result-1.csv").write_bytes(MISSING_PAGE_CSV)
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )

    def test_rechecking_overwritten_evidence_does_not_reuse_prior_pass(self):
        original = self.invoke()
        self.assert_outcome(original, "PASS", code=0, completion="complete")
        (self.root / "result-1.csv").write_bytes(MISSING_PAGE_CSV)
        self.assert_outcome(
            self.invoke(save=False), "UNVERIFIED", code=2,
            completion="partial", obligation_status="UNVERIFIED",
        )
        self.assertEqual(json.loads(original.stdout)["business_verdict"], "PASS")

    def test_wrong_run_or_attempt_identity_cannot_qualify_correct_csv(self):
        for field, wrong_value in (("run_id", "yesterdays-run"), ("attempt_id", "other-attempt")):
            with self.subTest(field=field):
                changes = {"run_id": "run-001", "attempt_id": "attempt-1"}
                changes[field] = wrong_value
                self.refresh_record(**changes)
                self.assert_outcome(
                    self.invoke(), "UNVERIFIED", code=2,
                    completion="partial", obligation_status="UNVERIFIED",
                )

    def test_wrong_executed_target_digest_is_unverified(self):
        self.refresh_record(target_sha256="f" * 64)
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )

    def test_modified_runtime_and_input_snapshots_do_not_qualify(self):
        for name in ("native.py", "pages.json"):
            with self.subTest(artifact=name):
                artifact = self.root / name
                original = artifact.read_bytes()
                artifact.write_bytes(original + b"\n")
                self.assert_outcome(
                    self.invoke(), "UNVERIFIED", code=2,
                    completion="partial", obligation_status="UNVERIFIED",
                )
                artifact.write_bytes(original)

    def test_observation_must_match_the_native_process_output(self):
        another = self.write_artifact("unrelated.csv", HEALTHY_CSV)
        self.refresh_record(output=another)
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )

    def test_nonzero_or_unterminated_process_is_an_execution_gap(self):
        for completed, exit_code in ((True, 1), (False, None)):
            with self.subTest(completed=completed, exit_code=exit_code):
                self.refresh_record(completed=completed, exit_code=exit_code)
                self.assert_outcome(
                    self.invoke(), "UNVERIFIED", code=2,
                    completion="partial", obligation_status="UNVERIFIED",
                )

    def test_stdout_claiming_pass_does_not_override_actual_csv_failure(self):
        self.replace_csv(MISSING_PAGE_CSV)
        self.refresh_record(stdout='{"verdict":"PASS","all_checks_passed":true}')
        self.assert_outcome(
            self.invoke(), "FAIL", code=1, completion="complete", obligation_status="FAIL"
        )

    def test_contract_digest_binds_exact_bytes_not_reformatted_json(self):
        self.freeze()
        self.contract_path.write_bytes(json_bytes(self.contract) + b"\n")
        self.assert_not_qualified(self.invoke(save=False))

    def test_goal_gap_preserves_partial_coverage_and_valid_obligation_fact(self):
        self.contract["goals"].append({
            "id": "browser-download",
            "text": "Download through the requested browser entrypoint.",
            "source": "explicit original request",
            "obligations": [],
            "gap": "A browser observation is unavailable.",
            "exclusion": None,
        })
        report = self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="PASS"
        )
        self.assertIn("browser-download", {item["id"] for item in report["goals"]})

    def test_missing_required_observation_cannot_inherit_another_obligation_pass(self):
        other = copy.deepcopy(self.contract["obligations"][0])
        other["id"] = "independent-observation"
        self.contract["obligations"].append(other)
        self.contract["goals"][0]["obligations"].append(other["id"])
        report = self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="PASS"
        )
        statuses = {item["id"]: item["status"] for item in report["obligations"]}
        self.assertEqual(statuses[other["id"]], "UNVERIFIED")

    def test_valid_failure_takes_precedence_over_another_unverified_obligation(self):
        other = copy.deepcopy(self.contract["obligations"][0])
        other["id"] = "independent-observation"
        self.contract["obligations"].append(other)
        self.contract["goals"][0]["obligations"].append(other["id"])
        self.replace_csv(MISSING_PAGE_CSV)
        report = self.assert_outcome(
            self.invoke(), "FAIL", code=1, completion="partial", obligation_status="FAIL"
        )
        statuses = {item["id"]: item["status"] for item in report["obligations"]}
        self.assertEqual(statuses[other["id"]], "UNVERIFIED")

    def test_sourced_exclusion_does_not_block_otherwise_complete_scoped_acceptance(self):
        self.contract["goals"].append({
            "id": "browser-download",
            "text": "Download through a browser entrypoint.",
            "source": "original request subsequently narrowed by its owner",
            "obligations": [],
            "gap": None,
            "exclusion": {
                "reason": "The owner explicitly limits this sample to the local CLI.",
                "source": "reviewed synthetic owner decision",
            },
        })
        report = self.assert_outcome(
            self.invoke(), "PASS", code=0, completion="complete", obligation_status="PASS"
        )
        self.assertIn("browser-download", {item["id"] for item in report["goals"]})

    def test_unknown_mapping_is_unverified_not_an_invalid_contract_or_fallback_pass(self):
        self.contract["obligations"][0]["mapping"] = "csv-unknown/v9"
        report = self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )
        self.assertNotEqual(report["material_status"], "invalid")

    def test_no_attempts_or_observations_does_not_pass(self):
        self.run["attempts"][0]["observations"] = []
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )
        self.run["attempts"] = []
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )

    def test_all_inapplicable_is_not_a_qualified_pass(self):
        obligation = self.contract["obligations"][0]
        obligation["applicable"] = False
        obligation["exclusion"] = {"reason": "Sample feature not applicable.", "source": "sample owner"}
        report = self.assert_not_qualified(self.invoke())
        self.assertNotEqual(report["material_status"], "invalid")
        self.assertEqual(report["obligations"][0]["status"], "NOT_APPLICABLE")

    def test_duplicate_or_unrouted_obligations_are_invalid(self):
        original = copy.deepcopy(self.contract)
        for case in ("duplicate id", "unrouted", "unknown goal reference", "conflicting route"):
            with self.subTest(case=case):
                self.contract = copy.deepcopy(original)
                if case == "duplicate id":
                    self.contract["obligations"].append(copy.deepcopy(self.contract["obligations"][0]))
                elif case == "unrouted":
                    self.contract["goals"][0]["obligations"] = []
                    self.contract["goals"][0]["gap"] = "Unavailable tool."
                elif case == "unknown goal reference":
                    self.contract["goals"][0]["obligations"] = ["not-defined"]
                else:
                    self.contract["goals"][0]["gap"] = "A gap cannot accompany a routing list."
                self.assert_invalid(self.invoke())

    def test_duplicate_goal_attempt_and_observation_ids_are_invalid(self):
        original_contract = copy.deepcopy(self.contract)
        original_run = copy.deepcopy(self.run)
        for case in ("goal", "attempt", "observation"):
            with self.subTest(collection=case):
                self.contract = copy.deepcopy(original_contract)
                self.run = copy.deepcopy(original_run)
                if case == "goal":
                    self.contract["goals"].append(copy.deepcopy(self.contract["goals"][0]))
                elif case == "attempt":
                    self.run["attempts"].append(copy.deepcopy(self.run["attempts"][0]))
                else:
                    observations = self.run["attempts"][0]["observations"]
                    observations.append(copy.deepcopy(observations[0]))
                self.assert_invalid(self.invoke())

    def test_required_structure_unknown_versions_and_extra_keys_are_invalid(self):
        original = copy.deepcopy(self.contract)
        for case in ("unknown version", "extra key", "missing key", "empty goals", "nonboolean required"):
            with self.subTest(case=case):
                self.contract = copy.deepcopy(original)
                if case == "unknown version":
                    self.contract["schema_version"] = "m2"
                elif case == "extra key":
                    self.contract["verdict"] = "PASS"
                elif case == "missing key":
                    del self.contract["scope"]
                elif case == "empty goals":
                    self.contract["goals"] = []
                else:
                    self.contract["obligations"][0]["required"] = "true"
                self.assert_invalid(self.invoke())

    def test_duplicate_json_keys_in_contract_or_run_are_invalid(self):
        for name in ("contract", "run"):
            with self.subTest(document=name):
                self.freeze()
                destination = self.contract_path if name == "contract" else self.run_path
                raw = destination.read_bytes().replace(
                    b'"schema_version": "m1"',
                    b'"schema_version": "m1", "schema_version": "m1"', 1,
                )
                destination.write_bytes(raw)
                if name == "contract":
                    self.run["contract_sha256"] = sha256(raw)
                    self.run_path.write_bytes(json_bytes(self.run))
                self.assert_invalid(self.invoke(save=False))

    def test_nonfinite_json_is_invalid(self):
        self.freeze()
        raw = self.contract_path.read_bytes().replace(b'"required": true', b'"required": NaN', 1)
        self.contract_path.write_bytes(raw)
        self.run["contract_sha256"] = sha256(raw)
        self.run_path.write_bytes(json_bytes(self.run))
        self.assert_invalid(self.invoke(save=False))

    def test_failure_is_not_washed_green_by_a_later_success(self):
        self.replace_csv(MISSING_PAGE_CSV)
        self.add_attempt(HEALTHY_CSV)
        report = self.assert_outcome(
            self.invoke(), "FAIL", code=1, completion="complete", obligation_status="FAIL"
        )
        self.assertEqual(len(report["attempts"]), 2)
        self.assertEqual(len(report["obligations"][0]["attempts"]), 2)

    def test_a_later_unknown_attempt_prevents_pass_without_erasing_valid_failure(self):
        self.add_attempt(HEALTHY_CSV)
        self.run["attempts"][1]["observations"] = []
        self.assert_outcome(
            self.invoke(), "UNVERIFIED", code=2, completion="partial", obligation_status="UNVERIFIED"
        )
        self.replace_csv(MISSING_PAGE_CSV)
        process = self.invoke()
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        report = self.read_report(process)
        self.assertEqual(report["business_verdict"], "FAIL", report)
        self.assertEqual(report["obligations"][0]["status"], "FAIL", report)

    def test_optional_valid_counterexample_still_takes_precedence(self):
        self.contract["obligations"][0]["required"] = False
        self.replace_csv(MISSING_PAGE_CSV)
        process = self.invoke()
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        report = self.read_report(process)
        self.assertEqual(report["business_verdict"], "FAIL", report)
        self.assertEqual(report["obligations"][0]["status"], "FAIL", report)

    def test_unfinished_execution_or_cleanup_does_not_erase_business_facts(self):
        for execution, cleanup in (("unknown", "retained"), ("interrupted", "retained"),
                                   ("completed", "residual"), ("completed", "unknown")):
            with self.subTest(execution=execution, cleanup=cleanup):
                self.run["execution_state"] = execution
                self.run["cleanup"]["state"] = cleanup
                self.assert_outcome(
                    self.invoke(), "PASS", code=2, completion="partial", obligation_status="PASS"
                )

    def test_valid_failure_keeps_failure_exit_code_when_cleanup_is_unknown(self):
        self.replace_csv(MISSING_PAGE_CSV)
        self.run["cleanup"]["state"] = "unknown"
        self.assert_outcome(
            self.invoke(), "FAIL", code=1, completion="partial", obligation_status="FAIL"
        )

    def test_absolute_traversal_and_unsupported_evidence_paths_are_rejected(self):
        outside = self.workspace / "outside.csv"
        outside.write_bytes(HEALTHY_CSV)
        self.write_artifact("result.bin", HEALTHY_CSV)
        for name in (str(outside), "../outside.csv", "result.bin"):
            with self.subTest(path=name):
                reference = {"path": name, "sha256": sha256(HEALTHY_CSV)}
                self.run["attempts"][0]["observations"][0]["artifact"] = copy.deepcopy(reference)
                self.refresh_record(output=reference)
                self.assert_not_qualified(self.invoke())
        self.assertEqual(outside.read_bytes(), HEALTHY_CSV)

    def test_symlinked_and_nonregular_evidence_are_rejected(self):
        outside = self.workspace / "outside.csv"
        outside.write_bytes(HEALTHY_CSV)
        destination = self.root / "result-1.csv"
        destination.unlink()
        try:
            destination.symlink_to(outside)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Creating a symlink is unavailable: {}".format(error))
        self.assert_not_qualified(self.invoke())
        destination.unlink()
        destination.mkdir()
        self.assert_not_qualified(self.invoke())

    def test_oversized_evidence_and_json_are_rejected_not_truncated_into_pass(self):
        self.replace_csv(HEALTHY_CSV + b"\n" * (2 * 1024 * 1024))
        self.assert_not_qualified(self.invoke())
        self.replace_csv(HEALTHY_CSV)
        self.freeze()
        raw = self.contract_path.read_bytes() + b" " * (2 * 1024 * 1024)
        self.contract_path.write_bytes(raw)
        self.run["contract_sha256"] = sha256(raw)
        self.run_path.write_bytes(json_bytes(self.run))
        self.assert_invalid(self.invoke(save=False))

    def test_excessive_evidence_references_cannot_return_a_partial_pass(self):
        for _ in range(129):
            self.add_attempt(HEALTHY_CSV)
        self.assert_not_qualified(self.invoke())

    def test_report_is_read_only_and_does_not_execute_recorded_commands(self):
        marker = self.workspace / "must-not-exist.txt"
        payload = "from pathlib import Path; Path({!r}).write_text('executed')".format(str(marker))
        runtime = self.write_artifact("native.py", payload.encode("utf-8"))
        self.run["runtime"] = runtime
        self.contract["target"]["sha256"] = runtime["sha256"]
        self.refresh_record(
            target_sha256=runtime["sha256"], argv=[sys.executable, "-c", payload]
        )
        self.freeze()
        before = {str(item.relative_to(self.root)): item.read_bytes() for item in self.root.rglob("*") if item.is_file()}
        self.assert_outcome(self.invoke(save=False), "PASS", code=0, completion="complete")
        after = {str(item.relative_to(self.root)): item.read_bytes() for item in self.root.rglob("*") if item.is_file()}
        self.assertEqual(after, before)
        self.assertFalse(marker.exists(), "Recorded argv/runtime is data, not a command to execute.")

    def test_markdown_does_not_render_supplied_html_or_remote_image_syntax(self):
        dangerous = 'Probe <script>alert(1)</script> ![pixel](https://example.invalid/pixel.png)'
        self.contract["journey"] = dangerous
        self.contract["goals"][0]["text"] = dangerous
        process = self.invoke(output_format="markdown")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("PASS", process.stdout)
        self.assertNotIn("<script>", process.stdout)
        self.assertNotIn("![pixel](https://example.invalid/pixel.png)", process.stdout)
        self.assertNotRegex(process.stdout, r"(?<!\\)!\[[^\n]*\]\(https?://")

    def test_new_output_file_contains_the_report(self):
        destination = self.root / "report.json"
        process = self.invoke(output=destination)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        report = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(report["business_verdict"], "PASS")
        self.assertEqual(report["completion"], "complete")

    def test_existing_output_and_input_files_are_never_overwritten(self):
        destination = self.root / "report.json"
        destination.write_bytes(b"keep this previous report\n")
        process = self.invoke(output=destination)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertEqual(destination.read_bytes(), b"keep this previous report\n")
        self.freeze()
        original_contract = self.contract_path.read_bytes()
        process = self.invoke(save=False, output=self.contract_path)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertEqual(self.contract_path.read_bytes(), original_contract)

    def test_dangling_output_symlink_does_not_create_its_target(self):
        destination = self.root / "report.json"
        outside = self.workspace / "must-not-create.json"
        try:
            destination.symlink_to(outside)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Creating a symlink is unavailable: {}".format(error))
        process = self.invoke(output=destination)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertTrue(destination.is_symlink())
        self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
