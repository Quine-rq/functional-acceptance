#!/usr/bin/env node
// Read-only development utility. It neither installs nor grants replacement authority.
import { constants, closeSync, fstatSync, lstatSync, openSync, readFileSync,
  readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export function inventory(root) {
  if (!lstatSync(root).isDirectory() || lstatSync(root).isSymbolicLink()) {
    throw new Error('Expected an ordinary package directory');
  }
  const entries = Object.create(null);
  let count = 0, bytes = 0;
  function walk(dir, prefix, depth) {
    if (depth > 16) throw new Error('Package nesting exceeds the review limit');
    for (const entry of readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      if (++count > 256) throw new Error('Package entry count exceeds the review limit');
      const relative = prefix + entry.name;
      const path = join(dir, entry.name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) throw new Error('Symlink found: review ordinary copies only');
      if (stat.isDirectory()) {
        entries[relative + '/'] = { type: 'directory' };
        walk(path, relative + '/', depth + 1);
      } else {
        if (!stat.isFile() || stat.size > 2 * 1024 * 1024) {
          throw new Error('Unsupported or oversized package entry');
        }
        bytes += stat.size;
        if (bytes > 16 * 1024 * 1024) throw new Error('Package exceeds the review byte limit');
        const fd = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
        try {
          const opened = fstatSync(fd);
          if (!opened.isFile() || opened.ino !== stat.ino || opened.dev !== stat.dev || opened.size !== stat.size) {
            throw new Error('Package changed while being reviewed');
          }
          const content = readFileSync(fd);
          const after = fstatSync(fd);
          if (content.length !== stat.size || after.size !== stat.size || after.mtimeMs !== opened.mtimeMs) {
            throw new Error('Package changed while being reviewed');
          }
          entries[relative] = { type: 'file', sha256: createHash('sha256').update(content).digest('hex'),
            execute_bits: opened.mode & 0o111 };
        } finally { closeSync(fd); }
      }
    }
  }
  walk(root, '', 0);
  if (entries['SKILL.md']?.type !== 'file') throw new Error('Package has no ordinary SKILL.md');
  return entries;
}

export function difference(before, after) {
  return {
    added: Object.keys(after).filter(key => !(key in before)).sort(),
    removed: Object.keys(before).filter(key => !(key in after)).sort(),
    changed: Object.keys(before).filter(key => key in after && JSON.stringify(before[key]) !== JSON.stringify(after[key])).sort(),
  };
}

export function reviewUpdate(baseline, installed, candidate) {
  const oldFiles = inventory(baseline), localFiles = inventory(installed), newFiles = inventory(candidate);
  const local = difference(oldFiles, localFiles);
  const unchanged = Object.values(local).every(entries => entries.length === 0);
  return { schema_version: 'package-review/v1',
    status: unchanged ? 'unmodified' : 'local-changes',
    local_changes: local, proposed_changes: difference(oldFiles, newFiles),
    baseline: oldFiles, installed: localFiles, candidate: newFiles,
    limitations: 'Read-only comparison of trusted, quiescent local copies. No source authentication, semantic approval, installer-lock validation, atomic upgrade or concurrent-writer protection.' };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 3) throw new Error('Usage: node integration/review-update.mjs BASELINE INSTALLED STAGED_CANDIDATE');
    const result = reviewUpdate(...args);
    console.log(JSON.stringify(result, null, 2));
    process.exitCode = result.status === 'unmodified' ? 0 : 2;
  } catch (error) {
    console.error(JSON.stringify({ status: 'unverified', error: error.code || error.message }));
    process.exitCode = 1;
  }
}
