# Part 01 — Monorepo Scaffold & Dev Environment

**Use with:** Claude Code / OpenCode / Codex. Paste this whole file as the task.

## Context
This is the first prompt in the TEMPUS build series (see `00-master-architecture.md` for full system context). Nothing exists yet. This part only builds the skeleton — no business logic.

## Objective
Stand up a production-grade **polyglot** monorepo — Python (FastAPI) for `apps/core`, TypeScript for the two extensions and shared packages — that every later part will build inside, with all tooling configured so an agent (or a human) can run one command on day one and get a working, linted, tested, type-checked baseline on both sides.

## Requirements

### Functional
- pnpm workspaces + Turborepo for the **TypeScript side** (`apps/chrome-extension`, `apps/vscode-extension`, `packages/*`) — build/test/lint/dev orchestration
- `uv` (or Poetry) for the **Python side** (`apps/core`) — its own `pyproject.toml`, virtualenv, dependency lock, independent of the pnpm workspace
- A root `Makefile` (or `justfile`) that wraps both: `make dev` runs the FastAPI dev server (`uvicorn` with reload) and `pnpm turbo dev` for the TS apps concurrently; `make lint`, `make test`, `make build` similarly fan out to both toolchains
- Empty but wired-up apps: `apps/core` (FastAPI, boots with one `/health` route), `apps/chrome-extension` (Vite + React + Manifest V3), `apps/vscode-extension` (VS Code extension scaffold)
- Empty but wired-up TS packages: `packages/types` (will later hold the *generated* OpenAPI types), `packages/core-sdk` (will later hold the *generated* typed client), `packages/ui-kit`
- Root `docker-compose.yml` with Postgres (pgvector-enabled image) and Redis services, wired to `.env`

### Non-functional (enterprise-grade)
- **Python side**: strict typing via `mypy` (or `pyright`), linting/formatting via `ruff`, all enforced in CI and pre-commit
- **TS side**: strict TypeScript everywhere (`strict: true`, `noUncheckedIndexedAccess: true`) — shared `tsconfig.base.json`; ESLint + Prettier with a shared config package
- `pre-commit` (Python) configured for `apps/core`, Husky + lint-staged for the TS side — both wired into the same git hooks so one commit runs both
- Commitlint (Conventional Commits) — this becomes the source for changelogs later
- Changesets configured for versioning the TS packages independently
- GitHub Actions CI skeleton: two parallel jobs — a Python job (install via `uv`, ruff, mypy, pytest) and a TS job (install via pnpm, lint, typecheck, build, test) — both required on every PR
- `.env.example` covering every env var any later part will need (Postgres URL, Redis URL, Ollama host, Anthropic/OpenAI keys, JWT secret, OAuth client IDs/secrets placeholders)
- `README.md` at root with setup instructions that actually work from a clean clone, covering both toolchains

## Deliverables (files/folders)
```
tempus/
├── apps/core/                     (FastAPI app: pyproject.toml, its own venv via uv,
│                                    boots with a single GET /health route via uvicorn)
├── apps/chrome-extension/         (Vite React app, Manifest V3, boots to a blank side panel)
├── apps/vscode-extension/         (yo code scaffold or manual equivalent, one no-op command)
├── packages/types/                (empty, exports one placeholder type — will hold generated
│                                    OpenAPI types from Part 08 onward)
├── packages/core-sdk/             (empty, exports one placeholder typed fetch client — will hold
│                                    the generated client from Part 08 onward)
├── packages/ui-kit/               (empty, exports one placeholder Button component)
├── infra/docker-compose.yml
├── .github/workflows/ci.yml
├── .husky/pre-commit
├── .pre-commit-config.yaml        (Python side: ruff, mypy hooks)
├── turbo.json
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── .eslintrc.cjs (or flat config)
├── Makefile                       (wraps both toolchains: dev/lint/test/build)
├── .env.example
└── README.md
```

## Step-by-step tasks
1. Init pnpm workspace + Turborepo for the TS side, root `package.json` with workspace scripts (`dev`, `build`, `lint`, `test`, `typecheck`) scoped to `apps/chrome-extension`, `apps/vscode-extension`, `packages/*` only.
2. Scaffold `apps/core` as a FastAPI project: `uv init`, add `fastapi`, `uvicorn[standard]` — one router with `GET /health` returning `{"status": "ok"}`, entrypoint via `uvicorn app.main:app --reload`.
3. Scaffold `apps/chrome-extension` with Vite's React-TS template + `manifest.json` (Manifest V3, side_panel permission, no real functionality yet).
4. Scaffold `apps/vscode-extension` with `yo code` equivalent structure — one command `tempus.ping` that shows an info message.
5. Create the three empty TS `packages/*` with `package.json`, `tsconfig.json` extending the base, and a single exported placeholder so imports resolve.
6. Wire TS `packages/*` as workspace dependencies into the two extension apps (core-sdk + types → both extensions; ui-kit → both).
7. Write `infra/docker-compose.yml`: Postgres image `pgvector/pgvector:pg16`, Redis `redis:7-alpine`, both with named volumes and healthchecks.
8. Configure ESLint + Prettier + shared config package `packages/eslint-config` (or inline shared config) for the TS side.
9. Configure `ruff` (lint + format) and `mypy` for `apps/core`, with config in `apps/core/pyproject.toml`.
10. Configure Husky + lint-staged (TS: eslint --fix + prettier) and `pre-commit` (Python: ruff + mypy) as git hooks that both run on commit; configure commitlint (conventional commits) on commit-msg.
11. Add Changesets (`.changeset/config.json`) for TS package versioning.
12. Write the root `Makefile`: `make dev` (uvicorn --reload for core, concurrently with `pnpm turbo dev` for the TS apps), `make lint` / `make test` / `make build` each fanning out to both `ruff`/`pytest` and `pnpm turbo`.
13. Write `.github/workflows/ci.yml` with two jobs: `python` (setup `uv`, install, ruff, mypy, pytest) and `typescript` (setup pnpm, install frozen lockfile, lint, typecheck, build, test) — both required to pass.
14. Write root `.env.example` with every variable listed above, each with a comment explaining what it's for.
15. Write `README.md`: prerequisites (Node/pnpm, Python/uv, Docker), `docker compose up -d`, Python setup (`cd apps/core && uv sync`), TS setup (`pnpm install`), `cp .env.example .env`, `make dev`, how to load the unpacked Chrome extension, how to run the VS Code extension in the Extension Development Host.

## Acceptance criteria
- [ ] `docker compose up -d && make dev` starts `apps/core` via uvicorn and it responds `{"status":"ok"}` on `/health`, while the TS apps boot concurrently
- [ ] `make lint` and `make test` both pass with zero errors from a clean clone (Python: ruff + mypy + pytest; TS: eslint + tsc + vitest)
- [ ] Chrome extension loads unpacked in `chrome://extensions` with no console errors, blank side panel opens
- [ ] VS Code extension launches in Extension Development Host, `tempus.ping` command works
- [ ] A commit with a non-conventional message is rejected by commitlint; a commit with a ruff/mypy violation is rejected by the Python pre-commit hook
- [ ] CI workflow's `python` and `typescript` jobs both pass on a fresh PR

## Out of scope (later parts)
- Any real business logic, database schema, or API routes beyond `/health`
- Auth, connectors, memory, tasks — all later parts
