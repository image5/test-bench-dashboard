"""
Core Module
核心模块
"""

from app.core.database import get_db, init_db, BaseModel

__all__ = ["get_db", "init_db", "BaseModel"]
