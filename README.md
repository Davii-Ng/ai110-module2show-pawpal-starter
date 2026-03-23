# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app for planning daily pet care with scheduling constraints, recurrence support, and explainable outputs.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What This App Does

PawPal+ lets a pet owner:

- Manage owner and pet profiles
- Add tasks with duration, priority, and pet assignment
- Generate a daily plan within a day window
- Show scheduled and unscheduled tasks with reasons
- Surface conflict warnings in the UI

## Features

The feature list below reflects the implemented algorithms in `pawpal_systems.py` and UI integration in `app.py`.

- **Sorting by time**
	Tasks are sorted chronologically using `earliest_time`, with support for `HH:MM` string fallback (`Scheduler.sort_by_time`) and recurring next-occurrence ordering (`Scheduler.sort_tasks_by_time`).
- **Task filtering**
	Tasks can be filtered by pet (ID or pet name) and completion state (`Scheduler.filter_tasks`, `Scheduler.filter_tasks_by_pet_name`).
- **Greedy schedule generation**
	The scheduler performs a first-fit greedy pass over incomplete tasks, enforcing earliest/latest times and optional day-window bounds (`Scheduler.generate_schedule`).
- **Unscheduled reason tracking**
	Tasks that cannot be placed are preserved with explicit reasons like `cannot meet latest_time`, `outside day window`, or conflict metadata.
- **Conflict warnings**
	Overlapping scheduled entries are detected and returned as human-readable warnings (`Scheduler.detect_conflicts`, `Scheduler.find_conflicts`).
- **Daily and weekly recurrence support**
	Recurring tasks support `daily`/`weekly` recurrence or explicit `frequency_days`, with next-task creation on completion (`Task.mark_complete`, `Task.next_occurrence`, `Scheduler.mark_task_complete`).
- **Explainable plan output**
	The scheduler produces explanation text for each schedule entry (`Scheduler.explain`) and the app surfaces this in a dedicated explanation section.
- **Auto ID management (internal)**
	IDs are generated automatically across domain entities via `IDManager`, while frontend display keeps IDs hidden for cleaner UX.

## Smarter Scheduling

This project adds several scheduling improvements: tasks can be sorted by next occurrence or an HH:MM string, filtered by pet or completion status, and recurring tasks are expanded lazily. The scheduler detects lightweight conflicts and will warn instead of crashing. Marking recurring tasks complete will automatically create the next occurrence.

## 📸 Demo

Add your final Streamlit screenshot at `assets/pawpal-demo.png`, then this section will render it in GitHub:

![PawPal+ Streamlit Demo](image.png)

Suggested capture: show the Task Board and Today's Plan sections with at least one conflict warning and one scheduled task.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

Current tests cover core model and scheduler behavior, including:

- Task completion state changes (`Task.mark_complete`)
- Pet/task linkage (`Pet.add_task` and task ID tracking)
- Sorting correctness (tasks returned in chronological order)
- Recurrence logic (daily completion creates a next-day task)
- Conflict detection (duplicate/overlapping scheduled times are flagged)
- Scheduling edge cases (no tasks, missed latest time, outside day window, completed-task filtering, malformed time strings)

Confidence Level: 4/5 stars

Rationale: test results are currently passing and cover core happy paths plus important edge cases, but additional scenarios (for example larger mixed-priority workloads and owner-availability enforcement) would further improve reliability confidence.
