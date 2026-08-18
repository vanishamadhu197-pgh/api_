CREATE DATABASE flower_shop;
USE flower_shop;

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    flower_type VARCHAR(50),
    color VARCHAR(30),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    supplier_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20),
    delivery_address VARCHAR(255),
    order_date DATE NOT NULL,
    delivery_date DATE,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(30) DEFAULT 'Pending'
);
