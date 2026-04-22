import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOP_URL = os.getenv('SHOP_URL')
API_VERSION = "2024-04"

def create_test_product():
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/products.json"
    
    headers = {
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }

    # بيانات المنتج الجديد
    new_product = {
        "product": {
            "title": "StoreBrain Magic Tool",
            "body_html": "<strong>This product was created by StoreBrain AI!</strong>",
            "vendor": "StoreBrain Labs",
            "product_type": "Digital Assistant",
            "status": "draft" # سنجعله مسودة أولاً لكي تراه في لوحة التحكم
        }
    }

    print("🚀 Sending new product to Shopify...")
    
    try:
        response = requests.post(url, json=new_product, headers=headers)
        
        if response.status_code == 201:
            product_data = response.json()['product']
            print(f"\n✅ SUCCESS! Product created.")
            print(f"📦 Product ID: {product_data['id']}")
            print(f"🔗 View it here: https://{SHOP_URL}/admin/products/{product_data['id']}")
        else:
            print(f"\n❌ Failed to create product. Status: {response.status_code}")
            print(f"Details: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    create_test_product()