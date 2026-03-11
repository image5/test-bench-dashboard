"""
Alarm Model
告警数据模型
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import BaseModel


class AlarmType(str, enum.Enum):
    """告警类型枚举"""
    OVER_TEMPERATURE = "over_temperature"       # 超温
    OVER_RPM = "over_rpm"                       # 超转速
    OVER_VOLTAGE = "over_voltage"               # 超压
    OVER_CURRENT = "over_current"               # 过流
    COMMUNICATION_ERROR = "communication_error" # 通信异常
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"     # 心跳超时
    CUSTOM = "custom"                           # 自定义


class AlarmSeverity(str, enum.Enum):
    """告警严重程度"""
    LOW = "low"           # 低
    MEDIUM = "medium"     # 中
    HIGH = "high"         # 高
    CRITICAL = "critical" # 严重


# 告警类型配置
ALARM_TYPE_CONFIG = {
    AlarmType.OVER_TEMPERATURE: {"label": "超温告警", "icon": "🌡️"},
    AlarmType.OVER_RPM: {"label": "超转速告警", "icon": "🔄"},
    AlarmType.OVER_VOLTAGE: {"label": "超压告警", "icon": "⚡"},
    AlarmType.OVER_CURRENT: {"label": "过流告警", "icon": "🔌"},
    AlarmType.COMMUNICATION_ERROR: {"label": "通信异常", "icon": "📡"},
    AlarmType.HEARTBEAT_TIMEOUT: {"label": "心跳超时", "icon": "💔"},
    AlarmType.CUSTOM: {"label": "自定义告警", "icon": "⚠️"},
}

# 严重程度颜色
SEVERITY_COLORS = {
    AlarmSeverity.LOW: "#fbbf24",
    AlarmSeverity.MEDIUM: "#f97316",
    AlarmSeverity.HIGH: "#ef4444",
    AlarmSeverity.CRITICAL: "#dc2626",
}


class Alarm(BaseModel):
    """告警记录表"""
    __tablename__ = "alarms"
    
    # 基本信息
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bench_id = Column(String(36), ForeignKey("test_benches.id"), nullable=False)
    
    # 告警信息
    type = Column(SQLEnum(AlarmType), nullable=False)
    severity = Column(SQLEnum(AlarmSeverity), nullable=False, default=AlarmSeverity.MEDIUM)
    message = Column(Text, nullable=False)
    
    # 触发值
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    
    # 确认信息
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    bench = relationship("TestBench", back_populates="alarms")
    
    def __repr__(self):
        return f"<Alarm {self.type} - {self.bench_id}>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "benchId": self.bench_id,
            "type": self.type.value if self.type else None,
            "typeInfo": ALARM_TYPE_CONFIG.get(self.type, {}) if self.type else {},
            "severity": self.severity.value if self.severity else None,
            "severityColor": SEVERITY_COLORS.get(self.severity, "#f97316"),
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "acknowledged": self.acknowledged,
            "acknowledgedBy": self.acknowledged_by,
            "acknowledgedAt": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }
