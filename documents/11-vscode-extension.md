# Part 11 — VS Code Extension

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–09 complete (specifically 08 for the API/SDK, 09 for notifications). Buildable in parallel with Part 10.

## Context
This is the "meets you where you actually work" surface for coding work specifically — time tracking that's aware of what you're coding, and TODOs that become real tracked tasks instead of comments that rot.

## Objective
A VS Code extension with status-bar time tracking, command-palette actions, a webview dashboard mirroring the Chrome side panel's core views, and CodeLens on TODO/FIXME comments — all on `packages/core-sdk`.

## Requirements

### Functional
- **Status bar item**: shows current active task/timer if one is running, click to open a quick-pick to switch/start/stop
- **Command palette commands**: `TEMPUS: Start Timer`, `TEMPUS: Stop Timer`, `TEMPUS: Quick Add Task`, `TEMPUS: Ask Assistant` (free text → routed to a skill, e.g. plan-my-day, via Core), `TEMPUS: Open Dashboard`
- **CodeLens**: on `// TODO` / `// FIXME` comments, show an inline "Track as task" action that creates a task with `source: "vscode"`, `source_ref` pointing to file+line, and links back (clicking the resulting task in the dashboard can reveal the file+line)
- **Webview dashboard**: reuses `packages/ui-kit` components where possible — today's tasks, quick capture, memory search (same feature set as the Chrome side panel's core views, adapted to VS Code's webview constraints)
- **Native notifications**: VS Code's `window.showInformationMessage` / `showWarningMessage` for task-due and overdue events relayed from Core's WebSocket gateway

### Non-functional
- Auth token stored via VS Code's `SecretStorage` API (never in plain settings/workspace state)
- Extension must not block the editor UI thread — all Core calls async, webview loads independently of editor responsiveness
- Works across multiple VS Code windows without duplicate timers or conflicting state (single source of truth is Core, not local extension state)

## Deliverables
```
apps/vscode-extension/
├── package.json                 (contributes: commands, viewsContainers, views)
├── src/
│   ├── extension.ts              (activation, command registration)
│   ├── status-bar/
│   │   └── timer-status-bar.ts
│   ├── codelens/
│   │   └── todo-codelens-provider.ts
│   ├── commands/
│   │   ├── start-stop-timer.ts
│   │   ├── quick-add-task.ts
│   │   └── ask-assistant.ts
│   ├── webview/
│   │   └── dashboard-panel.ts    (webview host, loads the React dashboard build)
│   └── notifications/
│       └── notification-bridge.ts (WS event → VS Code native notification)
└── webview-ui/                   (React app reusing packages/ui-kit, built separately, 
                                    bundled into the extension)
```

## Step-by-step tasks
1. Scaffold command contributions in `package.json`, register handlers in `extension.ts`.
2. Implement `TimerStatusBarItem`: subscribes to Core's WebSocket via `core-sdk` for timer state changes, click opens a `QuickPick` of active/recent tasks to start/switch, updates live.
3. Implement `TodoCodelensProvider`: regex/AST scan for `TODO`/`FIXME` comments, register a CodeLens with a "Track as task" command that calls `core-sdk`'s task creation with file+line as `source_ref`.
4. Implement the three remaining commands (`quick-add-task`, `start-stop-timer` toggle, `ask-assistant` — free text input via `showInputBox`, routed to Core which dispatches to the appropriate skill).
5. Build `webview-ui` as a small React app sharing `packages/ui-kit` components with the Chrome side panel (Today's Tasks, Quick Capture, Memory Search) — bundle via Vite, load into the webview via `DashboardPanel`.
6. Implement `notification-bridge.ts`: background WS listener maps Core notification events to VS Code native notifications, respecting the same quiet-hours logic already enforced server-side (client just renders what Core sends).
7. Store the device auth token via `context.secrets` (SecretStorage API), never in `globalState`/settings.
8. Handle multi-window: rely entirely on Core as source of truth for timer/task state — no window keeps its own authoritative timer state, always reflects what Core reports.

## Acceptance criteria
- [ ] Starting a timer from the status bar in one VS Code window is reflected correctly in a second open window (via Core, not local state)
- [ ] Clicking "Track as task" on a `// TODO` comment creates a task with correct file+line reference, retrievable from the dashboard
- [ ] `TEMPUS: Ask Assistant` correctly routes free text to Core and displays the response
- [ ] Auth token is confirmed to live in `SecretStorage`, not in any settings file (inspect the stored VS Code state to verify)
- [ ] A task-overdue event from Core produces a native VS Code notification without polling (verify via the WebSocket bridge, not a timer-based check)
- [ ] Webview dashboard renders and functions with the editor otherwise fully responsive (no UI thread blocking)

## Out of scope
- Chrome extension (Part 10, parallel-buildable)
- Any new Core functionality — this part only consumes the existing API
