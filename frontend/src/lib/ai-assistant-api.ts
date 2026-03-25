/**
 * AI辅助看板 API 客户端
 */

import axios from 'axios';
import { loadConfig } from './config';

const aiAssistantApi = axios.create({
  baseURL: 'http://localhost:8000/api/v1/ai-assistant',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

aiAssistantApi.interceptors.request.use(async (config) => {
  try {
    const appConfig = await loadConfig();
    config.baseURL = appConfig.apiUrl + '/ai-assistant';
  } catch (error) {
    console.warn('[AI Assistant API] Using default baseURL');
  }
  return config;
});

export interface AIActivity {
  name: string;
  count: number;
  percentage: number;
}

export interface AIOverview {
  total_assistances: number;
  total_manual_effort_saved_hours: number;
  total_activities: number;
  top_activity: string;
}

export interface DailyAIStats {
  date: string;
  total_count: number;
  by_activity: Record<string, number>;
}

export interface AIAssistantMetrics {
  overview: AIOverview;
  by_activity: AIActivity[];
  by_period: DailyAIStats[];
}

export interface AssistanceRecordCreate {
  activity_type: string;
  project_name?: string;
  description?: string;
  time_saved_hours?: number;
  record_date?: string;
}

export const aiAssistantAPI = {
  getMetrics: async (period: string = 'month'): Promise<AIAssistantMetrics> => {
    const response = await aiAssistantApi.get(`/metrics?period=${period}`);
    return response.data;
  },

  getOverview: async (): Promise<AIOverview> => {
    const response = await aiAssistantApi.get('/overview');
    return response.data;
  },

  listActivityTypes: async (): Promise<string[]> => {
    const response = await aiAssistantApi.get('/activity-types');
    return response.data;
  },

  addActivityType: async (name: string): Promise<{ message: string; name: string }> => {
    const response = await aiAssistantApi.post('/activity-types', { name });
    return response.data;
  },

  listRecords: async (activityType?: string, limit: number = 100): Promise<any[]> => {
    const params = new URLSearchParams();
    if (activityType) params.append('activity_type', activityType);
    params.append('limit', String(limit));
    const response = await aiAssistantApi.get(`/records?${params}`);
    return response.data;
  },

  addRecord: async (data: AssistanceRecordCreate): Promise<any> => {
    const response = await aiAssistantApi.post('/records', data);
    return response.data;
  },

  addRecordsBatch: async (records: AssistanceRecordCreate[]): Promise<{ message: string; added_count: number }> => {
    const response = await aiAssistantApi.post('/records/batch', records);
    return response.data;
  },

  resetData: async (): Promise<{ message: string }> => {
    const response = await aiAssistantApi.post('/reset');
    return response.data;
  },

  initDemoData: async (): Promise<{ message: string; record_count: number }> => {
    const response = await aiAssistantApi.post('/init-demo');
    return response.data;
  },
};

export default aiAssistantApi;
