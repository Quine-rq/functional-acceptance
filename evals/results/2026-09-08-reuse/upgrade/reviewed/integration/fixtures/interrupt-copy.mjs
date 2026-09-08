// Development-only fault injection into the real pinned installer. Not shipped.
// Only the explicitly named copy destination in this disposable test is affected.
import fs from 'node:fs/promises';
import { writeFileSync } from 'node:fs';
import { syncBuiltinESMExports } from 'node:module';
import { join, resolve, sep } from 'node:path';

const target = process.env.ACCEPTANCE_FAULT_DESTINATION;
const marker = process.env.ACCEPTANCE_FAULT_MARKER;
if (!target || !marker) throw new Error('Fault destination and marker are required');
const prefix = resolve(target) + sep;
const original = fs.cp;
fs.cp = async function (source, destination, options) {
  if (resolve(String(destination)).startsWith(prefix)) {
    // The CLI copies entries concurrently. Copy one complete entry and terminate
    // before any other intercepted entry, giving a reproducible partial package.
    if (String(destination) === join(target, 'SKILL.md')) {
      await original.call(this, source, destination, options);
      writeFileSync(marker, JSON.stringify({ event: 'copied-SKILL-before-termination' }), { flag: 'wx' });
      process.kill(process.pid, 'SIGKILL');
    }
    return new Promise(() => {});
  }
  return original.call(this, source, destination, options);
};
syncBuiltinESMExports();
