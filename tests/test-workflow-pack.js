const fs = require('fs');
const path = require('path');
const assert = require('assert');

const REPO_ROOT = path.resolve(__dirname, '..');

const REQUIRED_SKILLS = [
  ['skills/workflow/brainstorming/SKILL.md', 'brainstorming', 150],
  ['skills/workflow/subagent-development/SKILL.md', 'subagent-development', 150],
  ['skills/workflow/worktree-isolation/SKILL.md', 'worktree-isolation', 100],
  ['skills/workflow/strict-tdd/SKILL.md', 'strict-tdd', 100],
  ['skills/workflow/verification-before-completion/SKILL.md', 'verification-before-completion', 120],
  ['skills/workflow/finishing-development-branch/SKILL.md', 'finishing-development-branch', 120],
  ['skills/workflow/requesting-code-review/SKILL.md', 'requesting-code-review', 100],
  ['skills/workflow/dispatching-parallel-agents/SKILL.md', 'dispatching-parallel-agents', 120],
];

const REQUIRED_AGENTS = [
  ['agents/core/brainstormer.md', 'brainstormer'],
  ['agents/core/subagent-coordinator.md', 'subagent-coordinator'],
  ['agents/core/e2e-runner.md', 'e2e-runner'],
  ['agents/core/docs-lookup.md', 'docs-lookup'],
  ['agents/domain/database-reviewer.md', 'database-reviewer'],
  ['agents/domain/mle-reviewer.md', 'mle-reviewer'],
];

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

function readProjectFile(relativePath) {
  return fs.readFileSync(path.join(REPO_ROOT, relativePath), 'utf8');
}

function assertYamlFrontmatter(content, expectedName) {
  assert.ok(content.startsWith('---\n'), 'Missing opening YAML frontmatter delimiter');
  const endIndex = content.indexOf('\n---\n', 4);
  assert.notStrictEqual(endIndex, -1, 'Missing closing YAML frontmatter delimiter');
  const frontmatter = content.slice(4, endIndex);
  assert.match(frontmatter, new RegExp(`^name: ${expectedName}$`, 'm'), `Missing name: ${expectedName}`);
  assert.match(frontmatter, /^description: .+$/m, 'Missing description');
}

function countLines(content) {
  return content.split(/\r?\n/).length;
}

console.log('Running workflow pack tests...');

for (const [relativePath, skillName, minimumLines] of REQUIRED_SKILLS) {
  test(`${skillName} skill exists with contract`, () => {
    const content = readProjectFile(relativePath);
    assertYamlFrontmatter(content, skillName);
    assert.ok(countLines(content) >= minimumLines, `${relativePath} must have at least ${minimumLines} lines`);
    assert.match(content, /Superpowers/i, 'Must reference Superpowers methodology');
    assert.match(content, /## When to Activate/, 'Must define activation guidance');
    assert.match(content, /## Workflow/, 'Must define executable workflow');
    assert.match(content, /## Verification Checklist/, 'Must define verification checklist');
  });
}

for (const [relativePath, agentName] of REQUIRED_AGENTS) {
  test(`${agentName} agent exists with contract`, () => {
    const content = readProjectFile(relativePath);
    assertYamlFrontmatter(content, agentName);
    assert.match(content, /# Prompt Defense Baseline/, 'Agent must include prompt defense baseline');
    assert.match(content, /# Role Definition/, 'Agent must define role');
    assert.match(content, /# Workflow/, 'Agent must define workflow');
    assert.match(content, /# Output Format/, 'Agent must define output format');
  });
}

test('AGENTS.md routes new workflow agents', () => {
  const content = readProjectFile('AGENTS.md');
  assert.match(content, /brainstormer/, 'AGENTS.md must mention brainstormer');
  assert.match(content, /subagent-coordinator/, 'AGENTS.md must mention subagent-coordinator');
  assert.match(content, /e2e-runner/, 'AGENTS.md must mention e2e-runner');
  assert.match(content, /docs-lookup/, 'AGENTS.md must mention docs-lookup');
  assert.match(content, /database-reviewer/, 'AGENTS.md must mention database-reviewer');
  assert.match(content, /mle-reviewer/, 'AGENTS.md must mention mle-reviewer');
});

console.log(`\nResults: ${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
