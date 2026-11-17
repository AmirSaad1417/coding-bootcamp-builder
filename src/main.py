import os
import sys
from pathlib import Path

# Ensure project root is in sys.path so "from src.agents import ..." works seamlessly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Load OPENAI_API_KEY from .env using python-dotenv
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# 2. Raise a clear EnvironmentError if the key is missing
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or not api_key.strip():
    raise EnvironmentError("ERROR: OPENAI_API_KEY missing from environment or .env file.")

# 3. Import assess_user, research_projects, build_curriculum, review_curriculum
from src.agents import (
    assess_user,
    research_projects,
    build_curriculum,
    review_curriculum,
)


def run_pipeline():
    # 4. Define a hardcoded test user dict
    test_user = {
        "languages": "Python, basic HTML/CSS",
        "experience_years": "1 year",
        "projects_built": "a todo app, a weather app",
        "goal": "get a junior backend developer job",
        "hours_per_week": "15",
        "timeline_weeks": "8",
    }

    try:
        # Step 1: Assess User
        print("\n--- Running Assessor Agent ---")
        assessment = assess_user(test_user)
        print("Assessment Result:")
        print(f"  Level: {assessment.get('level')}")
        print(f"  Strong Languages: {assessment.get('strong_languages')}")
        print(f"  Weak Areas: {assessment.get('weak_areas')}")
        print(f"  Recommended Stack: {assessment.get('recommended_stack')}")
        print(f"  Summary: {assessment.get('assessment_summary')}")

        # Step 2: Research Projects
        print("\n--- Running Researcher Agent ---")
        projects = research_projects(assessment)
        print(f"Projects found: {len(projects)}")

        # Step 3: Build Curriculum
        print("\n--- Running Curriculum Builder Agent ---")
        timeline_weeks = int(test_user["timeline_weeks"])
        curriculum = build_curriculum(assessment, projects, timeline_weeks=timeline_weeks)
        print(f"Weeks built: {len(curriculum.get('weeks', []))}")

        # Step 4: Review Curriculum
        print("\n--- Running Reviewer Agent ---")
        reviewed = review_curriculum(curriculum, assessment)
        print("Review Feedback:")
        print(f"  Overall Feedback: {reviewed.get('overall_feedback')}")
        print(f"  Difficulty Rating: {reviewed.get('difficulty_rating')}")
        print(f"  Capstone Project: {reviewed.get('final_project', {}).get('title')}")

        # 7. Print "Pipeline complete." at the end if everything succeeds
        print("\nPipeline complete.")

    except Exception as e:
        print(f"\nPipeline error encountered: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
