import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Ensure .env is loaded
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)


def _strip_markdown(text: str) -> str:
    """Strips markdown code fences and whitespace from response text."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def build_curriculum(assessment: dict, projects: list, timeline_weeks: int) -> dict:
    """
    Sequences projects and assessment findings into a week-by-week curriculum.

    Parameters:
        assessment (dict): Assessment output from assess_user().
        projects (list): 8 researched projects from research_projects().
        timeline_weeks (int): Number of weeks for the curriculum.

    Returns:
        dict: Week-by-week curriculum containing total_weeks, weekly_hours,
              stack_focus, and weeks array.
    """
    target_weeks = int(timeline_weeks)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing from environment or .env file.")

    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    system_prompt = (
        "you are a coding bootcamp curriculum designer. Using the assessment and project "
        "list provided, build a structured week-by-week curriculum and return ONLY a raw JSON "
        "object with no markdown and no explanation with these exact keys:\n"
        "- total_weeks: integer\n"
        "- weekly_hours: integer\n"
        "- stack_focus: string\n"
        "- weeks: a list of week objects, each containing:\n"
        "  - week_number: integer\n"
        "  - theme: short title for the week\n"
        "  - project: the project title assigned to this week\n"
        "  - goals: list of 3 specific learning goals for this week\n"
        "  - deliverable: exactly what the user should have built by end of week\n"
        "  - resources: list of 2-3 specific resource names or types to use"
    )

    formatted_projects = "\n".join(
        [
            f"- Project {i+1}: {p.get('title', '')} | {p.get('description', '')} (Difficulty: {p.get('difficulty', '')}, Est. Hours: {p.get('estimated_hours', '')})"
            for i, p in enumerate(projects)
        ]
    )

    user_message = (
        f"Assessment Summary:\n"
        f"- Level: {assessment.get('level', '')}\n"
        f"- Recommended Stack: {assessment.get('recommended_stack', '')}\n"
        f"- Summary: {assessment.get('assessment_summary', '')}\n\n"
        f"Available Projects (8):\n"
        f"{formatted_projects}\n\n"
        f"Target Timeline: Exactly {target_weeks} weeks.\n"
        f"Generate exactly {target_weeks} week objects in the 'weeks' array (week_number 1 to {target_weeks})."
    )

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )
        raw_content = response.choices[0].message.content or ""
    except Exception as e:
        raise RuntimeError(f"Error calling LLM API for curriculum builder: {e}") from e

    cleaned_content = _strip_markdown(raw_content)

    try:
        parsed_curriculum = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse curriculum response into JSON: {e}\nRaw response:\n{raw_content}"
        ) from e

    if not isinstance(parsed_curriculum, dict):
        raise ValueError(
            f"Expected a JSON dictionary for curriculum, but received {type(parsed_curriculum).__name__}."
        )

    weeks_list = parsed_curriculum.get("weeks")
    if not isinstance(weeks_list, list):
        raise ValueError("Curriculum JSON is missing a valid 'weeks' list.")

    if len(weeks_list) != target_weeks:
        raise ValueError(
            f"Validation error: Expected exactly {target_weeks} weeks, but received {len(weeks_list)} weeks."
        )

    required_week_keys = [
        "week_number",
        "theme",
        "project",
        "goals",
        "deliverable",
        "resources",
    ]
    for idx, week_obj in enumerate(weeks_list):
        if not isinstance(week_obj, dict):
            raise ValueError(f"Week item at index {idx} is not a valid JSON object.")
        missing = [k for k in required_week_keys if k not in week_obj]
        if missing:
            raise ValueError(
                f"Week {week_obj.get('week_number', idx + 1)} is missing required keys: {missing}"
            )

    print(f"Curriculum built. {len(weeks_list)} weeks planned.")
    return parsed_curriculum
