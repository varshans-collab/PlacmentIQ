import sqlite3
import json
import os
from app.config import DB_PATH, DATA_DIR

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT,
        department TEXT,
        semester INTEGER,
        cgpa REAL,
        tenth_percentage REAL,
        twelfth_percentage REAL,
        backlogs INTEGER,
        python_score REAL,
        java_score REAL,
        sql_score REAL,
        dsa_score REAL,
        cloud_score REAL,
        web_score REAL,
        ml_score REAL,
        cybersecurity_score REAL,
        certifications INTEGER,
        project_count INTEGER,
        project_complexity INTEGER,
        internships INTEGER,
        opensource_projects INTEGER,
        quantitative_aptitude REAL,
        logical_aptitude REAL,
        coding_score REAL,
        communication_score REAL,
        presentation_score REAL,
        interview_score REAL,
        hackathons INTEGER,
        leadership INTEGER,
        target_role TEXT,
        placed INTEGER,
        data_source TEXT,
        profile_completeness REAL,
        evidence_confidence REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trajectory_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        month TEXT,
        readiness_score REAL,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        skill TEXT,
        difficulty TEXT,
        score REAL,
        passed INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Load / Sync 610 student cohort from json
    demo_json = os.path.join(DATA_DIR, "demo_cohort_610.json")
    if os.path.exists(demo_json):
        with open(demo_json, "r") as f:
            records = json.load(f)
        for r in records:
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
                r["student_id"], r.get("name", f"Student {r['student_id']}"), r["department"], r["semester"],
                r["cgpa"], r["tenth_percentage"], r["twelfth_percentage"], r["backlogs"], r["python_score"],
                r["java_score"], r["sql_score"], r["dsa_score"], r["cloud_score"], r["web_score"], r["ml_score"],
                r["cybersecurity_score"], r["certifications"], r["project_count"], r["project_complexity"],
                r["internships"], r["opensource_projects"], r["quantitative_aptitude"], r["logical_aptitude"],
                r["coding_score"], r["communication_score"], r["presentation_score"], r["interview_score"],
                r["hackathons"], r["leadership"], r["target_role"], r["placed"], r["data_source"],
                r["profile_completeness"], r["evidence_confidence"]
            ))
        
        # Seed trajectory snapshots for all 13 demo personas
        seed_trajectories(cursor)
        conn.commit()
        print("[OK] Synchronized SQLite Database with 600 student records and demo trajectories.")

    conn.close()

def seed_trajectories(cursor):
    months = ["September", "October", "November", "December"]
    
    # Trajectory curves for 13 demo personas
    demo_trajectories = {
        "ST_DEMO_001": [35.0, 42.0, 48.0, 53.7], # Ananya
        "ST_DEMO_002": [62.0, 67.0, 71.0, 78.5], # Rahul
        "ST_DEMO_003": [82.0, 85.0, 88.0, 92.0], # Priya
        "ST_DEMO_004": [70.0, 74.0, 78.0, 84.0], # Sneha
        "ST_DEMO_005": [40.0, 45.0, 49.0, 52.0], # Arjun
        "ST_DEMO_006": [65.0, 70.0, 74.0, 79.0], # Meera
        "ST_DEMO_007": [42.0, 48.0, 52.0, 56.0], # Karan
        "ST_DEMO_008": [72.0, 76.0, 80.0, 85.0], # Divya
        "ST_DEMO_009": [55.0, 59.0, 64.0, 68.0], # Rohan
        "ST_DEMO_010": [45.0, 49.0, 52.0, 55.0], # Nisha
        "ST_DEMO_011": [52.0, 56.0, 60.0, 64.0], # Vivek
        "ST_DEMO_012": [60.0, 64.0, 68.0, 72.0], # Pooja
        "ST_DEMO_013": [30.0, 34.0, 38.0, 42.0]  # Aditya
    }

    cursor.execute("DELETE FROM trajectory_snapshots WHERE student_id LIKE 'ST_DEMO_%'")

    for sid, scores in demo_trajectories.items():
        for m, s in zip(months, scores):
            status_text = "Ready" if s >= 80 else ("Near-Ready" if s >= 60 else "Needs Training")
            cursor.execute(
                "INSERT INTO trajectory_snapshots (student_id, month, readiness_score, status) VALUES (?, ?, ?, ?)",
                (sid, m, s, status_text)
            )
