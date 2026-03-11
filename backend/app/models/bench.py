"""
Test Bench Model
Test Bench Data Model
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Enum as SQLEnum, Text, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import BaseModel


class BenchType(str, enum.Enum):
    """Bench Type Enum"""
    HIL = "hil"                     # HIL Test Bench
    SYSTEM = "system"               # System Test Bench
    ASSEMBLY = "assembly"           # Assembly Test Bench
    HARDWARE = "hardware"           # Hardware Test Bench
    SOFTWARE = "software"           # Software Long-term Test Bench
    OTHER = "other"                 # Other Test Bench


class BenchStatus(str, enum.Enum):
    """Bench Status Enum"""
    RUNNING = "running"             # Running
    OFFLINE = "offline"             # Offline
    MAINTENANCE = "maintenance"     # Under Maintenance
    ALARM = "alarm"                 # Alarm
    IDLE = "idle"                   # Idle


# Bench Type Configuration
BENCH_TYPE_CONFIG = {
    BenchType.HIL: {"label": "HIL Test Bench", "icon": "🖥️", "color": "#3b82f6"},
    BenchType.SYSTEM: {"label": "System Test Bench", "icon": "🔧", "color": "#8b5cf6"},
    BenchType.ASSEMBLY: {"label": "Assembly Test Bench", "icon": "⚙️", "color": "#06b6d4"},
    BenchType.HARDWARE: {"label": "Hardware Test Bench", "icon": "🔌", "color": "#f59e0b"},
    BenchType.SOFTWARE: {"label": "Software Test Bench", "icon": "💻", "color": "#10b981"},
    BenchType.OTHER: {"label": "Other Test Bench", "icon": "📦", "color": "#6b7280"},
}

# Status Color Configuration
STATUS_COLORS = {
    BenchStatus.RUNNING: "#22c55e",     # Green
    BenchStatus.OFFLINE: "#6b7280",     # Gray
    BenchStatus.MAINTENANCE: "#f59e0b", # Yellow
    BenchStatus.ALARM: "#ef4444",       # Red
    BenchStatus.IDLE: "#3b82f6",        # Blue
}

# Status Label Configuration
STATUS_LABELS = {
    BenchStatus.RUNNING: "Running",
    BenchStatus.OFFLINE: "Offline",
    BenchStatus.MAINTENANCE: "Maintenance",
    BenchStatus.ALARM: "Alarm",
    BenchStatus.IDLE: "Idle",
}


class TestBench(BaseModel):
    """Test Bench Table"""
    __tablename__ = "test_benches"
    
    # Basic Info
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    laboratory_id = Column(String(36), ForeignKey("laboratories.id"), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(BenchType), nullable=False, default=BenchType.OTHER)
    
    # Network Configuration
    ip_address = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False, default=8080)
    
    # Position Info
    position_x = Column(Float, nullable=False, default=0)
    position_y = Column(Float, nullable=False, default=0)
    rotation = Column(Integer, default=0)
    
    # Status Info
    status = Column(SQLEnum(BenchStatus), nullable=False, default=BenchStatus.OFFLINE)
    last_heartbeat = Column(DateTime, nullable=True)
    current_task = Column(String(200), nullable=True)
    task_start_time = Column(DateTime, nullable=True)
    
    # Maintenance Info
    is_under_maintenance = Column(Boolean, default=False)
    maintenance_reason = Column(String(200), nullable=True)
    maintenance_start_time = Column(DateTime, nullable=True)
    maintenance_operator = Column(String(100), nullable=True)
    
    # Alarm Info
    has_alarm = Column(Boolean, default=False)
    alarm_message = Column(Text, nullable=True)
    
    # Extra Data (sensor readings, etc.)
    metrics = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alarms = relationship("Alarm", back_populates="bench", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="bench", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TestBench {self.name}>"
    
    def to_dict(self):
        """Convert to dict (for frontend format)"""
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
                "label": STATUS_LABELS.get(self.status, "Unknown"),
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
