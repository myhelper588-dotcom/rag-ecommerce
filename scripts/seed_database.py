import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = "./data/ecommerce.db"

def create_tables(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            id          INTEGER PRIMARY KEY,
            code        TEXT UNIQUE,
            type        TEXT,
            value       REAL,
            min_order   REAL,
            max_uses    INTEGER,
            uses_count  INTEGER DEFAULT 0,
            active      INTEGER DEFAULT 1,
            starts_at   TEXT,
            expires_at  TEXT,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS promo_usage (
            id          INTEGER PRIMARY KEY,
            promo_id    INTEGER,
            order_id    TEXT,
            customer_id INTEGER,
            discount    REAL,
            used_at     TEXT
        );

        CREATE TABLE IF NOT EXISTS promo_segments (
            id          INTEGER PRIMARY KEY,
            promo_id    INTEGER,
            segment     TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id           INTEGER PRIMARY KEY,
            order_number TEXT,
            customer_id  INTEGER,
            total_price  REAL,
            status       TEXT,
            promo_code   TEXT,
            created_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS analytics (
            id          INTEGER PRIMARY KEY,
            date        TEXT,
            promo_id    INTEGER,
            sessions    INTEGER,
            conversions INTEGER,
            revenue     REAL
        );
    """)
    conn.commit()
    print("✅ Tables created")

def seed_promo_codes(conn):
    cursor = conn.cursor()
    now = datetime.now()

    promos = [
        # (code, type, value, min_order, max_uses, active, starts_at, expires_at)
        ("WELCOME10",  "percentage", 10.0, 0.0,    1000, 1,
         (now - timedelta(days=90)).isoformat(),
         (now + timedelta(days=90)).isoformat()),

        ("SUMMER20",   "percentage", 20.0, 50.0,   500,  1,
         (now - timedelta(days=30)).isoformat(),
         (now + timedelta(days=30)).isoformat()),

        ("FLASH30",    "percentage", 30.0, 100.0,  200,  1,
         (now - timedelta(days=2)).isoformat(),
         (now + timedelta(days=2)).isoformat()),

        ("FREESHIP",   "shipping",   0.0,  30.0,   2000, 1,
         (now - timedelta(days=60)).isoformat(),
         (now + timedelta(days=60)).isoformat()),

        ("VIP15",      "percentage", 15.0, 75.0,   300,  1,
         (now - timedelta(days=45)).isoformat(),
         (now + timedelta(days=45)).isoformat()),

        ("SAVE5EUR",   "fixed",      5.0,  40.0,   500,  1,
         (now - timedelta(days=15)).isoformat(),
         (now + timedelta(days=15)).isoformat()),

        ("NEWCLIENT",  "percentage", 12.0, 0.0,    1000, 1,
         (now - timedelta(days=120)).isoformat(),
         (now + timedelta(days=120)).isoformat()),

        ("BLACKFRI40", "percentage", 40.0, 150.0,  1000, 0,
         (now - timedelta(days=200)).isoformat(),
         (now - timedelta(days=170)).isoformat()),

        ("XMAS25",     "percentage", 25.0, 80.0,   800,  0,
         (now - timedelta(days=180)).isoformat(),
         (now - timedelta(days=150)).isoformat()),

        ("LOYALTY20",  "percentage", 20.0, 100.0,  150,  1,
         (now - timedelta(days=10)).isoformat(),
         (now + timedelta(days=80)).isoformat()),

        ("STUDENT10",  "percentage", 10.0, 0.0,    500,  1,
         (now - timedelta(days=60)).isoformat(),
         (now + timedelta(days=120)).isoformat()),

        ("FLASH50",    "percentage", 50.0, 200.0,  100,  1,
         now.isoformat(),
         (now + timedelta(hours=48)).isoformat()),

        ("REFER15",    "percentage", 15.0, 0.0,    2000, 1,
         (now - timedelta(days=90)).isoformat(),
         (now + timedelta(days=90)).isoformat()),

        ("BUNDLE10",   "fixed",      10.0, 120.0,  300,  1,
         (now - timedelta(days=20)).isoformat(),
         (now + timedelta(days=40)).isoformat()),

        ("APP20",      "percentage", 20.0, 0.0,    1000, 1,
         (now - timedelta(days=30)).isoformat(),
         (now + timedelta(days=60)).isoformat()),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO promo_codes
        (code, type, value, min_order, max_uses, active, starts_at, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7],
           (datetime.now() - timedelta(days=random.randint(10, 120))).isoformat())
          for p in promos])
    conn.commit()
    print(f"✅ {len(promos)} promo codes created")

def seed_segments(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, code FROM promo_codes")
    promos = cursor.fetchall()

    segments_map = {
        "WELCOME10":  ["new_customers"],
        "SUMMER20":   ["all"],
        "FLASH30":    ["all"],
        "FREESHIP":   ["all"],
        "VIP15":      ["vip", "loyalty"],
        "SAVE5EUR":   ["all"],
        "NEWCLIENT":  ["new_customers"],
        "LOYALTY20":  ["loyalty"],
        "STUDENT10":  ["students"],
        "FLASH50":    ["vip"],
        "REFER15":    ["referral"],
        "BUNDLE10":   ["all"],
        "APP20":      ["mobile_users"],
    }

    rows = []
    for promo_id, code in promos:
        segs = segments_map.get(code, ["all"])
        for seg in segs:
            rows.append((promo_id, seg))

    cursor.executemany(
        "INSERT INTO promo_segments (promo_id, segment) VALUES (?, ?)", rows
    )
    conn.commit()
    print(f"✅ {len(rows)} segments assigned")

def seed_orders_and_usage(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, value, type, max_uses FROM promo_codes")
    promos = cursor.fetchall()

    statuses = ["paid", "paid", "paid", "pending", "refunded"]
    orders = []
    usage = []

    for i in range(200):
        order_date = datetime.now() - timedelta(days=random.randint(0, 180))
        status = random.choice(statuses)
        total = round(random.uniform(25, 350), 2)
        customer_id = random.randint(1, 80)
        promo_code = None
        discount = 0

        # 40% des commandes ont un promo code
        if random.random() < 0.40 and promos:
            promo = random.choice(promos)
            promo_id, code, value, ptype, max_uses = promo
            promo_code = code

            if ptype == "percentage":
                discount = round(total * value / 100, 2)
            elif ptype == "fixed":
                discount = min(value, total)
            elif ptype == "shipping":
                discount = round(random.uniform(4, 9), 2)

            usage.append((
                promo_id,
                f"ORD-{10000+i}",
                customer_id,
                discount,
                order_date.isoformat()
            ))

        orders.append((
            f"ORD-{10000+i}",
            customer_id,
            total,
            status,
            promo_code,
            order_date.isoformat()
        ))

    cursor.executemany("""
        INSERT INTO orders (order_number, customer_id, total_price, status, promo_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, orders)

    cursor.executemany("""
        INSERT INTO promo_usage (promo_id, order_id, customer_id, discount, used_at)
        VALUES (?, ?, ?, ?, ?)
    """, usage)

    # Met à jour uses_count
    cursor.execute("""
        UPDATE promo_codes SET uses_count = (
            SELECT COUNT(*) FROM promo_usage
            WHERE promo_usage.promo_id = promo_codes.id
        )
    """)

    conn.commit()
    print(f"✅ {len(orders)} orders · {len(usage)} promo usages")

def seed_analytics(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM promo_codes")
    promo_ids = [row[0] for row in cursor.fetchall()]
    rows = []

    for days_ago in range(90):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        for promo_id in random.sample(promo_ids, min(5, len(promo_ids))):
            sessions = random.randint(20, 300)
            conversions = random.randint(1, int(sessions * 0.15))
            revenue = round(conversions * random.uniform(40, 180), 2)
            rows.append((date, promo_id, sessions, conversions, revenue))

    cursor.executemany("""
        INSERT INTO analytics (date, promo_id, sessions, conversions, revenue)
        VALUES (?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"✅ {len(rows)} analytics entries")

def print_summary(conn):
    cursor = conn.cursor()
    print("\n📊 Database summary:")
    for table in ["promo_codes", "promo_usage", "orders", "analytics"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cursor.fetchone()[0]} rows")

    print("\n🎟️ Active promo codes:")
    cursor.execute("""
        SELECT code, type, value, uses_count, max_uses,
               date(expires_at) as expires
        FROM promo_codes WHERE active = 1
        ORDER BY uses_count DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]:12} | {row[1]:10} | {row[2]}% | {row[3]}/{row[4]} uses | expires {row[5]}")

def main():
    os.makedirs("./data", exist_ok=True)
    print("🌱 Creating promo codes database...")
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_promo_codes(conn)
    seed_segments(conn)
    seed_orders_and_usage(conn)
    seed_analytics(conn)
    print_summary(conn)
    conn.close()
    print(f"\n🎉 Database ready: {DB_PATH}")

if __name__ == "__main__":
    main()