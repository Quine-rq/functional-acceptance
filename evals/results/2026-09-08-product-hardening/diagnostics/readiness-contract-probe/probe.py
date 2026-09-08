"""Read-only existing-object UI probe; never click Confirm or submit a bookmark."""
import json, os, runpy, signal, socket, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
H = runpy.run_path(str(ROOT / 'final-handoff-runner.py'))
STOP = False

def stopped(signum, frame):
    global STOP
    STOP = True

def checkpoint():
    if STOP:
        raise RuntimeError('Probe stop requested at native boundary')

def save(path, value):
    H['save_new'](path, value)

def child():
    from playwright.sync_api import sync_playwright, expect
    signal.signal(signal.SIGTERM, stopped)
    signal.signal(signal.SIGINT, stopped)
    os.chmod(HERE, 0o700)
    baseline = H['bookmark_rows']()
    identity = H['identity']()
    old_hash = H['digest'](ROOT / 'final-results.json')
    private = json.loads((ROOT / '.acceptance-study/private.json').read_text())
    processes, groups, handles, blocked = [], [], [], []
    browser = pw = None
    start = time.monotonic()
    error_type = None
    if {r['id'] for r in baseline} != {5, 9, 14, 15} or not all(H['ports_free']().values()):
        raise RuntimeError('Unexpected baseline or occupied ports')
    env = dict(os.environ, PYTHONPATH='.acceptance-study:.', DJANGO_SETTINGS_MODULE='study_settings', LD_DISABLE_BACKGROUND_TASKS='True', PYTHONDONTWRITEBYTECODE='1')
    def launch(name, args, port):
        stdout = os.fdopen(os.open(HERE / (name+'.stdout.private.txt'), os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600), 'wb')
        stderr = os.fdopen(os.open(HERE / (name+'.stderr.private.txt'), os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600), 'wb')
        handles.extend([stdout, stderr])
        p = subprocess.Popen([str(ROOT/'.venv/bin/python'), *args], cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
        processes.append((name, p))
        for _ in range(80):
            checkpoint()
            with socket.socket() as s:
                if s.connect_ex(('127.0.0.1',port)) == 0: return
            if p.poll() is not None: raise RuntimeError('Owned server failed')
            time.sleep(.1)
        raise RuntimeError('Startup timeout')
    try:
        launch('article', ['-m','http.server','18742','--bind','127.0.0.1','--directory','.acceptance-study/article'], 18742)
        launch('application', [str(H['PACK']/'server.py'),'--project',str(ROOT)], 18741)
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=H['BROWSER'], headless=True, chromium_sandbox=True, args=['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1'])
        context = browser.new_context(service_workers='block')
        context.add_init_script(path=str(HERE/'observe.js'))
        page = context.new_page()
        page.set_default_timeout(2500)
        page.goto('http://127.0.0.1:18741/bookmarks')
        page.get_by_label('Username',exact=True).fill('fa_alice')
        page.get_by_label('Password',exact=True).fill(private['users']['fa_alice'])
        page.get_by_role('button',name='Login',exact=True).click()
        expect(page).not_to_have_url(__import__('re').compile('/login'))
        # Read-only scope after normal login; no bookmark POST can be sent.
        def readonly(route):
            if route.request.method not in ('GET','HEAD','OPTIONS'):
                blocked.append({'method':route.request.method})
                route.abort()
            else: route.continue_()
        context.route('**/*', readonly)
        for group_name in ('readiness-contract',):
            if group_name == 'frame-complete' and not any(r.get('before_cache_correlated_removal') for g in groups for r in g['rounds']):
                groups.append({'group':group_name,'rounds':[],'not_run':'No before-cache-correlated removal observed in baseline group'})
                break
            group = {'group':group_name,'rounds':[]}
            groups.append(group)
            for number in range(1,2):
                checkpoint()
                if time.monotonic()-start > 98:
                    group['stopped_for_budget'] = True
                    break
                row = {'round':number}
                group['rounds'].append(row)
                try:
                    page.goto('http://127.0.0.1:18741/bookmarks')
                    page.evaluate("window.__readonlyProbe.mark('list.ready')")
                    page.locator('ul.bookmark-list > li[data-bookmark-id="14"]').get_by_text('View',exact=True).click()
                    modal = page.locator('ld-details-modal')
                    expect(modal).to_be_visible()
                    expect(modal).to_have_attribute('data-bookmark-id','14')
                    page.evaluate("window.__readonlyProbe.mark('modal.visible')")
                    if group_name == 'frame-complete':
                        page.locator('turbo-frame#details-modal').evaluate('async frame => { await frame.loaded; }', timeout=2500)
                        page.wait_for_function("(() => { const f=document.querySelector('turbo-frame#details-modal'); return f && f.complete && !f.hasAttribute('busy') && f.getAttribute('aria-busy') !== 'true'; })()", timeout=2500)
                        page.evaluate("window.__readonlyProbe.mark('frame.stable')")
                    checkpoint()
                    page.evaluate("window.__readonlyProbe.mark('delete.begin')")
                    modal.get_by_role('button',name='Delete',exact=True).click()
                    page.evaluate("window.__readonlyProbe.mark('delete.returned')")
                    page.wait_for_timeout(450)
                    observed = page.evaluate('({events:window.__readonlyProbe.events, final_state:window.__readonlyProbe.state()})')
                    row.update(observed)
                    events = observed['events']
                    row['before_cache_correlated_removal'] = any(e['kind']=='turbo:before-cache' and e.get('phase')=='dispatch' and e['state']['dropdown_count']>0 and any(a['kind']=='turbo:before-cache' and a.get('phase')=='after-dispatch' and a['time_ms']>=e['time_ms'] and a['time_ms']-e['time_ms']<30 and a['state']['dropdown_count']==0 for a in events) for e in events)
                    row['removed_before_exit'] = any(e['kind']=='dropdown.removed' for e in events)
                    page.evaluate("window.__readonlyProbe.mark('exit.begin')")
                    cancel = page.locator('ld-confirm-dropdown').get_by_role('button',name='Cancel',exact=True)
                    if cancel.is_visible():
                        cancel.click()
                        row['exit_action'] = 'Cancel'
                    else:
                        page.keyboard.press('Escape')
                        row['exit_action'] = 'Escape'
                    row['events_after_exit'] = page.evaluate('window.__readonlyProbe.events')
                    row['state_after_exit'] = page.evaluate('window.__readonlyProbe.state()')
                    row['outcome'] = 'observed'
                except Exception as error:
                    row['outcome'] = 'observer-error'
                    row['error_type'] = type(error).__name__
                    try: row['events'] = page.evaluate('window.__readonlyProbe.events')
                    except Exception: pass
                    raise
                finally:
                    save(HERE / (group_name+'-'+str(number)+'.json'), row)
    except Exception as error:
        error_type = type(error).__name__
    finally:
        if browser:
            try: browser.close()
            except Exception: error_type = error_type or 'BrowserCloseError'
        if pw:
            try: pw.stop()
            except Exception: error_type = error_type or 'PlaywrightStopError'
        for name, p in reversed(processes):
            if p.poll() is None:
                p.terminate()
                try: p.wait(timeout=3)
                except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=2)
        for handle in handles: handle.close()
        summary = {'kind':'readiness-contract-probe','elapsed_ms':round((time.monotonic()-start)*1000),'bookmark_id':14,'groups':groups,'error_type':error_type,'blocked_write_attempts':blocked,'confirm_clicked':False,'baseline_ids':[r['id'] for r in baseline],'final_ids':[r['id'] for r in H['bookmark_rows']()],'all_bookmark_rows_unchanged':H['bookmark_rows']()==baseline,'source_and_environment_unchanged':all(H['identity']()[key]==identity[key] for key in ('scripts','environment','head','tracked_diff')), 'pack_documents_changed':[name for name, old in identity['pack_all'].items() if H['identity']()['pack_all'].get(name)!=old and not name.endswith('.py')],'old_final_results_unchanged':H['digest'](ROOT/'final-results.json')==old_hash,'processes':[{'name':n,'pid':p.pid,'returncode':p.poll()} for n,p in processes],'ports_free':H['ports_free']()}
        save(HERE/'result.json',summary)
        print(json.dumps({k:summary[k] for k in ('elapsed_ms','error_type','confirm_clicked','all_bookmark_rows_unchanged','ports_free')},ensure_ascii=False))
        print(json.dumps([{'group':g['group'],'rounds':len(g['rounds']),'before_cache_correlated_removals':sum(r.get('before_cache_correlated_removal',False) for r in g['rounds'])} for g in groups]))
    return 0 if error_type is None and summary['all_bookmark_rows_unchanged'] else 2

if __name__ == '__main__':
    if '--child' in sys.argv:
        sys.exit(child())
    os.chmod(HERE, 0o700)
    with os.fdopen(os.open(HERE/'probe.stdout.private.txt',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as stdout, os.fdopen(os.open(HERE/'probe.stderr.private.txt',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as stderr:
        started=time.monotonic()
        p=subprocess.Popen([sys.executable,str(Path(__file__)), '--child'],cwd=ROOT,stdout=stdout,stderr=stderr,start_new_session=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        try: p.wait(timeout=115)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGTERM)
            try: p.wait(timeout=max(.01,120-(time.monotonic()-started)))
            except subprocess.TimeoutExpired: os.killpg(p.pid,signal.SIGKILL); p.wait(timeout=2)
    print(json.dumps({'collector_code':p.returncode,'elapsed_ms':round((time.monotonic()-started)*1000),'result_file':str(HERE/'result.json')}))
    sys.exit(p.returncode)
