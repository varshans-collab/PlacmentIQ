import os
import json
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "backend", "model_artifacts")

FEATURE_COLUMNS = [
    "cgpa", "tenth_percentage", "twelfth_percentage", "backlogs",
    "python_score", "java_score", "sql_score", "dsa_score", "cloud_score",
    "web_score", "ml_score", "cybersecurity_score", "certifications",
    "project_count", "project_complexity", "internships", "opensource_projects",
    "quantitative_aptitude", "logical_aptitude", "coding_score",
    "communication_score", "presentation_score", "interview_score",
    "hackathons", "leadership"
]

def main():
    print("Evaluating Trained Model Artifacts & Persona Sanity...")
    model_path = os.path.join(ARTIFACTS_DIR, "calibrated_rf_model.joblib")
    explainer_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.joblib")
    metrics_path = os.path.join(ARTIFACTS_DIR, "governance_metrics.json")
    demo_json = os.path.join(DATA_DIR, "demo_cohort_610.json")

    model = joblib.load(model_path)
    explainer = joblib.load(explainer_path)

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    with open(demo_json, "r") as f:
        cohort = json.load(f)

    print("\n--- MODEL GOVERNANCE SUMMARY ---")
    print(f"Model Type: {metrics['model_type']}")
    print(f"Accuracy:   {metrics['metrics']['accuracy']*100:.2f}%")
    print(f"ROC-AUC:    {metrics['metrics']['roc_auc']:.4f}")
    print(f"F1 Score:   {metrics['metrics']['f1_score']:.4f}")

    print("\n--- DEMO PERSONA EVALUATION ---")
    personas = [cohort[0], cohort[1], cohort[2]] # Ananya, Rahul, Priya

    for p in personas:
        feat_df = pd.DataFrame([[p[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        prob = model.predict_proba(feat_df)[0][1]
        score = round(prob * 100, 1)

        if score < 60:
            status = "Needs Training"
        elif score < 80:
            status = "Near-Ready"
        else:
            status = "Ready"

        print(f"Persona: {p['name']} ({p['student_id']})")
        print(f"  Target Role: {p['target_role']}")
        print(f"  Calibrated Prob: {prob:.4f} -> Readiness Score: {score}% ({status})")

    print("\n[OK] Evaluation complete. Model artifacts ready for backend deployment.")

if __name__ == "__main__":
    main()
