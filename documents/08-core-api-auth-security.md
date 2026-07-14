# Part 08 — Core API, Auth & Security

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–07 complete.

## Context
Every module built so far (memory, tasks, router, connectors, email) exists inside Core but isn't reachable from outside it. This part exposes everything as a real API for the two extensions to consume, and locks it down properly — this is also where "enterprise-grade" stops being a description and starts being enforced.

## Objective
A complete REST + WebSocket API surface with device-level auth, OAuth2 connector flows exposed properly, secrets management, and an RBAC scaffold — all consumed through one typed `core-sdk` package (TypeScript, generated from Core's OpenAPI schema) shared by both extensions.

## Requirements

### Functional
- **REST API** covering: tasks (CRUD, complete, plan_day), memory (query, ingest passthrough for manual capture, forget), connectors (list, initiate OAuth, disconnect, status), skills (list, install, enable/disable, permission grant/revoke), notifications (list, dismiss, snooze)
- **WebSocket endpoint**: real-time push for task updates, new notifications, connector status changes — so both extensions stay in sync without polling
- **Device/session auth**: since this is local-first single-user, auth is device-based — first run generates a device keypair or long-lived token, extensions authenticate with it, JWT short-lived access tokens issued per session
- **OAuth2 connector flows**: proper redirect-based flow for Gmail/Outlook/Slack/GitHub, tokens stored via the Part 02 encryption helper, refresh handled transparently
- **`packages/core-sdk`**: fully typed TS client, **generated from Core's OpenAPI schema** (FastAPI produces this automatically from the Pydantic route models — no hand-written or hand-shared types) — this is the *only* way either extension talks to Core

### Non-functional (this is the enterprise section — don't skip it)
- RBAC scaffold: even single-user today, model permissions as roles/scopes now (`owner`, future `viewer`/`collaborator`) so multi-user later is additive, not a rewrite
- Rate limiting per connector and per API consumer (extension) to prevent runaway skill/connector loops from hammering external APIs — via `slowapi` (FastAPI-native, Flask-Limiter-style)
- All secrets (JWT signing key, encryption key, OAuth client secrets) loaded from env/secrets file, never hardcoded, never logged — add a startup check that fails loudly if required secrets are missing
- CORS locked down to only the extension origins (chrome-extension://<id>, vscode-webview://), via FastAPI's `CORSMiddleware`
- Input validation on every endpoint via Pydantic models — the same models double as the OpenAPI schema that generates the TS client, so validation and the client contract can never drift apart

## Deliverables
```
apps/core/app/
├── auth/
│   ├── __init__.py
│   ├── device_auth.py
│   ├── jwt_handler.py            (via python-jose or PyJWT)
│   └── oauth/
│       └── oauth_flow_router.py  (generic, used by every connector)
├── api/
│   ├── tasks_router.py
│   ├── memory_router.py
│   ├── connectors_router.py
│   ├── skills_router.py
│   └── notifications_router.py
├── realtime/
│   └── events_ws.py               (FastAPI native WebSocket endpoint)
├── security/
│   ├── rate_limit.py              (slowapi setup)
│   ├── secrets_check.py           (startup validation)
│   └── cors_config.py
└── main.py                        (FastAPI app assembly, mounts all routers)
packages/types/
├── generate.sh                    (pulls Core's /openapi.json, runs openapi-typescript)
└── generated/                     (openapi-typescript output — regenerated, never hand-edited)
packages/core-sdk/
├── client.ts                      (typed fetch/WS client, thin wrapper importing from packages/types)
docs/decisions/adr-008-auth-model.md
```

## Step-by-step tasks
1. Implement device-based auth: first-run token generation, JWT issuance/refresh, a FastAPI dependency (`Depends(require_auth)`) applied globally via a router-level dependency, with an explicit exemption list for the OAuth callback routes only.
2. Build the generic OAuth2 flow router — parameterized by connector type (path param or config lookup), reused by Gmail/Outlook/Slack/GitHub rather than one router per connector.
3. Build each REST router as a thin layer over the services from Parts 03/04/06/07 — no business logic here, just Pydantic validation + delegation + response shaping. Every request/response uses a Pydantic model (never a raw dict) so it shows up correctly in the OpenAPI schema.
4. Build the WebSocket endpoint (`@app.websocket(...)`): emit events on task changes, new notifications, connector status transitions; both extensions subscribe on connect.
5. Add `slowapi` rate-limiting, scoped per connector type and per API consumer.
6. Add `secrets_check.py` as a startup validator (runs in a FastAPI `lifespan` handler) — process exits with a clear message if any required secret is missing/malformed.
7. Lock down CORS to the real extension origins via `CORSMiddleware` (document how to find the Chrome extension ID for local dev in the README).
8. Wire OpenAPI metadata properly (tags, descriptions, response models on every route) so the generated schema is clean, then build `packages/types/generate.sh`: start Core, curl `/openapi.json`, run `openapi-typescript` against it into `packages/types/generated/`, and have `packages/core-sdk/client.ts` (auth header injection, WS connection helper) import from `packages/types` — both extensions import `core-sdk`, never `types` directly.
9. Write `docs/decisions/adr-008-auth-model.md` explaining the device-auth choice, the RBAC scaffold's future path to multi-user, and the OpenAPI-generation contract (never hand-edit `generated/`, always regenerate).

## Acceptance criteria
- [ ] An unauthenticated request to any non-public endpoint returns 401, not data
- [ ] `packages/core-sdk`'s generated client compiles against the actual API — a deliberately wrong payload fails at compile time, not just runtime; running `generate.sh` twice against an unchanged API produces no diff
- [ ] OAuth flow for at least one connector (Gmail) completes end-to-end through the generic router and stores encrypted tokens
- [ ] WebSocket events fire correctly when a task is completed via REST (subscribe, complete via a different client, confirm event received)
- [ ] Starting Core with a missing `JWT_SECRET` fails fast with a clear error, not a runtime crash on first request
- [ ] Rate limit triggers correctly when a connector is hammered in a test loop

## Out of scope
- Actual extension UIs (Parts 10/11)
- Notification delivery/scheduling logic (Part 09 — this part only exposes the notifications CRUD)
