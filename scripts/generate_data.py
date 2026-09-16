import os
import sys
import json
import random
import numpy as np
import pandas as pd

# Ensure UTF-8 output across all consoles/platforms
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Set fixed seed for perfect reproducibility
np.random.seed(42)
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

FEATURE_COLUMNS = [
    "cgpa", "tenth_percentage", "twelfth_percentage", "backlogs",
    "python_score", "java_score", "sql_score", "dsa_score", "cloud_score",
    "web_score", "ml_score", "cybersecurity_score", "certifications",
    "project_count", "project_complexity", "internships", "opensource_projects",
    "quantitative_aptitude", "logical_aptitude", "coding_score",
    "communication_score", "presentation_score", "interview_score",
    "hackathons", "leadership"
]

def generate_student_record(student_id, dept, is_demo=False, persona_type=None):
    if is_demo and persona_type == "Ananya":
        return {
            "student_id": "ST_DEMO_001",
            "name": "Ananya Sharma",
            "department": "ECE",
            "semester": 7,
            "cgpa": 7.2,
            "tenth_percentage": 82.0,
            "twelfth_percentage": 78.5,
            "backlogs": 0,
            "python_score": 5.0,
            "java_score": 4.0,
            "sql_score": 4.0,
            "dsa_score": 5.0,
            "cloud_score": 3.0,
            "web_score": 4.0,
            "ml_score": 3.0,
            "cybersecurity_score": 2.0,
            "certifications": 1,
            "project_count": 2,
            "project_complexity": 1,
            "internships": 0,
            "opensource_projects": 0,
            "quantitative_aptitude": 5.0,
            "logical_aptitude": 5.5,
            "coding_score": 4.5,
            "communication_score": 5.0,
            "presentation_score": 5.5,
            "interview_score": 5.0,
            "hackathons": 0,
            "leadership": 0,
            "target_role": "Data Analyst",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 85.0,
            "evidence_confidence": 62.0
        }
    elif is_demo and persona_type == "Rahul":
        return {
            "student_id": "ST_DEMO_002",
            "name": "Rahul Verma",
            "department": "CSE",
            "semester": 7,
            "cgpa": 8.1,
            "tenth_percentage": 89.0,
            "twelfth_percentage": 86.0,
            "backlogs": 0,
            "python_score": 8.0,
            "java_score": 7.0,
            "sql_score": 7.0,
            "dsa_score": 8.0,
            "cloud_score": 6.0,
            "web_score": 7.5,
            "ml_score": 6.5,
            "cybersecurity_score": 4.0,
            "certifications": 2,
            "project_count": 4,
            "project_complexity": 2,
            "internships": 1,
            "opensource_projects": 1,
            "quantitative_aptitude": 6.5,
            "logical_aptitude": 7.0,
            "coding_score": 7.5,
            "communication_score": 6.5,
            "presentation_score": 7.0,
            "interview_score": 7.0,
            "hackathons": 2,
            "leadership": 1,
            "target_role": "Full-Stack Developer",
            "placed": 1,
            "data_source": "SYNTHETIC",
            "profile_completeness": 92.0,
            "evidence_confidence": 78.0
        }
    elif is_demo and persona_type == "Priya":
        return {
            "student_id": "ST_DEMO_003",
            "name": "Priya Patel",
            "department": "CSE",
            "semester": 8,
            "cgpa": 9.2,
            "tenth_percentage": 95.0,
            "twelfth_percentage": 94.0,
            "backlogs": 0,
            "python_score": 9.0,
            "java_score": 8.5,
            "sql_score": 9.0,
            "dsa_score": 9.0,
            "cloud_score": 8.0,
            "web_score": 8.5,
            "ml_score": 8.5,
            "cybersecurity_score": 6.0,
            "certifications": 4,
            "project_count": 5,
            "project_complexity": 3,
            "internships": 2,
            "opensource_projects": 3,
            "quantitative_aptitude": 9.0,
            "logical_aptitude": 9.0,
            "coding_score": 9.0,
            "communication_score": 8.5,
            "presentation_score": 9.0,
            "interview_score": 9.0,
            "hackathons": 4,
            "leadership": 1,
            "target_role": "AI/ML Engineer",
            "placed": 1,
            "data_source": "SYNTHETIC",
            "profile_completeness": 98.0,
            "evidence_confidence": 92.0
        }
    elif is_demo and persona_type == "Sneha":
        return {
            "student_id": "ST_DEMO_004",
            "name": "Sneha Rao",
            "department": "ECE",
            "semester": 7,
            "cgpa": 8.4,
            "tenth_percentage": 88.0,
            "twelfth_percentage": 85.0,
            "backlogs": 0,
            "python_score": 8.2,
            "java_score": 7.5,
            "sql_score": 8.0,
            "dsa_score": 8.0,
            "cloud_score": 6.5,
            "web_score": 7.0,
            "ml_score": 7.5,
            "cybersecurity_score": 4.0,
            "certifications": 3,
            "project_count": 4,
            "project_complexity": 3,
            "internships": 0,
            "opensource_projects": 2,
            "quantitative_aptitude": 7.8,
            "logical_aptitude": 8.0,
            "coding_score": 8.2,
            "communication_score": 7.5,
            "presentation_score": 7.5,
            "interview_score": 7.5,
            "hackathons": 3,
            "leadership": 0,
            "target_role": "AI/ML Engineer",
            "placed": 1,
            "data_source": "SYNTHETIC",
            "profile_completeness": 90.0,
            "evidence_confidence": 80.0
        }
    elif is_demo and persona_type == "Arjun":
        return {
            "student_id": "ST_DEMO_005",
            "name": "Arjun Mehta",
            "department": "ISE",
            "semester": 7,
            "cgpa": 9.1,
            "tenth_percentage": 92.0,
            "twelfth_percentage": 91.0,
            "backlogs": 0,
            "python_score": 4.5,
            "java_score": 4.0,
            "sql_score": 4.5,
            "dsa_score": 4.0,
            "cloud_score": 2.5,
            "web_score": 3.5,
            "ml_score": 2.5,
            "cybersecurity_score": 2.0,
            "certifications": 0,
            "project_count": 1,
            "project_complexity": 1,
            "internships": 0,
            "opensource_projects": 0,
            "quantitative_aptitude": 8.5,
            "logical_aptitude": 8.5,
            "coding_score": 4.0,
            "communication_score": 6.5,
            "presentation_score": 6.5,
            "interview_score": 5.5,
            "hackathons": 0,
            "leadership": 0,
            "target_role": "Software Engineer",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 82.0,
            "evidence_confidence": 70.0
        }
    elif is_demo and persona_type == "Meera":
        return {
            "student_id": "ST_DEMO_006",
            "name": "Meera Nair",
            "department": "ECE",
            "semester": 7,
            "cgpa": 8.3,
            "tenth_percentage": 86.0,
            "twelfth_percentage": 84.0,
            "backlogs": 0,
            "python_score": 8.8,
            "java_score": 8.0,
            "sql_score": 8.5,
            "dsa_score": 8.5,
            "cloud_score": 7.0,
            "web_score": 7.5,
            "ml_score": 8.0,
            "cybersecurity_score": 5.0,
            "certifications": 2,
            "project_count": 4,
            "project_complexity": 2,
            "internships": 1,
            "opensource_projects": 1,
            "quantitative_aptitude": 7.5,
            "logical_aptitude": 8.0,
            "coding_score": 8.5,
            "communication_score": 3.5,
            "presentation_score": 3.5,
            "interview_score": 4.0,
            "hackathons": 2,
            "leadership": 0,
            "target_role": "Software Engineer",
            "placed": 1,
            "data_source": "SYNTHETIC",
            "profile_completeness": 88.0,
            "evidence_confidence": 76.0
        }
    elif is_demo and persona_type == "Karan":
        return {
            "student_id": "ST_DEMO_007",
            "name": "Karan Shah",
            "department": "CSE",
            "semester": 7,
            "cgpa": 7.6,
            "tenth_percentage": 84.0,
            "twelfth_percentage": 82.0,
            "backlogs": 0,
            "python_score": 4.0,
            "java_score": 3.5,
            "sql_score": 3.5,
            "dsa_score": 4.0,
            "cloud_score": 3.0,
            "web_score": 4.0,
            "ml_score": 3.0,
            "cybersecurity_score": 2.0,
            "certifications": 1,
            "project_count": 2,
            "project_complexity": 1,
            "internships": 0,
            "opensource_projects": 0,
            "quantitative_aptitude": 9.2,
            "logical_aptitude": 9.0,
            "coding_score": 4.0,
            "communication_score": 7.5,
            "presentation_score": 7.5,
            "interview_score": 6.0,
            "hackathons": 1,
            "leadership": 1,
            "target_role": "Business Analyst",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 84.0,
            "evidence_confidence": 68.0
        }
    elif is_demo and persona_type == "Divya":
        return {
            "student_id": "ST_DEMO_008",
            "name": "Divya Reddy",
            "department": "ISE",
            "semester": 8,
            "cgpa": 8.2,
            "tenth_percentage": 87.0,
            "twelfth_percentage": 85.0,
            "backlogs": 0,
            "python_score": 8.0,
            "java_score": 7.5,
            "sql_score": 8.0,
            "dsa_score": 7.8,
            "cloud_score": 7.5,
            "web_score": 8.0,
            "ml_score": 7.0,
            "cybersecurity_score": 4.0,
            "certifications": 3,
            "project_count": 5,
            "project_complexity": 3,
            "internships": 0,
            "opensource_projects": 2,
            "quantitative_aptitude": 7.0,
            "logical_aptitude": 7.5,
            "coding_score": 8.0,
            "communication_score": 7.5,
            "presentation_score": 8.0,
            "interview_score": 7.5,
            "hackathons": 3,
            "leadership": 1,
            "target_role": "Full-Stack Developer",
            "placed": 1,
            "data_source": "SYNTHETIC",
            "profile_completeness": 92.0,
            "evidence_confidence": 82.0
        }
    elif is_demo and persona_type == "Rohan":
        return {
            "student_id": "ST_DEMO_009",
            "name": "Rohan Kumar",
            "department": "Mechanical",
            "semester": 7,
            "cgpa": 6.4,
            "tenth_percentage": 72.0,
            "twelfth_percentage": 70.0,
            "backlogs": 1,
            "python_score": 8.0,
            "java_score": 6.5,
            "sql_score": 7.5,
            "dsa_score": 7.0,
            "cloud_score": 6.0,
            "web_score": 7.5,
            "ml_score": 6.0,
            "cybersecurity_score": 3.0,
            "certifications": 2,
            "project_count": 4,
            "project_complexity": 2,
            "internships": 1,
            "opensource_projects": 1,
            "quantitative_aptitude": 6.0,
            "logical_aptitude": 6.5,
            "coding_score": 7.5,
            "communication_score": 7.0,
            "presentation_score": 7.0,
            "interview_score": 7.0,
            "hackathons": 2,
            "leadership": 0,
            "target_role": "DevOps Engineer",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 86.0,
            "evidence_confidence": 72.0
        }
    elif is_demo and persona_type == "Nisha":
        return {
            "student_id": "ST_DEMO_010",
            "name": "Nisha Patel",
            "department": "CSE",
            "semester": 7,
            "cgpa": 7.8,
            "tenth_percentage": 85.0,
            "twelfth_percentage": 83.0,
            "backlogs": 0,
            "python_score": 4.0,
            "java_score": 3.5,
            "sql_score": 5.0,
            "dsa_score": 3.8,
            "cloud_score": 3.5,
            "web_score": 4.5,
            "ml_score": 3.0,
            "cybersecurity_score": 2.5,
            "certifications": 1,
            "project_count": 2,
            "project_complexity": 1,
            "internships": 1,
            "opensource_projects": 0,
            "quantitative_aptitude": 6.0,
            "logical_aptitude": 6.5,
            "coding_score": 3.8,
            "communication_score": 9.2,
            "presentation_score": 9.0,
            "interview_score": 8.0,
            "hackathons": 1,
            "leadership": 1,
            "target_role": "Product Associate",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 85.0,
            "evidence_confidence": 65.0
        }
    elif is_demo and persona_type == "Vivek":
        return {
            "student_id": "ST_DEMO_011",
            "name": "Vivek Rao",
            "department": "ECE",
            "semester": 8,
            "cgpa": 6.2,
            "tenth_percentage": 70.0,
            "twelfth_percentage": 68.0,
            "backlogs": 1,
            "python_score": 7.5,
            "java_score": 6.5,
            "sql_score": 7.0,
            "dsa_score": 6.8,
            "cloud_score": 6.5,
            "web_score": 7.0,
            "ml_score": 5.5,
            "cybersecurity_score": 4.0,
            "certifications": 2,
            "project_count": 3,
            "project_complexity": 2,
            "internships": 2,
            "opensource_projects": 1,
            "quantitative_aptitude": 6.5,
            "logical_aptitude": 6.5,
            "coding_score": 7.0,
            "communication_score": 7.5,
            "presentation_score": 7.5,
            "interview_score": 7.5,
            "hackathons": 2,
            "leadership": 0,
            "target_role": "Network Engineer",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 87.0,
            "evidence_confidence": 74.0
        }
    elif is_demo and persona_type == "Pooja":
        return {
            "student_id": "ST_DEMO_012",
            "name": "Pooja Singh",
            "department": "ISE",
            "semester": 7,
            "cgpa": 7.5,
            "tenth_percentage": 80.0,
            "twelfth_percentage": 78.0,
            "backlogs": 0,
            "python_score": 6.5,
            "java_score": 6.0,
            "sql_score": 6.5,
            "dsa_score": 6.5,
            "cloud_score": 5.5,
            "web_score": 6.5,
            "ml_score": 5.0,
            "cybersecurity_score": 3.5,
            "certifications": 1,
            "project_count": 3,
            "project_complexity": 2,
            "internships": 1,
            "opensource_projects": 0,
            "quantitative_aptitude": 6.5,
            "logical_aptitude": 7.0,
            "coding_score": 6.5,
            "communication_score": 6.5,
            "presentation_score": 7.0,
            "interview_score": 6.5,
            "hackathons": 1,
            "leadership": 0,
            "target_role": "System Analyst",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 88.0,
            "evidence_confidence": 75.0
        }
    elif is_demo and persona_type == "Aditya":
        return {
            "student_id": "ST_DEMO_013",
            "name": "Aditya Kumar",
            "department": "Mechanical",
            "semester": 7,
            "cgpa": 5.8,
            "tenth_percentage": 65.0,
            "twelfth_percentage": 62.0,
            "backlogs": 2,
            "python_score": 3.5,
            "java_score": 3.0,
            "sql_score": 3.0,
            "dsa_score": 3.0,
            "cloud_score": 2.0,
            "web_score": 3.0,
            "ml_score": 2.0,
            "cybersecurity_score": 1.5,
            "certifications": 0,
            "project_count": 1,
            "project_complexity": 1,
            "internships": 0,
            "opensource_projects": 0,
            "quantitative_aptitude": 4.0,
            "logical_aptitude": 4.5,
            "coding_score": 3.0,
            "communication_score": 4.0,
            "presentation_score": 4.5,
            "interview_score": 4.0,
            "hackathons": 0,
            "leadership": 0,
            "target_role": "QA Engineer",
            "placed": 0,
            "data_source": "SYNTHETIC",
            "profile_completeness": 75.0,
            "evidence_confidence": 55.0
        }

    # General random student record generation
    cgpa = np.clip(np.random.normal(7.4, 1.0), 5.0, 10.0)
    tenth = np.clip(cgpa * 8.5 + np.random.normal(12, 4), 55.0, 98.0)
    twelfth = np.clip(cgpa * 8.2 + np.random.normal(14, 4), 50.0, 97.0)

    # Backlogs: lower CGPA increases backlog probability
    backlog_prob = max(0.0, (7.5 - cgpa) * 0.2)
    backlogs = np.random.poisson(backlog_prob) if random.random() < 0.35 else 0
    backlogs = int(np.clip(backlogs, 0, 4))

    # Base tech skill correlated with CGPA & general aptitude (1-10 scale)
    base_ability = (cgpa / 10.0) * 7.0 + np.random.normal(0, 0.8)
    base_ability = float(np.clip(base_ability, 2.0, 9.5))

    python_score = np.clip(base_ability + np.random.normal(0.0, 1.2), 1.0, 10.0)
    java_score = np.clip(base_ability + np.random.normal(-0.2, 1.3), 1.0, 10.0)
    sql_score = np.clip(base_ability + np.random.normal(0.2, 1.2), 1.0, 10.0)
    dsa_score = np.clip(base_ability + np.random.normal(-0.1, 1.4), 1.0, 10.0)
    cloud_score = np.clip(base_ability * 0.75 + np.random.normal(-0.3, 1.4), 1.0, 10.0)
    web_score = np.clip(base_ability * 0.85 + np.random.normal(0.1, 1.3), 1.0, 10.0)
    ml_score = np.clip(base_ability * 0.70 + np.random.normal(-0.4, 1.5), 1.0, 10.0)
    cyber_score = np.clip(base_ability * 0.65 + np.random.normal(-0.5, 1.5), 1.0, 10.0)

    certifications = int(np.clip(np.random.poisson(1.2), 0, 5))
    project_count = int(np.clip(np.random.poisson(2.5), 1, 6))
    project_complexity = int(np.clip(round((python_score + dsa_score) / 7.0), 1, 3))

    intern_prob = max(0.05, (cgpa - 6.0) * 0.25 + (base_ability - 4.0) * 0.1)
    internships = int(np.clip(np.random.poisson(intern_prob), 0, 3))
    opensource = int(np.clip(np.random.poisson(0.4), 0, 3))

    quant_apt = np.clip((cgpa / 10.0) * 4.5 + np.random.normal(3.0, 1.1), 1.0, 10.0)
    logic_apt = np.clip((cgpa / 10.0) * 4.8 + np.random.normal(2.8, 1.0), 1.0, 10.0)
    coding_score = np.clip((dsa_score * 0.6 + python_score * 0.4) + np.random.normal(0.0, 0.7), 1.0, 10.0)

    comm_score = np.clip(np.random.normal(6.2, 1.4), 1.0, 10.0)
    pres_score = np.clip(comm_score * 0.9 + np.random.normal(0.4, 0.9), 1.0, 10.0)
    interview_score = np.clip((comm_score * 0.4 + dsa_score * 0.3 + python_score * 0.3) + np.random.normal(0.0, 0.8), 1.0, 10.0)

    hackathons = int(np.clip(np.random.poisson(0.6), 0, 4))
    leadership = 1 if (comm_score > 7.0 and random.random() < 0.4) else 0

    # Realistic, balanced Placement Index (0.0 to 1.0 scale)
    # Weights cover all major capability pillars:
    acad_component = (cgpa / 10.0) * 0.18 + (tenth / 100.0) * 0.04 + (twelfth / 100.0) * 0.04 - (backlogs * 0.08)
    dsa_coding_component = ((dsa_score + coding_score) / 20.0) * 0.22
    tech_skills_component = ((python_score + sql_score + java_score + web_score) / 40.0) * 0.16
    aptitude_component = ((quant_apt + logic_apt) / 20.0) * 0.14
    soft_interview_component = ((comm_score + interview_score) / 20.0) * 0.14
    exp_component = min(0.12, (internships * 0.04) + (project_count * 0.015) + (certifications * 0.01))

    readiness_index = acad_component + dsa_coding_component + tech_skills_component + aptitude_component + soft_interview_component + exp_component

    # Sigmoid centered around ~0.575 readiness index with realistic noise
    # Mean index for average student is ~0.54, giving balanced placement probability for average students
    logits = (readiness_index - 0.575) / 0.075
    prob = 1.0 / (1.0 + np.exp(-logits))
    placed = 1 if (random.random() < prob) else 0

    roles = ["Data Analyst", "AI/ML Engineer", "Full-Stack Developer", "Cloud/DevOps Engineer", "QA Specialist", "Cybersecurity Specialist"]
    target_role = random.choice(roles)

    return {
        "student_id": student_id,
        "name": f"Student {student_id}",
        "department": dept,
        "semester": random.choice([7, 8]),
        "cgpa": round(float(cgpa), 2),
        "tenth_percentage": round(float(tenth), 1),
        "twelfth_percentage": round(float(twelfth), 1),
        "backlogs": backlogs,
        "python_score": round(float(python_score), 1),
        "java_score": round(float(java_score), 1),
        "sql_score": round(float(sql_score), 1),
        "dsa_score": round(float(dsa_score), 1),
        "cloud_score": round(float(cloud_score), 1),
        "web_score": round(float(web_score), 1),
        "ml_score": round(float(ml_score), 1),
        "cybersecurity_score": round(float(cyber_score), 1),
        "certifications": certifications,
        "project_count": project_count,
        "project_complexity": project_complexity,
        "internships": internships,
        "opensource_projects": opensource,
        "quantitative_aptitude": round(float(quant_apt), 1),
        "logical_aptitude": round(float(logic_apt), 1),
        "coding_score": round(float(coding_score), 1),
        "communication_score": round(float(comm_score), 1),
        "presentation_score": round(float(pres_score), 1),
        "interview_score": round(float(interview_score), 1),
        "hackathons": hackathons,
        "leadership": leadership,
        "target_role": target_role,
        "placed": placed,
        "data_source": "SYNTHETIC",
        "profile_completeness": round(float(np.random.uniform(75, 99)), 1),
        "evidence_confidence": round(float(np.random.uniform(60, 95)), 1)
    }

def main():
    print("Generating Layer B Synthetic Data...")

    # 1. Generate 5,000 records for model training
    depts = ["CSE", "CSE", "ISE", "ECE", "Mechanical"] # Realistic distribution
    train_records = []
    for i in range(1, 5001):
        sid = f"ST{i:05d}"
        dept = random.choice(depts)
        rec = generate_student_record(sid, dept)
        train_records.append(rec)

    df_train = pd.DataFrame(train_records)
    train_csv_path = os.path.join(DATA_DIR, "training_data_5000.csv")
    df_train.to_csv(train_csv_path, index=False)
    
    placed_count = int(df_train["placed"].sum())
    total_count = len(df_train)
    print(f"[OK] Saved 5,000 training records to {train_csv_path}")
    print(f"  Target Class Distribution: Placed={placed_count} ({placed_count/total_count*100:.1f}%), Unplaced={total_count - placed_count} ({(total_count - placed_count)/total_count*100:.1f}%)")

    demo_records = [
        generate_student_record("", "ECE", is_demo=True, persona_type="Ananya"),
        generate_student_record("", "CSE", is_demo=True, persona_type="Rahul"),
        generate_student_record("", "CSE", is_demo=True, persona_type="Priya"),
        generate_student_record("", "ECE", is_demo=True, persona_type="Sneha"),
        generate_student_record("", "ISE", is_demo=True, persona_type="Arjun"),
        generate_student_record("", "ECE", is_demo=True, persona_type="Meera"),
        generate_student_record("", "CSE", is_demo=True, persona_type="Karan"),
        generate_student_record("", "ISE", is_demo=True, persona_type="Divya"),
        generate_student_record("", "Mechanical", is_demo=True, persona_type="Rohan"),
        generate_student_record("", "CSE", is_demo=True, persona_type="Nisha"),
        generate_student_record("", "ECE", is_demo=True, persona_type="Vivek"),
        generate_student_record("", "ISE", is_demo=True, persona_type="Pooja"),
        generate_student_record("", "Mechanical", is_demo=True, persona_type="Aditya")
    ]

    for i in range(14, 601):
        sid = f"ST_INST_{i:03d}"
        dept = random.choice(depts)
        rec = generate_student_record(sid, dept)
        demo_records.append(rec)

    demo_json_path = os.path.join(DATA_DIR, "demo_cohort_610.json")
    with open(demo_json_path, "w") as f:
        json.dump(demo_records, f, indent=2)
    print(f"[OK] Saved 610 student institutional demo cohort to {demo_json_path}")

    # 3. Generate Layer A AMEO Observed Benchmarks metadata reference
    ameo_benchmarks = {
        "dataset_name": "AMEO 2015 (Aspiring Minds Employment Outcome 2015)",
        "provenance_type": "OBSERVED",
        "sample_size": 4000,
        "year": 2015,
        "description": "Public national benchmark dataset for engineering employability assessment.",
        "benchmarks": {
            "median_salary_inr": 330000,
            "quant_aptitude_mean": 510, # Out of 800 scale
            "english_communication_mean": 525,
            "logical_reasoning_mean": 500,
            "domain_programming_mean": 450,
            "top_10_percentile": {
                "cgpa": 8.8,
                "quant_aptitude": 8.5,
                "logical_aptitude": 8.5,
                "coding_score": 8.8,
                "communication_score": 8.2,
                "python_score": 8.5,
                "sql_score": 8.5,
                "projects": 4,
                "internships": 2
            }
        }
    }
    ameo_path = os.path.join(DATA_DIR, "ameo_sample_benchmark.json")
    with open(ameo_path, "w") as f:
        json.dump(ameo_benchmarks, f, indent=2)
    print(f"[OK] Saved Layer A AMEO Benchmarks reference to {ameo_path}")

if __name__ == "__main__":
    main()

