"""
InsightIQ SQLite Database Management and Connection Utilities.
Provides idempotent schema creation, connection pooling, and read-only connection modes.
"""
import os
import sqlite3
from typing import Generator
from contextlib import contextmanager

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(DB_DIR, "insightiq.db"))
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

def get_db_connection() -> sqlite3.Connection:
    """Return a standard read/write SQLite connection with WAL mode and row factory enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass
    conn.execute("PRAGMA busy_timeout = 20000;")
    return conn

def get_readonly_connection() -> sqlite3.Connection:
    """Return a strict read-only SQLite connection for safe SQL Lab querying."""
    # SQLite URI mode=ro prevents any write/schema modifications at engine level
    abs_path = os.path.abspath(DB_PATH)
    uri = f"file:{abs_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 20000;")
    return conn

@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for safe database transactions with auto-commit/rollback."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Idempotently initialize all database tables and analytical indexes."""
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Datasets catalog
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                row_count INTEGER DEFAULT 0,
                column_count INTEGER DEFAULT 0,
                is_sample BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT
            );
        """)

        # Cleaned transactional sales records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                order_id TEXT NOT NULL,
                order_date TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                customer_name TEXT,
                segment TEXT,
                region TEXT,
                country TEXT DEFAULT 'United States',
                city TEXT,
                state TEXT,
                category TEXT,
                sub_category TEXT,
                product_id TEXT,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0.0,
                shipping_cost REAL DEFAULT 0.0,
                revenue REAL NOT NULL,
                cost REAL NOT NULL,
                profit REAL NOT NULL,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
            );
        """)

        # Data cleaning and audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cleaning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rows_before INTEGER NOT NULL,
                rows_after INTEGER NOT NULL,
                duplicates_removed INTEGER NOT NULL,
                nulls_handled INTEGER NOT NULL,
                outliers_flagged INTEGER NOT NULL,
                quality_score_before REAL NOT NULL,
                quality_score_after REAL NOT NULL,
                cleaning_log TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
            );
        """)

        # Analytical performance indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_dataset ON sales_data(dataset_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_data(dataset_id, order_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_region ON sales_data(dataset_id, region);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_category ON sales_data(dataset_id, category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales_data(dataset_id, customer_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_data(dataset_id, product_name);")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
