"""
Test Bench API Routes
测试台架 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.models.bench import TestBench, BenchType, BenchStatus
from app.models.maintenance import MaintenanceRecord
from app.schemas import (
    TestBenchCreate,
    TestBenchUpdate,
    TestBenchResponse,
    PositionUpdate,
    MaintenanceSet,
    HeartbeatData,
    BenchImportRequest,
    BenchImportResponse,
)

router = APIRouter(prefix="/benches", tags=["Test Benches"])


@router.get("", response_model=List[dict])
async def get_benches(
    laboratory_id: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取台架列表"""
    query = db.query(TestBench)

    if laboratory_id:
        query = query.filter(TestBench.laboratory_id == laboratory_id)
    if status:
        query = query.filter(TestBench.status == status)
    if type:
        query = query.filter(TestBench.type == type)

    benches = query.all()
    return [b.to_dict() for b in benches]


@router.get("/{bench_id}", response_model=dict)
async def get_bench(bench_id: str, db: Session = Depends(get_db)):
    """获取台架详情"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")
    return bench.to_dict()


@router.post("", response_model=dict)
async def create_bench(bench_data: TestBenchCreate, db: Session = Depends(get_db)):
    """创建台架"""
    bench = TestBench(
        laboratory_id=bench_data.laboratory_id,
        name=bench_data.name,
        type=BenchType(bench_data.type.value),
        ip_address=bench_data.ip_address,
        port=bench_data.port,
        position_x=bench_data.position_x,
        position_y=bench_data.position_y,
        rotation=bench_data.rotation,
        status=BenchStatus.OFFLINE,
    )
    db.add(bench)
    db.commit()
    db.refresh(bench)

    await ws_manager.broadcast({"event": "bench_created", "data": bench.to_dict()})

    return bench.to_dict()


@router.put("/{bench_id}", response_model=dict)
async def update_bench(
    bench_id: str, bench_data: TestBenchUpdate, db: Session = Depends(get_db)
):
    """更新台架信息"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    update_data = bench_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "type" and value:
            setattr(bench, key, BenchType(value.value))
        else:
            setattr(bench, key, value)

    bench.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bench)

    await ws_manager.broadcast({"event": "bench_updated", "data": bench.to_dict()})

    return bench.to_dict()


@router.delete("/{bench_id}")
async def delete_bench(bench_id: str, db: Session = Depends(get_db)):
    """删除台架"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    db.delete(bench)
    db.commit()

    await ws_manager.broadcast({"event": "bench_deleted", "data": {"id": bench_id}})

    return {"message": "台架已删除", "id": bench_id}


@router.put("/{bench_id}/position", response_model=dict)
async def update_position(
    bench_id: str, position_data: PositionUpdate, db: Session = Depends(get_db)
):
    """更新台架位置"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    bench.position_x = position_data.position_x
    bench.position_y = position_data.position_y
    if position_data.rotation is not None:
        bench.rotation = position_data.rotation
    bench.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(bench)

    await ws_manager.broadcast(
        {
            "event": "bench_moved",
            "data": {
                "id": bench_id,
                "position": {
                    "x": bench.position_x,
                    "y": bench.position_y,
                    "rotation": bench.rotation,
                },
            },
        }
    )

    return bench.to_dict()


@router.put("/{bench_id}/maintenance", response_model=dict)
async def set_maintenance(
    bench_id: str, maintenance_data: MaintenanceSet, db: Session = Depends(get_db)
):
    """设置维护状态"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    if maintenance_data.is_under_maintenance:
        bench.is_under_maintenance = True
        bench.maintenance_reason = maintenance_data.reason
        bench.maintenance_operator = maintenance_data.operator
        bench.maintenance_start_time = datetime.utcnow()
        bench.status = BenchStatus.MAINTENANCE

        record = MaintenanceRecord(
            bench_id=bench_id,
            reason=maintenance_data.reason or "",
            operator=maintenance_data.operator or "",
            start_time=datetime.utcnow(),
        )
        db.add(record)
    else:
        active_record = (
            db.query(MaintenanceRecord)
            .filter(
                MaintenanceRecord.bench_id == bench_id,
                MaintenanceRecord.end_time == None,
            )
            .first()
        )

        if active_record:
            active_record.end_time = datetime.utcnow()

        bench.is_under_maintenance = False
        bench.maintenance_reason = None
        bench.maintenance_operator = None
        bench.maintenance_start_time = None
        bench.status = BenchStatus.OFFLINE

    bench.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bench)

    await ws_manager.broadcast(
        {"event": "bench_maintenance_changed", "data": bench.to_dict()}
    )

    return bench.to_dict()


@router.post("/{bench_id}/heartbeat", response_model=dict)
async def heartbeat(
    bench_id: str, heartbeat_data: HeartbeatData, db: Session = Depends(get_db)
):
    """台架心跳"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    if bench.is_under_maintenance:
        return {"message": "台架在维护中，心跳被忽略"}

    bench.last_heartbeat = datetime.utcnow()

    if heartbeat_data.status:
        bench.status = BenchStatus(heartbeat_data.status.value)
    elif bench.status == BenchStatus.OFFLINE:
        bench.status = BenchStatus.IDLE

    if heartbeat_data.current_task:
        if bench.current_task != heartbeat_data.current_task:
            bench.current_task = heartbeat_data.current_task
            bench.task_start_time = datetime.utcnow()
    else:
        bench.current_task = None
        bench.task_start_time = None

    if heartbeat_data.metrics:
        bench.metrics = heartbeat_data.metrics

    bench.updated_at = datetime.utcnow()
    db.commit()

    await ws_manager.broadcast(
        {
            "event": "bench_heartbeat",
            "data": {
                "id": bench_id,
                "status": bench.to_dict()["status"],
                "currentTask": bench.current_task,
                "lastHeartbeat": bench.last_heartbeat.isoformat(),
            },
        }
    )

    return {"message": "心跳成功", "timestamp": bench.last_heartbeat.isoformat()}


@router.post("/{bench_id}/clear-alarm", response_model=dict)
async def clear_alarm(bench_id: str, db: Session = Depends(get_db)):
    """清除台架告警"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    bench.has_alarm = False
    bench.alarm_message = None
    if bench.status == BenchStatus.ALARM:
        bench.status = BenchStatus.IDLE

    bench.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bench)

    await ws_manager.broadcast(
        {"event": "bench_alarm_cleared", "data": {"id": bench_id}}
    )

    return bench.to_dict()


@router.get("/{bench_id}/maintenance-history", response_model=List[dict])
async def get_maintenance_history(bench_id: str, db: Session = Depends(get_db)):
    """获取台架维护历史"""
    bench = db.query(TestBench).filter(TestBench.id == bench_id).first()
    if not bench:
        raise HTTPException(status_code=404, detail="台架不存在")

    records = (
        db.query(MaintenanceRecord)
        .filter(MaintenanceRecord.bench_id == bench_id)
        .order_by(MaintenanceRecord.start_time.desc())
        .limit(50)
        .all()
    )

    return [r.to_dict() for r in records]


@router.post("/import", response_model=dict)
async def import_benches(
    import_data: BenchImportRequest, db: Session = Depends(get_db)
):
    """批量导入台架"""
    success_count = 0
    failed_count = 0
    errors = []
    created_benches = []

    for idx, item in enumerate(import_data.benches):
        try:
            bench_type = BenchType(item.type.lower())
        except ValueError:
            failed_count += 1
            errors.append(
                {
                    "row": idx + 1,
                    "name": item.name,
                    "error": f"无效的台架类型: {item.type}",
                }
            )
            continue

        try:
            bench = TestBench(
                laboratory_id=import_data.laboratory_id,
                name=item.name,
                type=bench_type,
                ip_address=item.ip_address,
                port=item.port,
                position_x=item.position_x,
                position_y=item.position_y,
                rotation=0,
                status=BenchStatus.OFFLINE,
            )
            db.add(bench)
            db.flush()
            created_benches.append(bench.to_dict())
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append({"row": idx + 1, "name": item.name, "error": str(e)})

    if success_count > 0:
        db.commit()
        for bench_data in created_benches:
            await ws_manager.broadcast({"event": "bench_created", "data": bench_data})

    return {
        "successCount": success_count,
        "failedCount": failed_count,
        "errors": errors,
        "createdBenches": created_benches,
    }
