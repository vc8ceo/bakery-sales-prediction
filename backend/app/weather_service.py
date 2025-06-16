import requests
import asyncio
from typing import Dict, Any
import json
from datetime import datetime, timedelta

class WeatherService:
    def __init__(self):
        self.livedoor_base_url = "https://weather.tsukumijima.net/api/forecast"
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"
        self.openweather_api_key = None  # 必要に応じて設定
        
    async def get_weather_forecast(self, postal_code: str = "1000001") -> Dict[str, Any]:
        """天気予報取得（Livedoor Weather互換API使用）"""
        try:
            # 郵便番号から地域コードを取得
            city_code = self._get_city_code(postal_code)
            print(f"郵便番号 {postal_code} -> 都市コード {city_code}")
            
            # Livedoor Weather互換APIから天気予報取得
            response = requests.get(
                self.livedoor_base_url,
                params={"city": city_code},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_livedoor_response(data)
            else:
                # フォールバック: デフォルト天気情報
                return self._get_default_weather()
                
        except Exception as e:
            print(f"天気予報取得エラー: {e}")
            return self._get_default_weather()
    
    def _get_city_code(self, postal_code: str) -> str:
        """郵便番号から都市コードを取得"""
        # 主要な郵便番号と都市コードのマッピング
        postal_to_city = {
            "1000001": "130010",  # 東京都千代田区 -> 東京
            "1000002": "130010",  # 東京都千代田区
            "1500001": "130010",  # 東京都渋谷区
            "1600001": "130010",  # 東京都新宿区
            "2310001": "140010",  # 神奈川県横浜市
            "2720832": "120010",  # 千葉県市川市曽谷 -> 千葉
            "2600000": "120010",  # 千葉県千葉市 -> 千葉
            "2750000": "120010",  # 千葉県習志野市 -> 千葉
            "5450001": "270000",  # 大阪府大阪市
            "4600001": "230010",  # 愛知県名古屋市
            "8120001": "400010",  # 福岡県福岡市
            "9800001": "040010",  # 宮城県仙台市
            "0600001": "016010",  # 北海道札幌市
        }
        
        # 直接マッピングがある場合は使用
        if postal_code in postal_to_city:
            return postal_to_city[postal_code]
        
        # 郵便番号の最初の3桁で地域を判定
        prefix = postal_code[:3]
        
        # 日本の郵便番号体系に基づく詳細な地域マッピング
        if prefix.startswith("1"):  # 東京都（100-199）
            return "130010"
        elif prefix.startswith("20") or prefix.startswith("21") or prefix.startswith("23") or prefix.startswith("24") or prefix.startswith("25"):  # 神奈川県（200-219, 230-259）
            return "140010"
        elif prefix.startswith("26") or prefix.startswith("27") or prefix.startswith("28") or prefix.startswith("29"):  # 千葉県（260-299）
            return "120010"
        elif prefix.startswith("30") or prefix.startswith("31") or prefix.startswith("32") or prefix.startswith("33") or prefix.startswith("34") or prefix.startswith("35") or prefix.startswith("36") or prefix.startswith("37") or prefix.startswith("38") or prefix.startswith("39"):  # 埼玉県（330-369）、群馬県（370-379）、栃木県（320-329）、茨城県（300-319）
            if prefix.startswith("30") or prefix.startswith("31"):  # 茨城県（300-319）
                return "080010"
            elif prefix.startswith("32") or prefix.startswith("33"):  # 栃木県（320-329）、埼玉県（330-369）
                if prefix.startswith("32"):
                    return "090010"  # 栃木県
                else:
                    return "110010"  # 埼玉県（さいたま）
            elif prefix.startswith("37"):  # 群馬県（370-379）
                return "100010"
            else:
                return "110010"  # その他は埼玉県扱い
        elif prefix.startswith("22") or prefix.startswith("41") or prefix.startswith("42") or prefix.startswith("43"):  # 静岡県（410-436）、山梨県（400-409）
            if prefix.startswith("22") or prefix.startswith("41") or prefix.startswith("42") or prefix.startswith("43"):
                return "220010"  # 静岡県
            else:
                return "190010"  # 山梨県
        elif prefix.startswith("44") or prefix.startswith("45") or prefix.startswith("46") or prefix.startswith("47") or prefix.startswith("48") or prefix.startswith("49"):  # 愛知県（440-498）、岐阜県（500-509）、三重県（510-519）
            return "230010"  # 愛知県
        elif prefix.startswith("5"):  # 大阪府、京都府、兵庫県など関西（500-679）
            if prefix.startswith("52") or prefix.startswith("53"):  # 滋賀県（520-529）
                return "250010"
            elif prefix.startswith("60") or prefix.startswith("61") or prefix.startswith("62"):  # 京都府（600-629）
                return "260010"
            elif prefix.startswith("53") or prefix.startswith("54") or prefix.startswith("55") or prefix.startswith("56") or prefix.startswith("57") or prefix.startswith("58") or prefix.startswith("59"):  # 大阪府（530-599）
                return "270000"
            elif prefix.startswith("65") or prefix.startswith("66") or prefix.startswith("67"):  # 兵庫県（650-679）
                return "280010"
            elif prefix.startswith("63") or prefix.startswith("64"):  # 奈良県（630-639）
                return "290010"
            elif prefix.startswith("64") or prefix.startswith("65"):  # 和歌山県（640-649）
                return "300010"
            else:
                return "270000"  # デフォルトは大阪府
        elif prefix.startswith("8"):  # 福岡県周辺（800-899）
            return "400010"
        elif prefix.startswith("9"):  # 東北地方（900-999）
            if prefix.startswith("98"):  # 宮城県（980-989）
                return "040010"
            elif prefix.startswith("96") or prefix.startswith("97"):  # 福島県（960-979）
                return "070010"
            elif prefix.startswith("99"):  # 山形県（990-999）
                return "060010"
            else:
                return "040010"  # デフォルトは宮城県
        elif prefix.startswith("0"):  # 北海道と東北北部（000-099）
            if prefix.startswith("01"):  # 秋田県（010-019）
                return "050010"
            elif prefix.startswith("02"):  # 岩手県（020-029）
                return "030010"
            elif prefix.startswith("03"):  # 青森県（030-039）
                return "020010"
            else:  # 北海道（000-099の大部分）
                return "016010"
        else:
            return "130010"  # デフォルトは東京
    
    def _parse_livedoor_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Livedoor APIレスポンス解析"""
        try:
            forecasts = data.get("forecasts", [])
            
            if len(forecasts) > 0:
                today_forecast = forecasts[0]
                
                # 明日の予報（存在する場合）
                tomorrow_forecast = forecasts[1] if len(forecasts) > 1 else today_forecast
                
                location_name = data.get("location", {}).get("city", "不明")
                print(f"取得した地域名: {location_name}")
                
                return {
                    "source": "livedoor",
                    "location": location_name,
                    "today": {
                        "date": today_forecast.get("date"),
                        "weather": today_forecast.get("telop", "不明"),
                        "max_temp": today_forecast.get("temperature", {}).get("max", {}).get("celsius"),
                        "min_temp": today_forecast.get("temperature", {}).get("min", {}).get("celsius"),
                        "precipitation": today_forecast.get("chanceOfRain", {})
                    },
                    "tomorrow": {
                        "date": tomorrow_forecast.get("date"),
                        "weather": tomorrow_forecast.get("telop", "不明"),
                        "max_temp": tomorrow_forecast.get("temperature", {}).get("max", {}).get("celsius"),
                        "min_temp": tomorrow_forecast.get("temperature", {}).get("min", {}).get("celsius"),
                        "precipitation": tomorrow_forecast.get("chanceOfRain", {})
                    },
                    "weather": tomorrow_forecast.get("telop", "晴れ"),  # 予測用
                    "temperature": tomorrow_forecast.get("temperature", {}).get("max", {}).get("celsius", 20)
                }
            else:
                return self._get_default_weather()
                
        except Exception as e:
            print(f"天気データ解析エラー: {e}")
            return self._get_default_weather()
    
    def _get_default_weather(self) -> Dict[str, Any]:
        """デフォルト天気情報"""
        tomorrow = datetime.now() + timedelta(days=1)
        
        return {
            "source": "default",
            "location": "東京",
            "today": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "weather": "晴れ",
                "max_temp": 20,
                "min_temp": 15,
                "precipitation": {"T00_06": "10%", "T06_12": "10%", "T12_18": "20%", "T18_24": "10%"}
            },
            "tomorrow": {
                "date": tomorrow.strftime("%Y-%m-%d"),
                "weather": "晴れ",
                "max_temp": 20,
                "min_temp": 15,
                "precipitation": {"T00_06": "10%", "T06_12": "10%", "T12_18": "20%", "T18_24": "10%"}
            },
            "weather": "晴れ",
            "temperature": 20
        }
    
    async def get_openweather_forecast(self, postal_code: str) -> Dict[str, Any]:
        """OpenWeatherMap APIから天気予報取得（バックアップ用）"""
        if not self.openweather_api_key:
            return self._get_default_weather()
        
        try:
            # 座標取得（簡略化）
            lat, lon = 35.6762, 139.6503  # 東京の座標
            
            response = requests.get(
                f"{self.openweather_base_url}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.openweather_api_key,
                    "units": "metric",
                    "lang": "ja"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_openweather_response(data)
            else:
                return self._get_default_weather()
                
        except Exception as e:
            print(f"OpenWeatherMap APIエラー: {e}")
            return self._get_default_weather()
    
    def _parse_openweather_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """OpenWeatherMap APIレスポンス解析"""
        try:
            forecasts = data.get("list", [])
            
            if len(forecasts) > 0:
                # 明日の予報を取得（24時間後のデータ）
                tomorrow_forecast = forecasts[8] if len(forecasts) > 8 else forecasts[0]
                
                return {
                    "source": "openweathermap",
                    "location": data.get("city", {}).get("name", "不明"),
                    "weather": tomorrow_forecast.get("weather", [{}])[0].get("description", "晴れ"),
                    "temperature": tomorrow_forecast.get("main", {}).get("temp", 20),
                    "humidity": tomorrow_forecast.get("main", {}).get("humidity", 50),
                    "pressure": tomorrow_forecast.get("main", {}).get("pressure", 1013)
                }
            else:
                return self._get_default_weather()
                
        except Exception as e:
            print(f"OpenWeatherMap データ解析エラー: {e}")
            return self._get_default_weather()

# テスト用の非同期関数
async def test_weather_service():
    """天気サービステスト"""
    weather_service = WeatherService()
    
    print("天気予報テスト開始...")
    
    # 東京の天気予報取得
    tokyo_weather = await weather_service.get_weather_forecast("1000001")
    print(f"東京の天気: {json.dumps(tokyo_weather, ensure_ascii=False, indent=2)}")
    
    # 大阪の天気予報取得
    osaka_weather = await weather_service.get_weather_forecast("5450001")
    print(f"大阪の天気: {json.dumps(osaka_weather, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_weather_service())