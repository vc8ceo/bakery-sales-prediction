from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
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
# Reactビルドファイルをチェック
react_build_dir = "static"
simple_html_mode = True

# Reactアプリの存在確認を緩和
potential_index_files = [
    os.path.join(react_build_dir, "index.html"),
    os.path.join("./static", "index.html"),
    os.path.join("app/static", "index.html")
]

for index_file in potential_index_files:
    if os.path.exists(index_file):
        react_build_dir = os.path.dirname(index_file)
        simple_html_mode = False
        break

if not simple_html_mode:
    app.mount("/static", StaticFiles(directory=react_build_dir), name="static")
    print(f"✅ Reactアプリを配信: {react_build_dir}")
else:
    print("⚠️ Reactアプリが見つかりません。シンプル版で起動します。")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """フロントエンドページを配信"""
    
    if not simple_html_mode:
        # Reactアプリを配信
        return FileResponse(os.path.join(react_build_dir, "index.html"))
    
    # シンプルHTML版を配信
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>パン屋売上予測システム</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            max-width: 800px;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .button {
            display: inline-block;
            padding: 15px 30px;
            background: #ff6b6b;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px 0 rgba(255, 107, 107, 0.4);
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(255, 107, 107, 0.6);
        }
        .api-button {
            background: #4ecdc4;
            box-shadow: 0 4px 15px 0 rgba(78, 205, 196, 0.4);
        }
        .api-button:hover {
            box-shadow: 0 6px 20px 0 rgba(78, 205, 196, 0.6);
        }
        .warning {
            background: #f39c12;
            box-shadow: 0 4px 15px 0 rgba(243, 156, 18, 0.4);
        }
        .warning:hover {
            box-shadow: 0 6px 20px 0 rgba(243, 156, 18, 0.6);
        }
        .status {
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🥖 パン屋売上予測システム</h1>
        <p>POSレジデータと天気予報データを活用した売上・来店客数予測Webアプリケーション</p>
        
        <div>
            <a href="/docs" class="button api-button">📚 API ドキュメント</a>
            <a href="/api/health" class="button">💚 ヘルスチェック</a>
        </div>
        
        <div class="status">
            <h3>⚠️ システム状況</h3>
            <p>✅ バックエンドAPI: 正常稼働中</p>
            <p>⚠️ フロントエンド: シンプル版で稼働中</p>
            <p style="color: #f39c12;">🔧 完全なReactアプリは準備中です</p>
        </div>

        <div class="status">
            <h3>📋 設計書で定義された機能</h3>
            <p>• <strong>ユーザー認証システム</strong>（ログイン・登録）</p>
            <p>• <strong>ユーザーダッシュボード</strong>（統計・予測履歴）</p>
            <p>• <strong>CSVアップロード機能</strong></p>
            <p>• <strong>機械学習モデル訓練</strong></p>
            <p>• <strong>売上予測フォーム</strong></p>
            <p>• <strong>設定管理</strong>（店舗情報・郵便番号）</p>
        </div>

        <div class="status">
            <h3>🛠️ 現在利用可能な機能（API経由）</h3>
            <p>• POST /api/auth/register - ユーザー登録</p>
            <p>• POST /api/auth/login - ログイン</p>
            <p>• GET /api/user/dashboard - ダッシュボード</p>
            <p>• POST /api/upload-data - データアップロード</p>
            <p>• POST /api/train-model - モデル訓練</p>
            <p>• POST /api/predict - 売上予測</p>
        </div>
    </div>

    <script>
        // ヘルスチェック
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                console.log('✅ API正常稼働:', data);
            })
            .catch(error => {
                console.error('❌ API Error:', error);
            });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/{path:path}", include_in_schema=False)
async def serve_frontend_routes(path: str):
    """React Router対応"""
    # API、docs、redocパスはスキップ
    if path.startswith("api/") or path.startswith("docs") or path.startswith("redoc"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    if not simple_html_mode:
        # Reactアプリの場合、SPAルーティング対応
        return FileResponse(os.path.join(react_build_dir, "index.html"))
    else:
        # シンプル版の場合はルートにリダイレクト
        raise HTTPException(status_code=404, detail="Page not found")

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