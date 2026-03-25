"""
Automation Test Data Models
自动化测试数据模型
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from datetime import datetime
import uuid

from app.core.database import BaseModel


class AutomationProject(BaseModel):
    """自动化测试项目"""

    __tablename__ = "automation_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    total_test_cases = Column(Integer, default=0)
    total_execution_time_hours = Column(Float, default=0.0)
    total_passed = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        pass_rate = 0.0
        if self.total_test_cases > 0:
            pass_rate = round(self.total_passed / self.total_test_cases * 100, 1)

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "total_test_cases": self.total_test_cases,
            "execution_time_hours": round(self.total_execution_time_hours, 2),
            "pass_rate": pass_rate,
            "failed_count": self.total_failed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AutomationExecution(BaseModel):
    """自动化执行记录"""

    __tablename__ = "automation_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("automation_projects.id"), nullable=True)
    execution_date = Column(DateTime, nullable=False, index=True)
    test_cases = Column(Integer, default=0)
    execution_time_hours = Column(Float, default=0.0)
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        pass_rate = 0.0
        if self.test_cases > 0:
            pass_rate = round(self.passed_count / self.test_cases * 100, 1)

        return {
            "id": self.id,
            "project_id": self.project_id,
            "date": self.execution_date.strftime("%Y-%m-%d")
            if self.execution_date
            else None,
            "test_cases": self.test_cases,
            "execution_time_hours": round(self.execution_time_hours, 2),
            "pass_rate": pass_rate,
            "failed_count": self.failed_count,
        }
