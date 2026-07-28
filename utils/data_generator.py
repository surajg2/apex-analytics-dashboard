"""
Realistic E-Commerce Synthetic Data Generator.
Generates relational tables: Customers, Categories, Products, Sellers,
Orders, Order_Items, Payments, and Reviews with temporal seasonality and business dynamics.
"""

import random
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Tuple

class EcommerceDataGenerator:
    """Generates production-grade synthetic e-commerce data with realistic business patterns."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)

        # US States and Cities for regional dynamics
        self.locations = [
            ("California", "Los Angeles", "90001"),
            ("California", "San Francisco", "94102"),
            ("California", "San Diego", "92101"),
            ("New York", "New York City", "10001"),
            ("New York", "Buffalo", "14201"),
            ("Texas", "Houston", "77001"),
            ("Texas", "Austin", "78701"),
            ("Texas", "Dallas", "75201"),
            ("Florida", "Miami", "33101"),
            ("Florida", "Orlando", "32801"),
            ("Illinois", "Chicago", "60601"),
            ("Washington", "Seattle", "98101"),
            ("Massachusetts", "Boston", "02108"),
            ("Georgia", "Atlanta", "30301"),
            ("Colorado", "Denver", "80202"),
            ("Pennsylvania", "Philadelphia", "19102"),
            ("North Carolina", "Raleigh", "27601"),
            ("Ohio", "Columbus", "43215")
        ]

        self.categories_data = [
            ("CAT_01", "Electronics", "Technology"),
            ("CAT_02", "Computers & Accessories", "Technology"),
            ("CAT_03", "Apparel & Fashion", "Lifestyle"),
            ("CAT_04", "Footwear", "Lifestyle"),
            ("CAT_05", "Home & Kitchen", "Home"),
            ("CAT_06", "Beauty & Personal Care", "Lifestyle"),
            ("CAT_07", "Books & Media", "Entertainment"),
            ("CAT_08", "Sports & Fitness", "Outdoors"),
            ("CAT_09", "Toys & Games", "Entertainment"),
            ("CAT_10", "Automotive & Tools", "Industrial")
        ]

        self.payment_methods = ["Credit Card", "PayPal", "Debit Card", "Buy Now Pay Later", "UPI"]

    def generate_all(
        self,
        num_customers: int = 3500,
        num_products: int = 150,
        num_sellers: int = 40,
        num_orders: int = 20000,
        start_date: str = "2023-01-01",
        end_date: str = "2025-12-31"
    ) -> Dict[str, pd.DataFrame]:
        """Generates all relational dataframes."""

        print("[INFO] Generating Categories & Products...")
        df_categories = pd.DataFrame(self.categories_data, columns=["category_id", "category_name", "department"])
        df_products = self._generate_products(num_products, df_categories)

        print("[INFO] Generating Sellers & Customers...")
        df_sellers = self._generate_sellers(num_sellers)
        df_customers = self._generate_customers(num_customers, start_date)

        print("[INFO] Generating Orders & Shipping data with Seasonality...")
        df_orders = self._generate_orders(num_orders, df_customers, start_date, end_date)

        print("[INFO] Generating Order Items...")
        df_order_items = self._generate_order_items(df_orders, df_products, df_sellers)

        print("[INFO] Generating Payments & Reviews...")
        df_payments = self._generate_payments(df_orders, df_order_items)
        df_reviews = self._generate_reviews(df_orders)

        print("[SUCCESS] Data Generation Complete!")

        return {
            "categories": df_categories,
            "products": df_products,
            "sellers": df_sellers,
            "customers": df_customers,
            "orders": df_orders,
            "order_items": df_order_items,
            "payments": df_payments,
            "reviews": df_reviews
        }

    def _generate_products(self, num_products: int, df_categories: pd.DataFrame) -> pd.DataFrame:
        product_prefixes = {
            "Electronics": ["Pro Wireless Earbuds", "Smart 4K TV", "Noise Cancelling Headphones", "Bluetooth Speaker", "Smartwatch Ultra", "HD Webcam", "Action Camera"],
            "Computers & Accessories": ["Mechanical Keyboard", "Ergonomic Gaming Mouse", "USB-C Hub Hub Pro", "UltraWide Monitor 34\"", "NVMe SSD 1TB", "Laptop Stand Aluminum", "Wireless Router Wi-Fi 6E"],
            "Apparel & Fashion": ["Organic Cotton T-Shirt", "Slim Fit Denim Jeans", "Winter Fleece Jacket", "Designer Sunglasses", "Leather Casual Belt", "Performance Hoodie"],
            "Footwear": ["Trail Running Shoes", "Leather Oxford Dress Shoes", "Air Cushion Sneakers", "Lightweight Sandals", "Waterproof Hiking Boots"],
            "Home & Kitchen": ["Espresso Coffee Machine", "Air Fryer XL 5.8Qt", "Robot Vacuum Cleaner", "Memory Foam Pillow", "Cast Iron Skillet Set", "Stainless Steel Knife Set"],
            "Beauty & Personal Care": ["Hydrating Face Serum", "Electric Toothbrush Pro", "Argan Oil Hair Mask", "Organic Body Wash", "UV Sunscreen SPF 50+"],
            "Books & Media": ["Mastering Python & SQL", "Data Science Playbook", "Deep Learning Fundamentals", "The Art of Clean Architecture", "SaaS Business Secrets"],
            "Sports & Fitness": ["Non-Slip Yoga Mat", "Adjustable Dumbbell Set", "Resistance Bands Pack", "Insulated Hydro Water Bottle", "GPS Cycling Computer"],
            "Toys & Games": ["STEM Robotics Kit", "Strategy Board Game", "Remote Control Drone", "Wooden Building Blocks", "3D Puzzle Set"],
            "Automotive & Tools": ["Digital Tire Inflaters", "OBD2 Scanner Diagnostic", "Car Dash Cam 4K", "Cordless Drill Kit 20V", "Microfiber Towel Set"]
        }

        products = []
        cat_list = df_categories.to_dict("records")
        for i in range(1, num_products + 1):
            prod_id = f"PRD_{i:04d}"
            category = random.choice(cat_list)
            cat_name = category["category_name"]
            base_names = product_prefixes.get(cat_name, ["Generic Quality Product"])
            prod_name = f"{random.choice(base_names)} - Mod {random.randint(100, 999)}"
            
            # Base price according to category
            if cat_name in ["Electronics", "Computers & Accessories"]:
                price = round(random.uniform(49.99, 899.99), 2)
            elif cat_name in ["Home & Kitchen", "Sports & Fitness"]:
                price = round(random.uniform(29.99, 349.99), 2)
            elif cat_name in ["Books & Media", "Beauty & Personal Care"]:
                price = round(random.uniform(12.99, 79.99), 2)
            else:
                price = round(random.uniform(19.99, 199.99), 2)

            cost_margin = random.uniform(0.35, 0.70) # 35% to 70% of price is cost
            cost = round(price * cost_margin, 2)
            stock_qty = random.randint(10, 500)

            products.append({
                "product_id": prod_id,
                "category_id": category["category_id"],
                "product_name": prod_name,
                "price": price,
                "cost": cost,
                "stock_quantity": stock_qty
            })

        return pd.DataFrame(products)

    def _generate_sellers(self, num_sellers: int) -> pd.DataFrame:
        seller_company_suffixes = ["Tech Solutions", "Global Trading", "Direct Retail", "Logistics Hub", "Imports Co", "Enterprise Group"]
        sellers = []
        for i in range(1, num_sellers + 1):
            loc = random.choice(self.locations)
            sellers.append({
                "seller_id": f"SLR_{i:03d}",
                "seller_name": f"Apex {random.choice(seller_company_suffixes)} {i}",
                "state": loc[0],
                "city": loc[1],
                "seller_rating": round(random.uniform(3.8, 4.95), 2)
            })
        return pd.DataFrame(sellers)

    def _generate_customers(self, num_customers: int, start_date: str) -> pd.DataFrame:
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Cameron", "Dakota",
                       "Ethan", "Sophia", "Liam", "Olivia", "Noah", "Emma", "Ava", "Lucas", "Mia", "Jackson"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                      "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

        segments = ["Consumer", "Corporate", "Small Business"]
        segment_weights = [0.70, 0.20, 0.10]

        start_dt = pd.to_datetime(start_date)
        customers = []
        for i in range(1, num_customers + 1):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            loc = random.choice(self.locations)
            signup_delay = random.randint(0, 730)
            signup_date = (start_dt + pd.Timedelta(days=signup_delay)).strftime("%Y-%m-%d")

            customers.append({
                "customer_id": f"CUST_{i:05d}",
                "first_name": fname,
                "last_name": lname,
                "email": f"{fname.lower()}.{lname.lower()}{i}@example-domain.com",
                "city": loc[1],
                "state": loc[0],
                "zip_code": loc[2],
                "signup_date": signup_date,
                "segment": np.random.choice(segments, p=segment_weights)
            })
        return pd.DataFrame(customers)

    def _generate_orders(
        self, num_orders: int, df_customers: pd.DataFrame, start_date: str, end_date: str
    ) -> pd.DataFrame:
        cust_ids = df_customers["customer_id"].tolist()
        cust_signup_map = dict(zip(df_customers["customer_id"], df_customers["signup_date"]))

        dt_start = pd.to_datetime(start_date)
        dt_end = pd.to_datetime(end_date)
        total_days = (dt_end - dt_start).days

        # Generate timestamps with realistic daily seasonality & YoY growth trend
        date_weights = []
        dates_list = [dt_start + pd.Timedelta(days=i) for i in range(total_days + 1)]
        
        for d in dates_list:
            weight = 1.0
            # Year-over-year growth
            year_factor = 1.0 + (d.year - dt_start.year) * 0.25
            weight *= year_factor
            
            # Monthly seasonality (Black Friday/Cyber Monday in Nov, Christmas in Dec)
            if d.month == 11:
                weight *= 2.2 # Black Friday surge
            elif d.month == 12:
                weight *= 1.8 # Holiday shopping
            elif d.month in [7, 8]:
                weight *= 0.85 # Summer slowdown
            
            # Day of week seasonality (higher on Mon/Tue/Sun)
            if d.dayofweek in [0, 1, 6]:
                weight *= 1.2
            
            date_weights.append(weight)

        norm_weights = np.array(date_weights) / sum(date_weights)
        chosen_dates = np.random.choice(dates_list, size=num_orders, p=norm_weights)
        chosen_dates.sort()

        order_statuses = ["Delivered", "Shipped", "Processing", "Cancelled"]
        status_weights = [0.92, 0.04, 0.02, 0.02]

        orders = []
        for i in range(1, num_orders + 1):
            order_id = f"ORD_{i:06d}"
            order_date = pd.to_datetime(chosen_dates[i - 1])

            # Select customer whose signup_date <= order_date
            cust_id = random.choice(cust_ids)
            signup_dt = pd.to_datetime(cust_signup_map[cust_id])
            if order_date < signup_dt:
                order_date = signup_dt + pd.Timedelta(hours=random.randint(1, 48))

            status = np.random.choice(order_statuses, p=status_weights)

            # Shipping & Delivery timestamps
            if status in ["Delivered", "Shipped"]:
                ship_delay = random.randint(1, 3)
                shipping_date = order_date + pd.Timedelta(days=ship_delay, hours=random.randint(1, 8))
                
                # Estimated delivery (e.g. 5 days after shipping)
                est_delivery = shipping_date + pd.Timedelta(days=5)

                if status == "Delivered":
                    # Actual delivery (sometimes delayed by 1-4 days)
                    is_delayed = random.random() < 0.10
                    act_delay_days = 5 + (random.randint(1, 4) if is_delayed else random.randint(-1, 1))
                    delivery_date = shipping_date + pd.Timedelta(days=max(1, act_delay_days))
                else:
                    delivery_date = pd.NaT
            else:
                shipping_date = pd.NaT
                est_delivery = pd.NaT
                delivery_date = pd.NaT

            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_status": status,
                "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "shipping_date": shipping_date.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(shipping_date) else None,
                "estimated_delivery": est_delivery.strftime("%Y-%m-%d") if pd.notnull(est_delivery) else None,
                "delivery_date": delivery_date.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(delivery_date) else None
            })

        return pd.DataFrame(orders)

    def _generate_order_items(
        self, df_orders: pd.DataFrame, df_products: pd.DataFrame, df_sellers: pd.DataFrame
    ) -> pd.DataFrame:
        product_list = df_products.to_dict("records")
        seller_ids = df_sellers["seller_id"].tolist()

        order_items = []
        item_counter = 1

        for order in df_orders.itertuples():
            # 1 to 4 items per order
            num_items = np.random.choice([1, 2, 3, 4], p=[0.65, 0.22, 0.09, 0.04])
            chosen_prods = random.sample(product_list, num_items)

            for prod in chosen_prods:
                item_id = f"ITEM_{item_counter:07d}"
                item_counter += 1

                qty = np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04])
                unit_price = prod["price"]
                
                # Freight / Shipping fee based on price
                freight = round(random.uniform(4.99, 19.99), 2)
                
                # Occasional discount (10% to 25%)
                has_discount = random.random() < 0.25
                discount = round(unit_price * random.choice([0.05, 0.10, 0.15, 0.20, 0.25]), 2) if has_discount else 0.0

                order_items.append({
                    "order_item_id": item_id,
                    "order_id": order.order_id,
                    "product_id": prod["product_id"],
                    "seller_id": random.choice(seller_ids),
                    "quantity": qty,
                    "unit_price": unit_price,
                    "freight_value": freight,
                    "discount_amount": discount
                })

        return pd.DataFrame(order_items)

    def _generate_payments(self, df_orders: pd.DataFrame, df_order_items: pd.DataFrame) -> pd.DataFrame:
        # Calculate total order value from items
        df_order_items["item_total"] = (
            (df_order_items["unit_price"] - df_order_items["discount_amount"]) * df_order_items["quantity"]
        ) + df_order_items["freight_value"]
        
        order_totals = df_order_items.groupby("order_id")["item_total"].sum().to_dict()

        payments = []
        pay_counter = 1
        for order in df_orders.itertuples():
            if order.order_status == "Cancelled":
                status = "Refunded"
            else:
                status = "Completed"

            total_val = round(order_totals.get(order.order_id, 49.99), 2)
            method = np.random.choice(
                self.payment_methods,
                p=[0.55, 0.20, 0.12, 0.08, 0.05]
            )

            installments = 1
            if method in ["Credit Card", "Buy Now Pay Later"] and total_val > 100:
                installments = random.choice([1, 2, 3, 6, 12])

            payments.append({
                "payment_id": f"PAY_{pay_counter:06d}",
                "order_id": order.order_id,
                "payment_method": method,
                "installments": installments,
                "payment_value": total_val,
                "payment_status": status
            })
            pay_counter += 1

        return pd.DataFrame(payments)

    def _generate_reviews(self, df_orders: pd.DataFrame) -> pd.DataFrame:
        delivered_orders = df_orders[df_orders["order_status"] == "Delivered"]
        
        review_titles_5 = ["Outstanding Quality!", "Fast Shipping & Great Packing", "Exceeded My Expectations", "Superb Value for Money", "Highly Recommended!"]
        review_titles_4 = ["Very Good Product", "Works as expected", "Good quality for the price", "Fast Delivery", "Satisfied overall"]
        review_titles_3 = ["Average product", "Decent, but could be better", "Okay experience", "Fair quality"]
        review_titles_2 = ["Disappointed", "Slower shipping than expected", "Not worth the price", "Poor packaging"]
        review_titles_1 = ["Terrible experience", "Item damaged / late", "Waste of money", "Never buying again"]

        reviews = []
        rev_counter = 1
        for order in delivered_orders.itertuples():
            # ~75% of delivered orders get a review
            if random.random() > 0.75:
                continue

            # Correlate score with delivery speed
            is_delayed = False
            if pd.notnull(order.delivery_date) and pd.notnull(order.estimated_delivery):
                is_delayed = pd.to_datetime(order.delivery_date) > pd.to_datetime(order.estimated_delivery)

            if is_delayed:
                score = np.random.choice([1, 2, 3, 4], p=[0.40, 0.30, 0.20, 0.10])
            else:
                score = np.random.choice([5, 4, 3, 2, 1], p=[0.65, 0.20, 0.08, 0.04, 0.03])

            title_map = {5: review_titles_5, 4: review_titles_4, 3: review_titles_3, 2: review_titles_2, 1: review_titles_1}
            title = random.choice(title_map[score])

            rev_date = pd.to_datetime(order.delivery_date) + pd.Timedelta(days=random.randint(0, 3))

            reviews.append({
                "review_id": f"REV_{rev_counter:06d}",
                "order_id": order.order_id,
                "review_score": score,
                "review_title": title,
                "review_date": rev_date.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(rev_date) else order.order_date
            })
            rev_counter += 1

        return pd.DataFrame(reviews)

if __name__ == "__main__":
    gen = EcommerceDataGenerator()
    data = gen.generate_all(num_orders=1000)
    for name, df in data.items():
        print(f"{name}: {df.shape}")
