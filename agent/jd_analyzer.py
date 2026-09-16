import json
import os
import re

from typing import Any

from pydantic import BaseModel


KNOWN_SKILLS = [
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "machine learning",
    "deep learning",
    "nlp",
    "natural language processing",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "opencv",
    "yolo",
    "fastapi",
    "flask",
    "django",
    "rest api",
    "rest apis",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "git",
    "github",
    "langchain",
    "llms",
    "agentic ai",
    "power bi",
    "tableau",
    "spark",
    "airflow",
]


class JobData(BaseModel):

    role: str = "Unknown Role"

    skills: list[str] = []

    experience: str = ""

    location: str = ""


def fallback_parse(
    text: str,
) -> dict[str, Any]:

    lower_text = text.lower()

    detected_skills = []

    for skill in KNOWN_SKILLS:

        pattern = (
            rf"(?<!\w)"
            rf"{re.escape(skill)}"
            rf"(?!\w)"
        )

        if re.search(
            pattern,
            lower_text,
        ):

            detected_skills.append(
                skill
            )

    role = "Unknown Role"

    known_roles = [
        "AI/ML Engineer",
        "AI Engineer",
        "ML Engineer",
        "Machine Learning Engineer",
        "Software Engineer",
        "SDE-1",
        "Software Developer",
        "Python Developer",
        "Data Scientist",
        "Data Analyst",
    ]

    for candidate in known_roles:

        if candidate.lower() in lower_text:

            role = candidate

            break

    experience_match = re.search(
        r"(\d+\s*(?:-|to)\s*\d+\s*years?|\d+\+?\s*years?)",
        lower_text,
    )

    location_match = re.search(
        r"(?:location|based in)\s*[:\-]\s*([^\n]+)",
        text,
        flags=re.IGNORECASE,
    )

    return {
        "role": role,
        "skills": list(
            dict.fromkeys(
                detected_skills
            )
        ),
        "experience": (
            experience_match.group(1)
            if experience_match
            else ""
        ),
        "location": (
            location_match.group(1).strip()
            if location_match
            else ""
        ),
    }


def analyze_job_description(
    text: str,
) -> dict[str, Any]:

    api_key = os.getenv(
        "GROQ_API_KEY",
        "",
    ).strip()

    if not api_key:

        return fallback_parse(
            text
        )

    try:

        from groq import Groq

        client = Groq(
            api_key=api_key
        )

        prompt = f"""
Extract structured information from this job description.

Return ONLY valid JSON.

Schema:

{{
    "role": "string",
    "skills": ["skill1", "skill2"],
    "experience": "string",
    "location": "string"
}}

Rules:
- Extract only information present in the job description.
- Use concise technical skill names.
- Do not invent requirements.

JOB DESCRIPTION:

{text}
"""

        response = (
            client.chat.completions.create(
                model=os.getenv(
                    "GROQ_MODEL",
                    "llama-3.1-8b-instant",
                ),
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract structured job "
                            "requirements and return "
                            "valid JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
        )

        raw = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        raw = (
            raw
            .removeprefix("```json")
            .removesuffix("```")
            .strip()
        )

        parsed = json.loads(
            raw
        )

        validated = (
            JobData
            .model_validate(
                parsed
            )
        )

        return validated.model_dump()

    except Exception:

        return fallback_parse(
            text
        )