"""Package integrity and relocated execution, not agent-behavior evaluations."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "functional-acceptance"
COLLECTOR = REPO / "examples" / "paginated_export" / "accept.py"


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class SkillPackageTests(unittest.TestCase):
    def test_only_runtime_resources_ship(self):
        self.assertEqual(set(inventory(SKILL)), {
            "SKILL.md", "agents/openai.yaml", "scripts/acceptance.py",
            "references/material-format.md", "references/host-compatibility.md",
        })
        self.assertFalse(any(p.is_symlink() for p in SKILL.rglob("*")))
        # A root SKILL.md makes ecosystem installers select the entire checkout.
        self.assertFalse((REPO / "SKILL.md").exists())

    def test_shared_frontmatter_has_no_host_execution_extensions(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        metadata = dict(line.split(": ", 1) for line in text.split("---\n", 2)[1].splitlines())
        self.assertEqual(set(metadata), {"name", "description"})
        self.assertEqual(metadata["name"], SKILL.name)
        self.assertRegex(metadata["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertTrue(0 < len(metadata["description"]) <= 1024)

    def test_relative_document_links_stay_inside_package(self):
        for path in SKILL.rglob("*.md"):
            links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8"))
            for link in links:
                if urlsplit(link).scheme or link.startswith("#"):
                    continue
                target = (path.parent / unquote(link.split("#", 1)[0])).resolve()
                with self.subTest(document=str(path.relative_to(SKILL)), link=link):
                    self.assertTrue(target.is_relative_to(SKILL.resolve()))
                    self.assertTrue(target.is_file())

    def test_relocated_helper_checks_real_runs_without_checkout_dependencies(self):
        with tempfile.TemporaryDirectory(prefix="skill-package-") as temp:
            root = Path(temp)
            installed = root / "project with spaces" / ".agents" / "skills" / SKILL.name
            shutil.copytree(SKILL, installed)
            before = inventory(installed)
            for case, code, verdict in [("healthy", 0, "PASS"), ("defect", 1, "FAIL"),
                                         ("missing-observation", 2, "UNVERIFIED")]:
                with self.subTest(case=case):
                    run = root / case
                    collected = subprocess.run(
                        [sys.executable, "-B", str(COLLECTOR), "--case", case, "--run-dir", str(run)],
                        cwd=root, capture_output=True, text=True, timeout=30)
                    self.assertEqual(collected.returncode, code, collected.stdout + collected.stderr)
                    result = subprocess.run(
                        [sys.executable, "-I", "-B", str(installed / "scripts" / "acceptance.py"),
                         "--contract", str(run / "contract.json"), "--run", str(run / "run.json"),
                         "--root", str(run), "--format", "json"],
                        cwd=root, capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                    self.assertEqual(json.loads(result.stdout)["business_verdict"], verdict)
            self.assertEqual(inventory(installed), before, "Running a helper must not modify its installation")

    def test_original_cli_path_still_dispatches(self):
        with tempfile.TemporaryDirectory(prefix="skill-legacy-cli-") as temp:
            args = [sys.executable, "-I", "-B"]
            original = subprocess.run(args + [str(REPO / "scripts" / "acceptance.py"), "--help"],
                                      cwd=temp, capture_output=True, text=True, timeout=15)
            packaged = subprocess.run(args + [str(SKILL / "scripts" / "acceptance.py"), "--help"],
                                      cwd=temp, capture_output=True, text=True, timeout=15)
            self.assertEqual(original.returncode, 0, original.stderr)
            self.assertEqual(original.stdout, packaged.stdout)


if __name__ == "__main__":
    unittest.main()
