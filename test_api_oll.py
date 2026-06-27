import requests

# Ollama のエンドポイント
OLLAMA_URL = "http://localhost:11434/api/generate"

# 使用するローカルモデル名（例：phi3:mini、gemma2:2b など）
MODEL_NAME = "phi3:mini"

# プロンプト
prompt = "こんにちは。簡単に自己紹介してください。"

# リクエストペイロード
payload = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "stream": False,  # ストリーミングしない場合
    "options": {
        "num_ctx": 512,      # メモリ節約
        "num_thread": 2      # CPU負荷とメモリ節約
    }
}

# API 呼び出し
response = requests.post(OLLAMA_URL, json=payload)

# 結果の取り出し
if response.status_code == 200:
    data = response.json()
    print("Ollama のローカルモデルに接続成功！\n")
    print("モデルからの応答:")
    print(data.get("response"))
else:
    print("エラー:", response.status_code, response.text)
