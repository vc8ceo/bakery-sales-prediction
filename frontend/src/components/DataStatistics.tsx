import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { DataStats } from '../types';

interface DataStatisticsProps {
  stats: DataStats | null;
  loading: boolean;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const DataStatistics: React.FC<DataStatisticsProps> = ({ stats, loading }) => {

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (!stats) {
    return (
      <Typography variant="body1" color="text.secondary">
        統計データがありません
      </Typography>
    );
  }

  // 月別売上データの準備
  const monthlyData = stats?.monthly_sales ? Object.entries(stats.monthly_sales).map(([month, sales]) => ({
    month: `${month}月`,
    sales: Math.round(Number(sales) || 0)
  })) : [];

  // 曜日別売上データの準備
  const weekdayNames = ['月', '火', '水', '木', '金', '土', '日'];
  const weekdayData = stats?.weekday_sales ? Object.entries(stats.weekday_sales).map(([day, sales]) => ({
    day: weekdayNames[parseInt(day)] || `曜日${day}`,
    sales: Math.round(Number(sales) || 0)
  })) : [];

  // 天気別売上データの準備
  const weatherJapanese = {
    'sunny': '晴れ',
    'cloudy': '曇り',
    'rainy': '雨',
    'sleet': 'みぞれ',
    'snow': '雪',
    'unknown': '不明'
  };
  
  const weatherData = stats?.weather_impact ? Object.entries(stats.weather_impact).map(([weather, sales]) => ({
    name: weatherJapanese[weather as keyof typeof weatherJapanese] || weather,
    sales: Math.round(Number(sales) || 0)
  })) : [];

  const formatCurrency = (value: number) => `¥${value.toLocaleString()}`;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        データ統計情報
      </Typography>

      <Grid container spacing={3}>
        {/* 基本情報 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                データ概要
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                {stats?.date_range && (
                  <Chip 
                    label={`期間: ${stats.date_range.start} ～ ${stats.date_range.end}`}
                    variant="outlined"
                  />
                )}
                {stats?.holiday_impact && (
                  <>
                    <Chip 
                      label={`祝日平均: ${formatCurrency(stats.holiday_impact.holiday_avg || 0)}`}
                      color="primary"
                      variant="outlined"
                    />
                    <Chip 
                      label={`平日平均: ${formatCurrency(stats.holiday_impact.regular_avg || 0)}`}
                      color="secondary"
                      variant="outlined"
                    />
                  </>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 月別売上グラフ */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                月別売上推移
              </Typography>
              <Box height={350}>
                {monthlyData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={monthlyData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="month" 
                        tick={{ fontSize: 12 }}
                        tickMargin={10}
                        interval={0}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis tickFormatter={formatCurrency} />
                      <Tooltip formatter={(value) => [formatCurrency(Number(value)), '売上']} />
                      <Line 
                        type="monotone" 
                        dataKey="sales" 
                        stroke="#8884d8" 
                        strokeWidth={3}
                        dot={{ r: 5 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                    <Typography color="text.secondary">データがありません</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 曜日別売上グラフ */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                曜日別売上
              </Typography>
              <Box height={350}>
                {weekdayData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weekdayData} margin={{ top: 5, right: 30, left: 20, bottom: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="day" 
                        tick={{ fontSize: 12 }}
                        tickMargin={10}
                        interval={0}
                        height={60}
                      />
                      <YAxis tickFormatter={formatCurrency} />
                      <Tooltip formatter={(value) => [formatCurrency(Number(value)), '売上']} />
                      <Bar dataKey="sales" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                    <Typography color="text.secondary">データがありません</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 天気別売上棒グラフ */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                天気別売上分布
              </Typography>
              <Box height={350}>
                {weatherData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weatherData} margin={{ top: 5, right: 30, left: 20, bottom: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="name" 
                        tick={{ fontSize: 12 }}
                        tickMargin={10}
                        interval={0}
                        height={60}
                      />
                      <YAxis tickFormatter={formatCurrency} />
                      <Bar dataKey="sales" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                    <Typography color="text.secondary">データがありません</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 祝日vs平日比較 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                祝日 vs 平日 売上比較
              </Typography>
              <Box height={350}>
                {stats?.holiday_impact ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={[
                        { type: '平日', sales: stats.holiday_impact.regular_avg || 0 },
                        { type: '祝日', sales: stats.holiday_impact.holiday_avg || 0 }
                      ]}
                      margin={{ top: 5, right: 30, left: 20, bottom: 40 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="type" 
                        tick={{ fontSize: 12 }}
                        tickMargin={10}
                        interval={0}
                        height={60}
                      />
                      <YAxis tickFormatter={formatCurrency} />
                      <Bar dataKey="sales" fill="#ffc658" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                    <Typography color="text.secondary">データがありません</Typography>
                  </Box>
                )}
              </Box>
              
              {stats?.holiday_impact && (
                <Box mt={2}>
                  <Typography variant="body2" color="text.secondary">
                    祝日効果: {(stats.holiday_impact.holiday_avg || 0) > (stats.holiday_impact.regular_avg || 0)
                      ? `+${formatCurrency((stats.holiday_impact.holiday_avg || 0) - (stats.holiday_impact.regular_avg || 0))}` 
                      : `${formatCurrency((stats.holiday_impact.holiday_avg || 0) - (stats.holiday_impact.regular_avg || 0))}`
                    } ({(((stats.holiday_impact.holiday_avg || 0) / (stats.holiday_impact.regular_avg || 1) - 1) * 100).toFixed(1)}%)
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DataStatistics;