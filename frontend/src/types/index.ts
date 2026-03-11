// 台架类型枚举
export enum BenchType {
  HIL = 'hil',
  SYSTEM = 'system',
  ASSEMBLY = 'assembly',
  HARDWARE = 'hardware',
  SOFTWARE = 'software',
  OTHER = 'other',
}

// 台架状态枚举
export enum BenchStatus {
  RUNNING = 'running',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
  ALARM = 'alarm',
  IDLE = 'idle',
}

// 告警类型枚举
export enum AlarmType {
  OVER_TEMPERATURE = 'over_temperature',
  OVER_RPM = 'over_rpm',
  OVER_VOLTAGE = 'over_voltage',
  OVER_CURRENT = 'over_current',
  COMMUNICATION_ERROR = 'communication_error',
  HEARTBEAT_TIMEOUT = 'heartbeat_timeout',
  CUSTOM = 'custom',
}

// 告警严重程度
export enum AlarmSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// 台架类型配置
export interface BenchTypeConfig {
  type: BenchType;
  label: string;
  icon: string;
  color: string;
}

// 台架状态信息
export interface BenchStatusInfo {
  state: BenchStatus;
  color: string;
  label: string;
  lastHeartbeat: string | null;
  currentTask: string | null;
  taskStartTime: string | null;
}

// 位置信息
export interface Position {
  x: number;
  y: number;
  rotation?: number;
}

// 网络配置
export interface NetworkConfig {
  ip: string;
  port: number;
}

// 维护信息
export interface MaintenanceInfo {
  isUnderMaintenance: boolean;
  reason: string | null;
  startTime: string | null;
  operator: string | null;
}

// 告警信息
export interface AlarmInfo {
  hasAlarm: boolean;
  message: string | null;
}

// 台架完整数据
export interface TestBench {
  id: string;
  laboratoryId: string | null;
  name: string;
  type: BenchType;
  typeInfo: BenchTypeConfig;
  network: NetworkConfig;
  position: Position;
  status: BenchStatusInfo;
  maintenance: MaintenanceInfo;
  alarm: AlarmInfo;
  metrics: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// 实验室
export interface Laboratory {
  id: string;
  name: string;
  description: string | null;
  backgroundImage: string | null;
  canvasSize: {
    width: number;
    height: number;
  };
  benchCount?: number;
  createdAt: string;
  updatedAt: string;
}

// 告警
export interface Alarm {
  id: string;
  benchId: string;
  type: AlarmType;
  typeInfo: {
    label: string;
    icon: string;
  };
  severity: AlarmSeverity;
  severityColor: string;
  message: string;
  value: number | null;
  threshold: number | null;
  acknowledged: boolean;
  acknowledgedBy: string | null;
  acknowledgedAt: string | null;
  createdAt: string;
}

// 统计概览
export interface StatisticsOverview {
  totalBenches: number;
  runningCount: number;
  offlineCount: number;
  maintenanceCount: number;
  alarmCount: number;
  idleCount: number;
  onlineRate: number;
  currentTime: string;
  statusBreakdown: Record<string, number>;
}

// 台架类型配置映射
export const BENCH_TYPE_CONFIGS: BenchTypeConfig[] = [
  { type: BenchType.HIL, label: 'HIL测试台架', icon: '🖥️', color: '#3b82f6' },
  { type: BenchType.SYSTEM, label: '系统测试台架', icon: '🔧', color: '#8b5cf6' },
  { type: BenchType.ASSEMBLY, label: '总成测试台架', icon: '⚙️', color: '#06b6d4' },
  { type: BenchType.HARDWARE, label: '硬件测试台架', icon: '🔌', color: '#f59e0b' },
  { type: BenchType.SOFTWARE, label: '软件长稳测试台架', icon: '💻', color: '#10b981' },
  { type: BenchType.OTHER, label: '其他测试台架', icon: '📦', color: '#6b7280' },
];

// 状态颜色映射
export const STATUS_COLORS: Record<BenchStatus, string> = {
  [BenchStatus.RUNNING]: '#22c55e',
  [BenchStatus.OFFLINE]: '#6b7280',
  [BenchStatus.MAINTENANCE]: '#f59e0b',
  [BenchStatus.ALARM]: '#ef4444',
  [BenchStatus.IDLE]: '#3b82f6',
};

// 状态标签映射
export const STATUS_LABELS: Record<BenchStatus, string> = {
  [BenchStatus.RUNNING]: '运行中',
  [BenchStatus.OFFLINE]: '离线',
  [BenchStatus.MAINTENANCE]: '维护中',
  [BenchStatus.ALARM]: '告警',
  [BenchStatus.IDLE]: '空闲',
};
