import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Alert,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  People,
  WbSunny,
  Thermostat,
  LocationOn,
  DateRange,
  MonetizationOn
} from '@mui/icons-material';
import { PredictionResult } from '../types';

interface PredictionResultsProps {
  result: PredictionResult | null;
  loading: boolean;
}

const PredictionResults: React.FC<PredictionResultsProps> = ({ result, loading }) => {
  if (loading) {
    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          予測実行中...
        </Typography>
        <LinearProgress sx={{ mb: 2 }} />
        <Typography variant="body2" color="text.secondary">
          天気予報データを取得し、機械学習モデルで予測計算中です
        </Typography>
      </Box>
    );
  }

  if (!result) {
    return (
      <Typography variant="body1" color="text.secondary">
        予測結果がありません。まず予測を実行してください。
      </Typography>
    );
  }

  const formatCurrency = (value: number) => `¥${Math.round(value).toLocaleString()}`;
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

  // 信頼区間の幅を計算
  const salesConfidenceWidth = result.confidence_interval.sales_upper - result.confidence_interval.sales_lower;
  const customersConfidenceWidth = result.confidence_interval.customers_upper - result.confidence_interval.customers_lower;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        📊 予測結果
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="subtitle2">
          予測日: {result.date} ({result.weather_forecast.location})
        </Typography>
        <Typography variant="body2">
          以下の予測は過去データと天気予報に基づく機械学習モデルの計算結果です。
          実際の売上は様々な要因により変動する可能性があります。
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {/* メイン予測結果 */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <MonetizationOn sx={{ mr: 1, color: 'success.main' }} />
                売上予測
              </Typography>
              
              <Typography variant="h3" color="success.main" gutterBottom>
                {formatCurrency(result.predicted_sales)}
              </Typography>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  信頼区間 (95%)
                </Typography>
                <Typography variant="body1">
                  {formatCurrency(result.confidence_interval.sales_lower)} ～ {formatCurrency(result.confidence_interval.sales_upper)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  予測幅: {formatCurrency(salesConfidenceWidth)}
                </Typography>
              </Box>

              <LinearProgress 
                variant="determinate" 
                value={75} 
                sx={{ mb: 1 }}
                color="success"
              />
              <Typography variant="caption" color="text.secondary">
                予測信頼度: 75%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <People sx={{ mr: 1, color: 'primary.main' }} />
                来店客数予測
              </Typography>
              
              <Typography variant="h3" color="primary.main" gutterBottom>
                {result.predicted_customers}人
              </Typography>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  信頼区間 (95%)
                </Typography>
                <Typography variant="body1">
                  {Math.round(result.confidence_interval.customers_lower)}人 ～ {Math.round(result.confidence_interval.customers_upper)}人
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  予測幅: {Math.round(customersConfidenceWidth)}人
                </Typography>
              </Box>

              <LinearProgress 
                variant="determinate" 
                value={70} 
                sx={{ mb: 1 }}
                color="primary"
              />
              <Typography variant="caption" color="text.secondary">
                予測信頼度: 70%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 天気予報情報 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <WbSunny sx={{ mr: 1, color: 'warning.main' }} />
                天気予報情報
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="subtitle2" color="text.secondary">
                      予測日天気
                    </Typography>
                    <Chip 
                      label={result.weather_forecast.weather}
                      color="primary"
                      variant="outlined"
                      size="medium"
                    />
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="subtitle2" color="text.secondary">
                      気温
                    </Typography>
                    <Typography variant="h6">
                      <Thermostat sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                      {result.weather_forecast.temperature}°C
                    </Typography>
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="subtitle2" color="text.secondary">
                      地域
                    </Typography>
                    <Typography variant="h6">
                      <LocationOn sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                      {result.weather_forecast.location}
                    </Typography>
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="subtitle2" color="text.secondary">
                      データソース
                    </Typography>
                    <Typography variant="body2">
                      {result.weather_forecast.source === 'livedoor' ? '気象庁データ' : '天気予報API'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {/* 詳細天気情報 */}
              {result.weather_forecast.tomorrow && (
                <Box mt={3}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="subtitle1" gutterBottom>
                    詳細天気予報
                  </Typography>
                  
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell>日付</TableCell>
                          <TableCell>{result.weather_forecast.tomorrow.date}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>天気</TableCell>
                          <TableCell>{result.weather_forecast.tomorrow.weather}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>最高気温</TableCell>
                          <TableCell>
                            {result.weather_forecast.tomorrow.max_temp ? 
                              `${result.weather_forecast.tomorrow.max_temp}°C` : '不明'}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>最低気温</TableCell>
                          <TableCell>
                            {result.weather_forecast.tomorrow.min_temp ? 
                              `${result.weather_forecast.tomorrow.min_temp}°C` : '不明'}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 予測の詳細分析 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 予測分析
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    売上予測について
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    予測売上: <strong>{formatCurrency(result.predicted_sales)}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    この予測は、過去の売上データ、曜日パターン、季節性、天気条件などを
                    機械学習モデルで分析した結果です。
                  </Typography>
                  
                  {result.predicted_sales > 50000 && (
                    <Alert severity="success">
                      好調な売上が見込まれます！
                    </Alert>
                  )}
                  
                  {result.predicted_sales < 30000 && (
                    <Alert severity="warning">
                      売上が通常より低めの予測です。
                    </Alert>
                  )}
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    来店客数について
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    予測客数: <strong>{result.predicted_customers}人</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    天気条件と過去の来店パターンから算出された予測客数です。
                    天気が売上に与える影響も考慮されています。
                  </Typography>

                  {result.predicted_customers > 60 && (
                    <Alert severity="info">
                      多くのお客様の来店が予想されます。
                    </Alert>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PredictionResults;