import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from tools.privacy_tool import anonymize
load_dotenv()

def get_shopify_headers():
    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    print(f"🔑 Token utilisé : {token[:15] if token else 'NONE'}...")
    return {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

def get_shopify_base_url():
    shop_url = os.getenv("SHOPIFY_SHOP_URL")
    version = os.getenv("SHOPIFY_API_VERSION", "2026-04")
    return f"https://{shop_url}/admin/api/{version}"

@tool
def shopify_get_products(query: str) -> str:
    """
    Récupère les produits depuis Shopify.
    Utilise cet outil pour : stock produits, catalogue,
    prix, variantes, collections, inventaire.
    Le paramètre query peut contenir des filtres comme :
    'limit=10', 'title=manteau', 'collection_id=123'
    """
    try:
        base_url = get_shopify_base_url()
        params = {}

        # Parse les filtres simples
        if query and query != "all":
            for part in query.split("&"):
                if "=" in part:
                    key, value = part.split("=", 1)
                    params[key.strip()] = value.strip()

        params["limit"] = params.get("limit", "20")
        params["fields"] = "id,title,product_type,variants,status"

        response = requests.get(
            f"{base_url}/products.json",
            headers=get_shopify_headers(),
            params=params
        )

        if response.status_code != 200:
            return f"❌ Erreur Shopify : {response.status_code}"

        products = response.json().get("products", [])

        if not products:
            return "Aucun produit trouvé"

        result = f"📦 {len(products)} produit(s) trouvé(s) :\n\n"
        for p in products:
            variants = p.get("variants", [])
            total_stock = sum(v.get("inventory_quantity", 0) for v in variants)
            price = variants[0].get("price", "N/A") if variants else "N/A"
            result += f"• {p['title']} | Prix: {price}€ | Stock: {total_stock}\n"

        return result

    except Exception as e:
        return f"❌ Erreur : {str(e)}"

@tool
def shopify_get_orders(query: str) -> str:
    """
    Récupère les commandes depuis Shopify.
    Utilise cet outil pour : commandes récentes, chiffre
    d'affaires, statut commandes, historique clients.
    Le paramètre query peut contenir :
    'limit=10', 'status=paid', 'created_at_min=2026-01-01'
    """
    try:
        base_url = get_shopify_base_url()
        params = {"status": "any"}

        if query and query != "all":
            for part in query.split("&"):
                if "=" in part:
                    key, value = part.split("=", 1)
                    params[key.strip()] = value.strip()

        params["limit"] = params.get("limit", "20")
        params["fields"] = "id,name,total_price,financial_status,created_at,line_items"

        response = requests.get(
            f"{base_url}/orders.json",
            headers=get_shopify_headers(),
            params=params
        )

        if response.status_code != 200:
            return f"❌ Erreur Shopify : {response.status_code}"

        orders = response.json().get("orders", [])

        if not orders:
            return "Aucune commande trouvée"

        total_revenue = sum(float(o.get("total_price", 0)) for o in orders)
        result = f"🛒 {len(orders)} commande(s) | CA total : {total_revenue:.2f}€\n\n"

        for o in orders:
            result += f"• {o['name']} | {o['total_price']}€ | {o['financial_status']} | {o['created_at'][:10]}\n"

        return anonymize(result)

    except Exception as e:
        return f"❌ Erreur : {str(e)}"