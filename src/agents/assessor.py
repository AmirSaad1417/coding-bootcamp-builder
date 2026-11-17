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


def assess_user(user_input: dict) -> dict:
    """
    Assesses the user's current level and technical background.

    Parameters:
        user_input (dict): Contains languages, experience_years, projects_built,
                           goal, hours_per_week, and timeline_weeks.

    Returns:
        dict: Parsed assessment profile with level, strong_languages, weak_areas,
              recommended_stack, and assessment_summary.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing from environment or .env file.")

    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    system_prompt = (
        "you are a senior coding mentor. "
        "Assess the user's current level and return ONLY a raw JSON "
        "object with no markdown and no explanation with these exact keys:\n"
        "- level: one of \"beginner\", \"intermediate\", \"advanced\"\n"
        "- strong_languages: list of languages they know well\n"
        "- weak_areas: list of specific gaps or weaknesses\n"
        "- recommended_stack: the stack they should focus on given their goal\n"
        "- assessment_summary: 2-3 sentences summarizing their profile"
    )

    user_message = (
        f"User Background & Goal:\n"
        f"- Languages: {user_input.get('languages', '')}\n"
        f"- Experience: {user_input.get('experience_years', '')}\n"
        f"- Projects Built: {user_input.get('projects_built', '')}\n"
        f"- Goal: {user_input.get('goal', '')}\n"
        f"- Hours Per Week: {user_input.get('hours_per_week', '')}\n"
        f"- Timeline Weeks: {user_input.get('timeline_weeks', '')}"
    )

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )
        raw_content = response.choices[0].message.content or ""
    except Exception as e:
        raise RuntimeError(f"Error calling LLM API: {e}") from e

    cleaned_content = _strip_markdown(raw_content)

    try:
        parsed_json = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse assessment response into JSON: {e}\nRaw response:\n{raw_content}"
        ) from e

    required_keys = [
        "level",
        "strong_languages",
        "weak_areas",
        "recommended_stack",
        "assessment_summary",
    ]
    missing_keys = [key for key in required_keys if key not in parsed_json]
    if missing_keys:
        raise ValueError(f"Assessment JSON is missing required keys: {missing_keys}")

    goal = user_input.get("goal", "the specified goal")
    print(f"Assessment complete for: {goal}")

    return parsed_json
