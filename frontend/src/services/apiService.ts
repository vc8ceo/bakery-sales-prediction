import axios from 'axios';
import { ModelStatusType, PredictionResult, DataStats, UploadResult, TrainResult, DashboardStats, PredictionHistoryItem } from '../types';
import { authService } from './authService';

// 本番環境では相対URLを使用、開発環境ではlocalhost
const API_BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター：認証トークンを自動追加
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const apiService = {
  // ヘルスチェック
  async healthCheck(): Promise<{message: string}> {
    const response = await api.get('/api/health');
    return response.data;
  },

  // データアップロード
  async uploadData(file: File): Promise<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/upload-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // モデル訓練
  async trainModel(): Promise<TrainResult> {
    const response = await api.post('/api/train-model');
    return response.data;
  },

  // 予測実行
  async predict(date: string, postalCode?: string): Promise<PredictionResult> {
    const response = await api.post('/api/predict', {
      date,
      postal_code: postalCode,
    });
    return response.data;
  },

  // ダッシュボード統計取得
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get('/api/user/dashboard');
    return response.data;
  },

  // 予測履歴取得
  async getPredictionHistory(skip: number = 0, limit: number = 50): Promise<PredictionHistoryItem[]> {
    const response = await api.get('/api/user/predictions', {
      params: { skip, limit },
    });
    return response.data;
  },

  // ユーザーデータ削除
  async deleteUserData(): Promise<{message: string}> {
    const response = await api.delete('/api/user/data');
    return response.data;
  },

  // モデル状況取得
  async getModelStatus(): Promise<ModelStatusType> {
    const response = await api.get('/api/model-status');
    return response.data;
  },

  // データ統計情報取得
  async getDataStats(): Promise<DataStats> {
    const response = await api.get('/api/data-stats');
    return response.data;
  },
};

// エラーハンドリング
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'APIエラーが発生しました';
    
    if (error.response) {
      // 認証エラーの場合、自動ログアウト
      if (error.response.status === 401) {
        authService.logout();
        window.location.reload();
        return Promise.reject(new Error('認証が無効です。再度ログインしてください。'));
      }
      
      // サーバーからのエラーレスポンス
      if (error.response.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response.data?.message) {
        errorMessage = error.response.data.message;
      }
    } else if (error.request) {
      // ネットワークエラー
      errorMessage = 'サーバーに接続できませんでした';
    }
    
    return Promise.reject(new Error(errorMessage));
  }
);