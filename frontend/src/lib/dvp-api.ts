/**
 * DVP API 客户端
 * 用于与 DVP 后端通信
 */

import axios from 'axios';
import { loadConfig } from './config';

const dvpApi = axios.create({
  baseURL: 'http://localhost:8000/api/v1/dvp',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

dvpApi.interceptors.request.use(async (config) => {
  try {
    const appConfig = await loadConfig();
    config.baseURL = appConfig.apiUrl + '/dvp';
  } catch (error) {
    console.warn('[DVP API] Using default baseURL');
  }
  return config;
});

dvpApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[DVP API] Error:', error);
    throw error;
  }
);

export interface Project {
  project_id: string;
  name: string;
  description?: string;
  total_experiments: number;
  total_devices: number;
  progress: number;
  param_checked: boolean;
  is_interrupted: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  total_experiments?: number;
  total_devices?: number;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  total_experiments?: number;
  total_devices?: number;
  completed_devices?: number;
  progress?: number;
  param_checked?: boolean;
  is_interrupted?: boolean;
}

export interface ProgressUpdate {
  progress: number;
  completed_devices?: number;
  param_checked?: boolean;
  is_interrupted?: boolean;
}

export interface ProjectStatistics {
  total_projects: number;
  running_projects: number;
  completed_projects: number;
  interrupted_projects: number;
  average_progress: number;
}

export const projectAPI = {
  getAll: async (skip = 0, limit = 100, status?: string): Promise<Project[]> => {
    const params = new URLSearchParams();
    params.append('skip', String(skip));
    params.append('limit', String(limit));
    if (status) params.append('status', status);
    const response = await dvpApi.get(`/projects?${params}`);
    return response.data;
  },

  getById: async (projectId: string): Promise<Project> => {
    const response = await dvpApi.get(`/projects/${projectId}`);
    return response.data;
  },

  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await dvpApi.post('/projects', data);
    return response.data;
  },

  update: async (projectId: string, data: ProjectUpdate): Promise<Project> => {
    const response = await dvpApi.put(`/projects/${projectId}`, data);
    return response.data;
  },

  updateProgress: async (projectId: string, data: ProgressUpdate): Promise<Project> => {
    const response = await dvpApi.put(`/projects/${projectId}/progress`, data);
    return response.data;
  },

  interrupt: async (projectId: string): Promise<Project> => {
    const response = await dvpApi.post(`/projects/${projectId}/interrupt`);
    return response.data;
  },

  resume: async (projectId: string): Promise<Project> => {
    const response = await dvpApi.post(`/projects/${projectId}/resume`);
    return response.data;
  },

  checkParams: async (projectId: string): Promise<Project> => {
    const response = await dvpApi.post(`/projects/${projectId}/check-params`);
    return response.data;
  },

  delete: async (projectId: string): Promise<{ message: string; project_id: string }> => {
    const response = await dvpApi.delete(`/projects/${projectId}`);
    return response.data;
  },

  getStatistics: async (): Promise<ProjectStatistics> => {
    const response = await dvpApi.get('/statistics');
    return response.data;
  },

  resetData: async (): Promise<{ message: string }> => {
    const response = await dvpApi.post('/reset');
    return response.data;
  },

  initDemoData: async (): Promise<{ message: string; project_count: number }> => {
    const response = await dvpApi.post('/init-demo');
    return response.data;
  },
};

export interface Experiment {
  project_id: string;
  experiment_id: string;
  name: string;
  total_devices: number;
  completed_devices: number;
  progress: number;
  param_checked: boolean;
  is_interrupted: boolean;
}

export const experimentAPI = {
  getByProject: async (projectId: string): Promise<Experiment[]> => {
    const response = await dvpApi.get(`/projects/${projectId}/experiments`);
    return response.data;
  },
};

export interface Device {
  project_id: string;
  experiment_id: string;
  device_id: string;
  name: string;
  status: 'running' | 'idle' | 'error' | 'completed';
  progress: number;
}

export const deviceAPI = {
  getByExperiment: async (projectId: string, experimentId: string): Promise<Device[]> => {
    const response = await dvpApi.get(`/projects/${projectId}/experiments/${experimentId}/devices`);
    return response.data;
  },
};

export default dvpApi;
