import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

response = requests.get(url)
models = response.json()

print("--- 🔍 الموديلات المتاحة لحسابك الآن ---")
for m in models.get('models', []):
    if 'generateContent' in m.get('supportedGenerationMethods', []):
        print(f"Model: {m['name']}")