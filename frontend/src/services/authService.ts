import { LoginRequest, RegisterRequest, AuthResponse, User, UserUpdateRequest } from '../types';

class AuthService {
  private readonly API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  private tokenKey = 'bakery_auth_token';

  // ローカルストレージからトークンを取得
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // ローカルストレージにトークンを保存
  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  // トークンを削除
  removeToken(): void {
    localStorage.removeItem(this.tokenKey);
  }

  // 認証ヘッダーを取得
  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // ユーザー登録
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'ユーザー登録に失敗しました');
    }

    const authResponse: AuthResponse = await response.json();
    this.setToken(authResponse.access_token);
    return authResponse;
  }

  // ログイン
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'ログインに失敗しました');
    }

    const authResponse: AuthResponse = await response.json();
    this.setToken(authResponse.access_token);
    return authResponse;
  }

  // ログアウト
  logout(): void {
    this.removeToken();
  }

  // 現在のユーザー情報を取得
  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${this.API_BASE_URL}/api/auth/me`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.removeToken();
        throw new Error('認証が無効です');
      }
      const error = await response.json();
      throw new Error(error.detail || 'ユーザー情報の取得に失敗しました');
    }

    return response.json();
  }

  // ユーザー情報を更新
  async updateUser(data: UserUpdateRequest): Promise<User> {
    const response = await fetch(`${this.API_BASE_URL}/api/auth/me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'ユーザー情報の更新に失敗しました');
    }

    return response.json();
  }

  // ログイン状態をチェック
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }
}

export const authService = new AuthService();