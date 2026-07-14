# Part 17 — Evals Framework

**Use with:** Claude Code / OpenCode / Codex. Requires Parts 01–16 complete. This is the last part in the series — it measures everything built before it.

## Context
"It looks like it's working" isn't a production metric. This part builds repeatable, automated measurement for the things that actually matter: is the memory classifier accurate, does the task parser get dates right, do agents actually complete their goals, do Guardrails actually catch injection attempts without being so trigger-happy they block everything. Without this, every future change to a prompt, model, or routing policy is a guess.

## Requirements

### Functional
- **Golden datasets**, one per measurable subsystem:
  - Memory classification (Part 03): labeled examples of layer + sensitivity classification
  - Task NL parsing (Part 04): free-text input → expected structured task output
  - Agent task success (Parts 14/15): goal + scenario → rubric for what "success" looks like, scored via LLM-as-judge since success often isn't exact-match
  - Guardrail effectiveness (Part 16): known injection patterns (must be blocked/escalated) alongside known-benign edge cases (must NOT be falsely blocked)
- **Automated eval runner**: executes each dataset against the current system, produces a scorecard (accuracy/precision/recall where exact-match applies, rubric score where LLM-as-judge applies)
- **LLM-as-judge**: for subjective quality (e.g., "was this day-plan actually reasonable given the constraints"), a dedicated judge prompt template run through the Router/Gateway (Part 05) using a fixed, cheaper model — tracked as its own line item in inference economics, not conflated with production traffic cost
- **Regression gating**: wired into CI (extends Part 13) — a PR that drops any eval score below its configured threshold fails the build
- **Feedback ingestion**: user corrections (fixing a mis-parsed task, dismissing a wrong memory, declining a Guardrails-escalated action) get captured and periodically reviewed as candidates to add to the golden datasets — real usage becomes eval data over time, not just synthetic examples written once

### Non-functional
- Eval runs must be reproducible — pin the judge model version, log it alongside every scorecard, so a score change is attributable to an actual system change, not model drift
- Eval datasets are version-controlled like code — changes to a golden dataset go through the same PR review as anything else

## Deliverables
```
evals/
├── datasets/
│   ├── memory_classification.jsonl
│   ├── task_parsing.jsonl
│   ├── agent_task_success.jsonl
│   └── guardrail_effectiveness.jsonl
├── runners/
│   ├── run_classification_evals.py
│   ├── run_parsing_evals.py
│   ├── run_agent_evals.py        (LLM-as-judge via the Gateway)
│   └── run_guardrail_evals.py
├── judge/
│   ├── llm_judge.py
│   └── templates/
│       └── judge-agent-success-v1.md
├── feedback_ingestion.py          (pulls user corrections into dataset candidate queue)
├── thresholds.yaml                (per-dataset pass/fail thresholds)
└── report.py                      (scorecard generation, trend-over-time)
.github/workflows/evals.yml        (PR-triggered on relevant path changes + scheduled nightly)
docs/evals/README.md
```

## Step-by-step tasks
1. Seed each golden dataset with an initial hand-written set of examples (aim for at least 30-50 per dataset to start) — cover both clear cases and the genuinely ambiguous ones that are most likely to regress silently.
2. Build `run_classification_evals.py` and `run_parsing_evals.py`: deterministic exact/near-match scoring against Parts 03/04's actual classifier/parser output.
3. Build `llm_judge.py` + `judge-agent-success-v1.md`: given a completed `AgentRun` (Part 14's trace) and its scenario's success rubric, the judge model scores 0-1 with a brief justification — pin the judge model explicitly (don't let it silently drift to "whatever the default model is this week").
4. Build `run_agent_evals.py`: runs scenarios from `agent_task_success.jsonl` through the actual Loop Engine, feeds the resulting trace to the judge, aggregates scores.
5. Build `run_guardrail_evals.py`: runs both the injection patterns (must be blocked/escalated) and the benign edge cases (must not be blocked) from `guardrail_effectiveness.jsonl` through Part 16's actual pipeline, scores both directions (catch rate AND false-positive rate — report both, since optimizing only one degrades the other).
6. Write `thresholds.yaml` with an initial reasonable floor per dataset (e.g., classification ≥90%, parsing ≥85%, agent success ≥75% given it's judged more subjectively, guardrail catch rate ≥95% with false-positive rate ≤10%).
7. Write `.github/workflows/evals.yml`: run all four eval suites on any PR touching `apps/core/app/{obsession,tasks,agents,guardrails}` or `evals/datasets/`, plus a nightly scheduled full run; fail the PR if any threshold is breached.
8. Build `feedback_ingestion.py`: hooks into user-correction points already built (task edits after NL-parse, memory dismissals, Guardrails confirmation declines) and writes them to a review queue rather than auto-adding to datasets (a human should still curate what becomes a permanent golden example).
9. Build `report.py`: a simple scorecard (markdown or JSON) per run, with score-over-time so a regression is visible even if it's still above threshold.
10. Write `docs/evals/README.md`: how to add a new dataset example, how to add a new dataset category entirely, how the judge model is chosen/pinned, and how to interpret a failing CI eval run.

## Acceptance criteria
- [ ] Running the full eval suite locally produces a scorecard for all four subsystems with clear pass/fail against `thresholds.yaml`
- [ ] Deliberately introducing a regression (e.g., breaking the date parser on a specific phrasing) causes the corresponding eval to fail and the CI job to go red
- [ ] The guardrail eval reports both catch rate and false-positive rate as separate numbers — a change that improves one at the clear expense of the other is visible, not hidden in a single blended score
- [ ] Two consecutive runs of the agent-success eval against an unchanged system produce consistent scores (judge model pinned, not silently drifting)
- [ ] A user's task-parse correction shows up in the feedback review queue, not automatically and silently added to the golden dataset
- [ ] `docs/evals/README.md` alone is enough for a stranger to add a new golden example correctly

## Out of scope
- Nothing new functionally — this part only measures Parts 01–16. If every eval passes its threshold and the guardrail injection test (Part 16) plus this suite are both green, the system is genuinely done, not just feature-complete.
