import os
import json
from typing import List, Union, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "backend", "model_artifacts")
DB_PATH = os.path.join(BASE_DIR, "backend", "placementiq.db")


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///backend/placementiq.db"
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    @field_validator("JWT_SECRET", mode="before")
    @classmethod
    def validate_jwt_secret(cls, v: Any) -> str:
        placeholder = "change-this-to-a-secure-random-secret-in-production"
        dev_placeholder = "dev-secret-key-placeholder-change-in-production"
        if not v or not str(v).strip():
            raise ValueError(
                "JWT_SECRET is missing or empty. A secure secret of at least 32 characters must be set in the environment or .env file."
            )
        v_clean = str(v).strip()
        if v_clean in (placeholder, dev_placeholder):
            raise ValueError(
                "Insecure JWT_SECRET: default placeholder text cannot be used. Please set a secure random secret in your environment or .env file."
            )
        if len(v_clean) < 32:
            raise ValueError(
                "Insecure JWT_SECRET: secret must be at least 32 characters long."
            )
        return v_clean

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                try:
                    return json.loads(v_trimmed)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

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
