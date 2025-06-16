import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Grid,
  Alert,
  Divider,
  InputAdornment
} from '@mui/material';
import { Store, LocationOn, Person, Lock } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const UserSettings: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [formData, setFormData] = useState({
    username: user?.username || '',
    store_name: user?.store_name || '',
    postal_code: user?.postal_code || '',
  });
  const [passwordData, setPasswordData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmitProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    // 郵便番号の検証
    if (formData.postal_code && !/^\d{7}$/.test(formData.postal_code)) {
      setError('郵便番号は7桁の数字で入力してください');
      setLoading(false);
      return;
    }

    try {
      await updateUser(formData);
      setMessage('プロフィールを更新しました');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    // パスワードの検証
    if (passwordData.password.length < 6) {
      setError('パスワードは6文字以上で入力してください');
      setLoading(false);
      return;
    }

    if (passwordData.password !== passwordData.confirmPassword) {
      setError('パスワードが一致しません');
      setLoading(false);
      return;
    }

    try {
      await updateUser({ password: passwordData.password });
      setMessage('パスワードを更新しました');
      setPasswordData({ password: '', confirmPassword: '' });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        ユーザー設定
      </Typography>

      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* プロフィール設定 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                プロフィール設定
              </Typography>

              <Box component="form" onSubmit={handleSubmitProfile}>
                <TextField
                  fullWidth
                  name="username"
                  label="ユーザー名"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  name="store_name"
                  label="店舗名"
                  value={formData.store_name}
                  onChange={handleChange}
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Store />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  name="postal_code"
                  label="郵便番号"
                  value={formData.postal_code}
                  onChange={handleChange}
                  placeholder="1000001"
                  helperText="7桁の数字で入力（例：1000001）"
                  sx={{ mb: 3 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LocationOn />
                      </InputAdornment>
                    ),
                  }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  fullWidth
                >
                  {loading ? '更新中...' : 'プロフィールを更新'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* パスワード変更 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                パスワード変更
              </Typography>

              <Box component="form" onSubmit={handleSubmitPassword}>
                <TextField
                  fullWidth
                  name="password"
                  type="password"
                  label="新しいパスワード"
                  value={passwordData.password}
                  onChange={handlePasswordChange}
                  required
                  sx={{ mb: 2 }}
                  helperText="6文字以上で入力してください"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  name="confirmPassword"
                  type="password"
                  label="パスワード確認"
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordChange}
                  required
                  sx={{ mb: 3 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock />
                      </InputAdornment>
                    ),
                  }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  fullWidth
                >
                  {loading ? '更新中...' : 'パスワードを変更'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* アカウント情報 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                アカウント情報
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography color="text.secondary">メールアドレス</Typography>
                  <Typography variant="body1">{user?.email}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography color="text.secondary">アカウント作成日</Typography>
                  <Typography variant="body1">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('ja-JP') : '-'}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserSettings;