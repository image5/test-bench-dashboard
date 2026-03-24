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

const DEFAULT_CONFIG: AppConfig = {
  apiUrl: 'http://localhost:8000/api/v1',
  dvpApiUrl: 'http://localhost:8001',
  version: '2.0.0',
  lastUpdate: new Date().toISOString().split('T')[0],
  features: {
    testBenchDashboard: true,
    dvpDashboard: true,
    automationDashboard: true,
    aiAssistantDashboard: true,
  },
};

let cachedConfig: AppConfig | null = null;
let configLoaded = false;

export async function loadConfig(): Promise<AppConfig> {
  if (cachedConfig) {
    return cachedConfig;
  }

  if (configLoaded) {
    return cachedConfig || DEFAULT_CONFIG;
  }

  try {
    const response = await fetch('/config.json');
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.status}`);
    }

    const config = await response.json();
    cachedConfig = {
      ...DEFAULT_CONFIG,
      ...config,
    };

    if (process.env.NODE_ENV === 'development') {
      console.log('[CONFIG] Loaded:', cachedConfig.apiUrl);
    }
  } catch (error) {
    console.warn('[CONFIG] Using defaults');
    cachedConfig = DEFAULT_CONFIG;
  }

  configLoaded = true;
  return cachedConfig!;
}

export async function getApiUrl(): Promise<string> {
  const config = await loadConfig();
  return config.apiUrl;
}

export async function getDvpApiUrl(): Promise<string> {
  const config = await loadConfig();
  return config.dvpApiUrl || 'http://localhost:8001';
}

export function getConfig(): AppConfig | null {
  return cachedConfig;
}

export function clearConfigCache(): void {
  cachedConfig = null;
  configLoaded = false;
}
