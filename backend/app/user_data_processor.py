import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
import io
import os
import pickle

from .user_models import User, UserData, UserModel
from .models import SalesPredictionModel

class UserDataProcessor:
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.data = None
        self.processed_data = None
        
    def process_user_csv_data(self, csv_content: bytes) -> pd.DataFrame:
        """ユーザーのCSVデータを処理してデータベースに保存"""
        try:
            # 既存のデータ処理ロジックを使用
            from .data_processor import DataProcessor
            processor = DataProcessor()
            df = processor.process_csv_data(csv_content)
            
            # データベースに保存
            self._save_to_database(df)
            
            self.data = df
            return df
            
        except Exception as e:
            raise Exception(f"ユーザーCSV処理エラー: {str(e)}")
    
    def _save_to_database(self, df: pd.DataFrame):
        """DataFrameをデータベースに保存"""
        # 既存のユーザーデータを削除（新しいデータで置き換え）
        self.db.query(UserData).filter(UserData.user_id == self.user_id).delete()
        
        # 新しいデータを挿入
        for _, row in df.iterrows():
            # 数値型の値を適切に処理（NaNをNoneに変換）
            user_data = UserData(
                user_id=self.user_id,
                store_id=str(row.get('store_id', 'default')),
                store_name=str(row.get('store_name', '店舗名なし')),
                date=row['date'],
                weather=str(row.get('weather', 'unknown')),
                sales=float(row['sales']) if pd.notna(row['sales']) else 0.0,
                target_achievement_rate=float(row.get('target_achievement_rate', 100.0)) if pd.notna(row.get('target_achievement_rate')) else 100.0,
                yoy_same_day_ratio=float(row.get('yoy_same_day_ratio', 100.0)) if pd.notna(row.get('yoy_same_day_ratio')) else 100.0,
                customers=int(row['customers']) if pd.notna(row['customers']) else 0,
                avg_spending=float(row.get('avg_spending', 0.0)) if pd.notna(row.get('avg_spending')) else 0.0,
                labor_cost_rate=float(row.get('labor_cost_rate', 30.0)) if pd.notna(row.get('labor_cost_rate')) else 30.0,
                cost_rate=float(row.get('cost_rate', 30.0)) if pd.notna(row.get('cost_rate')) else 30.0
            )
            self.db.add(user_data)
        
        self.db.commit()
    
    def load_user_data(self) -> Optional[pd.DataFrame]:
        """データベースからユーザーデータを読み込み"""
        user_data = self.db.query(UserData).filter(UserData.user_id == self.user_id).all()
        
        if not user_data:
            return None
        
        # DataFrameに変換
        data_list = []
        for data in user_data:
            data_dict = {
                'store_id': data.store_id,
                'store_name': data.store_name,
                'date': data.date,
                'weather': data.weather,
                'sales': data.sales,
                'target_achievement_rate': data.target_achievement_rate,
                'yoy_same_day_ratio': data.yoy_same_day_ratio,
                'customers': data.customers,
                'avg_spending': data.avg_spending,
                'labor_cost_rate': data.labor_cost_rate,
                'cost_rate': data.cost_rate
            }
            data_list.append(data_dict)
        
        df = pd.DataFrame(data_list)
        self.data = df
        return df
    
    def create_user_features(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """ユーザーデータから特徴量を作成"""
        if self.data is None:
            self.load_user_data()
        
        if self.data is None or len(self.data) == 0:
            raise Exception("ユーザーデータが存在しません")
        
        # 既存の特徴量エンジニアリングロジックを使用
        from .data_processor import DataProcessor
        processor = DataProcessor()
        processor.data = self.data
        
        return processor.create_features(self.data)
    
    def train_user_model(self) -> Dict[str, Any]:
        """ユーザー専用モデルを訓練"""
        try:
            # 特徴量作成
            features, targets = self.create_user_features()
            
            if len(features) < 10:
                raise Exception("訓練には最低10件のデータが必要です")
            
            # モデル訓練
            model = SalesPredictionModel()
            metrics = model.train(features, targets)
            
            # モデル保存
            model_dir = f"models/users/{self.user_id}"
            os.makedirs(model_dir, exist_ok=True)
            model_path = f"{model_dir}/sales_model.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # データベースにモデル情報を保存
            self._save_model_info(model_path, metrics, len(features))
            
            return metrics
            
        except Exception as e:
            raise Exception(f"ユーザーモデル訓練エラー: {str(e)}")
    
    def _save_model_info(self, model_path: str, metrics: Dict[str, Any], data_count: int):
        """モデル情報をデータベースに保存"""
        import json
        
        # 既存のモデル情報を削除
        self.db.query(UserModel).filter(UserModel.user_id == self.user_id).delete()
        
        # 新しいモデル情報を保存
        user_model = UserModel(
            user_id=self.user_id,
            model_name="sales_prediction_model",
            model_path=model_path,
            model_metrics=json.dumps(metrics),
            training_data_count=data_count
        )
        
        self.db.add(user_model)
        self.db.commit()
    
    def load_user_model(self) -> Optional[SalesPredictionModel]:
        """ユーザー専用モデルを読み込み"""
        model_info = self.db.query(UserModel)\
            .filter(UserModel.user_id == self.user_id)\
            .first()
        
        if not model_info or not os.path.exists(model_info.model_path):
            return None
        
        try:
            with open(model_info.model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            print(f"モデル読み込みエラー: {e}")
            return None
    
    def get_user_stats(self) -> Dict[str, Any]:
        """ユーザーデータの統計情報"""
        if self.data is None:
            self.load_user_data()
        
        if self.data is None or len(self.data) == 0:
            return {}
        
        from .data_processor import DataProcessor
        processor = DataProcessor()
        processor.data = self.data
        
        return processor.get_detailed_stats()
    
    def has_data(self) -> bool:
        """ユーザーデータが存在するかチェック"""
        count = self.db.query(UserData)\
            .filter(UserData.user_id == self.user_id)\
            .count()
        return count > 0
    
    def has_model(self) -> bool:
        """ユーザーモデルが存在するかチェック"""
        model_info = self.db.query(UserModel)\
            .filter(UserModel.user_id == self.user_id)\
            .first()
        
        return model_info is not None and os.path.exists(model_info.model_path)
    
    def predict_sales(self, prediction_date: datetime, weather_data: dict) -> Tuple[float, int, Dict[str, float]]:
        """ユーザーモデルで売上予測"""
        model = self.load_user_model()
        if model is None:
            raise Exception("ユーザーモデルが訓練されていません")
        
        # 特徴量作成
        features = self._create_prediction_features(prediction_date, weather_data)
        
        # 予測実行
        return model.predict(features)
    
    def _create_prediction_features(self, target_date: datetime, weather_data: dict) -> pd.DataFrame:
        """予測用特徴量作成"""
        # 既存のロジックを使用
        from .data_processor import DataProcessor
        processor = DataProcessor()
        
        # ユーザーの過去データを設定
        if self.data is None:
            self.load_user_data()
        processor.processed_data = self.data
        
        return processor.create_prediction_features(target_date.date(), weather_data)
    
    def delete_user_data(self):
        """ユーザーデータ・モデル・ファイルを完全削除"""
        try:
            # データベースからデータ削除
            self.db.query(UserData).filter(UserData.user_id == self.user_id).delete()
            
            # モデル情報を取得してファイル削除
            model_info = self.db.query(UserModel).filter(UserModel.user_id == self.user_id).first()
            if model_info and os.path.exists(model_info.model_path):
                os.remove(model_info.model_path)
                # ユーザーディレクトリも空なら削除
                model_dir = os.path.dirname(model_info.model_path)
                if os.path.exists(model_dir) and not os.listdir(model_dir):
                    os.rmdir(model_dir)
            
            # データベースからモデル情報削除
            self.db.query(UserModel).filter(UserModel.user_id == self.user_id).delete()
            
            # 予測履歴削除
            from .user_models import PredictionHistory
            self.db.query(PredictionHistory).filter(PredictionHistory.user_id == self.user_id).delete()
            
            self.db.commit()
            
            # インスタンス変数をリセット
            self.data = None
            self.processed_data = None
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"ユーザーデータ削除エラー: {str(e)}")