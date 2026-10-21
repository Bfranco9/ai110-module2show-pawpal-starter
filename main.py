"""Demo script: builds an owner with two pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", available_minutes=120, day_start="07:00", day_end="21:00")

    mochi = Pet("Mochi", "dog", age=3)
    biscuit = Pet("Biscuit", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    mochi.add_task(Task("Morning walk", 30, "high", time="07:30", frequency="daily"))
    mochi.add_task(Task("Evening walk", 30, "medium", time="18:00", frequency="daily"))
    biscuit.add_task(Task("Feeding", 10, "high", time="08:15", frequency="daily"))
    biscuit.add_task(Task("Litter box", 10, "medium", time="12:00", frequency="daily"))
    biscuit.add_task(Task("Brushing", 15, "low"))

    scheduler = Scheduler(owner)
    plan = scheduler.build_plan()

    print("=" * 50)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 50)
    for start, task, reason in plan:
        print(f"{start}  {task.pet_name:<8} {task.description:<14} {task.duration_minutes:>3} min  [{task.priority}]")
        print(f"       why: {reason}")

    if scheduler.skipped:
        print("\nSkipped:")
        for task, reason in scheduler.skipped:
            print(f"  {task.pet_name}: {task.description} - {reason}")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nConflicts:")
        for warning in conflicts:
            print(f"  ! {warning}")


if __name__ == "__main__":
    main()
