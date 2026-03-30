import streamlit as st
from pawpal_systems import Owner, Pet, Task, Scheduler, TimeWindow, save_to_json, load_from_json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
from datetime import datetime
from typing import List
import pandas as pd
import re

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700&family=Nunito:wght@400;600;700&display=swap');

:root {
    --paw-bg-a: #fff6e8;
    --paw-bg-b: #ffedd5;
    --paw-surface: #fffaf2;
    --paw-primary: #0f172a;
    --paw-accent: #f97316;
    --paw-accent-soft: #ffedd5;
    --paw-muted: #334155;
}

.stApp,
.stApp * {
    font-family: 'Nunito', sans-serif;
}

h1, h2, h3 {
    font-family: 'Baloo 2', cursive;
    letter-spacing: 0.2px;
    color: var(--paw-primary);
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top right, #ffe1bd 0%, var(--paw-bg-a) 36%, var(--paw-bg-b) 100%);
}

[data-testid="stMainBlockContainer"] {
    max-width: 1100px;
    padding-top: 1.25rem;
}

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
label,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"] {
    color: var(--paw-primary) !important;
}

[data-baseweb="input"] input,
[data-baseweb="select"] div,
[data-testid="stTextArea"] textarea {
    color: var(--paw-primary) !important;
}

/* Force real form controls to stay readable across dark/light themes */
[data-baseweb="input"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border: 1px solid #f1c28e !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #f1c28e !important;
    border-radius: 10px !important;
}

/* Match button style to input fields */
[data-testid="stButton"] button {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #f1c28e !important;
    border-radius: 10px !important;
}

[data-testid="stButton"] button:hover {
    background-color: #fff7ed !important;
    border-color: #f3b374 !important;
    color: #0f172a !important;
}

/* Keep placeholder/helper text readable against white input fields */
[data-baseweb="input"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

/* Ensure selected option labels in dropdowns are not washed out */
[data-baseweb="select"] span,
[data-baseweb="select"] p,
[data-baseweb="select"] input {
    color: var(--paw-primary) !important;
}

[data-baseweb="input"],
[data-baseweb="select"] {
    background: #ffffff !important;
    border-radius: 10px !important;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #f1c28e;
    border-radius: 12px;
    overflow: hidden;
    background: #ffffff;
}

.paw-banner {
    border: 1px solid #f3c38a;
    background: linear-gradient(135deg, #fff1dc, var(--paw-accent-soft));
    border-radius: 14px;
    padding: 0.85rem 1rem;
    color: var(--paw-primary);
    margin-bottom: 0.5rem;
    box-shadow: 0 8px 18px rgba(180, 93, 20, 0.08);
}

.paw-section-title {
    font-family: 'Baloo 2', cursive;
    color: var(--paw-primary);
    font-size: 1.15rem;
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
}

[data-testid="stAlertContainer"] {
    border-radius: 12px;
}
</style>
""",
        unsafe_allow_html=True,
)

st.title("🐾 PawPal+")

st.divider()

st.markdown('<div class="paw-section-title">Owner and Pet Setup</div>', unsafe_allow_html=True)
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_top")
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_top")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species_top")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "owner" not in st.session_state:
    saved_owner, saved_pets = load_from_json(DATA_FILE)
    st.session_state.owner = saved_owner
    st.session_state.pets = saved_pets
    if saved_owner:
        owners = st.session_state.setdefault("owners_by_name", {})
        owners[saved_owner.name] = saved_owner

def _save():
    save_to_json(DATA_FILE, st.session_state.owner, list(st.session_state.pets.values()))

st.markdown("### Owner & Pets")
owner_col, pet_col = st.columns(2)
with owner_col:
    owner_name = st.text_input("Owner name", value=owner_name, key="owner_name_col")
    if st.button("Create / Use Owner"):
        owners = st.session_state.setdefault("owners_by_name", {})
        # Reuse existing Owner by name if present in session_state
        if owner_name in owners:
            st.session_state.owner = owners[owner_name]
            st.info(f"Using existing owner: {st.session_state.owner.name}")
        else:
            o = Owner(name=owner_name)
            owners[owner_name] = o
            st.session_state.owner = o
            _save()
            st.success(f"Owner created: {st.session_state.owner.name}")

with pet_col:
    pet_name = st.text_input("Pet name", value=pet_name, key="pet_name_col")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species_col")
    if st.button("Add pet"):
        if st.session_state.owner is None:
            st.error("Create an owner first.")
        else:
            pet = Pet(name=pet_name, species=species)
            st.session_state.pets[pet.id] = pet
            st.session_state.owner.pet_ids.append(pet.id)
            _save()
            st.success(f"Added pet {pet.name}")

st.markdown("### Tasks")
col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

pet_options = [(p.id, p.name) for p in st.session_state.pets.values()]
selected_pet_id = None
if pet_options:
    selected_pet_id = st.selectbox("Assign to pet", [pid for pid, _ in pet_options], format_func=lambda pid: st.session_state.pets[pid].name)
else:
    st.info("No pets yet. Add a pet to assign tasks.")

if st.button("Add task"):
    if selected_pet_id is None:
        st.error("Select a pet first")
    else:
        # map priority label to integer
        priority_map = {"low": 1, "medium": 2, "high": 3}
        t = Task(type=task_title, duration_minutes=int(duration), priority=priority_map.get(priority, 2), pet_id=selected_pet_id)
        pet = st.session_state.pets[selected_pet_id]
        pet.add_task(t)
        _save()
        st.success(f"Added task '{t.type}' to {pet.name}")

if st.session_state.pets:
    st.write("Current pets:")
    owners = st.session_state.get("owners_by_name", {})
    pet_table = []
    for p in st.session_state.pets.values():
        owner_name = ""
        # find owner that references this pet id
        for o in owners.values():
            if p.id in getattr(o, "pet_ids", []):
                owner_name = o.name
                break
        # fallback to the currently selected owner
        if not owner_name and st.session_state.owner is not None:
            if p.id in getattr(st.session_state.owner, "pet_ids", []):
                owner_name = st.session_state.owner.name

        pet_table.append({
            "name": p.name,
            "species": p.species,
            "tasks": len(p.get_tasks()),
            "owner": owner_name,
        })

    st.dataframe(pd.DataFrame(pet_table), use_container_width=True, hide_index=True)

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")


def collect_tasks_from_pets(pets: List[Pet]) -> List[Task]:
    """Collect all tasks currently attached to pets."""
    tasks: List[Task] = []
    for pet in pets:
        tasks.extend(pet.get_tasks())
    return tasks


def format_task_time(task: Task) -> str:
    """Render earliest time or fallback to optional HH:MM time_str."""
    if getattr(task, "earliest_time", None):
        return task.earliest_time.strftime("%H:%M")
    return getattr(task, "time_str", "-")


def render_df(rows: List[dict]) -> None:
    """Render tabular rows with consistent spacing and width."""
    if not rows:
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def sanitize_text_for_ui(text: str) -> str:
    """Hide internal numeric IDs in frontend-facing messages."""
    cleaned = re.sub(r"\s*\(task\s+\d+\)", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"task\s+\d+", "task", cleaned, flags=re.IGNORECASE)
    return cleaned


pets = list(st.session_state.pets.values()) if st.session_state.pets else []
all_tasks = collect_tasks_from_pets(pets)
scheduler = Scheduler()

st.subheader("Task Board")
if not all_tasks:
    st.info("No tasks yet. Add a task to see sorted and filtered views.")
else:
    pet_filter_options = ["All pets"] + [p.name for p in pets]
    selected_pet_name = st.selectbox("Filter by pet", pet_filter_options, key="filter_pet_name")
    completed_label = st.selectbox("Completion", ["All", "Pending", "Completed"], key="filter_completed")
    completed_map = {"All": None, "Pending": False, "Completed": True}
    completed_filter = completed_map[completed_label]

    if selected_pet_name == "All pets":
        filtered_tasks = scheduler.filter_tasks(all_tasks, completed=completed_filter)
    else:
        filtered_tasks = scheduler.filter_tasks_by_pet_name(
            all_tasks,
            pets,
            pet_name=selected_pet_name,
            completed=completed_filter,
        )

    sorted_filtered_tasks = scheduler.sort_by_time(filtered_tasks)

    PRIORITY_EMOJI = {3: "\U0001f534 High", 2: "\U0001f7e1 Medium", 1: "\U0001f7e2 Low"}

    task_rows = []
    for task in sorted_filtered_tasks:
        pet_name_for_task = next((p.name for p in pets if p.id == task.pet_id), "Unknown")
        task_rows.append(
            {
                "time": format_task_time(task),
                "task": task.type,
                "pet": pet_name_for_task,
                "duration_min": task.duration_minutes,
                "priority": PRIORITY_EMOJI.get(task.priority, str(task.priority)),
                "status": "\u2705" if task.completed else "\u23f3",
            }
        )

    pending_count = sum(1 for t in sorted_filtered_tasks if not t.completed)
    completed_count = sum(1 for t in sorted_filtered_tasks if t.completed)
    m1, m2, m3 = st.columns(3)
    m1.metric("Visible Tasks", len(task_rows))
    m2.metric("Pending", pending_count)
    m3.metric("Completed", completed_count)

    st.success(f"Showing {len(task_rows)} task(s), sorted chronologically.")
    render_df(task_rows)

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.error("Create an owner first before generating a schedule.")
    else:
        owner = st.session_state.owner
        pets = list(st.session_state.pets.values())
        tasks = collect_tasks_from_pets(pets)
        # use a broad day window
        window = TimeWindow(start=datetime.now().replace(hour=6, minute=0, second=0, microsecond=0), end=datetime.now().replace(hour=20, minute=0, second=0, microsecond=0))
        schedule = scheduler.generate_schedule(owner, pets, tasks, day_window=window)
        explanations = scheduler.explain(schedule)
        warnings = scheduler.detect_conflicts(schedule, tasks, pets)

        st.subheader("Today's Plan")
        scheduled_rows = []
        unscheduled_rows = []

        for entry in schedule:
            task = next((tt for tt in tasks if tt.id == entry.task_id), None)
            pet_name_for_task = next((p.name for p in pets if p.id == (task.pet_id if task else None)), "Unknown")
            if entry.scheduled_start and entry.scheduled_end:
                scheduled_rows.append(
                    {
                        "start": entry.scheduled_start.strftime("%H:%M"),
                        "end": entry.scheduled_end.strftime("%H:%M"),
                        "task": task.type if task else "Unknown task",
                        "pet": pet_name_for_task,
                        "priority": task.priority if task else "-",
                    }
                )
            else:
                unscheduled_rows.append(
                    {
                        "task": task.type if task else "Unknown task",
                        "pet": pet_name_for_task,
                        "reason": entry.reason or "not scheduled",
                    }
                )

        if scheduled_rows:
            st.success(f"Scheduled {len(scheduled_rows)} task(s) today.")
            render_df(scheduled_rows)
        else:
            st.warning("No tasks could be scheduled in the current window.")

        if unscheduled_rows:
            st.warning(f"{len(unscheduled_rows)} task(s) could not be scheduled. Review reasons below.")
            render_df(unscheduled_rows)

        if warnings:
            st.warning("Potential task conflicts were detected. Please review and adjust to avoid overlapping care times.")
            with st.expander("Conflict details", expanded=True):
                for warning in warnings:
                    st.write(f"- {sanitize_text_for_ui(warning)}")

        with st.expander("Why this schedule was chosen"):
            explanation_rows = [{"explanation": sanitize_text_for_ui(reason)} for _, reason in explanations.items()]
            render_df(explanation_rows)

        st.subheader("Next Available Slot Finder")
        slot_duration = st.number_input(
            "Duration needed (minutes)", min_value=5, max_value=240, value=30, key="slot_dur"
        )
        if st.button("Find next slot"):
            slot = scheduler.find_next_available_slot(schedule, int(slot_duration), day_window=window)
            if slot:
                st.success(
                    f"Available slot: {slot.start.strftime('%H:%M')} – {slot.end.strftime('%H:%M')}"
                )
            else:
                st.warning("No open slot of that length exists in today's window.")
