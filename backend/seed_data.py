"""
InsightIQ Synthetic Retail Dataset Generator and Idempotent Seeder.
Generates 3,000+ realistic retail transactions across 24 months (2024-01-01 to 2025-12-31).
Uses fixed random seed 42 to guarantee deterministic, reproducible metrics.
"""
import os
import random
import datetime
import pandas as pd
from typing import List, Dict, Any
from backend.database import get_db_connection, init_db

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CATEGORIES = {
    "Technology": {
        "Phones": [("iPhone 15 Pro", 999.0, 720.0), ("Samsung Galaxy S24", 899.0, 640.0), ("Google Pixel 8", 699.0, 480.0)],
        "Accessories": [("Logitech MX Master 3S", 99.0, 52.0), ("Anker 65W GaN Charger", 49.0, 22.0), ("Apple AirPods Pro 2", 249.0, 160.0)],
        "Laptops": [("MacBook Air M3", 1199.0, 890.0), ("Dell XPS 15", 1499.0, 1100.0), ("Lenovo ThinkPad X1", 1349.0, 980.0)],
        "Machines": [("Canon ImageClass Laser Printer", 329.0, 240.0), ("Epson EcoTank Pro", 450.0, 310.0)]
    },
    "Furniture": {
        "Chairs": [("Herman Miller Aeron Ergonomic Chair", 850.0, 520.0), ("Steelcase Gesture Chair", 780.0, 490.0), ("Mesh Task Chair", 189.0, 110.0)],
        "Tables": [("Solid Oak Executive Desk", 620.0, 410.0), ("Adjustable Standing Desk", 480.0, 310.0), ("Conference Room Table", 950.0, 680.0)],
        "Bookcases": [("5-Tier Wooden Bookshelf", 179.0, 115.0), ("Modular Steel Storage Shelves", 220.0, 135.0)],
        "Furnishings": [("Architect LED Desk Lamp", 75.0, 35.0), ("Floor Anti-Fatigue Mat", 45.0, 18.0)]
    },
    "Office Supplies": {
        "Storage": [("Heavy-Duty File Storage Box 4-Pack", 38.0, 19.0), ("Locking 3-Drawer File Cabinet", 210.0, 130.0)],
        "Paper": [("Multipurpose Copy Paper 5000 Sheets", 48.0, 26.0), ("Premium Bright Laser Paper Ream", 16.0, 8.0)],
        "Binders": [("Heavy-Duty D-Ring Binder 2-Inch", 9.5, 3.5), ("Clear Presentation Sheet Protectors", 14.0, 5.0)],
        "Appliances": [("Compact Office Microwave", 119.0, 78.0), ("Countertop Water Cooler Dispenser", 165.0, 105.0)],
        "Art": [("Dual-Tip Artist Marker Set", 28.0, 12.0), ("Heavy-Duty Rotary Paper Trimmer", 65.0, 32.0)]
    }
}

REGIONS = {
    "North": ["New York", "Boston", "Chicago", "Minneapolis", "Detroit"],
    "South": ["Atlanta", "Miami", "Dallas", "Houston", "Charlotte"],
    "East": ["Philadelphia", "Washington D.C.", "Pittsburgh", "Baltimore", "Newark"],
    "West": ["Los Angeles", "San Francisco", "Seattle", "Denver", "Portland"],
    "Central": ["Kansas City", "Indianapolis", "Columbus", "St. Louis", "Omaha"]
}

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

def generate_customers(num_customers: int = 350) -> List[Dict[str, str]]:
    """Generate deterministic customer master records."""
    random.seed(42)
    customers = []
    for i in range(1, num_customers + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        c_id = f"CUST-{i:04d}"
        c_name = f"{first} {last}"
        seg = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
        region = random.choice(list(REGIONS.keys()))
        city = random.choice(REGIONS[region])
        customers.append({
            "customer_id": c_id,
            "customer_name": c_name,
            "segment": seg,
            "region": region,
            "city": city,
            "state": "US-State"
        })
    return customers

def generate_orders(num_orders: int = 3200) -> List[Dict[str, Any]]:
    """Generate 3,200+ deterministic order lines spanning 2024-01-01 to 2025-12-31."""
    random.seed(42)
    customers = generate_customers(350)
    
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days
    
    orders = []
    
    for i in range(1, num_orders + 1):
        # Time distribution: moderate upward trend and Q4 seasonality
        day_offset = int(random.triangular(0, total_days, total_days * 0.65))
        order_date = start_date + datetime.timedelta(days=day_offset)
        
        # Boost Q4 transactions (Oct - Dec holiday surge)
        if order_date.month in [10, 11, 12] and random.random() < 0.25:
            # slightly higher activity in Q4
            pass

        cust = random.choice(customers)
        category_name = random.choices(["Technology", "Furniture", "Office Supplies"], weights=[0.38, 0.32, 0.30])[0]
        sub_cat_name = random.choice(list(CATEGORIES[category_name].keys()))
        product_item = random.choice(CATEGORIES[category_name][sub_cat_name])
        
        product_name, unit_price, unit_cost = product_item
        product_id = f"PROD-{abs(hash(product_name)) % 10000:04d}"
        
        quantity = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[0.45, 0.25, 0.15, 0.08, 0.04, 0.02, 0.01])[0]
        
        # Plausible discounts: 0%, 5%, 10%, 15%, 20%, 30%
        discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20, 0.30], weights=[0.55, 0.15, 0.15, 0.08, 0.05, 0.02])[0]
        
        shipping_cost = round(random.uniform(4.5, 28.0), 2)
        
        # Strict formula adherence:
        # revenue = quantity * unit_price * (1 - discount)
        # cost = quantity * unit_cost
        # profit = revenue - cost - shipping_cost
        gross_revenue = quantity * unit_price
        revenue = round(gross_revenue * (1.0 - discount), 2)
        total_cost = round(quantity * unit_cost, 2)
        profit = round(revenue - total_cost - shipping_cost, 2)
        
        order_id = f"ORD-{order_date.year}-{1000 + (i % 2100):05d}"
        
        orders.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": cust["customer_id"],
            "customer_name": cust["customer_name"],
            "segment": cust["segment"],
            "region": cust["region"],
            "country": "United States",
            "city": cust["city"],
            "state": "Sample State",
            "category": category_name,
            "sub_category": sub_cat_name,
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
            "revenue": revenue,
            "cost": total_cost,
            "profit": profit
        })
        
    return orders

def seed_sample_data(force: bool = False) -> str:
    """
    Idempotently seeds the database with the core sample dataset.
    Returns the dataset ID.
    """
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sample_id = "sample_superstore"
    
    cursor.execute("SELECT id, row_count FROM datasets WHERE id = ?", (sample_id,))
    existing = cursor.fetchone()
    
    if existing and not force:
        conn.close()
        return sample_id
        
    # Generate deterministic orders
    orders = generate_orders(3200)
    df = pd.DataFrame(orders)
    
    # Save clean CSV copy for downloads
    clean_csv_path = os.path.join(DATA_DIR, "sample_superstore_clean.csv")
    df.to_csv(clean_csv_path, index=False)
    
    # Also generate demo upload with intentional data quality issues for testing/demonstration
    generate_demo_dirty_csv(df)
    
    # Insert or replace dataset metadata
    cursor.execute("""
        INSERT OR REPLACE INTO datasets (id, name, description, row_count, column_count, is_sample, file_path)
        VALUES (?, ?, ?, ?, ?, 1, ?)
    """, (
        sample_id,
        "Global Superstore Retail (2024-2025)",
        "Deterministic benchmark retail sales dataset spanning 24 months across Technology, Furniture, and Office Supplies with verified financial relationships.",
        len(orders),
        len(df.columns),
        clean_csv_path
    ))
    
    # Delete any previous rows for clean idempotent re-seeding
    cursor.execute("DELETE FROM sales_data WHERE dataset_id = ?", (sample_id,))
    
    # Insert rows in batch
    insert_records = []
    for row in orders:
        insert_records.append((
            sample_id,
            row["order_id"],
            row["order_date"],
            row["customer_id"],
            row["customer_name"],
            row["segment"],
            row["region"],
            row["country"],
            row["city"],
            row["state"],
            row["category"],
            row["sub_category"],
            row["product_id"],
            row["product_name"],
            row["quantity"],
            row["unit_price"],
            row["discount"],
            row["shipping_cost"],
            row["revenue"],
            row["cost"],
            row["profit"]
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
    return sample_id

def generate_demo_dirty_csv(clean_df: pd.DataFrame):
    """
    Creates a secondary CSV file 'demo_upload_with_issues.csv' containing
    well-documented data quality issues (duplicates, null values, trailing spaces,
    and out-of-format dates) for testing and demonstrating data cleaning.
    """
    dirty_df = clean_df.head(500).copy()
    
    # 1. Inject duplicate rows (5 duplicates)
    duplicates = dirty_df.iloc[10:15].copy()
    dirty_df = pd.concat([dirty_df, duplicates], ignore_index=True)
    
    # 2. Inject missing values (null discounts and missing customer name)
    dirty_df.loc[25:35, "discount"] = None
    dirty_df.loc[45:48, "customer_name"] = None
    
    # 3. Inject whitespace anomalies in categories
    dirty_df.loc[60:70, "category"] = dirty_df.loc[60:70, "category"] + "   "
    
    # 4. Inject unformatted date strings
    dirty_df.loc[80:85, "order_date"] = "15/11/2024"
    
    dirty_csv_path = os.path.join(DATA_DIR, "demo_upload_with_issues.csv")
    dirty_df.to_csv(dirty_csv_path, index=False)

if __name__ == "__main__":
    sid = seed_sample_data(force=True)
    print(f"Sample data successfully seeded under dataset ID: '{sid}'")
