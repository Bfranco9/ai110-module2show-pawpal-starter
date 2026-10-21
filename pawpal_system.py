"""PawPal+ system classes: Task, Pet, Owner, and Scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}


def to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight to an "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, grooming, etc.)."""

    description: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    time: str = ""  # fixed start time "HH:MM", or "" if flexible
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""  # set by Pet.add_task

    def priority_score(self) -> int:
        """Return a numeric score for this task's priority (unknown values count as low)."""
        return PRIORITY_SCORES.get(self.priority.lower(), 1)

    def is_due_today(self, today: Optional[date] = None) -> bool:
        """Return True if this task is not completed and is due on or before today."""
        today = today or date.today()
        return not self.completed and self.due_date <= today

    def mark_complete(self) -> Optional[Task]:
        """Mark this task completed and return the next occurrence if it recurs."""
        self.completed = True
        days = FREQUENCY_DAYS.get(self.frequency)
        if days is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + timedelta(days=days))


@dataclass
class Pet:
    """A pet's details and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the first task matching the description; return True if one was removed."""
        for task in self.tasks:
            if task.description == description:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> List[Task]:
        """Return tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """A pet owner who manages multiple pets and their scheduling constraints."""

    name: str
    available_minutes: int = 120
    day_start: str = "08:00"
    day_end: str = "20:00"
    preferences: Dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def set_availability(self, day_start: str, day_end: str, minutes: int) -> None:
        """Set the owner's daily time window and total minutes available for care."""
        self.day_start = day_start
        self.day_end = day_end
        self.available_minutes = minutes

    def set_preference(self, key: str, value: str) -> None:
        """Set a single owner preference."""
        self.preferences[key] = value

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


# A scheduled entry: (start "HH:MM", task, reason it was chosen)
PlanEntry = Tuple[str, Task, str]


class Scheduler:
    """The "brain": retrieves, organizes, and plans tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner with an empty plan and skipped list."""
        self.owner: Owner = owner
        self.plan: List[PlanEntry] = []
        self.skipped: List[Tuple[Task, str]] = []

    def get_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return the owner's tasks, optionally filtered by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by priority (high first), then fixed-time first, then shortest."""
        return sorted(tasks, key=lambda t: (-t.priority_score(), t.time == "", t.duration_minutes))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by fixed start time; flexible tasks go last."""
        return sorted(tasks, key=lambda t: (t.time == "", t.time))

    def filter_by_constraints(self, tasks: List[Task], today: Optional[date] = None) -> List[Task]:
        """Keep only tasks due today whose fixed time (if any) falls inside the owner's day."""
        start, end = to_minutes(self.owner.day_start), to_minutes(self.owner.day_end)
        kept = []
        for task in tasks:
            if not task.is_due_today(today):
                continue
            if task.time and not (start <= to_minutes(task.time) and to_minutes(task.time) + task.duration_minutes <= end):
                self.skipped.append((task, f"{task.time} is outside your {self.owner.day_start}-{self.owner.day_end} window"))
                continue
            kept.append(task)
        return kept

    def detect_conflicts(self, today: Optional[date] = None) -> List[str]:
        """Return warnings for fixed-time tasks due today that overlap, across all pets."""
        timed = self.sort_by_time([t for t in self.owner.get_all_tasks() if t.time and t.is_due_today(today)])
        warnings = []
        for i, first in enumerate(timed):
            first_end = to_minutes(first.time) + first.duration_minutes
            for second in timed[i + 1:]:
                if to_minutes(second.time) >= first_end:
                    break
                warnings.append(
                    f"{first.pet_name}'s '{first.description}' at {first.time} overlaps "
                    f"{second.pet_name}'s '{second.description}' at {second.time}"
                )
        return warnings

    def build_plan(self, today: Optional[date] = None) -> List[PlanEntry]:
        """Build today's plan: filter, sort by priority, fit into the time budget, assign start times."""
        self.plan, self.skipped = [], []
        day_start, day_end = to_minutes(self.owner.day_start), to_minutes(self.owner.day_end)
        busy: List[Tuple[int, int]] = []
        minutes_left = self.owner.available_minutes

        candidates = self.sort_by_priority(self.filter_by_constraints(self.owner.get_all_tasks(), today))
        for task in candidates:
            if task.duration_minutes > minutes_left:
                self.skipped.append((task, f"not enough time left ({minutes_left} min remaining)"))
                continue

            if task.time:
                start = to_minutes(task.time)
                if not self._is_free(busy, start, task.duration_minutes):
                    self.skipped.append((task, f"conflicts with a higher-priority task at {task.time}"))
                    continue
                reason = f"{task.priority} priority, fixed at {task.time}"
            else:
                start = self._find_open_slot(busy, day_start, day_end, task.duration_minutes)
                if start is None:
                    self.skipped.append((task, "no open slot left in your day"))
                    continue
                reason = f"{task.priority} priority, placed in the earliest open slot"

            busy.append((start, start + task.duration_minutes))
            minutes_left -= task.duration_minutes
            self.plan.append((to_hhmm(start), task, reason))

        self.plan.sort(key=lambda entry: entry[0])
        return self.plan

    def explain_plan(self) -> str:
        """Return a human-readable explanation of what was scheduled and what was skipped."""
        if not self.plan and not self.skipped:
            self.build_plan()
        lines = [f"Daily plan for {self.owner.name}:"]
        for start, task, reason in self.plan:
            lines.append(f"  {start} - {task.pet_name}: {task.description} ({task.duration_minutes} min) - {reason}")
        if self.skipped:
            lines.append("Skipped:")
            for task, reason in self.skipped:
                lines.append(f"  {task.pet_name}: {task.description} - {reason}")
        return "\n".join(lines)

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add its next occurrence to the same pet."""
        next_task = task.mark_complete()
        pet = self.owner.get_pet(task.pet_name)
        if next_task is not None and pet is not None:
            pet.add_task(next_task)
        return next_task

    @staticmethod
    def _is_free(busy: List[Tuple[int, int]], start: int, duration: int) -> bool:
        """Return True if [start, start + duration) doesn't overlap any busy interval."""
        end = start + duration
        return all(end <= b_start or start >= b_end for b_start, b_end in busy)

    def _find_open_slot(self, busy: List[Tuple[int, int]], day_start: int, day_end: int, duration: int) -> Optional[int]:
        """Return the earliest start time where the task fits before day_end, or None."""
        candidate = day_start
        for b_start, b_end in sorted(busy):
            if candidate + duration <= b_start:
                return candidate
            candidate = max(candidate, b_end)
        return candidate if candidate + duration <= day_end else None
