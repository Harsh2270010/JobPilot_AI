import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "jobpilot.db"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def get_connection():
    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def column_exists(
    connection,
    table_name,
    column_name,
):
    cursor = connection.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = cursor.fetchall()

    return any(
        column["name"] == column_name
        for column in columns
    )


def init_db():
    with get_connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                company TEXT NOT NULL,

                role TEXT NOT NULL,

                recruiter_name TEXT DEFAULT '',

                recruiter_email TEXT DEFAULT '',

                match_score REAL NOT NULL DEFAULT 0,

                matched_skills TEXT DEFAULT '',

                missing_skills TEXT DEFAULT '',

                generated_message TEXT DEFAULT '',

                status TEXT NOT NULL DEFAULT 'Not Applied',

                application_date TEXT NOT NULL,

                notes TEXT DEFAULT ''
            )
            """
        )

        # Upgrade an older JobPilot database if it already exists.
        columns_to_add = {
            "recruiter_name": "TEXT DEFAULT ''",
            "recruiter_email": "TEXT DEFAULT ''",
            "matched_skills": "TEXT DEFAULT ''",
            "missing_skills": "TEXT DEFAULT ''",
            "generated_message": "TEXT DEFAULT ''",
            "status": "TEXT NOT NULL DEFAULT 'Not Applied'",
            "application_date": "TEXT DEFAULT ''",
            "notes": "TEXT DEFAULT ''",
        }

        for column, definition in columns_to_add.items():

            if not column_exists(
                conn,
                "applications",
                column,
            ):

                conn.execute(
                    f"""
                    ALTER TABLE applications
                    ADD COLUMN {column} {definition}
                    """
                )

        conn.commit()


def list_applications():

    with get_connection() as conn:

        return conn.execute(
            """
            SELECT *
            FROM applications
            ORDER BY id DESC
            """
        ).fetchall()


def get_application(
    application_id: int,
):

    with get_connection() as conn:

        return conn.execute(
            """
            SELECT *
            FROM applications
            WHERE id = ?
            """,
            (
                application_id,
            ),
        ).fetchone()


def update_status(
    application_id: int,
    status: str,
):

    with get_connection() as conn:

        conn.execute(
            """
            UPDATE applications
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                application_id,
            ),
        )

        conn.commit()


def delete_application(
    application_id: int,
):

    with get_connection() as conn:

        conn.execute(
            """
            DELETE FROM applications
            WHERE id = ?
            """,
            (
                application_id,
            ),
        )

        conn.commit()