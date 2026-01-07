"""
Task 2: KPI Computation & Exploratory Analysis
Objective: Compute core KPIs and create visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class KPIAnalyzer:
    """
    Class for computing and visualizing mobility KPIs
    """
    
    def __init__(self, data_path="data/cleaned/cleaned_taxi_data.csv", output_dir="outputs"):
        """
        Initialize KPI Analyzer
        
        Args:
            data_path: Path to cleaned data CSV
            output_dir: Directory for output visualizations
        """
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.visualizations_dir = self.output_dir / "visualizations"
        self.visualizations_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = None
        self.kpis = {}
        
    def load_data(self):
        """Load cleaned data"""
        print(f"Loading data from {self.data_path}...")
        self.df = pd.read_csv(self.data_path, parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
        print(f"Loaded {len(self.df):,} records")
        return self.df
    
    def compute_kpis(self):
        """Compute all core KPIs"""
        print("\n" + "="*50)
        print("Computing Core KPIs...")
        print("="*50)
        
        # 1. Total & Monthly Trip Revenue
        self.kpis['total_revenue'] = self.df['total_amount'].sum()
        monthly_revenue = self.df.groupby(['pickup_year', 'pickup_month'])['total_amount'].sum()
        self.kpis['monthly_revenue'] = monthly_revenue
        print(f"✓ Total Revenue: ${self.kpis['total_revenue']:,.2f}")
        
        # 2. Average Trip Distance
        self.kpis['avg_trip_distance'] = self.df['trip_distance'].mean()
        print(f"✓ Average Trip Distance: {self.kpis['avg_trip_distance']:.2f} miles")
        
        # 3. Average Fare per Trip
        self.kpis['avg_fare_per_trip'] = self.df['fare_amount'].mean()
        print(f"✓ Average Fare per Trip: ${self.kpis['avg_fare_per_trip']:.2f}")
        
        # 4. Tip Percentage
        self.kpis['avg_tip_percentage'] = self.df['tip_percentage'].mean()
        self.kpis['total_tips'] = self.df['tip_amount'].sum()
        print(f"✓ Average Tip Percentage: {self.kpis['avg_tip_percentage']:.2f}%")
        
        # 5. Trips per Hour (Demand Pattern)
        self.kpis['trips_per_hour'] = self.df.groupby('pickup_hour').size()
        print(f"✓ Trips per Hour computed")
        
        # 6. Revenue per Mile
        self.kpis['avg_revenue_per_mile'] = self.df['revenue_per_mile'].mean()
        print(f"✓ Average Revenue per Mile: ${self.kpis['avg_revenue_per_mile']:.2f}")
        
        # 7. Peak vs Off-Peak Utilization
        peak_trips = self.df[self.df['is_peak_hour']].shape[0]
        off_peak_trips = self.df[~self.df['is_peak_hour']].shape[0]
        total_trips = len(self.df)
        
        self.kpis['peak_utilization'] = (peak_trips / total_trips) * 100
        self.kpis['off_peak_utilization'] = (off_peak_trips / total_trips) * 100
        print(f"✓ Peak Hour Utilization: {self.kpis['peak_utilization']:.2f}%")
        print(f"✓ Off-Peak Utilization: {self.kpis['off_peak_utilization']:.2f}%")
        
        # 8. Total trips
        self.kpis['total_trips'] = total_trips
        
        # 9. Average trip duration
        self.kpis['avg_trip_duration'] = self.df['trip_duration_minutes'].mean()
        print(f"✓ Average Trip Duration: {self.kpis['avg_trip_duration']:.2f} minutes")
        
        return self.kpis
    
    def visualize_monthly_revenue(self):
        """Visualize monthly revenue trends"""
        print("\nCreating monthly revenue visualization...")
        
        monthly_rev = self.kpis['monthly_revenue'].reset_index()
        monthly_rev['date'] = pd.to_datetime(
        dict(
            year=monthly_rev['pickup_year'],
            month=monthly_rev['pickup_month'],
            day=1
            )
        )

        monthly_rev = monthly_rev.sort_values('date')
        
        plt.figure(figsize=(14, 6))
        plt.plot(monthly_rev['date'], monthly_rev['total_amount'], 
                marker='o', linewidth=2, markersize=8)
        plt.title('Monthly Revenue Trends', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Revenue ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Format y-axis as currency
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        output_path = self.visualizations_dir / "monthly_revenue_trends.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")
    
    def visualize_hourly_demand_heatmap(self):
        """Create hourly demand heatmap"""
        print("\nCreating hourly demand heatmap...")
        
        # Create pivot table: day of week vs hour
        heatmap_data = self.df.pivot_table(
            values='total_amount',
            index='pickup_day_name',
            columns='pickup_hour',
            aggfunc='count',
            fill_value=0
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])
        
        plt.figure(figsize=(16, 8))
        sns.heatmap(heatmap_data, cmap='YlOrRd', annot=False, fmt='.0f', 
                   cbar_kws={'label': 'Number of Trips'})
        plt.title('Hourly Demand Heatmap (Trips by Day of Week and Hour)', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Hour of Day', fontsize=12)
        plt.ylabel('Day of Week', fontsize=12)
        plt.tight_layout()
        
        output_path = self.visualizations_dir / "hourly_demand_heatmap.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")
    
    def visualize_fare_distance_outliers(self):
        """Visualize fare and distance outliers"""
        print("\nCreating fare & distance outlier visualization...")
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Fare distribution
        axes[0].boxplot(self.df['fare_amount'], vert=True)
        axes[0].set_title('Fare Amount Distribution', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Fare Amount ($)', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # Distance distribution
        axes[1].boxplot(self.df['trip_distance'], vert=True)
        axes[1].set_title('Trip Distance Distribution', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Distance (miles)', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.visualizations_dir / "fare_distance_outliers.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")
    
    def visualize_tip_distribution(self):
        """Visualize tip distribution by time of day"""
        print("\nCreating tip distribution visualization...")
        
        # Create time of day categories
        self.df['time_of_day'] = pd.cut(
            self.df['pickup_hour'],
            bins=[0, 6, 12, 18, 24],
            labels=['Night (0-6)', 'Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)']
        )
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Tip percentage by time of day
        tip_by_time = self.df.groupby('time_of_day')['tip_percentage'].mean()
        axes[0].bar(tip_by_time.index, tip_by_time.values, color='skyblue', edgecolor='navy')
        axes[0].set_title('Average Tip Percentage by Time of Day', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Tip Percentage (%)', fontsize=12)
        axes[0].set_xlabel('Time of Day', fontsize=12)
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Tip amount distribution
        axes[1].hist(self.df['tip_amount'], bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
        axes[1].set_title('Tip Amount Distribution', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Tip Amount ($)', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.visualizations_dir / "tip_distribution.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")
    
    def visualize_trips_per_hour(self):
        """Visualize trips per hour pattern"""
        print("\nCreating trips per hour visualization...")
        
        trips_hour = self.kpis['trips_per_hour']
        
        plt.figure(figsize=(14, 6))
        plt.bar(trips_hour.index, trips_hour.values, color='steelblue', edgecolor='navy', alpha=0.7)
        plt.title('Trips per Hour (Demand Pattern)', fontsize=16, fontweight='bold')
        plt.xlabel('Hour of Day', fontsize=12)
        plt.ylabel('Number of Trips', fontsize=12)
        plt.xticks(range(24))
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        output_path = self.visualizations_dir / "trips_per_hour.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")
    
    def generate_kpi_report(self):
        """Generate a text report of all KPIs"""
        print("\nGenerating KPI report...")
        
        report_path = self.output_dir / "kpi_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MOBILITY ANALYTICS - KPI REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("CORE KPIs\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Trips: {self.kpis['total_trips']:,}\n")
            f.write(f"Total Revenue: ${self.kpis['total_revenue']:,.2f}\n")
            f.write(f"Average Trip Distance: {self.kpis['avg_trip_distance']:.2f} miles\n")
            f.write(f"Average Fare per Trip: ${self.kpis['avg_fare_per_trip']:.2f}\n")
            f.write(f"Average Tip Percentage: {self.kpis['avg_tip_percentage']:.2f}%\n")
            f.write(f"Total Tips: ${self.kpis['total_tips']:,.2f}\n")
            f.write(f"Average Revenue per Mile: ${self.kpis['avg_revenue_per_mile']:.2f}\n")
            f.write(f"Average Trip Duration: {self.kpis['avg_trip_duration']:.2f} minutes\n")
            f.write(f"Peak Hour Utilization: {self.kpis['peak_utilization']:.2f}%\n")
            f.write(f"Off-Peak Utilization: {self.kpis['off_peak_utilization']:.2f}%\n\n")
            
            f.write("MONTHLY REVENUE\n")
            f.write("-"*70 + "\n")
            for (year, month), revenue in self.kpis['monthly_revenue'].items():
                f.write(f"{year}-{month:02d}: ${revenue:,.2f}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print(f"✓ Report saved: {report_path}")
        return report_path


def main():
    """Main execution function"""
    print("="*70)
    print("TASK 2: KPI Computation & Exploratory Analysis")
    print("="*70)
    
    # Initialize analyzer
    analyzer = KPIAnalyzer()
    
    # Load data
    print("\n[Step 1] Loading cleaned data...")
    analyzer.load_data()
    
    # Compute KPIs
    print("\n[Step 2] Computing KPIs...")
    analyzer.compute_kpis()
    
    # Create visualizations
    print("\n[Step 3] Creating visualizations...")
    analyzer.visualize_monthly_revenue()
    analyzer.visualize_hourly_demand_heatmap()
    analyzer.visualize_fare_distance_outliers()
    analyzer.visualize_tip_distribution()
    analyzer.visualize_trips_per_hour()
    
    # Generate report
    print("\n[Step 4] Generating KPI report...")
    analyzer.generate_kpi_report()
    
    print("\n" + "="*70)
    print("✓ Task 2 Complete!")
    print(f"Visualizations saved to: {analyzer.visualizations_dir}")
    print("="*70)


if __name__ == "__main__":
    main()





