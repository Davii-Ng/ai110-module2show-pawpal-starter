import streamlit as st
from pawpal_systems import Owner, Pet, Task, Scheduler, TimeWindow
from datetime import datetime
from typing import List

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_top")
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_top")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species_top")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pets" not in st.session_state:
    st.session_state.pets = {}

st.markdown("### Owner & Pets")
owner_col, pet_col = st.columns(2)
with owner_col:
    owner_name = st.text_input("Owner name", value=owner_name, key="owner_name_col")
    if st.button("Create / Use Owner"):
        owners = st.session_state.setdefault("owners_by_name", {})
        # Reuse existing Owner by name if present in session_state
        if owner_name in owners:
            st.session_state.owner = owners[owner_name]
            st.info(f"Using existing owner: {st.session_state.owner.name} (id={st.session_state.owner.id})")
        else:
            o = Owner(name=owner_name)
            owners[owner_name] = o
            st.session_state.owner = o
            st.success(f"Owner created: {st.session_state.owner.name} (id={st.session_state.owner.id})")

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
            st.success(f"Added pet {pet.name} (id={pet.id})")

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
            "id": p.id,
            "name": p.name,
            "species": p.species,
            "tasks": len(p.get_tasks()),
            "owner": owner_name,
        })

    st.table(pet_table)

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.error("Create an owner first before generating a schedule.")
    else:
        owner = st.session_state.owner
        pets = list(st.session_state.pets.values())
        # collect all tasks from pets
        tasks: List[Task] = []
        for p in pets:
            tasks.extend(p.get_tasks())

        scheduler = Scheduler()
        # use a broad day window
        window = TimeWindow(start=datetime.now().replace(hour=6, minute=0, second=0, microsecond=0), end=datetime.now().replace(hour=20, minute=0, second=0, microsecond=0))
        schedule = scheduler.generate_schedule(owner, pets, tasks, day_window=window)
        explanations = scheduler.explain(schedule)

        st.subheader("Schedule")
        for e in schedule:
            if e.scheduled_start and e.scheduled_end:
                t = next((tt for tt in tasks if tt.id == e.task_id), None)
                pet_name = next((p.name for p in pets if p.id == (t.pet_id if t else None)), "Unknown")
                st.write(f"- {e.scheduled_start.strftime('%H:%M')} - {e.scheduled_end.strftime('%H:%M')}: {t.type} for {pet_name}")
            else:
                t = next((tt for tt in tasks if tt.id == e.task_id), None)
                pet_name = next((p.name for p in pets if p.id == (t.pet_id if t else None)), "Unknown")
                st.write(f"- UNSCHEDULED: {t.type if t else e.task_id} for {pet_name} — {e.reason}")
