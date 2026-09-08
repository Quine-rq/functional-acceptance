import assert from 'node:assert/strict';
import { chmodSync, cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync,
  realpathSync, renameSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { inventory, reviewUpdate } from './review-update.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, '..'), skill = join(repo, 'skills/functional-acceptance');
const cli = join(here, 'node_modules/skills/bin/cli.mjs');
const reviewer = join(here, 'review-update.mjs');

function setup(t) {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'acceptance-upgrade-')));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const baseline = join(root, 'reviewed baseline');
  cpSync(skill, baseline, { recursive: true, errorOnExist: true, force: false });
  const project = join(root, 'user project');
  mkdirSync(project);
  writeFileSync(join(project, 'unrelated.txt'), 'keep this user file');
  return { root, baseline, project };
}

function install(project, agent, { interrupt = false, marker } = {}) {
  const destination = join(project, agent === 'claude-code' ? '.claude/skills' : '.agents/skills', 'functional-acceptance');
  const args = interrupt ? ['--import', join(here, 'fixtures/interrupt-copy.mjs')] : [];
  args.push(cli, 'add', repo, '--skill', 'functional-acceptance', '--agent', agent, '--copy', '--yes');
  const result = spawnSync(process.execPath, args, {
    cwd: project, encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024,
    env: { ...process.env, CI: 'true', DO_NOT_TRACK: '1', DISABLE_TELEMETRY: '1',
      ACCEPTANCE_FAULT_DESTINATION: destination, ACCEPTANCE_FAULT_MARKER: marker || '' },
  });
  assert.equal(result.error, undefined, result.error?.message);
  if (interrupt) {
    assert.equal(result.signal, 'SIGKILL', result.stdout + result.stderr);
    assert.equal(JSON.parse(readFileSync(marker)).event, 'copied-SKILL-before-termination');
  } else {
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(inventory(destination), inventory(skill));
  }
  return destination;
}

test('read-only review distinguishes local changes from the proposed update', t => {
  const { root, baseline, project } = setup(t);
  const installed = install(project, 'codex');
  const staged = join(root, 'candidate'); cpSync(skill, staged, { recursive: true });
  writeFileSync(join(staged, 'SKILL.md'), readFileSync(join(staged, 'SKILL.md'), 'utf8') + '\nCandidate update.\n');
  assert.equal(reviewUpdate(baseline, installed, staged).status, 'unmodified');
  writeFileSync(join(installed, 'local-notes.txt'), 'local customization');
  const before = inventory(installed);
  const result = spawnSync(process.execPath, [reviewer, baseline, installed, staged], { encoding: 'utf8', timeout: 10000 });
  assert.equal(result.status, 2);
  const review = JSON.parse(result.stdout);
  assert.deepEqual(review.local_changes.added, ['local-notes.txt']);
  assert.deepEqual(review.proposed_changes.changed, ['SKILL.md']);
  assert.deepEqual(inventory(installed), before, 'Review must not change installed bytes');
});

test('review detects removed files and executable-bit changes', t => {
  const { baseline, project } = setup(t);
  const installed = install(project, 'codex');
  rmSync(join(installed, 'references/host-compatibility.md'));
  const script = join(installed, 'scripts/acceptance.py');
  chmodSync(script, inventory(baseline)['scripts/acceptance.py'].execute_bits ? 0o644 : 0o755);
  const review = reviewUpdate(baseline, installed, skill);
  assert.deepEqual(review.local_changes.removed, ['references/host-compatibility.md']);
  assert.deepEqual(review.local_changes.changed, ['scripts/acceptance.py']);
});

test('removing only owner execute permission is detected when execution becomes EACCES', t => {
  const { baseline, project } = setup(t);
  const installed = install(project, 'codex');
  for (const directory of [baseline, installed]) {
    writeFileSync(join(directory, 'probe.sh'), '#!/bin/sh\nexit 0\n');
    chmodSync(join(directory, 'probe.sh'), 0o755);
  }
  const probe = join(installed, 'probe.sh');
  assert.equal(spawnSync(probe, [], { timeout: 1000 }).status, 0);
  chmodSync(probe, 0o655);
  assert.equal(spawnSync(probe, [], { timeout: 1000 }).error?.code, 'EACCES');
  const review = reviewUpdate(baseline, installed, baseline);
  assert.equal(review.status, 'local-changes');
  assert.deepEqual(review.local_changes.changed, ['probe.sh']);
});

test('review treats prototype-like filenames and empty directories as local changes', t => {
  const { baseline, project } = setup(t);
  const installed = install(project, 'codex');
  for (const name of ['__proto__', 'constructor', 'toString']) writeFileSync(join(installed, name), 'local');
  mkdirSync(join(installed, 'empty-local'));
  const review = reviewUpdate(baseline, installed, skill);
  assert.equal(review.status, 'local-changes');
  assert.deepEqual(review.local_changes.added, ['__proto__', 'constructor', 'empty-local/', 'toString']);
});

test('review refuses links, missing entrypoint, oversize files and excessive entries', t => {
  const { root, baseline } = setup(t);
  const linked = join(root, 'link'); symlinkSync(baseline, linked, 'dir');
  assert.throws(() => inventory(linked), /ordinary/);
  symlinkSync(join(baseline, 'SKILL.md'), join(baseline, 'alias.md'));
  assert.throws(() => inventory(baseline), /Symlink/);
  rmSync(join(baseline, 'alias.md'));
  const empty = join(root, 'empty'); mkdirSync(empty);
  assert.throws(() => inventory(empty), /SKILL.md/);
  writeFileSync(join(baseline, 'oversized.txt'), Buffer.alloc(2 * 1024 * 1024 + 1));
  assert.throws(() => inventory(baseline), /oversized/);
  rmSync(join(baseline, 'oversized.txt'));
  for (let n = 0; n < 257; n++) writeFileSync(join(baseline, `extra-${n}`), '');
  assert.throws(() => inventory(baseline), /entry count/);
});

for (const agent of ['codex', 'claude-code']) {
  test(`${agent}: interrupted direct reinstall loses local edits; reviewed backup restores them`, t => {
    const { root, project } = setup(t);
    const installed = install(project, agent);
    writeFileSync(join(installed, 'local-only.txt'), 'keep local customization');
    const backup = join(root, 'backup'); cpSync(installed, backup, { recursive: true });
    const before = inventory(backup);
    const lock = join(project, 'skills-lock.json');
    const oldLock = existsSync(lock) ? readFileSync(lock) : null;
    install(project, agent, { interrupt: true, marker: join(root, 'fault.json') });
    assert.equal(existsSync(join(installed, 'local-only.txt')), false);
    assert.notDeepEqual(inventory(installed), inventory(skill));
    // The process is confirmed terminated by spawnSync. Preserve the partial copy.
    renameSync(installed, join(root, 'interrupted-copy'));
    cpSync(backup, installed, { recursive: true, errorOnExist: true, force: false });
    assert.deepEqual(inventory(installed), before);
    if (oldLock) assert.deepEqual(readFileSync(lock), oldLock);
    assert.equal(readFileSync(join(project, 'unrelated.txt'), 'utf8'), 'keep this user file');
  });

  test(`${agent}: interrupted staging never touches the live copy; replace and rollback preserve backups`, t => {
    const { root, baseline, project } = setup(t);
    const live = install(project, agent);
    // Reviewed synthetic older instruction, identical in baseline and live.
    // The staged current package must introduce a real byte-level difference.
    for (const directory of [baseline, live]) {
      writeFileSync(join(directory, 'SKILL.md'), readFileSync(join(directory, 'SKILL.md'), 'utf8') + '\nOlder reviewed instruction.\n');
    }
    const before = inventory(live);
    const stage1 = join(root, 'failed staging'); mkdirSync(stage1);
    install(stage1, agent, { interrupt: true, marker: join(root, 'fault.json') });
    assert.deepEqual(inventory(live), before);
    const stage2 = join(root, 'fresh staging'); mkdirSync(stage2);
    const candidate = install(stage2, agent);
    const review = reviewUpdate(baseline, live, candidate);
    assert.equal(review.status, 'unmodified');
    assert.deepEqual(review.proposed_changes.changed, ['SKILL.md']);
    // Simulates the documented, single-writer maintenance window, not an atomic
    // directory exchange or live-host reload. Backups are outside discovery roots.
    const backup = join(root, 'old copy');
    renameSync(live, backup);
    renameSync(candidate, live);
    assert.deepEqual(inventory(live), inventory(skill));
    assert.deepEqual(inventory(backup), before);
    renameSync(live, join(root, 'candidate retained'));
    renameSync(backup, live);
    assert.deepEqual(inventory(live), before);
    assert.equal(readFileSync(join(project, 'unrelated.txt'), 'utf8'), 'keep this user file');
  });
}
