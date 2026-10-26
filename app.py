import streamlit as st
import pawpal_system as pawpal

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

# Streamlit reruns this whole script on every interaction, so a plain `owner = Owner(...)`
# would be rebuilt (and its pets/tasks lost) each time. st.session_state is the "vault":
# a dict-like object that survives reruns. Only create the Owner if the key isn't there yet.
if "owner" not in st.session_state:
    st.session_state.owner = pawpal.Owner(name="Jordan")
owner: pawpal.Owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name can't be empty.")
    elif owner.get_pet(pet_name) is not None:
        st.warning(f"{pet_name} is already on your list.")
    else:
        owner.add_pet(pawpal.Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name}!")

if owner.pets:
    st.write("Your pets:")
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Tasks are attached to a pet and feed directly into the scheduler.")

if owner.pets:
    target_pet = st.selectbox("Pet", [p.name for p in owner.pets])
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        owner.get_pet(target_pet).add_task(
            pawpal.Task(description=task_title, duration_minutes=int(duration), priority=priority)
        )
        st.success(f"Added '{task_title}' for {target_pet}.")
else:
    st.info("Add a pet before adding tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet_name,
                "task": t.description,
                "minutes": t.duration_minutes,
                "priority": t.priority,
                "status": t.get_status(),
            }
            for t in all_tasks
        ]
    )

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = pawpal.Scheduler(owner)
    for warning in scheduler.detect_conflicts():
        st.warning(warning)
    plan = scheduler.build_plan()
    if plan:
        st.table(
            [
                {
                    "start": start,
                    "pet": task.pet_name,
                    "task": task.description,
                    "minutes": task.duration_minutes,
                    "why": reason,
                }
                for start, task, reason in plan
            ]
        )
    else:
        st.info("Nothing to schedule today.")
    for task, reason in scheduler.skipped:
        st.caption(f"Skipped {task.pet_name}: {task.description} - {reason}")
