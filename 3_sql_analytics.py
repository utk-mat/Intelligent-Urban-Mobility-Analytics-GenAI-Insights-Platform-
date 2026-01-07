"""
Task 3: Analytical SQL Layer
Objective: Business-focused SQL analytics on cleaned data
"""

import pandas as pd
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text
import os


class SQLAnalytics:
    """
    Class for performing SQL analytics on mobility data
    """
    
    def __init__(self, data_path="data/cleaned/cleaned_taxi_data.csv", 
                 db_path="mobility_analytics.db", output_dir="outputs"):
        """
        Initialize SQL Analytics
        
        Args:
            data_path: Path to cleaned data CSV
            db_path: SQLite database path
            output_dir: Directory for output results
        """
        self.data_path = Path(data_path)
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.sql_results_dir = self.output_dir / "sql_results"
        self.sql_results_dir.mkdir(parents=True, exist_ok=True)
        
        self.engine = None
        self.conn = None
        
    def setup_database(self):
        """Load cleaned data into SQLite database"""
        print(f"\nSetting up database: {self.db_path}...")
        
        # Create SQLite engine
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.conn = self.engine.connect()
        
        # Load cleaned data
        print(f"Loading data from {self.data_path}...")
        df = pd.read_csv(self.data_path, parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
        
        # Write to SQLite
        table_name = 'taxi_trips'
        df.to_sql(table_name, self.engine, if_exists='replace', index=False)
        print(f"✓ Data loaded into table '{table_name}' ({len(df):,} rows)")
        
        return self.engine
    
    def execute_query(self, query, query_name):
        """
        Execute SQL query and save results
        
        Args:
            query: SQL query string
            query_name: Name for saving results
        """
        print(f"\nExecuting: {query_name}...")
        print("-" * 50)
        
        try:
            result = pd.read_sql_query(text(query), self.conn)
            print(f"✓ Query executed successfully ({len(result)} rows)")
            print(result.head(10))
            
            # Save results
            output_file = self.sql_results_dir / f"{query_name}.csv"
            result.to_csv(output_file, index=False)
            print(f"✓ Results saved to: {output_file}")
            
            return result
        except Exception as e:
            print(f"✗ Error executing query: {e}")
            return None
    
    def query_peak_demand_hours(self):
        """Query: Peak demand hours using GROUP BY"""
        query = """
        SELECT 
            pickup_hour,
            COUNT(*) as trip_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_fare,
            AVG(trip_distance) as avg_distance
        FROM taxi_trips
        GROUP BY pickup_hour
        ORDER BY trip_count DESC
        LIMIT 10;
        """
        return self.execute_query(query, "peak_demand_hours")
    
    def query_revenue_by_pickup_zone(self):
        """Query: Revenue by pickup zone"""
        # Check if PULocationID exists, otherwise use a different approach
        query = """
        SELECT 
            CASE 
                WHEN PULocationID IS NOT NULL THEN CAST(PULocationID AS TEXT)
                ELSE 'Unknown'
            END as pickup_location,
            COUNT(*) as trip_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_fare,
            AVG(trip_distance) as avg_distance
        FROM taxi_trips
        GROUP BY pickup_location
        ORDER BY total_revenue DESC
        LIMIT 20;
        """
        return self.execute_query(query, "revenue_by_pickup_zone")
    
    def query_top_revenue_days(self):
        """Query: Top 10 highest-revenue days"""
        query = """
        SELECT 
            DATE(tpep_pickup_datetime) as trip_date,
            COUNT(*) as trip_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_fare,
            AVG(trip_distance) as avg_distance,
            SUM(tip_amount) as total_tips
        FROM taxi_trips
        GROUP BY trip_date
        ORDER BY total_revenue DESC
        LIMIT 10;
        """
        return self.execute_query(query, "top_revenue_days")
    
    def query_avg_fare_by_weekday(self):
        """Query: Average fare by weekday"""
        query = """
        SELECT 
            pickup_day_name as weekday,
            COUNT(*) as trip_count,
            AVG(fare_amount) as avg_fare,
            AVG(total_amount) as avg_total_amount,
            AVG(tip_percentage) as avg_tip_percentage,
            SUM(total_amount) as total_revenue
        FROM taxi_trips
        GROUP BY pickup_day_name
        ORDER BY 
            CASE pickup_day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END;
        """
        return self.execute_query(query, "avg_fare_by_weekday")
    
    def query_monthly_growth(self):
        """Query: Monthly growth using window functions"""
        query = """
        WITH monthly_revenue AS (
            SELECT 
                pickup_year,
                pickup_month,
                SUM(total_amount) as monthly_revenue,
                COUNT(*) as monthly_trips
            FROM taxi_trips
            GROUP BY pickup_year, pickup_month
        ),
        revenue_with_growth AS (
            SELECT 
                pickup_year,
                pickup_month,
                monthly_revenue,
                monthly_trips,
                LAG(monthly_revenue) OVER (ORDER BY pickup_year, pickup_month) as prev_month_revenue,
                LAG(monthly_trips) OVER (ORDER BY pickup_year, pickup_month) as prev_month_trips
            FROM monthly_revenue
        )
        SELECT 
            pickup_year,
            pickup_month,
            monthly_revenue,
            monthly_trips,
            prev_month_revenue,
            CASE 
                WHEN prev_month_revenue IS NOT NULL THEN 
                    ((monthly_revenue - prev_month_revenue) / prev_month_revenue * 100)
                ELSE NULL
            END as revenue_growth_percent,
            CASE 
                WHEN prev_month_trips IS NOT NULL THEN 
                    ((monthly_trips - prev_month_trips) / prev_month_trips * 100)
                ELSE NULL
            END as trip_growth_percent
        FROM revenue_with_growth
        ORDER BY pickup_year, pickup_month;
        """
        return self.execute_query(query, "monthly_growth")
    
    def query_peak_vs_offpeak_analysis(self):
        """Query: Peak vs Off-Peak analysis"""
        query = """
        SELECT 
            CASE 
                WHEN is_peak_hour = 1 THEN 'Peak Hours'
                ELSE 'Off-Peak Hours'
            END as time_category,
            COUNT(*) as trip_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_fare,
            AVG(trip_distance) as avg_distance,
            AVG(trip_duration_minutes) as avg_duration,
            AVG(tip_percentage) as avg_tip_percentage
        FROM taxi_trips
        GROUP BY time_category;
        """
        return self.execute_query(query, "peak_vs_offpeak_analysis")
    
    def query_weekend_analysis(self):
        """Query: Weekend vs Weekday analysis"""
        query = """
        SELECT 
            CASE 
                WHEN is_weekend = 1 THEN 'Weekend'
                ELSE 'Weekday'
            END as day_type,
            COUNT(*) as trip_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_fare,
            AVG(trip_distance) as avg_distance,
            AVG(tip_percentage) as avg_tip_percentage
        FROM taxi_trips
        GROUP BY day_type;
        """
        return self.execute_query(query, "weekend_analysis")
    
    def query_revenue_per_mile_analysis(self):
        """Query: Revenue per mile by hour"""
        query = """
        SELECT 
            pickup_hour,
            COUNT(*) as trip_count,
            AVG(revenue_per_mile) as avg_revenue_per_mile,
            AVG(total_amount) as avg_total_amount,
            AVG(trip_distance) as avg_distance
        FROM taxi_trips
        WHERE revenue_per_mile > 0
        GROUP BY pickup_hour
        ORDER BY avg_revenue_per_mile DESC;
        """
        return self.execute_query(query, "revenue_per_mile_analysis")
    
    def generate_sql_report(self):
        """Generate summary report of all SQL queries"""
        print("\nGenerating SQL analytics report...")
        
        report_path = self.sql_results_dir / "sql_analytics_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("SQL ANALYTICS REPORT\n")
            f.write("="*70 + "\n\n")
            f.write("All query results have been saved as CSV files in:\n")
            f.write(f"{self.sql_results_dir}\n\n")
            f.write("Query Files:\n")
            f.write("-"*70 + "\n")
            f.write("1. peak_demand_hours.csv - Top 10 peak demand hours\n")
            f.write("2. revenue_by_pickup_zone.csv - Revenue by pickup location\n")
            f.write("3. top_revenue_days.csv - Top 10 highest revenue days\n")
            f.write("4. avg_fare_by_weekday.csv - Average fare by weekday\n")
            f.write("5. monthly_growth.csv - Monthly growth trends\n")
            f.write("6. peak_vs_offpeak_analysis.csv - Peak vs Off-Peak comparison\n")
            f.write("7. weekend_analysis.csv - Weekend vs Weekday comparison\n")
            f.write("8. revenue_per_mile_analysis.csv - Revenue per mile by hour\n")
            f.write("\n" + "="*70 + "\n")
        
        print(f"✓ Report saved: {report_path}")
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
        print("\n✓ Database connection closed")


def main():
    """Main execution function"""
    print("="*70)
    print("TASK 3: Analytical SQL Layer")
    print("="*70)
    
    # Initialize SQL Analytics
    sql_analytics = SQLAnalytics()
    
    # Setup database
    print("\n[Step 1] Setting up database...")
    sql_analytics.setup_database()
    
    # Execute queries
    print("\n[Step 2] Executing analytical queries...")
    sql_analytics.query_peak_demand_hours()
    sql_analytics.query_revenue_by_pickup_zone()
    sql_analytics.query_top_revenue_days()
    sql_analytics.query_avg_fare_by_weekday()
    sql_analytics.query_monthly_growth()
    sql_analytics.query_peak_vs_offpeak_analysis()
    sql_analytics.query_weekend_analysis()
    sql_analytics.query_revenue_per_mile_analysis()
    
    # Generate report
    print("\n[Step 3] Generating SQL report...")
    sql_analytics.generate_sql_report()
    
    # Close connection
    sql_analytics.close_connection()
    
    print("\n" + "="*70)
    print("✓ Task 3 Complete!")
    print(f"SQL results saved to: {sql_analytics.sql_results_dir}")
    print("="*70)


if __name__ == "__main__":
    main()



