from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ユーザー関連スキーマ
class UserBase(BaseModel):
    email: EmailStr
    username: str
    store_name: Optional[str] = None
    postal_code: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    store_name: Optional[str] = None
    postal_code: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 認証関連スキーマ
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# データ関連スキーマ
class UserDataResponse(BaseModel):
    id: int
    date: datetime
    weather: Optional[str]
    sales: float
    customers: int
    avg_spending: Optional[float]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class UserDataStats(BaseModel):
    total_records: int
    date_range: dict
    sales_stats: dict
    customers_stats: dict
    weather_distribution: dict

# 予測履歴スキーマ
class PredictionHistoryResponse(BaseModel):
    id: int
    prediction_date: datetime
    predicted_sales: float
    predicted_customers: int
    weather_condition: Optional[str]
    temperature: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 予測リクエスト（ユーザー用）
class UserPredictionRequest(BaseModel):
    date: str
    postal_code: Optional[str] = None  # ユーザーのデフォルト郵便番号を使用

# ダッシュボード統計
class DashboardStats(BaseModel):
    total_data_points: int
    date_range: dict
    latest_prediction: Optional[PredictionHistoryResponse]
    model_status: dict
    sales_trend: List[dict]
    weather_impact: dict