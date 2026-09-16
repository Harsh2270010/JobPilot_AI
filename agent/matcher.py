import re


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


ALIASES = {
    "scikit-learn": {
        "scikit learn",
        "sklearn",
    },
    "rest api": {
        "rest apis",
        "rest",
    },
    "machine learning": {
        "ml",
    },
    "deep learning": {
        "dl",
    },
    "natural language processing": {
        "nlp",
    },
}


def normalize(value: str) -> str:

    value = value.lower()

    value = value.replace(
        "-",
        " ",
    )

    value = value.replace(
        "_",
        " ",
    )

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def equivalent(
    skill_a: str,
    skill_b: str,
) -> bool:

    a = normalize(skill_a)
    b = normalize(skill_b)

    if a == b:
        return True

    if (
        a in ALIASES
        and b in ALIASES[a]
    ):
        return True

    if (
        b in ALIASES
        and a in ALIASES[b]
    ):
        return True

    if a in b or b in a:
        return True

    return False


def extract_candidate_name(
    resume_text: str,
) -> str:

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    # Check explicit labels first.
    for line in lines[:20]:

        lower = line.lower()

        labels = [
            "name:",
            "candidate name:",
            "full name:",
        ]

        for label in labels:

            if lower.startswith(label):

                name = line[
                    len(label):
                ].strip()

                if name:
                    return name

    # Fallback for resumes where the name is simply
    # the first heading.
    for line in lines[:10]:

        words = line.split()

        if 2 <= len(words) <= 4:

            valid = all(
                word.replace(
                    ".",
                    "",
                ).isalpha()
                for word in words
            )

            if valid:
                return line

    return "Candidate"


def extract_candidate_skills(
    resume_text: str,
) -> list[str]:

    lower_text = resume_text.lower()

    found = []

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

            found.append(skill)

    return list(
        dict.fromkeys(
            found
        )
    )


def match_profile(
    job_skills: list[str],
    candidate_skills: list[str],
):

    matched = []
    missing = []

    for job_skill in job_skills:

        is_match = any(
            equivalent(
                job_skill,
                candidate_skill,
            )
            for candidate_skill
            in candidate_skills
        )

        if is_match:
            matched.append(job_skill)
        else:
            missing.append(job_skill)

    total = len(job_skills)

    if total:
        score = round(
            len(matched)
            / total
            * 100,
            1,
        )
    else:
        score = 0

    if score >= 80:
        recommendation = "APPLY"

    elif score >= 60:
        recommendation = (
            "APPLY WITH CAUTION"
        )

    else:
        recommendation = "SKIP"

    return {
        "matched": matched,
        "missing": missing,
        "score": score,
        "recommendation": recommendation,
    }