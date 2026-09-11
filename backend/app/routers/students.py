import sqlite3
import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.database import get_db
from app.schemas import StudentBase
from app.services.model_service import model_service
from app.services.intelligence_engine import calculate_career_fit, calculate_why_not_yet, calculate_opportunity_cost, calculate_minimum_improvement

router = APIRouter(prefix="/api/students", tags=["students"])

@router.get("")
def list_students(dept: str = None, status: str = None, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM students"
    params = []
    
    if dept:
        query += " WHERE department = ?"
        params.append(dept)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    students = [dict(row) for row in rows]

    # Calculate prediction status for list filtering if requested
    result = []
    batch_preds = model_service.predict_batch(students)

    for s, pred in zip(students, batch_preds):
        s["readiness_score"] = pred["readiness_score"]
        s["status"] = pred["status"]

        if status and s["status"] != status:
            continue
        result.append(s)

    return {"count": len(result), "students": result}

@router.get("/{student_id}")
def get_student_detail(student_id: str, include_heavy: bool = False, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student_dict = dict(row)
    pred = model_service.predict(student_dict)
    career_fit = calculate_career_fit(student_dict)
    why_not_yet = calculate_why_not_yet(student_dict, student_dict.get("target_role", "Data Analyst"), pred["all_shap"])
    
    # Heavy combinatorial searches loaded lazily on sub-tab navigation
    opp_cost = calculate_opportunity_cost(student_dict) if include_heavy else []
    mvi = calculate_minimum_improvement(student_dict, target_score=75.0) if include_heavy else None

    # Fetch trajectory snapshots directly from DB without re-running ML model
    cursor.execute("SELECT month, readiness_score, status FROM trajectory_snapshots WHERE student_id = ? ORDER BY id ASC", (student_id,))
    traj_rows = cursor.fetchall()
    trajectory = [dict(t) for t in traj_rows]

    return {
        "student": student_dict,
        "prediction": pred,
        "career_fit": career_fit,
        "why_not_yet": why_not_yet,
        "opportunity_cost": opp_cost,
        "minimum_improvement": mvi,
        "trajectory": trajectory,
        "data_provenance": "SYNTHETIC"
    }

@router.post("/validate-csv")
async def validate_students_csv(file: UploadFile = File(...), db: sqlite3.Connection = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV format")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    required_cols = ["cgpa", "python_score", "sql_score", "dsa_score", "department"]
    missing = [c for c in required_cols if c not in df.columns]

    errors = []
    seen_ids = set()
    duplicate_ids_count = 0
    valid_rows_count = 0
    invalid_rows_count = 0

    cursor = db.cursor()
    cursor.execute("SELECT student_id FROM students")
    existing_db_ids = set(row[0] for row in cursor.fetchall())

    preview_rows = []

    for idx, row in df.iterrows():
        row_num = idx + 2 # 1-indexed plus header row
        has_error = False
        sid = str(row.get("student_id", f"ST_CSV_{idx+1:04d}")).strip()

        if sid in seen_ids:
            duplicate_ids_count += 1
            errors.append({
                "row": row_num,
                "column": "student_id",
                "value": sid,
                "error": "Duplicate student ID in CSV"
            })
            has_error = True
        else:
            seen_ids.add(sid)

        # Check CGPA
        try:
            cgpa_val = float(row.get("cgpa", 7.0))
            if cgpa_val < 0.0 or cgpa_val > 10.0:
                errors.append({
                    "row": row_num,
                    "column": "cgpa",
                    "value": str(row.get("cgpa")),
                    "error": "CGPA must be between 0 and 10"
                })
                has_error = True
        except (ValueError, TypeError):
            errors.append({
                "row": row_num,
                "column": "cgpa",
                "value": str(row.get("cgpa")),
                "error": "CGPA must be a valid numeric score"
            })
            has_error = True

        # Check Skill Scores
        for skill_col in ["python_score", "sql_score", "dsa_score"]:
            if skill_col in df.columns:
                try:
                    s_val = float(row.get(skill_col, 5.0))
                    if s_val < 0.0 or s_val > 10.0:
                        errors.append({
                            "row": row_num,
                            "column": skill_col,
                            "value": str(row.get(skill_col)),
                            "error": "Score must be between 0 and 10"
                        })
                        has_error = True
                except (ValueError, TypeError):
                    errors.append({
                        "row": row_num,
                        "column": skill_col,
                        "value": str(row.get(skill_col)),
                        "error": f"Invalid numeric format for {skill_col}"
                    })
                    has_error = True

        if has_error:
            invalid_rows_count += 1
        else:
            valid_rows_count += 1
            if len(preview_rows) < 10:
                preview_rows.append({
                    "student_id": sid,
                    "name": str(row.get("name", f"Student {sid}")),
                    "department": str(row.get("department", "CSE")),
                    "cgpa": float(row.get("cgpa", 7.0)),
                    "python_score": float(row.get("python_score", 5.0)),
                    "sql_score": float(row.get("sql_score", 5.0)),
                    "dsa_score": float(row.get("dsa_score", 5.0)),
                    "target_role": str(row.get("target_role", "Data Analyst"))
                })

    return {
        "filename": file.filename,
        "filesize_bytes": len(content),
        "total_rows": len(df),
        "valid_rows": valid_rows_count,
        "invalid_rows": invalid_rows_count,
        "duplicate_ids": duplicate_ids_count,
        "missing_columns": missing,
        "errors": errors[:50], # Cap error display at top 50
        "preview": preview_rows
    }

@router.post("/upload")
async def upload_students_csv(file: UploadFile = File(...), db: sqlite3.Connection = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV format")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    required_cols = ["cgpa", "python_score", "sql_score", "dsa_score", "department"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV missing required columns: {missing}")

    cursor = db.cursor()
    inserted_count = 0
    rejected_count = 0

    try:
        cursor.execute("BEGIN TRANSACTION;")
        for idx, row in df.iterrows():
            # Basic row validation check
            try:
                cgpa = float(row.get("cgpa", 7.0))
                sql_score = float(row.get("sql_score", 5.0))
                python_score = float(row.get("python_score", 5.0))
                dsa_score = float(row.get("dsa_score", 5.0))

                if cgpa < 0.0 or cgpa > 10.0 or sql_score < 0.0 or sql_score > 10.0:
                    rejected_count += 1
                    continue
            except (ValueError, TypeError):
                rejected_count += 1
                continue

            sid = str(row.get("student_id", f"ST_CSV_{idx+1:04d}")).strip()
            name = str(row.get("name", f"Student {sid}"))
            dept = str(row.get("department", "CSE"))
            target_role = str(row.get("target_role", "Data Analyst"))

            cursor.execute("""
            INSERT OR REPLACE INTO students (
                student_id, name, department, semester, cgpa, tenth_percentage, twelfth_percentage,
                backlogs, python_score, java_score, sql_score, dsa_score, cloud_score, web_score,
                ml_score, cybersecurity_score, certifications, project_count, project_complexity,
                internships, opensource_projects, quantitative_aptitude, logical_aptitude,
                coding_score, communication_score, presentation_score, interview_score, hackathons,
                leadership, target_role, placed, data_source, profile_completeness, evidence_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sid, name, dept, int(row.get("semester", 7)),
                cgpa, float(row.get("tenth_percentage", 80.0)), float(row.get("twelfth_percentage", 80.0)),
                int(row.get("backlogs", 0)), python_score, float(row.get("java_score", 5.0)),
                sql_score, dsa_score, float(row.get("cloud_score", 4.0)), float(row.get("web_score", 5.0)),
                float(row.get("ml_score", 4.0)), float(row.get("cybersecurity_score", 3.0)),
                int(row.get("certifications", 1)), int(row.get("project_count", 2)), int(row.get("project_complexity", 1)),
                int(row.get("internships", 0)), int(row.get("opensource_projects", 0)),
                float(row.get("quantitative_aptitude", 6.0)), float(row.get("logical_aptitude", 6.0)),
                float(row.get("coding_score", 5.5)), float(row.get("communication_score", 6.0)),
                float(row.get("presentation_score", 6.0)), float(row.get("interview_score", 6.0)),
                int(row.get("hackathons", 0)), int(row.get("leadership", 0)), target_role, 0,
                "IMPORTED", 85.0, 75.0
            ))
            inserted_count += 1

        db.commit()
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction failed and was rolled back: {str(err)}")

    return {
        "message": f"Successfully ingested {inserted_count} student records.",
        "imported": inserted_count,
        "rejected": rejected_count,
        "data_provenance": "IMPORTED"
    }
