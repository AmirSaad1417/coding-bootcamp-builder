import re
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path so agents can be imported seamlessly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents import (
    assess_user,
    research_projects,
    build_curriculum,
    review_curriculum,
)

# 1. Page config
st.set_page_config(
    page_title="Coding Bootcamp Builder",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Professional styling (Modern UI/UX Pro design system)
st.markdown(
    """
    <style>
    /* Global modern clean typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero header gradient */
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .hero-caption {
        font-size: 1.08rem;
        color: #4B5563;
        margin-bottom: 1.8rem;
    }

    /* Card styling */
    .custom-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .badge-primary {
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
    }
    .badge-success {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
    }
    .badge-warning {
        background-color: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    /* Clean expander look */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 1.02rem !important;
    }

    /* Capstone container */
    .capstone-container {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 2. Header and Caption
st.markdown('<div class="hero-title">Coding Bootcamp Builder</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-caption">Build your personal coding bootcamp in seconds.</div>',
    unsafe_allow_html=True,
)

# 3. Form input section
with st.form("bootcamp_form"):
    languages = st.text_input(
        "What languages or frameworks do you know?",
        placeholder="e.g. Python, basic HTML/CSS, React",
    )

    experience_years = st.text_input(
        "How long have you been coding?",
        placeholder="e.g. 6 months, 2 years",
    )

    projects_built = st.text_area(
        "What have you built before? List any projects.",
        placeholder="e.g. A todo list app, weather dashboard, web scraper",
        help="List completed or in-progress projects to help calibrate your level.",
    )

    goal = st.text_input(
        "What is your goal?",
        placeholder="e.g. get a backend job, go freelance",
    )

    col1, col2 = st.columns(2)
    with col1:
        hours_per_week = st.number_input(
            "Hours available per week",
            min_value=1,
            max_value=40,
            value=10,
            step=1,
        )

    with col2:
        timeline_option = st.selectbox(
            "Timeline",
            options=["4 weeks", "8 weeks", "12 weeks", "16 weeks"],
            index=1,
        )

    submit_button = st.form_submit_button(
        "Build My Bootcamp",
        type="primary",
        use_container_width=True,
    )

# 4. Handle Form Submission & Pipeline Execution
if submit_button:
    # Validation: all text fields must be filled
    if not languages.strip() or not experience_years.strip() or not projects_built.strip() or not goal.strip():
        st.error("Please fill in all required fields before building your bootcamp.")
    else:
        # Extract integer weeks (e.g. "8 weeks" -> 8)
        timeline_match = re.search(r"\d+", timeline_option)
        timeline_weeks = int(timeline_match.group()) if timeline_match else 8

        user_input = {
            "languages": languages.strip(),
            "experience_years": experience_years.strip(),
            "projects_built": projects_built.strip(),
            "goal": goal.strip(),
            "hours_per_week": str(hours_per_week),
            "timeline_weeks": str(timeline_weeks),
        }

        try:
            # Agent 1: Assessor
            with st.spinner("Assessing your current level..."):
                assessment = assess_user(user_input)

            # Agent 2: Researcher
            with st.spinner("Researching the best projects for you..."):
                projects = research_projects(assessment)

            # Agent 3: Curriculum Builder
            with st.spinner("Building your week-by-week curriculum..."):
                curriculum = build_curriculum(
                    assessment=assessment,
                    projects=projects,
                    timeline_weeks=timeline_weeks,
                )

            # Agent 4: Reviewer
            with st.spinner("Adding mentorship checkpoints..."):
                reviewed = review_curriculum(
                    curriculum=curriculum,
                    assessment=assessment,
                )

            # Preserve stack_focus and metadata in the reviewed curriculum
            reviewed["stack_focus"] = curriculum.get("stack_focus", "Full Stack Development")
            reviewed["total_weeks"] = curriculum.get("total_weeks", timeline_weeks)
            reviewed["weekly_hours"] = curriculum.get("weekly_hours", hours_per_week)

            # Store in session state
            st.session_state["bootcamp_result"] = reviewed
            st.session_state["active_goal"] = goal.strip()

        except Exception as e:
            st.error(f"Error during bootcamp generation: {e}")

# 5. Display Results
if "bootcamp_result" in st.session_state:
    result = st.session_state["bootcamp_result"]

    st.markdown("---")

    # 1. Overall feedback
    overall_feedback = result.get("overall_feedback", "Great progress toward your goal.")
    st.success(overall_feedback)

    # 2. Difficulty rating and stack focus
    diff_rating = result.get("difficulty_rating", "Well Balanced")
    stack_focus = result.get("stack_focus", "Modern Software Development")
    if isinstance(stack_focus, list):
        stack_focus_str = ", ".join(stack_focus)
    elif isinstance(stack_focus, dict):
        stack_focus_str = ", ".join(f"{k}: {v}" for k, v in stack_focus.items())
    else:
        stack_focus_str = str(stack_focus)

    st.info(f"**Difficulty Rating:** {str(diff_rating).title()}  \n**Stack Focus:** {stack_focus_str}")

    # 3. Subheader: Your Week-by-Week Plan
    st.subheader("Your Week-by-Week Plan")

    weeks = result.get("weeks", [])
    for idx, week in enumerate(weeks):
        week_num = week.get("week_number", idx + 1)
        theme = week.get("theme", f"Phase {week_num}")
        project = week.get("project", "Weekly Applied Project")
        deliverable = week.get("deliverable", "Functional code submission")
        goals = week.get("goals", [])
        resources = week.get("resources", [])
        checkpoint = week.get("checkpoint", "Review code and ensure all tests pass.")

        with st.expander(f"Week {week_num} — {theme}", expanded=(idx == 0)):
            st.markdown(f"**Project:** {project}")
            st.markdown(f"**Deliverable:** {deliverable}")

            if goals:
                st.markdown("**Goals:**")
                for g in goals:
                    st.markdown(f"- {g}")

            if resources:
                st.markdown("**Resources:**")
                for r in resources:
                    st.markdown(f"- {r}")

            # Highlighted checkpoint question
            st.warning(f"**Mentor Checkpoint:** {checkpoint}")

    # 4. Final Capstone Project
    st.subheader("Final Capstone Project")
    final_proj = result.get("final_project", {})
    cap_title = final_proj.get("title", "Full Stack Capstone")
    cap_desc = final_proj.get("description", "A production-grade project demonstrating mastery.")
    cap_hours = final_proj.get("estimated_hours", 40)
    cap_reqs = final_proj.get("requirements", [])

    st.markdown(f"### {cap_title}")
    st.markdown(f"{cap_desc}")
    st.markdown(f"**Estimated Hours:** {cap_hours} hrs")

    if cap_reqs:
        st.markdown("**Requirements:**")
        for i, req in enumerate(cap_reqs, 1):
            st.markdown(f"{i}. {req}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Start Over button
    if st.button("Start Over", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
