---
name: ci-cd-setup
description: Design safe CI/CD pipelines for GitHub Actions, GitLab CI, and Jenkins with matrix builds, dependency caching, secret handling, deployment gates, and rollback checks.
argument-hint: "[platform | app-stack | deploy-target]"
metadata:
  origin: VEX
---

# CI/CD Setup

Use this skill when building or reviewing pipelines that build, test, package, scan, and deploy software from version control.

## Triggers

- User asks for CI, CD, pipeline, workflow, deploy automation, release gate, or build matrix.
- Repo has `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `Dockerfile`, Helm charts, or deploy scripts.
- A branch or PR needs repeatable validation before merge.
- A deploy must use environment secrets, approvals, or rollback steps.
- Existing pipeline is slow, flaky, or leaks credentials in logs.

## Inputs To Inspect

- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, or `build.gradle`.
- Lockfiles: `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`.
- Existing CI files: `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`.
- Runtime files: `Dockerfile`, `docker-compose.yml`, `helm/`, `k8s/`, `terraform/`.
- Test entrypoints and coverage settings.
- Secret names referenced in config; never inspect secret values.
- Branch protection and release requirements if available.

## Pipeline Shape

1. Trigger on pull requests for validation.
2. Trigger on default branch for publish/deploy.
3. Install dependencies from lockfile only.
4. Cache package manager and build caches by lockfile hash.
5. Run lint, typecheck, tests, and security scan before packaging.
6. Build artifact or container once; promote same artifact through environments.
7. Require manual approval for production.
8. Run smoke checks after deploy.
9. Keep rollback command documented but not automatic unless platform supports safe revision rollback.

## GitHub Actions Baseline

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node-version: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test -- --coverage
      - run: npm run build --if-present
```

## GitLab CI Baseline

```yaml
stages: [validate, package, deploy]

variables:
  NODE_ENV: test

cache:
  key:
    files:
      - package-lock.json
  paths:
    - .npm/

validate:node:
  image: node:22-alpine
  stage: validate
  parallel:
    matrix:
      - NODE_VERSION: ["20", "22"]
  before_script:
    - npm ci --cache .npm --prefer-offline
  script:
    - npm run lint --if-present
    - npm test -- --coverage
    - npm run build --if-present
  artifacts:
    when: always
    reports:
      junit: junit.xml
    paths:
      - coverage/
```

## Jenkins Declarative Pipeline

```groovy
pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  environment { NODE_ENV = 'test' }
  stages {
    stage('Install') {
      steps { sh 'npm ci' }
    }
    stage('Validate') {
      parallel {
        stage('Lint') { steps { sh 'npm run lint --if-present' } }
        stage('Test') { steps { sh 'npm test -- --coverage' } }
        stage('Build') { steps { sh 'npm run build --if-present' } }
      }
    }
    stage('Deploy production') {
      when { branch 'main' }
      steps {
        input message: 'Deploy production?'
        sh './scripts/deploy.sh production'
      }
    }
  }
  post {
    always { junit allowEmptyResults: true, testResults: 'junit.xml' }
  }
}
```

## Secrets Management

- Use platform secrets: GitHub `secrets.*`, GitLab masked protected variables, Jenkins credentials binding.
- Never put tokens in YAML, build logs, artifacts, or generated `.env` files.
- Grant minimum permissions per job; use `permissions:` in GitHub Actions.
- Prefer OIDC federation to cloud keys when deploying to AWS, GCP, or Azure.
- Scope production secrets to protected branches/environments only.

```yaml
permissions:
  contents: read
  id-token: write

environment: production
```

## Deployment Gates

- PR: lint + tests + build required.
- Main branch: package artifact and deploy staging.
- Production: manual approval, tagged release, or protected environment.
- Post-deploy: health endpoint, synthetic smoke test, and error-rate check.

## Verification Commands

```bash
# GitHub Actions syntax
npx actionlint

# GitLab CI syntax, requires GitLab access token or local runner setup
gitlab-runner exec docker validate

# Jenkinsfile syntax with Jenkins CLI or pipeline linter endpoint
curl -s -X POST -F "jenkinsfile=<Jenkinsfile" https://jenkins.example.com/pipeline-model-converter/validate
```

## Common Pitfalls

- Caching `node_modules` instead of package manager cache; causes stale native binaries.
- Deploying separately rebuilt artifacts per environment; breaks reproducibility.
- Using broad `GITHUB_TOKEN` permissions when read-only is enough.
- Running deployment on pull requests from forks.
- Missing `fail-fast: false` in matrix jobs, hiding platform-specific failures.
- Uploading coverage or build artifacts containing `.env` files.
- Mixing schema migration and app deploy without compatibility plan.

## Done Criteria

- Pipeline uses lockfile-based install.
- Tests run on PRs and default branch.
- Cache keys include lockfiles.
- Secrets use platform storage and least privilege.
- Deploy has approval or protected branch gate.
- Rollback path is documented and verified in non-production.
