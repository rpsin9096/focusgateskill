#!/usr/bin/env node

/**
 * Notice: focus-check.mjs is deprecated in focus-gate-v0.3 in favor of
 * the canonical Python implementation (focus-check.py).
 * This delegator forwards arguments to focus-check.py.
 */

import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pyScript = path.resolve(__dirname, 'focus-check.py');

const child = spawn('python3', [pyScript, ...process.argv.slice(2)], {
  stdio: 'inherit'
});

child.on('close', (code) => {
  process.exit(code ?? 0);
});
