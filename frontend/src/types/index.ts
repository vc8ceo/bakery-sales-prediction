export interface ModelStatusType {
  model_trained: boolean;
  data_loaded: boolean;
  model_path: string | null;
}

export interface User {
  id: number;
  email: string;
  username: string;
  store_name: string | null;
  postal_code: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface UserUpdateRequest {
  username?: string;
  store_name?: string;
  postal_code?: string;
  password?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  store_name?: string;
  postal_code?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DashboardStats {
  total_data_points: number;
  date_range: {
    start: string | null;
    end: string | null;
  };
  latest_prediction: PredictionHistoryItem | null;
  model_status: {
    trained: boolean;
    data_loaded: boolean;
  };
  sales_trend: Array<{
    month: string;
    avg_sales: number;
  }>;
  weather_impact: Record<string, number>;
}

export interface PredictionHistoryItem {
  id: number;
  prediction_date: string;
  predicted_sales: number;
  predicted_customers: number;
  weather_condition: string | null;
  temperature: number | null;
  created_at: string;
}

export interface PredictionResult {
  date: string;
  predicted_sales: number;
  predicted_customers: number;
  weather_forecast: WeatherForecast;
  confidence_interval: ConfidenceInterval;
}

export interface WeatherForecast {
  source: string;
  location: string;
  today: DayForecast;
  tomorrow: DayForecast;
  weather: string;
  temperature: number;
}

export interface DayForecast {
  date: string;
  weather: string;
  max_temp: number | null;
  min_temp: number | null;
  precipitation: Record<string, string>;
}

export interface ConfidenceInterval {
  sales_lower: number;
  sales_upper: number;
  customers_lower: number;
  customers_upper: number;
}

export interface DataStats {
  total_records?: number;
  date_range: {
    start: string | null;
    end: string | null;
  };
  columns?: string[];
  summary?: any;
  monthly_sales?: Record<string, number>;
  weekday_sales?: Record<string, number>;
  weather_impact?: Record<string, number>;
  holiday_impact?: {
    holiday_avg: number;
    regular_avg: number;
  };
}

export interface UploadResult {
  message: string;
  records_count: number;
  date_range: {
    start: string;
    end: string;
  };
  stats: {
    total_records: number;
    sales_stats: {
      mean: number;
      std: number;
      min: number;
      max: number;
    };
    customers_stats: {
      mean: number;
      std: number;
      min: number;
      max: number;
    };
    weather_distribution: Record<string, number>;
  };
}

export interface TrainResult {
  message: string;
  metrics: {
    sales_metrics: ModelMetrics;
    customers_metrics: ModelMetrics;
    sales_feature_importance: Record<string, number>;
    customers_feature_importance: Record<string, number>;
    training_samples: number;
    test_samples: number;
  };
  model_saved: string;
}

export interface ModelMetrics {
  mae: number;
  mse: number;
  rmse: number;
  r2: number;
  mape: number;
}