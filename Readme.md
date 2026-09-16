# JobPilot AI

**JobPilot AI** is an AI-powered job application productivity agent that helps job seekers analyze job descriptions, compare them with their resume, calculate a transparent compatibility score, generate personalized recruiter outreach, and track applications from a single dashboard.

The project combines **Streamlit**, **n8n**, **FastAPI**, **Groq**, and **SQLite** into an agent-style workflow.

## Features

### 1. Job Description Analysis

JobPilot analyzes a job description and extracts:

* Job role
* Required technical skills
* Experience requirements
* Location

Groq is used for structured extraction when an API key is available, with a deterministic fallback parser for resilience.

### 2. Resume Analysis

The uploaded resume is processed to extract:

* Candidate name
* Candidate technical skills

PDF resumes are supported using `pypdf`.

### 3. Skill Matching

The agent compares the candidate's skills against the skills identified from the job description.

It calculates:

* Matched skills
* Missing skills
* Match percentage
* Recommendation

The recommendation logic is deterministic:

| Match Score  | Recommendation     |
| ------------ | ------------------ |
| 80% or above | APPLY              |
| 60% - 79%    | APPLY WITH CAUTION |
| Below 60%    | SKIP               |

### 4. Personalized Outreach Generation

For suitable opportunities, JobPilot generates a professional recruiter outreach message based on:

* Candidate name
* Company
* Role
* Matching skills
* Missing skills

The system does not invent experience, achievements, or skills.

### 5. Application Tracking

Every analyzed opportunity can be stored in SQLite with:

* Company
* Role
* Recruiter name
* Recruiter email
* Match score
* Matched skills
* Missing skills
* Generated message
* Application status
* Application date
* Notes

Available statuses:

`Not Applied`, `Applied`, `Assessment`, `Interview`, `Rejected`, `Offer`

### 6. Dashboard

The Streamlit dashboard provides an overview of:

* Total applications
* Applied applications
* Assessments
* Interviews
* Average match score
* Recent applications

## Agent Workflow

```text
Resume + Job Description
          |
          v
     Streamlit UI
          |
          v
   n8n Cloud Webhook
          |
          v
   FastAPI Agent
          |
          +----------------------+
          |                      |
          v                      v
   Analyze Job JD         Analyze Resume
          |                      |
          +----------+-----------+
                     |
                     v
               Skill Matching
                     |
                     v
             Match Score
                     |
          +----------+----------+
          |          |          |
          v          v          v
        APPLY     CAUTION      SKIP
          |          |          |
          +----------+----------+
                     |
                     v
          Generate Outreach Message
                     |
                     v
              Save to SQLite
                     |
                     v
          Tracker + Dashboard
```

## n8n Workflow

n8n is used as the orchestration layer between the Streamlit application and the FastAPI agent.

The workflow contains three nodes:

```text
Webhook
   ↓
HTTP Request
   ↓
Respond to Webhook
```

### Webhook

Webhook path:

```text
jobpilot-analyze
```

The Streamlit application sends:

```json
{
  "company": "ABC Technologies",
  "recruiter_name": "Recruiter Name",
  "recruiter_email": "recruiter@example.com",
  "job_description": "Job description...",
  "resume_text": "Resume text...",
  "application_date": "2026-09-16"
}
```

### HTTP Request

The HTTP Request node sends the request to the publicly accessible FastAPI endpoint:

```text
https://YOUR_NGROK_URL/agent/run
```

For example:

```text
https://crewmate-judge-syndrome.ngrok-free.dev/agent/run
```

In n8n, use:

**Body Content Type:** JSON
**Specify Body:** Using Fields Below

Fields:

```text
company            → {{ $json.body.company }}
recruiter_name     → {{ $json.body.recruiter_name || '' }}
recruiter_email    → {{ $json.body.recruiter_email || '' }}
job_description    → {{ $json.body.job_description }}
resume_text        → {{ $json.body.resume_text || '' }}
application_date   → {{ $json.body.application_date }}
```

Using fields instead of manually constructing multiline raw JSON helps avoid JSON parsing errors.

## Project Structure

```text
JobPilot_AI/
│
├── app.py
├── requirements.txt
├── .env
│
├── agent/
│   ├── __init__.py
│   ├── jd_analyzer.py
│   ├── matcher.py
│   └── message_generator.py
│
├── backend/
│   ├── __init__.py
│   └── main.py
│
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
│
├── services/
│   ├── __init__.py
│   └── application_service.py
│
├── data/
│   └── jobpilot.db
│
└── n8n/
    └── JobPilot_n8n_workflow.json
```

## Technologies Used

* **Python 3.11+**
* **Streamlit** - Frontend and dashboard
* **FastAPI** - Backend API and agent execution
* **n8n Cloud** - Workflow orchestration
* **Groq** - LLM-based job description analysis and message generation
* **SQLite** - Application persistence
* **pypdf** - Resume PDF extraction
* **Pydantic** - API data validation
* **Requests** - HTTP communication
* **python-dotenv** - Environment configuration

## Installation

Clone or copy the project:

```bash
git clone <your-repository-url>
cd JobPilot_AI
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=llama-3.1-8b-instant
N8N_WEBHOOK_URL=https://YOUR_N8N_DOMAIN/webhook/jobpilot-analyze
```

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
N8N_WEBHOOK_URL=https://harsh7877.app.n8n.cloud/webhook/jobpilot-analyze
```

Do not commit your real API key to GitHub.

## Running the Project

### Step 1: Start FastAPI

From the project root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Step 2: Start ngrok

Because n8n Cloud cannot directly access `localhost`, expose FastAPI through ngrok:

```bash
ngrok http 8000
```

ngrok will provide a public HTTPS URL such as:

```text
https://your-random-url.ngrok-free.dev
```

Use that URL in the n8n HTTP Request node:

```text
https://your-random-url.ngrok-free.dev/agent/run
```

The ngrok URL can change when the tunnel is restarted.

### Step 3: Activate the n8n Workflow

Import:

```text
n8n/JobPilot_n8n_workflow.json
```

into n8n Cloud.

Make sure the webhook is active and the HTTP Request node points to the current ngrok URL.

### Step 4: Start Streamlit

Open another terminal:

```bash
streamlit run app.py
```

The Streamlit interface will open in your browser.

## How to Use

1. Enter the company name.
2. Enter recruiter information when available.
3. Paste the job description.
4. Upload your resume in PDF or TXT format.
5. Click the analysis button.
6. JobPilot sends the request through n8n.
7. FastAPI runs the agent workflow.
8. The job requirements are extracted.
9. Resume skills and candidate name are extracted.
10. Skills are compared.
11. A deterministic match score and recommendation are generated.
12. A personalized outreach message is created for suitable opportunities.
13. The application is saved automatically.
14. Review the result in the Tracker and Dashboard.

## Example Agent Output

```json
{
  "saved": true,
  "candidate": {
    "name": "Candidate",
    "skills": [
      "Python",
      "FastAPI",
      "Machine Learning",
      "SQL"
    ]
  },
  "job": {
    "role": "AI Engineer",
    "skills": [
      "Python",
      "FastAPI",
      "Machine Learning"
    ]
  },
  "match": {
    "matched": [
      "Python",
      "FastAPI",
      "Machine Learning"
    ],
    "missing": [],
    "score": 100,
    "recommendation": "APPLY"
  }
}
```

## Design Principles

### Deterministic Decision Logic

The final compatibility score is calculated using explicit skill-matching rules rather than allowing the LLM to decide the score.

This makes the recommendation easier to understand and demonstrate.

### LLM Where It Adds Value

Groq is used for tasks involving unstructured language:

* Job description interpretation
* Natural-language outreach generation

The core matching logic remains deterministic.

### Resilient Fallbacks

When Groq is unavailable, the application can still perform basic job-description parsing and skill matching using the fallback logic.

### Human-in-the-Loop

JobPilot assists with the application process but does not automatically submit job applications.

The user reviews the generated recommendation and outreach before taking action.

## Current Scope

The current version includes:

* Job description analysis
* Resume parsing
* Candidate skill extraction
* Skill matching
* Match scoring
* Apply / caution / skip recommendation
* Personalized outreach generation
* SQLite application tracking
* Streamlit dashboard
* n8n workflow orchestration

The current version does **not** include automatic email sending or recruiter-response handling.

## Troubleshooting

### n8n says the request resolves to a restricted IP

Do not use:

```text
http://127.0.0.1:8000
```

or:

```text
http://localhost:8000
```

n8n Cloud needs a publicly accessible endpoint.

Use your active ngrok URL:

```text
https://your-ngrok-url.ngrok-free.dev/agent/run
```

### n8n reports a JSON control-character error

Configure the HTTP Request node as:

```text
Body Content Type → JSON
Specify Body → Using Fields Below
```

Then map each field individually rather than manually writing multiline JSON.

### FastAPI returns 500

First check:

```text
http://127.0.0.1:8000/health
```

Then check the FastAPI terminal for the traceback.

### Resume name is showing as "Candidate"

The name extractor looks at the beginning of the resume for a name or name label.

A resume beginning with something such as:

```text
Name: Harsh Kumar
```

is easier for the extractor to identify.

### Generated message is saved but not visible

Check the application record in the Tracker. Older database records may contain an empty message if they were created by an earlier version of the application.

## Future Improvements

Possible future extensions include:

* Better resume section parsing
* More advanced semantic skill matching
* Job-source integrations
* Resume tailoring for individual jobs
* Duplicate-job detection
* Analytics by role, company, or skill
* Cloud database support
* Authentication and multi-user support

## License

This project is intended as an internship / portfolio prototype. Add an appropriate license before distributing it publicly.
