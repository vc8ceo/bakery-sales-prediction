import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  LinearProgress,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Psychology,
  CheckCircle,
  Info
} from '@mui/icons-material';
import { ModelStatusType, UploadResult, TrainResult } from '../types';

interface DataUploadProps {
  onUpload: (file: File) => Promise<UploadResult>;
  onTrain: () => Promise<TrainResult>;
  modelStatus: ModelStatusType | null;
  loading: boolean;
  onReset?: () => void; // リセット用のコールバックを追加
}

const DataUpload: React.FC<DataUploadProps> = ({
  onUpload,
  onTrain,
  modelStatus,
  loading,
  onReset
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [trainResult, setTrainResult] = useState<TrainResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // データが削除された場合にローカル状態をリセット
  React.useEffect(() => {
    if (!modelStatus?.data_loaded) {
      setUploadResult(null);
      setTrainResult(null);
      setError(null);
    }
  }, [modelStatus?.data_loaded]);

  const activeStep = modelStatus?.data_loaded 
    ? (modelStatus.model_trained ? 2 : 1) 
    : 0;

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    setError(null);

    const files = Array.from(e.dataTransfer.files);
    const csvFile = files.find(file => file.name.endsWith('.csv'));

    if (!csvFile) {
      setError('CSVファイルを選択してください');
      return;
    }

    try {
      const result = await onUpload(csvFile);
      setUploadResult(result);
    } catch (err: any) {
      setError(err.message);
    }
  }, [onUpload]);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setError('CSVファイルを選択してください');
      return;
    }

    setError(null);
    try {
      const result = await onUpload(file);
      setUploadResult(result);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleTrain = async () => {
    setError(null);
    try {
      const result = await onTrain();
      setTrainResult(result);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        データアップロードとモデル訓練
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Stepper activeStep={activeStep} orientation="vertical">
        <Step>
          <StepLabel>CSVデータアップロード</StepLabel>
          <StepContent>
            <Paper
              className={`upload-area ${dragOver ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              sx={{ p: 4, mb: 2, border: '2px dashed #ccc', textAlign: 'center' }}
            >
              <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                POSレジデータ(CSV)をドロップ または クリックして選択
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                ファイル形式: CSV (Shift_JIS エンコーディング)
              </Typography>
              
              <input
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                id="file-upload"
                disabled={loading}
              />
              <label htmlFor="file-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<InsertDriveFile />}
                  disabled={loading}
                >
                  ファイルを選択
                </Button>
              </label>
            </Paper>

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            {uploadResult && (
              <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="subtitle2">アップロード完了</Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                    <ListItemText primary={`データ件数: ${uploadResult.records_count}件`} />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Info color="info" /></ListItemIcon>
                    <ListItemText 
                      primary={`期間: ${uploadResult.date_range.start} ～ ${uploadResult.date_range.end}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Info color="info" /></ListItemIcon>
                    <ListItemText 
                      primary={`売上平均: ¥${Math.round(uploadResult.stats.sales_stats.mean).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Info color="info" /></ListItemIcon>
                    <ListItemText 
                      primary={`客数平均: ${Math.round(uploadResult.stats.customers_stats.mean)}人`} 
                    />
                  </ListItem>
                </List>
              </Alert>
            )}
          </StepContent>
        </Step>

        <Step>
          <StepLabel>機械学習モデル訓練</StepLabel>
          <StepContent>
            <Typography variant="body2" color="text.secondary" mb={2}>
              アップロードされたデータを使用して予測モデルを訓練します。
              Random Forestアルゴリズムを使用し、売上と来店客数を予測します。
            </Typography>

            <Box mb={2}>
              <Button
                variant="contained"
                onClick={handleTrain}
                startIcon={<Psychology />}
                disabled={loading || !modelStatus?.data_loaded}
                size="large"
              >
                モデル訓練開始
              </Button>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            {trainResult && (
              <Alert severity="success">
                <Typography variant="subtitle2">モデル訓練完了</Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                    <ListItemText 
                      primary={`売上予測精度 (R²): ${(trainResult.metrics.sales_metrics.r2 * 100).toFixed(1)}%`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                    <ListItemText 
                      primary={`客数予測精度 (R²): ${(trainResult.metrics.customers_metrics.r2 * 100).toFixed(1)}%`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Info color="info" /></ListItemIcon>
                    <ListItemText 
                      primary={`訓練データ: ${trainResult.metrics.training_samples}件 / テストデータ: ${trainResult.metrics.test_samples}件`} 
                    />
                  </ListItem>
                </List>
              </Alert>
            )}
          </StepContent>
        </Step>

        <Step>
          <StepLabel>準備完了</StepLabel>
          <StepContent>
            <Alert severity="success">
              <Typography variant="subtitle2">
                🎉 システム準備完了！
              </Typography>
              <Typography variant="body2">
                「予測実行」タブで売上予測を開始できます。
              </Typography>
            </Alert>
          </StepContent>
        </Step>
      </Stepper>
    </Box>
  );
};

export default DataUpload;