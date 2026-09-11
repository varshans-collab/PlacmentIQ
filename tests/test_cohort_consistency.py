import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def post_json(endpoint, body):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def test_cross_module_cohort_consistency():
    # 1. Overview API Count
    overview_data = get_json("/api/tpo/overview")
    overview_count = overview_data["total_students"]

    # 2. Heatmap Source Count
    heatmap_data = get_json("/api/tpo/heatmap")
    heatmap_source_count = sum(dept["total"] for dept in heatmap_data["heatmap"])

    # 3. Student Search Directory Count
    search_data = get_json("/api/students")
    search_source_count = search_data["count"]

    # 4. Placement Flight Simulator Count
    simulator_data = post_json("/api/simulator/run", {
        "target_role": "Data Analyst",
        "department": "ALL"
    })
    simulator_source_count = simulator_data["total_cohort"]

    # 5. Intervention Lab Baseline Count
    intervention_data = post_json("/api/simulator/interventions/compare", {
        "config": {
            "target_role": "Data Analyst",
            "department": "ALL"
        },
        "selected_interventions": ["SQL Bootcamp"]
    })
    intervention_baseline_count = intervention_data["interventions"][0]["baseline_cohort_size"]

    # 6. Filtered Vulnerable Student Subset Count (Default cutoffs: max_readiness=60, min_backlogs=0)
    vulnerable_data = get_json("/api/tpo/vulnerable")
    vulnerable_filtered_count = len(vulnerable_data["vulnerable_students"])

    print("==================================================")
    print("INSTITUTIONAL BASELINE COHORT AUDIT:")
    print(f"  Overview Count: {overview_count}")
    print(f"  Heatmap Source Count: {heatmap_source_count}")
    print(f"  Search Source Count: {search_source_count}")
    print(f"  Simulator Baseline Count: {simulator_source_count}")
    print(f"  Intervention Baseline Count: {intervention_baseline_count}")
    print("--------------------------------------------------")
    print("FILTERED SUBSET AUDIT:")
    print(f"  Vulnerable Student Risk List Count: {vulnerable_filtered_count} (Filtered subset <= {overview_count})")
    print("==================================================")

    # Institutional Baseline Assertions (All = 610)
    assert overview_count == 610, f"Expected 610 overview count, got {overview_count}"
    assert heatmap_source_count == 610, f"Expected 610 heatmap source count, got {heatmap_source_count}"
    assert search_source_count == 610, f"Expected 610 search count, got {search_source_count}"
    assert simulator_source_count == 610, f"Expected 610 simulator count, got {simulator_source_count}"
    assert intervention_baseline_count == 610, f"Expected 610 intervention baseline count, got {intervention_baseline_count}"

    # Filtered Vulnerable Subset Assertions
    assert vulnerable_filtered_count <= overview_count, f"Vulnerable list ({vulnerable_filtered_count}) cannot exceed total cohort ({overview_count})"
    assert vulnerable_filtered_count == overview_data["needs_training_count"], f"Vulnerable count ({vulnerable_filtered_count}) should match overview needs_training_count ({overview_data['needs_training_count']})"

    print("[OK] PASS: Institutional Cohort Lock (610) and Filtered Vulnerable Subset Audit Verified.")

if __name__ == "__main__":
    test_cross_module_cohort_consistency()
