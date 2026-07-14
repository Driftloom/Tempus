# TEMPUS: A Personal Intelligence Layer
### Concept Paper

**Status**: Concept / pre-build · **Author**: Rohit · **Companion**: `tempus-prompts/` (18-part build series) · **Related**: ARIA-OS (future federation target)

---

## Abstract

TEMPUS is an open-source, enterprise-grade personal intelligence layer that manages a person's time, tasks, and communications continuously, remembers everything relevant about their life and work in a structured layered memory, and acts on their behalf through a governed multi-agent system — all surfaced inside the two places a technical person actually lives: the browser and the editor. It is not a chatbot with a to-do list bolted on. It is a standing system: always ingesting (email, browser context, code context), always remembering (OBSESSION, its four-layer memory engine), and increasingly capable of acting (Skills for deterministic work, Agents for open-ended work), all inside a Harness that makes the acting part safe — guardrails, evals, audit, and human-in-the-loop escalation are not an afterthought bolted onto a working prototype, they are load-bearing from the first line of code.

This paper is the idea in full. The companion `tempus-prompts/` series is the idea broken into 18 buildable, sequential engineering prompts. Read this first if you want the *why*; read those if you want the *how*.

---

## 1. The Problem

Personal productivity tools today fall into two failure modes:

1. **Dumb but safe** — a to-do list, a calendar, a notes app. You do all the work of noticing what matters, deciding what's a task, and updating the system. The tool has no memory of *you* beyond what you typed into it verbatim, and it never acts.
2. **Smart but shallow** — an AI wrapper around a chat interface. It has no persistent memory across sessions worth trusting, no real access to your inbox or calendar beyond a plugin call, and if it *did* act on your behalf, you'd have no way to audit what it did or stop it from doing something wrong.

Nobody has built the thing in between: a system with a genuine, structured, persistent memory of your actual life and work — not a rolling chat log — that reads the sources where your obligations actually originate (email, calendar, code), decides what needs your attention, and is *trustworthy enough* to occasionally act without you, because the guardrails around it are as seriously engineered as the intelligence itself.

## 2. The Vision

TEMPUS is a personal intelligence layer, not an app. Concretely, that means:

- **It doesn't wait to be asked.** It reads your inbox, notices your deadlines, tracks your time, and proposes your day — you review and confirm rather than compose from scratch.
- **It remembers like a person would, not like a database would.** Working memory for what you're doing right now, episodic memory for what happened, semantic memory for stable facts and preferences, procedural memory for how you like things done — four layers, not one flat table of embeddings.
- **It's extensible by design, not by exception.** Every data source is a connector, every capability is a skill or agent, all speaking a standard protocol (MCP) — adding a new integration is a contribution, not a fork.
- **It's careful in proportion to its access.** The more autonomy a piece of the system has, the more scrutiny it operates under — a rule-based classifier gets a unit test, an agent that can act on your email gets an injection-defense test, a policy engine, and an audit trail.
- **It lives where you work.** Not a new tab you have to remember to open — a Chrome side panel and a VS Code panel, both thin clients over one shared backend brain.
- **It's yours.** Self-hosted, open-source, local-first. Your email and your memory of your own life are not a subscription.

## 3. Core Design Philosophy

Three principles run through every architectural decision in this project:

**Memory before intelligence.** A smarter model with no memory of you is still a stranger every session. A well-organized memory of your actual life, paired with a merely competent model, outperforms a brilliant model with amnesia. OBSESSION (Section 5.1) is the foundation everything else is built on, not a feature added later.

**The model is the least interesting part.** The reliability, safety, and actual usefulness of an agentic system live in what Anthropic calls the *harness* — planner, memory, state, tools, guardrails, evals, execution control — not in which model you point at it. TEMPUS is architected explicitly around this: Section 5 below is really a description of the Harness, with the model (local Ollama or cloud Claude, chosen per-request) as a replaceable component inside it.

**Autonomy is earned per action, not granted per system.** TEMPUS doesn't have a single trust level. A Skill that classifies an email's urgency runs unsupervised, because being wrong is cheap and recoverable. An Agent that's about to send a reply on your behalf, or delete a memory, or act on an instruction embedded inside an email, does not — it either can't do that action at all (permission model), or it pauses and asks (human-in-the-loop escalation). The system's default posture toward anything irreversible is to ask first.

## 4. Who This Is For

Built for one person first — you — but designed as if it will be read, forked, and extended by strangers, because that's the only way "enterprise-grade open source" means anything rather than being a description you put on a solo project. Every subsystem below has an authoring guide, a permission boundary, and a test suite specifically because a stranger has to be able to trust and extend it without reading your mind.

## 5. System Architecture

### 5.1 OBSESSION — the memory engine

Four layers, not one:

| Layer | Holds | Lifespan |
|---|---|---|
| Working | Current session/task context | Minutes–hours, TTL-based |
| Episodic | Timestamped events — things that happened | Long, decays if never re-referenced |
| Semantic | Stable facts and preferences about you | Persistent until explicitly changed |
| Procedural | Learned patterns in *how* you like things done | Persistent, reinforced by repetition |

Every piece of content that enters OBSESSION is classified into a layer, scored for importance, tagged with a sensitivity level (low/medium/high — this tag is what later decides whether an LLM call touching this content can go to the cloud at all), and embedded for retrieval. A nightly consolidation job merges duplicate memories, promotes repeatedly-referenced episodic memories into semantic ones, and decays what's gone stale — without this, a memory system just becomes a landfill. Retrieval is hybrid: vector similarity blended with recency and importance, not pure nearest-neighbor search. Everything is forgettable — a real delete API, because this system holds your email content and personal facts, and hygiene here isn't optional.

### 5.2 Task & Time Engine

Parses natural language into structured, timezone-correct tasks; tracks time against them; proposes (never auto-commits) a day plan by weighing due dates, explicit priority, and — via OBSESSION's procedural memory — your actual historical patterns of what you deprioritize. Every task lifecycle event (created, completed, missed) writes back into OBSESSION as an episodic memory, so the system's model of you updates from what you actually do, not just what you say.

### 5.3 Router & AI Gateway — the hybrid brain

One entry point (`route()`) for every model call in the system. Underneath, a hybrid build: LiteLLM handles provider abstraction, retries, and cost-tracking primitives across local (Ollama) and cloud (Claude) models; TEMPUS's own policy layer sits on top and makes the decision that actually matters — sensitivity-based routing. Health, financial, and personal content never leaves the machine, regardless of how well cloud reasoning would handle it; low-sensitivity, high-complexity reasoning goes to the cloud because that's what it's good at. Response caching and Anthropic prompt caching cut redundant spend; a hard budget circuit breaker prevents a misbehaving loop from silently running up a bill.

### 5.4 MCP Host — connectors, skills, plugins

Everything external is an MCP connector (Gmail, Calendar, Slack, GitHub — each swappable, each independently authored). Everything TEMPUS can *do* is either a **Skill** (deterministic, single-shot, cheap, easy to test and eval — "classify this," "extract that") or an **Agent** (Section 5.5 — open-ended, multi-step, genuinely needs a loop). Both share one permission model: nothing is auto-granted, every capability declares what it needs, and a stranger extending the system with a new connector or skill follows a documented authoring guide rather than reverse-engineering the core.

### 5.5 Agent Runtime & Multi-Agent Orchestration

The loop that makes "open-ended" possible: **plan → act → observe → reflect → improve**, re-planned every iteration rather than committed up front, because the right next step depends on what the last one revealed. Every step is persisted as it happens — an agent's progress survives a restart — and bounded by a hard budget (steps, time, cost) that is enforced, not advisory.

Above the single-agent loop sits a Supervisor that decides whether a request needs no delegation, one specialized subagent, or several run concurrently and merged. The initial roster — Email Agent, Planning Agent, Memory Curator Agent, Research Agent — is deliberately narrow in scope per agent (a Memory Curator Agent is architecturally *incapable* of calling an email tool, not just instructed not to) and deliberately documented as an extensible registry, because the honest long-term plan is that this Supervisor, or its subagents, eventually federate with ARIA-OS's own multi-agent system. Nothing about that federation is built yet. Nothing about this design blocks it either.

### 5.6 Guardrails

The part that makes reading your email and acting on it survivable. Every piece of content carries a provenance tag from the moment it's ingested — direct from you, recalled from memory, or externally sourced and untrusted (email, web). Untrusted content can be *observed* by an agent but can never by itself authorize a tool call; an action whose only justification traces back to an instruction embedded in an email is flagged and escalated to you, not executed. PII redaction runs as defense-in-depth even on content already classified low-sensitivity, in case the classifier was wrong. Every tool call passes a runtime authorization checkpoint — re-validated at call time, not just granted once at install time — against both the permission model and a small declarative policy engine (no autonomous external communication, caps on autonomous actions per day, confirmation required for anything irreversible). Every guardrail decision — allow, deny, or escalate — is audit-logged with the specific rule that fired.

### 5.7 Evals

The discipline that keeps the rest of this honest. Golden datasets for the things that can silently regress: memory classification accuracy, task-parsing accuracy, agent goal-completion (scored by a pinned LLM judge, since exact-match isn't meaningful for open-ended success), and — critically — guardrail effectiveness, measured on *both* axes: catch rate on real injection patterns and false-positive rate on legitimate actions, reported separately, because optimizing one at the other's expense is a regression dressed up as a win. Wired into CI as a regression gate, and fed continuously by your own real corrections — a mis-parsed task you fix, a memory you dismiss — reviewed before being folded into the permanent dataset, not auto-ingested.

### 5.8 Observability

Structured logs, Prometheus metrics, and OpenTelemetry traces across the full request path — API through service through model call through tool call — extended to cover agent loop steps and guardrail decisions specifically, because "the agent did something wrong three steps into a five-step run" is undiagnosable without a trace of all five steps.

### 5.9 Surfaces — Chrome and VS Code

Both are thin, sharing one typed client generated directly from the backend's API contract, so the two never drift apart. Chrome: a side panel for the day's tasks, quick capture, memory search, and page-context saving. VS Code: a status bar timer, TODO-comment-to-task conversion, and the same core views in a webview — because a meaningful share of what a task/time system needs to track for a developer originates in the editor, not the browser.

## 6. A Day, Concretely

Morning: TEMPUS has already synced overnight email, flagged three action items (a deadline, a meeting request, a document review), and created tasks for two of them — the third was ambiguous enough that the Email Agent escalated it for a one-line confirmation rather than guessing. The Planning Agent proposes a day plan around your existing calendar and your known preference (learned, not configured) for deep work before noon; you adjust one block and confirm. Mid-morning, you highlight a paragraph on a webpage and save it to memory via the Chrome extension — it's tagged, embedded, and available to the assistant the next time it's relevant, without you filing it anywhere. In the editor, a `// TODO: revisit this before the internship deadline` becomes a tracked task with one click, linked back to the exact file and line. That evening, the daily digest summarizes what came in, what got auto-actioned, and what's still waiting on you — and nothing in that digest is something the system did without a permission it was actually granted.

## 7. What Makes This Different

Not a to-do list with an AI feature — the memory and the action loop are the product, the task list is a side effect. Not a ChatGPT-with-memory wrapper — the memory is structured and layered, not a similarity search over raw chat history, and the model is a swappable, sensitivity-routed component rather than the whole system. Not a SaaS inbox tool — self-hosted, and the thing reading your email never has to leave your machine unless a specific piece of low-sensitivity reasoning genuinely benefits from it. Not "trust the agent" — the guardrails, evals, and audit trail are sized to the system's autonomy, built at the same time as the autonomy, not after an incident.

## 8. Roadmap

**Phase 1 — Foundation** (`tempus-prompts/01–13`): monorepo, database, OBSESSION, task/time engine, hybrid Router, MCP connector/skill framework, email intelligence, core API, notifications, both extensions, observability/security hardening, testing/CI/deployment. A working, single-agent, deterministic-skills system, self-hostable end to end.

**Phase 2 — Agentic Harness** (`tempus-prompts/14–17`): the Loop Engine, multi-agent orchestration, the full Guardrails layer, and the Evals framework. This is what turns TEMPUS from "a well-built assistant app" into a governed agentic system capable of open-ended, multi-step, semi-autonomous work.

**Phase 3 — Federation (not yet built, deliberately not blocked)**: TEMPUS's Supervisor and ARIA-OS's agent system as peers — either registering into each other's agent registries, or one subsuming the other, decided later with real usage data from both systems rather than upfront. The delegation contract built in Phase 2 exists specifically so this is a connector-level integration when it happens, not a rewrite.

## 9. Open Questions Worth Revisiting

- Whether the four-subagent roster is the right decomposition once real usage reveals what actually needs delegating versus what a single agent handles fine.
- Whether semantic response caching earns its complexity cost at actual usage volume, or whether exact-match caching alone is sufficient.
- Whether pgvector remains sufficient at scale, or a dedicated vector store becomes worth the operational overhead.
- The real shape of ARIA-OS federation — peer, parent, or subsumption — which is a question best answered after both systems have real mileage on them, not before.

## 10. Closing

TEMPUS's bet is that the boring, careful infrastructure — a real layered memory, a governed permission model, guardrails that assume the inbox is adversarial, evals that catch regressions before you do — is what actually differentiates a personal intelligence system from a demo. The model is rented. The harness is built. This paper is the shape of that harness; the eighteen files beside it are how it gets built.
