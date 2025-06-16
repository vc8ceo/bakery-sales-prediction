import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays
import io
from typing import Tuple, Dict, Any

class DataProcessor:
    def __init__(self):
        self.data = None
        self.processed_data = None
        self.jp_holidays = holidays.Japan()
    
    def process_csv_data(self, csv_content: bytes) -> pd.DataFrame:
        """CSVデータの読み込みと前処理"""
        try:
            # Shift_JISでデコード
            csv_string = csv_content.decode('shift_jis')
            
            # DataFrameに変換
            df = pd.read_csv(io.StringIO(csv_string))
            
            # カラム名を英語に変換
            column_mapping = {
                'AKR': 'store_id',
                '店舗名': 'store_name', 
                '日付': 'date',
                '天気': 'weather',
                '売上': 'sales',
                '目標達成率': 'target_achievement_rate',
                '前年同曜日比': 'yoy_same_day_ratio',
                '客数': 'customers',
                '客単価': 'avg_spending',
                '人件費率': 'labor_cost_rate',
                '原価率': 'cost_rate'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            # データ型変換
            df['date'] = pd.to_datetime(df['date'])
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
            df['customers'] = pd.to_numeric(df['customers'], errors='coerce')
            df['avg_spending'] = pd.to_numeric(df['avg_spending'], errors='coerce')
            
            # 売上が0またはNaNの行を除外
            df = df.dropna(subset=['sales', 'customers'])
            df = df[df['sales'] > 0]
            
            # 天気データの正規化
            df['weather'] = df['weather'].fillna('不明')
            weather_mapping = {
                '晴': 'sunny',
                '曇': 'cloudy', 
                '雨': 'rainy',
                'みぞれ': 'sleet',
                '雪': 'snow',
                '不明': 'unknown'
            }
            df['weather'] = df['weather'].map(weather_mapping).fillna('unknown')
            
            self.data = df
            return df
            
        except Exception as e:
            raise Exception(f"CSV処理エラー: {str(e)}")
    
    def create_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """特徴量エンジニアリング"""
        feature_df = df.copy()
        
        # 時系列特徴量
        feature_df['year'] = feature_df['date'].dt.year
        feature_df['month'] = feature_df['date'].dt.month
        feature_df['day'] = feature_df['date'].dt.day
        feature_df['weekday'] = feature_df['date'].dt.weekday  # 0=月曜日
        feature_df['is_weekend'] = feature_df['weekday'].isin([5, 6]).astype(int)
        
        # 祝日フラグ
        feature_df['is_holiday'] = feature_df['date'].apply(
            lambda x: x.date() in self.jp_holidays
        ).astype(int)
        
        # 天気エンコーディング
        weather_encoding = {
            'sunny': 0, 'cloudy': 1, 'rainy': 2, 
            'sleet': 3, 'snow': 4, 'unknown': -1
        }
        feature_df['weather_code'] = feature_df['weather'].map(weather_encoding)
        
        # 季節特徴量
        feature_df['season'] = feature_df['month'].apply(self._get_season)
        
        # 過去データ特徴量（7日間移動平均）
        feature_df = feature_df.sort_values('date')
        feature_df['sales_ma7'] = feature_df['sales'].rolling(window=7, min_periods=1).mean()
        feature_df['customers_ma7'] = feature_df['customers'].rolling(window=7, min_periods=1).mean()
        
        # 前週同曜日データ
        feature_df['prev_week_sales'] = feature_df['sales'].shift(7)
        feature_df['prev_week_customers'] = feature_df['customers'].shift(7)
        
        # 欠損値補完
        feature_df = feature_df.fillna(method='bfill').fillna(method='ffill')
        
        # 特徴量とターゲットを分離
        feature_columns = [
            'year', 'month', 'day', 'weekday', 'is_weekend', 'is_holiday',
            'weather_code', 'season', 'sales_ma7', 'customers_ma7',
            'prev_week_sales', 'prev_week_customers'
        ]
        
        X = feature_df[feature_columns]
        y = feature_df[['sales', 'customers']]
        
        self.processed_data = feature_df
        return X, y
    
    def create_prediction_features(self, target_date: datetime.date, weather_data: dict) -> pd.DataFrame:
        """予測用特徴量作成"""
        # 基本特徴量
        features = {
            'year': target_date.year,
            'month': target_date.month,
            'day': target_date.day,
            'weekday': target_date.weekday(),
            'is_weekend': 1 if target_date.weekday() in [5, 6] else 0,
            'is_holiday': 1 if target_date in self.jp_holidays else 0,
            'season': self._get_season(target_date.month)
        }
        
        # 天気特徴量
        weather_mapping = {
            '晴れ': 0, '曇り': 1, '雨': 2, 
            'みぞれ': 3, '雪': 4
        }
        weather_condition = weather_data.get('weather', '不明')
        features['weather_code'] = weather_mapping.get(weather_condition, -1)
        
        # 履歴特徴量（実際の実装では過去データから計算）
        if self.processed_data is not None:
            recent_data = self.processed_data.tail(30)
            features['sales_ma7'] = recent_data['sales'].mean()
            features['customers_ma7'] = recent_data['customers'].mean()
            features['prev_week_sales'] = recent_data['sales'].iloc[-7] if len(recent_data) >= 7 else recent_data['sales'].mean()
            features['prev_week_customers'] = recent_data['customers'].iloc[-7] if len(recent_data) >= 7 else recent_data['customers'].mean()
        else:
            # デフォルト値
            features['sales_ma7'] = 50000
            features['customers_ma7'] = 50
            features['prev_week_sales'] = 50000
            features['prev_week_customers'] = 50
        
        return pd.DataFrame([features])
    
    def _get_season(self, month: int) -> int:
        """季節を数値に変換"""
        if month in [3, 4, 5]:
            return 0  # 春
        elif month in [6, 7, 8]:
            return 1  # 夏
        elif month in [9, 10, 11]:
            return 2  # 秋
        else:
            return 3  # 冬
    
    def get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """基本統計情報"""
        return {
            'total_records': len(df),
            'sales_stats': {
                'mean': float(df['sales'].mean()),
                'std': float(df['sales'].std()),
                'min': float(df['sales'].min()),
                'max': float(df['sales'].max())
            },
            'customers_stats': {
                'mean': float(df['customers'].mean()),
                'std': float(df['customers'].std()),
                'min': int(df['customers'].min()),
                'max': int(df['customers'].max())
            },
            'weather_distribution': df['weather'].value_counts().to_dict()
        }
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """詳細統計情報"""
        # processed_dataがない場合は生データを使用
        if self.processed_data is None:
            if self.data is None:
                return {}
            df = self.data.copy()
            # 必要な特徴量を追加
            df['weekday'] = df['date'].dt.weekday
            df['is_holiday'] = df['date'].apply(
                lambda x: x.date() in self.jp_holidays
            ).astype(int)
        else:
            df = self.processed_data
        
        # 祝日データの平均を計算（NaNチェック付き）
        holiday_data = df[df['is_holiday'] == 1]['sales']
        regular_data = df[df['is_holiday'] == 0]['sales']
        
        holiday_avg = float(holiday_data.mean()) if len(holiday_data) > 0 and not holiday_data.isna().all() else 0.0
        regular_avg = float(regular_data.mean()) if len(regular_data) > 0 and not regular_data.isna().all() else 0.0
        
        return {
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'monthly_sales': df.groupby(df['date'].dt.month)['sales'].mean().to_dict(),
            'weekday_sales': df.groupby('weekday')['sales'].mean().to_dict(),
            'weather_impact': df.groupby('weather')['sales'].mean().to_dict(),
            'holiday_impact': {
                'holiday_avg': holiday_avg,
                'regular_avg': regular_avg
            }
        }
    
    def has_data(self) -> bool:
        """データが読み込まれているかチェック"""
        return self.data is not None and len(self.data) > 0
    
    def get_processed_data(self) -> pd.DataFrame:
        """処理済みデータを取得"""
        return self.processed_data if self.processed_data is not None else self.data