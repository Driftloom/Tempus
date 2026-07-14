# Part 09 — Notification & Scheduling System

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–08 complete.

## Context
Tasks and emails now generate work, but nothing surfaces it proactively yet. This part makes TEMPUS behave like a personal assistant that reaches out at the right time, rather than a system you have to check.

## Objective
A job-queue-backed reminder/notification engine (task due alerts, time-block starts, daily digests) with escalation and quiet-hours support, delivered cross-surface to both extensions.

## Requirements

### Functional
- Celery (with Redis as broker) or `arq`-backed scheduler: schedule a notification for a future time, process it when due, mark sent — recommend Celery here specifically for its mature `eta`/`countdown` scheduling and `revoke()` (needed for the idempotent-reschedule requirement below); document the choice in `docs/decisions/adr-009-job-queue.md`
- Notification types: task due soon, task overdue, time block starting, daily digest ready, connector needs re-auth, skill permission requested
- Escalation: an unacknowledged "overdue" notification re-fires on a backoff schedule (configurable) until dismissed or the task is completed
- Snooze: user can snooze a notification for a duration or "until tomorrow"; reschedules it
- Quiet hours: per-user configurable window where only high-priority notifications (nothing FYI-level) are delivered; rest are queued and delivered when quiet hours end
- Delivery is surface-agnostic at the Core level — Core emits via the WebSocket endpoint (Part 08); each extension decides how to render it as a native notification (Chrome notification API / VS Code notification API — built in Parts 10/11)

### Non-functional
- Idempotent scheduling — rescheduling a job for the same logical event (e.g. task due date changed) must cancel/replace the old scheduled job, not create a duplicate
- Missed jobs (Core was offline when a notification was due) fire immediately on next startup rather than being silently dropped

## Deliverables
```
apps/core/app/notifications/
├── __init__.py
├── scheduler/
│   ├── celery_app.py                (Celery app + Redis broker config)
│   ├── tasks.py                     (Celery task — the actual "fire" logic)
│   └── escalation.py
├── quiet_hours.py
├── service.py                       (schedule/cancel/snooze/dismiss — public API)
└── router.py                        (wired into Part 08's API, or merged there)
docs/decisions/adr-009-job-queue.md
```

## Step-by-step tasks
1. Set up Celery + worker against the Redis instance from Part 01; run the worker as its own process (documented in the root `Makefile`/`docker-compose.yml` alongside `uvicorn`).
2. Implement `NotificationsService.schedule()`: takes a type, payload, `scheduled_for`; on reschedule for the same logical source (e.g. `task_id` + type), calls `AsyncResult(prior_task_id).revoke()` before scheduling the new one, tracking the active Celery task id against the `notifications` row.
3. Implement the Celery task: on execution, check quiet hours (defer if in quiet hours and not high-priority), write `notifications` row as `sent`, emit via Part 08's WebSocket endpoint.
4. Implement escalation: on task-overdue notifications specifically, re-enqueue with backoff (e.g. 30min → 2hr → 6hr) via `apply_async(countdown=...)` until dismissed/completed, capped at a configurable max re-fires.
5. Implement snooze: revokes the current scheduled task, re-schedules for `now + duration` (or next-day-9am for "until tomorrow"), updates status to `snoozed`.
6. Implement quiet hours config (start/end time in user timezone) and the priority gate.
7. On Core startup (FastAPI `lifespan` handler), query for any notifications with `scheduled_for` in the past and `status: pending` — fire immediately (handles the "Core was offline" case).
8. Wire Task Engine (Part 04) to call `schedule()` on task creation/due-date change, and Email Intelligence (Part 07) to call it when the daily digest is ready.
9. Write `docs/decisions/adr-009-job-queue.md` documenting the Celery-over-arq call (mature revoke/eta support vs. lighter async-native footprint).

## Acceptance criteria
- [ ] Scheduling two notifications for the same task+type results in only one active job (second call cancels/replaces the first)
- [ ] An overdue task notification escalates on the configured backoff and stops after being dismissed
- [ ] A notification scheduled to fire during quiet hours is deferred and delivered right after quiet hours end (unless high-priority)
- [ ] Stopping Core, letting a scheduled notification's time pass, then restarting Core — the notification fires promptly on startup rather than never
- [ ] Snoozing "until tomorrow" reschedules to the expected time in the user's timezone

## Out of scope
- Native notification rendering (Chrome/VS Code notification APIs) — Parts 10/11
