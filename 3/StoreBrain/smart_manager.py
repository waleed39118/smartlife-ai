import os
import requests
import json
import sys
from dotenv import load_dotenv

# 1. إعدادات الترميز لضمان قراءة العربية بشكل سليم في Terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# 2. جلب الإعدادات من ملف .env
GROQ_KEY = os.getenv("GROQ_API_KEY")
SHOPIFY_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOP_URL = os.getenv('SHOP_URL')
SHOPIFY_API_VERSION = "2024-04"

def check_environment():
    """التحقق من جاهزية مفاتيح الربط"""
    if not GROQ_KEY:
        print("❌ خطأ: GROQ_API_KEY غير موجود في ملف .env")
        return False
    if not SHOPIFY_TOKEN or not SHOP_URL:
        print("❌ خطأ: بيانات شوبيفاي ناقصة في ملف .env")
        return False
    print(f"📡 نظام التشخيص: تم الاتصال بملف الإعدادات بنجاح.")
    return True

def ask_ai_groq(product_idea):
    """توليد محتوى المنتج باستخدام أحدث موديلات Llama المتاحة"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    # استخدام الموديل الأحدث llama-3.3-70b-versatile أو llama3-70b-8192
    # هذا الموديل هو البديل الرسمي للموديلات التي تم إيقافها
    model_name = "llama-3.3-70b-versatile"
    
    prompt_text = f"""
    بصفتك خبير تسويق محترف، قم بإنشاء منتج شوبيفاي باللغة العربية لـ: '{product_idea}'.
    يجب أن يكون الرد بصيغة JSON فقط ويحتوي على المفاتيح التالية:
    "title": اسم المنتج بشكل تسويقي جذاب.
    "description": وصف HTML غني يتضمن الميزات باستخدام <ul> و <li>.
    "tags": كلمات دلالية مفصولة بفاصلة.
    تأكد أن النص بالكامل بالعربية الفصحى الجذابة.
    """

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user", 
                "content": prompt_text
            }
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.6
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ خطأ من السيرفر ({response.status_code}): {response.text}")
            # إذا فشل الموديل الجديد، نجرب موديل Llama 3.1 كخيار احتياطي
            if "model_not_found" in response.text or "decommissioned" in response.text:
                print("🔄 جاري تجربة موديل احتياطي (Llama 3.1)...")
                payload["model"] = "llama-3.1-8b-instant"
                response = requests.post(url, headers=headers, json=payload, timeout=30)
            else:
                return None
            
        result = response.json()
        content = result['choices'][0]['message']['content']
        return json.loads(content)
        
    except Exception as e:
        print(f"❌ خطأ تقني في الاتصال بـ Groq: {str(e)}")
        return None

def upload_to_shopify(details, price):
    """رفع المنتج النهائي إلى شوبيفاي مع السعر وحالة النشاط"""
    endpoint = f"https://{SHOP_URL}/admin/api/{SHOPIFY_API_VERSION}/products.json"
    
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json"
    }
    
    product_payload = {
        "product": {
            "title": details.get('title'),
            "body_html": details.get('description'),
            "tags": details.get('tags'),
            "status": "active",
            "variants": [
                {
                    "price": price,
                    "inventory_management": "shopify"
                }
            ]
        }
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=product_payload, timeout=30)
        if response.status_code == 201:
            return response.json().get('product')
        else:
            print(f"❌ خطأ في شوبيفاي API: {response.text}")
            return None
    except Exception as e:
        print(f"❌ فشل الاتصال بشوبيفاي: {str(e)}")
        return None

def main():
    print("\n" + "="*55)
    print("      🚀 STOREBRAIN AI ENGINE v6.7 (UP-TO-DATE)    ")
    print("="*55)
    
    if not check_environment():
        return

    product_idea = input("\n💡 أدخل فكرة المنتج: ").strip()
    product_price = input("💰 حدد السعر: ").strip()

    # التحقق من أن السعر يحتوي على أرقام
    if not product_idea or not any(char.isdigit() for char in product_price):
        print("⚠️ يرجى إدخال اسم منتج صالح وسعر رقمي.")
        return

    print("\n🧠 جاري استدعاء المحرك الذكي (Llama 3.3)...")
    ai_data = ask_ai_groq(product_idea)
    
    if ai_data:
        print(f"✅ تم إنشاء المحتوى: {ai_data.get('title')}")
        print("📤 جاري رفع المنتج إلى متجرك...")
        
        success_product = upload_to_shopify(ai_data, product_price)
        if success_product:
            admin_url = f"https://{SHOP_URL}/admin/products/{success_product.get('id')}"
            print("\n" + "★"*55)
            print("🎉 مبروك! المنتج أصبح متاحاً الآن في متجرك.")
            print(f"🔗 رابط المعاينة: {admin_url}")
            print("★"*55 + "\n")
        else:
            print("❌ تعذر رفع المنتج لشوبيفاي. تأكد من صحة التوكن ورابط المتجر.")
    else:
        print("❌ فشل الذكاء الاصطناعي في الاستجابة.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 تم إغلاق البرنامج.")
        sys.exit(0)