import urllib.request
import json

def get_json(url, data=None):
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
        return json.loads(urllib.request.urlopen(req).read())
    return json.loads(urllib.request.urlopen(url).read())

def main():
    print("==========================================")
    print("PLACEMENTIQ — LIVE BACKEND DATA AUDIT")
    print("==========================================")

    # 1. Health Check
    print("\n1. GET /health")
    health = get_json('http://127.0.0.1:8000/health')
    print("   Status:", health)

    # 2. TPO Overview
    print("\n2. GET /api/tpo/overview")
    ov = get_json('http://127.0.0.1:8000/api/tpo/overview')
    print("   Total Students:", ov['total_students'])
    print("   Overall Readiness Avg:", ov['overall_readiness_avg'])
    print("   Ready Count:", ov['ready_count'], f"({ov['ready_pct']}%)")
    print("   Near-Ready Count:", ov['near_ready_count'], f"({ov['near_ready_pct']}%)")
    print("   Needs Training Count:", ov['needs_training_count'], f"({ov['needs_training_pct']}%)")
    print("   High Risk Count:", ov['high_risk_count'])
    print("   Next Best Action:", ov['next_best_institutional_action'])
    print("   Department Breakdown:")
    for d in ov['department_breakdown']:
        print(f"     - {d['department']}: total={d['total_students']}, avg={d['avg_readiness']}%, risk={d['high_risk_count']} ({d['high_risk_pct']}%)")

    # 3. Heatmap
    print("\n3. GET /api/tpo/heatmap (First 5 rows)")
    hm = get_json('http://127.0.0.1:8000/api/tpo/heatmap')
    heatmap_rows = hm.get('heatmap', [])
    print("   Total Heatmap Rows:", len(heatmap_rows))
    for row in heatmap_rows[:5]:
        print("     -", row)

    # 4. Vulnerable Students
    print("\n4. GET /api/tpo/vulnerable")
    vuln = get_json('http://127.0.0.1:8000/api/tpo/vulnerable')
    vuln_list = vuln.get('vulnerable_students', [])
    print("   Total Vulnerable Students Count:", len(vuln_list))
    for v in vuln_list[:5]:
        print(f"     - {v['student_id']}: {v['name']} ({v['department']}) | Readiness: {v['readiness_score']}% | Gap: {v.get('primary_gap')}")

    # 5. Flight Simulator Run
    print("\n5. POST /api/simulator/run")
    sim_config = {
        'target_role': 'Data Analyst',
        'department': 'ALL',
        'eligibility_cgpa': 7.0,
        'eligibility_max_backlogs': 0,
        'aptitude_threshold': 6.0,
        'technical_threshold': 6.5,
        'interview_threshold': 6.5
    }
    sim = get_json('http://127.0.0.1:8000/api/simulator/run', sim_config)
    print("   Target Role:", sim['target_role'])
    print("   Total Cohort Size:", sim['total_cohort'])
    print("   Selections:", sim['selections'], f"({sim['selection_rate']:.1f}%)")
    print("   Primary Bottleneck:", sim['primary_bottleneck'])
    print("   Funnel Stages:")
    for st in sim['stages']:
        print(f"     - {st['stage']}: Count={st['count']}, Passed={st['passed']}, Lost={st['lost']} ({st['loss_pct']:.1f}%)")

    # 6. Intervention Comparison & Optimizer
    print("\n6. POST /api/simulator/interventions/compare")
    lab_config = {
        'config': sim_config,
        'selected_interventions': ['SQL Bootcamp', 'Aptitude Training', 'Mock Interviews', 'DSA Intensive']
    }
    lab = get_json('http://127.0.0.1:8000/api/simulator/interventions/compare', lab_config)
    print("   Interventions Comparison:")
    for inter in lab.get('interventions', []):
        print(f"     - {inter['name']}: Baseline={inter['baseline_selections']} -> Simulated={inter['simulated_selections']} (Delta: +{inter['delta_selections']}) | Effort: {inter['effort']}")
    print("   +10 Optimizer:", lab.get('plus_10_optimizer'))

    # 7. Student Detail: Ananya Sharma (ST_DEMO_001)
    print("\n7. GET /api/students/ST_DEMO_001 (Ananya Sharma)")
    ananya = get_json('http://127.0.0.1:8000/api/students/ST_DEMO_001?include_heavy=true')
    s = ananya['student']
    p = ananya['prediction']
    print(f"   Student: {s['name']} | ID: {s['student_id']} | Dept: {s['department']} | Sem: {s['semester']} | CGPA: {s['cgpa']} | Role: {s['target_role']}")
    print(f"   Readiness Score: {p['readiness_score']}% | Status: {p['status']}")
    print("   Top Positive SHAP Factors:", [(f['feature_name'], round(f['shap_value'], 2)) for f in p['positive_factors'][:3]])
    print("   Top Negative SHAP Factors:", [(f['feature_name'], round(f['shap_value'], 2)) for f in p['negative_factors'][:3]])
    print("   Top Why-Not-Yet Gaps:", [(g['feature_name'], g['current_val'], g['required_val']) for g in ananya['why_not_yet'][:3]])
    print("   Top Opportunity Cost Item:", ananya['opportunity_cost'][0] if ananya.get('opportunity_cost') else "N/A")
    print("   Trajectory Snapshots Count:", len(ananya.get('trajectory', [])))

if __name__ == '__main__':
    main()
