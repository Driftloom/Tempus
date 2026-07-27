module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']
    ],
    'scope-enum': [2, 'always', ['core', 'chrome', 'vscode', 'memory', 'tasks', 'router', 'mcp', 'email', 'api', 'agents', 'guardrails', 'evals']],
    'subject-case': [0]
  }
};
