import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class SalesPredictionModel:
    def __init__(self):
        self.sales_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.customers_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = None
        
    def train(self, X: pd.DataFrame, y: pd.DataFrame) -> Dict[str, Any]:
        """モデル訓練"""
        try:
            # 特徴量カラム名を保存
            self.feature_columns = X.columns.tolist()
            
            # データ分割
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 特徴量スケーリング
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 売上モデル訓練
            self.sales_model.fit(X_train_scaled, y_train['sales'])
            sales_pred = self.sales_model.predict(X_test_scaled)
            
            # 客数モデル訓練
            self.customers_model.fit(X_train_scaled, y_train['customers'])
            customers_pred = self.customers_model.predict(X_test_scaled)
            
            # 評価指標計算
            sales_metrics = self._calculate_metrics(y_test['sales'], sales_pred)
            customers_metrics = self._calculate_metrics(y_test['customers'], customers_pred)
            
            # 特徴量重要度
            sales_feature_importance = dict(zip(
                self.feature_columns,
                self.sales_model.feature_importances_
            ))
            customers_feature_importance = dict(zip(
                self.feature_columns,
                self.customers_model.feature_importances_
            ))
            
            self.is_trained = True
            
            return {
                'sales_metrics': sales_metrics,
                'customers_metrics': customers_metrics,
                'sales_feature_importance': sales_feature_importance,
                'customers_feature_importance': customers_feature_importance,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            raise Exception(f"モデル訓練エラー: {str(e)}")
    
    def predict(self, X: pd.DataFrame) -> Tuple[float, int, Dict[str, float]]:
        """予測実行"""
        if not self.is_trained:
            raise Exception("モデルが訓練されていません")
        
        try:
            # 特徴量の順序を確認・調整
            X_ordered = X[self.feature_columns]
            
            # スケーリング
            X_scaled = self.scaler.transform(X_ordered)
            
            # 予測
            sales_pred = self.sales_model.predict(X_scaled)[0]
            customers_pred = self.customers_model.predict(X_scaled)[0]
            
            # 信頼区間の概算（標準偏差ベース）
            sales_std = np.std([tree.predict(X_scaled)[0] for tree in self.sales_model.estimators_[:10]])
            customers_std = np.std([tree.predict(X_scaled)[0] for tree in self.customers_model.estimators_[:10]])
            
            confidence_interval = {
                'sales_lower': max(0, sales_pred - 1.96 * sales_std),
                'sales_upper': sales_pred + 1.96 * sales_std,
                'customers_lower': max(0, customers_pred - 1.96 * customers_std),
                'customers_upper': customers_pred + 1.96 * customers_std
            }
            
            return sales_pred, int(customers_pred), confidence_interval
            
        except Exception as e:
            raise Exception(f"予測エラー: {str(e)}")
    
    def _calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """評価指標計算"""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        # MAPE計算（0除算回避）
        mape = np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1, None))) * 100
        
        return {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape)
        }
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """特徴量重要度取得"""
        if not self.is_trained:
            return {}
        
        return {
            'sales': dict(zip(self.feature_columns, self.sales_model.feature_importances_)),
            'customers': dict(zip(self.feature_columns, self.customers_model.feature_importances_))
        }
    
    def save_model(self, filepath: str):
        """モデル保存"""
        if not self.is_trained:
            raise Exception("訓練されていないモデルは保存できません")
        
        model_data = {
            'sales_model': self.sales_model,
            'customers_model': self.customers_model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath: str):
        """モデル読み込み"""
        model_data = joblib.load(filepath)
        
        self.sales_model = model_data['sales_model']
        self.customers_model = model_data['customers_model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']

class EnsembleModel(SalesPredictionModel):
    """アンサンブルモデル（複数アルゴリズムの組み合わせ）"""
    
    def __init__(self):
        super().__init__()
        
        # 複数のモデルを使用
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.linear_model import LinearRegression
        
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        self.model_weights = {'random_forest': 0.5, 'gradient_boosting': 0.3, 'linear_regression': 0.2}
    
    def train(self, X: pd.DataFrame, y: pd.DataFrame) -> Dict[str, Any]:
        """アンサンブルモデル訓練"""
        try:
            self.feature_columns = X.columns.tolist()
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 各モデルを訓練
            sales_predictions = []
            customers_predictions = []
            
            for name, model in self.models.items():
                # 売上予測モデル
                sales_model = model.__class__(**model.get_params())
                sales_model.fit(X_train_scaled, y_train['sales'])
                sales_pred = sales_model.predict(X_test_scaled)
                sales_predictions.append(sales_pred * self.model_weights[name])
                
                # 客数予測モデル
                customers_model = model.__class__(**model.get_params())
                customers_model.fit(X_train_scaled, y_train['customers'])
                customers_pred = customers_model.predict(X_test_scaled)
                customers_predictions.append(customers_pred * self.model_weights[name])
            
            # アンサンブル予測
            ensemble_sales_pred = np.sum(sales_predictions, axis=0)
            ensemble_customers_pred = np.sum(customers_predictions, axis=0)
            
            # 評価指標
            sales_metrics = self._calculate_metrics(y_test['sales'], ensemble_sales_pred)
            customers_metrics = self._calculate_metrics(y_test['customers'], ensemble_customers_pred)
            
            self.is_trained = True
            
            return {
                'sales_metrics': sales_metrics,
                'customers_metrics': customers_metrics,
                'model_type': 'ensemble',
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            raise Exception(f"アンサンブルモデル訓練エラー: {str(e)}")