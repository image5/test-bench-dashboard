"""
Main Application
主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.database import init_db
from app.api import benches_router, laboratories_router, alarms_router, statistics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    init_db()
    print("[OK] Database initialized")
    yield
    # 关闭时
    print("[INFO] Application shutdown")


# 创建应用
app = FastAPI(
    title="智能测试台架工厂数字孪生看板",
    description="Test Bench Factory Digital Twin Dashboard API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(benches_router, prefix="/api/v1")
app.include_router(laboratories_router, prefix="/api/v1")
app.include_router(alarms_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智能测试台架工厂数字孪生看板 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
