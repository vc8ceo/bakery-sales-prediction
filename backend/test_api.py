import requests
import json

def test_data_stats_api():
    """data-stats APIをテスト"""
    base_url = "http://127.0.0.1:8000"
    
    try:
        # model-status APIをテスト
        print("=== Model Status API テスト ===")
        response = requests.get(f"{base_url}/model-status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"モデル訓練済み: {status_data.get('model_trained')}")
            print(f"データ読み込み済み: {status_data.get('data_loaded')}")
        else:
            print(f"Model Status APIエラー: {response.status_code}")
        
        print("\n=== Data Stats API テスト ===")
        # data-stats APIをテスト
        response = requests.get(f"{base_url}/data-stats")
        
        if response.status_code == 200:
            stats_data = response.json()
            print("データ統計情報を正常に取得:")
            print(json.dumps(stats_data, ensure_ascii=False, indent=2))
        else:
            print(f"Data Stats APIエラー: {response.status_code}")
            print(f"エラー内容: {response.text}")
            
    except Exception as e:
        print(f"接続エラー: {e}")

if __name__ == "__main__":
    test_data_stats_api()