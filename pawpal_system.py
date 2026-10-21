"""PawPal+ system classes (skeleton based on diagrams/uml_draft.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, grooming, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = ""
    preferred_time: str = ""  # e.g. "morning", "afternoon", "evening"
    frequency: str = "daily"  # e.g. "daily", "weekly"
    completed: bool = False

    def priority_score(self) -> int:
        """Return a numeric score for this task's priority."""
        pass

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_due_today(self) -> bool:
        """Return True if this task should be scheduled today."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a care task by its title."""
        pass

    def get_pending_tasks(self) -> List[Task]:
        """Return tasks that are not yet completed."""
        pass


@dataclass
class Owner:
    """A pet owner and their scheduling constraints."""

    name: str
    available_minutes: int = 0
    available_windows: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def set_availability(self, windows: List[str], minutes: int) -> None:
        """Set the owner's available time windows and total minutes."""
        pass

    def set_preference(self, key: str, value: str) -> None:
        """Set a single owner preference."""
        pass


class Scheduler:
    """Builds a daily care plan for a pet based on the owner's constraints."""

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.plan: List[Tuple[str, Task]] = []
        self.skipped: List[Task] = []

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered from highest to lowest priority."""
        pass

    def filter_by_constraints(self, tasks: List[Task]) -> List[Task]:
        """Return only the tasks that fit the owner's availability and preferences."""
        pass

    def detect_conflicts(self) -> List[str]:
        """Return warnings for overlapping or conflicting tasks in the plan."""
        pass

    def build_plan(self) -> List[Tuple[str, Task]]:
        """Build and return the daily plan as (start time, task) pairs."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why tasks were chosen or skipped."""
        pass
