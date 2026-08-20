import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Database engine configuration ('sqlite' or 'mysql')
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DATABASE = os.getenv("DB_DATABASE", "flower_shop")

class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        if params is None:
            return self.conn.execute(query)
        return self.conn.execute(query, params)

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class MySQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        # Translate SQLite '?' to MySQL '%s'
        query = query.replace("?", "%s")
        if params is None:
            return self.cursor.execute(query)
        return self.cursor.execute(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def __getattr__(self, name):
        return getattr(self.cursor, name)

class MySQLConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self._cursor = None

    def _get_cursor(self):
        if self._cursor is None:
            self._cursor = self.conn.cursor()
        return self._cursor

    def execute(self, query, params=None):
        cursor = MySQLCursorWrapper(self._get_cursor())
        cursor.execute(query, params)
        return cursor

    def cursor(self):
        return MySQLCursorWrapper(self._get_cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        if self._cursor:
            self._cursor.close()
        self.conn.close()

def get_db_connection():
    """
    Establish a connection to either SQLite or MySQL based on DB_ENGINE.
    """
    if DB_ENGINE == "mysql":
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )
        return MySQLConnectionWrapper(conn)
    else:
        conn = sqlite3.connect("flower_shop.db")
        conn.row_factory = sqlite3.Row
        return SQLiteConnectionWrapper(conn)

def seed_db(conn):
    """
    Populate the database with sample products if the table is empty.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    row = cursor.fetchone()
    if isinstance(row, dict):
        count = list(row.values())[0]
    elif row is not None:
        count = row[0]
    else:
        count = 0
        
    if count == 0:
        sample_products = [
            ("Red Rose Bouquet", "Rose", "Red", 29.99, 50, "Flower Farms Ltd."),
            ("Sunset Tulips", "Tulip", "Orange", 19.99, 30, "Valley Growers"),
            ("White Lilies", "Lily", "White", 24.99, 25, "Premium Flora Inc."),
            ("Blue Orchids", "Orchid", "Blue", 39.99, 15, "Exotic Blooms")
        ]
        for p in sample_products:
            cursor.execute(
                """
                INSERT INTO products (product_name, flower_type, color, price, stock_quantity, supplier_name)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                p
            )
        conn.commit()

def init_db():
    """
    Create products and orders tables if they do not exist.
    Compatible with both SQLite and MySQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DB_ENGINE == "mysql":
        product_id_def = "product_id INT AUTO_INCREMENT PRIMARY KEY"
        order_id_def = "order_id INT AUTO_INCREMENT PRIMARY KEY"
        price_def = "DECIMAL(10,2) NOT NULL"
        total_amount_def = "DECIMAL(10,2) NOT NULL"
    else:
        product_id_def = "product_id INTEGER PRIMARY KEY AUTOINCREMENT"
        order_id_def = "order_id INTEGER PRIMARY KEY AUTOINCREMENT"
        price_def = "REAL NOT NULL"
        total_amount_def = "REAL NOT NULL"

    # Create products table (using type compatibility)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS products (
        {product_id_def},
        product_name VARCHAR(100) NOT NULL,
        flower_type VARCHAR(50),
        color VARCHAR(30),
        price {price_def},
        stock_quantity INTEGER DEFAULT 0,
        supplier_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create orders table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS orders (
        {order_id_def},
        customer_name VARCHAR(100) NOT NULL,
        customer_phone VARCHAR(20),
        delivery_address VARCHAR(255),
        order_date VARCHAR(10) NOT NULL,
        delivery_date VARCHAR(10),
        total_amount {total_amount_def},
        order_status VARCHAR(30) DEFAULT 'Pending'
    );
    """)
    
    conn.commit()
    
    # Seed the database
    seed_db(conn)
    
    conn.close()

if __name__ == "__main__":
    print(f"Initializing database using engine: {DB_ENGINE}")
    init_db()
    print("Database tables initialized and seeded successfully.")

