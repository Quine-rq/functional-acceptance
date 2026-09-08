"""Run the native pytest pack with all writes confined to a fresh artifact directory."""
import datetime
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from acceptance.lifecycle import run_group
run = ROOT / 'artifacts' / ('onboarding-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
run.mkdir(parents=True)
for name in ('tmp', 'home', 'config', 'cache'):
    (run / name).mkdir()
env = {
    'PATH': str(Path(sys.executable).parent) + ':/usr/bin:/bin',
    'HOME': str(run / 'home'),
    'XDG_CONFIG_HOME': str(run / 'config'),
    'XDG_CACHE_HOME': str(run / 'cache'),
    'TMPDIR': str(run / 'tmp'), 'TMP': str(run / 'tmp'), 'TEMP': str(run / 'tmp'),
    'PYTHONPATH': str(ROOT), 'PYTHONNOUSERSITE': '1',
    'PYTHONDONTWRITEBYTECODE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
    'ACCEPTANCE_RUN_DIR': str(run), 'LC_ALL': 'en_US.UTF-8',
}
cmd = [sys.executable, '-B', '-m', 'pytest', 'acceptance/test_onboarding.py', '-v', '-p', 'no:cacheprovider', '--basetemp', str(run / 'pytest-tmp'), '--junitxml', str(run / 'pytest.xml')]
(run / 'invocation.json').write_text(json.dumps({'cwd': str(ROOT), 'argv': cmd, 'environment': env}, indent=2))
print('Evidence: ' + str(run), flush=True)
with (run / 'pytest.stdout.txt').open('wb') as out, (run / 'pytest.stderr.txt').open('wb') as err:
    code = run_group(cmd, cwd=ROOT, env=env, stdout=out, stderr=err, run=run)
print((run / 'pytest.stdout.txt').read_text())
print((run / 'pytest.stderr.txt').read_text())
sys.exit(code)
