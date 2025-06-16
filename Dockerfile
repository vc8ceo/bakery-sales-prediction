# マルチステージビルド用のDockerfile
FROM node:18-alpine as frontend-builder

# フロントエンド ビルド
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Python バックエンド
FROM python:3.11-slim

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# Python 依存関係をインストール
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY backend/ ./

# フロントエンドのビルド結果をコピー
COPY --from=frontend-builder /app/frontend/build ./static

# モデル保存用ディレクトリを作成
RUN mkdir -p models/users models/trained

# アプリケーションを起動
EXPOSE $PORT

# Railwayでの起動コマンド（環境変数PORTを使用）
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT