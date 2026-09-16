# PLACEMENTIQ — AI Placement Intelligence & Intervention Simulator

> **Tagline:** Predict readiness. Explain the gaps. Simulate interventions. Improve placement outcomes.
>
> **Core Principle:** *“Most placement systems tell you who is ready. PlacementIQ goes further: it explains why a student is not ready, identifies the most valuable improvement, simulates where a placement pipeline may break, and helps an institution compare potential interventions.”*


---

## 1. Executive Summary & Core Positioning

PlacementIQ moves institutional career services beyond passive prediction. Traditional systems simply assign a fixed score to a student (`Student → Placement Score`). PlacementIQ implements a closed-loop intelligence and intervention simulator:

```text
Student Data → Predict → Explain → Diagnose → Recommend → Simulate → Optimize → Improve → Re-predict → Track
```

At the institutional level, PlacementIQ equips Training & Placement Officers (TPOs) with a decision-support platform:

```text
Student Cohort → Placement Funnel Simulation → Selection Bottleneck Detection → Intervention Simulation → Expected Impact → TPO Decision → Re-simulation
```

---

## 2. Three-Layer Data Provenance System & Empirical Validation

PlacementIQ enforces explicit data layer boundaries, empirical validation protocols, and visual provenance badges across every screen and API response:

- **`[OBSERVED]`** — Historical public source data (**AMEO 2015 / Aspiring Minds Employment Outcome 2015** and **Kaggle Campus Recruitment Benchmark Dataset** `Placement_Data_Full_Class.csv`). Used for national median salary benchmarks, percentile curves, and empirical validation baselines.
- **`[SYNTHETIC]`** — Computer-generated institutional prototype data (**5,000 training records** + **610-student institutional demonstration cohort** generated with deterministic seed `42`). Includes fictional demo personas **Ananya (ECE)**, **Rahul (CSE)**, and **Priya (CSE)**.
- **`[DERIVED]`** — Calculated indicators and gap analyses (Career Track Fit, Evidence Confidence, Profile Completeness, "Why Not Yet?" Gaps).
- **`[SIMULATED]`** — Counterfactual future scenarios dynamically generated during What-If slider changes, Opportunity Cost calculations, Placement Flight Simulator funnels, and Intervention Lab experiments.

### Empirical Data Validation & Governance
To ensure data integrity and guard against unrealistic synthetic distributions, PlacementIQ includes an automated statistical validation pipeline ([`scripts/validate_data.py`](file:///scripts/validate_data.py)) that audits synthetic training data against real-world recruitment data ([`Placement_Data_Full_Class.csv`](file:///data/Placement_Data_Full_Class.csv)):
- **Two-Sample Kolmogorov-Smirnov (KS) Tests** & **Wasserstein-1 ($L_1$) Distances** across overlapping academic and outcome dimensions.
- **Audit Findings**:
  - `[MATCH]` **Work Experience Rate**: Empirical 34.4% vs Synthetic 36.0% (KS $D = 0.016$, $p = 1.00$).
  - `[MODERATE]` **Degree Score**: Converted CGPA proxy ($\text{CGPA} \times 9.5$) aligns closely in median ($70.4\%$ vs $66.0\%$) and IQR (KS $D = 0.243$).
  - `[MODERATE]` **Placement Rate**: Calibrated at 61.6% (vs real 68.8%) to mitigate class imbalance.
  - `[DIVERGENT]` **10th%/12th% School Percentiles & Aptitude**: Synthetic engineering percentiles (mean ~75%) reflect technical entrance cutoffs vs general multi-stream Kaggle baseline (mean ~66%), and synthetic aptitude enforces technical screening cutoffs.
- **Methodological Caveat**: With $N_1 = 215$ vs $N_2 = 5{,}000$, KS tests possess near-maximal statistical power ($D_{\text{crit}} \approx 0.113$ at $\alpha=0.01$), flagging demographic stream differences rather than dataset defect.
- **Automated Governance Report**: Published to [`docs/data_validation_report.md`](file:///docs/data_validation_report.md).

---

## 3. Real Machine Learning & XAI Architecture

1. **Multi-Model Benchmark & Cross-Validation**: PlacementIQ evaluates three distinct model families using stratified 5-fold cross-validation on Layer B synthetic data (documented in [`docs/model_comparison.md`](file:///docs/model_comparison.md)):
   - **Logistic Regression (Scaled)**: ROC-AUC **$0.7725 \pm 0.0091$**, Accuracy $71.96 \pm 1.63\%$, Brier Score $0.1854 \pm 0.0035$ (`🟢 LOW RISK` on divergent features, 9.05% weight share).
   - **XGBoost (XGBClassifier)**: ROC-AUC **$0.7612 \pm 0.0105$**, Accuracy $70.60 \pm 1.53\%$, Brier Score $0.1898 \pm 0.0040$ (`🟢 LOW RISK` on divergent features, 9.60% weight share).
   - **RandomForestClassifier**: ROC-AUC **$0.7538 \pm 0.0126$**, Accuracy $70.66 \pm 1.49\%$, Brier Score $0.1925 \pm 0.0040$ (`🟡 MODERATE RISK` on divergent features, 22.51% weight share).
2. **Production Model Architecture & Engineering Tradeoff**:
   - `CalibratedClassifierCV(RandomForestClassifier)` (120 estimators, max depth 12) is deliberately chosen as the production model over Logistic Regression.
   - *Why?* On our synthetic data, Logistic Regression slightly edges out tree ensembles on ROC-AUC ($0.773$ vs $0.754$) because synthetic labels were generated via a logistic sigmoid link function, which naturally favors generalized linear models. We do not expect this linear ranking to hold on real-world placement data with threshold non-linearities (e.g., passing a hard DSA bar offsetting low academic scores).
   - *The Tradeoff:* We trade $\sim 0.019$ raw ROC-AUC points to gain **exact, unapproximated TreeSHAP attributions** (`shap.TreeExplainer`) and native non-linear interaction modeling, which are core requirements for the *What-If Simulator* and *Why Not Yet?* gap diagnostic engines.
3. **Model Target**: Binary `placed = 0/1`. Output is calibrated probability $P(\text{placed}=1)$, converted to **Estimated Placement Readiness Score** ($0 - 100\%$).
4. **Local Explainability**: `shap.TreeExplainer` loaded from serialized `shap_explainer.joblib`. Dynamically attributes positive (+SHAP) and negative (-SHAP) feature contributions relative to the baseline expected value.
5. **Offline Training & Validation Workflow**:
   ```bash
   python scripts/generate_data.py
   python scripts/validate_data.py
   python scripts/train_model.py
   python scripts/evaluate_model.py
   ```

---

## 4. Flagship Institutional Modules

### A. Placement Flight Simulator
Simulates how a 610-student cohort moves through recruitment drive stages:
$$\text{Cohort (610)} \longrightarrow \text{Eligibility} \longrightarrow \text{Aptitude} \longrightarrow \text{Technical} \longrightarrow \text{Interview} \longrightarrow \text{Estimated Selections}$$
Calculates stage-by-stage loss percentages:
$$\text{Loss \%} = \frac{\text{Previous Stage Count} - \text{Current Stage Count}}{\text{Previous Stage Count}} \times 100$$

### B. Selection Bottleneck Detector & Placement Pre-Mortem
Dynamically identifies the recruitment stage with the highest percentage drop-off (e.g., Technical Round 62.4% loss) and generates a pre-mortem failure diagnosis (*"Assume this drive failed — why?"*) with targeted preventive recommendations.

### C. Intervention Experiment Lab & "+10 Students" Optimizer
Allows TPOs to test counterfactual scenarios (e.g., *SQL Bootcamp*, *Aptitude Training*, *Mock Interviews*, *DSA Intensive*). Evaluates baseline expected selections vs simulated selections and searches for single interventions or combined packages that achieve a target gain of **+10 selections**.

### D. Opportunity Cost & Minimum Viable Improvement Engine
Computes the **Efficiency Index** for every student skill improvement:
$$\text{Efficiency Index} = \frac{\Delta \text{ Readiness Score}}{\text{Estimated Effort Hours}}$$
Identifies the minimum viable combination of skill boosts needed for a student to cross the 75% placement readiness threshold.

---

## 5. API Reference

- `POST /api/predict` — Calculates readiness score, status, SHAP attributions, and career track fit for a student profile.
- `POST /api/what-if` — Runs counterfactual model prediction on modified feature vectors.
- `GET  /api/students/{id}` — Fetches complete student profile, SHAP explanations, skill gaps, opportunity cost matrix, and trajectory snapshots.
- `POST /api/students/upload` — Ingests batch student CSV file, validates schema, and saves to database.
- `GET  /api/tpo/overview` — Institutional KPIs, high-risk cohort counts, and Next-Best Institutional Action.
- `GET  /api/tpo/heatmap` — Department $\times$ Skill competency matrix with STRONG/MODERATE/DEFICIT badges.
- `GET  /api/tpo/vulnerable` — Filterable vulnerability query (Department, Max Readiness, Backlogs, Skill Deficits).
- `POST /api/simulator/run` — Executes Placement Flight Simulator on configured cohort and cutoffs.
- `POST /api/simulator/interventions/compare` — Runs Intervention Lab scenario comparisons and +10 optimizer.
- `GET  /api/model-info` — Exposes live scikit-learn governance metrics, confusion matrix, and data provenance definitions.

---

## 6. Project Setup & Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Backend & ML Setup
```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt

# 2. Generate Layer B data (5,000 training, 610 demo cohort, AMEO metadata)
python scripts/generate_data.py

# 3. Validate synthetic data against real benchmark dataset
python scripts/validate_data.py

# 4. Train Calibrated Random Forest & SHAP Explainer
python scripts/train_model.py

# 5. Evaluate trained artifacts
python scripts/evaluate_model.py

# 6. Start FastAPI Backend Server (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
```

### Frontend Setup
```bash
# 1. Install Node dependencies
cd frontend
npm install

# 2. Start Vite Dev Server (Port 5173 with proxy to 8000)
npm run dev

# Or build production bundle
npm run build
```

---

## 7. 3-Minute Judge Demo Walkthrough

1. **Step 1: Open Ananya (ST_DEMO_001)** — Show her 10.7% readiness score (*Needs Training*) and profile completeness.
2. **Step 2: Click "Why Not Yet?"** — Inspect role-specific skill gaps (SQL gap: -4.0, Internship exposure).
3. **Step 3: Click "Real SHAP XAI"** — Inspect positive and negative SHAP feature attributions relative to the baseline expected value.
4. **Step 4: Click "What-If Simulator"** — Increase SQL from 4.0 to 8.0 and DSA from 5.0 to 7.0. Click *Run Counterfactual Model Simulation* to demonstrate model-driven score projection.
5. **Step 5: Switch to Placement Flight Simulator** — Show 610-student cohort funnel ($610 \rightarrow \text{Eligible} \rightarrow \text{Aptitude} \rightarrow \text{Technical} \rightarrow \text{Interview} \rightarrow \text{Selections}$).
6. **Step 6: Show Bottleneck Detector** — Highlight Technical Round as primary drop-off stage (62.4% loss).
7. **Step 7: Open Intervention Lab** — Select *SQL Bootcamp* + *Mock Interviews*. Compare baseline vs simulated expected selections.
8. **Step 8: Show "+10 Students" Optimizer** — Demonstrate recommended intervention package.
9. **Step 9: Switch to TPO Command Center** — View Department average readiness comparison, Skill Heatmap, and Vulnerability filter.
10. **Step 10: Open Model & Data Governance** — Show live scikit-learn metrics (76.90% Accuracy, 0.8292 ROC-AUC), Confusion Matrix, and 3-Layer Data Provenance definitions (`[OBSERVED]`, `[SYNTHETIC]`, `[DERIVED]`, `[SIMULATED]`).

---

## 8. Verification & Testing

Run the automated end-to-end verification suite:
```bash
python tests/test_pipeline.py
```
Outputs complete PASS status across ML model inference, SHAP consistency, What-If counterfactual logic, Career Track Fit, Opportunity Cost efficiency, Flight Simulator funnels, and Intervention Lab optimization.
