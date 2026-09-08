"""One read-only metadata diagnostic; never saves a bookmark."""
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib.parse import urlsplit, parse_qs
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[2]
env = dict(os.environ, PYTHONPATH='.acceptance-study:.', DJANGO_SETTINGS_MODULE='study_settings', LD_DISABLE_BACKGROUND_TASKS='True')
processes = []
facts = []
try:
    for port, args in [(18742, ['-m', 'http.server', '18742', '--bind', '127.0.0.1', '--directory', '.acceptance-study/article']), (18741, ['manage.py', 'runserver', '127.0.0.1:18741', '--noreload'])]:
        with socket.socket() as s:
            assert s.connect_ex(('127.0.0.1', port)) != 0, 'port occupied'
        p = subprocess.Popen([str(root / '.venv/bin/python'), *args], cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(p)
        for _ in range(100):
            assert p.poll() is None, 'server exited'
            with socket.socket() as s:
                if s.connect_ex(('127.0.0.1', port)) == 0: break
            time.sleep(.1)
        else: raise RuntimeError('startup timeout')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True, chromium_sandbox=True, args=['--disable-background-networking', '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1'])
        try:
            context = browser.new_context(service_workers='block')
            context.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname == '127.0.0.1' and urlsplit(route.request.url).port in (18741, 18742) else route.abort())
            page = context.new_page()
            page.goto('http://127.0.0.1:18741/login/')
            secret = json.loads((root / '.acceptance-study/private.json').read_text())['users']['fa_alice']
            page.get_by_label('Username', exact=True).fill('fa_alice')
            page.get_by_label('Password', exact=True).fill(secret)
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page).not_to_have_url('http://127.0.0.1:18741/login/')
            page.goto('http://127.0.0.1:18741/bookmarks/new')
            page.on('response', lambda r: facts.append({'path': urlsplit(r.url).path, 'status': r.status, 'article': parse_qs(urlsplit(r.url).query).get('url')}) if '/api/bookmarks/check' in r.url else None)
            page.get_by_label('URL', exact=True).fill('http://127.0.0.1:18742/article.html?diagnostic=metadata')
            expect(page.get_by_label('Title', exact=True)).to_have_value('Acceptance study article', timeout=10000)
            facts.append({'rendered_title': page.get_by_label('Title', exact=True).input_value(), 'bookmark_saved': False})
        finally:
            browser.close()
finally:
    for p in reversed(processes):
        if p.poll() is None:
            p.terminate()
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=5)
        facts.append({'owned_pid': p.pid, 'returncode': p.poll()})
    with (Path(__file__).parent / 'metadata-diagnostic.json').open('x') as f:
        json.dump(facts, f, indent=2)
print(json.dumps(facts, indent=2))
