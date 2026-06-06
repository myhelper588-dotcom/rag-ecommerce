import os
import sqlite3
from langchain.tools import tool
from dotenv import load_dotenv
from tools.privacy_tool import anonymize
load_dotenv()

DB_PATH = "./data/ecommerce.db"

def get_connection():
    """Retourne une connexion à la BDD"""
    return sqlite3.connect(DB_PATH)

@tool
def query_database(sql_query: str) -> str:
    """
    Exécute une requête SQL sur la base de données eCommerce.
    Utilise cet outil pour : analytics, historique commandes,
    retours produits, taux de conversion, CA par catégorie,
    performance produits, KPIs financiers.

    Schéma disponible :
    - products (id, sku, title, category, price, cost, stock)
    - orders (id, order_number, customer_id, customer_name, 
              total_price, status, created_at)
    - order_items (id, order_id, product_id, quantity, price)
    - returns (id, order_id, product_id, reason, amount, created_at)
    - analytics (id, date, category, sessions, conversions, revenue)

    Règles :
    - Toujours utiliser LIMIT (max 20)
    - Utiliser COUNT, SUM, AVG pour agréger
    - Ne jamais retourner customer_name — utiliser customer_id
    - Dates au format YYYY-MM-DD
    """
    try:
        # Sécurité — uniquement SELECT
        if not sql_query.strip().upper().startswith("SELECT"):
            return "❌ Seules les requêtes SELECT sont autorisées"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "Aucun résultat trouvé"

        # Formatage lisible
        result = f"📊 {len(rows)} résultat(s) :\n\n"
        result += " | ".join(columns) + "\n"
        result += "-" * 50 + "\n"
        
        for row in rows:
            result += " | ".join(str(v) for v in row) + "\n"
        return anonymize(result)

    except Exception as e:
        return f"❌ Erreur SQL : {str(e)}"