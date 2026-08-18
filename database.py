import sqlite3
import os

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

class MySQLConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self._cursor = None

    def _get_cursor(self):
        if self._cursor is None:
            self._cursor = self.conn.cursor()
        return self._cursor

    def execute(self, query, params=None):
        # Translate SQLite '?' to MySQL '%s'
        query = query.replace("?", "%s")
        cursor = self._get_cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor

    def cursor(self):
        return self._get_cursor()

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

def init_db():
    """
    Create products and orders tables if they do not exist.
    Compatible with both SQLite and MySQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create products table (using type compatibility)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name VARCHAR(100) NOT NULL,
        flower_type VARCHAR(50),
        color VARCHAR(30),
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        supplier_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name VARCHAR(100) NOT NULL,
        customer_phone VARCHAR(20),
        delivery_address VARCHAR(255),
        order_date VARCHAR(10) NOT NULL,
        delivery_date VARCHAR(10),
        total_amount REAL NOT NULL,
        order_status VARCHAR(30) DEFAULT 'Pending'
    );
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print(f"Initializing database using engine: {DB_ENGINE}")
    init_db()
    print("Database tables initialized successfully.")

