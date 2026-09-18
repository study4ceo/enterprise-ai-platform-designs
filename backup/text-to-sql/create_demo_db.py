"""Create demo SQLite database with sample data."""

import sqlite3
from pathlib import Path


def create_demo_database(db_path: str = "demo_db.sqlite"):
    """Create demo database with sample tables and data."""
    
    # Remove existing database
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            city TEXT,
            total_spent DECIMAL(10,2) DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price DECIMAL(10,2) NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date DATE,
            total_amount DECIMAL(10,2),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Insert sample customers
    customers = [
        (1, "John Doe", "john@email.com", "New York", 1500.00),
        (2, "Jane Smith", "jane@email.com", "Los Angeles", 2300.50),
        (3, "Bob Wilson", "bob@email.com", "Chicago", 850.00),
        (4, "Alice Brown", "alice@email.com", "Houston", 3200.00),
        (5, "Charlie Davis", "charlie@email.com", "Phoenix", 450.00),
    ]
    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers
    )
    
    # Insert sample products
    products = [
        (1, "Laptop", "Electronics", 999.99, 15),
        (2, "Mouse", "Electronics", 29.99, 50),
        (3, "Keyboard", "Electronics", 79.99, 30),
        (4, "Monitor", "Electronics", 299.99, 20),
        (5, "Desk Chair", "Furniture", 199.99, 25),
        (6, "Desk", "Furniture", 399.99, 10),
        (7, "USB Cable", "Accessories", 9.99, 100),
        (8, "Headphones", "Electronics", 149.99, 40),
    ]
    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?)", products
    )
    
    # Insert sample orders
    orders = [
        (1, 1, 1, 1, "2024-01-15", 999.99),
        (2, 1, 2, 2, "2024-01-16", 59.98),
        (3, 2, 4, 1, "2024-01-20", 299.99),
        (4, 2, 5, 2, "2024-01-21", 399.98),
        (5, 2, 8, 1, "2024-01-22", 149.99),
        (6, 3, 3, 1, "2024-02-01", 79.99),
        (7, 3, 7, 5, "2024-02-02", 49.95),
        (8, 4, 1, 2, "2024-02-10", 1999.98),
        (9, 4, 6, 1, "2024-02-11", 399.99),
        (10, 5, 7, 3, "2024-02-15", 29.97),
    ]
    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders
    )
    
    conn.commit()
    conn.close()
    
    print(f"✓ Demo database created: {db_path}")
    print(f"  - Customers: {len(customers)}")
    print(f"  - Products: {len(products)}")
    print(f"  - Orders: {len(orders)}")


if __name__ == "__main__":
    create_demo_database()
