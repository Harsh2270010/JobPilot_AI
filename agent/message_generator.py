import os


def generate_outreach_message(
    company: str,
    role: str,
    candidate_name: str,
    profile_skills: list[str],
    match: dict,
) -> str:

    candidate_name = (
        candidate_name.strip()
        or "Candidate"
    )

    api_key = os.getenv(
        "GROQ_API_KEY",
        "",
    ).strip()

    if api_key:

        try:

            from groq import Groq

            client = Groq(
                api_key=api_key
            )

            prompt = f"""
Write a personalized recruiter outreach message.

Candidate Name:
{candidate_name}

Company:
{company}

Role:
{role}

Candidate Skills:
{", ".join(profile_skills)}

Matching Skills:
{", ".join(match.get("matched", []))}

Missing Skills:
{", ".join(match.get("missing", []))}

Rules:
- 80-110 words
- Professional and concise
- Suitable for LinkedIn or email
- Use the candidate's actual name
- Do not invent experience
- Do not invent achievements
- Do not invent skills
- Mention only relevant matching skills
- Sign using the candidate's actual name
- Do not use a placeholder candidate name

Return ONLY the message body.
"""

            response = (
                client.chat.completions.create(
                    model=os.getenv(
                        "GROQ_MODEL",
                        "llama-3.1-8b-instant",
                    ),
                    temperature=0.4,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Write factual and "
                                "professional recruiter "
                                "outreach messages."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
            )

            generated = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            if (
                candidate_name.lower()
                not in generated.lower()
            ):

                generated += (
                    "\n\nBest regards,\n"
                    f"{candidate_name}"
                )

            return generated

        except Exception:

            pass

    strongest_skills = match.get(
        "matched",
        [],
    )[:3]

    skills_text = (
        ", ".join(
            strongest_skills
        )
        if strongest_skills
        else "relevant technical skills"
    )

    return f"""Hi [Recruiter Name],

I came across the {role} opportunity at {company} and found it closely aligned with my background in {skills_text}. I have hands-on experience working with these technologies and am actively looking for an opportunity where I can contribute while continuing to grow as an engineer.

I would appreciate the opportunity to be considered for this role.

Best regards,
{candidate_name}"""