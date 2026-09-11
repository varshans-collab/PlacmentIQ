import os
import json
import sqlite3
from fastapi import APIRouter, Depends
from app.config import ARTIFACTS_DIR, DATA_DIR
from app.database import get_db
from app.schemas import ResumeExtractRequest, AssessmentSubmitRequest
from app.services.resume_extractor import extract_resume_skills

router = APIRouter(prefix="/api", tags=["tools"])

@router.post("/resume/extract")
def extract_resume(req: ResumeExtractRequest):
    return extract_resume_skills(req.resume_text)

@router.post("/assessment")
def submit_assessment(req: AssessmentSubmitRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO assessment_results (student_id, skill, difficulty, score, passed)
    VALUES (?, ?, ?, ?, ?)
    """, (req.student_id, req.skill, req.difficulty, req.score, 1 if req.passed else 0))

    # Update evidence_confidence on student profile
    cursor.execute("UPDATE students SET evidence_confidence = MIN(99.0, evidence_confidence + 5.0) WHERE student_id = ?", (req.student_id,))
    db.commit()

    return {
        "message": f"Assessment recorded for {req.skill} ({req.difficulty}). Evidence confidence increased.",
        "student_id": req.student_id,
        "data_provenance": "DERIVED"
    }

@router.get("/model-info")
def get_model_info():
    gov_path = os.path.join(ARTIFACTS_DIR, "governance_metrics.json")
    ameo_path = os.path.join(DATA_DIR, "ameo_sample_benchmark.json")

    gov_metrics = {}
    if os.path.exists(gov_path):
        with open(gov_path, "r") as f:
            gov_metrics = json.load(f)

    ameo_meta = {}
    if os.path.exists(ameo_path):
        with open(ameo_path, "r") as f:
            ameo_meta = json.load(f)

    return {
        "model_governance": gov_metrics,
        "ameo_benchmark_metadata": ameo_meta,
        "dataset_architecture": {
            "layer_a_observed": "AMEO 2015 Public Benchmark Dataset",
            "layer_b_synthetic_training": "5,000 Synthetic Student Profiles (Calibrated RF)",
            "layer_b_demo_cohort": "600 Student Institutional Cohort",
            "layer_c_counterfactual": "Dynamic What-If & Flight Simulator Interventions"
        },
        "provenance_labels": {
            "OBSERVED": "Data obtained from actual public/source dataset (AMEO 2015).",
            "SYNTHETIC": "Computer-generated prototype data covering 25+ student features.",
            "DERIVED": "Calculated indicators (Career fit, Evidence confidence, Skill gaps).",
            "SIMULATED": "Counterfactual model predictions, What-If, and Flight Simulator scenarios."
        }
    }
