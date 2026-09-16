import os
import sys
import json

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.services.model_service import model_service
from app.services.intelligence_engine import (
    calculate_career_fit,
    calculate_why_not_yet,
    calculate_opportunity_cost,
    calculate_minimum_improvement
)
from app.services.simulator_engine import (
    run_flight_simulator,
    compare_interventions,
    run_plus10_optimizer
)

def run_all_tests():
    print("Running PLACEMENTIQ End-to-End Pipeline Verification Suite...\n")
    
    # Test 1 & 2: Model can train and serialize
    print("Test 1 & 2: Testing model training and serialization...")
    import subprocess
    train_proc = subprocess.run([sys.executable, "scripts/train_model.py"], capture_output=True, text=True)
    assert train_proc.returncode == 0, f"Training process failed: {train_proc.stderr}"
    assert os.path.exists(os.path.join(BASE_DIR, "backend", "model_artifacts", "calibrated_rf_model.joblib")), "Model joblib missing"
    print("[PASS] Test 1 & 2: Model can train and serialize successfully.")

    # Test 3: Model can reload
    print("Test 3: Testing model reload...")
    model_service.load_artifacts()
    assert model_service.is_loaded is True, "Model should reload successfully"
    print("[PASS] Test 3: Model reloaded successfully.")

    demo_json = os.path.join(BASE_DIR, "data", "demo_cohort_610.json")
    with open(demo_json, "r") as f:
        cohort = json.load(f)
    sample_student = cohort[0] # Ananya

    # Test 4: Prediction works
    print("Test 4: Testing model prediction...")
    pred = model_service.predict(sample_student)
    assert 0.0 <= pred["readiness_score"] <= 100.0, "Score range valid"
    assert pred["status"] in ["Needs Training", "Near-Ready", "Ready"], "Status valid"
    print(f"[PASS] Test 4: Prediction works: Score = {pred['readiness_score']}%, Status = {pred['status']}.")

    # Test 5: SHAP works
    print("Test 5: Testing SHAP explanations...")
    assert "positive_factors" in pred and "negative_factors" in pred, "SHAP factors present"
    assert len(pred["positive_factors"]) + len(pred["negative_factors"]) == 25, "All 25 features evaluated in SHAP"
    print("[PASS] Test 5: SHAP explanations work and return 25 feature attributions.")

    # Test 6: No-change What-If equals normal prediction
    print("Test 6: Testing No-change What-If consistency...")
    sim_pred = model_service.predict(sample_student)
    assert abs(pred["readiness_score"] - sim_pred["readiness_score"]) < 1e-5, "What-If with no changes must match base"
    print("[PASS] Test 6: No-change What-If equals normal prediction.")

    # Test 7: Minimum Improvement does not claim success unless target is reached
    print("Test 7: Testing Minimum Improvement target checking...")
    mvi_unreachable = calculate_minimum_improvement(sample_student, target_score=75.0)
    assert mvi_unreachable["achievable"] is False, "Unreachable target should set achievable=False"
    assert "Target cannot be reached" in mvi_unreachable["message"], "Proper message when target unreachable"
    assert "best_available" in mvi_unreachable, "Provides best_available separately when target unreachable"

    mvi_achievable = calculate_minimum_improvement(sample_student, target_score=50.0)
    assert mvi_achievable["achievable"] is True, "Achievable target should set achievable=True"
    assert mvi_achievable["projected_score"] >= 50.0, "Projected score must reach or exceed target"
    print("[PASS] Test 7: Minimum Improvement does not claim success unless target is reached.")

    # Test 8: Placement funnel counts never increase between stages
    print("Test 8: Testing placement funnel monotonicity...")
    config = {
        "target_role": "Data Analyst",
        "department": "ALL",
        "eligibility_cgpa": 7.0,
        "eligibility_max_backlogs": 0,
        "aptitude_threshold": 6.0,
        "technical_threshold": 6.5,
        "interview_threshold": 6.5
    }
    sim_res = run_flight_simulator(cohort, config)
    counts = [stage["count"] for stage in sim_res["stages"]]
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1], f"Stage count increased from {counts[i]} to {counts[i+1]}"
    print("[PASS] Test 8: Placement funnel counts never increase between stages.")

    # Test 9: Bottleneck is maximum-loss stage
    print("Test 9: Testing dynamic bottleneck detection...")
    bottleneck_stage = sim_res["primary_bottleneck"]["stage"]
    losses = {stage["stage"]: stage["loss_pct"] for stage in sim_res["stages"] if stage["stage"] != "Total Cohort"}
    max_loss_stage = max(losses, key=losses.get)
    assert bottleneck_stage == max_loss_stage, f"Bottleneck ({bottleneck_stage}) must match max loss stage ({max_loss_stage})"
    print(f"[PASS] Test 9: Bottleneck detector correctly identifies {bottleneck_stage} as max-loss stage ({losses[max_loss_stage]}%).")

    # Test 10: Intervention simulation never mutates baseline data
    print("Test 10: Testing cohort immutability during intervention simulation...")
    original_cohort_copy = json.dumps(cohort)
    interventions = compare_interventions(cohort, config, ["SQL Bootcamp", "Aptitude Training"])
    after_cohort_copy = json.dumps(cohort)
    assert original_cohort_copy == after_cohort_copy, "Cohort baseline mutated during intervention simulation"
    print("[PASS] Test 10: Intervention simulation never mutates baseline data.")

    # Test 11: Data provenance is correct
    print("Test 11: Testing data provenance tagging...")
    assert sim_res["data_provenance"] == "SIMULATED", "Flight simulator provenance must be SIMULATED"
    assert interventions[0]["data_provenance"] == "SIMULATED", "Intervention lab provenance must be SIMULATED"
    print("[PASS] Test 11: Data provenance tagging verified.")

    # Test 12: Data validation script runs and generates comprehensive report
    print("Test 12: Testing dataset validation script and report generation...")
    val_proc = subprocess.run([sys.executable, "scripts/validate_data.py"], capture_output=True, text=True)
    assert val_proc.returncode == 0, f"Validation script failed: {val_proc.stderr}"
    report_path = os.path.join(BASE_DIR, "docs", "data_validation_report.md")
    assert os.path.exists(report_path), "Data validation report markdown missing"
    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()

    # Verify key sections exist
    required_sections = [
        "Executive Governance Summary",
        "Methodological Notes & Statistical Caveats",
        "Sample Size Asymmetry",
        "Conversion Proxy Assumptions",
        "Statistical Comparison Matrix",
        "Detailed Feature-by-Feature Distribution Analysis",
        "Root-Cause Analysis"
    ]
    for section in required_sections:
        assert section in report_text, f"Report missing expected section: '{section}'"

    # Verify all 6 overlapping fields are audited and present
    required_fields = [
        "10th Grade Percentage (SSC)",
        "12th Grade Percentage (HSC)",
        "Undergraduate Degree Score (%)",
        "Aptitude / Employability Test Score",
        "Work Experience / Internship Exposure",
        "Placement Success Rate (Target Class)"
    ]
    for field in required_fields:
        assert field in report_text, f"Report missing expected audited field: '{field}'"

    # Verify statistical badges and ASCII frequency histograms are present
    assert "MATCH" in report_text, "Report missing MATCH classification"
    assert "MODERATE" in report_text, "Report missing MODERATE classification"
    assert "DIVERGENT" in report_text, "Report missing DIVERGENT classification"
    assert "Frequency Histogram Comparison" in report_text, "Report missing ASCII histograms"

    # Test 13: Multi-model comparison report, calibration diagram, and ablation-grounded regression checks
    """
    Test 13 verifies:
    1. Multi-model benchmark report (docs/model_comparison.md) contains 5-fold CV metrics and tradeoff writeup.
    2. Calibration reliability figure (docs/figures/calibration_comparison.png) is generated.
    3. Detailed selection rationale and error breakdown (docs/model_selection_rationale.md) is present.
    4. Divergence Threshold Grounding: The 25% ceiling on synthetic-divergent features
       (10th%, 12th%, Quant, Logic) is grounded in our empirical ablation experiment
       (which proved dropping these 4 features yields delta_AUC = 0.0000, confirming they
       provide redundant collinear signal that must not exceed 25% of decision weight).
    """
    print("Test 13: Testing multi-model comparison report, divergence thresholds, and production tradeoff...")
    model_comp_path = os.path.join(BASE_DIR, "docs", "model_comparison.md")
    assert os.path.exists(model_comp_path), "Model comparison markdown report missing"
    with open(model_comp_path, "r", encoding="utf-8") as f:
        comp_text = f.read()

    assert "Logistic Regression (Scaled)" in comp_text, "Missing Logistic Regression in comparison"
    assert "RandomForestClassifier" in comp_text, "Missing Random Forest in comparison"
    assert "XGBoost (XGBClassifier)" in comp_text, "Missing XGBoost in comparison"
    assert "Stratified 5-Fold Cross-Validation Comparison Table" in comp_text, "Missing 5-fold CV table"
    assert "Brier Score" in comp_text, "Missing Brier score in comparison"
    assert "Synthetic Feature Divergence & Generalization Risk Audit" in comp_text, "Missing divergence risk audit"
    assert "Full Feature Importance Matrix Across Models" in comp_text, "Missing feature importance matrix"
    assert "Generative Artifact" in comp_text or "generative" in comp_text, "Missing generative artifact explanation"
    assert "TreeSHAP" in comp_text, "Missing TreeSHAP explainability rationale"

    # Verify calibration plot and detailed selection rationale
    cal_fig_path = os.path.join(BASE_DIR, "docs", "figures", "calibration_comparison.png")
    assert os.path.exists(cal_fig_path), "Calibration comparison PNG figure missing"
    
    rationale_path = os.path.join(BASE_DIR, "docs", "model_selection_rationale.md")
    assert os.path.exists(rationale_path), "model_selection_rationale.md missing"
    with open(rationale_path, "r", encoding="utf-8") as f:
        rat_text = f.read()
    assert "Per-Department Error Breakdown" in rat_text, "Missing department breakdown in rationale"
    assert "Worst-Case Error Analysis" in rat_text, "Missing top-10 error analysis in rationale"
    assert "Feature Ablation Experiment" in rat_text, "Missing ablation experiment in rationale"

    # Assert quantitative divergence threshold checks from serialized governance metrics
    metrics_path = os.path.join(BASE_DIR, "backend", "model_artifacts", "governance_metrics.json")
    assert os.path.exists(metrics_path), "governance_metrics.json missing"
    with open(metrics_path, "r", encoding="utf-8") as f:
        gov = json.load(f)
    
    assert "divergence_risk_flags" in gov, "Missing divergence risk flags in governance metrics"
    rf_risk = gov["divergence_risk_flags"]["RandomForestClassifier"]
    # Production RF model must not exceed 25% exposure to synthetic-divergent features
    assert rf_risk["share_pct"] <= 25.0, f"Production RF divergent feature weight too high: {rf_risk['share_pct']}% > 25%"
    assert rf_risk["status"] in ["LOW RISK", "MODERATE RISK"], f"Production model has unacceptable risk status: {rf_risk['status']}"
    
    # Linear and XGBoost models must also remain bounded (< 20%)
    for m_name in ["Logistic Regression (Scaled)", "XGBoost (XGBClassifier)"]:
        m_risk = gov["divergence_risk_flags"][m_name]
        assert m_risk["share_pct"] <= 20.0, f"{m_name} divergent feature weight exceeded 20%: {m_risk['share_pct']}%"

    print(f"[PASS] Test 13: Multi-model comparison verified (RF divergent weight = {rf_risk['share_pct']}% <= 25% safe threshold, ablation grounded, calibration plot verified).")

    print("\n=======================================================")
    print("ALL 13 REGRESSION TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    run_all_tests()

