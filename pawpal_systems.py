
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import itertools
from datetime import timedelta


# Simple ID manager for auto-increment integer IDs. Use `IDManager.next_id()` to
# obtain a new unique integer ID within this process. This keeps the models
# convenient for tests and for usage from `app.py` without manual id bookkeeping.
class IDManager:
	_counter = itertools.count(1)

	@classmethod
	def next_id(cls) -> int:
		"""Return the next auto-increment integer ID."""
		return next(cls._counter)


@dataclass
class TimeWindow:
	# Use full datetimes for start/end so scheduling can be date-aware and
	# consistent with Task.earliest_time / Pet.pickup_time (which are
	# datetimes). For recurring daily windows a separate representation can be
	# added later.
	start: datetime
	end: datetime


@dataclass
class Owner:
	id: Optional[int] = None
	name: str = ""
	phone: Optional[str] = None
	email: Optional[str] = None
	availability: List[TimeWindow] = field(default_factory=list)
	pet_ids: List[int] = field(default_factory=list)

	def __post_init__(self) -> None:
		"""Auto-assign an ID to the owner if none was provided."""
		if self.id is None:
			self.id = IDManager.next_id()


@dataclass
class Pet:
	id: Optional[int] = None
	name: str = ""
	species: Optional[str] = None
	pickup_time: Optional[datetime] = None
	notes: Optional[str] = None
	task_ids: List[int] = field(default_factory=list)

	def __post_init__(self) -> None:
		"""Auto-assign an ID to the pet if none was provided."""
		if self.id is None:
			self.id = IDManager.next_id()

	# Keep explicit Task objects on the Pet for convenience in the app.
	tasks: List["Task"] = field(default_factory=list)

	def add_task(self, task: "Task") -> None:
		"""Attach a Task object to this Pet and record its id."""
		if task.id is None:
			task.__post_init__()
		self.tasks.append(task)
		if task.id not in self.task_ids:
			self.task_ids.append(task.id)

	def remove_task(self, task_id: int) -> bool:
		"""Remove a Task by id; return True if removed."""
		removed = False
		self.tasks = [t for t in self.tasks if not (removed := (t.id == task_id))]
		if task_id in self.task_ids:
			self.task_ids.remove(task_id)
		return removed

	def get_tasks(self) -> List["Task"]:
		"""Return a copy of this pet's Task list."""
		return list(self.tasks)

	def pending_tasks(self) -> List["Task"]:
		"""Return tasks for this pet that are not completed."""
		return [t for t in self.tasks if not getattr(t, "completed", False)]


@dataclass
class Task:
	id: Optional[int] = None
	type: str = ""
	duration_minutes: int = 0
	priority: int = 1
	price: Optional[float] = None
	pet_id: Optional[int] = None
	earliest_time: Optional[datetime] = None
	latest_time: Optional[datetime] = None
	recurring: bool = False
	# frequency_days: how many days between repeats for recurring tasks
	frequency_days: Optional[int] = None
	# optional human-friendly description
	description: Optional[str] = None
	# completion flag
	completed: bool = False

	def __post_init__(self) -> None:
		"""Auto-assign an ID to the task if none was provided."""
		if self.id is None:
			self.id = IDManager.next_id()

	def mark_complete(self) -> None:
		"""Mark this task as completed."""
		self.completed = True

	def is_due(self, at: Optional[datetime] = None) -> bool:
		"""Return True if the task is currently due (not completed and within window)."""
		now = at or datetime.now()
		if self.completed:
			return False
		if self.earliest_time and now < self.earliest_time:
			return False
		if self.latest_time and now > self.latest_time:
			return False
		return True

	def next_occurrence(self, after: Optional[datetime] = None) -> Optional[datetime]:
		"""Compute the next occurrence datetime for a recurring task."""
		if not self.recurring or not self.frequency_days:
			return self.earliest_time
		ref = after or (self.earliest_time or datetime.now())
		if self.earliest_time and ref < self.earliest_time:
			return self.earliest_time
		# compute next by advancing in frequency_days steps until > ref
		next_dt = self.earliest_time or ref
		while next_dt <= ref:
			next_dt = next_dt + timedelta(days=self.frequency_days)
		return next_dt


@dataclass
class ScheduleEntry:
	id: Optional[int] = None
	task_id: int = -1
	scheduled_start: Optional[datetime] = None
	scheduled_end: Optional[datetime] = None
	reason: Optional[str] = None

	def __post_init__(self) -> None:
		"""Auto-assign an ID to the schedule entry if absent."""
		if self.id is None:
			self.id = IDManager.next_id()


class Scheduler:
	"""Scheduler skeleton: implement scheduling algorithms here.

	Public methods are started as stubs so `app.py` can call them later.
	"""

	def __init__(self) -> None:
		"""Create a Scheduler with an in-memory schedule index."""
		# lightweight in-memory index (not persisted)
		self._entries: List[ScheduleEntry] = []

	def generate_schedule(self, owner: Owner, pets: List[Pet], tasks: List[Task], day_window: Optional[TimeWindow] = None) -> List[ScheduleEntry]:
		"""Generate schedule entries for the provided owner, pets, and tasks."""
		# Simple greedy scheduler:
		# - collect all incomplete tasks
		# - respect earliest/latest and the optional day_window
		# - sort by priority (higher first), then by earliest_time
		entries: List[ScheduleEntry] = []

		window_start = day_window.start if day_window else None
		window_end = day_window.end if day_window else None

		cand = [t for t in tasks if not getattr(t, "completed", False)]
		# Prefer scheduling tasks by their earliest allowed time first,
		# then by higher priority to break ties. This prevents late high-
		# priority tasks from blocking earlier low-priority tasks.
		def sort_key(t: Task):
			return (t.earliest_time or datetime.min, -t.priority)

		cand.sort(key=sort_key)

		cursor = window_start or (cand[0].earliest_time if cand and cand[0].earliest_time else datetime.now())
		for t in cand:
			start = max(cursor, t.earliest_time) if t.earliest_time else cursor
			if window_start and start < window_start:
				start = window_start
			end = start + timedelta(minutes=t.duration_minutes)
			# respect latest_time and window_end
			if t.latest_time and end > t.latest_time:
				entries.append(ScheduleEntry(task_id=t.id, scheduled_start=None, scheduled_end=None, reason="cannot meet latest_time"))
				continue
			if window_end and end > window_end:
				entries.append(ScheduleEntry(task_id=t.id, scheduled_start=None, scheduled_end=None, reason="outside day window"))
				continue
			entry = ScheduleEntry(task_id=t.id, scheduled_start=start, scheduled_end=end)
			entries.append(entry)
			cursor = end

		# save entries in-memory index
		self._entries = entries
		return entries

	def explain(self, schedule: List[ScheduleEntry]) -> Dict[int, str]:
		"""Produce human-readable explanations for each schedule entry.

		Returns a mapping from ScheduleEntry.id -> explanation string.
		"""
		explanations: Dict[int, str] = {}
		for e in schedule:
			if e.scheduled_start and e.scheduled_end:
				explanations[e.id] = f"Task {e.task_id} scheduled {e.scheduled_start.isoformat()} - {e.scheduled_end.isoformat()}"
			else:
				explanations[e.id] = f"Task {e.task_id} not scheduled: {e.reason or 'no reason provided'}"
		return explanations


__all__ = [
	"IDManager",
	"TimeWindow",
	"Owner",
	"Pet",
	"Task",
	"ScheduleEntry",
	"Scheduler",
]

