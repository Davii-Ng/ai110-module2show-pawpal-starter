from datetime import datetime, time
from pawpal_systems import Owner, Pet, Task, Scheduler, TimeWindow


def today_at(hour: int, minute: int = 0) -> datetime:
    now = datetime.now()
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def main() -> None:
    owner = Owner(name="Alice")

    # create two pets
    dog = Pet(name="Fido")
    cat = Pet(name="Whiskers")
    owner.pet_ids.extend([dog.id, cat.id])

    # tasks for pets (different times)
    walk = Task(
        type="Walk",
        duration_minutes=30,
        priority=3,
        pet_id=dog.id,
        earliest_time=today_at(9),
        latest_time=today_at(11),
        description="Morning walk for energy",
    )

    feed = Task(
        type="Feeding",
        duration_minutes=15,
        priority=2,
        pet_id=cat.id,
        earliest_time=today_at(12),
        latest_time=today_at(13),
        description="Lunchtime feeding",
    )

    meds = Task(
        type="Medication",
        duration_minutes=10,
        priority=5,
        pet_id=dog.id,
        earliest_time=today_at(17),
        latest_time=today_at(18),
        description="Evening medication",
    )

    # attach tasks to pets
    dog.add_task(walk)
    dog.add_task(meds)
    cat.add_task(feed)

    tasks = [walk, feed, meds]
    pets = [dog, cat]

    # day window (6:00 - 20:00)
    window = TimeWindow(start=today_at(6), end=today_at(20))

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner, pets, tasks, day_window=window)

    print("Today's Schedule:\n")
    if not schedule:
        print("  No scheduled items.")
        return

    # display schedule in chronological order
    schedule = sorted([s for s in schedule if s.scheduled_start], key=lambda e: e.scheduled_start)
    for e in schedule:
        task = next((t for t in tasks if t.id == e.task_id), None)
        label = task.type if task else f"Task {e.task_id}"
        pet_name = next((p.name for p in pets if p.id == (task.pet_id if task else None)), "Unknown")
        start = e.scheduled_start.strftime("%Y-%m-%d %H:%M")
        end = e.scheduled_end.strftime("%H:%M") if e.scheduled_end else "-"
        print(f"  {start} - {end}: {label} for {pet_name}")


if __name__ == "__main__":
    main()
