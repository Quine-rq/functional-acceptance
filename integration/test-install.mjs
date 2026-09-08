// Tests the real, pinned installer in disposable projects, not host model behavior.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync,
  rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, '..');
const skill = join(repo, 'skills', 'functional-acceptance');
const cli = join(here, 'node_modules', 'skills', 'bin', 'cli.mjs');
const name = 'functional-acceptance';
const destinations = {
  codex: '.agents/skills',
  'claude-code': '.claude/skills',
  cursor: '.agents/skills',
  'github-copilot': '.agents/skills',
  opencode: '.agents/skills',
};

function workspace(t) {
  const root = mkdtempSync(join(tmpdir(), 'acceptance-install-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const project = join(root, 'project with spaces');
  mkdirSync(project);
  writeFileSync(join(project, 'user-file.txt'), 'preserve this file');
  for (const path of new Set(Object.values(destinations))) {
    const other = join(project, path, 'unrelated-skill');
    mkdirSync(other, { recursive: true });
    writeFileSync(join(other, 'SKILL.md'), '---\nname: unrelated-skill\ndescription: Do not change me\n---\n');
  }
  return project;
}

function run(cwd, args, expected = 0) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd, encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024,
    // Local sources, explicit project targets and noninteractive flags avoid
    // downloads, selection history and global Skill installation.
    env: { ...process.env, CI: 'true', DO_NOT_TRACK: '1', DISABLE_TELEMETRY: '1' },
  });
  assert.equal(result.error, undefined, result.error?.message);
  assert.equal(result.signal, null);
  assert.equal(result.status, expected, result.stdout + result.stderr);
  return result.stdout;
}

function inventory(root, prefix = '') {
  const files = {};
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    const path = join(root, entry.name);
    assert.equal(lstatSync(path).isSymbolicLink(), false, `Unexpected link: ${relative}`);
    if (entry.isDirectory()) Object.assign(files, inventory(path, relative));
    else {
      assert.ok(entry.isFile(), relative);
      files[relative] = createHash('sha256').update(readFileSync(path)).digest('hex');
    }
  }
  return files;
}

function install(project, agent, source = repo) {
  run(project, ['add', source, '--skill', name, '--agent', agent, '--copy', '--yes']);
  const installed = join(project, destinations[agent], name);
  assert.deepEqual(inventory(installed), inventory(skill));
  assert.equal(readFileSync(join(project, 'user-file.txt'), 'utf8'), 'preserve this file');
  return installed;
}

function remove(project) {
  // Remove this name from all project paths: universal hosts share one copy.
  run(project, ['remove', name, '--yes']);
  for (const path of new Set(Object.values(destinations))) {
    assert.equal(existsSync(join(project, path, name)), false);
  }
  assert.equal(readFileSync(join(project, 'user-file.txt'), 'utf8'), 'preserve this file');
  for (const path of new Set(Object.values(destinations))) {
    assert.equal(readFileSync(join(project, path, 'unrelated-skill', 'SKILL.md'), 'utf8'),
      '---\nname: unrelated-skill\ndescription: Do not change me\n---\n');
  }
}

test('standard YAML parses without host-specific execution directives', () => {
  const frontmatter = readFileSync(join(skill, 'SKILL.md'), 'utf8').split('---\n')[1];
  const metadata = parse(frontmatter, { uniqueKeys: true });
  assert.deepEqual(Object.keys(metadata).sort(), ['description', 'name']);
  assert.equal(metadata.name, name);
  assert.equal(typeof metadata.description, 'string');
});

for (const agent of Object.keys(destinations)) {
  test(`${agent}: discover, install, reinstall and remove exact package bytes`, t => {
    const project = workspace(t);
    const before = inventory(project);
    const listed = run(project, ['add', repo, '--list']);
    assert.match(listed, /functional-acceptance/);
    assert.deepEqual(inventory(project), before, 'Listing must not install anything');
    install(project, agent);
    install(project, agent);
    remove(project);
  });
}

test('reinstall replaces local edits; it is not a safe merge or backup', t => {
  const project = workspace(t);
  const installed = install(project, 'claude-code');
  writeFileSync(join(installed, 'SKILL.md'), 'a disposable local edit');
  writeFileSync(join(installed, 'local-only.txt'), 'also replaced');
  install(project, 'claude-code');
  assert.equal(existsSync(join(installed, 'local-only.txt')), false);
  remove(project);
});

test('universal hosts share one copy, Claude uses its own copy', t => {
  const project = workspace(t);
  for (const agent of Object.keys(destinations)) install(project, agent);
  const paths = Object.values(destinations).map(path => join(project, path, name));
  assert.equal(new Set(paths).size, 2);
  remove(project);
});

test('an unknown host fails without modifying the project', t => {
  const project = workspace(t);
  const before = inventory(project);
  run(project, ['add', repo, '--skill', name, '--agent', 'not-a-host', '--copy', '--yes'], 1);
  assert.deepEqual(inventory(project), before);
});

test('a missing Skill name fails without installing a substitute', t => {
  const project = workspace(t);
  const before = inventory(project);
  run(project, ['add', repo, '--skill', 'missing-skill', '--agent', 'codex', '--copy', '--yes'], 1);
  assert.deepEqual(inventory(project), before);
});
