"""
DVP Dashboard API Routes
DVP进度看板 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

router = APIRouter(prefix="/dvp", tags=["DVP Dashboard"])


# ============ Pydantic 模型 ============


class Project(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    total_experiments: int
    total_devices: int
    progress: float
    param_checked: bool
    is_interrupted: bool
    created_at: str
    updated_at: str


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    total_experiments: int = Field(default=0, ge=0)
    total_devices: int = Field(default=0, ge=0)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    total_experiments: Optional[int] = Field(None, ge=0)
    total_devices: Optional[int] = Field(None, ge=0)
    completed_devices: Optional[int] = Field(None, ge=0)
    progress: Optional[float] = Field(None, ge=0, le=100)
    param_checked: Optional[bool] = None
    is_interrupted: Optional[bool] = None


class ProgressUpdate(BaseModel):
    progress: float = Field(..., ge=0, le=100)
    completed_devices: Optional[int] = Field(None, ge=0)
    param_checked: Optional[bool] = None
    is_interrupted: Optional[bool] = None


class ProjectStatistics(BaseModel):
    total_projects: int
    running_projects: int
    completed_projects: int
    interrupted_projects: int
    average_progress: float


# ============ 数据文件存储 ============

DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROJECTS_FILE = DATA_DIR / "dvp_projects.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_projects() -> List[dict]:
    ensure_data_dir()
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_projects(projects: List[dict]):
    ensure_data_dir()
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


# ============ API 端点 ============


@router.get("/projects", response_model=List[Project])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(
        None, description="筛选状态: running, completed, interrupted"
    ),
):
    """获取所有项目列表"""
    projects = load_projects()

    if status:
        if status == "running":
            projects = [
                p
                for p in projects
                if p["progress"] < 100 and not p.get("is_interrupted")
            ]
        elif status == "completed":
            projects = [p for p in projects if p["progress"] >= 100]
        elif status == "interrupted":
            projects = [p for p in projects if p.get("is_interrupted")]

    return projects[skip : skip + limit]


@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """获取单个项目详情"""
    projects = load_projects()

    for project in projects:
        if project["project_id"] == project_id:
            return project

    raise HTTPException(status_code=404, detail="项目不存在")


@router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    """创建新项目"""
    projects = load_projects()

    for p in projects:
        if p["name"] == project.name:
            raise HTTPException(status_code=400, detail="项目名称已存在")

    now = datetime.now()
    new_project = {
        "project_id": f"dvp_{now.strftime('%Y%m%d%H%M%S')}_{len(projects)}",
        "name": project.name,
        "description": project.description,
        "total_experiments": project.total_experiments,
        "total_devices": project.total_devices,
        "progress": 0.0,
        "param_checked": False,
        "is_interrupted": False,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    projects.append(new_project)
    save_projects(projects)

    return new_project


@router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, update: ProjectUpdate):
    """更新项目信息"""
    projects = load_projects()

    for project in projects:
        if project["project_id"] == project_id:
            if update.name is not None:
                for p in projects:
                    if p["project_id"] != project_id and p["name"] == update.name:
                        raise HTTPException(status_code=400, detail="项目名称已存在")
                project["name"] = update.name

            if update.description is not None:
                project["description"] = update.description
            if update.total_experiments is not None:
                project["total_experiments"] = update.total_experiments
            if update.total_devices is not None:
                project["total_devices"] = update.total_devices
            if update.completed_devices is not None:
                project["completed_devices"] = update.completed_devices
            if update.progress is not None:
                project["progress"] = update.progress
            if update.param_checked is not None:
                project["param_checked"] = update.param_checked
            if update.is_interrupted is not None:
                project["is_interrupted"] = update.is_interrupted

            project["updated_at"] = datetime.now().isoformat()
            save_projects(projects)
            return project

    raise HTTPException(status_code=404, detail="项目不存在")


@router.put("/projects/{project_id}/progress", response_model=Project)
async def update_progress(project_id: str, update: ProgressUpdate):
    """更新项目进度"""
    projects = load_projects()

    for project in projects:
        if project["project_id"] == project_id:
            project["progress"] = update.progress

            if update.completed_devices is not None:
                project["completed_devices"] = update.completed_devices
            if update.param_checked is not None:
                project["param_checked"] = update.param_checked
            if update.is_interrupted is not None:
                project["is_interrupted"] = update.is_interrupted

            project["updated_at"] = datetime.now().isoformat()
            save_projects(projects)
            return project

    raise HTTPException(status_code=404, detail="项目不存在")


@router.post("/projects/{project_id}/interrupt", response_model=Project)
async def interrupt_project(project_id: str):
    """中断项目"""
    projects = load_projects()

    for project in projects:
        if project["project_id"] == project_id:
            project["is_interrupted"] = True
            project["updated_at"] = datetime.now().isoformat()
            save_projects(projects)
            return project

    raise HTTPException(status_code=404, detail="项目不存在")


@router.post("/projects/{project_id}/resume", response_model=Project)
async def resume_project(project_id: str):
    """恢复项目"""
    projects = load_projects()

    for project in projects:
        if project["project_id"] == project_id:
            project["is_interrupted"] = False
            project["updated_at"] = datetime.now().isoformat()
            save_projects(projects)
            return project

    raise HTTPException(status_code=404, detail="项目不存在")


@router.post("/projects/{project_id}/check-params", response_model=Project)
async def check_project_params(project_id: str):
    """标记项目参数已检查"""
    projects = load_projects()

    for project in projects:
        if project["project_id"] == project_id:
            project["param_checked"] = True
            project["updated_at"] = datetime.now().isoformat()
            save_projects(projects)
            return project

    raise HTTPException(status_code=404, detail="项目不存在")


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    projects = load_projects()

    for i, project in enumerate(projects):
        if project["project_id"] == project_id:
            projects.pop(i)
            save_projects(projects)
            return {"message": "项目已删除", "project_id": project_id}

    raise HTTPException(status_code=404, detail="项目不存在")


@router.get("/statistics", response_model=ProjectStatistics)
async def get_statistics():
    """获取统计信息"""
    projects = load_projects()

    total = len(projects)
    running = sum(
        1 for p in projects if p["progress"] < 100 and not p.get("is_interrupted")
    )
    completed = sum(1 for p in projects if p["progress"] >= 100)
    interrupted = sum(1 for p in projects if p.get("is_interrupted"))
    avg_progress = sum(p["progress"] for p in projects) / total if total > 0 else 0

    return ProjectStatistics(
        total_projects=total,
        running_projects=running,
        completed_projects=completed,
        interrupted_projects=interrupted,
        average_progress=round(avg_progress, 1),
    )


@router.post("/reset")
async def reset_data():
    """重置所有数据"""
    save_projects([])
    return {"message": "数据已重置"}


@router.post("/init-demo")
async def init_demo_data():
    """初始化演示数据"""
    projects = load_projects()

    if projects:
        return {"message": "数据已存在，跳过初始化", "project_count": len(projects)}

    import random

    now = datetime.now()

    demo_projects = []
    project_names = [
        "电机控制器V1.0",
        "电池管理系统V2.0",
        "ADAS控制器V3.0",
        "车身控制器V1.5",
        "充电系统V2.0",
        "热管理系统V1.0",
        "转向控制器V2.5",
        "悬架控制器V1.2",
        "座椅控制器V1.0",
        "门控制器V2.0",
    ]

    for i, name in enumerate(project_names):
        total_experiments = random.randint(10, 30)
        total_devices = total_experiments * random.randint(5, 15)
        progress = random.uniform(0, 100)

        demo_projects.append(
            {
                "project_id": f"dvp_{i + 1:04d}",
                "name": name,
                "description": f"{name} DVP验证项目",
                "total_experiments": total_experiments,
                "total_devices": total_devices,
                "progress": round(progress, 1),
                "param_checked": random.choice([True, False]),
                "is_interrupted": random.random() < 0.1,
                "created_at": (now - timedelta(days=random.randint(1, 30))).isoformat(),
                "updated_at": now.isoformat(),
            }
        )

    save_projects(demo_projects)

    return {"message": "演示数据已初始化", "project_count": len(demo_projects)}
