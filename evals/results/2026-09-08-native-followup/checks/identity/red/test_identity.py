"""Stdlib-only checks of the real identity probe's import-safety boundary.

The probe is extracted from test_onboarding.py, without importing pytest. The
synthetic sqlite_utils modules below only expose observable import side effects;
these tests do not claim real sqlite-utils behavior or plugin compatibility.
"""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).with_name('test_onboarding.py')


def actual_probe():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    journey = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'journey')
    assignment = next(node for node in journey.body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == 'probe' for target in node.targets))
    return ast.literal_eval(assignment.value)


@unittest.skipUnless(os.name == 'posix', 'The acceptance pack requires POSIX')
class IdentityTests(unittest.TestCase):
    def exercise(self, behavior):
        with tempfile.TemporaryDirectory(prefix='acceptance-identity-') as raw:
            root = Path(raw)
            package = root / 'sqlite_utils'
            package.mkdir()
            marker = root / 'imports.txt'
            for name, label in [('__init__.py', 'application'), ('cli.py', 'cli')]:
                (package / name).write_text(
                    "from pathlib import Path\n"
                    f"with Path({str(marker)!r}).open('a', encoding='utf-8') as stream:\n"
                    f"    stream.write({label + chr(10)!r})\n", encoding='utf-8')
            # Substitute the external distribution-metadata boundary only.
            # Probe code and its import order remain exactly the shipped source.
            bootstrap = (
                'import sys, types\n'
                f'sys.path.insert(0, {str(root)!r})\n'
                "metadata = types.ModuleType('importlib.metadata')\n"
                "metadata.version = lambda name: 'synthetic-1.0'\n"
                'def entries(*, group):\n'
                "    assert group == 'sqlite_utils'\n"
                + ("    raise RuntimeError('synthetic metadata failure')\n" if behavior == 'metadata-error'
                   else "    return [types.SimpleNamespace(name='unexpected-synthetic-plugin')]\n" if behavior == 'plugin'
                   else '    return []\n')
                + 'metadata.entry_points = entries\n'
                "sys.modules['importlib.metadata'] = metadata\n"
                f"exec(compile({actual_probe()!r}, '<actual-identity-probe>', 'exec'))\n"
            )
            result = subprocess.run(
                [sys.executable, '-I', '-S', '-B', '-c', bootstrap], cwd=root,
                env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'},
                capture_output=True, text=True, encoding='utf-8', timeout=10)
            return result, marker.read_text(encoding='utf-8') if marker.exists() else '', str(package)

    def test_unexpected_plugin_is_refused_before_application_import(self):
        result, imports, _ = self.exercise('plugin')
        self.assertEqual(imports, '', 'Application import ran before the plugin safety decision')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unexpected-synthetic-plugin', result.stderr)


if __name__ == '__main__':
    unittest.main()
