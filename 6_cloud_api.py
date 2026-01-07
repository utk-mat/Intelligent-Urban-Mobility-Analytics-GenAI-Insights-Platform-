"""
Task 6: Cloud Deployment - Serverless Mobility Analytics API
Objective: Expose analytics via cloud APIs (AWS Lambda / Azure Function)
"""

import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from datetime import datetime

# AWS imports (optional)
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

load_dotenv()


class MobilityAnalyticsAPI:
    """
    FastAPI-based REST API for mobility analytics
    Can be deployed to AWS Lambda, Azure Functions, or run locally
    """
    
    def __init__(self, data_path="data/cleaned/cleaned_taxi_data.csv",
                 kpi_path="outputs/kpi_report.txt"):
        """
        Initialize API
        
        Args:
            data_path: Path to cleaned data
            kpi_path: Path to KPI report
        """
        self.data_path = Path(data_path)
        self.kpi_path = Path(kpi_path)
        
        # Load data
        self.df = None
        self.kpi_data = {}
        self._load_data()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Mobility Analytics API",
            description="REST API for urban mobility analytics and insights",
            version="1.0.0"
        )
        
        # Setup routes
        self._setup_routes()
    
    def _load_data(self):
        """Load data and KPIs"""
        print("Loading data for API...")
        
        if self.data_path.exists():
            self.df = pd.read_csv(self.data_path, 
                                 parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
            print(f"✓ Loaded {len(self.df):,} records")
        
        if self.kpi_path.exists():
            with open(self.kpi_path, 'r') as f:
                content = f.read()
                # Parse basic KPIs from report
                # In production, this would be from a database or cache
                self.kpi_data = {"report": content}
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "Mobility Analytics API",
                "version": "1.0.0",
                "endpoints": [
                    "/monthly-revenue",
                    "/peak-hours",
                    "/top-zones",
                    "/kpis",
                    "/health"
                ]
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/monthly-revenue")
        async def monthly_revenue(year: Optional[int] = None, month: Optional[int] = None):
            """Get monthly revenue data"""
            try:
                if self.df is None:
                    raise HTTPException(status_code=503, detail="Data not loaded")
                
                df = self.df.copy()
                
                if year:
                    df = df[df['pickup_year'] == year]
                if month:
                    df = df[df['pickup_month'] == month]
                
                monthly_rev = df.groupby(['pickup_year', 'pickup_month']).agg({
                    'total_amount': 'sum',
                    'fare_amount': 'sum',
                    'tip_amount': 'sum'
                }).reset_index()
                
                monthly_rev['total_revenue'] = monthly_rev['total_amount']
                monthly_rev['total_fare'] = monthly_rev['fare_amount']
                monthly_rev['total_tips'] = monthly_rev['tip_amount']
                
                result = monthly_rev[['pickup_year', 'pickup_month', 
                                     'total_revenue', 'total_fare', 'total_tips']].to_dict('records')
                
                return JSONResponse(content={
                    "success": True,
                    "data": result,
                    "count": len(result)
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/peak-hours")
        async def peak_hours():
            """Get peak hours analysis"""
            try:
                if self.df is None:
                    raise HTTPException(status_code=503, detail="Data not loaded")
                
                peak_data = self.df.groupby('pickup_hour').agg({
                    'total_amount': ['count', 'sum', 'mean'],
                    'trip_distance': 'mean',
                    'trip_duration_minutes': 'mean'
                }).reset_index()
                
                peak_data.columns = ['hour', 'trip_count', 'total_revenue', 
                                    'avg_fare', 'avg_distance', 'avg_duration']
                peak_data = peak_data.sort_values('trip_count', ascending=False)
                
                result = peak_data.to_dict('records')
                
                return JSONResponse(content={
                    "success": True,
                    "data": result,
                    "peak_hour": int(peak_data.iloc[0]['hour'])
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/top-zones")
        async def top_zones(limit: int = 10):
            """Get top zones by revenue"""
            try:
                if self.df is None:
                    raise HTTPException(status_code=503, detail="Data not loaded")
                
                if 'PULocationID' not in self.df.columns:
                    return JSONResponse(content={
                        "success": False,
                        "message": "Location data not available"
                    })
                
                zone_data = self.df.groupby('PULocationID').agg({
                    'total_amount': ['count', 'sum', 'mean'],
                    'trip_distance': 'mean'
                }).reset_index()
                
                zone_data.columns = ['zone_id', 'trip_count', 'total_revenue', 
                                   'avg_fare', 'avg_distance']
                zone_data = zone_data.sort_values('total_revenue', ascending=False).head(limit)
                
                result = zone_data.to_dict('records')
                
                return JSONResponse(content={
                    "success": True,
                    "data": result,
                    "count": len(result)
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/kpis")
        async def kpis():
            """Get all KPIs"""
            try:
                if self.df is None:
                    raise HTTPException(status_code=503, detail="Data not loaded")
                
                kpi_results = {
                    "total_trips": int(len(self.df)),
                    "total_revenue": float(self.df['total_amount'].sum()),
                    "avg_fare": float(self.df['fare_amount'].mean()),
                    "avg_distance": float(self.df['trip_distance'].mean()),
                    "avg_tip_percentage": float(self.df['tip_percentage'].mean()),
                    "avg_revenue_per_mile": float(self.df['revenue_per_mile'].mean()),
                    "avg_trip_duration": float(self.df['trip_duration_minutes'].mean()),
                    "peak_utilization": float((self.df['is_peak_hour'].sum() / len(self.df)) * 100)
                }
                
                return JSONResponse(content={
                    "success": True,
                    "data": kpi_results
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/demand-pattern")
        async def demand_pattern():
            """Get demand pattern by hour and day"""
            try:
                if self.df is None:
                    raise HTTPException(status_code=503, detail="Data not loaded")
                
                pattern = self.df.groupby(['pickup_day_name', 'pickup_hour']).size().reset_index(name='trip_count')
                result = pattern.to_dict('records')
                
                return JSONResponse(content={
                    "success": True,
                    "data": result
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


def create_lambda_handler():
    """Create AWS Lambda handler function"""
    api = MobilityAnalyticsAPI()
    
    def handler(event, context):
        """Lambda handler"""
        from mangum import Mangum
        asgi_handler = Mangum(api.app)
        return asgi_handler(event, context)
    
    return handler


def run_local(host="0.0.0.0", port=8000):
    """Run API locally"""
    api = MobilityAnalyticsAPI()
    print(f"\nStarting API server on http://{host}:{port}")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(api.app, host=host, port=port)


def deploy_to_s3(bucket_name: str, region: str = "us-east-1"):
    """Deploy aggregated KPIs to S3 (example)"""
    if not AWS_AVAILABLE:
        print("⚠ boto3 not available. Install with: pip install boto3")
        return
    
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        # Example: Upload KPI data
        kpi_file = "outputs/kpi_report.txt"
        if os.path.exists(kpi_file):
            s3_key = f"mobility-analytics/kpi_report_{datetime.now().strftime('%Y%m%d')}.txt"
            s3_client.upload_file(kpi_file, bucket_name, s3_key)
            print(f"✓ Uploaded {kpi_file} to s3://{bucket_name}/{s3_key}")
        
    except ClientError as e:
        print(f"✗ Error uploading to S3: {e}")


def main():
    """Main execution function"""
    print("="*70)
    print("TASK 6: Cloud Deployment - Serverless Mobility Analytics API")
    print("="*70)
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        # Deployment mode
        print("\n[Deployment Mode]")
        bucket = os.getenv("S3_BUCKET_NAME", "mobility-analytics-bucket")
        region = os.getenv("AWS_REGION", "us-east-1")
        deploy_to_s3(bucket, region)
    else:
        # Run locally
        print("\n[Local Mode]")
        print("Starting API server...")
        print("Access API at: http://localhost:8000")
        print("API Docs at: http://localhost:8000/docs")
        print("\nExample endpoints:")
        print("  GET /monthly-revenue")
        print("  GET /peak-hours")
        print("  GET /top-zones?limit=10")
        print("  GET /kpis")
        print("  GET /demand-pattern")
        print("\nPress Ctrl+C to stop")
        
        run_local()


if __name__ == "__main__":
    main()





