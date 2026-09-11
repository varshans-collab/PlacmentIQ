import copy
from app.config import ROLE_BENCHMARKS
from app.services.model_service import model_service, FEATURE_NAME_MAP

SKILL_EFFORT_HOURS = {
    "sql_score": 6.0,          # 6 hrs for SQL boost
    "python_score": 8.0,       # 8 hrs for Python boost
    "dsa_score": 12.0,         # 12 hrs for DSA boost
    "quantitative_aptitude": 5.0,# 5 hrs for Aptitude boost
    "communication_score": 8.0, # 8 hrs for Comm workshop
    "cloud_score": 10.0,       # 10 hrs for Cloud
    "web_score": 8.0,          # 8 hrs for Web
    "ml_score": 12.0,          # 12 hrs for ML
    "project_count": 15.0,     # 15 hrs to complete project
    "internships": 40.0        # 40 hrs internship experience
}

def calculate_career_fit(student_dict: dict) -> dict:
    fit_scores = {}
    for role, benchmarks in ROLE_BENCHMARKS.items():
        total_weight = 0.0
        achieved_weight = 0.0

        for feat, req_val in benchmarks.items():
            stu_val = float(student_dict.get(feat, 0.0))
            if req_val > 0:
                weight = float(req_val)
                ratio = min(1.0, stu_val / weight)
            else:
                weight = 1.0
                ratio = 1.0
            total_weight += weight
            achieved_weight += ratio * weight

        fit = round((achieved_weight / total_weight) * 100.0, 1)
        fit_scores[role] = fit

    return fit_scores

def calculate_why_not_yet(student_dict: dict, target_role: str, shap_dict: dict) -> list:
    benchmarks = ROLE_BENCHMARKS.get(target_role, ROLE_BENCHMARKS["Data Analyst"])
    gaps = []

    for feat, req_val in benchmarks.items():
        stu_val = float(student_dict.get(feat, 0.0))
        gap = round(req_val - stu_val, 1)
        shap_v = shap_dict.get(feat, 0.0)

        if gap > 0 or shap_v < 0:
            gaps.append({
                "feature": feat,
                "feature_name": FEATURE_NAME_MAP.get(feat, feat),
                "current_val": stu_val,
                "required_val": req_val,
                "gap": gap,
                "shap_impact": shap_v,
                "impact_score": round(gap * 2.0 + abs(min(0.0, shap_v)) * 50.0, 2),
                "explanation": f"Current level is {stu_val}/{req_val} (Gap: {gap if gap > 0 else 0}). Model attribution: {shap_v:+.4f}"
            })

    gaps.sort(key=lambda x: x["impact_score"], reverse=True)
    return gaps

def calculate_opportunity_cost(student_dict: dict) -> list:
    base_pred = model_service.predict(student_dict)
    base_score = base_pred["readiness_score"]

    matrix = []
    candidate_skills = [
        ("sql_score", 3.0, "SQL Mastery Bootcamp"),
        ("python_score", 2.0, "Python Problem Solving"),
        ("dsa_score", 2.0, "DSA & Coding Intensive"),
        ("quantitative_aptitude", 2.5, "Quantitative Aptitude Sprint"),
        ("communication_score", 2.0, "Interview Communication Workshop"),
        ("cloud_score", 3.0, "Cloud & DevOps Fundamentals"),
        ("project_count", 1.0, "Practical Capstone Project"),
        ("internships", 1.0, "Virtual Internship Program")
    ]

    for feat, boost, intervention_name in candidate_skills:
        counterfactual = copy.deepcopy(student_dict)
        cur_val = float(counterfactual.get(feat, 5.0))
        new_val = min(10.0 if "score" in feat or "aptitude" in feat else 5.0, cur_val + boost)
        counterfactual[feat] = new_val

        sim_pred = model_service.predict(counterfactual, include_shap=False)
        sim_score = sim_pred["readiness_score"]
        delta = round(sim_score - base_score, 1)

        hours = SKILL_EFFORT_HOURS.get(feat, 8.0)
        efficiency = round(delta / hours, 2) if hours > 0 else 0.0

        matrix.append({
            "feature": feat,
            "feature_name": FEATURE_NAME_MAP.get(feat, feat),
            "intervention": intervention_name,
            "current_value": cur_val,
            "simulated_value": new_val,
            "delta_readiness": delta,
            "effort_hours": hours,
            "efficiency_index": efficiency,
            "recommendation": f"Raise {FEATURE_NAME_MAP.get(feat, feat)} from {cur_val} to {new_val} (+{delta}% readiness for {hours}h effort)"
        })

    matrix.sort(key=lambda x: x["efficiency_index"], reverse=True)
    return matrix

def calculate_minimum_improvement(student_dict: dict, target_score: float = 75.0) -> dict:
    base_pred = model_service.predict(student_dict, include_shap=False)
    base_score = base_pred["readiness_score"]

    if base_score >= target_score:
        return {
            "achievable": True,
            "required": False,
            "current_score": base_score,
            "target_score": target_score,
            "projected_score": base_score,
            "needed_delta": 0.0,
            "achieved_delta": 0.0,
            "total_effort_hours": 0.0,
            "changes": [],
            "message": "Student already meets or exceeds target readiness threshold."
        }

    candidate_skills = [
        ("dsa_score", 2.0, "DSA & Coding Intensive", 12.0),
        ("sql_score", 2.5, "SQL Mastery Bootcamp", 6.0),
        ("python_score", 2.0, "Python Problem Solving", 8.0),
        ("quantitative_aptitude", 2.5, "Quantitative Aptitude Sprint", 5.0),
        ("communication_score", 2.0, "Interview Communication Workshop", 8.0),
        ("cloud_score", 2.5, "Cloud & DevOps Fundamentals", 10.0),
        ("project_count", 1.0, "Practical Capstone Project", 15.0),
        ("internships", 1.0, "Virtual Internship Program", 40.0)
    ]

    import itertools

    candidate_combos = []
    cf_student_dicts = []

    # Generate combinations of sizes 1 to 4
    for k in range(1, min(5, len(candidate_skills) + 1)):
        for combo in itertools.combinations(candidate_skills, k):
            counterfactual = copy.deepcopy(student_dict)
            combo_changes = []
            total_hours = 0.0

            for feat, boost, intervention_name, hours in combo:
                cur_val = float(counterfactual.get(feat, 5.0))
                max_cap = 10.0 if "score" in feat or "aptitude" in feat else 5.0
                new_val = min(max_cap, cur_val + boost)
                if new_val > cur_val:
                    counterfactual[feat] = new_val
                    combo_changes.append({
                        "feature": feat,
                        "feature_name": FEATURE_NAME_MAP.get(feat, feat),
                        "intervention": intervention_name,
                        "current_value": cur_val,
                        "simulated_value": new_val,
                        "effort_hours": hours
                    })
                    total_hours += hours

            if combo_changes:
                candidate_combos.append({
                    "total_effort_hours": total_hours,
                    "changes": combo_changes
                })
                cf_student_dicts.append(counterfactual)

    if not cf_student_dicts:
        return {
            "achievable": False,
            "required": True,
            "current_score": base_score,
            "target_score": target_score,
            "needed_delta": round(target_score - base_score, 1),
            "message": "Target cannot be reached with the currently available interventions.",
            "best_available": {"projected_score": base_score, "achieved_delta": 0.0, "total_effort_hours": 0.0, "changes": []}
        }

    # Single vectorized batch prediction call across all counterfactual combinations
    batch_preds = model_service.predict_batch(cf_student_dicts)

    valid_solutions = []
    best_overall = None
    max_projected_score = -1.0

    for item, pred in zip(candidate_combos, batch_preds):
        sim_score = pred["readiness_score"]
        delta = round(sim_score - base_score, 1)

        cand_result = {
            "projected_score": sim_score,
            "achieved_delta": delta,
            "total_effort_hours": item["total_effort_hours"],
            "changes": item["changes"]
        }

        if sim_score > max_projected_score:
            max_projected_score = sim_score
            best_overall = cand_result

        if sim_score >= target_score:
            valid_solutions.append(cand_result)

    if valid_solutions:
        valid_solutions.sort(key=lambda x: (x["total_effort_hours"], -x["projected_score"]))
        best_sol = valid_solutions[0]
        return {
            "achievable": True,
            "required": True,
            "current_score": base_score,
            "target_score": target_score,
            "needed_delta": round(target_score - base_score, 1),
            "achieved_delta": best_sol["achieved_delta"],
            "projected_score": best_sol["projected_score"],
            "total_effort_hours": best_sol["total_effort_hours"],
            "changes": best_sol["changes"],
            "message": f"Minimum intervention plan identified: Projected {best_sol['projected_score']}% readiness (Target: {target_score}%) with {best_sol['total_effort_hours']}h effort."
        }

    return {
        "achievable": False,
        "required": True,
        "current_score": base_score,
        "target_score": target_score,
        "needed_delta": round(target_score - base_score, 1),
        "message": "Target cannot be reached with the currently available interventions.",
        "best_available": {
            "projected_score": best_overall["projected_score"] if best_overall else base_score,
            "achieved_delta": best_overall["achieved_delta"] if best_overall else 0.0,
            "total_effort_hours": best_overall["total_effort_hours"] if best_overall else 0.0,
            "changes": best_overall["changes"] if best_overall else []
        }
    }

def calculate_roadmap(student_dict: dict, target_role: str, shap_dict: dict) -> dict:
    gaps = calculate_why_not_yet(student_dict, target_role, shap_dict)
    
    milestones = []
    critical_gaps = [g for g in gaps if g["gap"] > 1.5 or g["shap_impact"] < -0.05][:2]
    if critical_gaps:
        milestones.append({
            "phase": "Phase 1: Remedial Foundations (Weeks 1-3)",
            "focus": "Close critical skill deficits impacting ML model readiness",
            "items": [f"Complete {g['feature_name']} intensive training (Current: {g['current_val']}, Target: {g['required_val']})" for g in critical_gaps]
        })
    else:
        milestones.append({
            "phase": "Phase 1: Core Technical Mastery (Weeks 1-2)",
            "focus": "Solidify core competencies for target role",
            "items": ["Advance Python problem solving speed", "Practice SQL complex query optimization"]
        })

    milestones.append({
        "phase": "Phase 2: Industry Capstones & Applied Skills (Weeks 4-6)",
        "focus": "Build verified portfolio evidence and practical complexity",
        "items": [
            f"Build end-to-end {target_role} capstone project",
            "Contribute to open-source repository or internship assignment"
        ]
    })

    milestones.append({
        "phase": "Phase 3: Placement Sprints & Mock Interviews (Weeks 7-8)",
        "focus": "Aptitude speed building and communication confidence",
        "items": [
            "Complete 5 timed quantitative aptitude mock tests",
            "Participate in 2 mock technical & behavioral interviews"
        ]
    })

    return {
        "student_id": student_dict.get("student_id"),
        "target_role": target_role,
        "milestones": milestones,
        "data_provenance": "DERIVED"
    }



