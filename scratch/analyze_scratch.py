import os
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, brier_score_loss
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
df = pd.read_csv(os.path.join(DATA_DIR, "training_data_5000.csv"))

FEATURE_COLUMNS = [
    "cgpa", "tenth_percentage", "twelfth_percentage", "backlogs",
    "python_score", "java_score", "sql_score", "dsa_score", "cloud_score",
    "web_score", "ml_score", "cybersecurity_score", "certifications",
    "project_count", "project_complexity", "internships", "opensource_projects",
    "quantitative_aptitude", "logical_aptitude", "coding_score",
    "communication_score", "presentation_score", "interview_score",
    "hackathons", "leadership"
]
DIVERGENT = ["tenth_percentage", "twelfth_percentage", "quantitative_aptitude", "logical_aptitude"]
NON_DIVERGENT = [c for c in FEATURE_COLUMNS if c not in DIVERGENT]

X = df[FEATURE_COLUMNS].values
X_ablated = df[NON_DIVERGENT].values
y = df["placed"].values
depts = df["department"].values

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

oof_rf_prob = np.zeros(len(y))
oof_lr_prob = np.zeros(len(y))
oof_rf_uncal_prob = np.zeros(len(y))
oof_rf_ablated_prob = np.zeros(len(y))

for tr, val in skf.split(X, y):
    # Full RF
    rf = RandomForestClassifier(n_estimators=120, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)
    rf.fit(X[tr], y[tr])
    oof_rf_uncal_prob[val] = rf.predict_proba(X[val])[:, 1]
    
    cal_rf = CalibratedClassifierCV(estimator=rf, method="sigmoid", cv=3)
    cal_rf.fit(X[tr], y[tr])
    oof_rf_prob[val] = cal_rf.predict_proba(X[val])[:, 1]
    
    # Full LR
    lr = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000, random_state=42))])
    lr.fit(X[tr], y[tr])
    oof_lr_prob[val] = lr.predict_proba(X[val])[:, 1]
    
    # Ablated RF
    rf_ab = RandomForestClassifier(n_estimators=120, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)
    cal_rf_ab = CalibratedClassifierCV(estimator=rf_ab, method="sigmoid", cv=3)
    cal_rf_ab.fit(X_ablated[tr], y[tr])
    oof_rf_ablated_prob[val] = cal_rf_ab.predict_proba(X_ablated[val])[:, 1]

print("=== 5-Fold OOF Full vs Ablated ROC-AUC ===")
auc_full_rf = roc_auc_score(y, oof_rf_prob)
auc_ab_rf = roc_auc_score(y, oof_rf_ablated_prob)
auc_lr = roc_auc_score(y, oof_lr_prob)
print(f"Full Calibrated RF AUC:    {auc_full_rf:.4f} (Brier: {brier_score_loss(y, oof_rf_prob):.4f})")
print(f"Ablated Calibrated RF AUC: {auc_ab_rf:.4f} (Brier: {brier_score_loss(y, oof_rf_ablated_prob):.4f}, Delta: {auc_ab_rf - auc_full_rf:+.4f})")
print(f"Full LR AUC:               {auc_lr:.4f} (Brier: {brier_score_loss(y, oof_lr_prob):.4f})")

print("\n=== Calibration Curve Buckets (10 Bins) ===")
prob_true_rf, prob_pred_rf = calibration_curve(y, oof_rf_prob, n_bins=10, strategy="uniform")
prob_true_lr, prob_pred_lr = calibration_curve(y, oof_lr_prob, n_bins=10, strategy="uniform")
prob_true_uncal, prob_pred_uncal = calibration_curve(y, oof_rf_uncal_prob, n_bins=10, strategy="uniform")

for i, (pred_rf, true_rf) in enumerate(zip(prob_pred_rf, prob_true_rf)):
    print(f"Bin {i+1:02d}: Pred Prob = {pred_rf:.3f}, True Rate = {true_rf:.3f}, Delta = {pred_rf - true_rf:+.3f} ({'Over-confident' if pred_rf > true_rf else 'Under-confident'})")

print("\n=== Per Department Breakdown for Calibrated RF ===")
oof_rf_pred = (oof_rf_prob >= 0.5).astype(int)
for dept in np.unique(depts):
    idx = (depts == dept)
    y_d = y[idx]
    p_d = oof_rf_pred[idx]
    prob_d = oof_rf_prob[idx]
    acc = accuracy_score(y_d, p_d)
    prec = precision_score(y_d, p_d)
    rec = recall_score(y_d, p_d)
    f1 = f1_score(y_d, p_d)
    auc = roc_auc_score(y_d, prob_d)
    print(f"Dept: {dept:<12} N={np.sum(idx):<4} PlacedRate={np.mean(y_d):.3f} Acc={acc:.4f} Prec={prec:.4f} Rec={rec:.4f} F1={f1:.4f} AUC={auc:.4f}")

print("\n=== Top 10 Highest-Confidence Errors (Sorted by |y - PredProb|) ===")
errors = np.abs(y - oof_rf_prob)
top10_idx = np.argsort(errors)[::-1][:10]
for rank, i in enumerate(top10_idx, 1):
    row = df.iloc[i]
    err_type = "False Positive (P=1, Y=0)" if y[i] == 0 else "False Negative (P=0, Y=1)"
    print(f"\n#{rank}: Student {row['student_id']} ({row['department']}) — {err_type}")
    print(f"   Actual: {y[i]}, PredProb: {oof_rf_prob[i]:.4f}, Readiness: {oof_rf_prob[i]*100:.1f}%")
    print(f"   Academics: CGPA={row['cgpa']}, 10th%={row['tenth_percentage']}, 12th%={row['twelfth_percentage']}, Backlogs={row['backlogs']}")
    print(f"   Technical: DSA={row['dsa_score']}, Coding={row['coding_score']}, Python={row['python_score']}, SQL={row['sql_score']}, Java={row['java_score']}")
    print(f"   Aptitude & Soft: Quant={row['quantitative_aptitude']}, Logic={row['logical_aptitude']}, Comm={row['communication_score']}, Intv={row['interview_score']}")
    print(f"   Exp: Internships={row['internships']}, Projects={row['project_count']}, Complexity={row['project_complexity']}, Certs={row['certifications']}")
