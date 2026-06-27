from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# サービスアカウント認証
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="こんにちは。簡単に自己紹介してください。"
)

print(response.text)
