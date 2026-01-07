"""
Task 4: Scalable ETL with PySpark
Objective: Handle large-scale trip data efficiently using PySpark
"""

import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, avg, count, when, 
    hour, dayofweek, month, year, quarter,
    to_timestamp, datediff, round as spark_round
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import pandas as pd


class PySparkETL:
    """
    PySpark-based ETL pipeline for large-scale mobility data processing
    """
    
    def __init__(self, data_path="data/cleaned/cleaned_taxi_data.csv", 
                 output_dir="data/processed", spark_master="local[*]"):
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Java 17+ requires these specific exports to allow Spark/Hadoop to access internal APIs
        java_options = (
            "--add-opens=java.base/java.lang=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
            "--add-opens=java.base/java.io=ALL-UNNAMED "
            "--add-opens=java.base/java.net=ALL-UNNAMED "
            "--add-opens=java.base/java.nio=ALL-UNNAMED "
            "--add-opens=java.base/java.util=ALL-UNNAMED "
            "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
            "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED "
            "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
            "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED "
            "--add-opens=java.base/sun.security.action=ALL-UNNAMED "
            "--add-opens=java.base/sun.util.calendar=ALL-UNNAMED "
            "--add-opens=java.security.sasl/conf=ALL-UNNAMED"
        )

        print("Initializing Spark Session...")
        self.spark = SparkSession.builder \
            .appName("MobilityAnalyticsETL") \
            .master(spark_master) \
            .config("spark.driver.extraJavaOptions", java_options) \
            .config("spark.executor.extraJavaOptions", java_options) \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        print("✓ Spark Session created with Java 17 compatibility")
        
    def load_data(self):
        """Load data into Spark DataFrame"""
        print(f"\nLoading data from {self.data_path}...")
        
        if self.data_path.is_file():
            # Single CSV file
            self.df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(str(self.data_path))
        elif self.data_path.is_dir():
            # Directory with multiple CSV files
            self.df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(str(self.data_path / "*.csv"))
        else:
            raise FileNotFoundError(f"Data path not found: {self.data_path}")
        
        print(f"✓ Loaded {self.df.count():,} records")
        print(f"  Partitions: {self.df.rdd.getNumPartitions()}")
        self.df.printSchema()
        
        return self.df
    
    def clean_and_transform(self):
        """Clean and transform data at scale"""
        print("\n" + "="*50)
        print("Cleaning and Transforming Data...")
        print("="*50)
        
        # Convert timestamp columns
        if 'tpep_pickup_datetime' in self.df.columns:
            self.df = self.df.withColumn(
                'tpep_pickup_datetime',
                to_timestamp(col('tpep_pickup_datetime'))
            )
        if 'tpep_dropoff_datetime' in self.df.columns:
            self.df = self.df.withColumn(
                'tpep_dropoff_datetime',
                to_timestamp(col('tpep_dropoff_datetime'))
            )
        
        # Add derived columns if not present
        if 'pickup_hour' not in self.df.columns:
            self.df = self.df.withColumn('pickup_hour', hour('tpep_pickup_datetime'))
        
        if 'pickup_month' not in self.df.columns:
            self.df = self.df.withColumn('pickup_month', month('tpep_pickup_datetime'))
        
        if 'pickup_year' not in self.df.columns:
            self.df = self.df.withColumn('pickup_year', year('tpep_pickup_datetime'))
        
        if 'pickup_quarter' not in self.df.columns:
            self.df = self.df.withColumn('pickup_quarter', quarter('tpep_pickup_datetime'))
        
        if 'pickup_day_of_week' not in self.df.columns:
            self.df = self.df.withColumn('pickup_day_of_week', dayofweek('tpep_pickup_datetime'))
        
        # Calculate trip duration if not present
        if 'trip_duration_minutes' not in self.df.columns:
            self.df = self.df.withColumn(
                'trip_duration_minutes',
                (col('tpep_dropoff_datetime').cast("long") - 
                 col('tpep_pickup_datetime').cast("long")) / 60
            )
        
        # Calculate revenue per mile if not present
        if 'revenue_per_mile' not in self.df.columns:
            self.df = self.df.withColumn(
                'revenue_per_mile',
                when(col('trip_distance') > 0, 
                     col('total_amount') / col('trip_distance'))
                .otherwise(0)
            )
        
        # Peak hour classification
        if 'is_peak_hour' not in self.df.columns:
            self.df = self.df.withColumn(
                'is_peak_hour',
                col('pickup_hour').isin([6, 7, 8, 9, 17, 18, 19, 20])
            )
        
        print("✓ Data cleaning and transformation complete")
        print(f"  Final record count: {self.df.count():,}")
        
        return self.df
    
    def compute_monthly_revenue(self):
        """Compute monthly revenue KPI"""
        print("\nComputing monthly revenue...")
        
        monthly_revenue = self.df.groupBy('pickup_year', 'pickup_month') \
            .agg(
                spark_sum('total_amount').alias('total_revenue'),
                count('*').alias('trip_count'),
                avg('total_amount').alias('avg_fare'),
                avg('trip_distance').alias('avg_distance')
            ) \
            .orderBy('pickup_year', 'pickup_month')
        
        output_path = self.output_dir / "monthly_revenue.parquet"
        monthly_revenue.write.mode('overwrite').parquet(str(output_path))
        print(f"✓ Saved: {output_path}")
        
        # Show results
        print("\nMonthly Revenue Summary:")
        monthly_revenue.show(20, truncate=False)
        
        return monthly_revenue
    
    def compute_demand_by_zone(self):
        """Compute demand by pickup zone"""
        print("\nComputing demand by zone...")
        
        # Check if PULocationID exists
        if 'PULocationID' in self.df.columns:
            zone_demand = self.df.groupBy('PULocationID') \
                .agg(
                    count('*').alias('trip_count'),
                    spark_sum('total_amount').alias('total_revenue'),
                    avg('total_amount').alias('avg_fare'),
                    avg('trip_distance').alias('avg_distance'),
                    avg('trip_duration_minutes').alias('avg_duration')
                ) \
                .orderBy(col('trip_count').desc())
            
            output_path = self.output_dir / "demand_by_zone.parquet"
            zone_demand.write.mode('overwrite').parquet(str(output_path))
            print(f"✓ Saved: {output_path}")
            
            print("\nTop 10 Zones by Demand:")
            zone_demand.show(10, truncate=False)
            
            return zone_demand
        else:
            print("⚠ PULocationID column not found, skipping zone analysis")
            return None
    
    def compute_peak_hour_congestion(self):
        """Compute peak-hour congestion indicators"""
        print("\nComputing peak-hour congestion indicators...")
        
        congestion_metrics = self.df.groupBy('pickup_hour', 'is_peak_hour') \
            .agg(
                count('*').alias('trip_count'),
                avg('trip_duration_minutes').alias('avg_duration'),
                avg('trip_distance').alias('avg_distance'),
                # FIX: Wrap 'trip_duration_minutes' in col()
                avg(col('trip_duration_minutes') / col('trip_distance')).alias('avg_speed_factor'),
                spark_sum('total_amount').alias('total_revenue')
            ) \
            .orderBy('pickup_hour')
        
        
        output_path = self.output_dir / "peak_hour_congestion.parquet"
        congestion_metrics.write.mode('overwrite').parquet(str(output_path))
        print(f"✓ Saved: {output_path}")
        
        print("\nPeak Hour Congestion Metrics:")
        congestion_metrics.show(24, truncate=False)
        
        return congestion_metrics
    
    def compute_high_value_segments(self):
        """Compute high-value trip segments"""
        print("\nComputing high-value trip segments...")
        
        # Segment trips by revenue per mile
        high_value_segments = self.df \
            .withColumn(
                'value_segment',
                when(col('revenue_per_mile') >= 10, 'High Value')
                .when(col('revenue_per_mile') >= 5, 'Medium Value')
                .otherwise('Low Value')
            ) \
            .groupBy('value_segment', 'pickup_hour') \
            .agg(
                count('*').alias('trip_count'),
                avg('revenue_per_mile').alias('avg_revenue_per_mile'),
                spark_sum('total_amount').alias('total_revenue'),
                avg('trip_distance').alias('avg_distance')
            ) \
            .orderBy('value_segment', 'pickup_hour')
        
        output_path = self.output_dir / "high_value_segments.parquet"
        high_value_segments.write.mode('overwrite').parquet(str(output_path))
        print(f"✓ Saved: {output_path}")
        
        print("\nHigh-Value Trip Segments:")
        high_value_segments.show(50, truncate=False)
        
        return high_value_segments
    
    def explain_plan(self):
        """Capture and display Spark execution plan"""
        print("\n" + "="*50)
        print("Spark Execution Plan (DAG)")
        print("="*50)
        
        # Use a sample query to show execution plan
        sample_query = self.df.groupBy('pickup_year', 'pickup_month') \
            .agg(spark_sum('total_amount').alias('total_revenue'))
        
        print("\nLogical Plan:")
        sample_query.explain(extended=True)
        
        print("\nPhysical Plan:")
        sample_query.explain(mode="cost")
        
    def write_final_output(self):
        """Write final processed data to Parquet"""
        print("\nWriting final processed data to Parquet...")
        
        output_path = self.output_dir / "processed_taxi_data.parquet"
        
        # Repartition for better performance
        num_partitions = max(1, self.df.rdd.getNumPartitions())
        self.df.repartition(num_partitions).write \
            .mode('overwrite') \
            .option("compression", "snappy") \
            .parquet(str(output_path))
        
        print(f"✓ Final data saved to: {output_path}")
        print(f"  Partitions: {num_partitions}")
        
        return output_path
    
    def stop_spark(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("\n✓ Spark session stopped")


def main():
    """Main execution function"""
    print("="*70)
    print("TASK 4: Scalable ETL with PySpark")
    print("="*70)
    
    etl = None
    try:
        # Initialize ETL
        etl = PySparkETL()
        
        # Load data
        print("\n[Step 1] Loading data...")
        etl.load_data()
        
        # Clean and transform
        print("\n[Step 2] Cleaning and transforming data...")
        etl.clean_and_transform()
        
        # Compute KPIs
        print("\n[Step 3] Computing KPIs...")
        etl.compute_monthly_revenue()
        etl.compute_demand_by_zone()
        etl.compute_peak_hour_congestion()
        etl.compute_high_value_segments()
        
        # Explain execution plan
        print("\n[Step 4] Capturing execution plan...")
        etl.explain_plan()
        
        # Write final output
        print("\n[Step 5] Writing final output...")
        etl.write_final_output()
        
        print("\n" + "="*70)
        print("✓ Task 4 Complete!")
        print(f"Processed data saved to: {etl.output_dir}")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if etl:
            print("\nSpark UI available at: http://localhost:4040")
            input("Press ENTER to stop Spark and exit...")
            etl.stop_spark()

if __name__ == "__main__":
    main()



