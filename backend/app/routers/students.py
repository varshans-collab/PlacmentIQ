import sqlite3
import io
import uuid
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.database import get_db
from app.schemas import StudentBase, StudentRegisterRequest, StudentUpdateRequest
from app.services.model_service import model_service
from app.services.intelligence_engine import calculate_career_fit, calculate_why_not_yet, calculate_opportunity_cost, calculate_minimum_improvement
from app.services.auth_service import get_current_user, require_tpo, verify_student_ownership

router = APIRouter(prefix="/api/students", tags=["students"])

@router.post("/register")
def register_student(req: StudentRegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    email_clean = req.email.strip().lower()

    # Check for existing email in database
    cursor.execute("SELECT student_id, name, email FROM students WHERE LOWER(email) = ?", (email_clean,))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A student profile with this email address already exists. Please sign in instead."
        )

    # Generate collision-safe unique ST_USR_ ID
    while True:
        candidate_id = f"ST_USR_{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (candidate_id,))
        if not cursor.fetchone():
            student_id = candidate_id
            break

    student_data = {
        "student_id": student_id,
        "name": req.name.strip(),
        "email": email_clean,
        "department": req.department,
        "semester": req.semester,
        "cgpa": req.cgpa,
        "tenth_percentage": req.tenth_percentage,
        "twelfth_percentage": req.twelfth_percentage,
        "backlogs": req.backlogs,
        "python_score": req.python_score,
        "java_score": req.java_score,
        "sql_score": req.sql_score,
        "dsa_score": req.dsa_score,
        "cloud_score": req.cloud_score,
        "web_score": req.web_score,
        "ml_score": req.ml_score,
        "cybersecurity_score": req.cybersecurity_score,
        "certifications": req.certifications,
        "project_count": req.project_count,
        "project_complexity": req.project_complexity,
        "internships": req.internships,
        "opensource_projects": req.opensource_projects,
        "quantitative_aptitude": req.quantitative_aptitude,
        "logical_aptitude": req.logical_aptitude,
        "coding_score": req.coding_score,
        "communication_score": req.communication_score,
        "presentation_score": req.presentation_score,
        "interview_score": req.interview_score,
        "hackathons": req.hackathons,
        "leadership": req.leadership,
        "target_role": req.target_role,
        "placed": 0,
        "data_source": "USER_PROFILE",
        "profile_completeness": 95.0,
        "evidence_confidence": 80.0
    }

    try:
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("""
        INSERT INTO students (
            student_id, name, email, department, semester, cgpa, tenth_percentage, twelfth_percentage,
            backlogs, python_score, java_score, sql_score, dsa_score, cloud_score, web_score,
            ml_score, cybersecurity_score, certifications, project_count, project_complexity,
            internships, opensource_projects, quantitative_aptitude, logical_aptitude,
            coding_score, communication_score, presentation_score, interview_score, hackathons,
            leadership, target_role, placed, data_source, profile_completeness, evidence_confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_data["student_id"], student_data["name"], student_data["email"], student_data["department"],
            student_data["semester"], student_data["cgpa"], student_data["tenth_percentage"], student_data["twelfth_percentage"],
            student_data["backlogs"], student_data["python_score"], student_data["java_score"], student_data["sql_score"],
            student_data["dsa_score"], student_data["cloud_score"], student_data["web_score"], student_data["ml_score"],
            student_data["cybersecurity_score"], student_data["certifications"], student_data["project_count"],
            student_data["project_complexity"], student_data["internships"], student_data["opensource_projects"],
            student_data["quantitative_aptitude"], student_data["logical_aptitude"], student_data["coding_score"],
            student_data["communication_score"], student_data["presentation_score"], student_data["interview_score"],
            student_data["hackathons"], student_data["leadership"], student_data["target_role"], student_data["placed"],
            student_data["data_source"], student_data["profile_completeness"], student_data["evidence_confidence"]
        ))

        pred = model_service.predict(student_data)
        cursor.execute("""
        INSERT INTO trajectory_snapshots (student_id, month, readiness_score, status)
        VALUES (?, ?, ?, ?)
        """, (student_id, "September", pred["readiness_score"], pred["status"]))

        db.commit()
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register student: {str(err)}")

    return {
        "success": True,
        "message": "Student twin registered and diagnostic calculated successfully.",
        "student_id": student_id,
        "user": {
            "id": student_id,
            "name": student_data["name"],
            "email": student_data["email"]
        },
        "prediction": pred
    }

@router.get("")
def list_students(
    dept: str = None,
    status: str = None,
    current_user: dict = Depends(require_tpo),
    db: sqlite3.Connection = Depends(get_db)
):
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
def get_student_detail(
    student_id: str,
    include_heavy: bool = False,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    verify_student_ownership(student_id, current_user)
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

@router.put("/{student_id}")
def update_student_profile(
    student_id: str,
    req: StudentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    verify_student_ownership(student_id, current_user)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student_dict = dict(row)

    # Update fields provided in request
    update_data = req.model_dump(exclude_unset=True) if hasattr(req, "model_dump") else req.dict(exclude_unset=True)
    for k, v in update_data.items():
        if v is not None and k in student_dict:
            student_dict[k] = v

    # Re-predict using existing ModelService pipeline
    pred = model_service.predict(student_dict)

    # Persist updated profile to students table
    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys() if k in student_dict])
    if set_clause:
        values = [student_dict[k] for k in update_data.keys() if k in student_dict]
        values.append(student_id)
        cursor.execute(f"UPDATE students SET {set_clause} WHERE student_id = ?", values)

    # Update latest trajectory snapshot
    cursor.execute(
        "UPDATE trajectory_snapshots SET readiness_score = ?, status = ? WHERE student_id = ? AND month = 'September'",
        (pred["readiness_score"], pred["status"], student_id)
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO trajectory_snapshots (student_id, month, readiness_score, status) VALUES (?, 'September', ?, ?)",
            (student_id, pred["readiness_score"], pred["status"])
        )

    db.commit()

    career_fit = calculate_career_fit(student_dict)
    why_not_yet = calculate_why_not_yet(student_dict, student_dict.get("target_role", "Data Analyst"), pred["all_shap"])

    return {
        "success": True,
        "message": "Student profile updated successfully",
        "student": student_dict,
        "prediction": pred,
        "career_fit": career_fit,
        "why_not_yet": why_not_yet,
        "data_provenance": "USER_PROFILE"
    }

@router.post("/validate-csv")
async def validate_students_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_tpo),
    db: sqlite3.Connection = Depends(get_db)
):
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
async def upload_students_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_tpo),
    db: sqlite3.Connection = Depends(get_db)
):
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
