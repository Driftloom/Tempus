# Part 13 — Testing, CI/CD, Open-Source Packaging & Deployment

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–12 complete — this is the final part that makes the repo genuinely publishable and self-hostable by someone other than you.

## Context
The system works and is hardened. This part is what turns it into something you can actually push to GitHub as a real open-source project and have a stranger clone, run, and trust.

## Objective
A full testing pyramid, real CI/CD (not just the Part 01 skeleton), complete OSS hygiene, and a working self-host deployment path.

## Requirements

### Functional
- **Testing pyramid**: unit tests via `pytest` for every service built in Parts 02–09 (`apps/core`), unit tests via Vitest for the TS packages/extensions where they have real logic (e.g. `core-sdk`'s auth header handling), integration tests (`httpx.AsyncClient` / `pytest` against a test DB via docker-compose) for the FastAPI API layer, e2e tests for critical flows (Playwright for the Chrome extension, VS Code extension test runner for the VS Code extension)
- **CI/CD**: expand Part 01's skeleton into real pipelines — PR pipeline (Python: ruff/mypy/pytest with coverage; TS: lint/typecheck/vitest), release pipeline (on tag: build, package Chrome extension as a zip, package VS Code extension as a `.vsix`, build/push a Docker image for Core, generate changelog)
- **OSS hygiene**: `LICENSE` (Apache-2.0), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue templates (bug report, feature request), PR template, `docs/architecture.md` (a clean version of the master architecture doc for public consumption)
- **Deployment**: a working `docker-compose.prod.yml` for self-hosting Core + Postgres + Redis + Ollama on a VPS, plus documented steps for pointing the browser/VS Code extensions at a remote Core instead of localhost
- **Backup/restore**: scripts for backing up and restoring the Postgres volume (this holds someone's memory layer and task history — losing it is a real loss, document and script this properly)

### Non-functional
- Test coverage thresholds enforced in CI (pick a reasonable floor, e.g. 70% for `apps/core` via `pytest-cov`, and fail CI below it)
- Release pipeline must be reproducible from a clean checkout — no manual steps required beyond pushing a tag

## Deliverables
```
apps/core/test/
├── unit/                    (pytest, mirrors apps/core/app structure)
└── integration/             (pytest, API-level, against docker-composed test DB)
test/
└── e2e/
    ├── chrome/              (Playwright)
    └── vscode/              (VS Code extension test runner)
.github/workflows/
├── ci.yml                   (expanded from Part 01: full test pyramid + coverage gate, both toolchains)
└── release.yml              (tag-triggered: build, package, publish, changelog)
LICENSE
CONTRIBUTING.md
CODE_OF_CONDUCT.md
.github/ISSUE_TEMPLATE/
├── bug_report.md
└── feature_request.md
.github/PULL_REQUEST_TEMPLATE.md
docs/architecture.md
infra/
├── docker-compose.prod.yml
├── backup.sh
└── restore.sh
docs/deployment-guide.md
```

## Step-by-step tasks
1. Write `pytest` unit tests for every service across Parts 02–09 (repositories, classifiers, router policy, task parser/scorer, connector lifecycle, notification scheduler) — target the coverage floor via `pytest-cov`.
2. Write `pytest` integration tests for the full API surface from Part 08 (using `httpx.AsyncClient` against the FastAPI app), run against a docker-composed ephemeral test DB (spun up and torn down per CI run).
3. Write Playwright e2e tests for the Chrome extension's critical flows: quick capture creates a task, memory search returns results, connector status displays correctly.
4. Write VS Code extension e2e tests for: timer start/stop reflected in status bar, TODO CodeLens creates a task.
5. Expand `.github/workflows/ci.yml`: two jobs as established in Part 01 (`python`: ruff/mypy/pytest with coverage gate; `typescript`: eslint/tsc/vitest/build), plus a separate e2e job running Playwright and the VS Code test runner.
6. Write `.github/workflows/release.yml`: triggered on version tag — build all apps, zip the Chrome extension, package the VS Code extension as `.vsix` (via `vsce`), build and push the Core Docker image (multi-stage Dockerfile using `uv` for a lean install), run Changesets for the TS packages' changelog/version bump, and bump `apps/core`'s `pyproject.toml` version via the same tag (a small script or `bump-my-version`) so both sides stay in sync with the release tag.
7. Write `LICENSE` (Apache-2.0), `CONTRIBUTING.md` (dev setup for both toolchains, PR process, coding standards — link back to Part 06's connector/skill authoring guides), `CODE_OF_CONDUCT.md`, issue/PR templates.
8. Write `docs/architecture.md`: a cleaned-up, public-facing version of `00-master-architecture.md` — same diagram, no internal decision-log commentary.
9. Write `infra/docker-compose.prod.yml`: production-shaped compose file (proper restart policies, no dev bind-mounts, environment-driven config) for Core (built from its Dockerfile, running via `uvicorn`/`gunicorn`+`uvicorn` workers) + Postgres + Redis + Ollama + a Celery worker service.
10. Write `infra/backup.sh` / `infra/restore.sh`: `pg_dump`/`pg_restore` wrappers targeting the compose setup, documented in `docs/deployment-guide.md` alongside steps for pointing extensions at a remote Core URL instead of localhost.

## Acceptance criteria
- [ ] `make test` (or the CI equivalent) runs the full pyramid across both toolchains locally and in CI with consistent results
- [ ] CI fails a PR that drops Python coverage below the configured floor
- [ ] Pushing a version tag produces a GitHub release with a Chrome extension zip, a `.vsix`, a built Docker image, and an auto-generated changelog — with zero manual steps
- [ ] A fresh clone, following only `docs/deployment-guide.md`, can stand up a working self-hosted instance on a clean VPS
- [ ] `backup.sh` followed by `restore.sh` against a fresh Postgres instance correctly recovers all tasks and memory items
- [ ] The repo, viewed as a stranger would (README, LICENSE, CONTRIBUTING, architecture docs), reads as a legitimate, trustworthy open-source project

## Out of scope
- Nothing — this is the last part of the first wave. If everything above is checked, the repo is genuinely done for Parts 01–13.

**Forward reference**: once Parts 14–17 exist, extend `.github/workflows/ci.yml` to also run Part 16's `test/guardrails/` suite and Part 17's `evals/` suite (the latter via `.github/workflows/evals.yml`, kept separate since it has its own thresholds and a nightly schedule rather than running on every PR). Nothing here needs to be rebuilt for that — just add the additional CI jobs.
