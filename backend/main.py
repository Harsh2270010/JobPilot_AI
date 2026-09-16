from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent.jd_analyzer import analyze_job_description

from agent.matcher import (
    extract_candidate_name,
    extract_candidate_skills,
    match_profile,
)

from agent.message_generator import (
    generate_outreach_message,
)

from database.db import (
    init_db,
)

from services.application_service import (
    create_application,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="JobPilot AI",
    description="AI Job Application Productivity Agent",
    version="1.0.0",
)


init_db()


# ============================================================
# REQUEST MODEL
# ============================================================

class RunRequest(BaseModel):

    company: str = Field(
        min_length=1
    )

    recruiter_name: str = ""

    recruiter_email: str = ""

    role_hint: str = ""

    job_description: str = Field(
        min_length=1
    )

    resume_text: str = ""

    application_date: str


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "message":
        "JobPilot AI backend is running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# AGENT
# ============================================================

@app.post("/agent/run")
def run_agent(
    request: RunRequest,
):

    company = request.company.strip()

    recruiter_name = (
        request.recruiter_name.strip()
    )

    recruiter_email = (
        request.recruiter_email.strip()
    )

    job_description = (
        request.job_description.strip()
    )

    if not company:

        raise HTTPException(
            status_code=400,
            detail="Company is required.",
        )

    if not job_description:

        raise HTTPException(
            status_code=400,
            detail="Job description is required.",
        )

    trace = []

    # --------------------------------------------------------
    # 1. Analyze job
    # --------------------------------------------------------

    job = analyze_job_description(
        job_description
    )

    if (
        request.role_hint.strip()
        and
        job["role"] == "Unknown Role"
    ):

        job["role"] = (
            request.role_hint.strip()
        )

    trace.append(
        "Analyzed job description"
    )

    # --------------------------------------------------------
    # 2. Read resume
    # --------------------------------------------------------

    candidate_name = (
        extract_candidate_name(
            request.resume_text
        )
    )

    candidate_skills = (
        extract_candidate_skills(
            request.resume_text
        )
    )

    trace.append(
        "Extracted candidate name and skills from resume"
    )

    # --------------------------------------------------------
    # 3. Match
    # --------------------------------------------------------

    match = match_profile(
        job_skills=job["skills"],
        candidate_skills=candidate_skills,
    )

    trace.append(
        "Compared job requirements with candidate profile"
    )

    trace.append(
        "Calculated deterministic match score"
    )

    # --------------------------------------------------------
    # 4. Agent decision
    # --------------------------------------------------------

    if (
        match["recommendation"]
        == "SKIP"
    ):

        message = (
            "The agent recommends skipping this opportunity "
            "because too many required skills are missing."
        )

        trace.append(
            "Decided to skip outreach because compatibility is low"
        )

    else:

        message = (
            generate_outreach_message(
                company=company,
                role=job["role"],
                candidate_name=candidate_name,
                profile_skills=candidate_skills,
                match=match,
            )
        )

        trace.append(
            "Generated personalized LinkedIn/email outreach"
        )

    # --------------------------------------------------------
    # 5. Save application
    # --------------------------------------------------------

    application_id = (
        create_application(

            company=company,

            role=job["role"],

            recruiter_name=recruiter_name,

            recruiter_email=recruiter_email,

            match_score=match["score"],

            matched_skills=", ".join(
                match["matched"]
            ),

            missing_skills=", ".join(
                match["missing"]
            ),

            generated_message=message,

            status="Not Applied",

            application_date=request.application_date,

            notes=(
                f"Candidate: "
                f"{candidate_name}"
            ),
        )
    )

    trace.append(
        "Saved application to SQLite"
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "saved": True,

        "application_id":
            application_id,

        "agent_trace":
            trace,

        "candidate": {

            "name":
                candidate_name,

            "skills":
                candidate_skills,
        },

        "job":
            job,

        "match":
            match,

        "recruiter": {

            "name":
                recruiter_name,

            "email":
                recruiter_email,
        },

        "message":
            message,
    }