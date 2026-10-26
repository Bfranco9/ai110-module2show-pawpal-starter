# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

```
==================================================
Today's Schedule for Jordan
==================================================
07:00  Biscuit  Brushing        15 min  [low]
       why: low priority, placed in the earliest open slot
07:30  Mochi    Morning walk    30 min  [high]
       why: high priority, fixed at 07:30
08:15  Biscuit  Feeding         10 min  [high]
       why: high priority, fixed at 08:15
12:00  Biscuit  Litter box      10 min  [medium]
       why: medium priority, fixed at 12:00
18:00  Mochi    Evening walk    30 min  [medium]
       why: medium priority, fixed at 18:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov

```
Sample test output:
collected 30 items                                                                                                             

tests\test_pawpal.py ..............................                                                                      [100%]

===================================================== 30 passed in 0.12s ======================================================
```
# Paste your pytest output here
```

```
Confidence Level: 5
Description of Pytest:
There are 20 edge cases on top of the origial test cases covered in the pytest. There is areas to cover the sorting, recurring tasks, conflicts for back-to-back tasks that arent flagged, plan building, and the data setup. All test cases have passed with current build.
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders tasks by `HH:MM` start time using `sorted()` with a minutes-since-midnight key; flexible (untimed) tasks go last |
| Sorting by priority | `Scheduler.sort_by_priority()` | High priority first, then fixed-time tasks, then shortest duration; used when building the plan |
| Filtering | `Scheduler.get_tasks(pet_name, completed)`, `Scheduler.filter_by_constraints()` | Filter by pet and/or completion status (combinable); the plan also drops tasks not due yet or outside the owner's day window |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warning strings (never raises) for overlapping fixed-time tasks, same pet or different pets; `build_plan()` skips the lower-priority task and records why |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Completing a `daily` / `weekly` task creates the next occurrence due today + 1 / + 7 days (via `timedelta`) on the same pet; one-time tasks return `None`, and completing twice never duplicates |

### How each feature works

- **Sorting by time:** `sort_by_time()` converts each `"HH:MM"` to minutes with `to_minutes()`, so unpadded times like `"7:30"` still sort correctly. Sorting is stable, so tasks at the same time keep their original order.
- **Filtering:** `get_tasks(pet_name="Mochi", completed=False)` returns Mochi's pending tasks. Passing `None` (the default) for either argument skips that filter.
- **Conflict detection:** timed tasks are sorted, then each is compared with the tasks after it. The inner loop stops at the first task that starts at or after the current task ends. Back-to-back tasks (one ends exactly when the next starts) are not conflicts.
- **Recurring tasks:** `Task.mark_complete()` marks the task done and returns a copy with `completed=False` and a new `due_date`. `Scheduler.mark_task_complete()` adds that copy to the pet that owns the task.

Run `python main.py` to see all four features in the terminal.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
