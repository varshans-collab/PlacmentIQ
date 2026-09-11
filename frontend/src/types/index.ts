export type DataProvenanceType = 'OBSERVED' | 'SYNTHETIC' | 'DERIVED' | 'SIMULATED';

export interface Student {
  student_id: string;
  name: string;
  department: string;
  semester: number;
  cgpa: number;
  tenth_percentage: number;
  twelfth_percentage: number;
  backlogs: number;
  python_score: number;
  java_score: number;
  sql_score: number;
  dsa_score: number;
  cloud_score: number;
  web_score: number;
  ml_score: number;
  cybersecurity_score: number;
  certifications: number;
  project_count: number;
  project_complexity: number;
  internships: number;
  opensource_projects: number;
  quantitative_aptitude: number;
  logical_aptitude: number;
  coding_score: number;
  communication_score: number;
  presentation_score: number;
  interview_score: number;
  hackathons: number;
  leadership: number;
  target_role: string;
  placed?: number;
  data_source?: string;
  profile_completeness?: number;
  evidence_confidence?: number;
  readiness_score?: number;
  status?: string;
}

export interface ShapFactor {
  feature: string;
  feature_name: string;
  val: number;
  shap_value: number;
  is_positive: boolean;
}

export interface PredictionResult {
  student_id: string;
  readiness_score: number;
  status: string;
  calibrated_prob?: number;
  base_value: number;
  prediction_confidence: string;
  profile_completeness: number;
  evidence_confidence: number;
  positive_factors: ShapFactor[];
  negative_factors: ShapFactor[];
  all_shap?: Record<string, number>;
  next_best_action?: OpportunityCostItem;
  data_provenance: DataProvenanceType;
}

export interface WhyNotYetGap {
  feature: string;
  feature_name: string;
  current_val: number;
  required_val: number;
  gap: number;
  shap_impact: number;
  impact_score: number;
  explanation: string;
}

export interface OpportunityCostItem {
  feature: string;
  feature_name: string;
  intervention: string;
  current_value: number;
  simulated_value: number;
  delta_readiness: number;
  effort_hours: number;
  efficiency_index: number;
  recommendation: string;
}

export interface MinimumImprovementResult {
  required: boolean;
  current_score: number;
  target_score: number;
  needed_delta?: number;
  achieved_delta?: number;
  projected_score?: number;
  changes: OpportunityCostItem[];
}

export interface TrajectoryPoint {
  month: string;
  readiness_score: number;
  status: string;
}

export interface StudentDetailResponse {
  student: Student;
  prediction: PredictionResult;
  career_fit: Record<string, number>;
  why_not_yet: WhyNotYetGap[];
  opportunity_cost: OpportunityCostItem[];
  minimum_improvement: MinimumImprovementResult;
  trajectory: TrajectoryPoint[];
  data_provenance: DataProvenanceType;
}

export interface WhatIfResponse {
  student_id: string;
  target_role: string;
  original_score: number;
  original_status: string;
  projected_score: number;
  projected_status: string;
  score_delta: number;
  is_improvement: boolean;
  original_positive_factors: ShapFactor[];
  projected_positive_factors: ShapFactor[];
  updated_career_fit: Record<string, number>;
  updated_why_not_yet: WhyNotYetGap[];
  data_provenance: DataProvenanceType;
}

export interface FunnelStage {
  stage: string;
  count: number;
  passed: number;
  lost: number;
  loss_pct: number;
}

export interface BottleneckInfo {
  stage: string;
  loss_percentage: number;
  students_lost: number;
  key_deficits: string[];
  primary_skill_tested: string;
  recommendation: string;
}

export interface SimulatorResponse {
  target_role: string;
  department_filter: string;
  total_cohort: number;
  stages: FunnelStage[];
  selections: number;
  selection_rate: number;
  primary_bottleneck: BottleneckInfo;
  pre_mortem: string[];
  data_provenance: DataProvenanceType;
}

export interface InterventionResult {
  key: string;
  name: string;
  description: string;
  affected_students: number;
  baseline_selections: number;
  simulated_selections: number;
  delta_selections: number;
  effort: string;
  priority: string;
  data_provenance: DataProvenanceType;
}

export interface TPOOverviewResponse {
  total_students: number;
  overall_readiness_avg: number;
  ready_count: number;
  ready_pct: number;
  near_ready_count: number;
  near_ready_pct: number;
  needs_training_count: number;
  needs_training_pct: number;
  high_risk_count: number;
  department_breakdown: {
    department: string;
    total_students: number;
    avg_readiness: number;
    high_risk_count: number;
    high_risk_pct: number;
  }[];
  next_best_institutional_action: {
    title: string;
    affected_students: number;
    estimated_impact: string;
    effort: string;
    priority: string;
  };
  data_provenance: DataProvenanceType;
}

export interface GovernanceMetricsResponse {
  model_governance: {
    dataset_name: string;
    total_records: number;
    train_records: number;
    test_records: number;
    feature_count: number;
    model_type: string;
    calibration_method: string;
    training_seed: number;
    metrics: {
      accuracy: number;
      precision: number;
      recall: number;
      f1_score: number;
      roc_auc: number;
      confusion_matrix: number[][];
    };
    feature_importances: Record<string, number>;
  };
  ameo_benchmark_metadata: {
    dataset_name: string;
    provenance_type: string;
    sample_size: number;
    year: number;
    benchmarks: {
      median_salary_inr: number;
      quant_aptitude_mean: number;
      english_communication_mean: number;
      logical_reasoning_mean: number;
      top_10_percentile: Record<string, number>;
    };
  };
  provenance_labels: Record<string, string>;
}

export interface AuthUser {
  email: string;
  id: string;
  name: string;
}

export interface LoginResponse {
  authenticated: boolean;
  role: 'student' | 'rpo_tpo';
  redirect: string;
  token: string;
  user: AuthUser;
}
