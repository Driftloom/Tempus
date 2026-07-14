# Part 05 — Hybrid LLM Router & AI Gateway

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–04 complete (they stub this interface; this part implements it for real and rewires the stubs).

**Note on scope**: this part was originally "just" a routing policy. It's now upgraded to a full **AI Gateway** — provider abstraction, caching, and inference economics — built as a **hybrid**: [LiteLLM](https://github.com/BerriAI/litellm) (OSS, Python-native) handles the undifferentiated heavy lifting (normalizing calls across providers, retries, cost-tracking primitives, caching hooks), and TEMPUS's own sensitivity-routing policy, audit logging, and template registry sit on top as an in-house policy layer. You get the boring infrastructure for free and keep the differentiated logic as your own.

## Context
Every module so far (OBSESSION's classifiers, the task engine's NL parsing and day planner) calls a Router interface that's been stubbed. This part builds the real thing: a **Gateway** that centralizes model access (auth, routing, rate limits, caching, logging, provider abstraction — via LiteLLM) with a **sensitivity-and-complexity routing policy** on top that decides, per request, whether to run locally (Ollama) or in the cloud (Claude/GPT). Same fallback-chain instinct as your SafeVixAI 9-provider chain, now generalized into infrastructure instead of hand-rolled per-provider code.

## Objective
A single `Router` service with one method — `route(request)` — that every other module calls instead of ever touching a model provider or LiteLLM directly. Underneath, it's a thin policy layer over a LiteLLM-backed Gateway that adds caching and cost/budget enforcement.

## Requirements

### Functional
- Providers supported: **Ollama** (local, e.g. Mistral 7B) and at least one cloud provider (**Anthropic Claude**), accessed **through LiteLLM's unified interface** rather than hand-rolled per-provider adapters — adding OpenAI/Gemini later is a LiteLLM config entry, not new code
- Routing policy (in order of precedence):
  1. If request declares `sensitivity: "high"` → **local only**, never cloud, regardless of complexity
  2. If request declares `sensitivity: "medium"` → local by default, cloud only if `forceCloud: true` is explicitly passed by the caller with justification logged
  3. If `sensitivity: "low"` and `complexity: "high"` (multi-step reasoning, planning, synthesis) → cloud preferred, local fallback if cloud unavailable
  4. If `sensitivity: "low"` and `complexity: "low"` → local preferred (cheaper, faster, no network dependency)
- Fallback chain: if the preferred provider fails (timeout, error, rate limit), fall back per policy — cloud failure falls back to local always; local failure for a low-sensitivity request may fall back to cloud. LiteLLM's own retry/fallback config handles transient failures within a provider; TEMPUS's policy layer handles the cross-provider (local↔cloud) fallback on top.
- Unified request/response schema across providers (`ChatMessage[]` in, structured `{content, provider, model, latencyMs, tokensUsed, costUsd, cacheHit}` out) so callers never branch on provider
- Prompt template registry: named, versioned templates (e.g. `day-planner-v1`, `email-triage-v1`) rather than inline prompt strings scattered across modules
- **Response caching**: exact-match cache (hash of resolved prompt + params) for idempotent, repeated calls (e.g., re-classifying near-identical emails); optional semantic cache (embedding-similarity lookup, reusing OBSESSION's embedding service from Part 03) for near-duplicate queries where exact match won't hit
- **Prompt caching**: for providers that support it (Anthropic prompt caching on long, repeated system prompts/templates), enable it by default on any template over a size threshold — meaningful cost/latency win with no behavior change
- **Inference economics**: per-request cost tracked (via LiteLLM's cost-tracking callbacks), aggregated per day/provider/template; a configurable daily/monthly cost budget per provider — when a cloud budget is exceeded, the policy layer forces local-only until reset or an explicit override, rather than silently continuing to spend

### Non-functional
- Every routing decision is logged (provider chosen, sensitivity, complexity, reason, cache hit/miss, cost) — this becomes an audit trail and a place to tune the policy later
- Cost/latency tracked per request, aggregable into a usage dashboard (surfaced later, this part just needs the data captured correctly)
- Local provider (Ollama) failure should never crash a caller — always resolve to a usable response or a clearly-typed error, never an unhandled rejection
- Budget circuit breaker is a hard stop, not advisory — exceeding a configured cloud budget must actually prevent further cloud calls, not just log a warning

## Deliverables
```
apps/core/app/router/
├── __init__.py
├── service.py                    (the route() entrypoint — the ONLY thing other modules call)
├── policy/
│   └── routing_policy.py         (the precedence rules above, as a pure function)
├── gateway/
│   ├── litellm_client.py         (LiteLLM setup: model configs for Ollama + Anthropic,
│   │                               retry/fallback config, cost-tracking callback registration)
│   └── provider_config.py        (model name mappings, endpoints, per-provider settings)
├── caching/
│   ├── exact_match_cache.py      (hash-based cache, Redis-backed)
│   └── semantic_cache.py         (embedding-similarity cache, reuses Part 03's embedding service)
├── economics/
│   ├── cost_tracker.py           (per-request cost capture + aggregation)
│   └── budget_enforcer.py        (daily/monthly caps, hard circuit breaker)
├── templates/
│   ├── template_registry.py
│   └── prompts/                  (versioned .md or .txt prompt template files)
└── router.py                     (internal debug endpoint: test a route decision, view cost dashboard data)
docs/decisions/adr-005-routing-policy.md
docs/decisions/adr-005b-gateway-hybrid-approach.md
```

## Step-by-step tasks
1. Define `ChatRequest {messages, sensitivity, complexity, template_id?, force_cloud?}` and `ChatResponse {content, provider, model, latency_ms, tokens_used, cost_usd, cache_hit, reasoning}` as Pydantic models in `apps/core/app/router/schemas.py`.
2. Set up LiteLLM (`litellm_client.py`): configure the Ollama and Anthropic models as LiteLLM model entries, enable its built-in retry/fallback config for transient failures, register a cost-tracking callback so every call's cost is captured automatically.
3. Implement `routing_policy.py` as a pure, unit-testable function: `route_decision(request) -> (provider, reason)` — no side effects, easy to test every branch of the precedence table with pytest. This stays entirely TEMPUS-owned logic, calling into LiteLLM only for the actual model invocation.
4. Implement the caching layer: `exact_match_cache.py` checks a Redis-backed hash of the resolved prompt+params before calling LiteLLM at all; `semantic_cache.py` (used selectively — not every call needs this overhead) checks embedding similarity against recent cached responses for the same template.
5. Implement `cost_tracker.py` and `budget_enforcer.py`: aggregate LiteLLM's per-call cost data by day/provider/template; `budget_enforcer` checks against configured caps before allowing a cloud call, forcing local-only and logging clearly when a budget is exceeded.
6. Implement `RouterService.route()` (async): check exact-match cache → check semantic cache if applicable → apply routing policy → call LiteLLM (which internally handles retries) → apply TEMPUS's cross-provider fallback if LiteLLM's own retries exhaust → track cost/log decision → cache the response → return.
7. Build the template registry: load versioned prompt templates from `templates/prompts/`, support variable interpolation (Jinja2 or simple `.format()`), require every caller to reference a `template_id` rather than inline strings (rewire Part 03's classifiers and Part 04's parser/planner to use this), and flag templates over a size threshold for Anthropic prompt caching.
8. Add structured logging for every route decision (provider, sensitivity, complexity, latency, tokens, cost, cache hit/miss, fallback triggered y/n).
9. Write `docs/decisions/adr-005-routing-policy.md` (the precedence table and why high-sensitivity never touches cloud) and `docs/decisions/adr-005b-gateway-hybrid-approach.md` (why LiteLLM underneath + in-house policy on top, not one or the other).

## Acceptance criteria
- [ ] A request with `sensitivity: "high"` never calls the Anthropic provider, even if forced — verify with a test that asserts the cloud provider mock was never invoked
- [ ] A `sensitivity: low, complexity: high` request prefers cloud, and correctly falls back to local if the cloud call is mocked to fail
- [ ] Two identical low-sensitivity requests in a row hit the exact-match cache on the second call — verify via a cache-hit flag in the response and that LiteLLM was only actually invoked once
- [ ] Exceeding a configured daily cloud budget (test with a low limit) forces subsequent requests to local-only and logs the reason clearly — verify no further cloud spend occurs past the cap
- [ ] Every route decision produces a log entry with provider + reason + cost + cache status
- [ ] OBSESSION's sensitivity classifier and the task engine's day planner both go through this Router with no direct provider or LiteLLM calls remaining anywhere else in the codebase (grep for provider SDK / litellm imports outside `router/`)
- [ ] Swapping in a third provider (e.g. OpenAI) requires only a LiteLLM config addition, no changes to `RouterService` or the policy function

## Out of scope
- MCP tool-calling within the router (Part 06 wires MCP tools into requests)
- Guardrails-level PII redaction and injection defense (Part 16 builds this as a pre-processing step this Router calls into once it exists)
- A user-facing cost/usage dashboard UI (the data is captured here; surfacing it is a later, optional addition)
