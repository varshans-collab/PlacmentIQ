from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class StudentBase(BaseModel):
    student_id: str
    name: Optional[str] = "Student"
    department: str
    semester: int
    cgpa: float
    tenth_percentage: float
    twelfth_percentage: float
    backlogs: int
    python_score: float
    java_score: float
    sql_score: float
    dsa_score: float
    cloud_score: float
    web_score: float
    ml_score: float
    cybersecurity_score: float
    certifications: int
    project_count: int
    project_complexity: int
    internships: int
    opensource_projects: int
    quantitative_aptitude: float
    logical_aptitude: float
    coding_score: float
    communication_score: float
    presentation_score: float
    interview_score: float
    hackathons: int
    leadership: int
    target_role: str
    placed: Optional[int] = 0
    data_source: Optional[str] = "SYNTHETIC"
    profile_completeness: Optional[float] = 85.0
    evidence_confidence: Optional[float] = 75.0

class PredictionRequest(BaseModel):
    student_id: Optional[str] = "CUSTOM"
    features: Dict[str, float]

class WhatIfRequest(BaseModel):
    student_id: str
    modified_features: Dict[str, float]
    target_role: Optional[str] = None

class ShapContribution(BaseModel):
    feature: str
    feature_name: str
    val: float
    shap_value: float
    is_positive: bool

class PredictionResponse(BaseModel):
    student_id: str
    readiness_score: float
    status: str
    prediction_confidence: str
    profile_completeness: float
    evidence_confidence: float
    base_value: float
    career_fit: Dict[str, float]
    positive_factors: List[ShapContribution]
    negative_factors: List[ShapContribution]
    next_best_action: Dict[str, Any]
    data_provenance: str = "SIMULATED"

class SimulatorConfigRequest(BaseModel):
    target_role: str = "Data Analyst"
    department: Optional[str] = "ALL"
    batch_size: int = 600
    eligibility_cgpa: float = 7.0
    eligibility_max_backlogs: int = 0
    aptitude_threshold: float = 6.0
    technical_threshold: float = 6.5
    interview_threshold: float = 6.5

class InterventionCompareRequest(BaseModel):
    config: SimulatorConfigRequest
    selected_interventions: List[str]

class ResumeExtractRequest(BaseModel):
    resume_text: str

class AssessmentSubmitRequest(BaseModel):
    student_id: str
    skill: str
    difficulty: str
    score: float
    passed: bool
