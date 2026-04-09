from datetime import datetime

class DataLineage:
    def __init__(self):
        self.lineage = []
    
    def track(self, source, destination, 
              operation, rows, status="SUCCESS"):
        entry = {
            'timestamp': datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'),
            'source': source,
            'destination': destination,
            'operation': operation,
            'rows_processed': rows,
            'status': status
        }
        self.lineage.append(entry)
        print(f"✅ [{entry['timestamp']}] "
              f"{operation}: {source} → "
              f"{destination} ({rows} rows)")
    
    def get_report(self):
        print("\n" + "="*60)
        print("         DATA LINEAGE REPORT")
        print("="*60)
        for entry in self.lineage:
            print(f"\n📍 Operation: {entry['operation']}")
            print(f"   Source: {entry['source']}")
            print(f"   Destination: {entry['destination']}")
            print(f"   Rows: {entry['rows_processed']}")
            print(f"   Status: {entry['status']}")
            print(f"   Time: {entry['timestamp']}")
        print("\n" + "="*60)
        print(f"Total Operations: {len(self.lineage)}")
        print("="*60)

# Run lineage tracking
if __name__ == "__main__":
    lineage = DataLineage()
    
    # Track entire pipeline
    lineage.track(
        source="olist_customers_dataset.csv",
        destination="customers_clean",
        operation="EXTRACT & CLEAN",
        rows=99441
    )
    lineage.track(
        source="olist_orders_dataset.csv",
        destination="orders_clean",
        operation="EXTRACT & CLEAN",
        rows=23619
    )
    lineage.track(
        source="olist_order_items_dataset.csv",
        destination="order_items_clean",
        operation="EXTRACT & CLEAN",
        rows=38047
    )
    lineage.track(
        source="customers_clean + orders_clean",
        destination="fact_orders",
        operation="STAR SCHEMA MERGE",
        rows=25368
    )
    lineage.track(
        source="fact_orders",
        destination="orders_analysis",
        operation="DELAY DETECTION",
        rows=23619
    )
    lineage.track(
        source="orders_analysis",
        destination="risk_scores",
        operation="RISK SCORING",
        rows=23619
    )
    lineage.track(
        source="orders_analysis",
        destination="spark_dataframe",
        operation="PYSPARK TRANSFORM",
        rows=11808
    )
    lineage.track(
        source="olist_orders_topic",
        destination="kafka_consumer",
        operation="KAFKA STREAMING",
        rows=10
    )
    lineage.track(
        source="fact_orders",
        destination="olist_warehouse.db",
        operation="LOAD TO WAREHOUSE",
        rows=23619
    )
    
    # Print report
    lineage.get_report()