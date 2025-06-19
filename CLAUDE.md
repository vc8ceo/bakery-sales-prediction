# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

パン屋売上予測システム - POSレジデータと天気予報を活用した機械学習による売上・来店客数予測Webアプリケーション

### 現在のディレクトリ構造

```
bakery-sales-prediction/
├── backend/                           # Python FastAPI バックエンド
│   ├── app/                          # アプリケーションコア
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI メインアプリ・ルーティング
│   │   ├── auth.py                   # JWT認証・ユーザー管理
│   │   ├── database.py               # DB接続・環境自動検出
│   │   ├── models.py                 # 機械学習モデル定義
│   │   ├── user_models.py            # SQLAlchemy データベースモデル
│   │   ├── schemas.py                # Pydantic スキーマ定義
│   │   ├── user_routes.py            # ユーザー関連APIルーター
│   │   ├── data_processor.py         # データ前処理・特徴量エンジニアリング
│   │   ├── user_data_processor.py    # ユーザー専用データ処理クラス
│   │   └── weather_service.py        # 天気予報API連携
│   ├── models/                       # 機械学習モデル保存
│   │   ├── users/                    # ユーザー別モデル
│   │   └── trained/                  # 共通学習済みモデル
│   ├── requirements.txt              # Python依存関係
│   ├── tests/                        # テストコード
│   └── venv_win/                     # Windows仮想環境
├── frontend/                         # React TypeScript フロントエンド
│   ├── src/
│   │   ├── components/               # UIコンポーネント
│   │   │   ├── AuthPage.tsx          # 認証ページ（ログイン・登録切り替え）
│   │   │   ├── LoginForm.tsx         # ログインフォーム
│   │   │   ├── RegisterForm.tsx      # ユーザー登録フォーム
│   │   │   ├── UserDashboard.tsx     # ユーザーダッシュボード・統計表示
│   │   │   ├── UserSettings.tsx      # ユーザー設定（店舗情報・郵便番号）
│   │   │   ├── DataUpload.tsx        # CSVアップロード・モデル訓練
│   │   │   ├── DataStatistics.tsx    # データ統計可視化
│   │   │   ├── ModelStatus.tsx       # モデル状況表示
│   │   │   ├── PredictionForm.tsx    # 売上予測フォーム
│   │   │   └── PredictionResults.tsx # 予測結果表示
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx       # React認証コンテキスト
│   │   ├── services/
│   │   │   ├── apiService.ts         # メインAPI通信クライアント
│   │   │   └── authService.ts        # 認証専用API
│   │   └── types/
│   │       └── index.ts              # TypeScript型定義
│   ├── build/                        # ビルド出力
│   ├── package.json                  # Node.js依存関係
│   └── tsconfig.json                 # TypeScript設定
├── static/                           # 本番用静的ファイル（frontend/buildのコピー）
├── data/                             # サンプルデータ
├── .env.example                      # 環境変数テンプレート
├── Dockerfile                        # マルチステージビルド用
├── railway.json                      # Railway設定
├── システム設計書.md                    # 詳細設計文書
└── README.md                         # プロジェクト説明
```

### 技術スタック

**バックエンド**
- Python 3.11 + FastAPI 0.104.1
- SQLAlchemy 2.0 (PostgreSQL/SQLite自動切り替え)
- scikit-learn 1.3.2 + XGBoost 2.0.2
- JWT認証 (python-jose + passlib)
- pandas 2.1.3, numpy 1.24.3

**フロントエンド**  
- React 18.2 + TypeScript 4.7
- Material-UI 5.14 (コンポーネント・テーマ)
- Axios (API通信・インターセプター)
- Recharts 2.8 (グラフ・チャート)
- date-fns 2.30 (日付処理)

**インフラ・デプロイ**
- Docker (マルチステージビルド)
- Railway (PaaS・PostgreSQL)
- GitHub (リポジトリ・自動デプロイ)

## アーキテクチャ設計

### ユーザー中心データ分離
- **完全ユーザー分離**: 全データがuser_idで分離
- **個別モデル**: ユーザーごとの機械学習モデル（`models/users/{user_id}/`）
- **専用統計**: ユーザー別ダッシュボード・予測履歴

### 認証・セキュリティ
- **JWT認証**: すべての保護エンドポイントでBearer認証
- **自動トークン管理**: Axiosインターセプターで自動付与
- **401自動ログアウト**: 認証エラー時の自動状態クリア

### データベース戦略
```python
# 環境自動検出ロジック (database.py)
if PGHOST and PGPORT:          # Railway PostgreSQL
    use_postgresql()
elif ENVIRONMENT == "development":  # 開発環境
    use_sqlite()
else:                          # 手動設定
    use_database_url()
```

### デプロイメント統合
- **開発時**: React(:3000) + FastAPI(:8000) 分離
- **本番時**: FastAPI単体でReact静的ファイル配信
- **SPAルーティング**: 非APIパスを全てindex.htmlにルーティング

## API設計

### エンドポイント構造
全APIエンドポイントは`/api/`プレフィックスで静的ファイル配信と分離：

#### 認証API (`/api/auth/*`)
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/me` - 現在のユーザー情報取得
- `PUT /api/auth/me` - ユーザー情報更新

#### ユーザーデータAPI (`/api/user/*`)
- `GET /api/user/dashboard` - ダッシュボード統計
- `GET /api/user/data` - ユーザーデータ一覧
- `GET /api/user/predictions` - 予測履歴
- `DELETE /api/user/data` - ユーザーデータ削除

#### コア機能API (`/api/*`)
- `GET /api/health` - ヘルスチェック
- `POST /api/upload-data` - CSVアップロード
- `POST /api/train-model` - モデル訓練
- `POST /api/predict` - 売上予測
- `GET /api/model-status` - モデル状況確認
- `GET /api/data-stats` - データ統計情報

### 認証設計
- **JWT認証**: すべての保護エンドポイントでBearer認証
- **自動ログアウト**: 401レスポンスで自動ログアウト
- **トークンインターセプター**: Axiosでリクエスト時自動トークン付与

## 機械学習パイプライン

### データ処理フロー
1. **CSVアップロード**: Shift_JISエンコーディング対応
2. **データ前処理**: 列名マッピング（日本語→英語）
3. **特徴量エンジニアリング**: 時系列特徴量（曜日、季節、移動平均）
4. **天気データ統合**: Livedoor Weather API連携

### モデル訓練
- **アルゴリズム**: RandomForest（売上・客数別々のモデル）
- **保存場所**: `models/users/{user_id}/sales_model.pkl`
- **メタデータ**: `user_models`テーブルで管理
- **評価指標**: MAE, MSE, RMSE, R², MAPE

### 予測実行
- **入力**: 日付、郵便番号（天気予報取得用）
- **出力**: 売上・客数予測値 + 信頼区間
- **履歴保存**: `prediction_history`テーブル

## 開発・デプロイメント

### ローカル開発セットアップ
```bash
# データベース起動（PostgreSQL）
docker run --name bakery-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# 環境変数設定
export DATABASE_URL="postgresql://postgres:password@localhost/bakery_db"
export SECRET_KEY="your-secret-key-here"
export ENVIRONMENT="development"

# バックエンド起動
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# フロントエンド起動（別ターミナル）
cd frontend
npm install
npm start  # port 3000
```

### 本番ビルド・デプロイ
```bash
# フロントエンドビルド
cd frontend
npm run build

# 静的ファイルコピー
xcopy /E /I /Y frontend\build static

# Docker ビルド
docker build -t bakery-app .

# Railway デプロイ
git push origin main  # 自動デプロイ
```

### 環境変数
#### 必須環境変数
- `SECRET_KEY`: JWT署名用秘密鍵
- `ENVIRONMENT`: development/production

#### オプション環境変数
- `DATABASE_URL`: PostgreSQL接続文字列
- `FRONTEND_URL`: CORS許可用フロントエンドURL
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`: Railway PostgreSQL自動設定

## 重要な実装詳細

### CSVデータ処理
- **エンコーディング**: Shift_JIS（日本語CSV対応）
- **列マッピング**: 日本語列名→英語（`data_processor.py`）
- **データ検証**: 型変換・欠損値処理

### 天気連携
- **API**: Livedoor Weather互換
- **郵便番号マッピング**: 日本全国主要都市対応
- **フォールバック**: API障害時のデフォルト天気データ

### フロントエンド状態管理
- **認証**: React Context（グローバル）
- **データ**: ローカル状態 + API通信
- **エラーハンドリング**: 統一エラー表示・401自動ログアウト

### デバッグ機能
- **APIエラーでもタブ有効化**: フロントエンドフォールバック
- **データ削除後の状態リセット**: モデル状況・ローカル状態クリア
- **インラインスクリプト**: HTMLレベルでの動的修正対応

## 最近の重要な修正

### タブ表示問題の解決
- **問題**: CSVアップロード後、データ統計・予測タブが開かない
- **原因**: `/api/model-status`, `/api/data-stats` の404エラー
- **解決**: フロントエンドでAPIエラー時のフォールバック処理追加

### データ削除後の状態リセット
- **問題**: データ削除後にCSVアップロードボタンが非表示
- **解決**: `handleDataDelete`でモデル状況を初期化、DataUploadコンポーネントで状態リセット

### デプロイ課題
- **問題**: Railway デプロイメント失敗
- **対応**: 安定版コミットの使用、段階的修正アプローチ

## プロジェクト状況

### 動作確認済み機能
- ✅ ユーザー認証（登録・ログイン）
- ✅ CSVデータアップロード
- ✅ ダッシュボード表示
- ✅ データ削除・状態リセット
- ✅ 基本的なAPI通信

### 開発中・課題
- ⚠️ Railway デプロイメント安定化
- ⚠️ バックエンドAPIエンドポイント（model-status, data-stats）
- 🔄 モデル訓練・予測機能の完全動作確認

### 技術的考慮事項
- **ファイルシステム**: `models/users/`, `models/trained/` ディレクトリ必須
- **環境検出**: 自動データベース選択ロジック
- **CORS設定**: 開発・本番環境適応
- **静的ファイル配信**: React SPAルーティング対応