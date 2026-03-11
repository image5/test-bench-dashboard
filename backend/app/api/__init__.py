"""
API Routes Module
API 路由模块
"""

from app.api.benches import router as benches_router
from app.api.laboratories import router as laboratories_router
from app.api.alarms import router as alarms_router
from app.api.statistics import router as statistics_router

__all__ = [
    "benches_router",
    "laboratories_router",
    "alarms_router",
    "statistics_router"
]
