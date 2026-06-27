import os
from dotenv import load_dotenv
from google import genai

# .env の読み込み
load_dotenv()

# APIキー取得
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("エラー: GOOGLE_API_KEY が設定されていません")
    exit(1)

# Gemini API クライアント作成
client = genai.Client(api_key=api_key)

# モデル呼び出し
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="こんにちは。簡単に自己紹介してください。"
)

print("APIの接続に成功しました！")
print("\nGeminiからの応答:")
print(response.text)
