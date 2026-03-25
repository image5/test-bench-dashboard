"""
AI Assistant Dashboard API Routes
AI辅助看板 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
from pathlib import Path

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant Dashboard"])


# ============ Pydantic 模型 ============


class AIActivity(BaseModel):
    name: str
    count: int
    percentage: float


class AIOverview(BaseModel):
    total_assistances: int
    total_manual_effort_saved_hours: float
    total_activities: int
    top_activity: str


class DailyAIStats(BaseModel):
    date: str
    total_count: int
    by_activity: Dict[str, int]


class AIAssistantMetrics(BaseModel):
    overview: AIOverview
    by_activity: List[AIActivity]
    by_period: List[DailyAIStats]


class ActivityTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class AssistanceRecordCreate(BaseModel):
    activity_type: str = Field(..., description="活动类型名称")
    project_name: Optional[str] = None
    description: Optional[str] = None
    time_saved_hours: float = Field(default=0.5, ge=0)
    record_date: Optional[str] = None


# ============ 默认活动类型 ============

DEFAULT_ACTIVITY_TYPES = [
    "需求分析",
    "测试策略",
    "测试设计",
    "用例编写",
    "用例审查",
    "脚本编写",
    "脚本调试",
    "脚本执行",
    "日志分析",
    "数据分析",
    "报告编写",
]


# ============ 数据文件存储 ============

DATA_DIR = Path(__file__).parent.parent.parent / "data"
ACTIVITY_TYPES_FILE = DATA_DIR / "ai_activity_types.json"
RECORDS_FILE = DATA_DIR / "ai_assistance_records.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json_file(filepath: Path, default=None):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or []


def save_json_file(filepath: Path, data):
    ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============ API 端点 ============


@router.get("/metrics", response_model=AIAssistantMetrics)
async def get_ai_metrics(
    period: str = Query("month", description="统计周期: day, week, month, year"),
):
    """获取AI辅助指标"""
    records = load_json_file(RECORDS_FILE)
    activity_types = load_json_file(ACTIVITY_TYPES_FILE)

    if not activity_types:
        activity_types = DEFAULT_ACTIVITY_TYPES
        save_json_file(ACTIVITY_TYPES_FILE, activity_types)

    if not records:
        return AIAssistantMetrics(
            overview=AIOverview(
                total_assistances=0,
                total_manual_effort_saved_hours=0,
                total_activities=len(activity_types),
                top_activity="无",
            ),
            by_activity=[
                AIActivity(name=act, count=0, percentage=0) for act in activity_types
            ],
            by_period=[],
        )

    now = datetime.now()
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)

    filtered_records = []
    for record in records:
        record_date_str = record.get(
            "record_date", record.get("created_at", now.isoformat())
        )
        try:
            record_date = datetime.fromisoformat(
                record_date_str.replace("Z", "+00:00").split("+")[0]
            )
        except:
            record_date = now
        if record_date >= start_date:
            filtered_records.append(record)

    activity_counts = {}
    total_count = 0
    total_time_saved = 0

    for act in activity_types:
        activity_counts[act] = 0

    for record in filtered_records:
        act_type = record.get("activity_type", "")
        if act_type in activity_counts:
            activity_counts[act_type] += 1
            total_count += 1
            total_time_saved += record.get("time_saved_hours", 0.5)

    by_activity = []
    for act, count in activity_counts.items():
        percentage = round(count / total_count * 100, 1) if total_count > 0 else 0
        by_activity.append(AIActivity(name=act, count=count, percentage=percentage))

    by_activity.sort(key=lambda x: x.count, reverse=True)

    by_period = []
    date_groups = {}
    for record in filtered_records:
        date_str = record.get("record_date", record.get("created_at", ""))[:10]
        if not date_str:
            continue
        if date_str not in date_groups:
            date_groups[date_str] = {"total": 0, "by_activity": {}}
            for act in activity_types:
                date_groups[date_str]["by_activity"][act] = 0

        act_type = record.get("activity_type", "")
        if act_type in date_groups[date_str]["by_activity"]:
            date_groups[date_str]["by_activity"][act_type] += 1
            date_groups[date_str]["total"] += 1

    for date_str in sorted(date_groups.keys()):
        data = date_groups[date_str]
        by_period.append(
            DailyAIStats(
                date=date_str,
                total_count=data["total"],
                by_activity=data["by_activity"],
            )
        )

    top_activity = (
        by_activity[0].name if by_activity and by_activity[0].count > 0 else "无"
    )

    overview = AIOverview(
        total_assistances=total_count,
        total_manual_effort_saved_hours=round(total_time_saved, 2),
        total_activities=len(activity_types),
        top_activity=top_activity,
    )

    return AIAssistantMetrics(
        overview=overview, by_activity=by_activity, by_period=by_period
    )


@router.get("/overview", response_model=AIOverview)
async def get_ai_overview():
    """获取AI辅助总览数据"""
    metrics = await get_ai_metrics()
    return metrics.overview


@router.get("/activity-types", response_model=List[str])
async def list_activity_types():
    """获取活动类型列表"""
    activity_types = load_json_file(ACTIVITY_TYPES_FILE)
    if not activity_types:
        return DEFAULT_ACTIVITY_TYPES
    return activity_types


@router.post("/activity-types", response_model=dict)
async def add_activity_type(activity: ActivityTypeCreate):
    """添加活动类型"""
    activity_types = load_json_file(ACTIVITY_TYPES_FILE)

    if activity.name in activity_types:
        raise HTTPException(status_code=400, detail="活动类型已存在")

    activity_types.append(activity.name)
    save_json_file(ACTIVITY_TYPES_FILE, activity_types)

    return {"message": "活动类型已添加", "name": activity.name}


@router.get("/records", response_model=List[dict])
async def list_records(
    activity_type: Optional[str] = Query(None), limit: int = Query(100, ge=1, le=1000)
):
    """获取辅助记录列表"""
    records = load_json_file(RECORDS_FILE)

    if activity_type:
        records = [r for r in records if r.get("activity_type") == activity_type]

    records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return records[:limit]


@router.post("/records", response_model=dict)
async def add_record(record: AssistanceRecordCreate):
    """添加辅助记录"""
    activity_types = load_json_file(ACTIVITY_TYPES_FILE)
    if not activity_types:
        activity_types = DEFAULT_ACTIVITY_TYPES
        save_json_file(ACTIVITY_TYPES_FILE, activity_types)

    if record.activity_type not in activity_types:
        raise HTTPException(
            status_code=400, detail=f"无效的活动类型: {record.activity_type}"
        )

    records = load_json_file(RECORDS_FILE)

    new_record = {
        "id": f"ai_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(records)}",
        "activity_type": record.activity_type,
        "project_name": record.project_name,
        "description": record.description,
        "time_saved_hours": record.time_saved_hours,
        "record_date": record.record_date or datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat(),
    }

    records.append(new_record)
    save_json_file(RECORDS_FILE, records)

    return new_record


@router.post("/records/batch", response_model=dict)
async def add_records_batch(records: List[AssistanceRecordCreate]):
    """批量添加辅助记录"""
    activity_types = load_json_file(ACTIVITY_TYPES_FILE)
    if not activity_types:
        activity_types = DEFAULT_ACTIVITY_TYPES
        save_json_file(ACTIVITY_TYPES_FILE, activity_types)

    existing_records = load_json_file(RECORDS_FILE)
    added_count = 0

    for record in records:
        if record.activity_type not in activity_types:
            continue

        new_record = {
            "id": f"ai_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(existing_records)}",
            "activity_type": record.activity_type,
            "project_name": record.project_name,
            "description": record.description,
            "time_saved_hours": record.time_saved_hours,
            "record_date": record.record_date or datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
        }
        existing_records.append(new_record)
        added_count += 1

    save_json_file(RECORDS_FILE, existing_records)

    return {"message": f"已添加 {added_count} 条记录", "added_count": added_count}


@router.post("/reset")
async def reset_data():
    """重置数据"""
    save_json_file(RECORDS_FILE, [])
    return {"message": "数据已重置"}


@router.post("/init-demo")
async def init_demo_data():
    """初始化演示数据"""
    records = load_json_file(RECORDS_FILE)

    if records:
        return {"message": "数据已存在，跳过初始化", "record_count": len(records)}

    save_json_file(ACTIVITY_TYPES_FILE, DEFAULT_ACTIVITY_TYPES)

    demo_records = []
    now = datetime.now()

    for i in range(30):
        date = (now - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        import random

        for _ in range(random.randint(10, 30)):
            activity = random.choice(DEFAULT_ACTIVITY_TYPES)
            demo_records.append(
                {
                    "id": f"ai_{date}_{len(demo_records)}",
                    "activity_type": activity,
                    "project_name": random.choice(["项目A", "项目B", "项目C", None]),
                    "description": f"{activity}演示记录",
                    "time_saved_hours": round(random.uniform(0.2, 1.0), 2),
                    "record_date": date,
                    "created_at": datetime.now().isoformat(),
                }
            )

    save_json_file(RECORDS_FILE, demo_records)

    return {"message": "演示数据已初始化", "record_count": len(demo_records)}
