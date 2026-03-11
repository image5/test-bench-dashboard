"""
Laboratory Model
Laboratory Data Model
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime
import uuid

from app.core.database import BaseModel


class Laboratory(BaseModel):
    """Laboratory Table"""
    __tablename__ = "laboratories"
    
    # Basic Info
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # Background Image
    background_image = Column(String(500), nullable=True)
    
    # Canvas Size
    width = Column(Integer, default=1920)
    height = Column(Integer, default=1080)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Laboratory {self.name}>"
    
    def to_dict(self):
        """Convert to dict"""
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
