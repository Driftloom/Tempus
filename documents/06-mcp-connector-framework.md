# Part 06 — Connector / Plugin / Skill Framework (MCP Host)

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–05 complete.

## Context
This is the extensibility backbone you asked for: "connectors, plugins, skills, etc." Building it on **MCP (Model Context Protocol)** rather than a custom plugin system means every connector doubles as a standard MCP server usable outside TEMPUS too, and it's the same protocol you're already certified on.

## Three extension types (definitions — use these consistently everywhere)

- **Connector**: wraps an external data source/service (Gmail, Google Calendar, Slack, GitHub, Notion) as an MCP server. Exposes tools (`list_emails`, `create_event`) and resources (a mailbox, a calendar).
- **Skill**: a composable capability built from Router calls + tool calls (e.g. "plan-my-day", "email-triage", "weekly-review"). A skill is prompt + orchestration logic, not a raw data source.
- **Plugin**: a UI/behavior extension inside the Chrome or VS Code extension itself (e.g. a custom side-panel widget). Plugins are consumers of the Core API, not part of the MCP host.

TEMPUS Core is the **MCP Host**: it holds MCP client connections to every enabled connector, and Skills call through the host to use them.

**Forward reference**: Parts 14–15 add Agents (loop-based, multi-step) as a second consumer of this same MCP Host and permission model — an Agent's toolset is scoped exactly the same way a Skill's is. Part 16 later adds a *runtime* authorization checkpoint on top of the install-time grant built here (re-validating at call-time, not just at grant-time) — this part still needs to build the grant/check/revoke primitives correctly, since Part 16 depends on them rather than replacing them.

## Requirements

### Functional
- MCP host manages lifecycle of connector server processes (start, health-check, restart on crash, stop on disable)
- Skill manifest format (`skill.json`): name, version, description, required permissions (`read_memory`, `write_memory`, `read_tasks`, `write_tasks`, connector access list), entrypoint
- Permission model: a skill declares required permissions in its manifest; nothing is auto-granted — first use requires explicit user approval (persisted in `plugin_permissions`), and any permission escalation (new version requesting more) requires re-approval
- Local skill registry: install a skill from a local path or a git URL, validate its manifest, register it, list installed skills, enable/disable, uninstall
- Skill execution sandboxing: skills run in a restricted context (no arbitrary filesystem/network access beyond what's declared). **Note on the language switch**: Node had `vm`/worker-threads with restricted globals as an easy in-process sandbox; Python doesn't have an equivalent that's actually safe (`exec()` with a restricted namespace is not a real security boundary). Build v1 sandboxing as **subprocess isolation** instead — each skill run spawns as a separate OS process via `multiprocessing` or `subprocess`, with resource limits set via the `resource` module (CPU time, memory) and a restricted environment (no inherited env vars beyond an explicit allowlist, no filesystem access outside a scoped temp dir). Document in Part 12 that container-based isolation (Docker-in-Docker or gVisor/nsjail) is the recommended upgrade path if skills ever run untrusted third-party code

### Non-functional
- Every connector/skill action that touches memory, tasks, or external data is written to `audit_log` (actor = skill/connector id, action, resource)
- A misbehaving connector (crashes, hangs) must not take down Core — isolate failures, surface connector `status: error` in the UI-facing API

## Deliverables
```
apps/core/app/mcp_host/
├── __init__.py
├── service.py                 (manages MCP client connections to connectors, via the
│                                official `mcp` Python SDK)
├── connector_lifecycle.py     (start/stop/health-check/restart)
├── permissions/
│   └── permission_service.py  (grant/revoke/check against plugin_permissions)
├── skills/
│   ├── skill_registry.py      (install/list/enable/disable/uninstall)
│   ├── skill_runner.py        (subprocess-isolated execution)
│   └── skill_manifest.py      (Pydantic schema for skill.json)
└── router.py
connectors/
└── _template/                   (a scaffold connector: manifest + one no-op tool, 
                                   used as the starting point for Part 07's real connectors)
skills/
└── _template/                   (a scaffold skill: manifest + one no-op run(), 
                                   used as the starting point for real skills)
docs/connector-authoring-guide.md
docs/skill-authoring-guide.md
```

## Step-by-step tasks
1. Define `skill.json` and connector manifest as Pydantic models — version, name, description, permissions, entrypoint.
2. Build `McpHostService`: given a connector config, spawn/connect its MCP server via the official `mcp` Python SDK's client, expose its tools/resources to the rest of Core through a typed interface.
3. Build connector lifecycle management: health-checks on an interval (via an `asyncio` background task), auto-restart with backoff on crash, mark `status: error` after repeated failures, surface via `connectors` table (Part 02).
4. Build `PermissionService`: `check_permission(skill_id, permission)`, `request_permission(...)` (returns pending, requires explicit user grant via API — stub the actual UI approval flow, Part 08/10/11 will surface it), `revoke_permission(...)`.
5. Build `SkillRegistry`: install from local path (copy + validate manifest + register in `skills_registry` table), install from git URL (clone + same validation), list/enable/disable/uninstall.
6. Build `SkillRunner`: executes a skill's entrypoint as an isolated subprocess (via `multiprocessing.Process` or `subprocess.run` against a small runner script), passing in only the permitted capabilities (a scoped memory client, scoped task client, scoped connector tool access) via a serialized context — enforce CPU/memory limits with the `resource` module and a scrubbed environment.
7. Every skill/connector action funnels through a wrapper that writes to `audit_log` before/after execution.
8. Build the `_template` connector and `_template` skill as working scaffolds with a `README.md` each explaining how to extend them.
9. Write `docs/connector-authoring-guide.md` and `docs/skill-authoring-guide.md` — these are what makes this genuinely "open source extensible," so write them as if a stranger will use them.

## Acceptance criteria
- [ ] Installing the `_template` skill via the registry works end-to-end and it appears as `enabled: false` until explicitly enabled
- [ ] A skill that hasn't been granted `write_tasks` cannot create a task — attempting it throws a clear permission error, not a silent no-op
- [ ] Killing a connector's process mid-operation results in Core marking it `status: error` and continuing to serve unrelated requests without crashing
- [ ] Every skill/connector action appears in `audit_log` with correct actor attribution
- [ ] A second developer (or a fresh agent session) can follow `docs/connector-authoring-guide.md` alone and build a working no-op connector without additional context

## Out of scope
- Real connectors (Gmail, Calendar, etc.) — Part 07
- Exposing permission approval UI in the extensions — Parts 10/11
