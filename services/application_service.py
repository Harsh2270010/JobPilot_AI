from database.db import get_connection


def create_application(
    company: str,
    role: str,
    recruiter_name: str,
    recruiter_email: str,
    match_score: float,
    matched_skills: str,
    missing_skills: str,
    generated_message: str,
    status: str,
    application_date: str,
    notes: str = "",
):

    with get_connection() as conn:

        cursor = conn.execute(
            """
            INSERT INTO applications (

                company,
                role,
                recruiter_name,
                recruiter_email,
                match_score,
                matched_skills,
                missing_skills,
                generated_message,
                status,
                application_date,
                notes
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                role,
                recruiter_name,
                recruiter_email,
                match_score,
                matched_skills,
                missing_skills,
                generated_message,
                status,
                application_date,
                notes,
            ),
        )

        conn.commit()

        return cursor.lastrowid