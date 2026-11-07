from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class StudentBase(BaseModel):
    student_id: str
    name: Optional[str] = "Student"
    email: Optional[str] = None
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

class StudentRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=150)
    department: str = Field("CSE", min_length=2, max_length=50)
    semester: int = Field(7, ge=1, le=8)
    cgpa: float = Field(7.5, ge=0.0, le=10.0)
    tenth_percentage: float = Field(80.0, ge=0.0, le=100.0)
    twelfth_percentage: float = Field(80.0, ge=0.0, le=100.0)
    backlogs: int = Field(0, ge=0)
    python_score: float = Field(5.0, ge=0.0, le=10.0)
    java_score: float = Field(5.0, ge=0.0, le=10.0)
    sql_score: float = Field(5.0, ge=0.0, le=10.0)
    dsa_score: float = Field(5.0, ge=0.0, le=10.0)
    cloud_score: float = Field(4.0, ge=0.0, le=10.0)
    web_score: float = Field(5.0, ge=0.0, le=10.0)
    ml_score: float = Field(4.0, ge=0.0, le=10.0)
    cybersecurity_score: float = Field(3.0, ge=0.0, le=10.0)
    certifications: int = Field(1, ge=0)
    project_count: int = Field(2, ge=0)
    project_complexity: int = Field(1, ge=1, le=3)
    internships: int = Field(0, ge=0)
    opensource_projects: int = Field(0, ge=0)
    quantitative_aptitude: float = Field(6.0, ge=0.0, le=10.0)
    logical_aptitude: float = Field(6.0, ge=0.0, le=10.0)
    coding_score: float = Field(5.5, ge=0.0, le=10.0)
    communication_score: float = Field(6.0, ge=0.0, le=10.0)
    presentation_score: float = Field(6.0, ge=0.0, le=10.0)
    interview_score: float = Field(6.0, ge=0.0, le=10.0)
    hackathons: int = Field(0, ge=0)
    leadership: int = Field(0, ge=0, le=1)
    target_role: str = Field("Data Analyst", min_length=2)

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

class StudentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, min_length=2, max_length=50)
    semester: Optional[int] = Field(None, ge=1, le=8)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    tenth_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    twelfth_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    backlogs: Optional[int] = Field(None, ge=0)
    python_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    java_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    sql_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    dsa_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    cloud_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    web_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    ml_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    cybersecurity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    certifications: Optional[int] = Field(None, ge=0)
    project_count: Optional[int] = Field(None, ge=0)
    project_complexity: Optional[int] = Field(None, ge=1, le=3)
    internships: Optional[int] = Field(None, ge=0)
    opensource_projects: Optional[int] = Field(None, ge=0)
    quantitative_aptitude: Optional[float] = Field(None, ge=0.0, le=10.0)
    logical_aptitude: Optional[float] = Field(None, ge=0.0, le=10.0)
    coding_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    communication_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    presentation_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    interview_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    hackathons: Optional[int] = Field(None, ge=0)
    leadership: Optional[int] = Field(None, ge=0, le=1)
    target_role: Optional[str] = Field(None, min_length=2)

