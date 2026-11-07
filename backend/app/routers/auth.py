import sqlite3
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from app.database import get_db
from app.services.password_service import hash_password, verify_password
from app.services.auth_service import create_access_token, get_current_user
from app.services.model_service import model_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])

DEMO_ALIASES = {
    "student@placementiq.demo": "ST_DEMO_001",
    "ananya@placementiq.demo": "ST_DEMO_001",
    "rahul@placementiq.demo": "ST_DEMO_002",
    "priya@placementiq.demo": "ST_DEMO_003",
    "sneha@placementiq.demo": "ST_DEMO_004",
    "arjun@placementiq.demo": "ST_DEMO_005",
    "meera@placementiq.demo": "ST_DEMO_006",
    "karan@placementiq.demo": "ST_DEMO_007",
    "divya@placementiq.demo": "ST_DEMO_008",
    "rohan@placementiq.demo": "ST_DEMO_009",
    "nisha@placementiq.demo": "ST_DEMO_010",
    "vivek@placementiq.demo": "ST_DEMO_011",
    "pooja@placementiq.demo": "ST_DEMO_012",
    "aditya@placementiq.demo": "ST_DEMO_013",
}


class LoginRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    role: Optional[str] = None


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)
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


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    email_clean = req.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valid email is required")
    if len(req.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")

    cursor = db.cursor()

    # Check for existing user in users table
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email_clean,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists. Please sign in instead."
        )

    # Check for existing student in students table
    cursor.execute("SELECT student_id FROM students WHERE LOWER(email) = ?", (email_clean,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student profile with this email address already exists. Please sign in instead."
        )

    # Generate collision-safe student ID
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

        pwd_hash = hash_password(req.password)
        cursor.execute("""
        INSERT INTO users (email, password_hash, role, student_id, is_active)
        VALUES (?, ?, 'student', ?, 1)
        """, (email_clean, pwd_hash, student_id))
        user_id = cursor.lastrowid

        db.commit()
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register account: {str(err)}"
        )

    access_token = create_access_token({
        "sub": str(user_id),
        "email": email_clean,
        "role": "student",
        "student_id": student_id
    })

    return {
        "success": True,
        "message": "Student account registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "token": access_token,
        "user": {
            "id": user_id,
            "user_id": user_id,
            "email": email_clean,
            "role": "student",
            "student_id": student_id,
            "name": student_data["name"],
            "department": student_data["department"],
            "target_role": student_data["target_role"]
        }
    }


@router.post("/login")
def login(req: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    email_clean = req.email.strip().lower()
    if not email_clean:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    cursor = db.cursor()

    # Resolve demo alias or ST_ student ID
    lookup_email = email_clean
    lookup_sid = None
    if email_clean in DEMO_ALIASES:
        lookup_sid = DEMO_ALIASES[email_clean]
    elif email_clean.startswith("st_"):
        lookup_sid = email_clean.upper()

    # Check direct email match first, then fallback to alias or student_id
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email_clean,))
    row = cursor.fetchone()

    if not row and lookup_sid:
        cursor.execute("SELECT * FROM users WHERE student_id = ? OR LOWER(email) = ?", (lookup_sid, lookup_email))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user = dict(row)

    # Verify password
    valid_password = verify_password(req.password, user["password_hash"])
    if not valid_password:
        # Fallback for student demo accounts if student123 was used
        if user.get("role") == "student" and req.password == "student123" and verify_password("demo123", user["password_hash"]):
            valid_password = True
        elif user.get("role") == "tpo" and req.password == "tpo123" and verify_password("tpo123", user["password_hash"]):
            valid_password = True

    if not valid_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")

    access_token = create_access_token({
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
        "student_id": user.get("student_id")
    })

    # Fetch display name from students table if linked
    user_name = "Student"
    if user.get("student_id"):
        cursor.execute("SELECT name FROM students WHERE student_id = ?", (user["student_id"],))
        s_row = cursor.fetchone()
        if s_row and s_row[0]:
            user_name = s_row[0]
        else:
            user_name = f"Student {user['student_id']}"
    elif user.get("role") == "tpo":
        user_name = "Institutional Placement Officer"

    role_val = user["role"]
    redirect_val = "/student" if role_val == "student" else "/rpo"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "token": access_token,
        "authenticated": True,
        "role": role_val,
        "redirect": redirect_val,
        "student_id": user.get("student_id"),
        "user": {
            "id": user.get("student_id") or f"USER_{user['id']}",
            "user_id": user["id"],
            "email": user["email"],
            "role": role_val,
            "student_id": user.get("student_id"),
            "name": user_name
        }
    }


@router.get("/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    user_name = "User"
    dept = None
    target_role = None
    if current_user.get("student_id"):
        cursor = db.cursor()
        cursor.execute("SELECT name, department, target_role FROM students WHERE student_id = ?", (current_user["student_id"],))
        s_row = cursor.fetchone()
        if s_row:
            user_name = s_row[0] if s_row[0] else f"Student {current_user['student_id']}"
            dept = s_row[1]
            target_role = s_row[2]
        else:
            user_name = f"Student {current_user['student_id']}"
    elif current_user.get("role") == "tpo":
        user_name = "Institutional Placement Officer"

    user_payload = {
        "id": current_user.get("student_id") or f"USER_{current_user['id']}",
        "user_id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "student_id": current_user.get("student_id"),
        "department": dept,
        "target_role": target_role,
        "is_active": bool(current_user.get("is_active")),
        "name": user_name
    }

    return {
        "authenticated": True,
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "student_id": current_user.get("student_id"),
        "department": dept,
        "target_role": target_role,
        "is_active": bool(current_user.get("is_active")),
        "name": user_name,
        "user": user_payload
    }


