"""
AI Assistant Data Models
AI辅助数据模型
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from datetime import datetime
import uuid

from app.core.database import BaseModel


class AIActivityType(BaseModel):
    """AI活动类型"""

    __tablename__ = "ai_activity_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sort_order": self.sort_order,
        }


class AIAssistanceRecord(BaseModel):
    """AI辅助记录"""

    __tablename__ = "ai_assistance_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_type_id = Column(
        String(36), ForeignKey("ai_activity_types.id"), nullable=False
    )
    project_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    time_saved_hours = Column(Float, default=0.0)
    execution_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "activity_type_id": self.activity_type_id,
            "project_name": self.project_name,
            "description": self.description,
            "time_saved_hours": self.time_saved_hours,
            "date": self.execution_date.strftime("%Y-%m-%d")
            if self.execution_date
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DVPProject(BaseModel):
    """DVP项目"""

    __tablename__ = "dvp_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    total_experiments = Column(Integer, default=0)
    total_devices = Column(Integer, default=0)
    completed_devices = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    param_checked = Column(Integer, default=0)
    is_interrupted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "project_id": self.id,
            "name": self.name,
            "description": self.description,
            "total_experiments": self.total_experiments,
            "total_devices": self.total_devices,
            "progress": round(self.progress, 1),
            "param_checked": bool(self.param_checked),
            "is_interrupted": bool(self.is_interrupted),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
