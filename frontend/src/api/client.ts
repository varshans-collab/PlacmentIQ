import axios from 'axios';
import {
  StudentDetailResponse,
  WhatIfResponse,
  SimulatorResponse,
  InterventionResult,
  TPOOverviewResponse,
  GovernanceMetricsResponse
} from '../types';

const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '';
const API_BASE = `${BASE_URL}/api`;

const apiClient = axios.create({
  baseURL: '',
  timeout: 10000
});

// Response interceptor for clean error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred';
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message = 'Request timed out after 10s. Please check backend connection and retry.';
    } else if (error.response?.data?.detail) {
      message = typeof error.response.data.detail === 'string'
        ? error.response.data.detail
        : JSON.stringify(error.response.data.detail);
    } else if (error.response?.data?.error) {
      message = error.response.data.error;
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

export const fetchStudentDetail = async (studentId: string, includeHeavy: boolean = false): Promise<StudentDetailResponse> => {
  const params: Record<string, any> = {};
  if (includeHeavy) params.include_heavy = 'true';
  const res = await apiClient.get<StudentDetailResponse>(`${API_BASE}/students/${studentId}`, { params });
  return res.data;
};

export const fetchOpportunityCost = async (studentId: string): Promise<{ student_id: string; matrix: any[]; data_provenance: string }> => {
  const res = await apiClient.get(`${API_BASE}/opportunity-cost/${studentId}`);
  return res.data;
};

export const fetchMinimumImprovement = async (studentId: string, targetScore: number = 75.0): Promise<{ student_id: string; result: any; data_provenance: string }> => {
  const res = await apiClient.get(`${API_BASE}/minimum-improvement/${studentId}`, {
    params: { target: targetScore }
  });
  return res.data;
};

export const fetchRoadmap = async (studentId: string, role?: string): Promise<{ student_id: string; target_role: string; milestones: any[]; data_provenance: string }> => {
  const res = await apiClient.get(`${API_BASE}/roadmap/${studentId}`, {
    params: { role }
  });
  return res.data;
};



export const fetchStudentsList = async (dept?: string, status?: string) => {
  const params: Record<string, string> = {};
  if (dept) params.dept = dept;
  if (status) params.status = status;
  const res = await apiClient.get(`${API_BASE}/students`, { params });
  return res.data;
};

export const runWhatIfSimulation = async (
  studentId: string,
  modifiedFeatures: Record<string, number>,
  targetRole?: string
): Promise<WhatIfResponse> => {
  const res = await apiClient.post<WhatIfResponse>(`${API_BASE}/what-if`, {
    student_id: studentId,
    modified_features: modifiedFeatures,
    target_role: targetRole
  });
  return res.data;
};

export const fetchTPOOverview = async (dept?: string): Promise<TPOOverviewResponse> => {
  const params: Record<string, string> = {};
  if (dept && dept !== 'ALL') params.dept = dept;
  const res = await apiClient.get<TPOOverviewResponse>(`${API_BASE}/tpo/overview`, { params });
  return res.data;
};

export const fetchSkillHeatmap = async (dept?: string, semester?: number, role?: string) => {
  const params: Record<string, any> = {};
  if (dept && dept !== 'ALL') params.dept = dept;
  if (semester && semester > 0) params.semester = semester;
  if (role && role !== 'ALL') params.role = role;
  const res = await apiClient.get(`${API_BASE}/tpo/heatmap`, { params });
  return res.data;
};

export const fetchVulnerableStudents = async (
  dept?: string,
  maxReadiness: number = 60,
  minBacklogs: number = 0,
  skillDeficit?: string,
  semester?: number,
  role?: string,
  riskLevel?: string,
  sortBy: string = 'readiness_asc'
) => {
  const params: Record<string, any> = { max_readiness: maxReadiness, min_backlogs: minBacklogs, sort_by: sortBy };
  if (dept && dept !== 'ALL') params.dept = dept;
  if (skillDeficit && skillDeficit !== 'ALL') params.skill_deficit = skillDeficit;
  if (semester && semester > 0) params.semester = semester;
  if (role && role !== 'ALL') params.role = role;
  if (riskLevel && riskLevel !== 'ALL') params.risk_level = riskLevel;
  const res = await apiClient.get(`${API_BASE}/tpo/vulnerable`, { params });
  return res.data;
};

export const validateCsvApi = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await apiClient.post(`${API_BASE}/students/validate-csv`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const runFlightSimulator = async (config: {
  target_role: string;
  department?: string;
  eligibility_cgpa?: number;
  eligibility_max_backlogs?: number;
  aptitude_threshold?: number;
  technical_threshold?: number;
  interview_threshold?: number;
}): Promise<SimulatorResponse> => {
  const res = await apiClient.post<SimulatorResponse>(`${API_BASE}/simulator/run`, config);
  return res.data;
};

export const compareInterventions = async (
  config: any,
  selectedInterventions: string[]
): Promise<{ interventions: InterventionResult[]; plus_10_optimizer: any }> => {
  const res = await apiClient.post(`${API_BASE}/simulator/interventions/compare`, {
    config,
    selected_interventions: selectedInterventions
  });
  return res.data;
};

export const extractResumeSkills = async (resumeText: string) => {
  const res = await apiClient.post(`${API_BASE}/resume/extract`, { resume_text: resumeText });
  return res.data;
};

export const submitMicroAssessment = async (studentId: string, skill: string, difficulty: string, score: number, passed: boolean) => {
  const res = await apiClient.post(`${API_BASE}/assessment`, {
    student_id: studentId,
    skill,
    difficulty,
    score,
    passed
  });
  return res.data;
};

export const fetchModelGovernance = async (): Promise<GovernanceMetricsResponse> => {
  const res = await apiClient.get<GovernanceMetricsResponse>(`${API_BASE}/model-info`);
  return res.data;
};

export const loginApi = async (email: string, password: string, role: string) => {
  const res = await apiClient.post(`${API_BASE}/auth/login`, { email, password, role });
  return res.data;
};

