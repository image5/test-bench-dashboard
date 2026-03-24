import axios from 'axios';
import { TestBench, Laboratory, Alarm, StatisticsOverview, BenchType, BenchStatus } from '@/types';
import { loadConfig } from './config';

// 默认 API 地址（作为后备）
const DEFAULT_API_BASE = 'http://localhost:8000/api/v1';

// 创建 axios 实例
const api = axios.create({
  baseURL: DEFAULT_API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 动态设置 baseURL 的拦截器
api.interceptors.request.use(async (config) => {
  try {
    const appConfig = await loadConfig();
    config.baseURL = appConfig.apiUrl;
  } catch (error) {
    console.warn('[API] Failed to load config, using default baseURL');
    config.baseURL = DEFAULT_API_BASE;
  }
  return config;
});

// ============ 台架 API ============

export const benchesApi = {
  // 获取台架列表
  list: async (params?: { laboratoryId?: string; status?: string; type?: string }): Promise<TestBench[]> => {
    const response = await api.get('/benches', { params });
    return response.data;
  },

  // 获取台架详情
  get: async (id: string): Promise<TestBench> => {
    const response = await api.get(`/benches/${id}`);
    return response.data;
  },

  // 创建台架
  create: async (data: {
    name: string;
    type: BenchType;
    ipAddress: string;
    port: number;
    laboratoryId?: string;
    positionX?: number;
    positionY?: number;
  }): Promise<TestBench> => {
    const response = await api.post('/benches', {
      name: data.name,
      type: data.type,
      ip_address: data.ipAddress,
      port: data.port,
      laboratory_id: data.laboratoryId,
      position_x: data.positionX || 0,
      position_y: data.positionY || 0,
    });
    return response.data;
  },

  // 更新台架
  update: async (id: string, data: Partial<{
    name: string;
    type: BenchType;
    ipAddress: string;
    port: number;
    laboratoryId: string;
  }>): Promise<TestBench> => {
    const response = await api.put(`/benches/${id}`, {
      name: data.name,
      type: data.type,
      ip_address: data.ipAddress,
      port: data.port,
      laboratory_id: data.laboratoryId,
    });
    return response.data;
  },

  // 删除台架
  delete: async (id: string): Promise<void> => {
    await api.delete(`/benches/${id}`);
  },

  // 更新位置
  updatePosition: async (id: string, x: number, y: number, rotation?: number): Promise<TestBench> => {
    const response = await api.put(`/benches/${id}/position`, {
      position_x: x,
      position_y: y,
      rotation,
    });
    return response.data;
  },

  // 设置维护状态
  setMaintenance: async (id: string, data: {
    isUnderMaintenance: boolean;
    reason?: string;
    operator?: string;
  }): Promise<TestBench> => {
    const response = await api.put(`/benches/${id}/maintenance`, {
      is_under_maintenance: data.isUnderMaintenance,
      reason: data.reason,
      operator: data.operator,
    });
    return response.data;
  },

  // 心跳
  heartbeat: async (id: string, data: {
    status?: BenchStatus;
    currentTask?: string;
    metrics?: Record<string, any>;
  }): Promise<void> => {
    await api.post(`/benches/${id}/heartbeat`, data);
  },

  // 清除告警
  clearAlarm: async (id: string): Promise<TestBench> => {
    const response = await api.post(`/benches/${id}/clear-alarm`);
    return response.data;
  },

  // 批量导入
  import: async (data: {
    laboratoryId?: string;
    benches: Array<{
      name: string;
      type: string;
      ip_address: string;
      port: number;
      position_x: number;
      position_y: number;
    }>;
  }): Promise<{
    successCount: number;
    failedCount: number;
    errors: Array<{ row: number; name: string; error: string }>;
    createdBenches: TestBench[];
  }> => {
    const response = await api.post('/benches/import', {
      laboratory_id: data.laboratoryId,
      benches: data.benches,
    });
    return response.data;
  },
};

// ============ 实验室 API ============

export const laboratoriesApi = {
  list: async (): Promise<Laboratory[]> => {
    const response = await api.get('/laboratories');
    return response.data;
  },

  get: async (id: string): Promise<Laboratory> => {
    const response = await api.get(`/laboratories/${id}`);
    return response.data;
  },

  create: async (data: {
    name: string;
    description?: string;
    backgroundImage?: string;
    width?: number;
    height?: number;
  }): Promise<Laboratory> => {
    const response = await api.post('/laboratories', {
      name: data.name,
      description: data.description,
      background_image: data.backgroundImage,
      width: data.width,
      height: data.height,
    });
    return response.data;
  },

  update: async (id: string, data: Partial<{
    name: string;
    description: string;
    backgroundImage: string;
    width: number;
    height: number;
  }>): Promise<Laboratory> => {
    const response = await api.put(`/laboratories/${id}`, {
      name: data.name,
      description: data.description,
      background_image: data.backgroundImage,
      width: data.width,
      height: data.height,
    });
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/laboratories/${id}`);
  },
};

// ============ 告警 API ============

export const alarmsApi = {
  list: async (params?: { benchId?: string; acknowledged?: boolean }): Promise<Alarm[]> => {
    const response = await api.get('/alarms', { params });
    return response.data;
  },

  getActive: async (): Promise<Alarm[]> => {
    const response = await api.get('/alarms/active');
    return response.data;
  },

  create: async (data: {
    benchId: string;
    type: string;
    severity: string;
    message: string;
    value?: number;
    threshold?: number;
  }): Promise<Alarm> => {
    const response = await api.post('/alarms', {
      bench_id: data.benchId,
      type: data.type,
      severity: data.severity,
      message: data.message,
      value: data.value,
      threshold: data.threshold,
    });
    return response.data;
  },

  acknowledge: async (id: string, acknowledgedBy: string): Promise<Alarm> => {
    const response = await api.put(`/alarms/${id}/acknowledge`, {
      acknowledged_by: acknowledgedBy,
    });
    return response.data;
  },
};

// ============ 统计 API ============

export const statisticsApi = {
  getOverview: async (): Promise<StatisticsOverview> => {
    const response = await api.get('/statistics/overview');
    return response.data;
  },

  getByLaboratory: async (labId: string): Promise<any> => {
    const response = await api.get(`/statistics/laboratory/${labId}`);
    return response.data;
  },

  getByType: async (): Promise<Record<string, any>> => {
    const response = await api.get('/statistics/by-type');
    return response.data;
  },
};

export default api;
