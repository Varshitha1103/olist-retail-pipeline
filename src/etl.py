import pandas as pd
import sqlite3
from datetime import datetime

def extract_data(data_path):
    """Extract - Load all CSV files"""
    print(f"[{datetime.now()}] Starting Extraction...")
    
    customers = pd.read_csv(f'{data_path}/olist_customers_dataset.csv')
    orders = pd.read_csv(f'{data_path}/olist_orders_dataset.csv')
    order_items = pd.read_csv(f'{data_path}/olist_order_items_dataset.csv', engine='python', on_bad_lines='skip')
    payments = pd.read_csv(f'{data_path}/olist_order_payments_dataset.csv')
    products = pd.read_csv(f'{data_path}/olist_products_dataset.csv')
    sellers = pd.read_csv(f'{data_path}/olist_sellers_dataset.csv')
    category = pd.read_csv(f'{data_path}/product_category_name_translation.csv')
    
    print(f"[{datetime.now()}] Extraction Complete!")
    return customers, orders, order_items, payments, products, sellers, category

def transform_data(customers, orders, order_items, payments, products, sellers, category):
    """Transform - Clean and process data"""
    print(f"[{datetime.now()}] Starting Transformation...")
    
    # Clean orders
    orders_clean = orders.dropna(subset=['order_status'])
    date_cols = ['order_approved_at','order_delivered_carrier_date','order_delivered_customer_date']
    for col in date_cols:
        orders_clean[col] = orders_clean[col].fillna('unknown')
    orders_clean['order_purchase_timestamp'] = pd.to_datetime(orders_clean['order_purchase_timestamp'])
    
    # Clean others
    customers_clean = customers.dropna()
    products_clean = products.merge(category, on='product_category_name', how='left').fillna('unknown')
    order_items_clean = order_items.dropna()
    payments_clean = payments.dropna()
    
    # Create fact table
    fact_orders = orders_clean.merge(order_items_clean, on='order_id', how='left')
    fact_orders = fact_orders.merge(payments_clean, on='order_id', how='left')
    fact_orders = fact_orders.merge(customers_clean, on='customer_id', how='left')
    fact_orders = fact_orders.drop_duplicates(subset=['order_id'])
    
    # Delay detection
    orders_analysis = orders_clean.copy()
    orders_analysis['order_purchase_timestamp'] = pd.to_datetime(orders_analysis['order_purchase_timestamp'])
    orders_analysis['order_estimated_delivery_date'] = pd.to_datetime(orders_analysis['order_estimated_delivery_date'], errors='coerce')
    orders_analysis['order_delivered_customer_date'] = pd.to_datetime(orders_analysis['order_delivered_customer_date'], errors='coerce')
    orders_analysis['estimated_days'] = (orders_analysis['order_estimated_delivery_date'] - orders_analysis['order_purchase_timestamp']).dt.days
    orders_analysis['actual_days'] = (orders_analysis['order_delivered_customer_date'] - orders_analysis['order_purchase_timestamp']).dt.days
    orders_analysis['delay_days'] = orders_analysis['actual_days'] - orders_analysis['estimated_days']
    orders_analysis['is_delayed'] = orders_analysis['delay_days'] > 0
    
    print(f"[{datetime.now()}] Transformation Complete!")
    return fact_orders, orders_analysis

def load_data(fact_orders, orders_analysis):
    """Load - Save to database"""
    print(f"[{datetime.now()}] Starting Load...")
    
    conn = sqlite3.connect('olist_warehouse.db')
    fact_orders.to_sql('fact_orders', conn, if_exists='replace', index=False)
    orders_analysis.to_sql('orders_analysis', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"[{datetime.now()}] Load Complete!")
    print(f"✅ {len(fact_orders)} records loaded!")

def run_quality_checks(fact_orders):
    """Data Quality Checks"""
    print(f"\n[{datetime.now()}] Running Quality Checks...")
    
    duplicates = fact_orders['order_id'].duplicated().sum()
    invalid_prices = fact_orders[fact_orders['price'] < 0].shape[0] if 'price' in fact_orders.columns else 0
    
    print(f"✅ Duplicates: {duplicates}")
    print(f"✅ Invalid Prices: {invalid_prices}")
    print(f"[{datetime.now()}] Quality Checks Complete!")