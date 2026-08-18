from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager
import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables on startup
    database.init_db()
    yield

app = FastAPI(
    title="Flower Shop API",
    description="A Python FastAPI REST service for managing a flower shop database.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Pydantic Data Models ---

class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100, example="Red Rose Bouquet")
    flower_type: Optional[str] = Field(None, max_length=50, example="Rose")
    color: Optional[str] = Field(None, max_length=30, example="Red")
    price: float = Field(..., gt=0, example=29.99)
    stock_quantity: int = Field(0, ge=0, example=50)
    supplier_name: Optional[str] = Field(None, max_length=100, example="Flower Farms Ltd.")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    flower_type: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=30)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    supplier_name: Optional[str] = Field(None, max_length=100)

class ProductResponse(ProductBase):
    product_id: int
    created_at: str

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100, example="John Doe")
    customer_phone: Optional[str] = Field(None, max_length=20, example="+1-555-0199")
    delivery_address: Optional[str] = Field(None, max_length=255, example="123 Blossom Lane, Garden City")
    order_date: str = Field(..., example="2026-08-19")  # YYYY-MM-DD format
    delivery_date: Optional[str] = Field(None, example="2026-08-20")
    total_amount: float = Field(..., gt=0, example=89.97)
    order_status: Optional[str] = Field("Pending", max_length=30, example="Pending")

class OrderCreate(OrderBase):
    pass

class OrderStatusUpdate(BaseModel):
    order_status: str = Field(..., min_length=1, max_length=30, example="Completed")

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, max_length=20)
    delivery_address: Optional[str] = Field(None, max_length=255)
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    total_amount: Optional[float] = Field(None, gt=0)
    order_status: Optional[str] = Field(None, max_length=30)

class OrderResponse(OrderBase):
    order_id: int

    class Config:
        from_attributes = True


# --- API Routes ---

@app.get("/")
def read_root():
    """Welcome endpoint providing instructions to API users."""
    return {
        "message": "Welcome to the Flower Shop API!",
        "interactive_docs": "/docs",
        "alternative_docs": "/redoc"
    }

# --- PRODUCTS ENDPOINTS ---

@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_products():
    """Retrieve all products in the database."""
    conn = database.get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(p) for p in products]

@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int):
    """Retrieve a specific product by its ID."""
    conn = database.get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    conn.close()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(product)

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: ProductCreate):
    """Create a new product in the database."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO products (product_name, flower_type, color, price, stock_quantity, supplier_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            product.product_name,
            product.flower_type,
            product.color,
            product.price,
            product.stock_quantity,
            product.supplier_name,
        )
    )
    product_id = cursor.lastrowid
    conn.commit()
    
    new_product = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(new_product)

@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(product_id: int, product: ProductUpdate):
    """Update an existing product's details dynamically."""
    conn = database.get_db_connection()
    
    existing = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    
    updates = product.model_dump(exclude_unset=True)
    if not updates:
        conn.close()
        return dict(existing)
        
    query_parts = []
    params = []
    for key, value in updates.items():
        query_parts.append(f"{key} = ?")
        params.append(value)
    
    params.append(product_id)
    query = f"UPDATE products SET {', '.join(query_parts)} WHERE product_id = ?"
    
    conn.execute(query, tuple(params))
    conn.commit()
    
    updated_product = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(updated_product)

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(product_id: int):
    """Delete a product from the database by ID."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    existing = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
        
    cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
    return None

# --- ORDERS ENDPOINTS ---

@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def get_orders():
    """Retrieve all orders in the database."""
    conn = database.get_db_connection()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return [dict(o) for o in orders]

@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: int):
    """Retrieve a specific order by ID."""
    conn = database.get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return dict(order)

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order: OrderCreate):
    """Create a new order in the database."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders (customer_name, customer_phone, delivery_address, order_date, delivery_date, total_amount, order_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            order.customer_name,
            order.customer_phone,
            order.delivery_address,
            order.order_date,
            order.delivery_date,
            order.total_amount,
            order.order_status,
        )
    )
    order_id = cursor.lastrowid
    conn.commit()
    
    new_order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(new_order)

@app.put("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def update_order(order_id: int, order: OrderUpdate):
    """Update an order dynamically by ID."""
    conn = database.get_db_connection()
    
    existing = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    updates = order.model_dump(exclude_unset=True)
    if not updates:
        conn.close()
        return dict(existing)
        
    query_parts = []
    params = []
    for key, value in updates.items():
        query_parts.append(f"{key} = ?")
        params.append(value)
        
    params.append(order_id)
    query = f"UPDATE orders SET {', '.join(query_parts)} WHERE order_id = ?"
    
    conn.execute(query, tuple(params))
    conn.commit()
    
    updated_order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(updated_order)

@app.patch("/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    """Update only the status of an existing order."""
    conn = database.get_db_connection()
    existing = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    conn.execute("UPDATE orders SET order_status = ? WHERE order_id = ?", (status_update.order_status, order_id))
    conn.commit()
    
    updated_order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(updated_order)

@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Orders"])
def delete_order(order_id: int):
    """Delete an order from the database by ID."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    existing = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()
    return None
