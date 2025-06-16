from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """ユーザーテーブル"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    store_name = Column(String(200), nullable=True)  # 店舗名
    postal_code = Column(String(10), nullable=True)  # 郵便番号
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーション
    user_data = relationship("UserData", back_populates="user", cascade="all, delete-orphan")
    prediction_history = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")

class UserData(Base):
    """ユーザーごとのPOSデータ"""
    __tablename__ = "user_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 元のCSVデータカラム
    store_id = Column(String(50), nullable=True)
    store_name = Column(String(200), nullable=True)
    date = Column(DateTime, nullable=False)
    weather = Column(String(50), nullable=True)
    sales = Column(Float, nullable=False)
    target_achievement_rate = Column(Float, nullable=True)
    yoy_same_day_ratio = Column(Float, nullable=True)
    customers = Column(Integer, nullable=False)
    avg_spending = Column(Float, nullable=True)
    labor_cost_rate = Column(Float, nullable=True)
    cost_rate = Column(Float, nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーション
    user = relationship("User", back_populates="user_data")

class PredictionHistory(Base):
    """予測履歴テーブル"""
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    prediction_date = Column(DateTime, nullable=False)  # 予測対象日
    predicted_sales = Column(Float, nullable=False)
    predicted_customers = Column(Integer, nullable=False)
    weather_condition = Column(String(100), nullable=True)
    temperature = Column(Float, nullable=True)
    confidence_lower_sales = Column(Float, nullable=True)
    confidence_upper_sales = Column(Float, nullable=True)
    confidence_lower_customers = Column(Float, nullable=True)
    confidence_upper_customers = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーション
    user = relationship("User", back_populates="prediction_history")

class UserModel(Base):
    """ユーザーごとの学習済みモデル"""
    __tablename__ = "user_models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    model_name = Column(String(100), nullable=False)  # sales_model, customers_model
    model_path = Column(String(500), nullable=False)  # ファイルパス
    model_metrics = Column(Text, nullable=True)  # JSON形式でメトリクスを保存
    training_data_count = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーション
    user = relationship("User")