/**
 * 自动化测试看板 API 客户端
 */

import axios from 'axios';
import { loadConfig } from './config';

const automationApi = axios.create({
  baseURL: 'http://localhost:8000/api/v1/automation',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

automationApi.interceptors.request.use(async (config) => {
  try {
    const appConfig = await loadConfig();
    config.baseURL = appConfig.apiUrl + '/automation';
  } catch (error) {
    console.warn('[Automation API] Using default baseURL');
  }
  return config;
});

export interface AutomationStats {
  total_test_cases: number;
  total_execution_time_hours: number;
  total_manual_effort_saved_hours: number;
  total_projects: number;
  pass_rate: number;
}

export interface ProjectAutomationStats {
  project_name: string;
  test_cases: number;
  execution_time_hours: number;
  pass_rate: number;
  failed_count: number;
}

export interface DailyStats {
  date: string;
  test_cases: number;
  execution_time_hours: number;
  pass_rate: number;
  failed_count: number;
}

export interface AutomationMetrics {
  overview: AutomationStats;
  by_project: ProjectAutomationStats[];
  by_period: DailyStats[];
}

export interface AutomationProject {
  id: string;
  name: string;
  description?: string;
  total_test_cases: number;
  execution_time_hours: number;
  created_at: string;
  updated_at: string;
}

export interface ExecutionCreate {
  project_id?: string;
  execution_date: string;
  test_cases: number;
  execution_time_hours: number;
  passed_count: number;
  failed_count: number;
}

export const automationAPI = {
  getMetrics: async (period: string = 'month', project?: string): Promise<AutomationMetrics> => {
    const params = new URLSearchParams({ period });
    if (project) params.append('project', project);
    
    const response = await automationApi.get(`/metrics?${params}`);
    return response.data;
  },

  getOverview: async (): Promise<AutomationStats> => {
    const response = await automationApi.get('/overview');
    return response.data;
  },

  listProjects: async (): Promise<AutomationProject[]> => {
    const response = await automationApi.get('/projects');
    return response.data;
  },

  createProject: async (data: { name: string; description?: string }): Promise<AutomationProject> => {
    const response = await automationApi.post('/projects', data);
    return response.data;
  },

  addExecution: async (data: ExecutionCreate): Promise<any> => {
    const response = await automationApi.post('/executions', data);
    return response.data;
  },

  resetData: async (): Promise<{ message: string }> => {
    const response = await automationApi.post('/reset');
    return response.data;
  },

  initDemoData: async (): Promise<{ message: string; project_count: number; execution_count: number }> => {
    const response = await automationApi.post('/init-demo');
    return response.data;
  },
};

export default automationApi;
