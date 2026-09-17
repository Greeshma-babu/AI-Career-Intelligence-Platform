from collections import Counter
import re

from app.api.adzuna_client import AdzunaClient

# ============================================================
# TRACKED SKILLS
# ============================================================

TRACKED_SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Generative AI",
    "GenAI",
    "LLM",
    "RAG",
    "LangChain",
    "LangGraph",
    "FastAPI",
    "Flask",
    "Django",
    "PyTorch",
    "TensorFlow",
    "Scikit-learn",
    "NLP",
    "Computer Vision",
    "OpenCV",
    "YOLO",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "GitHub",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "REST API",
    "API",
    "Selenium",
    "Playwright",
    "Appium",
    "MLOps",
    "DevOps",
]


# ============================================================
# TRACKED JOB ROLES
# ============================================================

TRACKED_ROLES = [
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Scientist",
    "Data Engineer",
    "Generative AI Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "Software Engineer",
    "Backend Engineer",
    "Python Developer",
    "DevOps Engineer",
    "MLOps Engineer",
    "QA Engineer",
    "Automation Engineer",
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================


def normalize_text(text):
    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text).lower(),
    ).strip()


# ============================================================
# EXTRACT SKILLS FROM JOBS
# ============================================================


def extract_skills(jobs):

    skill_counter = Counter()

    for job in jobs:

        title = job.get("title", "")

        description = job.get(
            "description",
            "",
        )

        combined_text = normalize_text(f"{title} {description}")

        for skill in TRACKED_SKILLS:

            pattern = r"\b" + re.escape(skill.lower()) + r"\b"

            if re.search(
                pattern,
                combined_text,
            ):
                skill_counter[skill] += 1

    return skill_counter


# ============================================================
# EXTRACT JOB ROLES
# ============================================================


def extract_roles(jobs):

    role_counter = Counter()

    for job in jobs:

        title = normalize_text(job.get("title", ""))

        for role in TRACKED_ROLES:

            if role.lower() in title:

                role_counter[role] += 1

    return role_counter


# ============================================================
# BUILD SKILL TRENDS
# ============================================================


def build_skill_trends(
    skill_counter,
    total_jobs,
):

    trends = []

    for skill, count in skill_counter.most_common():

        percentage = 0

        if total_jobs > 0:
            percentage = round(
                (count / total_jobs) * 100,
                2,
            )

        trends.append(
            {
                "skill": skill,
                "job_count": count,
                "percentage": percentage,
            }
        )

    return trends


# ============================================================
# BUILD ROLE TRENDS
# ============================================================


def build_role_trends(
    role_counter,
    total_jobs,
):

    trends = []

    for role, count in role_counter.most_common():

        percentage = 0

        if total_jobs > 0:
            percentage = round(
                (count / total_jobs) * 100,
                2,
            )

        trends.append(
            {
                "role": role,
                "job_count": count,
                "percentage": percentage,
            }
        )

    return trends


# ============================================================
# SALARY STATISTICS
# ============================================================


def calculate_salary_statistics(jobs):

    salaries = []

    for job in jobs:

        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if salary_min is not None:

            try:
                salaries.append(float(salary_min))
            except (
                TypeError,
                ValueError,
            ):
                pass

        if salary_max is not None:

            try:
                salaries.append(float(salary_max))
            except (
                TypeError,
                ValueError,
            ):
                pass

    if not salaries:

        return {
            "available": False,
            "average": None,
            "minimum": None,
            "maximum": None,
        }

    return {
        "available": True,
        "average": round(
            sum(salaries) / len(salaries),
            2,
        ),
        "minimum": min(salaries),
        "maximum": max(salaries),
    }


# ============================================================
# GET MARKET TRENDS
# ============================================================


def get_market_trends(
    query="AI Engineer",
    country="in",
    pages=2,
    results_per_page=50,
    location=None,
):

    # --------------------------------------------------------
    # Create Adzuna client only when Market Trends is called
    # --------------------------------------------------------

    adzuna_client = AdzunaClient()

    all_jobs = []

    # --------------------------------------------------------
    # Fetch jobs
    # --------------------------------------------------------

    for page in range(
        1,
        pages + 1,
    ):

        response = adzuna_client.search_jobs(
            country=country,
            query=query,
            page=page,
            results_per_page=results_per_page,
            location=location,
        )

        jobs = response.get(
            "results",
            [],
        )

        all_jobs.extend(jobs)

        if not jobs:
            break

    # --------------------------------------------------------
    # Total jobs
    # --------------------------------------------------------

    total_jobs = len(all_jobs)

    # --------------------------------------------------------
    # Skill analysis
    # --------------------------------------------------------

    skill_counter = extract_skills(all_jobs)

    skill_trends = build_skill_trends(
        skill_counter,
        total_jobs,
    )

    # --------------------------------------------------------
    # Role analysis
    # --------------------------------------------------------

    role_counter = extract_roles(all_jobs)

    role_trends = build_role_trends(
        role_counter,
        total_jobs,
    )

    # --------------------------------------------------------
    # Salary analysis
    # --------------------------------------------------------

    salary_statistics = calculate_salary_statistics(all_jobs)

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "query": query,
        "country": country,
        "location": location,
        "total_jobs": total_jobs,
        "top_skills": skill_trends[:10],
        "top_roles": role_trends[:10],
        "salary_statistics": salary_statistics,
        "jobs": all_jobs,
    }
