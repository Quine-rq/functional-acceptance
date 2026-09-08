"""Single-variable timing probe; uses actual pack supervisor and child roles."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

task = Path.cwd()
pack = task / 'outputs/functional-acceptance/examples/sqlite_utils/acceptance'
spec = importlib.util.spec_from_file_location('lifecycle', pack / 'lifecycle.py')
lifecycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lifecycle)
base = task / 'work/lifecycle-startup-probe'
base.mkdir()
results = []
for timeout in (.5, 4):
    run = base / str(timeout)
    run.mkdir()
    code = 'import runpy,sys,time; time.sleep(.65); sys.argv='+repr([str(pack / 'test_lifecycle.py'), '--child', 'leader', str(run), 'orphan'])+'; runpy.run_path(sys.argv[0],run_name="__main__")'
    with (run / 'stdout').open('wb') as out, (run / 'stderr').open('wb') as err:
        rc = lifecycle.run_group([sys.executable, '-B', '-c', code], cwd=run,
             env={'PATH': '/usr/bin:/bin'}, stdout=out, stderr=err, run=run, timeout=timeout)
    result=json.loads((run / 'termination.json').read_text())
    assert result['cleanup']['terminal'], result
    results.append({'timeout':timeout,'returncode':rc,'state':result['state'],
                    'writer_started':(run/'writer.json').exists(),'cleanup':result['cleanup']})
assert [r['returncode'] for r in results] == [124, 70], results
(base/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
