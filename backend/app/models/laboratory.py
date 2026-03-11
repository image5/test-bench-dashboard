"""
Laboratory Model
实验室数据模型
"""

from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
import uuid

from app.core.database import BaseModel


class Laboratory(BaseModel):
    """实验室表"""
    __tablename__ = "laboratories"
    
    # 基本信息
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # 背景图
    background_image = Column(String(500), nullable=True)
    
    # 画布尺寸
    width = Column(Integer, default=1920)
    height = Column(Integer, default=1080)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Laboratory {self.name}>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "backgroundImage": self.background_image,
            "canvasSize": {
                "width": self.width,
                "height": self.height
            },
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
