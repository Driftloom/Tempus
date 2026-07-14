# Part 12 — Observability, Security Hardening & Enterprise Compliance

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–11 complete — this is a hardening pass across the whole system, not a new feature surface.

## Context
Everything functions by this point. This part is what actually makes it "enterprise-grade" rather than just feature-complete: you can see what the system is doing, prove what it did, and trust that a bad skill/connector can't quietly do damage. Given this system reads your email and holds a persistent memory of your personal life, this part isn't optional polish.

## Objective
Full observability (structured logs, metrics, traces), a real security hardening pass on the sandboxing introduced in Part 06, encryption verification across the board, and a documented threat model.

**Forward reference**: if you're building this after Parts 14–17 exist, extend the tracing setup (task 3 below) to include spans for Agent loop steps (Part 14's `agent_run_steps`) and Guardrails decisions (Part 16) as well — same OpenTelemetry instrumentation approach, just more spans in the same trace. If you're building this before Parts 14–17, just build the base observability described here; the second-wave parts already assume it exists and won't require rework.

## Requirements

### Functional
- **Structured logging**: replace any ad-hoc `print()`/default logging across the codebase with a structured logger (`structlog`, or stdlib `logging` + `python-json-logger`), consistent fields (request_id, user_id, module, action), log levels honored via env config
- **Metrics**: `/metrics` endpoint (Prometheus format) via `prometheus-fastapi-instrumentator`, exposing request rates/latencies per endpoint, Router provider usage counts, memory ingestion/query rates, connector health, job queue depth/failure rates
- **Tracing**: OpenTelemetry (`opentelemetry-instrumentation-fastapi` + relevant SQLAlchemy/httpx instrumentation) spans across a request's full path (API → service → Router/DB/connector calls) so a slow request can be diagnosed end-to-end
- **Audit log completeness review**: verify every module that was supposed to write to `audit_log` (Parts 03, 06, 07, 08) actually does, for every mutating action
- **Skill sandbox hardening**: revisit Part 06's subprocess-isolation sandbox — add explicit resource limits (execution timeout via `signal.alarm` or a supervising process, memory cap via `resource.setrlimit`), verify a malicious test skill genuinely cannot access the filesystem, network (beyond declared permissions), or process environment
- **Encryption audit**: verify every credential/token column is actually encrypted at rest (spot-check the raw DB), verify the encryption key itself is never logged or exposed via any API response

### Non-functional
- All of the above should be verifiable by a test, not just "should be true" — write tests for the sandbox escape attempts and the encryption audit specifically
- Produce a written threat model — this is a real deliverable, not a checkbox

## Deliverables
```
apps/core/app/observability/
├── logging/
│   └── structured_logger.py     (global logger config, request-id middleware)
├── metrics/
│   └── metrics.py                (/metrics wiring via prometheus-fastapi-instrumentator)
└── tracing/
    └── otel_setup.py
apps/core/app/mcp_host/skills/
└── sandbox_hardening.py         (resource limits, escape-attempt guards — extends Part 06's runner)
test/security/
├── test_sandbox_escape.py       (attempts filesystem/network/env access from a test 
                                   malicious skill, asserts all blocked)
└── test_encryption_audit.py     (inserts a credential, asserts raw DB value isn't plaintext,
                                   asserts no API response ever includes it)
docs/security/threat-model.md
docs/security/SECURITY.md        (how to report a vulnerability — needed for Part 13's OSS hygiene too)
```

## Step-by-step tasks
1. Replace all logging across every module built in Parts 02–11 with the structured logger; add request-id middleware (FastAPI middleware using `contextvars`) so every log line in a request's lifecycle is correlatable.
2. Wire the `/metrics` endpoint via `prometheus-fastapi-instrumentator`; instrument key paths (API request duration, Router provider selection counts, memory query latency, job queue depth) with custom counters/histograms where the default instrumentation doesn't cover it.
3. Set up OpenTelemetry: instrument the API layer (`opentelemetry-instrumentation-fastapi`), DB calls (`opentelemetry-instrumentation-sqlalchemy`), and Router provider calls (manual spans around `httpx`/SDK calls) with spans; wire a simple local exporter (console or a local Jaeger via docker-compose) for dev visibility.
4. Audit every mutating action across Parts 03/06/07/08 against `audit_log` — write a checklist in `docs/security/audit-coverage.md` mapping action → confirmed logged (yes/no), fix gaps.
5. Harden the skill sandbox: add execution timeout and memory limits to `SkillRunner` (via `resource.setrlimit` and a subprocess timeout), write `test_sandbox_escape.py` with a deliberately malicious test skill attempting filesystem read, outbound network call, and `os.environ` access — assert all three are blocked.
6. Write `test_encryption_audit.py`: insert a connector credential, query the raw DB row directly (bypassing the repository), assert the token value doesn't appear in plaintext; also assert no existing API endpoint response includes a decrypted token.
7. Write `docs/security/threat-model.md`: enumerate the trust boundaries (user's machine ↔ Core, Core ↔ connectors, Core ↔ cloud LLM providers, Core ↔ installed skills), what each boundary is trusted/not trusted to do, and the mitigations already in place (sensitivity routing, sandboxing, encryption, audit logging).
8. Write `docs/security/SECURITY.md`: vulnerability reporting process (even for a personal open-source project, this is expected of anything calling itself enterprise-grade).

## Acceptance criteria
- [ ] Every log line across the system is structured JSON with consistent fields, correlatable by request-id
- [ ] `/metrics` returns valid Prometheus-format output reflecting real traffic
- [ ] A trace for a single API request shows spans across API → service → DB/Router/connector layers
- [ ] `test_sandbox_escape.py` passes — the malicious test skill is fully blocked on all three attempted escapes
- [ ] `test_encryption_audit.py` passes — no plaintext credential in raw DB row, no token in any API response
- [ ] `docs/security/audit-coverage.md` shows 100% of identified mutating actions confirmed logged (or explicitly justified exceptions)
- [ ] `docs/security/threat-model.md` and `SECURITY.md` exist and are complete

## Out of scope
- New functional features — this part touches only observability/security across existing code
