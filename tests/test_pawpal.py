from datetime import datetime, timedelta

from pawpal_systems import Owner, Pet, ScheduleEntry, Scheduler, Task, TimeWindow


def test_task_mark_complete():
    t = Task(type="Test", duration_minutes=5)
    assert not t.completed
    t.mark_complete()
    assert t.completed


def test_pet_add_task_increases_count():
    p = Pet(name="Buddy")
    initial = len(p.get_tasks())
    t = Task(type="Feeding", duration_minutes=10)
    p.add_task(t)
    assert len(p.get_tasks()) == initial + 1
    assert t.id in p.task_ids


def test_sorting_correctness_returns_chronological_order():
    scheduler = Scheduler()
    base = datetime(2026, 1, 1, 8, 0)

    t_late = Task(type="Walk", duration_minutes=30, earliest_time=base + timedelta(hours=2))
    t_mid = Task(type="Feed", duration_minutes=10, earliest_time=base + timedelta(hours=1))
    t_early = Task(type="Meds", duration_minutes=5, earliest_time=base)

    sorted_tasks = scheduler.sort_tasks_by_time([t_late, t_mid, t_early])
    assert [t.id for t in sorted_tasks] == [t_early.id, t_mid.id, t_late.id]


def test_recurrence_daily_task_creates_next_day_on_complete():
    completed_at = datetime(2026, 1, 1, 9, 0)
    daily = Task(
        type="Daily walk",
        duration_minutes=20,
        recurring=True,
        recurrence="daily",
    )

    next_task = daily.mark_complete(at=completed_at)

    assert daily.completed is True
    assert next_task is not None
    assert next_task.earliest_time == completed_at + timedelta(days=1)
    assert next_task.completed is False


def test_conflict_detection_flags_duplicate_times():
    scheduler = Scheduler()
    owner = Owner(name="Nora")
    pet1 = Pet(name="Buddy")
    pet2 = Pet(name="Milo")

    t1 = Task(type="Walk", duration_minutes=30, pet_id=pet1.id)
    t2 = Task(type="Feeding", duration_minutes=15, pet_id=pet2.id)

    start = datetime(2026, 1, 1, 10, 0)
    end = datetime(2026, 1, 1, 10, 30)
    schedule = [
        ScheduleEntry(task_id=t1.id, scheduled_start=start, scheduled_end=end),
        ScheduleEntry(task_id=t2.id, scheduled_start=start, scheduled_end=end),
    ]

    warnings = scheduler.detect_conflicts(schedule, [t1, t2], [pet1, pet2])
    assert warnings


def test_generate_schedule_with_no_tasks_returns_empty_list():
    scheduler = Scheduler()
    owner = Owner(name="Nora")

    entries = scheduler.generate_schedule(owner, pets=[], tasks=[])

    assert entries == []


def test_generate_schedule_marks_unscheduled_when_latest_time_missed():
    scheduler = Scheduler()
    owner = Owner(name="Nora")
    pet = Pet(name="Buddy")

    earliest = datetime(2026, 1, 1, 9, 0)
    latest = datetime(2026, 1, 1, 9, 10)
    task = Task(
        type="Long walk",
        duration_minutes=30,
        pet_id=pet.id,
        earliest_time=earliest,
        latest_time=latest,
    )

    entries = scheduler.generate_schedule(owner, [pet], [task])

    assert len(entries) == 1
    assert entries[0].scheduled_start is None
    assert entries[0].reason == "cannot meet latest_time"


def test_generate_schedule_marks_unscheduled_outside_day_window():
    scheduler = Scheduler()
    owner = Owner(name="Nora")
    pet = Pet(name="Buddy")

    day_window = TimeWindow(
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )
    task = Task(
        type="Grooming",
        duration_minutes=30,
        pet_id=pet.id,
        earliest_time=datetime(2026, 1, 1, 9, 45),
        latest_time=datetime(2026, 1, 1, 11, 0),
    )

    entries = scheduler.generate_schedule(owner, [pet], [task], day_window=day_window)

    assert len(entries) == 1
    assert entries[0].scheduled_start is None
    assert entries[0].reason == "outside day window"


def test_generate_schedule_skips_completed_tasks():
    scheduler = Scheduler()
    owner = Owner(name="Nora")
    pet = Pet(name="Buddy")
    base = datetime(2026, 1, 1, 8, 0)

    completed_task = Task(
        type="Completed feed",
        duration_minutes=10,
        pet_id=pet.id,
        earliest_time=base,
        latest_time=base + timedelta(hours=1),
        completed=True,
    )
    pending_task = Task(
        type="Pending meds",
        duration_minutes=5,
        pet_id=pet.id,
        earliest_time=base + timedelta(minutes=15),
        latest_time=base + timedelta(hours=1),
    )

    entries = scheduler.generate_schedule(owner, [pet], [completed_task, pending_task])

    assert len(entries) == 1
    assert entries[0].task_id == pending_task.id
    assert entries[0].scheduled_start is not None


def test_sort_by_time_puts_invalid_time_str_last():
    scheduler = Scheduler()
    base = datetime(2026, 1, 1, 8, 0)

    timed = Task(type="Walk", duration_minutes=20, earliest_time=base)
    malformed = Task(type="Feed", duration_minutes=10)
    setattr(malformed, "time_str", "not-a-time")

    sorted_tasks = scheduler.sort_by_time([malformed, timed])

    assert sorted_tasks[0].id == timed.id
    assert sorted_tasks[-1].id == malformed.id
