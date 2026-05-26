import sqlite3
import os
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('fr_FR')

DB_PATH = "./data/ecommerce.db"

def create_tables(conn):
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            sku TEXT,
            title TEXT,
            category TEXT,
            price REAL,
            cost REAL,
            stock INTEGER,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            order_number TEXT,
            customer_id INTEGER,
            customer_name TEXT,
            total_price REAL,
            status TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL
        );

        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            reason TEXT,
            amount REAL,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY,
            date TEXT,
            category TEXT,
            sessions INTEGER,
            conversions INTEGER,
            revenue REAL
        );
    """)
    conn.commit()
    print("✅ Tables créées")

def seed_products(conn):
    cursor = conn.cursor()
    categories = ["Manteaux", "Vestes", "Robes", "Pantalons", "Accessoires"]
    products = []
    
    for i in range(50):
        category = random.choice(categories)
        price = round(random.uniform(29, 299), 2)
        cost = round(price * random.uniform(0.3, 0.5), 2)
        products.append((
            f"SKU-{1000+i}",
            fake.catch_phrase(),
            category,
            price,
            cost,
            random.randint(0, 150),
            fake.date_time_this_year().isoformat()
        ))
    
    cursor.executemany("""
        INSERT INTO products (sku, title, category, price, cost, stock, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, products)
    conn.commit()
    print(f"✅ {len(products)} produits créés")

def seed_orders(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, price FROM products")
    products = cursor.fetchall()
    
    statuses = ["paid", "paid", "paid", "pending", "refunded"]
    orders = []
    order_items = []
    returns = []
    return_reasons = [
        "Taille incorrecte",
        "Article défectueux", 
        "Ne correspond pas à la description",
        "Changement d'avis",
        "Délai de livraison trop long"
    ]

    for i in range(200):
        order_date = datetime.now() - timedelta(days=random.randint(0, 180))
        status = random.choice(statuses)
        nb_items = random.randint(1, 4)
        selected_products = random.sample(products, min(nb_items, len(products)))
        total = sum(p[1] for p in selected_products)
        customer_id = random.randint(1, 80)

        orders.append((
            f"ORD-{10000+i}",
            customer_id,
            f"Client #{customer_id}",
            round(total, 2),
            status,
            order_date.isoformat()
        ))

        order_id = i + 1
        for product in selected_products:
            order_items.append((
                order_id,
                product[0],
                1,
                product[1]
            ))

        # 20% de retours
        if status == "paid" and random.random() < 0.2:
            product = random.choice(selected_products)
            returns.append((
                order_id,
                product[0],
                random.choice(return_reasons),
                round(product[1] * 0.85, 2),
                order_date.isoformat()
            ))

    cursor.executemany("""
        INSERT INTO orders (order_number, customer_id, customer_name, 
                           total_price, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, orders)

    cursor.executemany("""
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
    """, order_items)

    cursor.executemany("""
        INSERT INTO returns (order_id, product_id, reason, amount, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, returns)

    conn.commit()
    print(f"✅ {len(orders)} commandes créées")
    print(f"✅ {len(returns)} retours créés")

def seed_analytics(conn):
    cursor = conn.cursor()
    categories = ["Manteaux", "Vestes", "Robes", "Pantalons", "Accessoires"]
    analytics = []

    for days_ago in range(180):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        for category in categories:
            sessions = random.randint(100, 1000)
            conversions = random.randint(5, int(sessions * 0.05))
            revenue = round(conversions * random.uniform(50, 200), 2)
            analytics.append((date, category, sessions, conversions, revenue))

    cursor.executemany("""
        INSERT INTO analytics (date, category, sessions, conversions, revenue)
        VALUES (?, ?, ?, ?, ?)
    """, analytics)
    conn.commit()
    print(f"✅ {len(analytics)} entrées analytics créées")

def main():
    os.makedirs("./data", exist_ok=True)
    print("🌱 Création de la base de données...")
    
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_products(conn)
    seed_orders(conn)
    seed_analytics(conn)
    conn.close()
    
    print(f"\n🎉 Base de données créée : {DB_PATH}")

if __name__ == "__main__":
    main()