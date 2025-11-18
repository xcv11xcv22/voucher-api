import os
from sqlalchemy import create_engine
from sqlalchemy.orm import  DeclarativeBase

class Base(DeclarativeBase):
    """所有 ORM Model 都要繼承的基底類別"""
    pass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 預設正式用的 DB 檔案路徑
default_db_path = os.path.join(DATA_DIR, "vouchers.db")
default_db_url = f"sqlite:///{default_db_path}"

# 優先使用環境變數 DATABASE_URL，沒設就用預設
DATABASE_URL = os.getenv("DATABASE_URL", default_db_url)

engine = create_engine(
    DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False},
)