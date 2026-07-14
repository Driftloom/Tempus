# Part 15 — Multi-Agent Orchestration

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–14 complete.

## Context
The Loop Engine (Part 14) runs one agent at a time. This part adds a Supervisor (the Orchestrator) that decides whether a request needs one specialized subagent, several run in sequence, or several fanned out and merged — and a default roster of four subagents. Each subagent is just an `Agent` (Part 14) with a specific goal template, a restricted toolset, and its own isolated working-memory scope.

## The default roster (yours to extend later via the registry — not a fixed law)

| Agent | Owns | Toolset scope |
|---|---|---|
| **Email Agent** | Multi-step email reasoning beyond Part 07's deterministic pipeline (drafting a reply, handling an ambiguous thread) | Email connector tools, Task creation, Memory ingest |
| **Planning Agent** | Complex scheduling negotiation (Part 04's day planner escalates here when constraints conflict) | Task Engine, Calendar connector, Memory query |
| **Memory Curator Agent** | Reviewing ambiguous/conflicting memories that Part 03's deterministic consolidation couldn't confidently resolve | Memory read/write **only** — cannot touch Email, Task, or Calendar tools |
| **Research Agent** | Open-ended asks ("look into X," "find options for Y") | Web/search connector (when one exists), Memory ingest |

**Forward-compat note**: the delegation contract below is documented as a stable interface specifically so that, much later, ARIA-OS's agents could register into this same roster, or TEMPUS's Orchestrator could itself run as a subagent inside ARIA-OS. Nothing here builds that integration — it just avoids painting into a corner.

## Requirements

### Functional
- **Agent registry** (`registry.py`): config-driven list of available agent types — name, goal template, toolset, budget defaults. Adding a new agent type means adding a config entry + a prompt template, not touching the Orchestrator's code.
- **Orchestrator**: receives a request (user-initiated or event-triggered, e.g. "email digest ready and contains an ambiguous thread"), decides one of: handle directly (no delegation needed), delegate to exactly one subagent, or fan out to multiple subagents concurrently.
- **Delegation contract** (`delegation_schema.py`, Pydantic): `AgentDelegationRequest {agent_type, goal, context_refs, budget}` → subagent runs its own `LoopEngine` instance → `AgentDelegationResult {status, summary, artifacts, memory_refs}`.
- **Context isolation**: each subagent run gets its own working-memory session (a scoped tag within OBSESSION's working layer, keyed by `agent_run_id`) — it sees only what the Orchestrator explicitly hands it (`context_refs`, resolved via `obsession.query()`), never the Orchestrator's full context or another subagent's in-flight state.
- **Result merging**: when multiple subagents ran concurrently, the Orchestrator explicitly reconciles their results before committing anything — if two subagents both propose changes to the same task, the merge step resolves the conflict (e.g., most recent wins, or flag for user confirmation if genuinely contradictory) rather than applying both blindly.

### Non-functional
- A subagent's tool access is enforced by Part 06's permission model at the MCP Host level, not just by convention in its prompt — the Memory Curator Agent must be *incapable* of calling Email tools, not just instructed not to
- Concurrent subagent runs share Core's resources safely — respect the same budget/rate-limit constraints as any other agent run (Part 14's execution control applies per-subagent, and the Orchestrator has its own aggregate budget across a fan-out)

## Deliverables
```
apps/core/app/agents/orchestration/
├── __init__.py
├── orchestrator.py            (decide direct/delegate/fan-out; merge results)
├── registry.py                 (config-driven agent type registry)
├── delegation_schema.py        (AgentDelegationRequest/Result — the stable contract)
├── subagents/
│   ├── email_agent.py
│   ├── planning_agent.py
│   ├── memory_curator_agent.py
│   └── research_agent.py
├── templates/
│   ├── orchestrator-decide-v1.md
│   └── merge-conflict-v1.md
└── router.py
docs/decisions/adr-015-multi-agent-design.md
docs/decisions/adr-015b-future-federation-extension-point.md   (short — the ARIA-OS forward-compat note, not an implementation)
```

## Step-by-step tasks
1. Define `AgentDelegationRequest`/`AgentDelegationResult` as Pydantic models — treat this as a real API contract, version it (`v1`) from day one.
2. Build `registry.py`: loads agent type configs (goal template reference, toolset scope, default budget) — the four subagents above as the initial entries.
3. Build each subagent as a thin `Agent` (Part 14) definition: a goal template + toolset scope reference into the registry. The subagent's "intelligence" is almost entirely in its prompt template and restricted toolset, not bespoke code — resist the urge to special-case logic per subagent in the orchestration layer.
4. Build `Orchestrator.handle(request)`: calls the Router with `orchestrator-decide-v1` to classify the request as direct/single-delegate/fan-out, then either handles it inline, invokes one subagent via `LoopEngine.run()`, or invokes several concurrently (`asyncio.gather`).
5. Implement context isolation: before delegating, the Orchestrator resolves `context_refs` via `obsession.query()` scoped to what's relevant to the goal, and the subagent's `LoopEngine` run tags all its working-memory writes with its own `agent_run_id` — verify a subagent cannot query another's in-flight scope.
6. Implement result merging: for fan-out cases, run everything through `merge-conflict-v1` only when subagent results actually conflict (same resource touched) — don't invoke a merge LLM call for the common case where results are independent.
7. Enforce toolset restrictions at the MCP Host permission-check layer (Part 06), not just by omitting tools from the subagent's prompt — verify with a permission-denial test.
8. Write `docs/decisions/adr-015-multi-agent-design.md` and the short `adr-015b` federation note.

## Acceptance criteria
- [ ] The Orchestrator given a simple single-domain request (e.g., "help me plan tomorrow") delegates to exactly the Planning Agent, not a fan-out
- [ ] Given a genuinely multi-part ambiguous request touching both email and scheduling, the Orchestrator fans out to two subagents and merges without double-creating tasks or memories
- [ ] The Memory Curator Agent's attempt to call an Email tool is denied at the permission layer with a clear error, not silently ignored
- [ ] Two concurrently-running subagents cannot read each other's in-flight working-memory scope (verified directly, not just assumed from code review)
- [ ] Registering a fifth agent type (a test "no-op agent") requires only a registry config entry + template — zero changes to `orchestrator.py`
- [ ] `AgentDelegationRequest`/`Result` schemas are documented well enough that a stranger could understand the contract without reading the Orchestrator's implementation

## Out of scope
- Actual ARIA-OS integration — only the extension point is documented (adr-015b), nothing is wired
- Guardrails enforcement of the *content* an agent produces (vs. tool permission, which this part does enforce) — Part 16
