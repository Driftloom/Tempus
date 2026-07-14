# Part 10 — Chrome Extension

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–09 complete (specifically 08 for the API/SDK, 09 for notifications).

## Context
This is one of the two surfaces you actually live in. It should feel like a lightweight command center, not a dashboard you have to navigate — quick capture and glanceable status are the priorities over exhaustive views.

## Objective
A Manifest V3 Chrome extension with a side panel dashboard, page-context capture, real-time sync with Core, and native notifications — built entirely on `packages/core-sdk`.

## Requirements

### Functional
- **Side panel** (primary UI): today's tasks (grouped by time block/priority), quick-capture input (NL task entry, hits the Task Engine's NL parser), memory search bar, connector status indicators, pending permission-grant requests from skills
- **Content script**: adds a lightweight "Save to TEMPUS" action (context menu + optional floating button) that captures selected text or the current page's key content into OBSESSION with `source: "browser"` and the page URL as `source_ref`
- **Background service worker**: maintains the WebSocket connection to Core (Part 08's gateway), reconnects on failure, relays real-time events to the side panel and to Chrome's native notification API
- **Omnibox**: typing a keyword (e.g. `t`) + Tab in the address bar, then free text, quick-adds a task without opening the side panel
- **Badge**: extension icon badge shows count of pending/overdue tasks

### Non-functional
- All Core communication goes through `packages/core-sdk` — no raw `fetch` calls to Core scattered in extension code
- Auth token (from Part 08's device auth) stored in `chrome.storage.local` (never `localStorage`), refreshed transparently
- Graceful offline state: if Core is unreachable, side panel shows a clear "disconnected" state rather than silently failing or showing stale data as if current

## Deliverables
```
apps/chrome-extension/
├── manifest.json                (Manifest V3: sidePanel, contextMenus, notifications, 
                                    storage, omnibox permissions)
├── src/
│   ├── background/
│   │   └── service-worker.ts    (WS connection, event relay, notification bridge)
│   ├── content/
│   │   └── capture.ts           (context menu + selection capture)
│   ├── side-panel/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── TodayTasks.tsx
│   │   │   ├── QuickCapture.tsx
│   │   │   ├── MemorySearch.tsx
│   │   │   ├── ConnectorStatus.tsx
│   │   │   └── PermissionRequests.tsx
│   │   └── main.tsx
│   └── omnibox/
│       └── omnibox.ts
```

## Step-by-step tasks
1. Configure `manifest.json` with `side_panel`, `contextMenus`, `notifications`, `storage`, `omnibox` permissions and the correct CSP for connecting to Core's `localhost` origin (and documenting how to point it at a remote Core URL for non-local deployments).
2. Build the background service worker: opens a WebSocket to Core via `core-sdk`, handles reconnect-with-backoff, on receiving task/notification events relays to (a) the side panel via `chrome.runtime` messaging and (b) `chrome.notifications.create` for anything that should be a native OS notification.
3. Build `TodayTasks`: fetches via `core-sdk`, groups by time block, shows priority, supports complete/snooze inline.
4. Build `QuickCapture`: free-text input, calls the Task Engine's NL parse endpoint, shows the parsed result (with ambiguous fields highlighted) before confirming creation.
5. Build `MemorySearch`: calls `obsession.query` via SDK, renders ranked results.
6. Build `ConnectorStatus`: lists connectors with status badges, "reconnect" action triggers the OAuth flow (opens Core's OAuth URL in a new tab).
7. Build `PermissionRequests`: lists pending skill permission requests (from Part 06), approve/deny buttons calling the permission API.
8. Build the content script: context menu item "Save selection to TEMPUS," captures `{text, url, title}` and posts to OBSESSION ingest via SDK.
9. Build the omnibox handler: keyword input triggers the same NL task creation as Quick Capture.
10. Implement the badge: background worker updates `chrome.action.setBadgeText` based on pending/overdue count from real-time events.
11. Implement the disconnected state: if the WS connection drops, side panel shows a persistent banner, retries per the background worker's backoff.

## Acceptance criteria
- [ ] Side panel loads today's tasks correctly grouped, and completing a task updates in real time without a manual refresh
- [ ] Quick capture correctly creates a task from natural language and surfaces ambiguous date parsing before confirming
- [ ] Right-clicking selected text on any webpage successfully saves it to memory, visible via a subsequent Memory Search
- [ ] Killing Core mid-session shows the disconnected state in the side panel and recovers automatically once Core is back
- [ ] A skill permission request appears in the side panel and approving it is reflected in Core's `plugin_permissions` table
- [ ] Extension badge count matches actual pending/overdue task count

## Out of scope
- VS Code extension (Part 11, parallel-buildable)
- Any new Core functionality — this part only consumes the existing API
