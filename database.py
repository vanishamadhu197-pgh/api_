import sqlite3
import os

DB_FILE = "flower_shop.db"

def get_db_connection():
    """
    Establish a connection to the SQLite database.
    Sets row_factory to sqlite3.Row for dictionary-like access.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Create products and orders tables matching the schema definitions,
    adapted for SQLite compatibility.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        flower_type TEXT,
        color TEXT,
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        supplier_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT,
        delivery_address TEXT,
        order_date TEXT NOT NULL,
        delivery_date TEXT,
        total_amount REAL NOT NULL,
        order_status TEXT DEFAULT 'Pending'
    );
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print(f"Initializing SQLite database at: {os.path.abspath(DB_FILE)}")
    init_db()
    print("Database tables initialized successfully.")
