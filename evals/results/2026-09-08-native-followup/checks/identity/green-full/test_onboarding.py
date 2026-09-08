"""Real CLI processes; independent JSON contract and read-only SQLite observations."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

import pytest
from acceptance.lifecycle import write_record

ROOT = Path(__file__).resolve().parents[1]
CONTACTS = [
    {'id': 17, 'name': '合成联系人·林 🌙', 'note': '第一行\n第二行', 'email': None, 'rank': 0, 'score': 1.25},
    {'id': 4, 'name': 'Synthetic "Ada"', 'note': 'She said "hello". \\ path', 'email': '', 'rank': -2, 'score': 0.0},
    {'id': 93, 'name': 'Élodie テスト', 'note': '', 'email': 'synthetic@example.invalid', 'rank': 7, 'score': -3.5},
]
SENTINEL = [{'id': 'unrelated-01', 'note': '合成保留数据 "keep"\n原样', 'optional': None}]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def same_contacts(actual):
    assert isinstance(actual, list)
    assert len(actual) == len(CONTACTS)
    assert len({r['id'] for r in actual}) == len(CONTACTS)
    # Canonical JSON distinguishes null/empty string, booleans/numbers and types.
    canonical = lambda rows: json.dumps(sorted(rows, key=lambda r: r['id']), ensure_ascii=False, sort_keys=True)
    assert canonical(actual) == canonical(CONTACTS)


@pytest.fixture(scope='module')
def journey():
    run = Path(os.environ['ACCEPTANCE_RUN_DIR']).resolve()
    assert run.is_relative_to(ROOT / 'artifacts')
    db = run / 'contacts.db'
    commands = {}

    def invoke(label, args, module=True):
        argv = [sys.executable, '-B'] + (['-m', 'sqlite_utils'] if module else []) + [str(a) for a in args]
        outpath, errpath = run / (label + '.stdout'), run / (label + '.stderr')
        started = time.time()
        with outpath.open('wb') as out, errpath.open('wb') as err:
            p = subprocess.Popen(argv, cwd=ROOT, env=dict(os.environ), stdout=out, stderr=err)
            timed_out = False
            try:
                write_record(run / (label + '.started.json'), {
                    'argv': argv, 'cwd': str(ROOT), 'pid': p.pid, 'pgid': os.getpgid(p.pid),
                    'started_unix': started, 'stdout': outpath.name, 'stderr': errpath.name, 'terminal': False,
                })
                try:
                    rc = p.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    p.kill()
                    rc = p.wait(timeout=2)
            finally:
                if p.poll() is None:
                    p.kill()
                    p.wait(timeout=2)
        record = {'argv': argv, 'cwd': str(ROOT), 'pid': p.pid, 'returncode': rc, 'timed_out': timed_out, 'started_unix': started, 'ended_unix': time.time(), 'stdout': outpath.name, 'stderr': errpath.name, 'terminal': True}
        write_record(run / (label + '.command.json'), record)
        commands[label] = record
        assert not timed_out, 'CLI timed out; stop observations and let the runner reap its owned group'
        return record

    probe = """import sys
import importlib.metadata as m
plugins = [entry.name for entry in m.entry_points(group='sqlite_utils')]
if plugins:
    print('Unexpected sqlite-utils plugins; refusing application import: ' + ', '.join(plugins), file=sys.stderr)
    raise SystemExit(2)
versions = {name: m.version(name) for name in ('sqlite-utils', 'pytest')}
import os, json, sqlite3, sqlite_utils, sqlite_utils.cli
print(json.dumps({'executable':sys.executable,'python':sys.version,'cwd':os.getcwd(),'uid':os.getuid(),'sqlite':sqlite3.sqlite_version,'package':sqlite_utils.__file__,'cli':sqlite_utils.cli.__file__,'version':versions['sqlite-utils'],'pytest':versions['pytest'],'plugins':plugins}))
"""
    invoke('00-identity', ['-c', probe], module=False)
    identity = json.loads((run / '00-identity.stdout').read_text())
    assert Path(identity['package']).resolve() == ROOT / 'sqlite_utils/__init__.py'
    assert Path(identity['cli']).resolve() == ROOT / 'sqlite_utils/cli.py'
    assert identity['plugins'] == [], 'Unexpected environment plugins; do not execute unknown extensions'
    save(run / 'identity.json', identity)
    files = list((ROOT / 'sqlite_utils').rglob('*.py')) + [ROOT / 'pyproject.toml', ROOT / 'ONBOARDING-REQUIREMENTS.md', ROOT / 'acceptance/test_onboarding.py', ROOT / 'acceptance/run.py', ROOT / 'acceptance/lifecycle.py']
    save(run / 'source-sha256.json', {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    for cmd in ('insert', 'query', 'rows'):
        assert invoke('help-' + cmd, [cmd, '--help'])['returncode'] == 0
    save(run / 'contacts.input.json', CONTACTS)
    save(run / 'unrelated.input.json', SENTINEL)
    duplicate = [{**CONTACTS[0], 'name': 'MUST NOT REPLACE', 'note': 'changed', 'email': 'wrong@example.invalid'}]
    save(run / 'duplicate.input.json', duplicate)

    def snapshot(label):
        with closing(sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            schema = [dict(r) for r in conn.execute("select type,name,tbl_name,sql from sqlite_master where tbl_name='unrelated' order by type,name")]
            rows = [dict(r) for r in conn.execute('select * from unrelated order by id')]
            tables = [r[0] for r in conn.execute("select name from sqlite_master where type='table' order by name")]
            contacts = [dict(r) for r in conn.execute('select * from contacts order by id')] if 'contacts' in tables else None
            result = {'schema': schema, 'unrelated': rows, 'tables': tables, 'contacts': contacts}
        save(run / (label + '.snapshot.json'), result)
        return result

    assert invoke('01-seed', ['insert', db, 'unrelated', run / 'unrelated.input.json', '--pk', 'id'])['returncode'] == 0
    snapshots = [snapshot('01-seeded')]
    invoke('02-import', ['insert', db, 'contacts', run / 'contacts.input.json', '--pk', 'id'])
    snapshots.append(snapshot('02-imported'))
    invoke('03-read-new-process', ['query', db, 'select * from contacts order by id'])
    snapshots.append(snapshot('03-read'))
    invoke('04-export', ['rows', db, 'contacts'])
    # Retain exact stdout bytes as the JSON export, then reopen in the test.
    (run / 'contacts.export.json').write_bytes((run / '04-export.stdout').read_bytes())
    snapshots.append(snapshot('04-exported'))
    invoke('05-duplicate', ['insert', db, 'contacts', run / 'duplicate.input.json', '--pk', 'id'])
    snapshots.append(snapshot('05-rejected'))
    invoke('06-read-after-rejection', ['rows', db, 'contacts'])
    snapshots.append(snapshot('06-final'))
    save(run / 'writer-state.json', {'state': 'all CLI processes terminated and waited; all observer connections closed', 'database': str(db)})
    return run, commands, snapshots


def test_import_persists_exact_values(journey):
    _, commands, snapshots = journey
    assert commands['02-import']['returncode'] == 0
    same_contacts(snapshots[1]['contacts'])


def test_new_cli_process_reads_all_contacts(journey):
    run, commands, _ = journey
    assert commands['03-read-new-process']['returncode'] == 0
    assert commands['03-read-new-process']['started_unix'] >= commands['02-import']['ended_unix']
    same_contacts(json.loads((run / '03-read-new-process.stdout').read_text()))


def test_retained_json_export_roundtrips(journey):
    run, commands, _ = journey
    assert commands['04-export']['returncode'] == 0
    same_contacts(json.loads((run / 'contacts.export.json').read_text()))


def test_duplicate_id_is_visible_and_preserves_every_contact(journey):
    run, commands, snapshots = journey
    result = commands['05-duplicate']
    assert not result['timed_out']
    assert result['returncode'] != 0
    diagnostic = (run / '05-duplicate.stderr').read_text() + (run / '05-duplicate.stdout').read_text()
    assert 'UNIQUE constraint failed: contacts.id' in diagnostic
    same_contacts(snapshots[4]['contacts'])
    assert commands['06-read-after-rejection']['returncode'] == 0
    same_contacts(json.loads((run / '06-read-after-rejection.stdout').read_text()))


def test_unrelated_table_schema_and_row_preserved_at_every_boundary(journey):
    _, _, snapshots = journey
    assert snapshots[0]['unrelated'] == SENTINEL
    assert snapshots[0]['schema']
    for snapshot in snapshots:
        assert snapshot['unrelated'] == SENTINEL
        assert snapshot['schema'] == snapshots[0]['schema']
    assert snapshots[-1]['tables'] == ['contacts', 'unrelated']
