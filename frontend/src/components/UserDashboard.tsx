import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  History,
  CloudDownload,
  Delete,
  Store,
  LocationOn,
  Person
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';

import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import { DashboardStats, PredictionHistoryItem } from '../types';

interface UserDashboardProps {
  onDeleteData?: () => Promise<{ message: string }>;
}

const UserDashboard: React.FC<UserDashboardProps> = ({ onDeleteData }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [predictionHistory, setPredictionHistory] = useState<PredictionHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [dashboardStats, predictions] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getPredictionHistory(0, 10),
      ]);

      setStats(dashboardStats);
      setPredictionHistory(predictions);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteData = async () => {
    if (window.confirm('すべてのデータを削除しますか？この操作は取り消せません。')) {
      try {
        if (onDeleteData) {
          const result = await onDeleteData();
          alert(result.message);
          await loadDashboardData();
        } else {
          // フォールバック：直接APIを呼び出し
          await apiService.deleteUserData();
          await loadDashboardData();
          alert('データを削除しました');
        }
      } catch (err: any) {
        setError(err.message);
      }
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'yyyy/MM/dd', { locale: ja });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>読み込み中...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Grid container spacing={3}>
        {/* ユーザー情報カード */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center">
                  <Person sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      {user?.store_name || user?.username} さんのダッシュボード
                    </Typography>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Chip
                        icon={<Store />}
                        label={user?.store_name || '店舗名未設定'}
                        variant="outlined"
                      />
                      <Chip
                        icon={<LocationOn />}
                        label={user?.postal_code ? `〒${user.postal_code}` : '郵便番号未設定'}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </Box>
                <Tooltip title="データを削除">
                  <IconButton color="error" onClick={handleDeleteData}>
                    <Delete />
                  </IconButton>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 統計カード */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Assessment sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    データ件数
                  </Typography>
                  <Typography variant="h4">
                    {stats?.total_data_points || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp sx={{ mr: 2, fontSize: 40, color: 'success.main' }} />
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    モデル状況
                  </Typography>
                  <Chip
                    label={stats?.model_status.trained ? 'モデル訓練済み' : '未訓練'}
                    color={stats?.model_status.trained ? 'success' : 'default'}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <History sx={{ mr: 2, fontSize: 40, color: 'info.main' }} />
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    予測回数
                  </Typography>
                  <Typography variant="h4">
                    {predictionHistory.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* データ期間 */}
        {stats?.date_range.start && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  データ期間
                </Typography>
                <Typography variant="body1">
                  {formatDate(stats.date_range.start)} ～ {stats.date_range.end ? formatDate(stats.date_range.end) : '現在'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 売上トレンド */}
        {stats?.sales_trend && stats.sales_trend.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  月別売上トレンド
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={stats.sales_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <RechartsTooltip
                      formatter={(value: number) => [formatCurrency(value), '平均売上']}
                    />
                    <Line
                      type="monotone"
                      dataKey="avg_sales"
                      stroke="#1976d2"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 天気の影響 */}
        {stats?.weather_impact && Object.keys(stats.weather_impact).length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  天気別売上影響
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={Object.entries(stats.weather_impact).map(([weather, sales]) => ({
                      weather,
                      sales,
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="weather" />
                    <YAxis />
                    <RechartsTooltip
                      formatter={(value: number) => [formatCurrency(value), '平均売上']}
                    />
                    <Bar dataKey="sales" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 最近の予測履歴 */}
        {predictionHistory.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  最近の予測履歴
                </Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>予測日</TableCell>
                        <TableCell align="right">予測売上</TableCell>
                        <TableCell align="right">予測客数</TableCell>
                        <TableCell>天気</TableCell>
                        <TableCell>実行日時</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {predictionHistory.slice(0, 5).map((prediction) => (
                        <TableRow key={prediction.id}>
                          <TableCell>
                            {formatDate(prediction.prediction_date)}
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(prediction.predicted_sales)}
                          </TableCell>
                          <TableCell align="right">
                            {prediction.predicted_customers}人
                          </TableCell>
                          <TableCell>
                            {prediction.weather_condition || '不明'}
                          </TableCell>
                          <TableCell>
                            {formatDate(prediction.created_at)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 最新予測結果 */}
        {stats?.latest_prediction && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  最新の予測結果
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={3}>
                    <Typography color="text.secondary">予測日</Typography>
                    <Typography variant="h6">
                      {formatDate(stats.latest_prediction.prediction_date)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography color="text.secondary">予測売上</Typography>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(stats.latest_prediction.predicted_sales)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography color="text.secondary">予測客数</Typography>
                    <Typography variant="h6" color="primary">
                      {stats.latest_prediction.predicted_customers}人
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography color="text.secondary">天気条件</Typography>
                    <Typography variant="h6">
                      {stats.latest_prediction.weather_condition || '不明'}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default UserDashboard;