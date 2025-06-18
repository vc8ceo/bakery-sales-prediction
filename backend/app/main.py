from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np
import pickle
import os
from sqlalchemy.orm import Session

from .models import SalesPredictionModel
from .data_processor import DataProcessor
from .weather_service import WeatherService
from .database import get_db, create_tables
from .auth import get_current_active_user
from .user_models import User, PredictionHistory
from .user_data_processor import UserDataProcessor
from .user_routes import router as auth_router, user_router
from .schemas import UserPredictionRequest

app = FastAPI(
    title="パン屋売上予測API",
    description="POSレジデータと天気予報を使った売上・来店客数予測システム",
    version="1.0.0"
)

# CORS設定
origins = [
    "http://localhost:3000",
    "http://localhost:3002", 
    "http://localhost:3007",
    "http://127.0.0.1:3007"
]

# 本番環境では環境変数からフロントエンドURLを追加
frontend_url = os.getenv('FRONTEND_URL')
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター追加
app.include_router(auth_router)
app.include_router(user_router)

# 静的ファイル配信（本番環境用）
# 静的ファイルとフロントエンド配信
# 複数の場所をチェック
static_locations = ["static", "app/static", "./static", "./app/static"]
static_dir = None

for location in static_locations:
    if os.path.exists(location):
        static_dir = location
        break

if static_dir:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"message": "フロントエンドファイルが見つかりません", "static_dir": static_dir, "files": os.listdir(static_dir) if os.path.exists(static_dir) else []}
    
    @app.get("/{path:path}", include_in_schema=False)
    async def serve_frontend_routes(path: str):
        # API、docs、redocパスはスキップ
        if path.startswith("api/") or path.startswith("docs") or path.startswith("redoc"):
            raise HTTPException(status_code=404, detail="Not Found")
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend files not found")
else:
    @app.get("/", include_in_schema=False)
    async def no_frontend():
        return {
            "message": "フロントエンドが設定されていません", 
            "api_docs": "/docs",
            "current_dir": os.getcwd(),
            "files": os.listdir("."),
            "checked_locations": static_locations
        }

# グローバル変数
data_processor = DataProcessor()
weather_service = WeatherService()
prediction_model = None

class PredictionRequest(BaseModel):
    date: str
    postal_code: Optional[str] = "1000001"  # 東京都千代田区

class PredictionResponse(BaseModel):
    date: str
    predicted_sales: float
    predicted_customers: int
    weather_forecast: dict
    confidence_interval: dict

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    global prediction_model
    
    # データベースの初期化
    create_tables()
    print("データベーステーブルを初期化しました")
    
    # 学習済みモデルの読み込み（存在する場合）
    model_path = "models/trained/sales_model.pkl"
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                prediction_model = pickle.load(f)
            print("学習済みモデルを読み込みました")
        except Exception as e:
            print(f"モデル読み込みエラー: {e}")

@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {"message": "パン屋売上予測APIが稼働中です"}

@app.post("/api/upload-data")
async def upload_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """CSVデータのアップロードと前処理（ユーザー専用）"""
    try:
        # ファイルの保存
        contents = await file.read()
        
        # ユーザー専用データ処理
        user_processor = UserDataProcessor(current_user.id, db)
        df = user_processor.process_user_csv_data(contents)
        
        # 基本統計情報
        stats = user_processor.get_user_stats()
        
        return {
            "message": "データが正常にアップロードされました",
            "records_count": len(df),
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d'),
                "end": df['date'].max().strftime('%Y-%m-%d')
            },
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"データ処理エラー: {str(e)}")

@app.post("/api/train-model")
async def train_model(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """機械学習モデルの訓練（ユーザー専用）"""
    try:
        # ユーザー専用データ処理
        user_processor = UserDataProcessor(current_user.id, db)
        
        # データの確認
        if not user_processor.has_data():
            raise HTTPException(status_code=400, detail="訓練データがありません。まずCSVファイルをアップロードしてください。")
        
        # モデル訓練
        metrics = user_processor.train_user_model()
        
        return {
            "message": "モデル訓練が完了しました",
            "metrics": metrics,
            "model_saved": f"models/users/{current_user.id}/sales_model.pkl"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"モデル訓練エラー: {str(e)}")

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_sales(
    request: UserPredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """売上予測（ユーザー専用）"""
    try:
        # ユーザー専用データ処理
        user_processor = UserDataProcessor(current_user.id, db)
        
        # モデルの確認
        if not user_processor.has_model():
            raise HTTPException(status_code=400, detail="予測モデルが訓練されていません。")
        
        # 日付解析
        target_date = datetime.strptime(request.date, '%Y-%m-%d')
        
        # 郵便番号設定（リクエストまたはユーザーのデフォルト）
        postal_code = request.postal_code or current_user.postal_code or "1000001"
        
        # 天気予報取得
        weather_data = await weather_service.get_weather_forecast(postal_code)
        
        # 予測実行
        sales_pred, customers_pred, confidence = user_processor.predict_sales(target_date, weather_data)
        
        # 予測履歴を保存
        prediction_history = PredictionHistory(
            user_id=current_user.id,
            prediction_date=target_date,
            predicted_sales=sales_pred,
            predicted_customers=customers_pred,
            weather_condition=weather_data.get('weather'),
            temperature=weather_data.get('temperature'),
            confidence_lower_sales=confidence.get('sales_lower'),
            confidence_upper_sales=confidence.get('sales_upper'),
            confidence_lower_customers=confidence.get('customers_lower'),
            confidence_upper_customers=confidence.get('customers_upper')
        )
        db.add(prediction_history)
        db.commit()
        
        return PredictionResponse(
            date=request.date,
            predicted_sales=float(sales_pred),
            predicted_customers=int(customers_pred),
            weather_forecast=weather_data,
            confidence_interval=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測エラー: {str(e)}")

@app.get("/api/model-status")
async def get_model_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """モデル状況確認（ユーザー専用）"""
    user_processor = UserDataProcessor(current_user.id, db)
    
    return {
        "model_trained": user_processor.has_model(),
        "data_loaded": user_processor.has_data(),
        "model_path": f"models/users/{current_user.id}/sales_model.pkl" if user_processor.has_model() else None
    }

@app.get("/api/data-stats")
async def get_data_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """データ統計情報（ユーザー専用）"""
    user_processor = UserDataProcessor(current_user.id, db)
    
    if not user_processor.has_data():
        raise HTTPException(status_code=400, detail="データがロードされていません")
    
    return user_processor.get_user_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)