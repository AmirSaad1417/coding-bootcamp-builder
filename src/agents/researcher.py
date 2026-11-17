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


def research_projects(assessment: dict) -> list:
    """
    Finds and returns 8 tailored projects based on the user's assessment profile.

    Parameters:
        assessment (dict): Contains level, strong_languages, weak_areas,
                           recommended_stack, and assessment_summary.

    Returns:
        list: Exactly 8 project dicts, each containing title, description,
              skills_taught, difficulty, estimated_hours, and why_this_project.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing from environment or .env file.")

    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    system_prompt = (
        "you are a coding curriculum researcher.\n"
        "Based on the assessment provided, find and return ONLY a raw JSON "
        "array with no markdown and no explanation.\n"
        "The array must contain exactly 8 project objects.\n"
        "Each project object must have these exact keys:\n"
        "- title: short project name\n"
        "- description: what the project does in one sentence\n"
        "- skills_taught: list of 3-4 specific skills this project teaches\n"
        "- difficulty: one of \"easy\", \"medium\", \"hard\"\n"
        "- estimated_hours: integer number of hours to complete\n"
        "- why_this_project: one sentence explaining why it fits this user"
    )

    formatted_assessment = json.dumps(assessment, indent=2)
    user_message = (
        "Here is the user's assessment profile:\n\n"
        f"{formatted_assessment}\n\n"
        "Return exactly 8 project objects in a raw JSON array matching the required schema."
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
        raise RuntimeError(f"Error calling LLM API for project research: {e}") from e

    cleaned_content = _strip_markdown(raw_content)

    try:
        parsed_projects = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse research response into a JSON array: {e}\nRaw response:\n{raw_content}"
        ) from e

    if not isinstance(parsed_projects, list):
        raise ValueError(
            f"Expected a JSON array of projects, but received {type(parsed_projects).__name__}."
        )

    if len(parsed_projects) != 8:
        raise ValueError(
            f"Validation error: Expected exactly 8 projects, but received {len(parsed_projects)}."
        )

    required_keys = [
        "title",
        "description",
        "skills_taught",
        "difficulty",
        "estimated_hours",
        "why_this_project",
    ]
    for idx, project in enumerate(parsed_projects):
        if not isinstance(project, dict):
            raise ValueError(f"Project at index {idx} is not a valid JSON object.")
        missing = [key for key in required_keys if key not in project]
        if missing:
            raise ValueError(
                f"Project at index {idx} ('{project.get('title', 'Unknown')}') missing required keys: {missing}"
            )

    print("Research complete. 8 projects found.")
    return parsed_projects
