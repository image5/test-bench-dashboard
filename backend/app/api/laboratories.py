"""
Laboratory API Routes
实验室 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.laboratory import Laboratory
from app.models.bench import TestBench
from app.schemas import LaboratoryCreate, LaboratoryUpdate

router = APIRouter(prefix="/laboratories", tags=["Laboratories"])


@router.get("", response_model=List[dict])
async def get_laboratories(db: Session = Depends(get_db)):
    """获取实验室列表"""
    labs = db.query(Laboratory).all()
    return [lab.to_dict() for lab in labs]


@router.get("/{lab_id}", response_model=dict)
async def get_laboratory(lab_id: str, db: Session = Depends(get_db)):
    """获取实验室详情"""
    lab = db.query(Laboratory).filter(Laboratory.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="实验室不存在")
    
    # 获取实验室内的台架数量
    bench_count = db.query(TestBench).filter(TestBench.laboratory_id == lab_id).count()
    
    result = lab.to_dict()
    result["benchCount"] = bench_count
    return result


@router.post("", response_model=dict)
async def create_laboratory(lab_data: LaboratoryCreate, db: Session = Depends(get_db)):
    """创建实验室"""
    # 检查名称是否重复
    existing = db.query(Laboratory).filter(Laboratory.name == lab_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="实验室名称已存在")
    
    lab = Laboratory(
        name=lab_data.name,
        description=lab_data.description,
        background_image=lab_data.background_image,
        width=lab_data.width,
        height=lab_data.height
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab.to_dict()


@router.put("/{lab_id}", response_model=dict)
async def update_laboratory(
    lab_id: str,
    lab_data: LaboratoryUpdate,
    db: Session = Depends(get_db)
):
    """更新实验室"""
    lab = db.query(Laboratory).filter(Laboratory.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="实验室不存在")
    
    update_data = lab_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lab, key, value)
    
    db.commit()
    db.refresh(lab)
    return lab.to_dict()


@router.delete("/{lab_id}")
async def delete_laboratory(lab_id: str, db: Session = Depends(get_db)):
    """删除实验室"""
    lab = db.query(Laboratory).filter(Laboratory.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="实验室不存在")
    
    # 检查是否还有台架
    bench_count = db.query(TestBench).filter(TestBench.laboratory_id == lab_id).count()
    if bench_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"实验室内还有 {bench_count} 个台架，请先迁移或删除"
        )
    
    db.delete(lab)
    db.commit()
    return {"message": "实验室已删除", "id": lab_id}
