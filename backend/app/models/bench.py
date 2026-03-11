"""
Test Bench Model
测试台架数据模型
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Enum as SQLEnum, Text, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import BaseModel


class BenchType(str, enum.Enum):
    """台架类型枚举"""
    HIL = "hil"                     # HIL测试台架
    SYSTEM = "system"               # 系统测试台架
    ASSEMBLY = "assembly"           # 总成测试台架
    HARDWARE = "hardware"           # 硬件测试台架
    SOFTWARE = "software"           # 软件长稳测试台架
    OTHER = "other"                 # 其他测试台架


class BenchStatus(str, enum.Enum):
    """台架状态枚举"""
    RUNNING = "running"             # 运行中
    OFFLINE = "offline"             # 离线
    MAINTENANCE = "maintenance"     # 维护中
    ALARM = "alarm"                 # 告警
    IDLE = "idle"                   # 空闲


# 台架类型配置
BENCH_TYPE_CONFIG = {
    BenchType.HIL: {"label": "HIL测试台架", "icon": "🖥️", "color": "#3b82f6"},
    BenchType.SYSTEM: {"label": "系统测试台架", "icon": "🔧", "color": "#8b5cf6"},
    BenchType.ASSEMBLY: {"label": "总成测试台架", "icon": "⚙️", "color": "#06b6d4"},
    BenchType.HARDWARE: {"label": "硬件测试台架", "icon": "🔌", "color": "#f59e0b"},
    BenchType.SOFTWARE: {"label": "软件长稳测试台架", "icon": "💻", "color": "#10b981"},
    BenchType.OTHER: {"label": "其他测试台架", "icon": "📦", "color": "#6b7280"},
}

# 状态颜色配置
STATUS_COLORS = {
    BenchStatus.RUNNING: "#22c55e",     # 绿色
    BenchStatus.OFFLINE: "#6b7280",     # 灰色
    BenchStatus.MAINTENANCE: "#f59e0b", # 黄色
    BenchStatus.ALARM: "#ef4444",       # 红色
    BenchStatus.IDLE: "#3b82f6",        # 蓝色
}

# 状态标签配置
STATUS_LABELS = {
    BenchStatus.RUNNING: "运行中",
    BenchStatus.OFFLINE: "离线",
    BenchStatus.MAINTENANCE: "维护中",
    BenchStatus.ALARM: "告警",
    BenchStatus.IDLE: "空闲",
}


class TestBench(BaseModel):
    """测试台架表"""
    __tablename__ = "test_benches"
    
    # 基本信息
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    laboratory_id = Column(String(36), ForeignKey("laboratories.id"), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(BenchType), nullable=False, default=BenchType.OTHER)
    
    # 网络配置
    ip_address = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False, default=8080)
    
    # 位置信息
    position_x = Column(Float, nullable=False, default=0)
    position_y = Column(Float, nullable=False, default=0)
    rotation = Column(Integer, default=0)
    
    # 状态信息
    status = Column(SQLEnum(BenchStatus), nullable=False, default=BenchStatus.OFFLINE)
    last_heartbeat = Column(DateTime, nullable=True)
    current_task = Column(String(200), nullable=True)
    task_start_time = Column(DateTime, nullable=True)
    
    # 维护信息
    is_under_maintenance = Column(Boolean, default=False)
    maintenance_reason = Column(String(200), nullable=True)
    maintenance_start_time = Column(DateTime, nullable=True)
    maintenance_operator = Column(String(100), nullable=True)
    
    # 告警信息
    has_alarm = Column(Boolean, default=False)
    alarm_message = Column(Text, nullable=True)
    
    # 额外数据（传感器读数等）
    metrics = Column(JSON, default=dict)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    alarms = relationship("Alarm", back_populates="bench", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="bench", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TestBench {self.name}>"
    
    def to_dict(self):
        """转换为字典（适配前端格式）"""
        return {
            "id": self.id,
            "laboratoryId": self.laboratory_id,
            "name": self.name,
            "type": self.type.value if self.type else None,
            "typeInfo": BENCH_TYPE_CONFIG.get(self.type, {}) if self.type else {},
            "network": {
                "ip": self.ip_address,
                "port": self.port
            },
            "position": {
                "x": self.position_x,
                "y": self.position_y,
                "rotation": self.rotation
            },
            "status": {
                "state": self.status.value if self.status else None,
                "color": STATUS_COLORS.get(self.status, "#6b7280"),
                "label": STATUS_LABELS.get(self.status, "未知"),
                "lastHeartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
                "currentTask": self.current_task,
                "taskStartTime": self.task_start_time.isoformat() if self.task_start_time else None
            },
            "maintenance": {
                "isUnderMaintenance": self.is_under_maintenance,
                "reason": self.maintenance_reason,
                "startTime": self.maintenance_start_time.isoformat() if self.maintenance_start_time else None,
                "operator": self.maintenance_operator
            },
            "alarm": {
                "hasAlarm": self.has_alarm,
                "message": self.alarm_message
            },
            "metrics": self.metrics or {},
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
