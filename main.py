from datetime import datetime, time
from pawpal_systems import Owner, Pet, Task, Scheduler, TimeWindow


def today_at(hour: int, minute: int = 0) -> datetime:
    now = datetime.now()
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def main() -> None:
    owner = Owner(name="Alice")

    pets: List[Pet] = []
    tasks: List[Task] = []

    # create up to 5 pets, each with 3 activities at different times
    activity_types = ["Walk", "Feeding", "Grooming"]
    base_hours = [8, 12, 17]
    for i in range(5):
        pet = Pet(name=f"Pet{i+1}")
        pets.append(pet)
        owner.pet_ids.append(pet.id)

        for j, act in enumerate(activity_types):
            hour = base_hours[j] + (i % 3)  # small stagger by pet
            t = Task(
                type=act,
                duration_minutes=15 + (5 * j),
                priority=3 - j,  # vary priority
                pet_id=pet.id,
                earliest_time=today_at(hour),
                latest_time=today_at(hour + 1),
                description=f"{act} for {pet.name}",
            )
            pet.add_task(t)
            tasks.append(t)

    # day window (6:00 - 20:00)
    window = TimeWindow(start=today_at(6), end=today_at(20))

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner, pets, tasks, day_window=window)

    print("Today's Schedule:\n")

    scheduled = sorted([s for s in schedule if s.scheduled_start], key=lambda e: e.scheduled_start)
    unscheduled = [s for s in schedule if not s.scheduled_start]

    print("Scheduled:")
    if not scheduled:
        print("  (none)")
    else:
        for i, e in enumerate(scheduled, start=1):
            task = next((t for t in tasks if t.id == e.task_id), None)
            label = task.type if task else f"Task {e.task_id}"
            pet_name = next((p.name for p in pets if p.id == (task.pet_id if task else None)), "Unknown")
            start = e.scheduled_start.strftime("%Y-%m-%d %H:%M")
            end = e.scheduled_end.strftime("%H:%M") if e.scheduled_end else "-"
            desc = (task.description or "") if task else ""
            print(f"  {i}. {start} - {end} | {label} | {pet_name} | {desc}")

    if unscheduled:
        print("\nUnscheduled / Conflicts:")
        for i, e in enumerate(unscheduled, start=1):
            task = next((t for t in tasks if t.id == e.task_id), None)
            label = task.type if task else f"Task {e.task_id}"
            pet_name = next((p.name for p in pets if p.id == (task.pet_id if task else None)), "Unknown")
            reason = e.reason or "conflict"
            earliest = task.earliest_time.strftime("%H:%M") if task and task.earliest_time else "-"
            latest = task.latest_time.strftime("%H:%M") if task and task.latest_time else "-"
            print(f"  {i}. {label} for {pet_name} | window {earliest}-{latest} | {reason}")

    print(f"\nTotal scheduled: {len(scheduled)} | Unscheduled: {len(unscheduled)}")


if __name__ == "__main__":
    main()
