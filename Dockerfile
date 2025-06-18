# マルチステージビルド用のDockerfile
FROM node:18-alpine as frontend-builder

# フロントエンド ビルド
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./

# デバッグ情報を追加
RUN echo "=== フロントエンドビルド開始 ===" && ls -la

# フロントエンドをビルド
RUN npm run build

# ビルド結果を確認
RUN echo "=== ビルド完了後 ===" && ls -la build/

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

# 静的ファイルが正しくコピーされたか確認
RUN echo "=== 静的ファイル確認 ===" && ls -la static/ || echo "静的ディレクトリが存在しません"

# モデル保存用ディレクトリを作成
RUN mkdir -p models/users models/trained

# アプリケーションを起動
EXPOSE 8000

# 起動スクリプトを作成
RUN echo '#!/bin/bash\nuvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh
RUN chmod +x /app/start.sh

# Railwayでの起動コマンド
CMD ["/app/start.sh"]