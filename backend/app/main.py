"""
Main Application
主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.core.database import init_db
from app.core.device_monitor import device_monitor
from app.core.websocket_manager import ws_manager
from app.api import (
    benches_router,
    laboratories_router,
    alarms_router,
    statistics_router,
    config_router,
    automation_router,
    ai_assistant_router,
    dvp_router,
    websocket_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    init_db()
    print("[OK] Database initialized")

    device_monitor.set_ws_manager(ws_manager)
    device_monitor.start()
    monitor_task = asyncio.create_task(device_monitor.monitor_devices())
    print("[OK] Device monitor started")

    yield

    device_monitor.stop()
    monitor_task.cancel()
    print("[INFO] Application shutdown")


app = FastAPI(
    title="智能测试台架工厂数字孪生看板",
    description="Test Bench Factory Digital Twin Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router)
app.include_router(benches_router, prefix="/api/v1")
app.include_router(laboratories_router, prefix="/api/v1")
app.include_router(alarms_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")
app.include_router(automation_router, prefix="/api/v1")
app.include_router(ai_assistant_router, prefix="/api/v1")
app.include_router(dvp_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智能测试台架工厂数字孪生看板 API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0", port=8000)
