
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import itertools


# Simple ID manager for auto-increment integer IDs. Use `IDManager.next_id()` to
# obtain a new unique integer ID within this process. This keeps the models
# convenient for tests and for usage from `app.py` without manual id bookkeeping.
class IDManager:
	_counter = itertools.count(1)

	@classmethod
	def next_id(cls) -> int:
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
		if self.id is None:
			self.id = IDManager.next_id()


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

	def __post_init__(self) -> None:
		if self.id is None:
			self.id = IDManager.next_id()


@dataclass
class ScheduleEntry:
	id: Optional[int] = None
	task_id: int = -1
	scheduled_start: Optional[datetime] = None
	scheduled_end: Optional[datetime] = None
	reason: Optional[str] = None

	def __post_init__(self) -> None:
		if self.id is None:
			self.id = IDManager.next_id()


class Scheduler:
	"""Scheduler skeleton: implement scheduling algorithms here.

	Public methods are started as stubs so `app.py` can call them later.
	"""

	def __init__(self) -> None:
		pass

	def generate_schedule(self, owner: Owner, pets: List[Pet], tasks: List[Task], day_window: Optional[TimeWindow] = None) -> List[ScheduleEntry]:
		"""Generate a list of ScheduleEntry objects for the given owner, pets and tasks.

		This is a stub. Implement a heuristic or constraint solver to respect
		priorities, durations, and time windows.
		"""
		raise NotImplementedError()

	def explain(self, schedule: List[ScheduleEntry]) -> Dict[int, str]:
		"""Produce human-readable explanations for each schedule entry.

		Returns a mapping from ScheduleEntry.id -> explanation string.
		"""
		raise NotImplementedError()


__all__ = [
	"IDManager",
	"TimeWindow",
	"Owner",
	"Pet",
	"Task",
	"ScheduleEntry",
	"Scheduler",
]

