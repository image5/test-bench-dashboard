"""
API Routes Module
API 路由模块
"""

from app.api.benches import router as benches_router
from app.api.laboratories import router as laboratories_router
from app.api.alarms import router as alarms_router
from app.api.statistics import router as statistics_router
from app.api.config import router as config_router
from app.api.automation import router as automation_router
from app.api.ai_assistant import router as ai_assistant_router
from app.api.dvp import router as dvp_router
from app.api.websocket import router as websocket_router

__all__ = [
    "benches_router",
    "laboratories_router",
    "alarms_router",
    "statistics_router",
    "config_router",
    "automation_router",
    "ai_assistant_router",
    "dvp_router",
    "websocket_router",
]
