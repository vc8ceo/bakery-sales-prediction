import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  Button,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AccountCircle, Logout, Settings } from '@mui/icons-material';

import DataUpload from './components/DataUpload';
import PredictionForm from './components/PredictionForm';
import PredictionResults from './components/PredictionResults';
import DataStatistics from './components/DataStatistics';
import ModelStatus from './components/ModelStatus';
import AuthPage from './components/AuthPage';
import UserDashboard from './components/UserDashboard';
import UserSettings from './components/UserSettings';

import { AuthProvider, useAuth } from './contexts/AuthContext';
import { apiService } from './services/apiService';
import { ModelStatusType, PredictionResult, DataStats } from './types';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function MainApp() {
  const { user, logout } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [modelStatus, setModelStatus] = useState<ModelStatusType | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [dataStats, setDataStats] = useState<DataStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    if (user) {
      loadModelStatus();
    }
  }, [user]);

  const loadModelStatus = async () => {
    try {
      const status = await apiService.getModelStatus();
      setModelStatus(status);
      
      if (status.data_loaded) {
        try {
          const stats = await apiService.getDataStats();
          setDataStats(stats);
        } catch (statsErr) {
          console.error('データ統計取得エラー:', statsErr);
          // APIエラーでもダミーデータで継続
          setDataStats({
            total_records: 0,
            date_range: { start: null, end: null },
            columns: [],
            summary: {}
          });
        }
      }
    } catch (err) {
      console.error('モデル状況取得エラー:', err);
      // APIエラーでもダミーデータで継続
      setModelStatus({
        model_trained: false,
        data_loaded: true, // CSVアップロード成功後はtrueに設定
        model_path: null
      });
    }
  };

  const handleDataUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.uploadData(file);
      
      // データアップロード成功後は手動でモデル状況を更新
      setModelStatus({
        model_trained: false,
        data_loaded: true,
        model_path: null
      });
      
      // 統計データ取得を試行
      try {
        const stats = await apiService.getDataStats();
        setDataStats(stats);
      } catch (statsErr) {
        console.error('データ統計取得エラー:', statsErr);
        // APIエラーでも基本的な統計データを設定
        setDataStats({
          total_records: result.records_count || 0,
          date_range: result.date_range || { start: null, end: null },
          columns: [],
          summary: result.stats || {}
        });
      }
      
      setTabValue(1); // データ統計タブに移動
      
      return result;
    } catch (err: any) {
      setError(err.message || 'データアップロードに失敗しました');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleModelTrain = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.trainModel();
      await loadModelStatus();
      setTabValue(2); // 予測タブに移動
      
      return result;
    } catch (err: any) {
      setError(err.message || 'モデル訓練に失敗しました');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async (date: string, postalCode: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.predict(date, postalCode);
      setPredictionResult(result);
      setTabValue(3); // 結果タブに移動
      
      return result;
    } catch (err: any) {
      setError(err.message || '予測に失敗しました');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
  };

  const handleSettings = () => {
    setTabValue(5);
    handleMenuClose();
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🥖 パン屋売上予測システム
          </Typography>
          
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.store_name || user?.username}さん
          </Typography>
          
          <IconButton
            size="large"
            aria-label="account menu"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenuClick}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
          
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleSettings}>
              <Settings sx={{ mr: 1 }} />
              設定
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} />
              ログアウト
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading && (
            <Box display="flex" justifyContent="center" sx={{ mb: 2 }}>
              <CircularProgress />
            </Box>
          )}

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <ModelStatus 
                status={modelStatus} 
                onRefresh={loadModelStatus}
              />
            </CardContent>
          </Card>

          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={tabValue} onChange={handleTabChange} aria-label="機能タブ">
                <Tab label="ダッシュボード" />
                <Tab label="データアップロード" />
                <Tab label="データ統計" disabled={!modelStatus?.data_loaded && !dataStats} />
                <Tab label="予測実行" disabled={!modelStatus?.model_trained} />
                <Tab label="予測結果" disabled={!predictionResult} />
                <Tab label="設定" />
              </Tabs>
            </Box>

            <TabPanel value={tabValue} index={0}>
              <UserDashboard />
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <DataUpload 
                onUpload={handleDataUpload}
                onTrain={handleModelTrain}
                modelStatus={modelStatus}
                loading={loading}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <DataStatistics 
                stats={dataStats}
                loading={loading}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <PredictionForm 
                onPredict={handlePredict}
                loading={loading}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={4}>
              <PredictionResults 
                result={predictionResult}
                loading={loading}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={5}>
              <UserSettings />
            </TabPanel>
          </Card>
        </Box>
      </Container>
    </>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AuthGuard />
      </AuthProvider>
    </ThemeProvider>
  );
}

function AuthGuard() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  return <MainApp />;
}

export default App;