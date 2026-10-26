"""Demo script: exercises sorting, filtering, recurring tasks, and conflict detection."""

from typing import Iterable

from pawpal_system import Owner, Pet, Scheduler, Task

# (pet, species, age) and their tasks as (description, minutes, priority, time, frequency).
# Tasks are deliberately entered out of time order, and two overlap, to exercise the scheduler.
PETS = [
    ("Mochi", "dog", 3),
    ("Biscuit", "cat", 5),
]
TASKS = {
    "Mochi": [
        ("Evening walk", 30, "medium", "18:00", "daily"),
        ("Morning walk", 30, "high", "07:30", "daily"),
        ("Vet meds", 15, "high", "07:30", "once"),  # same time as Morning walk
    ],
    "Biscuit": [
        ("Litter box", 10, "medium", "12:00", "daily"),
        ("Feeding", 10, "high", "08:15", "daily"),
        ("Brushing", 15, "low", "", "weekly"),
    ],
}


def build_owner() -> Owner:
    """Create the demo owner and populate pets/tasks from the tables above."""
    owner = Owner("Jordan", available_minutes=120, day_start="07:00", day_end="21:00")
    for name, species, age in PETS:
        pet = Pet(name, species, age)
        for description, minutes, priority, time, frequency in TASKS[name]:
            pet.add_task(Task(description, minutes, priority, time=time, frequency=frequency))
        owner.add_pet(pet)
    return owner


def show(title: str, tasks: Iterable[Task]) -> None:
    """Print a titled list of tasks."""
    print(f"\n{title}")
    for t in tasks:
        when = t.time or "flexible"
        print(f"  {when:<8} {t.pet_name:<8} {t.description:<14} {t.get_status():<9} due {t.due_date}")


def main() -> None:
    owner = build_owner()
    scheduler = Scheduler(owner)

    print("=" * 60)
    print(f"PawPal+ demo for {owner.name}")
    print("=" * 60)

    # Sorting: tasks were added out of order; sort_by_time fixes that.
    show("Sorted by time", scheduler.sort_by_time(scheduler.get_tasks()))

    # Filtering by pet and by status.
    show("Filter: Biscuit only (insertion order)", scheduler.get_tasks(pet_name="Biscuit"))
    show("Filter: Biscuit only, then sorted", scheduler.sort_by_time(scheduler.get_tasks(pet_name="Biscuit")))

    # Conflict detection: warn before building the plan.
    print("\nConflicts")
    for warning in scheduler.detect_conflicts() or ["none"]:
        print(f"  ! {warning}")

    # Plan: the lower-priority overlapping task should be skipped.
    plan = scheduler.build_plan()
    print("\nToday's plan")
    for start, task, reason in plan:
        print(f"  {start}  {task.pet_name:<8} {task.description:<14} {task.duration_minutes:>3} min  ({reason})")
    for task, reason in scheduler.skipped:
        print(f"  skipped: {task.pet_name} {task.description} - {reason}")

    # Recurring tasks: completing a daily/weekly task spawns the next occurrence.
    print("\nCompleting recurring tasks")
    for task in scheduler.get_tasks(completed=False):
        if task.frequency != "once":
            nxt = scheduler.mark_task_complete(task)
            print(f"  {task.pet_name} {task.description} ({task.frequency}) -> next due {nxt.due_date}")
    show("Filter: completed", scheduler.get_tasks(completed=True))
    show("Filter: pending (includes new recurrences)", scheduler.get_tasks(completed=False))


if __name__ == "__main__":
    main()
