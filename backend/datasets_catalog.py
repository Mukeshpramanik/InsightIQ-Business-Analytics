"""
InsightIQ Multi-Dataset Catalog and Specialized Domain Generators.
Generates realistic, domain-specific benchmark datasets:
1. Sales & Revenue Analytics (B2B Enterprise Technology & Contracts)
2. Customer Analytics (Loyalty Cohorts & Omnichannel Retail)
3. E-commerce Analytics (D2C Online Store & Digital Marketing)
4. HR Analytics (Workforce Headcount, Payroll & Productivity Return)
"""
import os
import random
import datetime
import pandas as pd
from typing import List, Dict, Any
from backend.database import get_db_connection, init_db, db_session
from backend.seed_data import DATA_DIR

# ==============================================================================
# DATASET 1: Sales & Revenue Analytics (B2B Enterprise Tech & Professional Services)
# ==============================================================================

B2B_CATEGORIES = {
    "Cloud Infrastructure": {
        "Compute Blades": [("HyperScale Compute Blade 64C", 4800.0, 3100.0), ("Dense GPU Inference Blade", 9500.0, 6400.0)],
        "Storage Arrays": [("Enterprise NVMe SAN Array 100TB", 14500.0, 9800.0), ("Hybrid Object Storage Pod", 7200.0, 4800.0)],
        "Network Fabric": [("100GbE Spine Core Switch", 6200.0, 4100.0), ("ToR Leaf Switch 48-Port", 3400.0, 2200.0)]
    },
    "Cybersecurity": {
        "Network Defense": [("NextGen Firewall Appliance", 5800.0, 3600.0), ("DDoS Mitigation Controller", 8400.0, 5400.0)],
        "Identity & Access": [("Zero-Trust SSO Enterprise License", 1800.0, 650.0), ("Privileged Access Manager", 3200.0, 1100.0)],
        "Security Operations": [("Managed SIEM 24/7 Subscription", 4500.0, 2600.0), ("Automated EDR Protection Node", 2100.0, 800.0)]
    },
    "Enterprise Software": {
        "Data Platforms": [("Distributed SQL Cluster License", 8900.0, 2900.0), ("Real-Time Streaming Kafka Core", 6400.0, 2100.0)],
        "Developer Tools": [("Enterprise DevOps CI/CD Suite", 3500.0, 1200.0), ("AI Code Assist Organization Pack", 2400.0, 850.0)],
        "Analytics": [("Insight Engine Enterprise Tier", 5200.0, 1800.0), ("Data Mesh Governance Suite", 4100.0, 1400.0)]
    },
    "Professional Services": {
        "Advisory": [("Cloud Architecture Roadmap Audit", 3800.0, 2200.0), ("Enterprise Cybersecurity Readiness Assessment", 4600.0, 2800.0)],
        "Implementation": [("Core Infrastructure Migration Sprint", 7500.0, 4500.0), ("Disaster Recovery Failover Drill", 3200.0, 1900.0)],
        "Support": [("24/7 Dedicated Technical Account Manager", 6000.0, 3400.0), ("Executive Escalation Support Retainer", 2500.0, 1400.0)]
    }
}

B2B_CLIENTS = [
    ("Apex Global Technologies", "Strategic Enterprise", "North America", "New York", "NY"),
    ("Quantum Dynamics Labs", "Strategic Enterprise", "North America", "San Francisco", "CA"),
    ("Meridian Health Systems", "Strategic Enterprise", "North America", "Chicago", "IL"),
    ("Vanguard Financial Corp", "Strategic Enterprise", "North America", "Boston", "MA"),
    ("Starlight Media Networks", "Mid-Market Commercial", "North America", "Los Angeles", "CA"),
    ("Horizon Logistics Int.", "Mid-Market Commercial", "North America", "Atlanta", "GA"),
    ("Nexis Energy Solutions", "Mid-Market Commercial", "North America", "Houston", "TX"),
    ("Cascade Retail Group", "Mid-Market Commercial", "North America", "Seattle", "WA"),
    ("AlphaBio Research Inc.", "Public Sector & Edu", "North America", "Washington D.C.", "DC"),
    ("Metro Transit Authority", "Public Sector & Edu", "North America", "Denver", "CO"),
    ("Bayern Automation AG", "Strategic Enterprise", "EMEA", "Munich", "Bavaria"),
    ("Nordic Cloud Telecom", "Strategic Enterprise", "EMEA", "Stockholm", "Stockholm"),
    ("Helvetia Asset Trust", "Strategic Enterprise", "EMEA", "Zurich", "Zurich"),
    ("Seine Interactive SAS", "Mid-Market Commercial", "EMEA", "Paris", "Ile-de-France"),
    ("Thames FinTech Partners", "Mid-Market Commercial", "EMEA", "London", "Greater London"),
    ("Tokio Systems Kabushiki", "Strategic Enterprise", "APAC", "Tokyo", "Kanto"),
    ("SingaPort Maritime Logic", "Strategic Enterprise", "APAC", "Singapore", "Central"),
    ("Austral Wind Utilities", "Mid-Market Commercial", "APAC", "Sydney", "NSW"),
    ("Seoul Semicon Foundry", "Strategic Enterprise", "APAC", "Seoul", "Gyeonggi"),
    ("Sao Paulo Agrotech SA", "Mid-Market Commercial", "Latin America", "Sao Paulo", "SP")
]

def generate_sales_revenue_records(count: int = 2800) -> List[Dict[str, Any]]:
    """Generates B2B Enterprise technology deals spanning 2024-01-01 to 2025-12-31."""
    random.seed(101) # Stable deterministic seed for Dataset 1
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days
    
    records = []
    for i in range(1, count + 1):
        # B2B quarterly closing cycle (higher weight at quarter ends: March, June, Sept, Dec)
        day_offset = random.randint(0, total_days)
        order_date = start_date + datetime.timedelta(days=day_offset)
        
        # Quarter end deal surge
        if order_date.month in [3, 6, 9, 12] and order_date.day > 18 and random.random() < 0.35:
            pass
            
        client = random.choice(B2B_CLIENTS)
        client_name, segment, region, city, state = client
        cust_id = f"ACC-{abs(hash(client_name)) % 10000:04d}"
        
        category = random.choice(list(B2B_CATEGORIES.keys()))
        sub_cat = random.choice(list(B2B_CATEGORIES[category].keys()))
        prod_tuple = random.choice(B2B_CATEGORIES[category][sub_cat])
        prod_name, unit_price, unit_cost = prod_tuple
        prod_id = f"SKU-{abs(hash(prod_name)) % 10000:04d}"
        
        # Volume units
        quantity = random.choices([1, 2, 3, 5, 8, 12, 20], weights=[0.40, 0.25, 0.15, 0.10, 0.05, 0.03, 0.02])[0]
        # Corporate enterprise discount
        discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[0.50, 0.25, 0.15, 0.07, 0.03])[0]
        shipping_cost = round(random.uniform(50.0, 350.0), 2)
        
        gross = quantity * unit_price
        revenue = round(gross * (1.0 - discount), 2)
        total_cost = round(quantity * unit_cost, 2)
        profit = round(revenue - total_cost - shipping_cost, 2)
        
        order_id = f"INV-{order_date.year}-{10000 + i}"
        
        records.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": cust_id,
            "customer_name": client_name,
            "segment": segment,
            "region": region,
            "country": "United States" if region == "North America" else ("United Kingdom" if city == "London" else "Germany" if city == "Munich" else "International"),
            "city": city,
            "state": state,
            "category": category,
            "sub_category": sub_cat,
            "product_id": prod_id,
            "product_name": prod_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
            "revenue": revenue,
            "cost": total_cost,
            "profit": profit
        })
        
    return records

def seed_sales_revenue_dataset(force: bool = False) -> str:
    """Idempotently seeds Dataset 1: Sales & Revenue Analytics."""
    init_db()
    ds_id = "sales_revenue_analytics"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, row_count FROM datasets WHERE id = ?", (ds_id,))
    existing = cursor.fetchone()
    if existing and not force:
        conn.close()
        return ds_id
        
    records = generate_sales_revenue_records(2800)
    df = pd.DataFrame(records)
    csv_path = os.path.join(DATA_DIR, f"{ds_id}_clean.csv")
    df.to_csv(csv_path, index=False)
    
    cursor.execute("""
        INSERT OR REPLACE INTO datasets (id, name, description, row_count, column_count, is_sample, file_path)
        VALUES (?, ?, ?, ?, ?, 1, ?)
    """, (
        ds_id,
        "B2B Sales & Revenue Analytics",
        "Enterprise technology sales contracts, cloud infrastructure subscriptions, cybersecurity appliances, and professional consulting deals across corporate accounts.",
        len(records),
        len(df.columns),
        csv_path
    ))
    
    cursor.execute("DELETE FROM sales_data WHERE dataset_id = ?", (ds_id,))
    
    insert_records = []
    for r in records:
        insert_records.append((
            ds_id, r["order_id"], r["order_date"], r["customer_id"], r["customer_name"],
            r["segment"], r["region"], r["country"], r["city"], r["state"],
            r["category"], r["sub_category"], r["product_id"], r["product_name"],
            r["quantity"], r["unit_price"], r["discount"], r["shipping_cost"],
            r["revenue"], r["cost"], r["profit"]
        ))
        
    cursor.executemany("""
        INSERT INTO sales_data (
            dataset_id, order_id, order_date, customer_id, customer_name, segment,
            region, country, city, state, category, sub_category, product_id,
            product_name, quantity, unit_price, discount, shipping_cost, revenue, cost, profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_records)
    
    conn.commit()
    conn.close()
    return ds_id

# ==============================================================================
# DATASET 2: Customer Analytics (Loyalty Cohorts & Omnichannel Retail)
# ==============================================================================

CUSTOMER_CATEGORIES = {
    "Health & Nutrition": {
        "Supplements": [("Whey Protein Isolate 2kg", 68.0, 32.0), ("Plant-Based Collagen Peptides", 42.0, 18.0), ("Daily Micronutrient Complex", 34.0, 12.0)],
        "Superfoods": [("Organic Ceremonial Matcha", 38.0, 16.0), ("Cold-Pressed Green Cleanse 6-Pack", 45.0, 22.0)]
    },
    "Apparel & Activewear": {
        "Performance Tops": [("Seamless Moisture-Wicking Tee", 48.0, 18.0), ("Merino Wool Thermal Long Sleeve", 85.0, 38.0)],
        "Bottoms": [("High-Waist Compression Leggings", 78.0, 28.0), ("Four-Way Stretch Trail Shorts", 58.0, 22.0)],
        "Footwear": [("Carbon-Plated Road Runner", 195.0, 95.0), ("Recovery Foam Slide", 45.0, 16.0)]
    },
    "Beauty & Skincare": {
        "Facial Care": [("Hyaluronic Acid Hydrating Serum", 52.0, 18.0), ("Advanced Retinol Night Cream", 64.0, 22.0), ("Vitamin C Glow Essence", 46.0, 15.0)],
        "Sun & Body": [("Mineral Sheer Sunscreen SPF 50", 36.0, 12.0), ("Exfoliating Body Polish", 28.0, 9.0)]
    },
    "Home & Lifestyle": {
        "Recovery & Sleep": [("Weighted Deep Sleep Blanket", 120.0, 55.0), ("Contoured Memory Foam Pillow", 75.0, 30.0)],
        "Mindfulness": [("Eco-Friendly Natural Rubber Yoga Mat", 88.0, 36.0), ("Ultrasonic Stone Aromatherapy Diffuser", 65.0, 25.0)]
    }
}

LOYALTY_TIERS = ["Platinum VIP", "Gold Member", "Silver Member", "Regular Customer"]
LOYALTY_WEIGHTS = [0.15, 0.25, 0.35, 0.25]
RETAIL_REGIONS = ["Metro East", "Metro West", "Suburban South", "Urban North", "Midwest Central"]

LOYALTY_FIRST_NAMES = [
    "Sophia", "Liam", "Olivia", "Noah", "Emma", "Oliver", "Amelia", "James", "Ava", "Elijah",
    "Isabella", "William", "Mia", "Henry", "Evelyn", "Lucas", "Harper", "Benjamin", "Camila", "Theodore",
    "Gianna", "Mateo", "Abigail", "Levi", "Luna", "Sebastian", "Ella", "Daniel", "Elizabeth", "Jack"
]

LOYALTY_LAST_NAMES = [
    "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott",
    "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner"
]

def generate_customer_cohorts(count: int = 300) -> List[Dict[str, Any]]:
    """Generates customer loyalty members with tiered purchasing profiles."""
    random.seed(202)
    cohorts = []
    for i in range(1, count + 1):
        first = random.choice(LOYALTY_FIRST_NAMES)
        last = random.choice(LOYALTY_LAST_NAMES)
        tier = random.choices(LOYALTY_TIERS, weights=LOYALTY_WEIGHTS)[0]
        region = random.choice(RETAIL_REGIONS)
        # Power law frequency probability
        freq_weight = 12 if tier == "Platinum VIP" else 7 if tier == "Gold Member" else 4 if tier == "Silver Member" else 2
        cohorts.append({
            "customer_id": f"LOYAL-{i:04d}",
            "customer_name": f"{first} {last}",
            "segment": tier,
            "region": region,
            "city": f"{region.split()[0]} City",
            "state": "State",
            "freq_weight": freq_weight
        })
    return cohorts

def generate_customer_analytics_records(total_orders: int = 3400) -> List[Dict[str, Any]]:
    """Generates 3,400 customer-centric transactions spanning 2024-01-01 to 2025-12-31."""
    random.seed(202)
    customers = generate_customer_cohorts(300)
    customer_weights = [c["freq_weight"] for c in customers]
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days
    
    records = []
    for i in range(1, total_orders + 1):
        # Time distribution: steady progression with mid-year summer sale and holiday boost
        day_offset = random.randint(0, total_days)
        order_date = start_date + datetime.timedelta(days=day_offset)
        
        cust = random.choices(customers, weights=customer_weights)[0]
        
        category = random.choice(list(CUSTOMER_CATEGORIES.keys()))
        sub_cat = random.choice(list(CUSTOMER_CATEGORIES[category].keys()))
        prod_tuple = random.choice(CUSTOMER_CATEGORIES[category][sub_cat])
        prod_name, unit_price, unit_cost = prod_tuple
        prod_id = f"PROD-{abs(hash(prod_name)) % 10000:04d}"
        
        # Quantity
        quantity = random.choices([1, 2, 3, 4, 6], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]
        
        # Tier discounts: Platinum gets 15%, Gold 10%, Silver 5%, Regular 0%
        base_disc = 0.15 if cust["segment"] == "Platinum VIP" else 0.10 if cust["segment"] == "Gold Member" else 0.05 if cust["segment"] == "Silver Member" else 0.0
        # Occasional promotional coupon
        promo = 0.05 if random.random() < 0.15 else 0.0
        discount = round(min(0.25, base_disc + promo), 2)
        
        shipping_cost = 0.0 if cust["segment"] in ["Platinum VIP", "Gold Member"] else round(random.uniform(3.99, 12.50), 2)
        
        gross = quantity * unit_price
        revenue = round(gross * (1.0 - discount), 2)
        total_cost = round(quantity * unit_cost, 2)
        profit = round(revenue - total_cost - shipping_cost, 2)
        
        order_id = f"LOY-{order_date.year}-{10000 + i}"
        
        records.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": cust["customer_id"],
            "customer_name": cust["customer_name"],
            "segment": cust["segment"],
            "region": cust["region"],
            "country": "United States",
            "city": cust["city"],
            "state": cust["state"],
            "category": category,
            "sub_category": sub_cat,
            "product_id": prod_id,
            "product_name": prod_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
            "revenue": revenue,
            "cost": total_cost,
            "profit": profit
        })
        
    return records

def seed_customer_analytics_dataset(force: bool = False) -> str:
    """Idempotently seeds Dataset 2: Customer Analytics."""
    init_db()
    ds_id = "customer_analytics"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, row_count FROM datasets WHERE id = ?", (ds_id,))
    existing = cursor.fetchone()
    if existing and not force:
        conn.close()
        return ds_id
        
    records = generate_customer_analytics_records(3400)
    df = pd.DataFrame(records)
    csv_path = os.path.join(DATA_DIR, f"{ds_id}_clean.csv")
    df.to_csv(csv_path, index=False)
    
    cursor.execute("""
        INSERT OR REPLACE INTO datasets (id, name, description, row_count, column_count, is_sample, file_path)
        VALUES (?, ?, ?, ?, ?, 1, ?)
    """, (
        ds_id,
        "Customer Loyalty & Omnichannel Analytics",
        "Customer-centric retail loyalty transactions tracking repeat cohorts, member tiers (Platinum, Gold, Silver, Regular), customer lifetime value, and retention.",
        len(records),
        len(df.columns),
        csv_path
    ))
    
    cursor.execute("DELETE FROM sales_data WHERE dataset_id = ?", (ds_id,))
    
    insert_records = []
    for r in records:
        insert_records.append((
            ds_id, r["order_id"], r["order_date"], r["customer_id"], r["customer_name"],
            r["segment"], r["region"], r["country"], r["city"], r["state"],
            r["category"], r["sub_category"], r["product_id"], r["product_name"],
            r["quantity"], r["unit_price"], r["discount"], r["shipping_cost"],
            r["revenue"], r["cost"], r["profit"]
        ))
        
    cursor.executemany("""
        INSERT INTO sales_data (
            dataset_id, order_id, order_date, customer_id, customer_name, segment,
            region, country, city, state, category, sub_category, product_id,
            product_name, quantity, unit_price, discount, shipping_cost, revenue, cost, profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_records)
    
    conn.commit()
    conn.close()
    return ds_id

# ==============================================================================
# DATASET 3: E-commerce Analytics (Global D2C Online Store & Digital Marketing)
# ==============================================================================

ECOMM_CATEGORIES = {
    "Consumer Electronics": {
        "Audio": [("ANC Wireless Headphones Pro", 229.0, 95.0), ("True Wireless Sport Earbuds", 89.0, 32.0), ("Portable Waterproof Bluetooth Speaker", 65.0, 24.0)],
        "Charging & Power": [("100W GaN Desktop Charger Hub", 79.0, 28.0), ("Magnetic Qi2 Fast Power Bank", 54.0, 19.0)],
        "Display & Vision": [("34-Inch Curved WQHD Monitor", 449.0, 260.0), ("4K Ultra HD Streaming Webcam", 129.0, 48.0)]
    },
    "Gaming & Esports": {
        "Keyboards": [("Custom Hot-Swap Mechanical Keyboard", 159.0, 62.0), ("Low-Profile Wireless TKL Board", 119.0, 46.0)],
        "Precision Mice": [("Ultra-Lightweight 49g Gaming Mouse", 85.0, 29.0), ("Ergonomic Vertical Wireless Mouse", 69.0, 25.0)],
        "Audio & Streaming": [("Broadcast Cardioid USB Microphone", 139.0, 52.0), ("Spatial Audio Wireless Headset", 179.0, 68.0)]
    },
    "Apparel & Streetwear": {
        "Outerwear": [("Heavyweight 500GSM Boxy Hoodie", 95.0, 32.0), ("Waterproof Technical Windbreaker", 125.0, 44.0)],
        "Pants": [("Modular Cargo Utility Pants", 88.0, 30.0), ("Relaxed Fit Japanese Denim", 110.0, 42.0)],
        "Accessories": [("Everyday Weatherproof Sling Bag", 58.0, 20.0), ("Reflective Runner Cap", 32.0, 9.0)]
    },
    "Home & Smart Living": {
        "Kitchen Tech": [("Smart Precision Gooseneck Kettle", 115.0, 42.0), ("Digital Dual-Zone Air Fryer", 149.0, 58.0)],
        "Air & Climate": [("True HEPA Smart Air Purifier", 169.0, 65.0), ("Ultrasonic Cool Mist Humidifier", 59.0, 21.0)]
    }
}

ECOMM_CHANNELS = ["Organic Search", "Paid Google Ads", "Social Media Ad", "Email Campaign", "Affiliate Network"]
ECOMM_CHANNEL_WEIGHTS = [0.30, 0.25, 0.22, 0.13, 0.10]
ECOMM_ZONES = ["Domestic Priority", "Express Coastal", "Standard Ground", "International Air", "Local Courier"]

ECOMM_SHOPPERS = [
    ("Lucas Vance", "New York", "Domestic Priority"),
    ("Chloe Bennet", "Los Angeles", "Express Coastal"),
    ("Ethan Wright", "Chicago", "Standard Ground"),
    ("Grace Kim", "Seattle", "Local Courier"),
    ("Mason Patel", "Austin", "Standard Ground"),
    ("Zoe Rodriguez", "Miami", "Express Coastal"),
    ("Liam Tanaka", "London", "International Air"),
    ("Hannah Muller", "Berlin", "International Air"),
    ("Noah Dubois", "Paris", "International Air"),
    ("Aria Chen", "Toronto", "International Air"),
    ("Caleb Foster", "Denver", "Standard Ground"),
    ("Maya Lin", "San Francisco", "Local Courier"),
    ("Leo Rossi", "Rome", "International Air"),
    ("Harper Clark", "Atlanta", "Domestic Priority"),
    ("Benjamin Hayes", "Boston", "Domestic Priority")
]

def generate_ecommerce_analytics_records(total_orders: int = 3600) -> List[Dict[str, Any]]:
    """Generates 3,600 D2C online orders spanning 2024-01-01 to 2025-12-31 with seasonal spikes."""
    random.seed(303)
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days
    
    # Generate 450 distinct shopper profiles
    shoppers = []
    for idx in range(1, 451):
        base_name, city, zone = random.choice(ECOMM_SHOPPERS)
        shoppers.append({
            "shopper_id": f"SHOP-{idx:04d}",
            "shopper_name": f"{base_name} {idx}",
            "city": city,
            "region": zone
        })
        
    records = []
    for i in range(1, total_orders + 1):
        day_offset = random.randint(0, total_days)
        order_date = start_date + datetime.timedelta(days=day_offset)
        
        # Cyber Week / Black Friday Q4 boost (late November / December)
        is_q4_peak = (order_date.month == 11 and order_date.day >= 20) or (order_date.month == 12 and order_date.day <= 24)
        
        shopper = random.choice(shoppers)
        channel = random.choices(ECOMM_CHANNELS, weights=ECOMM_CHANNEL_WEIGHTS)[0]
        
        category = random.choice(list(ECOMM_CATEGORIES.keys()))
        sub_cat = random.choice(list(ECOMM_CATEGORIES[category].keys()))
        prod_tuple = random.choice(ECOMM_CATEGORIES[category][sub_cat])
        prod_name, unit_price, unit_cost = prod_tuple
        prod_id = f"SKU-{abs(hash(prod_name)) % 10000:04d}"
        
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.60, 0.22, 0.10, 0.05, 0.03])[0]
        
        # Discounts: Flash sale / Promo codes higher during Q4 peak
        if is_q4_peak:
            discount = random.choices([0.10, 0.15, 0.20, 0.25, 0.30], weights=[0.20, 0.30, 0.25, 0.15, 0.10])[0]
        else:
            discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[0.55, 0.20, 0.15, 0.07, 0.03])[0]
            
        shipping_cost = 0.0 if (quantity * unit_price >= 100.0 or channel == "Email Campaign") else round(random.uniform(4.99, 14.99), 2)
        
        gross = quantity * unit_price
        revenue = round(gross * (1.0 - discount), 2)
        total_cost = round(quantity * unit_cost, 2)
        profit = round(revenue - total_cost - shipping_cost, 2)
        
        order_id = f"WEB-{order_date.year}-{10000 + i}"
        
        records.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": shopper["shopper_id"],
            "customer_name": shopper["shopper_name"],
            "segment": channel,
            "region": shopper["region"],
            "country": "United States" if "International" not in shopper["region"] else "International",
            "city": shopper["city"],
            "state": "Online",
            "category": category,
            "sub_category": sub_cat,
            "product_id": prod_id,
            "product_name": prod_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
            "revenue": revenue,
            "cost": total_cost,
            "profit": profit
        })
        
    return records

def seed_ecommerce_analytics_dataset(force: bool = False) -> str:
    """Idempotently seeds Dataset 3: E-commerce Analytics."""
    init_db()
    ds_id = "ecommerce_analytics"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, row_count FROM datasets WHERE id = ?", (ds_id,))
    existing = cursor.fetchone()
    if existing and not force:
        conn.close()
        return ds_id
        
    records = generate_ecommerce_analytics_records(3600)
    df = pd.DataFrame(records)
    csv_path = os.path.join(DATA_DIR, f"{ds_id}_clean.csv")
    df.to_csv(csv_path, index=False)
    
    cursor.execute("""
        INSERT OR REPLACE INTO datasets (id, name, description, row_count, column_count, is_sample, file_path)
        VALUES (?, ?, ?, ?, ?, 1, ?)
    """, (
        ds_id,
        "Global Direct-to-Consumer (D2C) E-commerce",
        "Multi-channel online store transactions tracking marketing channels (Organic, Paid Search, Social Ad, Email, Affiliate), promotional flash sales, and cart fulfillment zones.",
        len(records),
        len(df.columns),
        csv_path
    ))
    
    cursor.execute("DELETE FROM sales_data WHERE dataset_id = ?", (ds_id,))
    
    insert_records = []
    for r in records:
        insert_records.append((
            ds_id, r["order_id"], r["order_date"], r["customer_id"], r["customer_name"],
            r["segment"], r["region"], r["country"], r["city"], r["state"],
            r["category"], r["sub_category"], r["product_id"], r["product_name"],
            r["quantity"], r["unit_price"], r["discount"], r["shipping_cost"],
            r["revenue"], r["cost"], r["profit"]
        ))
        
    cursor.executemany("""
        INSERT INTO sales_data (
            dataset_id, order_id, order_date, customer_id, customer_name, segment,
            region, country, city, state, category, sub_category, product_id,
            product_name, quantity, unit_price, discount, shipping_cost, revenue, cost, profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_records)
    
    conn.commit()
    conn.close()
    return ds_id

# ==============================================================================
# DATASET 4: HR Analytics (Workforce Headcount, Payroll & Productivity Return)
# ==============================================================================

HR_DEPARTMENTS = {
    "Engineering & Product": {
        "AI & Machine Learning": [("Principal Staff AI Scientist", 16500.0, 11500.0), ("Senior Deep Learning Engineer", 13200.0, 9200.0)],
        "Cloud Infrastructure": [("Lead Cloud Systems Architect", 14800.0, 10200.0), ("Senior Site Reliability Engineer", 12500.0, 8600.0)],
        "Product Management": [("Director of Product Strategy", 15500.0, 10800.0), ("Senior Technical Product Manager", 12800.0, 8900.0)]
    },
    "Go-to-Market & Sales": {
        "Enterprise Sales": [("Strategic Enterprise Account Exec", 14200.0, 8500.0), ("Key Account Solution Consultant", 11800.0, 7800.0)],
        "Marketing & Demand": [("Head of Growth Marketing", 12400.0, 8200.0), ("Digital Campaign Strategist", 8900.0, 5800.0)]
    },
    "Operations & Legal": {
        "Legal & Regulatory": [("Senior Corporate Counsel", 15200.0, 10500.0), ("Compliance & Ethics Officer", 10800.0, 7200.0)],
        "People & Talent": [("Global Talent Acquisition Director", 12600.0, 8400.0), ("Senior People Operations Specialist", 8200.0, 5400.0)]
    },
    "Corporate & Finance": {
        "Financial Planning": [("Director of Financial Planning & Analysis", 15000.0, 10200.0), ("Senior Corporate Financial Analyst", 9800.0, 6600.0)],
        "Internal Operations": [("Workplace Technology Manager", 9500.0, 6400.0), ("Executive Business Partner", 7800.0, 5200.0)]
    }
}

HR_LEVELS = ["Executive Leadership", "Senior Management", "Core Professional", "Contract Specialist", "Early Career Associate"]
HR_LEVEL_WEIGHTS = [0.10, 0.25, 0.45, 0.12, 0.08]
HR_HUBS = [
    ("San Francisco HQ", "United States", "San Francisco", "CA"),
    ("New York Tech Hub", "United States", "New York", "NY"),
    ("London EMEA Center", "United Kingdom", "London", "Greater London"),
    ("Singapore APAC Hub", "Singapore", "Singapore", "Central"),
    ("Austin Operations Center", "United States", "Austin", "TX")
]

HR_FIRST_NAMES = [
    "Alexander", "Samantha", "Marcus", "Elena", "Julian", "Clara", "Adrian", "Victoria",
    "Dominic", "Natalia", "Gabriel", "Serena", "Xavier", "Valerie", "Malcolm", "Diana",
    "Tristan", "Camilla", "Zachary", "Vivian", "Harrison", "Beatrice", "Maxwell", "Melody"
]

HR_LAST_NAMES = [
    "Vance", "Kovacs", "Sterling", "Montenegro", "Sinclair", "Hawthorne", "Mercer", "Kaufman",
    "Prescott", "Davenport", "Fairchild", "Whitmore", "Kensington", "Blackwood", "Ashford", "Thornton"
]

def generate_employee_roster(count: int = 320) -> List[Dict[str, Any]]:
    """Generates employee workforce profiles."""
    random.seed(404)
    roster = []
    for i in range(1, count + 1):
        first = random.choice(HR_FIRST_NAMES)
        last = random.choice(HR_LAST_NAMES)
        level = random.choices(HR_LEVELS, weights=HR_LEVEL_WEIGHTS)[0]
        hub_name, country, city, state = random.choice(HR_HUBS)
        roster.append({
            "employee_id": f"EMP-{i:04d}",
            "employee_name": f"{first} {last}",
            "level": level,
            "hub": hub_name,
            "country": country,
            "city": city,
            "state": state
        })
    return roster

def generate_hr_analytics_records(total_allocations: int = 3000) -> List[Dict[str, Any]]:
    """Generates 3,000 monthly employee workforce allocation and productivity lines."""
    random.seed(404)
    employees = generate_employee_roster(320)
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days
    
    records = []
    for i in range(1, total_allocations + 1):
        day_offset = random.randint(0, total_days)
        order_date = start_date + datetime.timedelta(days=day_offset)
        
        emp = random.choice(employees)
        
        dept = random.choice(list(HR_DEPARTMENTS.keys()))
        team = random.choice(list(HR_DEPARTMENTS[dept].keys()))
        role_tuple = random.choice(HR_DEPARTMENTS[dept][team])
        role_name, monthly_output_val, monthly_comp_cost = role_tuple
        role_id = f"ROLE-{abs(hash(role_name)) % 10000:04d}"
        
        # Headcount FTE allocation (typically 1.0, sometimes shared split 0.5 or lead 1.25)
        quantity = 1
        unit_price = monthly_output_val
        discount = 0.0 # Overhead variance
        shipping_cost = round(random.uniform(150.0, 450.0), 2) # Hardware/SaaS enablement tooling per seat
        
        gross = quantity * unit_price
        revenue = round(gross * (1.0 - discount), 2)
        total_cost = round(quantity * monthly_comp_cost, 2)
        profit = round(revenue - total_cost - shipping_cost, 2)
        
        order_id = f"HR-{order_date.year}-{10000 + i}"
        
        records.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": emp["employee_id"],
            "customer_name": emp["employee_name"],
            "segment": emp["level"],
            "region": emp["hub"],
            "country": emp["country"],
            "city": emp["city"],
            "state": emp["state"],
            "category": dept,
            "sub_category": team,
            "product_id": role_id,
            "product_name": role_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
            "revenue": revenue,
            "cost": total_cost,
            "profit": profit
        })
        
    return records

def seed_hr_analytics_dataset(force: bool = False) -> str:
    """Idempotently seeds Dataset 4: HR Analytics."""
    init_db()
    ds_id = "hr_analytics"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, row_count FROM datasets WHERE id = ?", (ds_id,))
    existing = cursor.fetchone()
    if existing and not force:
        conn.close()
        return ds_id
        
    records = generate_hr_analytics_records(3000)
    df = pd.DataFrame(records)
    csv_path = os.path.join(DATA_DIR, f"{ds_id}_clean.csv")
    df.to_csv(csv_path, index=False)
    
    cursor.execute("""
        INSERT OR REPLACE INTO datasets (id, name, description, row_count, column_count, is_sample, file_path)
        VALUES (?, ?, ?, ?, ?, 1, ?)
    """, (
        ds_id,
        "Workforce & Human Capital Analytics",
        "Corporate human capital metrics tracking departmental headcount, total compensation & benefits costs, human capital ROI, and talent distribution across global offices.",
        len(records),
        len(df.columns),
        csv_path
    ))
    
    cursor.execute("DELETE FROM sales_data WHERE dataset_id = ?", (ds_id,))
    
    insert_records = []
    for r in records:
        insert_records.append((
            ds_id, r["order_id"], r["order_date"], r["customer_id"], r["customer_name"],
            r["segment"], r["region"], r["country"], r["city"], r["state"],
            r["category"], r["sub_category"], r["product_id"], r["product_name"],
            r["quantity"], r["unit_price"], r["discount"], r["shipping_cost"],
            r["revenue"], r["cost"], r["profit"]
        ))
        
    cursor.executemany("""
        INSERT INTO sales_data (
            dataset_id, order_id, order_date, customer_id, customer_name, segment,
            region, country, city, state, category, sub_category, product_id,
            product_name, quantity, unit_price, discount, shipping_cost, revenue, cost, profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_records)
    
    conn.commit()
    conn.close()
    return ds_id

def seed_all_additional_datasets(force: bool = False) -> List[str]:
    """Idempotently seeds all 4 specialized domain datasets."""
    ids = []
    ids.append(seed_sales_revenue_dataset(force=force))
    ids.append(seed_customer_analytics_dataset(force=force))
    ids.append(seed_ecommerce_analytics_dataset(force=force))
    ids.append(seed_hr_analytics_dataset(force=force))
    return ids

