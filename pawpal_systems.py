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
	# optional recurrence string: 'daily', 'weekly' (preferred over frequency_days when set)
	recurrence: Optional[str] = None
	# optional human-friendly description
	description: Optional[str] = None
	# completion flag
	completed: bool = False

	def __post_init__(self) -> None:
		"""Auto-assign an ID to the task if none was provided."""
		if self.id is None:
			self.id = IDManager.next_id()

	def mark_complete(self, at: Optional[datetime] = None) -> Optional["Task"]:
		"""Mark this task as completed.

		If the task is recurring (`recurrence` or `frequency_days` set) a new
		Task instance for the next occurrence will be returned (and the caller
		is responsible for persisting/attaching it). Returns the new Task or
		`None` if no follow-up is created.
		"""
		now = at or datetime.now()
		self.completed = True

		# determine effective frequency in days
		freq = None
		if self.recurrence:
			if self.recurrence.lower() == "daily":
				freq = 1
			elif self.recurrence.lower() == "weekly":
				freq = 7
		# frequency_days takes precedence if explicitly set
		if self.frequency_days:
			freq = self.frequency_days

		if not self.recurring or not freq:
			return None

		# compute the next earliest_time as now + freq days (use timedelta)
		next_dt = now + timedelta(days=freq)

		# compute a corresponding latest_time offset if we have one
		new_latest = None
		if self.earliest_time and self.latest_time:
			delta = self.latest_time - self.earliest_time
			new_latest = next_dt + delta

		new_task = Task(
			id=None,
			type=self.type,
			duration_minutes=self.duration_minutes,
			priority=self.priority,
			price=self.price,
			pet_id=self.pet_id,
			earliest_time=next_dt,
			latest_time=new_latest,
			recurring=self.recurring,
			frequency_days=self.frequency_days,
			recurrence=self.recurrence,
			description=self.description,
			completed=False,
		)
		return new_task

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
		"""Compute the next occurrence datetime for a recurring task.

		If the task is non-recurring this returns `earliest_time`.
		If `after` is provided, the first occurrence strictly after that
		datetime is returned. If no valid occurrence exists (e.g. frequency
		not set) returns None.
		"""
		# determine frequency: prefer explicit frequency_days, otherwise map recurrence
		freq_days = self.frequency_days
		if not freq_days and self.recurrence:
			if self.recurrence.lower() == "daily":
				freq_days = 1
			elif self.recurrence.lower() == "weekly":
				freq_days = 7
		if not self.recurring or not freq_days:
			# non-recurring or missing frequency: single occurrence semantics
			if self.earliest_time is None:
				return None
			if after and self.earliest_time <= after:
				return None
			return self.earliest_time

		if freq_days <= 0:
			return None

		ref = after or (self.earliest_time or datetime.now())

		# earliest occurrence anchor
		start = self.earliest_time or ref
		if ref < start:
			return start

		# compute seconds-based step and jump by arithmetic (avoids loops)
		step_secs = freq_days * 86400
		diff_secs = (ref - start).total_seconds()
		# number of steps to advance to be strictly > ref
		steps = int(diff_secs // step_secs) + 1
		return start + timedelta(days=steps * freq_days)

	def occurrences_between(self, start: datetime, end: datetime) -> List[datetime]:
		"""Return all occurrence datetimes within [start, end]."""
		results: List[datetime] = []
		if not self.recurring or not self.frequency_days:
			if self.earliest_time and start <= self.earliest_time <= end:
				results.append(self.earliest_time)
			return results

		# find first occurrence >= start
		occ = self.next_occurrence(after=start - timedelta(days=self.frequency_days or 1))
		while occ and occ <= end:
			results.append(occ)
			occ = occ + timedelta(days=self.frequency_days)
		return results


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

	def mark_task_complete(self, task: Task, pets: List[Pet], tasks: List[Task], at: Optional[datetime] = None) -> Optional[Task]:
		"""Mark `task` complete, and if recurring create the next occurrence.

		The new Task (if any) is appended to `tasks` and attached to the
		corresponding `Pet` in `pets` via `Pet.add_task()`.
		Returns the new Task or None.
		"""
		new_task = task.mark_complete(at=at)
		if not new_task:
			return None
		# persist: add to global tasks list and attach to pet object if present
		tasks.append(new_task)
		# attach to pet if pet object exists
		if new_task.pet_id is not None:
			pet = next((p for p in pets if p.id == new_task.pet_id), None)
			if pet:
				pet.add_task(new_task)
		return new_task

	def filter_tasks(self, tasks: List[Task], pet_id: Optional[int] = None, completed: Optional[bool] = None) -> List[Task]:
		"""Return tasks filtered by `pet_id` and/or `completed` status."""
		res = tasks
		if pet_id is not None:
			res = [t for t in res if t.pet_id == pet_id]
		if completed is not None:
			res = [t for t in res if bool(t.completed) is bool(completed)]
		return res

	def filter_tasks_by_pet_name(self, tasks: List[Task], pets: List[Pet], pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
		"""Filter tasks by pet name and/or completion flag.

		Args:
			tasks: list of Task objects to filter.
			pets: list of Pet objects (used to resolve names to ids).
			pet_name: optional case-insensitive pet name to match. If None no
				pet-name filtering is applied.
			completed: optional completion flag to filter by.

		Returns:
			A list of Task objects that match the provided filters.
		"""
		if pet_name is None and completed is None:
			return list(tasks)
		res = tasks
		if pet_name is not None:
			# find matching pet ids
			matching_ids = {p.id for p in pets if p.name.lower() == pet_name.lower()}
			res = [t for t in res if t.pet_id in matching_ids]
		if completed is not None:
			res = [t for t in res if bool(t.completed) is bool(completed)]
		return res

	def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
		"""Stable sort of tasks by earliest occurrence time then by priority.

		Recurring tasks are ordered by their next occurrence (if any).
		"""
		def key(t: Task):
			next_dt = None
			if t.recurring:
				next_dt = t.next_occurrence()
			else:
				next_dt = t.earliest_time
			# treat None as far past so tasks without time sort last
			return ((next_dt or datetime.max), -t.priority)
		return sorted(tasks, key=key)

	# convenience alias requested by callers
	def sort_by_time(self, tasks: List[Task]) -> List[Task]:
		"""Sort tasks by their next occurrence or a short `time_str`.

		This helper prefers `earliest_time` when present. If a task exposes a
		`time_str` attribute in "HH:MM" format it will be parsed into today's
		wall time for ordering. Tasks without any time information sort last.

		Returns a new list of tasks sorted from earliest to latest.
		"""
		# support tasks that may carry a `time_str` attribute
		def adapt_key(t: Task):
			# prefer earliest_time if available
			if getattr(t, "earliest_time", None):
				return (t.earliest_time, -t.priority)
			# try time_str
			time_str = getattr(t, "time_str", None)
			if isinstance(time_str, str):
				try:
					hh, mm = time_str.split(":")
					tm = datetime.now().replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
					return (tm, -t.priority)
				except Exception:
					pass
			# fallback
			return (datetime.max, -t.priority)
		return sorted(tasks, key=adapt_key)

	def find_conflicts(self, schedule: List[ScheduleEntry]) -> List[tuple]:
		"""Return list of (entry1, entry2) pairs that overlap."""
		pairs: List[tuple] = []
		# consider only scheduled entries
		scheduled = [e for e in schedule if e.scheduled_start and e.scheduled_end]
		scheduled.sort(key=lambda e: e.scheduled_start)
		for a, b in zip(scheduled, scheduled[1:]):
			if a.scheduled_end > b.scheduled_start:
				pairs.append((a, b))
		return pairs

	def detect_conflicts(self, schedule: List[ScheduleEntry], tasks: List[Task], pets: List[Pet]) -> List[str]:
		"""Detect overlapping scheduled entries and return warnings.

		This is a lightweight, non-fatal detector: it scans scheduled entries in
		start-time order and for any overlapping pair produces a short human-
		readable warning string instead of throwing an exception.

		Args:
			schedule: list of ScheduleEntry objects produced by `generate_schedule`.
			tasks: list of Task objects (used to convert ids to labels).
			pets: list of Pet objects (used to convert pet ids to names).

		Returns:
			A list of warning strings describing each detected overlap.
		"""
		warnings: List[str] = []
		# only consider entries that have concrete scheduled times
		scheduled = [e for e in schedule if e.scheduled_start and e.scheduled_end]
		# sort by start time
		scheduled.sort(key=lambda e: e.scheduled_start)
		for i in range(len(scheduled)):
			a = scheduled[i]
			for b in scheduled[i+1:]:
				# if the next entry starts at/after a ends we can break the inner loop
				if b.scheduled_start >= a.scheduled_end:
					break
				# overlap detected
				t1 = next((t for t in tasks if t.id == a.task_id), None)
				t2 = next((t for t in tasks if t.id == b.task_id), None)
				p1 = next((p for p in pets if p.id == (t1.pet_id if t1 else None)), None)
				p2 = next((p for p in pets if p.id == (t2.pet_id if t2 else None)), None)
				when = max(a.scheduled_start, b.scheduled_start).strftime("%Y-%m-%d %H:%M")
				label1 = f"{t1.type} (task {t1.id})" if t1 else f"Task {a.task_id}"
				label2 = f"{t2.type} (task {t2.id})" if t2 else f"Task {b.task_id}"
				pet_label1 = p1.name if p1 else "Unknown"
				pet_label2 = p2.name if p2 else "Unknown"
				warnings.append(f"Conflict at {when}: {label1} for {pet_label1} overlaps {label2} for {pet_label2}")
		return warnings

	def generate_schedule(self, owner: Owner, pets: List[Pet], tasks: List[Task], day_window: Optional[TimeWindow] = None) -> List[ScheduleEntry]:
		"""Generate schedule entries for the provided owner, pets, and tasks."""
		# Simple greedy scheduler:
		# - collect all incomplete tasks
		# - respect earliest/latest and the optional day_window
		# - sort by priority (higher first), then by earliest_time
		entries: List[ScheduleEntry] = []

		window_start = day_window.start if day_window else None
		window_end = day_window.end if day_window else None

		# consider only incomplete tasks
		cand = [t for t in tasks if not getattr(t, "completed", False)]

		# expand recurring tasks to their next occurrence within the window
		expanded: List[Task] = []
		for t in cand:
			if t.recurring:
				# compute next occurrence relative to window_start (or now)
				ref = window_start or datetime.now()
				next_dt = t.next_occurrence(after=ref - timedelta(days=t.frequency_days or 1))
				if next_dt is None:
					# no upcoming occurrence
					continue
				# clone lightweight view for scheduling: don't mutate original task
				s = Task(
					id=t.id,
					type=t.type,
					duration_minutes=t.duration_minutes,
					priority=t.priority,
					price=t.price,
					pet_id=t.pet_id,
					earliest_time=next_dt,
					latest_time=t.latest_time,
					recurring=t.recurring,
					frequency_days=t.frequency_days,
					description=t.description,
					completed=t.completed,
				)
				expanded.append(s)
			else:
				expanded.append(t)

		# sort by earliest_time then by priority (higher priority first)
		def sort_key(t: Task):
			return (t.earliest_time or datetime.min, -t.priority)

		expanded.sort(key=sort_key)

		# initialize cursor to the start of the day window or the first task's earliest
		cursor = window_start or (expanded[0].earliest_time if expanded and expanded[0].earliest_time else datetime.now())
		for t in expanded:
			start = max(cursor, t.earliest_time) if t.earliest_time else cursor
			if window_start and start < window_start:
				start = window_start
			end = start + timedelta(minutes=t.duration_minutes)
			# try first-fit if overlapping previous entries
			if entries and entries[-1].scheduled_end and start < entries[-1].scheduled_end:
				start = entries[-1].scheduled_end
				end = start + timedelta(minutes=t.duration_minutes)
			# respect latest_time and window_end
			if t.latest_time and end > t.latest_time:
				entries.append(ScheduleEntry(task_id=t.id, scheduled_start=None, scheduled_end=None, reason="cannot meet latest_time"))
				continue
			if window_end and end > window_end:
				entries.append(ScheduleEntry(task_id=t.id, scheduled_start=None, scheduled_end=None, reason="outside day window"))
				continue
			# if still overlapping after first-fit attempt, mark conflict
			conflict = False
			for e in entries:
				if e.scheduled_start and e.scheduled_end and not (end <= e.scheduled_start or start >= e.scheduled_end):
					conflict = True
					break
			if conflict:
				entries.append(ScheduleEntry(task_id=t.id, scheduled_start=None, scheduled_end=None, reason=f"conflict with task {e.task_id}"))
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

