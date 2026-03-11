"""
Statistics API Routes
统计 API 路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.core.database import get_db
from app.models.bench import TestBench, BenchStatus
from app.models.laboratory import Laboratory
from app.schemas import StatisticsOverview, LaboratoryStatistics

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=dict)
async def get_overview(db: Session = Depends(get_db)):
    """获取总览统计"""
    benches = db.query(TestBench).all()
    
    total = len(benches)
    running = sum(1 for b in benches if b.status == BenchStatus.RUNNING)
    offline = sum(1 for b in benches if b.status == BenchStatus.OFFLINE)
    maintenance = sum(1 for b in benches if b.status == BenchStatus.MAINTENANCE)
    alarm = sum(1 for b in benches if b.status == BenchStatus.ALARM)
    idle = sum(1 for b in benches if b.status == BenchStatus.IDLE)
    
    # 在线率 = (运行 + 空闲 + 告警) / 总数
    online = running + idle + alarm
    online_rate = (online / total * 100) if total > 0 else 0
    
    return {
        "totalBenches": total,
        "runningCount": running,
        "offlineCount": offline,
        "maintenanceCount": maintenance,
        "alarmCount": alarm,
        "idleCount": idle,
        "onlineRate": round(online_rate, 1),
        "currentTime": datetime.utcnow().isoformat(),
        "statusBreakdown": {
            "running": running,
            "offline": offline,
            "maintenance": maintenance,
            "alarm": alarm,
            "idle": idle
        }
    }


@router.get("/laboratory/{lab_id}", response_model=dict)
async def get_laboratory_statistics(lab_id: str, db: Session = Depends(get_db)):
    """获取实验室统计"""
    lab = db.query(Laboratory).filter(Laboratory.id == lab_id).first()
    if not lab:
        return {"error": "实验室不存在"}
    
    benches = db.query(TestBench).filter(TestBench.laboratory_id == lab_id).all()
    
    total = len(benches)
    running = sum(1 for b in benches if b.status == BenchStatus.RUNNING)
    offline = sum(1 for b in benches if b.status == BenchStatus.OFFLINE)
    maintenance = sum(1 for b in benches if b.status == BenchStatus.MAINTENANCE)
    alarm = sum(1 for b in benches if b.status == BenchStatus.ALARM)
    idle = sum(1 for b in benches if b.status == BenchStatus.IDLE)
    
    online = running + idle + alarm
    online_rate = (online / total * 100) if total > 0 else 0
    
    return {
        "laboratoryId": lab_id,
        "laboratoryName": lab.name,
        "totalBenches": total,
        "runningCount": running,
        "offlineCount": offline,
        "maintenanceCount": maintenance,
        "alarmCount": alarm,
        "idleCount": idle,
        "onlineRate": round(online_rate, 1)
    }


@router.get("/by-type", response_model=dict)
async def get_statistics_by_type(db: Session = Depends(get_db)):
    """按类型统计"""
    from app.models.bench import BenchType
    
    benches = db.query(TestBench).all()
    
    type_stats = {}
    for bench_type in BenchType:
        type_benches = [b for b in benches if b.type == bench_type]
        total = len(type_benches)
        
        if total > 0:
            running = sum(1 for b in type_benches if b.status == BenchStatus.RUNNING)
            offline = sum(1 for b in type_benches if b.status == BenchStatus.OFFLINE)
            maintenance = sum(1 for b in type_benches if b.status == BenchStatus.MAINTENANCE)
            alarm = sum(1 for b in type_benches if b.status == BenchStatus.ALARM)
            idle = sum(1 for b in type_benches if b.status == BenchStatus.IDLE)
            
            type_stats[bench_type.value] = {
                "total": total,
                "running": running,
                "offline": offline,
                "maintenance": maintenance,
                "alarm": alarm,
                "idle": idle
            }
    
    return type_stats
