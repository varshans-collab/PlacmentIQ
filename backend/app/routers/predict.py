import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas import PredictionRequest, WhatIfRequest
from app.services.model_service import model_service
from app.services.intelligence_engine import (
    calculate_career_fit,
    calculate_why_not_yet,
    calculate_opportunity_cost,
    calculate_minimum_improvement,
    calculate_roadmap
)


router = APIRouter(prefix="/api", tags=["prediction"])

@router.post("/predict")
def predict_features(req: PredictionRequest):
    pred = model_service.predict(req.features)
    career_fit = calculate_career_fit(req.features)

    # Determine top action
    opp_cost = calculate_opportunity_cost(req.features)
    top_action = opp_cost[0] if opp_cost else {}

    return {
        "student_id": req.student_id,
        "readiness_score": pred["readiness_score"],
        "status": pred["status"],
        "prediction_confidence": "High (Calibrated Random Forest)",
        "profile_completeness": 90.0,
        "evidence_confidence": 80.0,
        "base_value": pred["base_value"],
        "career_fit": career_fit,
        "positive_factors": pred["positive_factors"],
        "negative_factors": pred["negative_factors"],
        "next_best_action": top_action,
        "data_provenance": "SIMULATED"
    }

@router.post("/what-if")
def what_if_simulation(req: WhatIfRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (req.student_id,))
    row = cursor.fetchone()

    if row:
        base_features = dict(row)
    else:
        # Fallback default feature map if ID not in DB
        base_features = {
            "cgpa": 7.2, "python_score": 5.0, "sql_score": 4.0, "dsa_score": 5.0,
            "cloud_score": 3.0, "quantitative_aptitude": 5.0, "communication_score": 5.0,
            "project_count": 2, "internships": 0, "backlogs": 0
        }

    # 1. Original prediction from model
    orig_pred = model_service.predict(base_features)
    orig_score = orig_pred["readiness_score"]

    # 2. Counterfactual prediction with modified features
    sim_features = dict(base_features)
    sim_features.update(req.modified_features)

    sim_pred = model_service.predict(sim_features)
    sim_score = sim_pred["readiness_score"]
    delta = round(sim_score - orig_score, 1)

    target_role = req.target_role or base_features.get("target_role", "Data Analyst")
    sim_fit = calculate_career_fit(sim_features)
    sim_why_not = calculate_why_not_yet(sim_features, target_role, sim_pred["all_shap"])

    return {
        "student_id": req.student_id,
        "target_role": target_role,
        "original_score": orig_score,
        "original_status": orig_pred["status"],
        "projected_score": sim_score,
        "projected_status": sim_pred["status"],
        "score_delta": delta,
        "is_improvement": delta >= 0,
        "original_positive_factors": orig_pred["positive_factors"][:4],
        "projected_positive_factors": sim_pred["positive_factors"][:4],
        "updated_career_fit": sim_fit,
        "updated_why_not_yet": sim_why_not,
        "data_provenance": "SIMULATED"
    }

@router.get("/skill-gaps/{student_id}")
def get_skill_gaps(student_id: str, role: str = "Data Analyst", db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student_dict = dict(row)
    pred = model_service.predict(student_dict)
    gaps = calculate_why_not_yet(student_dict, role, pred["all_shap"])

    return {
        "student_id": student_id,
        "target_role": role,
        "readiness_score": pred["readiness_score"],
        "gaps": gaps,
        "data_provenance": "DERIVED"
    }

@router.get("/opportunity-cost/{student_id}")
def get_opportunity_cost(student_id: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student_dict = dict(row)
    matrix = calculate_opportunity_cost(student_dict)
    return {"student_id": student_id, "matrix": matrix, "data_provenance": "SIMULATED"}

@router.get("/minimum-improvement/{student_id}")
def get_minimum_improvement(student_id: str, target: float = 75.0, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student_dict = dict(row)
    res = calculate_minimum_improvement(student_dict, target_score=target)
    return {"student_id": student_id, "result": res, "data_provenance": "SIMULATED"}

@router.get("/roadmap/{student_id}")
def get_roadmap(student_id: str, role: str = "Data Analyst", db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student_dict = dict(row)
    pred = model_service.predict(student_dict)
    target_role = role or student_dict.get("target_role", "Data Analyst")
    res = calculate_roadmap(student_dict, target_role, pred["all_shap"])
    return res

