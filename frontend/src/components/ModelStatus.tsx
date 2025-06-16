import React from 'react';
import {
  Box,
  Typography,
  Chip,
  IconButton,
  Stack,
  Tooltip
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Refresh,
  CloudUpload,
  Psychology
} from '@mui/icons-material';
import { ModelStatusType } from '../types';

interface ModelStatusProps {
  status: ModelStatusType | null;
  onRefresh: () => void;
}

const ModelStatus: React.FC<ModelStatusProps> = ({ status, onRefresh }) => {
  if (!status) {
    return (
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Typography variant="h6">システム状況</Typography>
        <IconButton onClick={onRefresh} size="small">
          <Refresh />
        </IconButton>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="h6">システム状況</Typography>
        <Tooltip title="状況を更新">
          <IconButton onClick={onRefresh} size="small">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        <Chip
          icon={status.data_loaded ? <CheckCircle /> : <Cancel />}
          label={
            <Box display="flex" alignItems="center" gap={1}>
              <CloudUpload fontSize="small" />
              データ読込: {status.data_loaded ? '完了' : '未完了'}
            </Box>
          }
          color={status.data_loaded ? 'success' : 'default'}
          variant={status.data_loaded ? 'filled' : 'outlined'}
        />

        <Chip
          icon={status.model_trained ? <CheckCircle /> : <Cancel />}
          label={
            <Box display="flex" alignItems="center" gap={1}>
              <Psychology fontSize="small" />
              モデル訓練: {status.model_trained ? '完了' : '未完了'}
            </Box>
          }
          color={status.model_trained ? 'success' : 'default'}
          variant={status.model_trained ? 'filled' : 'outlined'}
        />
      </Stack>

      {status.model_path && (
        <Typography variant="caption" display="block" mt={1} color="text.secondary">
          モデル保存先: {status.model_path}
        </Typography>
      )}

      {!status.data_loaded && (
        <Typography variant="body2" color="text.secondary" mt={1}>
          まず CSVファイルをアップロードしてください
        </Typography>
      )}

      {status.data_loaded && !status.model_trained && (
        <Typography variant="body2" color="text.secondary" mt={1}>
          データが読み込まれました。モデルを訓練してください
        </Typography>
      )}

      {status.data_loaded && status.model_trained && (
        <Typography variant="body2" color="success.main" mt={1}>
          ✅ システム準備完了！予測を実行できます
        </Typography>
      )}
    </Box>
  );
};

export default ModelStatus;