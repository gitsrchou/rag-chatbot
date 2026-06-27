import os
from dotenv import load_dotenv
import google.genai as genai

# 環境変数の読み込み
load_dotenv()

# APIキーの取得
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("エラー: GOOGLE_API_KEYが設定されていません")
    exit(1)

# Gemini APIの設定
genai.configure(api_key=api_key)

# モデルの初期化
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# テスト用のプロンプト
response = model.generate_content("こんにちは。簡単に自己紹介してください。")

print("APIの接続に成功しました！")
print("\nGeminiからの応答:")
print(response.text)
