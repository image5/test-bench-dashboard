"""
Automation Dashboard API Routes
自动化测试看板 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from app.core.database import get_db, SessionLocal
from app.models.automation import AutomationProject, AutomationExecution

router = APIRouter(prefix="/automation", tags=["Automation Dashboard"])


# ============ Pydantic 模型 ============


class AutomationStats(BaseModel):
    total_test_cases: int
    total_execution_time_hours: float
    total_manual_effort_saved_hours: float
    total_projects: int
    pass_rate: float


class ProjectAutomationStats(BaseModel):
    project_name: str
    test_cases: int
    execution_time_hours: float
    pass_rate: float
    failed_count: int


class DailyStats(BaseModel):
    date: str
    test_cases: int
    execution_time_hours: float
    pass_rate: float
    failed_count: int


class AutomationMetrics(BaseModel):
    overview: AutomationStats
    by_project: List[ProjectAutomationStats]
    by_period: List[DailyStats]


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ExecutionCreate(BaseModel):
    project_id: Optional[str] = None
    execution_date: str
    test_cases: int = Field(..., ge=0)
    execution_time_hours: float = Field(..., ge=0)
    passed_count: int = Field(..., ge=0)
    failed_count: int = Field(..., ge=0)


# ============ 数据文件存储 ============

DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROJECTS_FILE = DATA_DIR / "automation_projects.json"
EXECUTIONS_FILE = DATA_DIR / "automation_executions.json"


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


@router.get("/metrics", response_model=AutomationMetrics)
async def get_automation_metrics(
    period: str = Query("month", description="统计周期: day, week, month, year"),
    project: Optional[str] = Query(None, description="项目名称筛选"),
):
    """获取自动化测试指标"""
    projects = load_json_file(PROJECTS_FILE)
    executions = load_json_file(EXECUTIONS_FILE)

    if not projects:
        return AutomationMetrics(
            overview=AutomationStats(
                total_test_cases=0,
                total_execution_time_hours=0,
                total_manual_effort_saved_hours=0,
                total_projects=0,
                pass_rate=0,
            ),
            by_project=[],
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

    filtered_executions = []
    for exec_data in executions:
        exec_date = datetime.fromisoformat(
            exec_data.get("execution_date", now.isoformat())
        )
        if exec_date >= start_date:
            filtered_executions.append(exec_data)

    by_project = []
    total_cases = 0
    total_time = 0
    total_passed = 0
    total_failed = 0

    for proj in projects:
        proj_id = proj.get("id")
        proj_executions = [
            e for e in filtered_executions if e.get("project_id") == proj_id
        ]

        if project and project.lower() not in proj.get("name", "").lower():
            continue

        proj_cases = sum(e.get("test_cases", 0) for e in proj_executions)
        proj_time = sum(e.get("execution_time_hours", 0) for e in proj_executions)
        proj_passed = sum(e.get("passed_count", 0) for e in proj_executions)
        proj_failed = sum(e.get("failed_count", 0) for e in proj_executions)

        pass_rate = round(proj_passed / proj_cases * 100, 1) if proj_cases > 0 else 0

        by_project.append(
            ProjectAutomationStats(
                project_name=proj.get("name", ""),
                test_cases=proj_cases,
                execution_time_hours=round(proj_time, 2),
                pass_rate=pass_rate,
                failed_count=proj_failed,
            )
        )

        total_cases += proj_cases
        total_time += proj_time
        total_passed += proj_passed
        total_failed += proj_failed

    by_project.sort(key=lambda x: x.test_cases, reverse=True)

    by_period = []
    date_groups = {}
    for exec_data in filtered_executions:
        date_str = exec_data.get("execution_date", "")[:10]
        if date_str not in date_groups:
            date_groups[date_str] = {"cases": 0, "time": 0, "passed": 0, "failed": 0}
        date_groups[date_str]["cases"] += exec_data.get("test_cases", 0)
        date_groups[date_str]["time"] += exec_data.get("execution_time_hours", 0)
        date_groups[date_str]["passed"] += exec_data.get("passed_count", 0)
        date_groups[date_str]["failed"] += exec_data.get("failed_count", 0)

    for date_str in sorted(date_groups.keys()):
        data = date_groups[date_str]
        cases = data["cases"]
        passed = data["passed"]
        by_period.append(
            DailyStats(
                date=date_str,
                test_cases=cases,
                execution_time_hours=round(data["time"], 2),
                pass_rate=round(passed / cases * 100, 1) if cases > 0 else 0,
                failed_count=data["failed"],
            )
        )

    overview = AutomationStats(
        total_test_cases=total_cases,
        total_execution_time_hours=round(total_time, 2),
        total_manual_effort_saved_hours=round(total_time * 8, 2),
        total_projects=len(projects),
        pass_rate=round(total_passed / total_cases * 100, 1) if total_cases > 0 else 0,
    )

    return AutomationMetrics(
        overview=overview, by_project=by_project, by_period=by_period
    )


@router.get("/overview", response_model=AutomationStats)
async def get_automation_overview():
    """获取自动化测试总览数据"""
    metrics = await get_automation_metrics()
    return metrics.overview


@router.get("/projects", response_model=List[dict])
async def list_projects():
    """获取项目列表"""
    return load_json_file(PROJECTS_FILE)


@router.post("/projects", response_model=dict)
async def create_project(project: ProjectCreate):
    """创建项目"""
    projects = load_json_file(PROJECTS_FILE)

    for p in projects:
        if p.get("name") == project.name:
            raise HTTPException(status_code=400, detail="项目名称已存在")

    new_project = {
        "id": f"auto_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(projects)}",
        "name": project.name,
        "description": project.description,
        "total_test_cases": 0,
        "total_execution_time_hours": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    projects.append(new_project)
    save_json_file(PROJECTS_FILE, projects)

    return new_project


@router.post("/executions", response_model=dict)
async def add_execution(execution: ExecutionCreate):
    """添加执行记录"""
    executions = load_json_file(EXECUTIONS_FILE)

    new_execution = {
        "id": f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(executions)}",
        "project_id": execution.project_id,
        "execution_date": execution.execution_date,
        "test_cases": execution.test_cases,
        "execution_time_hours": execution.execution_time_hours,
        "passed_count": execution.passed_count,
        "failed_count": execution.failed_count,
        "created_at": datetime.now().isoformat(),
    }

    executions.append(new_execution)
    save_json_file(EXECUTIONS_FILE, executions)

    if execution.project_id:
        projects = load_json_file(PROJECTS_FILE)
        for proj in projects:
            if proj.get("id") == execution.project_id:
                proj["total_test_cases"] = (
                    proj.get("total_test_cases", 0) + execution.test_cases
                )
                proj["total_execution_time_hours"] = (
                    proj.get("total_execution_time_hours", 0)
                    + execution.execution_time_hours
                )
                proj["updated_at"] = datetime.now().isoformat()
                break
        save_json_file(PROJECTS_FILE, projects)

    return new_execution


@router.post("/reset")
async def reset_data():
    """重置数据（清空所有数据）"""
    save_json_file(PROJECTS_FILE, [])
    save_json_file(EXECUTIONS_FILE, [])
    return {"message": "数据已重置"}


@router.post("/init-demo")
async def init_demo_data():
    """初始化演示数据"""
    projects = load_json_file(PROJECTS_FILE)
    executions = load_json_file(EXECUTIONS_FILE)

    if projects:
        return {"message": "数据已存在，跳过初始化", "project_count": len(projects)}

    demo_projects = [
        {
            "id": "auto_001",
            "name": "新能源控制器V1.0",
            "description": "新能源控制器自动化测试",
        },
        {"id": "auto_002", "name": "电池管理系统V2.0", "description": "BMS自动化测试"},
        {"id": "auto_003", "name": "电机控制器V3.0", "description": "MCU自动化测试"},
        {"id": "auto_004", "name": "充电系统V1.5", "description": "OBC自动化测试"},
        {"id": "auto_005", "name": "热管理系统V2.0", "description": "TMS自动化测试"},
    ]

    for proj in demo_projects:
        proj["total_test_cases"] = 0
        proj["total_execution_time_hours"] = 0
        proj["created_at"] = datetime.now().isoformat()
        proj["updated_at"] = datetime.now().isoformat()

    save_json_file(PROJECTS_FILE, demo_projects)

    demo_executions = []
    now = datetime.now()
    for i in range(30):
        date = (now - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        for proj in demo_projects:
            import random

            cases = random.randint(20, 100)
            passed = random.randint(int(cases * 0.85), cases)
            failed = cases - passed
            time_hours = cases * random.uniform(0.01, 0.03)

            demo_executions.append(
                {
                    "id": f"exec_{date}_{proj['id']}",
                    "project_id": proj["id"],
                    "execution_date": date,
                    "test_cases": cases,
                    "execution_time_hours": round(time_hours, 2),
                    "passed_count": passed,
                    "failed_count": failed,
                    "created_at": datetime.now().isoformat(),
                }
            )

    save_json_file(EXECUTIONS_FILE, demo_executions)

    return {
        "message": "演示数据已初始化",
        "project_count": len(demo_projects),
        "execution_count": len(demo_executions),
    }
