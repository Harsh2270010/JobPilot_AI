from dataclasses import dataclass


@dataclass
class Application:
    id: int
    company: str
    role: str
    recruiter_name: str
    recruiter_email: str
    match_score: float
    matched_skills: str
    missing_skills: str
    generated_message: str
    status: str
    application_date: str
    notes: str

    STATUSES = [
        "Not Applied",
        "Applied",
        "Assessment",
        "Interview",
        "Rejected",
        "Offer",
    ]