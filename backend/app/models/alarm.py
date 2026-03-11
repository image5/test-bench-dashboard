"""
Alarm Model
Alarm Data Model
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import BaseModel


class AlarmType(str, enum.Enum):
    """Alarm Type Enum"""
    OVER_TEMPERATURE = "over_temperature"       # Over Temperature
    OVER_RPM = "over_rpm"                       # Over RPM
    OVER_VOLTAGE = "over_voltage"               # Over Voltage
    OVER_CURRENT = "over_current"               # Over Current
    COMMUNICATION_ERROR = "communication_error" # Communication Error
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"     # Heartbeat Timeout
    CUSTOM = "custom"                           # Custom


class AlarmSeverity(str, enum.Enum):
    """Alarm Severity Enum"""
    LOW = "low"           # Low
    MEDIUM = "medium"     # Medium
    HIGH = "high"         # High
    CRITICAL = "critical" # Critical


# Alarm Type Configuration
ALARM_TYPE_CONFIG = {
    AlarmType.OVER_TEMPERATURE: {"label": "Over Temperature", "icon": "🌡️"},
    AlarmType.OVER_RPM: {"label": "Over RPM", "icon": "🔄"},
    AlarmType.OVER_VOLTAGE: {"label": "Over Voltage", "icon": "⚡"},
    AlarmType.OVER_CURRENT: {"label": "Over Current", "icon": "🔌"},
    AlarmType.COMMUNICATION_ERROR: {"label": "Communication Error", "icon": "📡"},
    AlarmType.HEARTBEAT_TIMEOUT: {"label": "Heartbeat Timeout", "icon": "💔"},
    AlarmType.CUSTOM: {"label": "Custom Alarm", "icon": "⚠️"},
}

# Severity Colors
SEVERITY_COLORS = {
    AlarmSeverity.LOW: "#fbbf24",
    AlarmSeverity.MEDIUM: "#f97316",
    AlarmSeverity.HIGH: "#ef4444",
    AlarmSeverity.CRITICAL: "#dc2626",
}


class Alarm(BaseModel):
    """Alarm Record Table"""
    __tablename__ = "alarms"
    
    # Basic Info
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bench_id = Column(String(36), ForeignKey("test_benches.id"), nullable=False)
    
    # Alarm Info
    type = Column(SQLEnum(AlarmType), nullable=False)
    severity = Column(SQLEnum(AlarmSeverity), nullable=False, default=AlarmSeverity.MEDIUM)
    message = Column(Text, nullable=False)
    
    # Trigger Value
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    
    # Acknowledge Info
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    bench = relationship("TestBench", back_populates="alarms")
    
    def __repr__(self):
        return f"<Alarm {self.type} - {self.bench_id}>"
    
    def to_dict(self):
        """Convert to dict"""
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
