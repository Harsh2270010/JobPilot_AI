import os

from datetime import date

import requests

import streamlit as st

from dotenv import load_dotenv

from pypdf import PdfReader

from database.db import (
    delete_application,
    init_db,
    list_applications,
    update_status,
)

from database.models import Application


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

init_db()

st.set_page_config(
    page_title="JobPilot AI",
    page_icon="🚀",
    layout="wide",
)


N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "http://localhost:5678/webhook/jobpilot-analyze",
)


# ============================================================
# SAMPLE JOB
# ============================================================

SAMPLE_JD = """
We are hiring a Junior AI/ML Engineer.

Requirements:
- 0-2 years of experience
- Strong Python programming
- Machine Learning and Deep Learning fundamentals
- SQL and REST APIs
- Experience with FastAPI or Flask
- Familiarity with Docker and AWS
- Good problem-solving skills

Location: Bengaluru
"""


# ============================================================
# RESUME
# ============================================================

def extract_pdf_text(
    uploaded_file,
):

    reader = PdfReader(
        uploaded_file
    )

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:

            pages.append(text)

    return "\n".join(
        pages
    )


def default_resume():

    return """
Name: Harsh Kumar

Education:
B.Tech AI & ML

Experience:
ML Intern
Python Automation Developer

Skills:
Python
C++
R
MySQL
Machine Learning
Deep Learning
TensorFlow
PyTorch
Scikit-learn
OpenCV
YOLO
NLP
LangChain
LLMs
Agentic AI
FastAPI
Flask
Django
Streamlit
Git
GitHub
Pandas
NumPy
Matplotlib
Power BI
Tableau
"""


# ============================================================
# N8N REQUEST
# ============================================================

def run_n8n_workflow(

    company,

    recruiter_name,

    recruiter_email,

    job_description,

    resume_text,

):

    payload = {

        "company":
            company,

        "recruiter_name":
            recruiter_name,

        "recruiter_email":
            recruiter_email,

        "job_description":
            job_description,

        "resume_text":
            resume_text,

        "application_date":
            str(date.today()),
    }

    response = requests.post(

        N8N_WEBHOOK_URL,

        json=payload,

        timeout=120,
    )

    if not response.ok:

        raise RuntimeError(
            f"n8n returned "
            f"{response.status_code}: "
            f"{response.text}"
        )

    return response.json()


# ============================================================
# ANALYZER
# ============================================================

def show_analyzer():

    st.subheader(
        "🤖 Job Analyzer"
    )

    # --------------------------------------------------------
    # Company
    # --------------------------------------------------------

    company = st.text_input(

        "Company",

        placeholder=(
            "e.g. ABC Technologies"
        ),

        key="company_input",
    )

    # --------------------------------------------------------
    # Recruiter
    # --------------------------------------------------------

    recruiter_name = st.text_input(

        "Recruiter Name",

        placeholder=(
            "e.g. Rahul Sharma"
        ),

        key="recruiter_name_input",
    )

    recruiter_email = st.text_input(

        "Recruiter Email",

        placeholder=(
            "recruiter@company.com"
        ),

        key="recruiter_email_input",
    )

    # --------------------------------------------------------
    # Job Description
    # --------------------------------------------------------

    job_description = st.text_area(

        "Job Description",

        value=SAMPLE_JD,

        height=300,

        key="job_description_input",
    )

    # --------------------------------------------------------
    # Resume
    # --------------------------------------------------------

    resume_file = st.file_uploader(

        "Upload Resume",

        type=[
            "pdf",
            "txt",
        ],

        key="resume_upload",
    )

    if resume_file:

        try:

            if (
                resume_file.name
                .lower()
                .endswith(".pdf")
            ):

                resume_text = (
                    extract_pdf_text(
                        resume_file
                    )
                )

            else:

                resume_text = (
                    resume_file
                    .read()
                    .decode(
                        "utf-8",
                        errors="ignore",
                    )
                )

            st.success(
                "✅ Resume loaded successfully."
            )

            if not resume_text.strip():

                st.warning(
                    "The resume appears to contain "
                    "no extractable text."
                )

        except Exception as exc:

            st.error(
                "Could not read the resume."
            )

            st.exception(
                exc
            )

            return

    else:

        resume_text = default_resume()

        st.info(
            "No resume uploaded. "
            "Using the demo candidate profile."
        )

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    if st.button(

        "🚀 Run JobPilot Agent",

        type="primary",

        use_container_width=True,

    ):

        if not company.strip():

            st.error(
                "Company is required."
            )

            return

        if not job_description.strip():

            st.error(
                "Job description is required."
            )

            return

        if recruiter_email.strip():

            if "@" not in recruiter_email:

                st.error(
                    "Enter a valid recruiter email."
                )

                return

        try:

            with st.spinner(
                "JobPilot agent is working..."
            ):

                result = run_n8n_workflow(

                    company=
                        company,

                    recruiter_name=
                        recruiter_name,

                    recruiter_email=
                        recruiter_email,

                    job_description=
                        job_description,

                    resume_text=
                        resume_text,
                )

            st.session_state[
                "agent_result"
            ] = result

        except Exception as exc:

            st.error(
                "JobPilot workflow failed."
            )

            st.exception(
                exc
            )

            return

    result = st.session_state.get(
        "agent_result"
    )

    if not result:

        st.info(
            "Run the agent to see the result."
        )

        return

    # ========================================================
    # AGENT TRACE
    # ========================================================

    st.markdown(
        "## 🧠 Agent Activity"
    )

    for step in result.get(
        "agent_trace",
        [],
    ):

        st.success(
            f"✓ {step}"
        )

    # ========================================================
    # CANDIDATE
    # ========================================================

    candidate = result[
        "candidate"
    ]

    st.markdown(
        "### 👤 Candidate"
    )

    st.write(
        f"**Name:** "
        f"{candidate.get('name', 'Candidate')}"
    )

    # ========================================================
    # JOB + MATCH
    # ========================================================

    job = result[
        "job"
    ]

    match = result[
        "match"
    ]

    recruiter = result[
        "recruiter"
    ]

    left, right = st.columns(2)

    with left:

        st.markdown(
            "### 💼 Job Summary"
        )

        st.write(
            f"**Role:** "
            f"{job['role']}"
        )

        st.write(
            f"**Experience:** "
            f"{job['experience'] or 'Not specified'}"
        )

        st.write(
            f"**Location:** "
            f"{job['location'] or 'Not specified'}"
        )

        st.write(
            "**Required Skills:** "
            + (
                ", ".join(
                    job["skills"]
                )
                if job["skills"]
                else "None"
            )
        )

    with right:

        st.markdown(
            "### 🎯 Candidate Match"
        )

        st.metric(
            "Match Score",
            f"{match['score']:.0f}%",
        )

        if (
            match["recommendation"]
            == "APPLY"
        ):

            st.success(
                "### ✅ APPLY"
            )

        elif (
            match["recommendation"]
            == "APPLY WITH CAUTION"
        ):

            st.warning(
                "### ⚠️ APPLY WITH CAUTION"
            )

        else:

            st.error(
                "### ❌ SKIP"
            )

    # ========================================================
    # SKILLS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### ✅ Matched Skills"
        )

        if match["matched"]:

            for skill in match["matched"]:

                st.write(
                    f"✓ {skill}"
                )

        else:

            st.write(
                "None"
            )

    with col2:

        st.markdown(
            "### ❌ Missing Skills"
        )

        if match["missing"]:

            for skill in match["missing"]:

                st.write(
                    f"✗ {skill}"
                )

        else:

            st.write(
                "None"
            )

    # ========================================================
    # OUTREACH
    # ========================================================

    st.markdown(
        "## ✉️ LinkedIn / Email Outreach"
    )

    display_email = (
        recruiter.get("email")
        or recruiter_email
        or "Not provided"
    )

    st.write(
        f"**Recruiter:** "
        f"{recruiter.get('name') or 'Not provided'}"
    )

    st.write(
        f"**Recruiter Email:** "
        f"{display_email}"
    )

    st.text_area(

        "Generated Message",

        value=result["message"],

        height=240,

        key="generated_message",

    )


# ============================================================
# TRACKER
# ============================================================

def show_tracker():

    st.subheader(
        "📋 Application Tracker"
    )

    applications = list_applications()

    if not applications:

        st.info(
            "No applications saved yet."
        )

        return

    search = st.text_input(

        "Search company or role",

        placeholder=(
            "e.g. Google or AI Engineer"
        ),

        key="tracker_search",
    )

    shown = 0

    for application in applications:

        company = application[
            "company"
        ]

        role = application[
            "role"
        ]

        if search:

            query = search.lower()

            if (
                query
                not in company.lower()

                and

                query
                not in role.lower()
            ):

                continue

        shown += 1

        with st.container(
            border=True
        ):

            c1, c2, c3, c4, c5 = st.columns(
                [
                    2,
                    2,
                    1.2,
                    1.8,
                    0.7,
                ]
            )

            c1.write(
                f"**{company}**"
            )

            c2.write(
                role
            )

            c3.metric(
                "Match",
                f"{application['match_score']:.0f}%",
            )

            current_status = (
                application["status"]
            )

            selected_status = c4.selectbox(

                "Status",

                Application.STATUSES,

                index=Application.STATUSES.index(
                    current_status
                ),

                key=(
                    f"status_"
                    f"{application['id']}"
                ),

                label_visibility="collapsed",
            )

            if (
                selected_status
                != current_status
            ):

                update_status(

                    application["id"],

                    selected_status,
                )

                st.rerun()

            if c5.button(

                "🗑️",

                key=(
                    f"delete_"
                    f"{application['id']}"
                ),
            ):

                delete_application(
                    application["id"]
                )

                st.rerun()

            with st.expander(
                "View Details"
            ):

                st.write(
                    f"**Recruiter:** "
                    f"{application['recruiter_name'] or 'Not provided'}"
                )

                st.write(
                    f"**Recruiter Email:** "
                    f"{application['recruiter_email'] or 'Not provided'}"
                )

                st.write(
                    f"**Application Date:** "
                    f"{application['application_date']}"
                )

                st.write(
                    f"**Matched Skills:** "
                    f"{application['matched_skills'] or 'None'}"
                )

                st.write(
                    f"**Missing Skills:** "
                    f"{application['missing_skills'] or 'None'}"
                )

                st.text_area(

                    "Generated Outreach",

                    application[
                        "generated_message"
                    ],

                    height=200,

                    disabled=True,

                    key=(
                        f"message_"
                        f"{application['id']}"
                    ),
                )

    if shown == 0:

        st.warning(
            "No applications match your search."
        )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    st.subheader(
        "📊 Dashboard"
    )

    applications = list_applications()

    total = len(
        applications
    )

    applied = sum(
        app["status"] == "Applied"
        for app in applications
    )

    assessment = sum(
        app["status"] == "Assessment"
        for app in applications
    )

    interviews = sum(
        app["status"] == "Interview"
        for app in applications
    )

    rejected = sum(
        app["status"] == "Rejected"
        for app in applications
    )

    offers = sum(
        app["status"] == "Offer"
        for app in applications
    )

    average_match = (

        round(

            sum(
                app["match_score"]
                for app in applications
            )
            / total

        )

        if total

        else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Applications",
        total,
    )

    c2.metric(
        "Applied",
        applied,
    )

    c3.metric(
        "Assessments",
        assessment,
    )

    c4.metric(
        "Interviews",
        interviews,
    )

    c5.metric(
        "Avg Match",
        f"{average_match}%",
    )

    if not applications:

        st.info(
            "No application data yet."
        )

        return

    st.markdown(
        "### Application Pipeline"
    )

    rows = []

    for application in applications:

        rows.append(

            {
                "Company":
                    application[
                        "company"
                    ],

                "Role":
                    application[
                        "role"
                    ],

                "Match":
                    f"{application['match_score']:.0f}%",

                "Status":
                    application[
                        "status"
                    ],

                "Recruiter":
                    application[
                        "recruiter_email"
                    ] or "Not provided",
            }
        )

    st.dataframe(

        rows,

        use_container_width=True,

        hide_index=True,
    )


# ============================================================
# MAIN
# ============================================================

st.title(
    "🚀 JobPilot AI"
)

st.caption(
    "AI Job Application Productivity Agent"
)

st.markdown(
    """
**Analyze → Match → Decide → Generate Outreach → Save → Track**
"""
)

tab1, tab2, tab3 = st.tabs(

    [
        "🤖 Analyze Job",
        "📋 Application Tracker",
        "📊 Dashboard",
    ]
)

with tab1:

    show_analyzer()

with tab2:

    show_tracker()

with tab3:

    show_dashboard()