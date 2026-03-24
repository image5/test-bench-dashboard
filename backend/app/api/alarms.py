"""
Alarm API Routes
告警 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.models.alarm import Alarm, AlarmType, AlarmSeverity
from app.models.bench import TestBench, BenchStatus
from app.schemas import AlarmCreate, AlarmAcknowledge, AlarmResponse

router = APIRouter(prefix="/alarms", tags=["Alarms"])


@router.get("", response_model=List[dict])
async def get_alarms(
    bench_id: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """获取告警列表"""
    query = db.query(Alarm)

    if bench_id:
        query = query.filter(Alarm.bench_id == bench_id)
    if acknowledged is not None:
        query = query.filter(Alarm.acknowledged == acknowledged)
    if severity:
        query = query.filter(Alarm.severity == severity)

    alarms = query.order_by(Alarm.created_at.desc()).limit(limit).all()
    return [a.to_dict() for a in alarms]


@router.get("/active", response_model=List[dict])
async def get_active_alarms(db: Session = Depends(get_db)):
    """获取未确认的活跃告警"""
    alarms = (
        db.query(Alarm)
        .filter(Alarm.acknowledged == False)
        .order_by(Alarm.created_at.desc())
        .all()
    )
    return [a.to_dict() for a in alarms]


@router.post("", response_model=dict)
async def create_alarm(alarm_data: AlarmCreate, db: Session = Depends(get_db)):
    """创建告警"""
    bench = db.query(TestBench).filter(TestBench.id == alarm_data.bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    alarm = Alarm(
        bench_id=alarm_data.bench_id,
        type=AlarmType(alarm_data.type.value),
        severity=AlarmSeverity(alarm_data.severity.value),
        message=alarm_data.message,
        value=alarm_data.value,
        threshold=alarm_data.threshold,
    )
    db.add(alarm)

    bench.has_alarm = True
    bench.alarm_message = alarm_data.message
    bench.status = BenchStatus.ALARM
    bench.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(alarm)

    await ws_manager.broadcast({"event": "alarm_created", "data": alarm.to_dict()})

    return alarm.to_dict()


@router.put("/{alarm_id}/acknowledge", response_model=dict)
async def acknowledge_alarm(
    alarm_id: str, ack_data: AlarmAcknowledge, db: Session = Depends(get_db)
):
    """确认告警"""
    alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="告警不存在")

    alarm.acknowledged = True
    alarm.acknowledged_by = ack_data.acknowledged_by
    alarm.acknowledged_at = datetime.utcnow()

    db.commit()
    db.refresh(alarm)

    await ws_manager.broadcast({"event": "alarm_acknowledged", "data": alarm.to_dict()})

    return alarm.to_dict()


@router.post("/{alarm_id}/clear-bench-alarm")
async def clear_bench_alarm(alarm_id: str, db: Session = Depends(get_db)):
    """确认告警并清除台架告警状态"""
    alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="告警不存在")

    alarm.acknowledged = True
    alarm.acknowledged_at = datetime.utcnow()

    bench = db.query(TestBench).filter(TestBench.id == alarm.bench_id).first()
    if bench:
        bench.has_alarm = False
        bench.alarm_message = None
        if bench.status == BenchStatus.ALARM:
            bench.status = BenchStatus.IDLE
        bench.updated_at = datetime.utcnow()

    db.commit()

    await ws_manager.broadcast(
        {
            "event": "alarm_cleared",
            "data": {"alarmId": alarm_id, "benchId": alarm.bench_id},
        }
    )

    return {"message": "告警已确认并清除台架状态"}
