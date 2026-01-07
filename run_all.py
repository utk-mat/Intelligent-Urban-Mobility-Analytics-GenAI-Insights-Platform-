"""
Quick Start Script - Run all tasks sequentially
"""

import sys
import subprocess
from pathlib import Path

def run_task(task_number, task_name, script_path):
    """Run a task and handle errors"""
    print("\n" + "="*70)
    print(f"TASK {task_number}: {task_name}")
    print("="*70)
    
    if not Path(script_path).exists():
        print(f"⚠ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False
        )
        print(f"\n✓ Task {task_number} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Task {task_number} failed with error: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠ Task {task_number} interrupted by user")
        return False


def main():
    """Run all tasks in sequence"""
    print("="*70)
    print("INTELLIGENT URBAN MOBILITY ANALYTICS & GENAI INSIGHTS PLATFORM")
    print("Quick Start - Running All Tasks")
    print("="*70)
    
    tasks = [
        (1, "Data Ingestion & Cleaning", "1_data_ingestion_cleaning.py"),
        (2, "KPI Computation & Visualization", "2_kpi_computation.py"),
        (3, "SQL Analytics", "3_sql_analytics.py"),
        (4, "PySpark ETL", "4_pyspark_etl.py"),
        (5, "GenAI Assistant", "5_genai_assistant.py"),
    ]
    
    results = []
    
    for task_num, task_name, script_path in tasks:
        success = run_task(task_num, task_name, script_path)
        results.append((task_num, task_name, success))
        
        if not success:
            print(f"\n⚠ Task {task_num} failed. Continue with next task? (y/n): ", end="")
            try:
                response = input().strip().lower()
                if response != 'y':
                    print("\nStopping execution.")
                    break
            except KeyboardInterrupt:
                print("\n\nExecution stopped by user.")
                break
    
    # Summary
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70)
    for task_num, task_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"Task {task_num}: {task_name} - {status}")
    
    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Review outputs in 'outputs/' directory")
    print("2. Check visualizations in 'outputs/visualizations/'")
    print("3. Run 'python 6_cloud_api.py' to start API server")
    print("="*70)


if __name__ == "__main__":
    main()





