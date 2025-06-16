import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  Alert,
  Tooltip
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { TrendingUp, LocationOn, CalendarToday } from '@mui/icons-material';
import dayjs, { Dayjs } from 'dayjs';
import 'dayjs/locale/ja';

interface PredictionFormProps {
  onPredict: (date: string, postalCode: string) => Promise<any>;
  loading: boolean;
}



const PredictionForm: React.FC<PredictionFormProps> = ({ onPredict, loading }) => {
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(
    dayjs().add(1, 'day') // デフォルトは明日
  );
  const [postalCode, setPostalCode] = useState('1000001');
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    if (!selectedDate) {
      setError('予測日を選択してください');
      return;
    }

    // 今日より前の日付はエラー
    if (selectedDate.isBefore(dayjs(), 'day')) {
      setError('今日以降の日付を選択してください');
      return;
    }

    setError(null);

    const dateStr = selectedDate.format('YYYY-MM-DD');
    const postal = postalCode;

    // 郵便番号の簡単なバリデーション
    if (!/^\d{7}$/.test(postal)) {
      setError('郵便番号は7桁の数字で入力してください（例：1000001）');
      return;
    }

    try {
      await onPredict(dateStr, postal);
    } catch (err: any) {
      setError(err.message);
    }
  };



  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ja">
      <Box>
        <Typography variant="h5" gutterBottom>
          売上予測
        </Typography>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          予測したい日付と地域を選択して、売上と来店客数を予測します。
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <CalendarToday sx={{ mr: 1, verticalAlign: 'middle' }} />
                  予測日設定
                </Typography>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <DatePicker
                    label="予測日"
                    value={selectedDate}
                    onChange={setSelectedDate}
                    minDate={dayjs()}
                    maxDate={dayjs().add(7, 'day')}
                    disabled={loading}
                    format="YYYY年MM月DD日"
                  />
                </FormControl>

                {selectedDate && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      選択日: {selectedDate.format('YYYY年MM月DD日（dddd）')}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <LocationOn sx={{ mr: 1, verticalAlign: 'middle' }} />
                  地域設定
                </Typography>

                <TextField
                  fullWidth
                  label="郵便番号"
                  value={postalCode}
                  onChange={(e) => setPostalCode(e.target.value)}
                  placeholder="1000001"
                  helperText="7桁の数字で入力してください（例：1000001）"
                  disabled={loading}
                  sx={{ mb: 2 }}
                />

                <Typography variant="body2" color="text.secondary">
                  選択地域: 〒{postalCode || '未入力'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box textAlign="center">
                  <Tooltip title="機械学習モデルが天気予報データと過去の売上パターンを分析して予測します">
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handlePredict}
                      disabled={loading || !selectedDate}
                      startIcon={<TrendingUp />}
                      sx={{ minWidth: 200 }}
                    >
                      {loading ? '予測中...' : '売上予測を実行'}
                    </Button>
                  </Tooltip>
                </Box>

                <Typography variant="body2" color="text.secondary" align="center" mt={2}>
                  💡 予測には数秒かかる場合があります
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </LocalizationProvider>
  );
};

export default PredictionForm;