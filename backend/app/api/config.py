"""
Config API Routes
配置管理 API 路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import json
import os
import datetime
from pathlib import Path

router = APIRouter(prefix="/config", tags=["Config"])

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "frontend" / "public" / "config.json"


class ConfigUpdate(BaseModel):
    """配置更新模型"""
    apiUrl: str
    version: Optional[str] = "1.0.0"
    lastUpdate: Optional[str] = None


class ConfigResponse(BaseModel):
    """配置响应模型"""
    apiUrl: str
    version: str
    lastUpdate: str


@router.get("", response_model=ConfigResponse)
async def get_config():
    """获取当前配置"""
    try:
        if not CONFIG_FILE.exists():
            # 返回默认配置
            return ConfigResponse(
                apiUrl="http://localhost:8000/api/v1",
                version="1.0.0",
                lastUpdate="2026-03-12"
            )
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return ConfigResponse(**config)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置失败: {str(e)}")


@router.post("", response_model=ConfigResponse)
async def update_config(config_data: ConfigUpdate):
    """更新配置"""
    try:
        # 准备配置数据
        config_dict = {
            "apiUrl": config_data.apiUrl,
            "version": config_data.version or "1.0.0",
            "lastUpdate": config_data.lastUpdate or str(datetime.date.today())
        }
        
        # 确保目录存在
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        return ConfigResponse(**config_dict)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.post("/reset", response_model=ConfigResponse)
async def reset_config():
    """重置为默认配置"""
    try:
        default_config = {
            "apiUrl": "http://localhost:8000/api/v1",
            "version": "1.0.0",
            "lastUpdate": str(datetime.date.today())
        }
        
        # 确保目录存在
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return ConfigResponse(**default_config)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置配置失败: {str(e)}")
