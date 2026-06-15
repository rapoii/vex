const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const TESTS_DIR = __dirname;
const files = fs.readdirSync(TESTS_DIR).filter(f => f.startsWith('test-') && f.endsWith('.js'));

let allPassed = true;

for (const file of files) {
  console.log(`\n--- Running ${file} ---`);
  const result = spawnSync('node', [path.join(TESTS_DIR, file)], { stdio: 'inherit' });
  if (result.status !== 0) {
    allPassed = false;
  }
}

if (!allPassed) {
  console.error('\n❌ Some tests failed.');
  process.exit(1);
} else {
  console.log('\n✅ All tests passed.');
}
