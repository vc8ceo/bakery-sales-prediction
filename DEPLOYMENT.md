# Railway デプロイメント手順書

## 🚀 概要

このドキュメントでは、パン屋売上予測システムをRailwayにデプロイする手順を説明します。

## 📋 事前準備

### 必要なアカウント
- [Railway](https://railway.app) アカウント
- [GitHub](https://github.com) アカウント
- Git がローカルにインストールされていること

### プロジェクトの確認
デプロイ前に以下のファイルが存在することを確認してください：
- `Dockerfile` - コンテナ設定
- `railway.json` - Railway設定
- `.env.example` - 環境変数テンプレート
- `.gitignore` - Git除外設定

## 🔧 デプロイ手順

### 1. GitHubリポジトリの準備

```bash
# プロジェクトディレクトリに移動
cd /path/to/bakery-sales-prediction

# Gitリポジトリを初期化（まだの場合）
git init

# ファイルをステージング
git add .

# 初回コミット
git commit -m "🥖 Initial commit: Bakery sales prediction system with user management

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# GitHubリポジトリを作成し、リモートを追加
git remote add origin https://github.com/YOUR-USERNAME/bakery-sales-prediction.git

# GitHubにプッシュ
git branch -M main
git push -u origin main
```

### 2. Railway プロジェクトの作成

1. [Railway](https://railway.app) にログイン
2. 「New Project」をクリック
3. 「Deploy from GitHub repo」を選択
4. 作成したリポジトリを選択

### 3. PostgreSQL データベースの追加

1. Railway プロジェクトダッシュボードで「Add Service」をクリック
2. 「Database」→「PostgreSQL」を選択
3. データベースが自動的にプロビジョニングされます

### 4. 環境変数の設定

Railway プロジェクトの「Variables」タブで以下の環境変数を設定：

#### 必須環境変数
```bash
# JWT認証用秘密鍵（強力なランダム文字列を生成）
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long

# 環境設定
ENVIRONMENT=production

# フロントエンドURL（デプロイ後のRailway URLに更新）
FRONTEND_URL=https://your-app-name.up.railway.app
```

#### Railway が自動設定する変数
PostgreSQL を追加すると、以下の変数が自動的に設定されます：
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`
- `PGDATABASE`

### 5. デプロイの実行

1. 環境変数設定後、Railwayが自動的にデプロイを開始します
2. デプロイログで進行状況を確認できます
3. 完了すると、アプリケーションURLが表示されます

### 6. デプロイ後の確認

#### ヘルスチェック
```bash
curl https://your-app-name.up.railway.app/api/health
```

期待されるレスポンス：
```json
{
  "message": "パン屋売上予測APIが稼働中です"
}
```

#### データベース接続確認
1. アプリケーションにアクセス
2. ユーザー登録を試行
3. 正常に登録できれば、データベース接続成功

## 🔄 継続的デプロイ

### コード更新手順
```bash
# 変更をコミット
git add .
git commit -m "機能追加: 新しい予測機能

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# GitHubにプッシュ
git push origin main
```

Railway は GitHub との連携により、`main` ブランチへのプッシュで自動デプロイされます。

## 🛠 トラブルシューティング

### よくある問題と解決方法

#### 1. ビルドエラー
**症状**: Docker ビルドが失敗する
**解決方法**:
- `Dockerfile` の構文を確認
- 依存関係ファイル（`requirements.txt`, `package.json`）の確認
- Railway ログでエラー詳細を確認

#### 2. データベース接続エラー
**症状**: アプリケーションがデータベースに接続できない
**解決方法**:
- PostgreSQL サービスが正常に起動しているか確認
- 環境変数が正しく設定されているか確認
- `database.py` の接続設定を確認

#### 3. CORS エラー
**症状**: フロントエンドからAPIにアクセスできない
**解決方法**:
- `FRONTEND_URL` 環境変数が正しく設定されているか確認
- Railway のアプリケーションURL を `FRONTEND_URL` に設定

#### 4. 静的ファイル配信エラー
**症状**: フロントエンドページが表示されない
**解決方法**:
- Docker ビルド時にフロントエンドが正しくビルドされているか確認
- `static` ディレクトリが存在するか確認

### ログの確認方法
```bash
# Railway CLI をインストール（オプション）
npm install -g @railway/cli

# ログイン
railway login

# ログを表示
railway logs
```

## 📊 監視とメンテナンス

### メトリクス監視
Railway ダッシュボードで以下を監視：
- CPU使用率
- メモリ使用量
- ネットワーク使用量
- データベース接続数

### バックアップ
- PostgreSQL の自動バックアップはRailwayが提供
- 追加のバックアップが必要な場合は、定期的にデータエクスポートを実行

### スケーリング
トラフィック増加時は Railway ダッシュボードからリソースを調整可能

## 🔐 セキュリティ

### 本番環境での注意点
1. **強力な SECRET_KEY の使用**
   ```bash
   # Python で強力なキーを生成
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **環境変数の適切な管理**
   - 機密情報は `.env` ファイルではなく Railway の環境変数で管理
   - `.env.example` には実際の値を含めない

3. **HTTPS の確認**
   - Railway は自動的に HTTPS を提供
   - 独自ドメインを使用する場合も HTTPS を確保

## 📞 サポート

### 問題が解決しない場合
1. Railway [ドキュメント](https://docs.railway.app) を確認
2. Railway [Discord コミュニティ](https://discord.gg/railway) で質問
3. プロジェクトの Issue を GitHub で作成

---

**🎉 デプロイ完了後、あなたのパン屋売上予測システムが世界中からアクセス可能になります！**