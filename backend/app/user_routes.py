from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from .database import get_db
from .auth import (
    AuthService, authenticate_user, create_user, get_current_active_user,
    get_user_by_email, get_user_by_username
)
from .user_models import User, UserData, PredictionHistory
from .schemas import (
    UserCreate, UserResponse, UserUpdate, LoginRequest, TokenResponse,
    UserDataResponse, PredictionHistoryResponse, DashboardStats
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """ユーザー登録"""
    # 既存ユーザーチェック
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=400,
            detail="このメールアドレスは既に登録されています"
        )
    
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=400,
            detail="このユーザー名は既に使用されています"
        )
    
    # ユーザー作成
    user = create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        store_name=user_data.store_name,
        postal_code=user_data.postal_code
    )
    
    # トークン生成
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """ログイン"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # トークン生成
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """現在のユーザー情報取得"""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """現在のユーザー情報更新"""
    # ユーザー名の重複チェック
    if user_update.username and user_update.username != current_user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="このユーザー名は既に使用されています"
            )
        current_user.username = user_update.username
    
    # その他の情報更新
    if user_update.store_name is not None:
        current_user.store_name = user_update.store_name
    if user_update.postal_code is not None:
        current_user.postal_code = user_update.postal_code
    if user_update.password:
        current_user.hashed_password = AuthService.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

# ユーザーデータ管理用ルーター
user_router = APIRouter(prefix="/api/user", tags=["user_data"])

@user_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ダッシュボード統計情報取得"""
    # ユーザーのデータ統計
    user_data = db.query(UserData).filter(UserData.user_id == current_user.id).all()
    
    if not user_data:
        return DashboardStats(
            total_data_points=0,
            date_range={"start": None, "end": None},
            latest_prediction=None,
            model_status={"trained": False, "data_loaded": False},
            sales_trend=[],
            weather_impact={}
        )
    
    # 日付範囲
    dates = [data.date for data in user_data]
    date_range = {
        "start": min(dates).strftime('%Y-%m-%d'),
        "end": max(dates).strftime('%Y-%m-%d')
    }
    
    # 最新の予測
    latest_prediction = db.query(PredictionHistory)\
        .filter(PredictionHistory.user_id == current_user.id)\
        .order_by(PredictionHistory.created_at.desc())\
        .first()
    
    # 売上トレンド（月別）
    sales_by_month = {}
    for data in user_data:
        month_key = data.date.strftime('%Y-%m')
        if month_key not in sales_by_month:
            sales_by_month[month_key] = []
        sales_by_month[month_key].append(data.sales)
    
    sales_trend = [
        {"month": month, "avg_sales": sum(sales) / len(sales)}
        for month, sales in sales_by_month.items()
    ]
    
    # 天気の影響
    weather_impact = {}
    for data in user_data:
        if data.weather:
            if data.weather not in weather_impact:
                weather_impact[data.weather] = []
            weather_impact[data.weather].append(data.sales)
    
    weather_impact = {
        weather: sum(sales) / len(sales)
        for weather, sales in weather_impact.items()
    }
    
    return DashboardStats(
        total_data_points=len(user_data),
        date_range=date_range,
        latest_prediction=PredictionHistoryResponse.from_orm(latest_prediction) if latest_prediction else None,
        model_status={"trained": True, "data_loaded": True},  # 実際の実装では動的に取得
        sales_trend=sales_trend,
        weather_impact=weather_impact
    )

@user_router.get("/data", response_model=List[UserDataResponse])
async def get_user_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """ユーザーデータ一覧取得"""
    user_data = db.query(UserData)\
        .filter(UserData.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [UserDataResponse.from_orm(data) for data in user_data]

@user_router.get("/predictions", response_model=List[PredictionHistoryResponse])
async def get_prediction_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """予測履歴取得"""
    predictions = db.query(PredictionHistory)\
        .filter(PredictionHistory.user_id == current_user.id)\
        .order_by(PredictionHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [PredictionHistoryResponse.from_orm(pred) for pred in predictions]

@user_router.delete("/data")
async def delete_user_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ユーザーデータ削除"""
    try:
        # ユーザー専用データ処理クラスで完全削除
        from .user_data_processor import UserDataProcessor
        user_processor = UserDataProcessor(current_user.id, db)
        user_processor.delete_user_data()
        
        return {"message": "ユーザーデータが完全に削除されました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ削除エラー: {str(e)}")