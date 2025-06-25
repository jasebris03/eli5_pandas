#!/usr/bin/env python3
"""Script to create sample Excel and Parquet files from the CSV data."""

import pandas as pd
from pathlib import Path

def create_sample_files():
    """Create Excel and Parquet sample files from the CSV data."""
    
    # Read the CSV file
    csv_path = Path("sample_data/sample_data.csv")
    if not csv_path.exists():
        print("Error: sample_data.csv not found!")
        return
    
    print("Reading CSV file...")
    df = pd.read_csv(csv_path)
    
    # Convert hire_date to datetime
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    
    # Create Excel file
    print("Creating Excel file...")
    excel_path = Path("sample_data/sample_data.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"✅ Excel file created: {excel_path}")
    
    # Create Parquet file
    print("Creating Parquet file...")
    parquet_path = Path("sample_data/sample_data.parquet")
    df.to_parquet(parquet_path, index=False)
    print(f"✅ Parquet file created: {parquet_path}")
    
    # Create a file with some missing values for testing
    print("Creating file with missing values...")
    df_with_missing = df.copy()
    
    # Add some missing values
    df_with_missing.loc[5, 'salary'] = None
    df_with_missing.loc[10, 'age'] = None
    df_with_missing.loc[15, 'department'] = None
    df_with_missing.loc[20, 'hire_date'] = None
    df_with_missing.loc[25, 'rating'] = None
    df_with_missing.loc[30, 'email'] = None
    df_with_missing.loc[35, 'city'] = None
    df_with_missing.loc[40, 'is_active'] = None
    df_with_missing.loc[45, 'name'] = None
    
    # Save as CSV with missing values
    missing_csv_path = Path("sample_data/sample_data_with_missing.csv")
    df_with_missing.to_csv(missing_csv_path, index=False)
    print(f"✅ CSV with missing values created: {missing_csv_path}")
    
    # Save as JSON with missing values
    missing_json_path = Path("sample_data/sample_data_with_missing.json")
    df_with_missing.to_json(missing_json_path, orient='records', indent=2, date_format='iso')
    print(f"✅ JSON with missing values created: {missing_json_path}")
    
    print("\n🎉 All sample files created successfully!")
    print("\nFiles created:")
    print("  📄 sample_data/sample_data.xlsx")
    print("  📄 sample_data/sample_data.parquet")
    print("  📄 sample_data/sample_data_with_missing.csv")
    print("  📄 sample_data/sample_data_with_missing.json")

if __name__ == "__main__":
    create_sample_files() 