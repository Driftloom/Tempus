# Part 14 — Agent Runtime & Loop Engine

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–13 complete. This is the start of the "second wave" — see `00-master-architecture.md` section 1.5 for how this fits the overall Harness.

## Context
Everything built so far (Skills in Part 06) is single-shot: one Router call, done. That's correct for well-defined tasks, but genuinely open-ended goals ("figure out how to fit these three conflicting deadlines into my week," "look into this opportunity and tell me if it's worth pursuing") don't have a predetermined next action — they need a real loop: **plan → act → observe → reflect → improve**, repeated until the goal is met or a budget runs out.

This part builds that loop as a generic engine. Part 15 builds the specific subagents that run on top of it.

## Objective
A resumable, budget-bounded Agent Runtime that executes the plan→act→observe→reflect cycle for any registered Agent definition, persists its state so a crash doesn't lose progress, and produces a full step-by-step trace of what it did and why.

## The loop, precisely

1. **Plan**: given the goal, prior steps, and retrieved context, decide the next single action (not a full plan up front — replan every iteration, since observations change what's optimal). A Router/Gateway call against a `agent-plan-v1` template.
2. **Act**: execute that action — call a tool via the MCP Host (a Skill, a connector tool, or a Core service method), **through the Guardrails checkpoint** (Part 16 — stub this call now, wire fully once Part 16 exists).
3. **Observe**: capture the tool's result (success, error, or partial data) and append it to the agent's working-memory session in OBSESSION (this *is* the agent's scratch state — no second memory store).
4. **Reflect**: assess whether the goal is now met. Prefer a deterministic check where one exists (e.g., "task X now has status=completed"); fall back to a Router call (`agent-reflect-v1` template) only when goal-completion genuinely requires judgment.
5. **Improve/Loop**: if not met and budget remains, go back to Plan with the updated state. If met, budget exhausted, or an unrecoverable error occurred, terminate with a structured result.

## Requirements

### Functional
- `Agent` definition: a goal, an allowed toolset (references into MCP Host + Skills, scoped per Part 06's permission model), a budget (`max_steps`, `max_duration_seconds`, `max_cost_usd`), and an optional deterministic completion-check function
- `LoopEngine.run(agent, initial_context) -> AgentRun`: executes the full loop, returns a structured result `{status: completed|budget_exhausted|error|cancelled, summary, artifacts, steps}`
- Every step (plan/act/observe/reflect) persisted to `agent_runs` / `agent_run_steps` tables as it happens — not just at the end — so a run can be **resumed** after a Core restart from its last completed step, not from scratch
- Cancellation: an in-flight run can be cancelled via API; the loop checks a cancellation flag between steps and stops promptly, not mid-tool-call
- Streaming: the API exposes a way to subscribe to a run's steps as they happen (reuse Part 08's WebSocket endpoint), so an extension could show live progress

### Non-functional
- Budget enforcement is hard, not advisory — a run that hits `max_steps` or `max_cost_usd` stops immediately, even mid-goal, and returns a partial result explaining what got done and what didn't
- No silent infinite loops: a hard ceiling (e.g., 25 steps) applies even if the agent's own budget is misconfigured higher
- Every terminate-with-error path produces a human-readable explanation, not just an exception trace

## Deliverables
```
apps/core/app/agents/
├── __init__.py
├── agent_base.py            (Agent definition: goal, toolset, budget, completion check)
├── loop_engine.py            (the plan→act→observe→reflect→improve loop, generic)
├── execution_control.py      (budget enforcement, hard ceiling, cancellation)
├── state/
│   └── agent_state_store.py  (persists agent_runs/agent_run_steps, resumable)
├── templates/
│   ├── agent-plan-v1.md
│   └── agent-reflect-v1.md
└── router.py                 (FastAPI: start run, get status/steps, cancel)
apps/core/app/database/models/agent_runs.py   (new tables — see below)
docs/decisions/adr-014-agent-loop-design.md
```

### New tables (extends Part 02's schema — add via a new Alembic migration, don't touch existing tables)
```sql
agent_runs (id, agent_type, goal, status [running|completed|budget_exhausted|error|cancelled],
            current_step_index, budget_max_steps, budget_max_duration_s, budget_max_cost_usd,
            cost_used_usd, started_at, completed_at, result_summary, error_reason)

agent_run_steps (id, agent_run_id, step_index, step_type [plan|act|observe|reflect],
                 content, tool_called nullable, tool_result nullable, cost_usd, created_at)
```

## Step-by-step tasks
1. Define `agent_runs` / `agent_run_steps` SQLModel classes and generate the Alembic migration.
2. Define `Agent` as a Pydantic/dataclass definition — goal template, allowed tool names, budget, optional `check_complete(state) -> bool`.
3. Implement `LoopEngine.run()`: the core loop described above, persisting each step immediately (not batched) so a crash mid-run loses at most the in-flight step.
4. Implement `execution_control.py`: budget tracking (steps, wall-clock, cumulative cost pulled from Router/Gateway's per-call cost reporting — Part 05), hard ceiling override, cancellation flag check between steps.
5. Implement `agent_state_store.py`: on Core startup, find any `agent_runs` with `status: running` and no recent step — either resume (if the tool call that was in-flight is safely retryable) or mark as `error` with a clear "interrupted, not retryable" reason. Document which tool calls are considered safely resumable vs. not (idempotent ones only).
6. Write the `agent-plan-v1` and `agent-reflect-v1` prompt templates, registered through Part 05's template registry.
7. Wire a stubbed Guardrails checkpoint call in the Act step (`guardrails.check_tool_call(...)` returning `allow` for now) — Part 16 will implement this for real.
8. Build the FastAPI router: `POST /agents/runs` (start), `GET /agents/runs/{id}` (status + steps), `POST /agents/runs/{id}/cancel`, plus a WebSocket subscription for live steps.
9. Write `docs/decisions/adr-014-agent-loop-design.md` covering the replan-every-iteration choice (vs. plan-once-execute-many) and the resumability model.

## Acceptance criteria
- [ ] A test agent with a 3-step goal (e.g., "create a task, verify it exists, mark it high priority") completes correctly within budget
- [ ] Killing the Core process mid-run and restarting resumes from the last persisted step rather than restarting the goal from scratch (for a safely-resumable scenario), or terminates cleanly with a clear reason (for a non-resumable one)
- [ ] An agent whose `max_steps` is exhausted stops immediately with `status: budget_exhausted` and a summary of partial progress — it does not silently continue
- [ ] Cancelling a run via the API stops it within one step boundary, not mid-tool-call
- [ ] Every run's full step trace (plan/act/observe/reflect, in order) is retrievable via `GET /agents/runs/{id}`
- [ ] The hard step ceiling stops a misconfigured agent (`max_steps` set absurdly high) regardless of its own budget setting

## Out of scope
- Specific subagents (Email Agent, Planning Agent, etc.) — Part 15
- Real Guardrails enforcement — Part 16 (stubbed here)
- Delegation between agents — Part 15
