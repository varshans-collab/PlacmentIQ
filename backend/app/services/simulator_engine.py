import copy
from app.config import ROLE_BENCHMARKS

INTERVENTION_CATALOG = {
    "SQL Bootcamp": {
        "name": "SQL Bootcamp & Database Mastery",
        "description": "Intensive 2-week hands-on SQL query optimization and database design bootcamp.",
        "target_skills": ["sql_score"],
        "boost": 2.5,
        "max_cap": 8.5,
        "effort": "Medium (20 Hours)",
        "cost_per_student": 1500
    },
    "Aptitude Training": {
        "name": "Quantitative & Logical Aptitude Sprint",
        "description": "Targeted problem-solving speed and accuracy training for placement rounds.",
        "target_skills": ["quantitative_aptitude", "logical_aptitude"],
        "boost": 2.0,
        "max_cap": 8.5,
        "effort": "Medium (15 Hours)",
        "cost_per_student": 1200
    },
    "Mock Interviews": {
        "name": "Mock Technical & Behavioral Interview Lab",
        "description": "1-on-1 industry mock interviews with personalized feedback and communication coaching.",
        "target_skills": ["interview_score", "communication_score", "presentation_score"],
        "boost": 2.0,
        "max_cap": 8.5,
        "effort": "High (25 Hours)",
        "cost_per_student": 2500
    },
    "DSA Intensive": {
        "name": "Data Structures & Algorithms Bootcamp",
        "description": "Rigorous coding practice covering arrays, trees, dynamic programming, and system design.",
        "target_skills": ["dsa_score", "coding_score"],
        "boost": 2.0,
        "max_cap": 8.5,
        "effort": "High (30 Hours)",
        "cost_per_student": 2000
    },
    "Cloud & DevOps Workshop": {
        "name": "AWS/Azure Cloud Practitioner Workshop",
        "description": "Hands-on cloud deployment, Docker, CI/CD pipelines, and cloud architecture.",
        "target_skills": ["cloud_score"],
        "boost": 2.5,
        "max_cap": 8.5,
        "effort": "Medium (20 Hours)",
        "cost_per_student": 1800
    },
    "Project Program": {
        "name": "Industry Capstone Project Program",
        "description": "Guided building of advanced full-stack / ML capstone projects with GitHub proof.",
        "target_skills": ["project_count", "project_complexity"],
        "boost": 1.0,
        "max_cap": 5.0,
        "effort": "High (35 Hours)",
        "cost_per_student": 2200
    }
}

def run_flight_simulator(cohort: list, config: dict) -> dict:
    target_role = config.get("target_role", "Data Analyst")
    dept_filter = config.get("department", "ALL")
    elig_cgpa = config.get("eligibility_cgpa", 7.0)
    elig_backlogs = config.get("eligibility_max_backlogs", 0)
    apt_thresh = config.get("aptitude_threshold", 6.0)
    tech_thresh = config.get("technical_threshold", 6.5)
    interview_thresh = config.get("interview_threshold", 6.5)

    # 1. Filter cohort by department if specified
    filtered_cohort = cohort
    if dept_filter and dept_filter != "ALL":
        filtered_cohort = [s for s in cohort if s.get("department") == dept_filter]

    total_count = len(filtered_cohort)
    if total_count == 0:
        return {"error": "No students match the specified cohort filter"}

    # 2. Stage 1: Academic Eligibility
    eligible_students = [
        s for s in filtered_cohort
        if float(s.get("cgpa", 0.0)) >= elig_cgpa and int(s.get("backlogs", 0)) <= elig_backlogs
    ]
    elig_count = len(eligible_students)

    # 3. Stage 2: Aptitude Round
    aptitude_passed = [
        s for s in eligible_students
        if (float(s.get("quantitative_aptitude", 0.0)) + float(s.get("logical_aptitude", 0.0))) / 2.0 >= apt_thresh
    ]
    apt_count = len(aptitude_passed)

    # 4. Stage 3: Technical Round (Role-specific primary skill test)
    role_benchmarks = ROLE_BENCHMARKS.get(target_role, ROLE_BENCHMARKS["Data Analyst"])
    primary_skill = "sql_score" if target_role == "Data Analyst" else ("python_score" if "AI" in target_role else "dsa_score")

    tech_passed = [
        s for s in aptitude_passed
        if float(s.get(primary_skill, 0.0)) >= tech_thresh and float(s.get("coding_score", 0.0)) >= (tech_thresh - 1.0)
    ]
    tech_count = len(tech_passed)

    # 5. Stage 4: Interview Round (Selections)
    selections = [
        s for s in tech_passed
        if (float(s.get("interview_score", 0.0)) + float(s.get("communication_score", 0.0))) / 2.0 >= interview_thresh
    ]
    selection_count = len(selections)

    # Calculate losses
    loss_elig = total_count - elig_count
    pct_loss_elig = round((loss_elig / total_count) * 100.0, 1) if total_count > 0 else 0.0

    loss_apt = elig_count - apt_count
    pct_loss_apt = round((loss_apt / elig_count) * 100.0, 1) if elig_count > 0 else 0.0

    loss_tech = apt_count - tech_count
    pct_loss_tech = round((loss_tech / apt_count) * 100.0, 1) if apt_count > 0 else 0.0

    loss_int = tech_count - selection_count
    pct_loss_int = round((loss_int / tech_count) * 100.0, 1) if tech_count > 0 else 0.0

    stages = [
        {"stage": "Total Cohort", "count": total_count, "passed": total_count, "lost": 0, "loss_pct": 0.0},
        {"stage": "Eligibility Filter", "count": elig_count, "passed": elig_count, "lost": loss_elig, "loss_pct": pct_loss_elig},
        {"stage": "Aptitude Round", "count": apt_count, "passed": apt_count, "lost": loss_apt, "loss_pct": pct_loss_apt},
        {"stage": "Technical Round", "count": tech_count, "passed": tech_count, "lost": loss_tech, "loss_pct": pct_loss_tech},
        {"stage": "Interview Round", "count": selection_count, "passed": selection_count, "lost": loss_int, "loss_pct": pct_loss_int}
    ]

    # Detect primary bottleneck
    stage_losses = [
        ("Eligibility Filter", pct_loss_elig, loss_elig, ["cgpa", "backlogs"]),
        ("Aptitude Round", pct_loss_apt, loss_apt, ["quantitative_aptitude", "logical_aptitude"]),
        ("Technical Round", pct_loss_tech, loss_tech, [primary_skill, "coding_score", "dsa_score"]),
        ("Interview Round", pct_loss_int, loss_int, ["interview_score", "communication_score"])
    ]
    stage_losses.sort(key=lambda x: x[1], reverse=True)
    primary_bottleneck = stage_losses[0]

    bottleneck_info = {
        "stage": primary_bottleneck[0],
        "loss_percentage": primary_bottleneck[1],
        "students_lost": primary_bottleneck[2],
        "key_deficits": primary_bottleneck[3],
        "primary_skill_tested": primary_skill,
        "recommendation": f"Primary pipeline drop-off occurs at {primary_bottleneck[0]} ({primary_bottleneck[1]}% loss, {primary_bottleneck[2]} students eliminated). Focus intervention on {', '.join(primary_bottleneck[3])}."
    }

    # Pre-mortem analysis
    pre_mortem = [
        f"1. High drop-off at {primary_bottleneck[0]} ({primary_bottleneck[1]}% eliminated due to {primary_bottleneck[3][0]} deficit).",
        f"2. Aptitude bottleneck eliminated {loss_apt} eligible candidates ({pct_loss_apt}% loss).",
        f"3. Interview communication barrier eliminated {loss_int} technical qualifiers ({pct_loss_int}% loss)."
    ]

    return {
        "target_role": target_role,
        "department_filter": dept_filter,
        "total_cohort": total_count,
        "stages": stages,
        "selections": selection_count,
        "selection_rate": round((selection_count / total_count) * 100.0, 1),
        "primary_bottleneck": bottleneck_info,
        "pre_mortem": pre_mortem,
        "data_provenance": "SIMULATED"
    }

def compare_interventions(cohort: list, config: dict, selected_keys: list = None) -> list:
    if selected_keys is None:
        selected_keys = list(INTERVENTION_CATALOG.keys())

    baseline_sim = run_flight_simulator(cohort, config)
    baseline_selections = baseline_sim["selections"]

    results = []

    for key in selected_keys:
        if key not in INTERVENTION_CATALOG:
            continue
        spec = INTERVENTION_CATALOG[key]

        # Apply counterfactual boost to cohort
        sim_cohort = copy.deepcopy(cohort)
        affected_count = 0

        for student in sim_cohort:
            was_affected = False
            for feat in spec["target_skills"]:
                cur_val = float(student.get(feat, 5.0))
                if cur_val < spec["max_cap"]:
                    student[feat] = min(spec["max_cap"], cur_val + spec["boost"])
                    was_affected = True
            if was_affected:
                affected_count += 1

        sim_res = run_flight_simulator(sim_cohort, config)
        new_selections = sim_res["selections"]
        delta_selections = new_selections - baseline_selections

        results.append({
            "key": key,
            "name": spec["name"],
            "description": spec["description"],
            "baseline_cohort_size": len(cohort),
            "affected_students": affected_count,
            "baseline_selections": baseline_selections,
            "simulated_selections": new_selections,
            "delta_selections": delta_selections,
            "effort": spec["effort"],
            "priority": "HIGH" if delta_selections >= 8 else ("MEDIUM" if delta_selections >= 4 else "LOW"),
            "data_provenance": "SIMULATED"
        })

    results.sort(key=lambda x: x["delta_selections"], reverse=True)
    return results

def run_plus10_optimizer(cohort: list, config: dict) -> dict:
    baseline_sim = run_flight_simulator(cohort, config)
    baseline = baseline_sim["selections"]
    target_gain = 10

    single_results = compare_interventions(cohort, config)
    best_single = single_results[0] if single_results else None

    # Combination check
    combo_keys = ["SQL Bootcamp", "Mock Interviews"]
    sim_cohort = copy.deepcopy(cohort)
    for key in combo_keys:
        spec = INTERVENTION_CATALOG[key]
        for s in sim_cohort:
            for feat in spec["target_skills"]:
                cur_val = float(s.get(feat, 5.0))
                if cur_val < spec["max_cap"]:
                    s[feat] = min(spec["max_cap"], cur_val + spec["boost"])

    combo_sim = run_flight_simulator(sim_cohort, config)
    combo_selections = combo_sim["selections"]
    combo_delta = combo_selections - baseline

    return {
        "target_selection_increase": target_gain,
        "baseline_cohort_size": len(cohort),
        "baseline_selections": baseline,
        "recommended_primary_intervention": best_single,
        "recommended_combination": {
            "name": "SQL Bootcamp + Mock Interviews Package",
            "interventions": combo_keys,
            "simulated_selections": combo_selections,
            "delta_selections": combo_delta,
            "achieves_target": combo_delta >= target_gain,
            "effort": "Combined High (45 Hours)"
        },
        "data_provenance": "SIMULATED"
    }
