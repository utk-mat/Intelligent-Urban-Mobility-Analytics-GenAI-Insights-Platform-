"""
Task 1: Data Ingestion & Cleaning with OOP
Objective: Prepare raw trip data for analytics using Object-Oriented Programming
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import kagglehub
from kagglehub import KaggleDatasetAdapter


class MobilityDataAnalyzer:
    """
    OOP-based class for loading, cleaning, and feature engineering of mobility data
    """
    
    def __init__(self, data_dir="data"):
        """
        Initialize the analyzer with data directory paths
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.cleaned_dir = self.data_dir / "cleaned"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.cleaned_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = None
        self.cleaned_df = None
        
    def load_data(self, dataset_name="elemento/nyc-yellow-taxi-trip-data", 
              file_path="yellow_tripdata_2015-01.csv", sample_size=None):
        """
        Load raw taxi trip data from Kaggle
        
        Args:
            dataset_name: Kaggle dataset identifier
            file_path: Specific file path within dataset (empty for all files)
            sample_size: Number of rows to sample (None for full dataset)
        """
        print("Loading data from Kaggle...")
        try:
            # Load the dataset
            self.df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                dataset_name,
                file_path,
            )
            
            # Sample if specified (useful for testing)
            if sample_size and len(self.df) > sample_size:
                print(f"Sampling {sample_size} rows from {len(self.df)} total rows...")
                self.df = self.df.sample(n=sample_size, random_state=42)
            
            print(f"Loaded {len(self.df)} records")
            print(f"Columns: {list(self.df.columns)}")
            print("\nFirst 5 records:")
            print(self.df.head())
            print("\nData Info:")
            print(self.df.info())
            
            # Save raw data
            raw_file = self.raw_dir / "raw_taxi_data.csv"
            self.df.to_csv(raw_file, index=False)
            print(f"\nRaw data saved to: {raw_file}")
            
            return self.df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def clean_data(self):
        """
        Clean the loaded data:
        - Handle missing passenger counts
        - Remove zero or negative trip distances
        - Fix invalid timestamps
        - Convert data types
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        print("\n" + "="*50)
        print("Starting Data Cleaning...")
        print("="*50)
        
        df_clean = self.df.copy()
        initial_rows = len(df_clean)
        
        # 1. Handle missing passenger counts
        print(f"\n1. Handling missing passenger counts...")
        missing_passengers = df_clean['passenger_count'].isna().sum()
        print(f"   Missing passenger counts: {missing_passengers}")
        df_clean['passenger_count'] = df_clean['passenger_count'].fillna(1)  # Default to 1
        
        # 2. Remove zero or negative trip distances
        print(f"\n2. Removing invalid trip distances...")
        invalid_distances = len(df_clean[df_clean['trip_distance'] <= 0])
        print(f"   Invalid distances (<=0): {invalid_distances}")
        df_clean = df_clean[df_clean['trip_distance'] > 0]
        
        # 3. Convert pickup & dropoff times to datetime
        print(f"\n3. Converting timestamps...")
        datetime_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        for col in datetime_columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                    invalid_dates = df_clean[col].isna().sum()
                    print(f"   {col}: {invalid_dates} invalid dates")
                except Exception as e:
                    print(f"   Error converting {col}: {e}")
        
        # Remove rows with invalid timestamps
        df_clean = df_clean.dropna(subset=datetime_columns)
        
        # 4. Convert fare, tip, total amount to numeric
        print(f"\n4. Converting monetary columns to numeric...")
        monetary_columns = ['fare_amount', 'tip_amount', 'total_amount', 
                           'tolls_amount', 'extra', 'mta_tax']
        for col in monetary_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                df_clean[col] = df_clean[col].fillna(0)
        
        # Remove rows with negative or zero total amount
        df_clean = df_clean[df_clean['total_amount'] > 0]
        
        # 5. Remove duplicates
        print(f"\n5. Removing duplicates...")
        duplicates = df_clean.duplicated().sum()
        print(f"   Duplicate rows: {duplicates}")
        df_clean = df_clean.drop_duplicates()
        
        # Summary
        final_rows = len(df_clean)
        removed_rows = initial_rows - final_rows
        print(f"\n" + "="*50)
        print(f"Cleaning Summary:")
        print(f"  Initial rows: {initial_rows:,}")
        print(f"  Final rows: {final_rows:,}")
        print(f"  Removed rows: {removed_rows:,} ({removed_rows/initial_rows*100:.2f}%)")
        print("="*50)
        
        self.cleaned_df = df_clean
        return df_clean
    
    def feature_engineering(self):
        """
        Create new features:
        - Hour of day
        - Day of week
        - Month
        - Quarter
        - Trip duration
        - Revenue per mile
        """
        if self.cleaned_df is None:
            raise ValueError("No cleaned data. Call clean_data() first.")
        
        print("\n" + "="*50)
        print("Feature Engineering...")
        print("="*50)
        
        df = self.cleaned_df.copy()
        
        # Extract datetime features from pickup time
        pickup_col = 'tpep_pickup_datetime'
        if pickup_col in df.columns:
            df['pickup_hour'] = df[pickup_col].dt.hour
            df['pickup_day_of_week'] = df[pickup_col].dt.dayofweek  # 0=Monday, 6=Sunday
            df['pickup_day_name'] = df[pickup_col].dt.day_name()
            df['pickup_month'] = df[pickup_col].dt.month
            df['pickup_quarter'] = df[pickup_col].dt.quarter
            df['pickup_date'] = df[pickup_col].dt.date
            df['pickup_year'] = df[pickup_col].dt.year
            
            print(f"✓ Extracted datetime features from {pickup_col}")
        
        # Calculate trip duration
        dropoff_col = 'tpep_dropoff_datetime'
        if pickup_col in df.columns and dropoff_col in df.columns:
            df['trip_duration_minutes'] = (
                (df[dropoff_col] - df[pickup_col]).dt.total_seconds() / 60
            )
            # Remove trips with negative or zero duration
            df = df[df['trip_duration_minutes'] > 0]
            print(f"✓ Calculated trip duration")
        
        # Revenue per mile
        if 'total_amount' in df.columns and 'trip_distance' in df.columns:
            df['revenue_per_mile'] = df['total_amount'] / df['trip_distance']
            df['revenue_per_mile'] = df['revenue_per_mile'].replace([np.inf, -np.inf], 0)
            print(f"✓ Calculated revenue per mile")
        
        # Tip percentage
        if 'tip_amount' in df.columns and 'fare_amount' in df.columns:
            df['tip_percentage'] = (df['tip_amount'] / df['fare_amount'] * 100).fillna(0)
            df['tip_percentage'] = df['tip_percentage'].replace([np.inf, -np.inf], 0)
            print(f"✓ Calculated tip percentage")
        
        # Peak hours classification (6-10 AM, 5-9 PM)
        if 'pickup_hour' in df.columns:
            df['is_peak_hour'] = df['pickup_hour'].isin(
                list(range(6, 10)) + list(range(17, 21))
            )
            print(f"✓ Classified peak hours")
        
        # Weekend flag
        if 'pickup_day_of_week' in df.columns:
            df['is_weekend'] = df['pickup_day_of_week'].isin([5, 6])
            print(f"✓ Classified weekends")
        
        self.cleaned_df = df
        print(f"\nFinal dataset shape: {df.shape}")
        print(f"New features added: {set(df.columns) - set(self.df.columns) if self.df is not None else set()}")
        
        return df
    
    def export_clean_data(self, filename="cleaned_taxi_data.csv"):
        """
        Export cleaned and feature-engineered data
        
        Args:
            filename: Output filename
        """
        if self.cleaned_df is None:
            raise ValueError("No cleaned data. Run clean_data() and feature_engineering() first.")
        
        output_path = self.cleaned_dir / filename
        self.cleaned_df.to_csv(output_path, index=False)
        print(f"\n✓ Cleaned data exported to: {output_path}")
        print(f"  Rows: {len(self.cleaned_df):,}")
        print(f"  Columns: {len(self.cleaned_df.columns)}")
        
        return output_path
    
    def get_summary_statistics(self):
        """Get summary statistics of cleaned data"""
        if self.cleaned_df is None:
            raise ValueError("No cleaned data available.")
        
        print("\n" + "="*50)
        print("Summary Statistics")
        print("="*50)
        print(self.cleaned_df.describe())
        return self.cleaned_df.describe()


def main():
    """Main execution function"""
    print("="*70)
    print("TASK 1: Data Ingestion & Cleaning")
    print("="*70)
    
    # Initialize analyzer
    analyzer = MobilityDataAnalyzer()
    
    # Load data (using sample for faster processing - remove sample_size for full dataset)
    print("\n[Step 1] Loading data...")
    analyzer.load_data(sample_size=100000)  # Remove sample_size for full dataset
    
    # Clean data
    print("\n[Step 2] Cleaning data...")
    analyzer.clean_data()
    
    # Feature engineering
    print("\n[Step 3] Feature engineering...")
    analyzer.feature_engineering()
    
    # Export cleaned data
    print("\n[Step 4] Exporting cleaned data...")
    analyzer.export_clean_data()
    
    # Summary statistics
    print("\n[Step 5] Generating summary statistics...")
    analyzer.get_summary_statistics()
    
    print("\n" + "="*70)
    print("✓ Task 1 Complete!")
    print("="*70)


if __name__ == "__main__":
    main()





