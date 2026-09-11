import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "backend", "model_artifacts")
DB_PATH = os.path.join(BASE_DIR, "backend", "placementiq.db")

FEATURE_COLUMNS = [
    "cgpa", "tenth_percentage", "twelfth_percentage", "backlogs",
    "python_score", "java_score", "sql_score", "dsa_score", "cloud_score",
    "web_score", "ml_score", "cybersecurity_score", "certifications",
    "project_count", "project_complexity", "internships", "opensource_projects",
    "quantitative_aptitude", "logical_aptitude", "coding_score",
    "communication_score", "presentation_score", "interview_score",
    "hackathons", "leadership"
]

ROLE_BENCHMARKS = {
    "Data Analyst": {
        "sql_score": 8.0,
        "python_score": 7.5,
        "quantitative_aptitude": 7.5,
        "logical_aptitude": 7.5,
        "communication_score": 7.0,
        "project_count": 3,
        "internships": 1
    },
    "AI/ML Engineer": {
        "python_score": 9.0,
        "ml_score": 8.0,
        "dsa_score": 8.0,
        "quantitative_aptitude": 8.0,
        "project_complexity": 3,
        "project_count": 3,
        "internships": 1
    },
    "Full-Stack Developer": {
        "python_score": 7.5,
        "web_score": 8.5,
        "sql_score": 8.0,
        "dsa_score": 8.0,
        "coding_score": 8.0,
        "project_count": 4,
        "internships": 1
    },
    "Cloud/DevOps Engineer": {
        "cloud_score": 8.5,
        "python_score": 7.0,
        "sql_score": 7.0,
        "logical_aptitude": 7.5,
        "certifications": 2,
        "project_count": 3,
        "internships": 1
    },
    "QA Specialist": {
        "python_score": 6.5,
        "sql_score": 7.0,
        "logical_aptitude": 7.0,
        "communication_score": 7.5,
        "project_count": 2,
        "internships": 0
    },
    "Cybersecurity Specialist": {
        "cybersecurity_score": 8.5,
        "python_score": 7.0,
        "dsa_score": 7.0,
        "certifications": 2,
        "project_count": 3,
        "internships": 1
    }
}
