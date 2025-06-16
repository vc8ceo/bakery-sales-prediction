from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import os

# Railway PostgreSQLの環境変数を優先的に使用
if all(key in os.environ for key in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']):
    DATABASE_URL = f"postgresql://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}@{os.environ['PGHOST']}:{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
else:
    # 環境変数から接続情報を取得
    DATABASE_URL = config(
        'DATABASE_URL', 
        default='postgresql://bakery_user:bakery_pass@localhost/bakery_db'
    )

# 開発環境ではSQLiteを使用
if os.getenv('ENVIRONMENT') == 'development':
    DATABASE_URL = "sqlite:///./bakery_sales.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """データベースセッション取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """テーブル作成"""
    Base.metadata.create_all(bind=engine)