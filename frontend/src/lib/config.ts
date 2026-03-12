/**
 * 动态配置加载器
 * 从 /config.json 加载运行时配置，支持不同网络环境
 */

interface AppConfig {
  apiUrl: string;
  dvpApiUrl: string;
  version: string;
  lastUpdate: string;
  features?: {
    testBenchDashboard: boolean;
    dvpDashboard: boolean;
    automationDashboard: boolean;
    aiAssistantDashboard: boolean;
  };
}

// 默认配置（作为后备）
const DEFAULT_CONFIG: AppConfig = {
  apiUrl: 'http://localhost:8000/api/v1',
  dvpApiUrl: 'http://localhost:8001',
  version: '2.0.0',
  lastUpdate: new Date().toISOString().split('T')[0],
  features: {
    testBenchDashboard: true,
    dvpDashboard: true,
    automationDashboard: false,
    aiAssistantDashboard: false,
  },
};

let cachedConfig: AppConfig | null = null;

/**
 * 加载配置文件
 * 优先从 /config.json 加载，失败则使用默认配置
 */
export async function loadConfig(): Promise<AppConfig> {
  // 如果已缓存，直接返回
  if (cachedConfig) {
    return cachedConfig;
  }

  try {
    // 尝试从 public/config.json 加载
    const response = await fetch('/config.json');
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.status}`);
    }
    
    const config = await response.json();
    cachedConfig = {
      ...DEFAULT_CONFIG,
      ...config,
    };
    
    console.log('[CONFIG] Loaded from /config.json:', cachedConfig);
    return cachedConfig!;
  } catch (error) {
    console.warn('[CONFIG] Failed to load config, using defaults:', error);
    cachedConfig = DEFAULT_CONFIG;
    return DEFAULT_CONFIG;
  }
}

/**
 * 获取 API 基础 URL
 */
export async function getApiUrl(): Promise<string> {
  const config = await loadConfig();
  return config.apiUrl;
}

/**
 * 获取 DVP API 基础 URL
 */
export async function getDvpApiUrl(): Promise<string> {
  const config = await loadConfig();
  return config.dvpApiUrl || 'http://localhost:8001';
}

/**
 * 获取当前配置（同步，可能为 null）
 */
export function getConfig(): AppConfig | null {
  return cachedConfig;
}

/**
 * 清除配置缓存（用于重新加载配置）
 */
export function clearConfigCache(): void {
  cachedConfig = null;
}
