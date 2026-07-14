# Part 03 — Memory Engine ("OBSESSION")

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–02 complete.

## Context
This is the system's core differentiator: a memory layer that's actually layered, not a flat log of everything ever said. Every other subsystem (tasks, email, connectors, both extensions) reads from and writes to this. Get the retrieval quality right — a memory system nobody trusts to surface the right thing is worse than no memory system.

## Objective
Build OBSESSION: an ingestion → classification → embedding → storage → consolidation → retrieval pipeline with four memory layers, exposed as a clean internal API other modules call.

## The four layers (this is the actual design)

| Layer | What it holds | Lifespan | Example |
|---|---|---|---|
| **Working** | Current session/context | TTL, minutes–hours | "User is currently looking at the Q3 report tab" |
| **Episodic** | Timestamped events — things that *happened* | Long, but decays if never re-referenced | "Had a call with Priya about the internship deadline on July 3" |
| **Semantic** | Facts, preferences, stable knowledge about the user | Persistent until explicitly changed | "User prefers deep work blocks in the morning"; "User is applying to Microsoft SWE internship" |
| **Procedural** | Learned patterns about *how* the user likes things done | Persistent, reinforced by repetition | "When user says 'draft it', they want a Slack-ready message, not an email" |

## Requirements

### Functional
- Ingestion API: any module can call `obsession.ingest({content, source, sourceRef, userId})` — classification (layer, importance, sensitivity) happens inside, caller doesn't decide the layer
- Retrieval API: `obsession.query({query, userId, filters, limit})` — hybrid ranking: vector similarity + recency decay + importance score + explicit tag match
- Consolidation job (scheduled, via Celery beat or `arq` cron): merges near-duplicate semantic memories, promotes repeatedly-referenced episodic memories toward semantic, decays/archives stale working & low-importance episodic memories
- Explicit forget API: `obsession.forget({memoryId})` and `obsession.forgetByFilter({...})` — hard delete, also removes embedding and edges, writes to audit_log
- Memory edges: when two memories are related (same task, same person, causally linked), create a `memory_edges` row — enables "show me everything connected to X" traversal, not just similarity search

### Non-functional
- Every ingested item gets a **sensitivity** tag (`low|medium|high`) at classification time — this tag is what Part 05's LLM router will use to decide local-vs-cloud. Get this classification step built with a clear, overridable ruleset (keyword/PII heuristics + local LLM classification), not just a cloud call
- Retrieval must be fast enough for interactive use (<300ms p95 for a query against a few thousand memories) — index appropriately (ivfflat or hnsw on the vector column)
- Idempotent ingestion — ingesting the same source content twice should update, not duplicate (dedupe on source+sourceRef+content hash)

## Deliverables
```
apps/core/app/obsession/
├── __init__.py
├── service.py                    (ingest, query, forget — the public API)
├── classification/
│   ├── layer_classifier.py       (decides working/episodic/semantic/procedural)
│   ├── sensitivity_classifier.py (low/medium/high — local model or ruleset)
│   └── importance_scorer.py
├── embedding/
│   └── embedding_service.py      (wraps local or cloud embedding model, cached)
├── retrieval/
│   └── hybrid_ranker.py          (vector + recency + importance + tags)
├── consolidation/
│   └── consolidation_job.py      (Celery task / arq cron function, scheduled nightly)
└── router.py                     (internal-only FastAPI router for debugging/testing)
docs/decisions/adr-003-memory-layers.md
```

## Step-by-step tasks
1. Write the layer classifier: rule-based first pass (source type strongly implies layer — e.g. email → episodic, explicit "remember that I prefer X" → semantic), with an LLM fallback for ambiguous content via the Router (built in Part 05 — stub it with a simple interface now, wire it properly once Part 05 exists).
2. Write the sensitivity classifier: keyword/entity ruleset (health terms, financial terms, family names) as a fast first pass, escalate to local LLM only when ambiguous.
3. Write the embedding service — abstracted behind an interface so swapping providers later doesn't ripple through the codebase.
4. Implement `ingest()`: classify → embed → dedupe check → write to `memory_items` → create edges to any explicitly referenced tasks/memories.
5. Implement `query()`: embed the query, vector search top-N, re-rank by `similarity * w1 + recency_decay * w2 + importance * w3`, apply any explicit filters (layer, tags, date range).
6. Implement the consolidation job: find near-duplicate semantic memories (cosine similarity above threshold) and merge; find episodic memories referenced 3+ times in the last 30 days and promote to semantic; archive (soft-delete) working memories past TTL and low-importance episodic memories past a configurable age.
7. Implement `forget()` and `forgetByFilter()` with audit logging.
8. Write `docs/decisions/adr-003-memory-layers.md` documenting the layer definitions and promotion/decay rules so future-you doesn't relitigate this.

## Acceptance criteria
- [ ] Ingesting the same content twice (same source+ref) updates in place, doesn't duplicate
- [ ] A query for "internship deadline" returns the relevant semantic + episodic memories ranked above irrelevant but textually-similar noise
- [ ] Sensitivity classification correctly flags a sample of health/financial content as `high` and generic scheduling content as `low`
- [ ] Consolidation job merges two near-duplicate memories into one without losing the more detailed content
- [ ] `forget()` fully removes the memory, its embedding, and its edges, and leaves an audit_log entry
- [ ] p95 query latency under 300ms against a seeded set of 2,000+ memory items

## Out of scope
- The LLM router itself (Part 05) — stub its interface here
- Exposing this via public API to extensions (Part 08)
