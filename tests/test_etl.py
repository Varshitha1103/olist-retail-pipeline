import pytest
import pandas as pd
import sqlite3

# Full path to CSV files
DATA_PATH = r"C:\Users\varshapreetham\Desktop\Brazillian dataset"

# Test 1 - Data Loading
def test_data_loading():
    customers = pd.read_csv(f'{DATA_PATH}\\olist_customers_dataset.csv')
    assert len(customers) > 0
    assert 'customer_id' in customers.columns
    print("✅ Test 1 Passed: Data Loading")

# Test 2 - Data Cleaning
def test_data_cleaning():
    orders = pd.read_csv(f'{DATA_PATH}\\olist_orders_dataset.csv')
    orders_clean = orders.dropna(subset=['order_status'])
    assert orders_clean['order_status'].isnull().sum() == 0
    print("✅ Test 2 Passed: Data Cleaning")

# Test 3 - No Negative Prices
def test_no_negative_prices():
    order_items = pd.read_csv(
        f'{DATA_PATH}\\olist_order_items_dataset.csv',
        engine='python',
        on_bad_lines='skip')
    assert len(order_items[order_items['price'] < 0]) == 0
    print("✅ Test 3 Passed: No Negative Prices")

# Test 4 - Database Connection
def test_database_connection():
    conn = sqlite3.connect(':memory:')
    assert conn is not None
    conn.close()
    print("✅ Test 4 Passed: Database Connection")

# Test 5 - Star Schema
def test_star_schema():
    orders = pd.read_csv(f'{DATA_PATH}\\olist_orders_dataset.csv')
    customers = pd.read_csv(f'{DATA_PATH}\\olist_customers_dataset.csv')
    fact = orders.merge(customers, on='customer_id', how='left')
    assert len(fact) > 0
    assert 'order_id' in fact.columns
    print("✅ Test 5 Passed: Star Schema")

# Test 6 - Delay Detection
def test_delay_detection():
    orders = pd.read_csv(f'{DATA_PATH}\\olist_orders_dataset.csv')
    orders['order_purchase_timestamp'] = pd.to_datetime(
        orders['order_purchase_timestamp'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(
        orders['order_estimated_delivery_date'], errors='coerce')
    orders['order_delivered_customer_date'] = pd.to_datetime(
        orders['order_delivered_customer_date'], errors='coerce')
    orders['delay_days'] = (
        orders['order_delivered_customer_date'] -
        orders['order_estimated_delivery_date']).dt.days
    orders['is_delayed'] = orders['delay_days'] > 0
    delayed = orders['is_delayed'].sum()
    assert delayed > 0
    print(f"✅ Test 6 Passed: {delayed} delays found")

if __name__ == "__main__":
    test_data_loading()
    test_data_cleaning()
    test_no_negative_prices()
    test_database_connection()
    test_star_schema()
    test_delay_detection()
    print("\n🎉 ALL TESTS PASSED!")