"""
SQLite Database Manager for E-Commerce Analytics Platform.
Handles schema initialization, indexes, view creation, and dataframe persistence.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, Optional, Tuple

class DatabaseManager:
    """Manages SQLite database connection, table schemas, indexes, and analytical views."""

    def __init__(self, db_path: str = "data/ecommerce.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Returns a sqlite3 connection object with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_schema(self):
        """Creates database tables with primary keys, foreign keys, and indexes."""
        schema_sql = """
        -- 1. Categories
        CREATE TABLE IF NOT EXISTS categories (
            category_id TEXT PRIMARY KEY,
            category_name TEXT NOT NULL,
            department TEXT NOT NULL
        );

        -- 2. Products
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            category_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            cost REAL NOT NULL,
            stock_quantity INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );

        -- 3. Sellers
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id TEXT PRIMARY KEY,
            seller_name TEXT NOT NULL,
            state TEXT NOT NULL,
            city TEXT NOT NULL,
            seller_rating REAL NOT NULL
        );

        -- 4. Customers
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            segment TEXT NOT NULL
        );

        -- 5. Orders
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_status TEXT NOT NULL,
            order_date TEXT NOT NULL,
            shipping_date TEXT,
            estimated_delivery TEXT,
            delivery_date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        -- 6. Order Items
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            seller_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            freight_value REAL NOT NULL,
            discount_amount REAL DEFAULT 0.0,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
        );

        -- 7. Payments
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            installments INTEGER DEFAULT 1,
            payment_value REAL NOT NULL,
            payment_status TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        -- 8. Reviews
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            review_score INTEGER NOT NULL,
            review_title TEXT,
            review_date TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        -- INDEXES FOR PERFORMANCE
        CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
        CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
        CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
        CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
        CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
        CREATE INDEX IF NOT EXISTS idx_reviews_order ON reviews(order_id);
        """

        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def populate_database(self, tables_dict: Dict[str, pd.DataFrame]):
        """Populates database with generated dataframes."""
        self.initialize_schema()
        with self.get_connection() as conn:
            for table_name, df in tables_dict.items():
                df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.commit()

        self._create_views()

    def _create_views(self):
        """Creates analytical SQL Views for streamlined reporting."""
        views_sql = """
        -- Order Summary View with calculated gross revenue, net revenue, and item count
        DROP VIEW IF EXISTS vw_order_summary;
        CREATE VIEW vw_order_summary AS
        SELECT 
            o.order_id,
            o.customer_id,
            c.first_name || ' ' || c.last_name AS customer_name,
            c.state AS customer_state,
            c.segment AS customer_segment,
            o.order_status,
            o.order_date,
            o.shipping_date,
            o.delivery_date,
            COUNT(oi.order_item_id) AS total_items,
            SUM(oi.quantity * oi.unit_price) AS gross_sales,
            SUM(oi.discount_amount * oi.quantity) AS total_discount,
            SUM(oi.freight_value) AS total_shipping_fee,
            SUM((oi.unit_price - oi.discount_amount) * oi.quantity) AS net_sales,
            p.payment_method,
            r.review_score
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN payments p ON o.order_id = p.order_id
        LEFT JOIN reviews r ON o.order_id = r.order_id
        GROUP BY o.order_id;

        -- Daily Sales Trend View
        DROP VIEW IF EXISTS vw_daily_sales;
        CREATE VIEW vw_daily_sales AS
        SELECT 
            DATE(order_date) AS sales_date,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_id) AS unique_customers,
            ROUND(SUM(net_sales), 2) AS total_revenue,
            ROUND(AVG(net_sales), 2) AS avg_order_value
        FROM vw_order_summary
        WHERE order_status != 'Cancelled'
        GROUP BY DATE(order_date);
        """
        with self.get_connection() as conn:
            conn.executescript(views_sql)
            conn.commit()

    def query(self, sql: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Executes a SELECT SQL query and returns a Pandas DataFrame."""
        with self.get_connection() as conn:
            if params:
                return pd.read_sql_query(sql, conn, params=params)
            return pd.read_sql_query(sql, conn)

if __name__ == "__main__":
    db = DatabaseManager()
    db.initialize_schema()
    print("✅ Database schema initialized successfully.")
