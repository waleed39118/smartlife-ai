import os
import requests
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SHOP_URL = os.getenv('SHOP_URL')

scopes = "read_products,write_products,read_inventory,write_inventory,read_orders,write_orders"
redirect_uri = "http://localhost:8000/callback"

auth_url = f"https://{SHOP_URL}/admin/oauth/authorize?client_id={CLIENT_ID}&scope={scopes}&redirect_uri={redirect_uri}"

print("\n" + "="*50)
print("🤖 أداة صيد التوكن (Token Catcher) - StoreBrain")
print("="*50 + "\n")

print("الخطوة 1: اضغط على هذا الرابط (أو انسخه في متصفحك):")
print(f"\n👉  {auth_url}  👈\n")
print("الخطوة 2: ستفتح صفحة شوبيفاي، اضغط على زر 'Install' أو 'تثبيت'.")
print("الخطوة 3: سيتم توجيهك لصفحة بيضاء معطلة (هذا فخ مقصود).")
print("الخطوة 4: انسخ الرابط الطويل جداً من أعلى المتصفح والصقه هنا:")

redirected_url = input("\n🔗 الصق الرابط هنا ثم اضغط Enter: ")

try:
    parsed_url = urlparse(redirected_url)
    code = parse_qs(parsed_url.query).get('code')

    if code:
        code = code[0]
        token_url = f"https://{SHOP_URL}/admin/oauth/access_token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code
        }
        
        response = requests.post(token_url, json=payload)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("\n🎉 نجاح ساحق! انسخ التوكن الخاص بك الآن:")
            print(f"\n✅ {token}\n")
        else:
            print(f"\n❌ فشل استخراج التوكن. رسالة شوبيفاي: {response.text}")
    else:
        print("\n❌ لم أتمكن من العثور على الكود في الرابط.")
except Exception as e:
    print(f"\n❌ حدث خطأ: {str(e)}")