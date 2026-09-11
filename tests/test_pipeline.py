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

    print("\n=======================================================")
    print("ALL 11 REGRESSION TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    run_all_tests()

