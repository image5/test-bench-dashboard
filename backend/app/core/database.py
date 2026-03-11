"""
Database Configuration
数据库配置 - SQLite (Windows友好)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "test_bench.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# SQLite 数据库 URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 特殊配置
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
BaseModel = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    from app.models import BenchType, BenchStatus
    BaseModel.metadata.create_all(bind=engine)
