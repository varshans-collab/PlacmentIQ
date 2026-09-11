import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import shap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "backend", "model_artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

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
    print("Training Genuine ML Model Pipeline...")
    train_csv = os.path.join(DATA_DIR, "training_data_5000.csv")
    if not os.path.exists(train_csv):
        raise FileNotFoundError(f"Training data not found at {train_csv}. Run generate_data.py first.")

    df = pd.read_csv(train_csv)
    X = df[FEATURE_COLUMNS]
    y = df["placed"]

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 1. Base Random Forest
    base_rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    base_rf.fit(X_train, y_train)

    # 2. Probability Calibration
    try:
        calibrated_model = CalibratedClassifierCV(estimator=base_rf, method="sigmoid", cv=5)
    except TypeError:
        calibrated_model = CalibratedClassifierCV(base_estimator=base_rf, method="sigmoid", cv=5)
        
    calibrated_model.fit(X_train, y_train)

    # 3. Model Evaluation on Test Set
    y_pred = calibrated_model.predict(X_test)
    y_prob = calibrated_model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature Importances from base RF
    importances = dict(zip(FEATURE_COLUMNS, base_rf.feature_importances_.round(4).tolist()))

    print(f"[OK] Model Trained Successfully!")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")

    # 4. Initialize SHAP Explainer on base tree model
    explainer = shap.TreeExplainer(base_rf)

    # 5. Save Artifacts
    model_path = os.path.join(ARTIFACTS_DIR, "calibrated_rf_model.joblib")
    base_rf_path = os.path.join(ARTIFACTS_DIR, "base_rf_model.joblib")
    explainer_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.joblib")

    joblib.dump(calibrated_model, model_path)
    joblib.dump(base_rf, base_rf_path)
    joblib.dump(explainer, explainer_path)

    metrics = {
        "dataset_name": "Layer B Synthetic Institutional Dataset",
        "total_records": len(df),
        "train_records": len(X_train),
        "test_records": len(X_test),
        "feature_count": len(FEATURE_COLUMNS),
        "model_type": "CalibratedClassifierCV (RandomForestClassifier)",
        "calibration_method": "Platt Sigmoidal Calibration",
        "training_seed": 42,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm
        },
        "feature_importances": importances,
        "expected_value": float(explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value)
    }

    metrics_path = os.path.join(ARTIFACTS_DIR, "governance_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    # Also export governance.json and metrics.json for compatibility
    with open(os.path.join(ARTIFACTS_DIR, "governance.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    with open(os.path.join(ARTIFACTS_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    feature_meta = {
        "total_features": len(FEATURE_COLUMNS),
        "features": FEATURE_COLUMNS,
        "feature_types": {col: "numeric" for col in FEATURE_COLUMNS},
        "target": "placed",
        "provenance": "SYNTHETIC_LAYER_B"
    }
    with open(os.path.join(ARTIFACTS_DIR, "feature_metadata.json"), "w") as f:
        json.dump(feature_meta, f, indent=2)

    print(f"[OK] Saved model artifacts to {ARTIFACTS_DIR}")

if __name__ == "__main__":
    main()
