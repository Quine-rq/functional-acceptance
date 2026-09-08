"""Frozen old m1 material reading, not replaying a historical product run."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / 'fixtures' / 'm1-history'
SKILL = REPO / 'skills' / 'functional-acceptance'


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class MaterialCompatibilityTests(unittest.TestCase):
    def test_frozen_fixture_digests_and_declared_normalization(self):
        provenance = json.loads((FIXTURES / 'provenance.json').read_text())
        self.assertEqual(provenance['source_commit'], 'edc295c285da4550ec2fadca1e2f455d5be06fef')
        self.assertEqual(len(provenance['runs']), 3)
        for run in provenance['runs']:
            with self.subTest(case=run['scenario']):
                self.assertEqual(hashes(FIXTURES / run['scenario']), run['published_sha256'])
                changed = {name for name in run['original_sha256']
                           if run['original_sha256'][name] != run['published_sha256'][name]}
                self.assertEqual(changed, {'run.json', 'attempt-1/execution.json'})
                self.assertEqual(run['old_collector_exit'], run['current_helper_exit'])

    def check(self, installed, root):
        return subprocess.run([sys.executable, '-I', '-B', str(installed / 'scripts/acceptance.py'),
                               '--contract', str(root / 'contract.json'), '--run', str(root / 'run.json'),
                               '--root', str(root), '--format', 'json'], cwd=root.parent,
                              capture_output=True, text=True, timeout=20)

    def test_installed_helper_preserves_old_verdicts_and_material(self):
        with tempfile.TemporaryDirectory(prefix='acceptance-legacy-') as directory:
            root = Path(directory)
            installed = root / 'relocated skill'; shutil.copytree(SKILL, installed)
            before = hashes(installed)
            for scenario, code, verdict in [('healthy', 0, 'PASS'), ('defect', 1, 'FAIL'),
                                             ('missing-observation', 2, 'UNVERIFIED')]:
                with self.subTest(case=scenario):
                    material = root / scenario; shutil.copytree(FIXTURES / scenario, material)
                    prior = hashes(material)
                    result = self.check(installed, material)
                    self.assertEqual(result.returncode, code, result.stderr + result.stdout)
                    self.assertEqual(json.loads(result.stdout)['business_verdict'], verdict)
                    self.assertEqual(hashes(material), prior)
            self.assertEqual(hashes(installed), before)

    def test_unknown_schema_is_not_silently_migrated(self):
        with tempfile.TemporaryDirectory(prefix='acceptance-future-') as directory:
            root = Path(directory) / 'run'; shutil.copytree(FIXTURES / 'healthy', root)
            file = root / 'run.json'; data = json.loads(file.read_text())
            data['schema_version'] = 'future-unimplemented'
            file.write_text(json.dumps(data))
            before = hashes(root)
            result = self.check(SKILL, root)
            self.assertEqual(result.returncode, 2, result.stdout)
            response = json.loads(result.stdout)
            self.assertEqual(response['material_status'], 'invalid')
            self.assertIn('unsupported run schema', response['error'])
            self.assertNotIn('business_verdict', response)
            self.assertEqual(hashes(root), before)

    def test_missing_old_evidence_cannot_reuse_a_previous_pass(self):
        with tempfile.TemporaryDirectory(prefix='acceptance-missing-old-') as directory:
            root = Path(directory) / 'run'; shutil.copytree(FIXTURES / 'healthy', root)
            self.assertEqual(self.check(SKILL, root).returncode, 0)
            (root / 'attempt-1/output.csv').unlink()
            result = self.check(SKILL, root)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertFalse(json.loads(result.stdout)['qualified_pass'])


if __name__ == '__main__':
    unittest.main()
