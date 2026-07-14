# Part 07 — Email Intelligence Pipeline

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–06 complete.

## Context
This is the "should know the important things from mail" requirement. Built as a real connector (Gmail first, Outlook second) plus an extraction pipeline that writes into both the Task Engine and OBSESSION — the point isn't "summarize my inbox," it's "the assistant already knows what's in there and acted on it."

**Security note (read before building)**: email is the single largest untrusted-input surface in this whole system. Every piece of content this pipeline extracts must be tagged as `external_untrusted:email` provenance (Part 16 defines the tagging mechanism) the moment it's ingested — this part just needs to apply the tag consistently at the point of ingestion into OBSESSION (Part 03) and Task creation (Part 04), so Part 16's injection defense has something to enforce against later. Don't build any deterministic auto-action here that would be genuinely dangerous if an email contained a manipulative instruction (e.g., never auto-send anything based solely on email content) — Part 06's Skill permission model already constrains this pipeline's Skill to task-creation and memory-ingest, not send/delete actions, which is the correct default.

## Objective
A Gmail MCP connector + a triage/extraction pipeline that turns unread/recent email into structured tasks and memory entries automatically, plus a daily digest.

## Requirements

### Functional
- **Gmail connector** (`connectors/gmail/`): OAuth2 flow, MCP tools — `list_messages`, `get_message`, `mark_read`, `list_recent(since)`. Built against the connector template from Part 06.
- **Outlook connector** (`connectors/outlook/`): same shape via Microsoft Graph API — build second, reusing as much pipeline logic as possible.
- **Extraction pipeline**:
  1. Fetch new/unread messages since last sync
  2. Local-model pass (via Router, `sensitivity: high` — email content is personal by default): classify category (action-required, fyi, newsletter, spam-like, personal), redact/flag PII
  3. Entity extraction: deadlines, action items, meeting requests, sender importance (is this a known important contact from memory?)
  4. For genuinely complex prioritization/summarization where sensitivity allows, escalate to cloud via Router per its policy — most email content should stay `high` sensitivity by default; only allow `low`/`medium` if the user explicitly marks a sender/label as non-sensitive
  5. Action items → create tasks via Task Engine (`source: "email"`, `source_ref: messageId`)
  6. Key facts (new commitments, deadlines mentioned, relationship context) → `obsession.ingest()`
- **Daily digest**: a skill (`skills/email-triage/`) that runs on a schedule, produces a structured summary of what came in and what was auto-actioned, delivered via the Notification system (Part 09)

### Non-functional
- Default sensitivity for all email content is `high` unless the user has explicitly configured a sender/domain as lower-sensitivity — err toward privacy
- Idempotent sync: re-running sync on the same time window must not create duplicate tasks/memories (dedupe on `source_ref`)
- Sync failures (expired OAuth token, API rate limit) must degrade gracefully and surface a clear `connector.status: error` rather than silently stopping

## Deliverables
```
connectors/gmail/
├── manifest.json
├── auth/oauth_flow.py
├── tools/
│   ├── list_messages.py
│   ├── get_message.py
│   └── mark_read.py
├── pyproject.toml              (standalone MCP server, own deps: google-api-python-client etc.)
└── README.md
connectors/outlook/            (same shape, via msgraph-sdk-python)
apps/core/app/email_intelligence/
├── __init__.py
├── pipeline/
│   ├── classifier.py
│   ├── entity_extractor.py
│   └── action_item_mapper.py
├── sync/
│   └── sync_service.py        (fetch-since-last-sync, dedupe, orchestrate pipeline)
└── router.py
skills/email-triage/
├── skill.json
└── run.py                     (daily digest generation)
```

## Step-by-step tasks
1. Implement Gmail OAuth2 flow and the three MCP tools against the Gmail API, using the official `mcp` Python SDK to expose them as a standard MCP server (this connector runs as its own small process/package, per Part 06's connector lifecycle).
2. Implement `SyncService`: track `last_sync_at` per connector, fetch new messages, hand each to the pipeline.
3. Implement `classifier.py`: local Router call (`sensitivity: high`) to categorize each message and flag whether it contains an action item or deadline.
4. Implement `entity_extractor.py`: pull structured `{deadline, action_description, meeting_request, sender}` from flagged messages.
5. Implement `action_item_mapper.py`: convert extracted entities into Task Engine `create_task()` calls with `source: "email"` and idempotency check against `source_ref`.
6. Wire facts (non-task-worthy but memory-worthy content — e.g. "sender mentioned they're the new PM on this account") into `obsession.ingest()` with appropriate layer/sensitivity, and with `provenance: external_untrusted:email` set on every ingested item and every created task's `source_ref` metadata (this is the tag Part 16's injection defense will later enforce against — get it applied consistently now even though nothing consumes it yet).
7. Build `skills/email-triage/run.py`: aggregate the sync run's results into a digest object, hand off to Notifications (Part 09) — stub the notification call if Part 09 isn't built yet.
8. Repeat 1–2 for Outlook via Microsoft Graph (`msgraph-sdk` Python package), reusing the pipeline (steps 3–6 should be connector-agnostic already if built correctly).
9. Write `connectors/gmail/README.md` and `connectors/outlook/README.md` covering required OAuth app setup (scopes needed, redirect URI, how to get credentials) — this is real setup friction for an open-source user, document it well.

## Acceptance criteria
- [ ] Connecting a real (or sandboxed test) Gmail account and running sync produces tasks for genuinely actionable emails and no tasks for newsletters/FYI content
- [ ] Re-running sync on an unchanged inbox produces zero duplicate tasks or memories
- [ ] Email content is routed through the Router with `sensitivity: high` by default — verify no email content reaches the cloud provider without an explicit user override
- [ ] An expired OAuth token results in `connector.status: error` with a clear reason, not a crash or silent failure
- [ ] Daily digest correctly summarizes what was synced and what actions were taken

## Out of scope
- Notification delivery mechanics (Part 09 — this part only produces the digest content)
- Surfacing connector setup/OAuth UI in the extensions (Parts 10/11)
