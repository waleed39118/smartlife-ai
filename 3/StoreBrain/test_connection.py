import os
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOP_URL = os.getenv('SHOP_URL')
API_VERSION = "2024-04"

def check_shopify_connection():
    # URL to fetch shop details
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/shop.json"
    
    headers = {
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }

    print(f"Connecting to: {SHOP_URL}...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            shop_info = response.json()['shop']
            print("\nSUCCESS: Connection Established!")
            print(f"Store Name: {shop_info['name']}")
            print(f"Currency: {shop_info['currency']}")
            print("\nStoreBrain is now officially online!")
        else:
            print(f"\nFAILED: Connection Error. Status Code: {response.status_code}")
            print(f"Details: {response.text}")
            
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    check_shopify_connection()