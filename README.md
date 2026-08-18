# Flower Shop API

A lightweight, robust Python FastAPI REST API with a local SQLite database, built according to your database schema.

This project includes:
1. `schema.sql`: Original MySQL DDL commands for creating `products` and `orders` tables.
2. `database.py`: Python code to establish database connections and initialize tables in SQLite (`flower_shop.db`).
3. `main.py`: FastAPI server implementing complete CRUD endpoints for products and orders.
4. `client.py`: Python demonstration client that shows how to make API calls (GET, POST, PUT, PATCH, DELETE) to the server.

---

## Getting Started

### 1. Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI Server

Launch the development server with auto-reload:

```bash
uvicorn main:app --reload
```

The server will start at: `http://127.0.0.1:8000`

### 3. Explore API Documentation

Once the server is running, you can explore, test, and view schemas for all endpoints via:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Using the Python Client

You can run the interactive client script to demonstrate standard API operations (creating products, updating details, creating orders, patching status, and deleting records):

```bash
python client.py
```

---

## API Endpoint Reference

### Products
- `GET /products` - Retrieve all products
- `GET /products/{product_id}` - Retrieve a single product
- `POST /products` - Add a new product
- `PUT /products/{product_id}` - Update a product details
- `DELETE /products/{product_id}` - Remove a product

### Orders
- `GET /orders` - Retrieve all orders
- `GET /orders/{order_id}` - Retrieve a single order
- `POST /orders` - Place a new order
- `PUT /orders/{order_id}` - Update order details
- `PATCH /orders/{order_id}/status` - Quick update for order status
- `DELETE /orders/{order_id}` - Cancel/delete an order
