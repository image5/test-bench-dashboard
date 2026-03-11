"""
Pydantic Schemas
数据验证模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


# ============ 枚举 ============

class BenchType(str, Enum):
    HIL = "hil"
    SYSTEM = "system"
    ASSEMBLY = "assembly"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    OTHER = "other"


class BenchStatus(str, Enum):
    RUNNING = "running"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ALARM = "alarm"
    IDLE = "idle"


class AlarmType(str, Enum):
    OVER_TEMPERATURE = "over_temperature"
    OVER_RPM = "over_rpm"
    OVER_VOLTAGE = "over_voltage"
    OVER_CURRENT = "over_current"
    COMMUNICATION_ERROR = "communication_error"
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"
    CUSTOM = "custom"


class AlarmSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============ 实验室 ============

class LaboratoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    background_image: Optional[str] = None
    width: int = Field(default=1920, ge=800, le=4096)
    height: int = Field(default=1080, ge=600, le=2160)


class LaboratoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    background_image: Optional[str] = None
    width: Optional[int] = Field(None, ge=800, le=4096)
    height: Optional[int] = Field(None, ge=600, le=2160)


class LaboratoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    background_image: Optional[str]
    width: int
    height: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 台架 ============

class TestBenchCreate(BaseModel):
    laboratory_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    type: BenchType = Field(default=BenchType.OTHER)
    ip_address: str = Field(..., pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    port: int = Field(default=8080, ge=1, le=65535)
    position_x: float = Field(default=0)
    position_y: float = Field(default=0)
    rotation: int = Field(default=0, ge=0, le=360)


class TestBenchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[BenchType] = None
    ip_address: Optional[str] = Field(None, pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    port: Optional[int] = Field(None, ge=1, le=65535)
    laboratory_id: Optional[str] = None


class PositionUpdate(BaseModel):
    position_x: float
    position_y: float
    rotation: Optional[int] = Field(None, ge=0, le=360)


class MaintenanceSet(BaseModel):
    is_under_maintenance: bool
    reason: Optional[str] = None
    operator: Optional[str] = None


class HeartbeatData(BaseModel):
    status: Optional[BenchStatus] = None
    current_task: Optional[str] = None
    metrics: Optional[Dict] = None


class TestBenchResponse(BaseModel):
    id: str
    laboratory_id: Optional[str]
    name: str
    type: BenchType
    ip_address: str
    port: int
    position_x: float
    position_y: float
    rotation: int
    status: BenchStatus
    last_heartbeat: Optional[datetime]
    current_task: Optional[str]
    task_start_time: Optional[datetime]
    is_under_maintenance: bool
    maintenance_reason: Optional[str]
    maintenance_start_time: Optional[datetime]
    maintenance_operator: Optional[str]
    has_alarm: bool
    alarm_message: Optional[str]
    metrics: Optional[Dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 告警 ============

class AlarmCreate(BaseModel):
    bench_id: str
    type: AlarmType
    severity: AlarmSeverity = Field(default=AlarmSeverity.MEDIUM)
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None


class AlarmAcknowledge(BaseModel):
    acknowledged_by: str


class AlarmResponse(BaseModel):
    id: str
    bench_id: str
    type: AlarmType
    severity: AlarmSeverity
    message: str
    value: Optional[float]
    threshold: Optional[float]
    acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 统计 ============

class StatisticsOverview(BaseModel):
    total_benches: int
    running_count: int
    offline_count: int
    maintenance_count: int
    alarm_count: int
    idle_count: int
    online_rate: float
    current_time: datetime


class LaboratoryStatistics(BaseModel):
    laboratory_id: str
    laboratory_name: str
    total_benches: int
    running_count: int
    offline_count: int
    maintenance_count: int
    alarm_count: int
    idle_count: int
    online_rate: float
