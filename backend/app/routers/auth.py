from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str

class LoginResponse(BaseModel):
    authenticated: bool
    role: str
    redirect: str
    token: str
    user: dict

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    email_clean = req.email.strip().lower()
    role_clean = req.role.strip().lower()

    if role_clean == "student":
        if (email_clean == "student@placementiq.demo" and req.password == "student123") or (email_clean.startswith("st_") and req.password == "student123"):
            student_id = "ST_DEMO_001"
            if email_clean.startswith("st_"):
                student_id = email_clean.upper()
            return {
                "authenticated": True,
                "role": "student",
                "redirect": "/student",
                "token": f"demo-student-token-{student_id}",
                "user": {
                    "email": email_clean,
                    "id": student_id,
                    "name": "Ananya Sharma" if student_id == "ST_DEMO_001" else student_id
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect login details. Please try again.")

    elif role_clean in ["rpo_tpo", "tpo", "rpo"]:
        if (email_clean == "tpo@placementiq.demo" and req.password == "tpo123") or (email_clean == "rpo@placementiq.demo" and req.password == "tpo123"):
            return {
                "authenticated": True,
                "role": "rpo_tpo",
                "redirect": "/rpo",
                "token": "demo-tpo-token-001",
                "user": {
                    "email": email_clean,
                    "id": "TPO_ADMIN_001",
                    "name": "Institutional Placement Officer"
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect login details. Please try again.")
    else:
        raise HTTPException(status_code=400, detail="Invalid role specified.")
