# Part 04 — Task & Time Engine

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–03 complete.

## Context
This is the "human personal assistant" part — it has to feel like something that manages your time proactively, not a to-do list you maintain. It reads from and writes to OBSESSION (a task created from an email should leave a memory trace; a completed task pattern should inform procedural memory).

## Objective
A task/time core that: parses natural language into structured tasks, tracks time against them, schedules time blocks, scores priority, and proactively proposes a day plan.

## Requirements

### Functional
- Natural language task capture: `"remind me to submit the resume draft by Friday 6pm"` → structured task with `due_at`, `title`, inferred `priority`
- Recurring tasks via RRULE (daily standup, weekly review, etc.)
- Time tracking: start/stop/pause against a task, computes `actual_minutes`, supports Pomodoro-style blocks
- Time blocking: propose and store `time_blocks` on a calendar-like structure (focus blocks, meetings, breaks)
- Priority scoring engine combining: explicit priority, due-date urgency, historical completion patterns pulled from OBSESSION's procedural layer (e.g. "user always deprioritizes low-stakes admin tasks — deprioritize accordingly unless due today")
- Daily planning: `task_engine.plan_day(user_id)` — calls the Router (Part 05) to propose a schedule given today's tasks, calendar events, and known focus-time preferences from memory
- Task lifecycle hooks: on create/complete/miss-deadline, write an episodic memory entry to OBSESSION

### Non-functional
- All NL parsing must degrade gracefully — if parsing confidence is low, return the best structured guess *plus* the ambiguous fields flagged, never silently guess wrong on a due date
- Timezone-correct throughout — store UTC, render in `user.timezone`

## Deliverables
```
apps/core/app/tasks/
├── __init__.py
├── service.py
├── nlp/
│   └── nl_task_parser.py       (dateparser/dateutil for dates + Router call for intent/title extraction)
├── scheduling/
│   ├── time_block_service.py
│   └── day_planner_service.py  (calls Router for plan proposal)
├── priority/
│   └── priority_scorer.py
├── time_tracking/
│   └── time_tracking_service.py
└── router.py                   (FastAPI router for this domain)
```

## Step-by-step tasks
1. Integrate `dateparser` (or `python-dateutil` + a custom relative-phrase layer) for date/time extraction from free text; build `nl_task_parser.py` that extracts `{title, due_at, confidence, ambiguous_fields}`. For phrasing dateparser can't confidently resolve, fall back to a Router call with a structured extraction prompt rather than guessing.
2. Implement `TasksService` CRUD wrapping the Part 02 repository, with lifecycle hooks that call `obsession.ingest()` on create/complete/miss.
3. Implement recurrence: on completing a recurring task, generate the next occurrence per its RRULE (`python-dateutil.rrule`).
4. Implement `TimeTrackingService`: start/stop/pause, computes duration, supports multiple concurrent timers only if explicitly allowed (default: one active timer per user).
5. Implement `PriorityScorer`: weighted function of urgency (time to due), explicit priority, and a "historical deprioritization pattern" signal fetched from `obsession.query()` against procedural memory.
6. Implement `DayPlannerService.plan_day()`: gather today's tasks + calendar events (calendar integration comes in Part 07, stub the interface now) + memory-derived preferences, call the Router with a structured planning prompt, parse the response into proposed `time_blocks`, do NOT auto-commit them — return as a proposal the user must confirm.
7. Wire `TimeBlockService` to persist confirmed blocks.

## Acceptance criteria
- [ ] `"finish the SafeVixAI README by tomorrow 9am"` parses to a task with correct `due_at` in the user's timezone and reasonable title
- [ ] An ambiguous input like `"deal with the thing soon"` returns low confidence and flags `due_at` as ambiguous rather than guessing a date
- [ ] Completing a recurring task correctly spawns the next occurrence per RRULE
- [ ] Priority scores visibly shift when a task's due date approaches vs. when it's far out
- [ ] `plan_day()` returns a proposed schedule that doesn't double-book an existing calendar event or confirmed time block
- [ ] Every task create/complete/miss event produces a corresponding OBSESSION episodic memory (verify via `obsession.query`)

## Out of scope
- Actual calendar sync (Part 07 — connectors)
- The Router implementation itself (Part 05) — stub the call interface
- Exposing any of this to the extensions (Part 08)
