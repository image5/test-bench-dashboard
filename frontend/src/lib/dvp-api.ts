/**
 * DVP API 客户端
 * 用于与 DVP 后端通信
 */

import axios from 'axios';
import { getDvpApiUrl } from './config';

// DVP API 基础配置
const DVP_API_BASE = 'http://localhost:8001'; // DVP 后端默认端口

const dvpApi = axios.create({
  baseURL: DVP_API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 动态设置 baseURL
dvpApi.interceptors.request.use(async (config) => {
  try {
    const dvpUrl = await getDvpApiUrl();
    config.baseURL = dvpUrl;
    console.log('[DVP API] Using URL:', dvpUrl);
  } catch (error) {
    console.warn('[DVP API] Using default baseURL');
  }
  return config;
});

// 响应拦截器 - 统一错误处理
dvpApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
      console.error('[DVP API] Connection failed - DVP backend may not be running');
      throw new Error('DVP后端服务未启动，请先启动DVP后端服务（端口8001）');
    }
    throw error;
  }
);

// ============ 项目 API ============

export interface Project {
  project_id: string;
  name: string;
  total_experiments: number;
  total_devices: number;
  progress: number;
  param_checked: boolean;
  is_interrupted: boolean;
  created_at: string;
  updated_at: string;
}

export const projectAPI = {
  getAll: async (skip = 0, limit = 100): Promise<{ data: Project[]; total: number }> => {
    const response = await dvpApi.get(`/api/projects?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getById: async (projectId: string): Promise<Project> => {
    const response = await dvpApi.get(`/api/projects/${projectId}`);
    return response.data;
  },

  getStatistics: async (projectId: string): Promise<any> => {
    const response = await dvpApi.get(`/api/projects/${projectId}/statistics`);
    return response.data;
  },
};

// ============ 实验组 API ============

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
    const response = await dvpApi.get(`/api/projects/${projectId}/experiments`);
    return response.data;
  },

  getById: async (projectId: string, experimentId: string): Promise<Experiment> => {
    const response = await dvpApi.get(`/api/projects/${projectId}/experiments/${experimentId}`);
    return response.data;
  },
};

// ============ 设备 API ============

export interface Device {
  project_id: string;
  experiment_id: string;
  device_id: string;
  name: string;
  status: 'running' | 'idle' | 'error' | 'completed';
  progress: number;
  oscilloscope?: {
    waveform: number[];
    sample_rate: number;
    timestamp: string;
  };
  metrics?: {
    power?: number;
    current?: number;
    temperature?: number;
    pressure?: number;
  };
  alerts?: Array<{
    level: string;
    message: string;
    timestamp: string;
  }>;
}

export const deviceAPI = {
  getByExperiment: async (projectId: string, experimentId: string): Promise<Device[]> => {
    const response = await dvpApi.get(`/api/projects/${projectId}/experiments/${experimentId}/devices`);
    return response.data;
  },

  getById: async (projectId: string, experimentId: string, deviceId: string): Promise<Device> => {
    const response = await dvpApi.get(`/api/projects/${projectId}/experiments/${experimentId}/devices/${deviceId}`);
    return response.data;
  },
};

export default dvpApi;
