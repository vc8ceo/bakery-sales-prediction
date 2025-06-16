# パン屋売上予測システム

POSレジデータと天気予報データを活用した次営業日の売上・来店客数予測Webアプリケーション

## 機能
- CSVデータ読込・前処理（Shift_JIS対応）
- 天気予報API連携
- 機械学習による売上・来店客数予測
- Web UI による予測結果表示

## 技術スタック
- **バックエンド**: Python, FastAPI, scikit-learn, pandas
- **フロントエンド**: React, TypeScript
- **天気API**: Livedoor Weather互換API

## プロジェクト構造
```
bakery-sales-prediction/
├── backend/           # Python FastAPI サーバー
│   ├── app/          # アプリケーションコード
│   └── tests/        # テストコード
├── frontend/         # React アプリケーション
│   ├── src/          # ソースコード
│   └── public/       # 静的ファイル
├── data/            # データファイル
│   ├── raw/         # 元データ
│   └── processed/   # 前処理済みデータ
├── models/          # 機械学習モデル
│   ├── trained/     # 学習済みモデル
│   └── configs/     # モデル設定
└── README.md
```

## 🚀 デプロイ

### Railway へのデプロイ
詳細な手順は [DEPLOYMENT.md](./DEPLOYMENT.md) を参照してください。

#### 簡単な手順
1. GitHubリポジトリにプッシュ
2. Railway でプロジェクトを作成
3. PostgreSQL を追加
4. 環境変数を設定
5. 自動デプロイ完了！

### 必要な環境変数
```bash
SECRET_KEY=your-super-secret-jwt-key
ENVIRONMENT=production
FRONTEND_URL=https://your-app.up.railway.app
```

## 💻 ローカル開発

### 開発環境のセットアップ
```bash
# データベース起動（PostgreSQL）
docker run --name bakery-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# 環境変数設定
export DATABASE_URL="postgresql://postgres:password@localhost/bakery_db"
export SECRET_KEY="your-secret-key-here"
export ENVIRONMENT="development"
```

### アプリケーション起動
1. **バックエンド**: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
2. **フロントエンド**: `cd frontend && npm install && npm start`

アクセス:
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs