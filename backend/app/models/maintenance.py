"""
Maintenance Record Model
维护记录数据模型
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import BaseModel


class MaintenanceRecord(BaseModel):
    """维护记录表"""
    __tablename__ = "maintenance_records"
    
    # 基本信息
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bench_id = Column(String(36), ForeignKey("test_benches.id"), nullable=False)
    
    # 维护信息
    reason = Column(String(200), nullable=False)
    operator = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    
    # 时间信息
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    bench = relationship("TestBench", back_populates="maintenance_records")
    
    def __repr__(self):
        return f"<MaintenanceRecord {self.bench_id}>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "benchId": self.bench_id,
            "reason": self.reason,
            "operator": self.operator,
            "notes": self.notes,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "duration": self._calculate_duration(),
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }
    
    def _calculate_duration(self):
        """计算维护时长"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return None
