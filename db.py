from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 資料庫使用 SQLite 
DATABASE_URL = "sqlite:///./vouchers.db"


class Base(DeclarativeBase):
    """所有 ORM Model 都要繼承的基底類別"""
    pass


# echo=True 會顯示 SQL，除錯時可以改成 True
engine = create_engine(DATABASE_URL, echo=False, future=True)

# API 裡會用到的 Session 工廠
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)
