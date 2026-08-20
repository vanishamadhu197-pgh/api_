import requests
import json
import time
import os
import urllib3

# Disable warnings for self-signed SSL certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Setup session to bypass self-signed certificate verification
session = requests.Session()
session.verify = False

def pretty_print(title, data):
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2))

def run_demo():
    print("Starting Flower Shop API Client Demo...")
    print(f"Connecting to API at: {BASE_URL}")

    # Check connection
    try:
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("Successfully connected to the API.")
            pretty_print("Root Endpoint", response.json())
        else:
            print(f"Error: API returned status code {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to the API server.")
        print("Please make sure the server is running by executing:")
        print("  uvicorn main:app --reload")
        return

    # --- 1. CREATE PRODUCTS (POST) ---
    product1_data = {
        "product_name": "Crimson Roses Bouquet",
        "flower_type": "Rose",
        "color": "Red",
        "price": 34.99,
        "stock_quantity": 45,
        "supplier_name": "Premium Flora Inc."
    }
    
    product2_data = {
        "product_name": "Sunset Tulips",
        "flower_type": "Tulip",
        "color": "Orange",
        "price": 19.99,
        "stock_quantity": 30,
        "supplier_name": "Valley Growers"
    }

    print("\n--- 1. Creating Products ---")
    p1_response = session.post(f"{BASE_URL}/products", json=product1_data)
    p2_response = session.post(f"{BASE_URL}/products", json=product2_data)

    if p1_response.status_code == 201:
        p1 = p1_response.json()
        pretty_print("Created Product 1", p1)
        p1_id = p1["product_id"]
    else:
        print("Failed to create Product 1")
        return

    if p2_response.status_code == 201:
        p2 = p2_response.json()
        pretty_print("Created Product 2", p2)
        p2_id = p2["product_id"]
    else:
        print("Failed to create Product 2")
        return

    # --- 2. GET ALL PRODUCTS (GET) ---
    print("\n--- 2. Fetching All Products ---")
    all_products_resp = session.get(f"{BASE_URL}/products")
    pretty_print("All Products in Database", all_products_resp.json())

    # --- 3. UPDATE PRODUCT (PUT) ---
    print("\n--- 3. Updating Stock & Price of Product 1 ---")
    update_data = {
        "price": 32.50,
        "stock_quantity": 40
    }
    update_resp = session.put(f"{BASE_URL}/products/{p1_id}", json=update_data)
    pretty_print("Updated Product 1", update_resp.json())

    # --- 4. CREATE ORDER (POST) ---
    print("\n--- 4. Creating a New Customer Order ---")
    order_data = {
        "customer_name": "Alice Smith",
        "customer_phone": "+1-555-0143",
        "delivery_address": "456 Oak Avenue, Blossom District",
        "order_date": "2026-08-19",
        "delivery_date": "2026-08-21",
        "total_amount": 52.49,
        "order_status": "Pending"
    }
    order_resp = session.post(f"{BASE_URL}/orders", json=order_data)
    if order_resp.status_code == 201:
        order = order_resp.json()
        pretty_print("Created Order", order)
        order_id = order["order_id"]
    else:
        print("Failed to create Order")
        return

    # --- 5. GET ALL ORDERS (GET) ---
    print("\n--- 5. Fetching All Orders ---")
    all_orders_resp = session.get(f"{BASE_URL}/orders")
    pretty_print("All Orders in Database", all_orders_resp.json())

    # --- 6. UPDATE ORDER STATUS (PATCH) ---
    print("\n--- 6. Updating Order Status to 'Shipped' ---")
    status_data = {"order_status": "Shipped"}
    status_resp = session.patch(f"{BASE_URL}/orders/{order_id}/status", json=status_data)
    pretty_print("Updated Order (Status Patch)", status_resp.json())

    # --- 7. CLEANUP / DELETE DEMO DATA (DELETE) ---
    print("\nDo you want to clean up the demo database records?")
    cleanup = input("Type 'yes' to delete the demo records, or hit Enter to keep them: ").strip().lower()
    
    if cleanup == "yes":
        print("\n--- Cleaning Up Demo Records ---")
        
        # Delete Order
        delete_order_resp = session.delete(f"{BASE_URL}/orders/{order_id}")
        if delete_order_resp.status_code == 204:
            print(f"Successfully deleted Order {order_id}")
        
        # Delete Products
        for pid in [p1_id, p2_id]:
            delete_prod_resp = session.delete(f"{BASE_URL}/products/{pid}")
            if delete_prod_resp.status_code == 204:
                print(f"Successfully deleted Product {pid}")
    else:
        print("\nRecords preserved in the database.")

if __name__ == "__main__":
    run_demo()
