
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional, Dict


@dataclass
class TimeWindow:
	start: time
	end: time


@dataclass
class Owner:
	id: int
	name: str
	phone: Optional[str] = None
	email: Optional[str] = None
	availability: List[TimeWindow] = field(default_factory=list)
	pet_ids: List[int] = field(default_factory=list)


@dataclass
class Pet:
	id: int
	name: str
	species: Optional[str] = None
	pickup_time: Optional[datetime] = None
	notes: Optional[str] = None
	task_ids: List[int] = field(default_factory=list)


@dataclass
class Task:
	id: int
	type: str
	duration_minutes: int
	priority: int = 1
	price: Optional[float] = None
	pet_id: Optional[int] = None
	earliest_time: Optional[datetime] = None
	latest_time: Optional[datetime] = None
	recurring: bool = False


@dataclass
class ScheduleEntry:
	id: int
	task_id: int
	scheduled_start: Optional[datetime] = None
	scheduled_end: Optional[datetime] = None
	reason: Optional[str] = None


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


__all__ = ["TimeWindow", "Owner", "Pet", "Task", "ScheduleEntry", "Scheduler"]

