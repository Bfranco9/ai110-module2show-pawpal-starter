import sys
from pathlib import Path

# Make pawpal_system.py (one folder up) importable when running `pytest`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler():
    owner = Owner("Jordan", day_start="07:00", day_end="21:00")
    dog, cat = Pet("Mochi", "dog"), Pet("Biscuit", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return Scheduler(owner), dog, cat


def test_sort_by_time_orders_chronologically_with_flexible_last():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Evening", 10, time="18:00"))
    dog.add_task(Task("Flex", 10))
    dog.add_task(Task("Morning", 10, time="07:30"))

    result = scheduler.sort_by_time(scheduler.get_tasks())

    assert [t.description for t in result] == ["Morning", "Evening", "Flex"]


def test_filter_by_pet_and_status():
    scheduler, dog, cat = make_scheduler()
    dog.add_task(Task("Walk", 30))
    cat.add_task(Task("Feed", 10))
    scheduler.get_tasks(pet_name="Biscuit")[0].mark_complete()

    assert [t.description for t in scheduler.get_tasks(pet_name="Mochi")] == ["Walk"]
    assert [t.description for t in scheduler.get_tasks(completed=True)] == ["Feed"]
    assert [t.description for t in scheduler.get_tasks(completed=False)] == ["Walk"]


def test_daily_task_recurs_next_day():
    scheduler, dog, _ = make_scheduler()
    task = Task("Walk", 30, frequency="daily")
    dog.add_task(task)

    nxt = scheduler.mark_task_complete(task)

    assert task.completed and not nxt.completed
    assert nxt.due_date == date.today() + timedelta(days=1)
    assert nxt in dog.tasks and nxt.pet_name == "Mochi"


def test_weekly_task_recurs_in_seven_days_and_completing_twice_is_safe():
    scheduler, dog, _ = make_scheduler()
    task = Task("Bath", 20, frequency="weekly")
    dog.add_task(task)

    nxt = scheduler.mark_task_complete(task)

    assert nxt.due_date == date.today() + timedelta(days=7)
    assert scheduler.mark_task_complete(task) is None
    assert len(dog.tasks) == 2


def test_detect_conflicts_same_exact_time():
    scheduler, dog, cat = make_scheduler()
    dog.add_task(Task("Walk", 30, time="08:00"))
    cat.add_task(Task("Feed", 10, time="08:00"))

    assert len(scheduler.detect_conflicts()) == 1


def test_one_time_task_does_not_recur():
    scheduler, dog, _ = make_scheduler()
    task = Task("Vet", 30)
    dog.add_task(task)

    assert scheduler.mark_task_complete(task) is None
    assert len(dog.tasks) == 1


def test_detect_conflicts_across_pets():
    scheduler, dog, cat = make_scheduler()
    dog.add_task(Task("Walk", 30, time="08:00"))
    cat.add_task(Task("Feed", 10, time="08:15"))
    cat.add_task(Task("Litter", 10, time="12:00"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1 and "Walk" in warnings[0] and "Feed" in warnings[0]


def test_build_plan_skips_conflicting_lower_priority_task():
    scheduler, dog, cat = make_scheduler()
    dog.add_task(Task("Walk", 30, "high", time="08:00"))
    cat.add_task(Task("Feed", 10, "low", time="08:15"))

    plan = scheduler.build_plan()

    assert [t.description for _, t, _ in plan] == ["Walk"]
    assert scheduler.skipped[0][0].description == "Feed"


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, "high"))

    assert len(pet.tasks) == 1


# ---- Edge cases ----


def test_sort_by_time_handles_unpadded_times_and_is_stable():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Ten", 10, time="10:00"))
    dog.add_task(Task("SevenThirty", 10, time="7:30"))
    dog.add_task(Task("TenB", 10, time="10:00"))

    result = scheduler.sort_by_time(scheduler.get_tasks())

    assert [t.description for t in result] == ["SevenThirty", "Ten", "TenB"]


def test_sort_by_priority_order_ties_and_unknown_priority():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Low", 5, "low"))
    dog.add_task(Task("HighLong", 30, "high"))
    dog.add_task(Task("HighShort", 10, "high"))
    dog.add_task(Task("HighTimed", 30, "high", time="09:00"))
    dog.add_task(Task("Weird", 5, "urgent"))
    tasks = scheduler.get_tasks()

    result = scheduler.sort_by_priority(tasks)

    assert [t.description for t in result[:3]] == ["HighTimed", "HighShort", "HighLong"]
    assert {t.description for t in result[-2:]} == {"Low", "Weird"}
    assert tasks[0].description == "Low"  # input list not mutated


def test_sort_empty_list():
    scheduler, _, _ = make_scheduler()

    assert scheduler.sort_by_time([]) == []
    assert scheduler.sort_by_priority([]) == []


def test_recurring_next_task_is_pending_and_separate_object():
    scheduler, dog, _ = make_scheduler()
    task = Task("Walk", 30, frequency="daily")
    dog.add_task(task)

    nxt = scheduler.mark_task_complete(task)

    assert nxt is not task and nxt.completed is False and task.completed is True


def test_overdue_recurring_task_recurs_from_today():
    scheduler, dog, _ = make_scheduler()
    task = Task("Walk", 30, frequency="daily", due_date=date.today() - timedelta(days=3))
    dog.add_task(task)

    nxt = scheduler.mark_task_complete(task)

    assert nxt.due_date == date.today() + timedelta(days=1)


def test_recurring_task_with_unknown_pet_is_not_added():
    scheduler, _, _ = make_scheduler()
    task = Task("Walk", 30, frequency="daily", pet_name="Ghost")

    nxt = scheduler.mark_task_complete(task)

    assert nxt is not None
    assert scheduler.get_tasks() == []


def test_unknown_frequency_does_not_recur():
    scheduler, dog, _ = make_scheduler()
    task = Task("Odd", 10, frequency="monthly")
    dog.add_task(task)

    assert scheduler.mark_task_complete(task) is None


def test_back_to_back_tasks_are_not_conflicts():
    scheduler, dog, cat = make_scheduler()
    dog.add_task(Task("Walk", 30, time="08:00"))
    cat.add_task(Task("Feed", 10, time="08:30"))

    assert scheduler.detect_conflicts() == []


def test_conflicts_ignore_completed_future_and_flexible_tasks():
    scheduler, dog, cat = make_scheduler()
    done = Task("Done", 30, time="08:00")
    dog.add_task(done)
    done.mark_complete()
    dog.add_task(Task("Future", 30, time="08:00", due_date=date.today() + timedelta(days=2)))
    cat.add_task(Task("Flex", 30))
    cat.add_task(Task("Active", 30, time="08:00"))

    assert scheduler.detect_conflicts() == []


def test_three_overlapping_tasks_give_three_warnings():
    scheduler, dog, cat = make_scheduler()
    dog.add_task(Task("A", 60, time="08:00"))
    cat.add_task(Task("B", 60, time="08:10"))
    cat.add_task(Task("C", 60, time="08:20"))

    assert len(scheduler.detect_conflicts()) == 3


def test_build_plan_with_no_tasks_or_no_pets():
    scheduler, _, _ = make_scheduler()

    assert scheduler.build_plan() == []
    assert Scheduler(Owner("Empty")).build_plan() == []


def test_build_plan_places_flexible_task_around_fixed_one():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Fixed", 60, "high", time="07:00"))
    dog.add_task(Task("Flex", 30, "medium"))

    plan = scheduler.build_plan()

    assert [(s, t.description) for s, t, _ in plan] == [("07:00", "Fixed"), ("08:00", "Flex")]


def test_build_plan_skips_task_longer_than_available_time():
    scheduler, dog, _ = make_scheduler()
    scheduler.owner.available_minutes = 20
    dog.add_task(Task("Long", 30))

    assert scheduler.build_plan() == []
    assert "not enough time" in scheduler.skipped[0][1]


def test_build_plan_skips_fixed_task_outside_day_window():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Early", 10, time="06:00"))
    dog.add_task(Task("Late", 30, time="20:45"))  # ends 21:15, past 21:00

    assert scheduler.build_plan() == []
    assert len(scheduler.skipped) == 2


def test_build_plan_flexible_task_boundary_fit():
    owner = Owner("Jordan", available_minutes=500, day_start="08:00", day_end="09:00")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Exact", 60))
    scheduler = Scheduler(owner)

    assert [t.description for _, t, _ in scheduler.build_plan()] == ["Exact"]

    pet.tasks[0].duration_minutes = 61

    assert scheduler.build_plan() == []
    assert "no open slot" in scheduler.skipped[0][1]


def test_build_plan_excludes_completed_and_future_tasks():
    scheduler, dog, _ = make_scheduler()
    done = Task("Done", 10)
    dog.add_task(done)
    done.mark_complete()
    dog.add_task(Task("Future", 10, due_date=date.today() + timedelta(days=1)))

    assert scheduler.build_plan() == []


def test_build_plan_twice_does_not_duplicate():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Walk", 30))
    dog.add_task(Task("Huge", 9999))

    scheduler.build_plan()
    scheduler.build_plan()

    assert len(scheduler.plan) == 1 and len(scheduler.skipped) == 1


def test_get_tasks_unknown_pet_and_combined_filters():
    scheduler, dog, _ = make_scheduler()
    a, b = Task("A", 10), Task("B", 10)
    dog.add_task(a)
    dog.add_task(b)
    a.mark_complete()

    assert scheduler.get_tasks(pet_name="Nobody") == []
    assert scheduler.get_tasks(pet_name="Mochi", completed=True) == [a]
    assert scheduler.get_tasks(pet_name="Biscuit", completed=True) == []


def test_remove_task_missing_and_duplicate_descriptions():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 10))
    pet.add_task(Task("Walk", 20))

    assert pet.remove_task("Nope") is False
    assert pet.remove_task("Walk") is True
    assert [t.duration_minutes for t in pet.tasks] == [20]


def test_malformed_time_raises_value_error():
    scheduler, dog, _ = make_scheduler()
    dog.add_task(Task("Bad", 10, time="8am"))

    with pytest.raises(ValueError):
        scheduler.sort_by_time(scheduler.get_tasks())
