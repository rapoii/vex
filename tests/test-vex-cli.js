const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const assert = require('assert');

const REPO_ROOT = path.resolve(__dirname, '..');
const VEX_CLI = path.join(REPO_ROOT, 'tools', 'vex.py');

function runVex(args, cwd = REPO_ROOT) {
  return spawnSync('python', [VEX_CLI, ...args], { cwd, encoding: 'utf-8' });
}

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (err) {
    console.error(`❌ ${name}`);
    console.error(err.message);
    failed++;
  }
}

console.log('Running VEX CLI tests...');

// 1. Help output
test('shows help and exits 0', () => {
  const result = runVex(['--help']);
  assert.strictEqual(result.status, 0, `Expected 0, got ${result.status}`);
  assert.match(result.stdout, /usage:/i);
  assert.match(result.stdout, /scan/);
  assert.match(result.stdout, /status/);
});

// 2. Doctor JSON output
test('doctor command returns valid JSON envelope', () => {
  const result = runVex(['doctor', '--json']);
  // Doctor might fail initially if config missing, but must be valid JSON
  const parsed = JSON.parse(result.stdout);
  assert.ok('ok' in parsed, 'Missing ok flag');
  assert.ok('command' in parsed, 'Missing command field');
  assert.strictEqual(parsed.command, 'doctor');
});

// 3. Subcommand propagation (we test scan wrapper)
test('scan wrapper propagates extra args', () => {
  // Pass an invalid flag to scan, should see it propagated to the sub-script
  const result = runVex(['scan', '--invalid-flag-for-test']);
  assert.notStrictEqual(result.status, 0, 'Expected failure on invalid flag');
  // Argparse in vex_skill_gen.py should catch it
  assert.ok(result.stderr.includes('unrecognized arguments') || result.stderr.includes('invalid_flag'), 'Args not propagated');
});

console.log(`\nResults: ${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
