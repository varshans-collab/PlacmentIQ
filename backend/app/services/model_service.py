import os
import joblib
import numpy as np
import pandas as pd
from app.config import ARTIFACTS_DIR, FEATURE_COLUMNS

FEATURE_NAME_MAP = {
    "cgpa": "CGPA",
    "tenth_percentage": "10th Percentage",
    "twelfth_percentage": "12th Percentage",
    "backlogs": "Active Backlogs",
    "python_score": "Python Proficiency",
    "java_score": "Java Proficiency",
    "sql_score": "SQL & Databases",
    "dsa_score": "Data Structures & Algorithms",
    "cloud_score": "Cloud & DevOps",
    "web_score": "Web Development",
    "ml_score": "Machine Learning",
    "cybersecurity_score": "Cybersecurity",
    "certifications": "Certifications",
    "project_count": "Projects Built",
    "project_complexity": "Project Complexity",
    "internships": "Internship Experience",
    "opensource_projects": "Open Source Contributions",
    "quantitative_aptitude": "Quantitative Aptitude",
    "logical_aptitude": "Logical Reasoning",
    "coding_score": "Hands-on Coding",
    "communication_score": "Communication Skills",
    "presentation_score": "Presentation Ability",
    "interview_score": "Interview Performance",
    "hackathons": "Hackathon Experience",
    "leadership": "Leadership Roles"
}

class ModelService:
    def __init__(self):
        self.calibrated_model = None
        self.base_rf = None
        self.explainer = None
        self.expected_value = 0.5
        self.is_loaded = False

    def load_artifacts(self):
        model_path = os.path.join(ARTIFACTS_DIR, "calibrated_rf_model.joblib")
        base_rf_path = os.path.join(ARTIFACTS_DIR, "base_rf_model.joblib")
        explainer_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.joblib")

        if os.path.exists(model_path) and os.path.exists(explainer_path):
            self.calibrated_model = joblib.load(model_path)
            self.base_rf = joblib.load(base_rf_path)
            self.explainer = joblib.load(explainer_path)
            
            exp_val = self.explainer.expected_value
            if isinstance(exp_val, (list, np.ndarray)):
                self.expected_value = float(exp_val[1]) if len(exp_val) > 1 else float(exp_val[0])
            else:
                self.expected_value = float(exp_val)
            
            self.is_loaded = True
            print("[OK] ModelService loaded calibrated RF model & SHAP TreeExplainer successfully.")
        else:
            print(f"[WARNING] Model artifacts not found at {ARTIFACTS_DIR}. Run train_model.py script.")

    def predict(self, feature_dict: dict, include_shap: bool = True) -> dict:
        if not self.is_loaded:
            self.load_artifacts()

        # Construct DataFrame in exact feature order
        row = [float(feature_dict.get(col, 5.0)) for col in FEATURE_COLUMNS]
        X = pd.DataFrame([row], columns=FEATURE_COLUMNS)

        # 1. Calibrated Probability Prediction
        prob = float(self.calibrated_model.predict_proba(X)[0][1])
        readiness_score = round(prob * 100.0, 1)

        if readiness_score < 60.0:
            status = "Needs Training"
        elif readiness_score < 80.0:
            status = "Near-Ready"
        else:
            status = "Ready"

        if not include_shap:
            return {
                "readiness_score": readiness_score,
                "status": status,
                "calibrated_prob": round(prob, 4),
                "base_value": round(self.expected_value * 100.0, 1),
                "positive_factors": [],
                "negative_factors": [],
                "all_shap": {}
            }

        # 2. Real SHAP TreeExplainer Local Attribution
        shap_values = self.explainer.shap_values(X)
        if isinstance(shap_values, list):
            vals = shap_values[1][0] # class 1 attributions
        elif len(shap_values.shape) == 3:
            vals = shap_values[0, :, 1]
        else:
            vals = shap_values[0]

        positive_factors = []
        negative_factors = []

        for col, val, shap_v in zip(FEATURE_COLUMNS, row, vals):
            shap_rounded = round(float(shap_v), 4)
            item = {
                "feature": col,
                "feature_name": FEATURE_NAME_MAP.get(col, col),
                "val": round(float(val), 1),
                "shap_value": shap_rounded,
                "is_positive": bool(shap_v >= 0)
            }
            if shap_v >= 0:
                positive_factors.append(item)
            else:
                negative_factors.append(item)

        # Sort factors by magnitude
        positive_factors.sort(key=lambda x: x["shap_value"], reverse=True)
        negative_factors.sort(key=lambda x: x["shap_value"]) # most negative first

        return {
            "readiness_score": readiness_score,
            "status": status,
            "calibrated_prob": round(prob, 4),
            "base_value": round(self.expected_value * 100.0, 1),
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "all_shap": {col: round(float(v), 4) for col, v in zip(FEATURE_COLUMNS, vals)}
        }

    def predict_batch(self, student_dicts: list) -> list:
        if not self.is_loaded:
            self.load_artifacts()

        if not student_dicts:
            return []

        rows = [[float(s.get(col, 5.0)) for col in FEATURE_COLUMNS] for s in student_dicts]
        X = pd.DataFrame(rows, columns=FEATURE_COLUMNS)

        probs = self.calibrated_model.predict_proba(X)[:, 1]

        results = []
        for prob in probs:
            p_val = float(prob)
            score = round(p_val * 100.0, 1)
            if score < 60.0:
                st = "Needs Training"
            elif score < 80.0:
                st = "Near-Ready"
            else:
                st = "Ready"
            results.append({
                "readiness_score": score,
                "status": st,
                "calibrated_prob": round(p_val, 4)
            })

        return results

model_service = ModelService()
