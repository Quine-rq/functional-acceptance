// Optional, no-model host probe. Uses an already installed Codex; no login or config changes.
import assert from 'node:assert/strict';
import { mkdtempSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const cli = join(here, 'node_modules', 'skills', 'bin', 'cli.mjs');
const project = realpathSync(mkdtempSync(join(tmpdir(), 'acceptance-codex-discovery-')));
const env = { ...process.env, CI: 'true', DO_NOT_TRACK: '1', DISABLE_TELEMETRY: '1' };
let server;
let closePromise;
let lines;
const waiting = new Map();
let sequence = 0;
let startupDiagnostics = '';

function command(executable, args) {
  const result = spawnSync(executable, args, { cwd: project, env, encoding: 'utf8', timeout: 15000 });
  assert.equal(result.error, undefined, result.error?.message);
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return result.stdout.trim();
}

function rpc(method, params) {
  return new Promise((resolveResult, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => {
      waiting.delete(id);
      reject(new Error(`${method}: timed out; ${startupDiagnostics || 'no classified startup error'}`));
    }, 10000);
    waiting.set(id, { resolveResult, reject, timer });
    server.stdin.write(`${JSON.stringify({ id, method, params })}\n`);
  });
}

function rejectPending(error) {
  for (const pending of waiting.values()) {
    clearTimeout(pending.timer);
    pending.reject(error);
  }
  waiting.clear();
}

try {
  const version = command('codex', ['--version']);
  command('git', ['init', '--quiet']);
  command(process.execPath, [cli, 'add', resolve(here, '..'), '--skill', 'functional-acceptance',
    '--agent', 'codex', '--copy', '--yes']);
  server = spawn('codex', ['app-server', '--stdio'], { cwd: project, env, stdio: ['pipe', 'pipe', 'pipe'] });
  server.stderr.on('data', chunk => {
    // Classify startup failures without exposing settings or credentials.
    const text = chunk.toString();
    if (/Operation not permitted|Permission denied/i.test(text)) startupDiagnostics = 'startup permission error';
    else if (/error|failed/i.test(text) && !startupDiagnostics) startupDiagnostics = 'startup error (details not retained)';
  });
  closePromise = new Promise(resolveClose => server.once('close', resolveClose));
  server.on('error', rejectPending);
  server.stdin.on('error', rejectPending);
  server.on('close', () => rejectPending(new Error('Codex closed before responding')));
  lines = createInterface({ input: server.stdout });
  lines.on('line', line => {
    let message;
    try { message = JSON.parse(line); } catch { return; }
    const pending = waiting.get(message.id);
    if (!pending) return;
    clearTimeout(pending.timer);
    waiting.delete(message.id);
    if (message.error) pending.reject(new Error(JSON.stringify(message.error)));
    else pending.resolveResult(message.result);
  });
  await rpc('initialize', { clientInfo: { name: 'acceptance-discovery-check', version: '0.1.0' } });
  server.stdin.write(`${JSON.stringify({ method: 'initialized' })}\n`);
  const result = await rpc('skills/list', { cwds: [project], forceReload: true });
  const target = join(project, '.agents', 'skills', 'functional-acceptance', 'SKILL.md');
  const entry = result.data.find(item => item.cwd === project);
  assert.ok(entry, 'Host must return the requested project');
  const matches = entry.skills.filter(item => item.name === 'functional-acceptance' && item.path === target);
  assert.equal(matches.length, 1, 'Host must discover exactly the installed copy');
  assert.equal(matches[0].enabled, true);
  assert.equal(matches[0].scope, 'repo');
  assert.equal(matches[0].interface.displayName, 'Functional Acceptance');
  assert.deepEqual(entry.errors.filter(item => item.path.startsWith(join(project, '.agents'))), []);
  command(process.execPath, [cli, 'remove', 'functional-acceptance', '--yes']);
  const removed = await rpc('skills/list', { cwds: [project], forceReload: true });
  assert.equal(removed.data.flatMap(item => item.skills).some(item => item.path === target), false);
  console.log(JSON.stringify({ host: version, installed_discovered: true, enabled: true,
    scope: 'repo', ui_metadata_loaded: true, removed_not_discovered: true,
    model_invoked: false, workflow_execution: 'not tested' }, null, 2));
} finally {
  for (const pending of waiting.values()) clearTimeout(pending.timer);
  lines?.close();
  if (server) {
    server.stdin.end();
    const timer = setTimeout(() => server.kill('SIGKILL'), 3000);
    await closePromise;
    clearTimeout(timer);
  }
  rmSync(project, { recursive: true, force: true });
}
