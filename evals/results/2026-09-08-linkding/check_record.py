"""Check this captured study record, not the live application or authenticity."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
inventory = json.loads((ROOT / 'files.json').read_text())
for item in inventory['files']:
    file = (ROOT / item['path']).resolve()
    assert file.is_relative_to(ROOT), item['path']
    assert hashlib.sha256(file.read_bytes()).hexdigest() == item['exported_sha256'], item['path']

attempts = []
for group in ('initial', 'replay'):
    for result_file in sorted((ROOT / 'artifacts' / group).glob('*/result.json')):
        result = json.loads(result_file.read_text())
        events = [json.loads(line) for line in result_file.with_name('events.jsonl').read_text().splitlines()]
        identity = next(e for e in events if e['kind'] == 'identity')
        executed = result_file.with_name('executed_regression.py').read_bytes()
        assert hashlib.sha256(executed).hexdigest() == identity['script_sha256']
        assert identity['head'] == '65813a75404b1319aca8b09700fadc0b15adabaf'
        assert events[-1]['kind'] == 'finished'
        assert events[-1]['exit_code'] == result['exit_code']
        assert all(p['returncode'] is not None and p['port_closed'] for p in result['processes'])
        attempts.append(result)

assert len(attempts) == 6  # independent blocked attempt plus five assisted attempts
assert sum(r['exit_code'] == 0 for r in attempts) == 1
passed = ROOT / 'artifacts/replay/assisted-run-20260908T052630285071Z'
result = json.loads((passed / 'result.json').read_text())
events = [json.loads(line) for line in (passed / 'events.jsonl').read_text().splitlines()]
assert len(result['checks']) == 24 and set(result['checks'].values()) == {'PASS'}
assert result['execution_cleanup'] == 'stopped'
checks = {e['name']: e for e in events if e['kind'] == 'check'}
assert set(checks) == set(result['checks'])
assert all(e['status'] == 'PASS' for e in checks.values())
db = {e['label']: e['rows'] for e in events if e['kind'] == 'database_observation'}
target, control = result['target_id'], result['control_id']
assert (target, control) == (3, 4)
assert db['initial'] == db['invalid URL'] == db['control cleaned']
assert [r['id'] for r in db['initial']] == [1, 2]
assert [r['id'] for r in db['target deleted']] == [1, 2, control]
saved = next(r for r in db['save_private_tags_notes'] if r['id'] == target)
assert saved == next(r for r in db['server_restart_retrieval'] if r['id'] == target)
assert saved == next(r for r in db['owner_unchanged_after_attack'] if r['id'] == target)
assert saved['owner'] == 'fa_alice' and saved['shared'] == 0
assert checks['real_http_metadata']['evidence']['requested_article'] == saved['url']
assert checks['real_http_metadata']['evidence']['response_status'] == 200
assert checks['bob_edit_get_denied']['evidence']['status'] == 404
write = next(e for e in events if e['kind'] == 'bob_exact_id_write_attempt')
assert write['bookmark_id'] == target and write['status'] == 404
restart = next(e for e in events if e['kind'] == 'restart_correlated')
assert restart['old_pid'] != restart['new_pid'] and restart['bookmark_id'] == target
assert len([e for e in events if e['kind'] == 'browser_started']) == len([e for e in events if e['kind'] == 'browser_closed']) == 5
assert not any(e['kind'] in ('cleanup_unresolved', 'blocked_out_of_scope_request', 'obstacle') for e in events)
assert (ROOT / 'replay/assisted_regression.py').read_bytes() == (passed / 'executed_regression.py').read_bytes()
print('Record checks passed: captured hashes, 6 retained attempts, one complete 24-subcheck journey. This does not rerun linkding or authenticate collection.')
