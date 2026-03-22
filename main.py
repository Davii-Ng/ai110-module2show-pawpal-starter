from datetime import datetime, time, timedelta
from typing import List
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

    # add a few tasks out-of-order using time_str to demonstrate HH:MM sorting
    extra1 = Task(type="Checkup", duration_minutes=20, priority=2, pet_id=pets[2].id, description="Checkup for Pet3")
    extra1.time_str = "08:30"
    tasks.append(extra1)

    extra2 = Task(type="Play", duration_minutes=10, priority=1, pet_id=pets[0].id, description="Playtime for Pet1")
    extra2.time_str = "07:45"
    tasks.append(extra2)

    extra3 = Task(type="Feed", duration_minutes=10, priority=3, pet_id=pets[1].id, description="Extra feeding for Pet2")
    extra3.time_str = "18:15"
    tasks.append(extra3)

    # create two tasks intentionally at the same time to demonstrate conflict detection
    conflict_time = today_at(9)
    t_conf1 = Task(type="VetCheck", duration_minutes=30, priority=2, pet_id=pets[0].id, earliest_time=conflict_time, latest_time=conflict_time + timedelta(hours=1), description="Vet check for Pet1")
    t_conf2 = Task(type="Bath", duration_minutes=30, priority=2, pet_id=pets[1].id, earliest_time=conflict_time, latest_time=conflict_time + timedelta(hours=1), description="Bath for Pet2")
    tasks.append(t_conf1)
    tasks.append(t_conf2)

    # day window (6:00 - 20:00)
    window = TimeWindow(start=today_at(6), end=today_at(20))

    scheduler = Scheduler()

    # Demonstrate sorting by HH:MM (via sort_by_time) and filtering by pet name
    print("\nDemo: tasks sorted by time (including HH:MM strings):")
    sorted_tasks = scheduler.sort_by_time(tasks)
    # header
    print(f"  {'Time':6} | {'Task':12} | {'Pet':10} | {'Description':40}")
    print("  " + "-" * 6 + "-+" + "-" * 14 + "+" + "-" * 12 + "+" + "-" * 42)
    for t in sorted_tasks:
        time_label = t.earliest_time.strftime("%H:%M") if getattr(t, "earliest_time", None) else getattr(t, "time_str", "-")
        pet_name = next((p.name for p in pets if p.id == t.pet_id), "Unknown")
        print(f"  {time_label:<6} | {t.type:<12} | {pet_name:<10} | {((t.description or '')[:40]):40}")

    print("\nDemo: filter tasks for Pet3 (not completed):")
    pet3_tasks = scheduler.filter_tasks_by_pet_name(tasks, pets, pet_name="Pet3", completed=False)
    print(f"  {'Time':6} | {'Task':12} | {'Description':40}")
    print("  " + "-" * 6 + "-+" + "-" * 14 + "+" + "-" * 42)
    for t in pet3_tasks:
        time_label = t.earliest_time.strftime("%H:%M") if getattr(t, "earliest_time", None) else getattr(t, "time_str", "-")
        print(f"  {time_label:<6} | {t.type:<12} | {((t.description or '')[:40]):40}")
    schedule = scheduler.generate_schedule(owner, pets, tasks, day_window=window)

    # detect and print lightweight conflict warnings
    warnings = scheduler.detect_conflicts(schedule, tasks, pets)
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print("  -", w)

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
            print(f"  {i:10}. {start} - {end} | {label} | {pet_name} | {desc}")

    if unscheduled:
        print("\nUnscheduled / Conflicts:")
        for i, e in enumerate(unscheduled, start=1):
            task = next((t for t in tasks if t.id == e.task_id), None)
            label = task.type if task else f"Task {e.task_id}"
            pet_name = next((p.name for p in pets if p.id == (task.pet_id if task else None)), "Unknown")
            reason = e.reason or "conflict"
            earliest = task.earliest_time.strftime("%H:%M") if task and task.earliest_time else "-"
            latest = task.latest_time.strftime("%H:%M") if task and task.latest_time else "-"
            print(f"  {i:10}. {label} for {pet_name} | window {earliest}-{latest} | {reason}")

    print(f"\nTotal scheduled: {len(scheduled)} | Unscheduled: {len(unscheduled)}")


if __name__ == "__main__":
    main()
