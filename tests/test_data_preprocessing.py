import pytest
import pandas as pd
from src.data_preprocessing import load_and_merge_data

def test_load_and_merge_data_integrity():
    """
    Test that the merging process preserves data integrity.
    """
    gen_file = "Plant_1_Generation_Data.csv"
    weather_file = "Plant_1_Weather_Sensor_Data.csv"
    
    df = load_and_merge_data(gen_file, weather_file)
    
    # Test 1: Check if dataframe is not empty
    assert not df.empty, "Merged dataframe is empty!"
    
    # Test 2: Verify specific columns exist after merge
    required_columns = ['DC_POWER', 'IRRADIATION', 'DATE_TIME', 'AMBIENT_TEMPERATURE']
    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"
        
    # Test 3: Check for data loss
    # Solar data usually has ~3150 timestamps. 
    # If we have significantly fewer rows, the merge is failing.
    # Plant 1 has roughly 68,000 rows across multiple inverters (Source Keys)
    assert len(df) > 40000, f"Significant data loss detected. Row count: {len(df)}"

    # Test 4: Check that timestamps are actually datetime objects
    assert pd.api.types.is_datetime64_any_dtype(df['DATE_TIME']), "DATE_TIME is not datetime type"

    print("\n✅ Data Ingestion Tests Passed!")