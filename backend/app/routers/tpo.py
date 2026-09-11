import sqlite3
import numpy as np
from fastapi import APIRouter, Depends
from app.database import get_db
from app.services.model_service import model_service

router = APIRouter(prefix="/api/tpo", tags=["tpo"])

@router.get("/overview")
def get_tpo_overview(dept: str = None, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM students"
    params = []
    if dept and dept != "ALL":
        query += " WHERE department = ?"
        params.append(dept)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    students = [dict(r) for r in rows]

    total_count = len(students)
    if total_count == 0:
        return {"error": "No students found"}

    ready_count = 0
    near_ready_count = 0
    needs_training_count = 0
    scores = []
    dept_distribution = {}

    batch_preds = model_service.predict_batch(students)

    for s, pred in zip(students, batch_preds):
        score = pred["readiness_score"]
        status = pred["status"]
        scores.append(score)

        if status == "Ready":
            ready_count += 1
        elif status == "Near-Ready":
            near_ready_count += 1
        else:
            needs_training_count += 1

        d = s["department"]
        if d not in dept_distribution:
            dept_distribution[d] = {"count": 0, "sum_score": 0.0, "needs_training": 0}
        dept_distribution[d]["count"] += 1
        dept_distribution[d]["sum_score"] += score
        if status == "Needs Training":
            dept_distribution[d]["needs_training"] += 1

    overall_avg = round(float(np.mean(scores)), 1) if scores else 0.0

    dept_kpis = []
    for d, stats in dept_distribution.items():
        avg = round(stats["sum_score"] / stats["count"], 1) if stats["count"] > 0 else 0.0
        dept_kpis.append({
            "department": d,
            "total_students": stats["count"],
            "avg_readiness": avg,
            "high_risk_count": stats["needs_training"],
            "high_risk_pct": round((stats["needs_training"] / stats["count"]) * 100.0, 1)
        })

    next_best_action = {
        "title": "SQL Bootcamp & Database Mastery",
        "affected_students": needs_training_count,
        "estimated_impact": "+11 to +15 expected selections",
        "effort": "Medium (20 Hours)",
        "priority": "HIGH"
    }

    return {
        "total_students": total_count,
        "overall_readiness_avg": overall_avg,
        "ready_count": ready_count,
        "ready_pct": round((ready_count / total_count) * 100.0, 1),
        "near_ready_count": near_ready_count,
        "near_ready_pct": round((near_ready_count / total_count) * 100.0, 1),
        "needs_training_count": needs_training_count,
        "needs_training_pct": round((needs_training_count / total_count) * 100.0, 1),
        "high_risk_count": needs_training_count,
        "department_breakdown": dept_kpis,
        "next_best_institutional_action": next_best_action,
        "data_provenance": "SYNTHETIC"
    }

@router.get("/heatmap")
def get_skill_heatmap(
    dept: str = None,
    semester: int = None,
    role: str = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if dept and dept != "ALL":
        query += " AND department = ?"
        params.append(dept)
    if semester and semester > 0:
        query += " AND semester = ?"
        params.append(semester)
    if role and role != "ALL":
        query += " AND target_role = ?"
        params.append(role)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    students = [dict(r) for r in rows]

    departments = ["CSE", "ISE", "ECE", "Mechanical"]
    skills = ["python_score", "sql_score", "dsa_score", "cloud_score", "quantitative_aptitude", "communication_score"]
    skill_names = {
        "python_score": "Python",
        "sql_score": "SQL",
        "dsa_score": "DSA",
        "cloud_score": "Cloud",
        "quantitative_aptitude": "Aptitude",
        "communication_score": "Communication"
    }

    grid = []
    for d in departments:
        dept_students = [s for s in students if s["department"] == d]
        if not dept_students:
            continue

        row_data = {"department": d, "total": len(dept_students), "skills": {}}
        for sk in skills:
            vals = [float(s.get(sk, 5.0)) for s in dept_students]
            avg_val = round(float(np.mean(vals)), 1)

            if avg_val < 3.0:
                status = "Critical"
            elif avg_val < 5.0:
                status = "Needs Improvement"
            elif avg_val < 7.0:
                status = "Developing"
            elif avg_val < 8.5:
                status = "Strong"
            else:
                status = "Advanced"

            s_name = skill_names[sk]
            row_data["skills"][s_name] = {
                "score": avg_val,
                "status": status,
                "student_count": len(dept_students)
            }
            # Maintain flat keys for backward compatibility
            row_data[s_name] = {
                "score": avg_val,
                "status": status,
                "student_count": len(dept_students)
            }

        grid.append(row_data)

    return {"heatmap": grid, "skills": list(skill_names.values()), "data_provenance": "DERIVED"}

@router.get("/vulnerable")
def get_vulnerable_students(
    dept: str = None,
    semester: int = None,
    role: str = None,
    max_readiness: float = 60.0,
    min_backlogs: int = 0,
    skill_deficit: str = None,
    risk_level: str = None,
    sort_by: str = "readiness_asc",
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    students = [dict(r) for r in rows]

    vulnerable_list = []
    batch_preds = model_service.predict_batch(students)

    for s, pred in zip(students, batch_preds):
        if dept and dept != "ALL" and s["department"] != dept:
            continue
        if semester and semester > 0 and int(s.get("semester", 7)) != semester:
            continue
        if role and role != "ALL" and s.get("target_role") != role:
            continue
        if int(s.get("backlogs", 0)) < min_backlogs:
            continue

        score = pred["readiness_score"]
        if score >= max_readiness:
            continue

        if skill_deficit and skill_deficit != "ALL":
            stu_skill_val = float(s.get(skill_deficit, 5.0))
            if stu_skill_val >= 6.0:
                continue

        # Derived Risk Level
        if score < 40.0:
            risk = "CRITICAL"
        elif score < 60.0:
            risk = "HIGH"
        else:
            risk = "MODERATE"

        if risk_level and risk_level != "ALL" and risk != risk_level:
            continue

        # Determine Lowest Competency / Primary Skill Deficit
        sql_v = float(s.get("sql_score", 5.0))
        dsa_v = float(s.get("dsa_score", 5.0))
        comm_v = float(s.get("communication_score", 5.0))
        proj_v = int(s.get("project_count", 0))
        intern_v = int(s.get("internships", 0))

        if sql_v <= dsa_v and sql_v <= comm_v and sql_v < 6.0:
            top_deficit = f"SQL {sql_v:.1f}/10"
            reason_badge = "SQL GAP"
            recommended_action = "SQL Foundations Bootcamp"
            primary_gap = "SQL & Databases"
        elif dsa_v <= comm_v and dsa_v < 6.0:
            top_deficit = f"DSA {dsa_v:.1f}/10"
            reason_badge = "CODING GAP"
            recommended_action = "DSA & Coding Intensive"
            primary_gap = "Data Structures & Algorithms"
        elif comm_v < 6.0:
            top_deficit = f"Comm {comm_v:.1f}/10"
            reason_badge = "COMMUNICATION GAP"
            recommended_action = "Interview Communication Workshop"
            primary_gap = "Communication Skills"
        elif proj_v < 2:
            top_deficit = f"Projects {proj_v} built"
            reason_badge = "PROJECT GAP"
            recommended_action = "Capstone Project Program"
            primary_gap = "Project Complexity"
        elif intern_v == 0:
            top_deficit = "0 Internships"
            reason_badge = "INTERNSHIP GAP"
            recommended_action = "Virtual Internship Program"
            primary_gap = "Internship Experience"
        else:
            top_deficit = f"Aptitude {float(s.get('quantitative_aptitude', 5.0)):.1f}/10"
            reason_badge = "APTITUDE GAP"
            recommended_action = "Quantitative Aptitude Sprint"
            primary_gap = "Quantitative Aptitude"

        vulnerable_list.append({
            "student_id": s["student_id"],
            "name": s.get("name", f"Student {s['student_id']}"),
            "department": s["department"],
            "semester": s["semester"],
            "cgpa": s["cgpa"],
            "backlogs": s["backlogs"],
            "readiness_score": score,
            "status": pred["status"],
            "risk": risk,
            "target_role": s["target_role"],
            "top_deficit": top_deficit,
            "reason_badge": reason_badge,
            "recommended_action": recommended_action,
            "primary_gap": primary_gap
        })

    # Sorting
    if sort_by == "readiness_asc":
        vulnerable_list.sort(key=lambda x: x["readiness_score"])
    elif sort_by == "risk_desc":
        risk_rank = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2}
        vulnerable_list.sort(key=lambda x: (risk_rank.get(x["risk"], 3), x["readiness_score"]))
    elif sort_by == "dept_asc":
        vulnerable_list.sort(key=lambda x: x["department"])
    elif sort_by == "name_asc":
        vulnerable_list.sort(key=lambda x: x["name"])

    return {"count": len(vulnerable_list), "vulnerable_students": vulnerable_list, "data_provenance": "DERIVED"}
