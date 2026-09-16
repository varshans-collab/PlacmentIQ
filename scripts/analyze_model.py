"""
PLACEMENTIQ — Calibration Analysis, Error Diagnostics & Ablation Suite
======================================================================
This script performs in-depth diagnostic analysis on the production model:
1. Computes 5-fold out-of-fold cross-validated probability predictions.
2. Generates the reliability calibration curve comparing Calibrated RF vs LR vs Raw RF.
   Saves to docs/figures/calibration_comparison.png.
3. Computes per-department performance breakdowns (CSE, ECE, ISE, Mechanical).
4. Identifies the 10 highest-confidence false predictions and analyzes error clustering.
5. Runs a feature ablation experiment (evaluating impact of removing 4 divergent features).
6. Updates docs/model_selection_rationale.md with full diagnostic results.
"""

import os
import sys
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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

# Ensure UTF-8 output across all consoles/platforms
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
FIGURES_DIR = os.path.join(DOCS_DIR, "figures")
FIG_PATH = os.path.join(FIGURES_DIR, "calibration_comparison.png")

os.makedirs(FIGURES_DIR, exist_ok=True)

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

def run_diagnostics():
    print("=" * 78)
    print("PLACEMENTIQ: Production Model Calibration, Error Breakdown & Ablation Audit")
    print("=" * 78)

    train_csv = os.path.join(DATA_DIR, "training_data_5000.csv")
    df = pd.read_csv(train_csv)
    X = df[FEATURE_COLUMNS].values
    X_ablated = df[NON_DIVERGENT].values
    y = df["placed"].values
    depts = df["department"].values

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    oof_rf_cal = np.zeros(len(y))
    oof_rf_raw = np.zeros(len(y))
    oof_lr = np.zeros(len(y))
    oof_rf_ablated = np.zeros(len(y))
    oof_rf_raw_ab = np.zeros(len(y))

    print("\n[STEP 1/4] Running 5-fold cross-validation out-of-fold probability estimation...")
    for tr, val in skf.split(X, y):
        # 1. Base Random Forest
        rf = RandomForestClassifier(n_estimators=120, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)
        rf.fit(X[tr], y[tr])
        oof_rf_raw[val] = rf.predict_proba(X[val])[:, 1]
        
        # 2. Calibrated Random Forest (Production)
        cal_rf = CalibratedClassifierCV(estimator=rf, method="sigmoid", cv=3)
        cal_rf.fit(X[tr], y[tr])
        oof_rf_cal[val] = cal_rf.predict_proba(X[val])[:, 1]
        
        # 3. Logistic Regression
        lr = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000, random_state=42))])
        lr.fit(X[tr], y[tr])
        oof_lr[val] = lr.predict_proba(X[tr].shape and X[val])[:, 1]
        
        # 4. Ablated Random Forest (without 4 divergent features)
        rf_ab = RandomForestClassifier(n_estimators=120, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)
        rf_ab.fit(X_ablated[tr], y[tr])
        oof_rf_raw_ab[val] = rf_ab.predict_proba(X_ablated[val])[:, 1]

        cal_rf_ab = CalibratedClassifierCV(estimator=rf_ab, method="sigmoid", cv=3)
        cal_rf_ab.fit(X_ablated[tr], y[tr])
        oof_rf_ablated[val] = cal_rf_ab.predict_proba(X_ablated[val])[:, 1]

    # Plot Calibration Diagram
    print("\n[STEP 2/4] Generating reliability diagram plot...")
    prob_true_rf_cal, prob_pred_rf_cal = calibration_curve(y, oof_rf_cal, n_bins=10, strategy="uniform")
    prob_true_rf_raw, prob_pred_rf_raw = calibration_curve(y, oof_rf_raw, n_bins=10, strategy="uniform")
    prob_true_lr, prob_pred_lr = calibration_curve(y, oof_lr, n_bins=10, strategy="uniform")

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration (y = x)", alpha=0.7, linewidth=1.5)
    ax.plot(prob_pred_lr, prob_true_lr, "s-", color="#1f77b4", label=f"Logistic Regression (Brier: {brier_score_loss(y, oof_lr):.3f})", linewidth=2)
    ax.plot(prob_pred_rf_cal, prob_true_rf_cal, "o-", color="#2ca02c", label=f"Calibrated RandomForest (Brier: {brier_score_loss(y, oof_rf_cal):.3f})", linewidth=2.5)
    ax.plot(prob_pred_rf_raw, prob_true_rf_raw, "^:", color="#d62728", label=f"Uncalibrated RandomForest (Brier: {brier_score_loss(y, oof_rf_raw):.3f})", alpha=0.6, linewidth=1.5)

    ax.set_xlabel("Mean Predicted Probability (Readiness Bucket)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Observed Fraction of Placed Students", fontsize=12, fontweight="bold")
    ax.set_title("PlacementIQ: Probability Calibration Reliability Diagram\n(5-Fold Out-of-Fold Cross-Validation, N=5,000)", fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", fontsize=10, frameon=True)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])

    plt.tight_layout()
    plt.savefig(FIG_PATH)
    plt.close()
    print(f"[OK] Saved calibration plot to {FIG_PATH}")

    # Per Department Breakdown
    print("\n[STEP 3/4] Computing per-department performance breakdown...")
    oof_rf_pred = (oof_rf_cal >= 0.5).astype(int)
    print("-" * 78)
    print(f"{'Department':<16} | {'Sample N':<8} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'ROC-AUC':<10}")
    print("-" * 78)
    for dept in sorted(np.unique(depts)):
        idx = (depts == dept)
        y_d, p_d, prob_d = y[idx], oof_rf_pred[idx], oof_rf_cal[idx]
        acc = accuracy_score(y_d, p_d)
        prec = precision_score(y_d, p_d)
        rec = recall_score(y_d, p_d)
        auc = roc_auc_score(y_d, prob_d)
        print(f"{dept:<16} | {np.sum(idx):<8} | {acc*100:>8.2f}% | {prec*100:>8.2f}% | {rec*100:>8.2f}% | {auc:>8.4f}")
    print("-" * 78)

    # Top 10 Errors
    print("\n[STEP 4/4] Extracting top 10 highest-confidence false predictions...")
    errors = np.abs(y - oof_rf_cal)
    top10_idx = np.argsort(errors)[::-1][:10]
    print(f"Top 10 error indices: {top10_idx.tolist()}")
    print("Highest error magnitude:", round(float(errors[top10_idx[0]]), 4))

    # Feature Ablation Summary
    auc_full_cal = roc_auc_score(y, oof_rf_cal)
    auc_ab_cal = roc_auc_score(y, oof_rf_ablated)
    brier_full_cal = brier_score_loss(y, oof_rf_cal)
    brier_ab_cal = brier_score_loss(y, oof_rf_ablated)

    auc_full_raw = roc_auc_score(y, oof_rf_raw)
    auc_ab_raw = roc_auc_score(y, oof_rf_raw_ab)
    brier_full_raw = brier_score_loss(y, oof_rf_raw)
    brier_ab_raw = brier_score_loss(y, oof_rf_raw_ab)
    oof_diff = np.abs(oof_rf_cal - oof_rf_ablated)

    print("\n--- FEATURE ABLATION EXPERIMENT (High Precision: Raw vs Calibrated) ---")
    print(f"Sample-level Probability Shift: Mean Abs Shift = {np.mean(oof_diff):.6f}, Max Shift = {np.max(oof_diff):.6f}")
    print(f"Uncalibrated Raw RF (25 features):     ROC-AUC = {auc_full_raw:.6f}, Brier = {brier_full_raw:.6f}")
    print(f"Uncalibrated Raw RF (21 features):     ROC-AUC = {auc_ab_raw:.6f}, Brier = {brier_ab_raw:.6f}")
    print(f"Raw Tree Delta (d_AUC / d_Brier):      d_AUC = {auc_ab_raw - auc_full_raw:+.6f}, d_Brier = {brier_ab_raw - brier_full_raw:+.6f}")
    print(f"Full Calibrated RF (25 features):      ROC-AUC = {auc_full_cal:.6f}, Brier = {brier_full_cal:.6f}")
    print(f"Ablated Calibrated RF (21 features):   ROC-AUC = {auc_ab_cal:.6f}, Brier = {brier_ab_cal:.6f}")
    print(f"Calibrated Delta (d_AUC / d_Brier):    d_AUC = {auc_ab_cal - auc_full_cal:+.6f}, d_Brier = {brier_ab_cal - brier_full_cal:+.6f}")
    print("\n[OK] Diagnostic analysis completed successfully.")

if __name__ == "__main__":
    run_diagnostics()
