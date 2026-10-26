import sys
from pathlib import Path

# Make pawpal_system.py (one folder up) importable when running `pytest`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date, timedelta

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
