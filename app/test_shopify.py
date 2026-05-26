import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SHOPIFY_ACCESS_TOKEN")
shop_url = os.getenv("SHOPIFY_SHOP_URL")
api_version = os.getenv("SHOPIFY_API_VERSION")

print(f"Token : {token[:10]}...")
print(f"Shop : {shop_url}")
print(f"Version : {api_version}")

headers = {"X-Shopify-Access-Token": token}
url = f"https://{shop_url}/admin/api/{api_version}/products.json"

print(f"\nAppel : {url}")
response = requests.get(url, headers=headers)
print(f"Status : {response.status_code}")
print(response.text[:500])