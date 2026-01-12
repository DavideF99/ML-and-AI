import pandas as pd
from pathlib import Path

# 1. Define the BASE_DIR relative to THIS file (src/data_preprocessing.py)
# .parent goes to src, .parent again goes to renewable-energy-forecast/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def load_and_merge_data(gen_filename, weather_filename):
    """
    Loads data using paths relative to the project root.
    """
    # Construct absolute paths based on the project root
    gen_path = BASE_DIR / "data" / "raw" / gen_filename
    weather_path = BASE_DIR / "data" / "raw" / weather_filename

    # Validation: Check if files actually exist before reading
    if not gen_path.exists():
        raise FileNotFoundError(f"Could not find: {gen_path}")

    # 1. Load data
    gen_df = pd.read_csv(gen_path)
    weather_df = pd.read_csv(weather_path)

    # 2. Convert DATE_TIME to datetime objects
    gen_df['DATE_TIME'] = pd.to_datetime(gen_df['DATE_TIME'], dayfirst=False)
    weather_df['DATE_TIME'] = pd.to_datetime(weather_df['DATE_TIME'], dayfirst=False)

    # 3. Merge on DATE_TIME
    df = pd.merge(gen_df, weather_df, on='DATE_TIME', how='inner')
    
    # 4. Clean up redundant columns
    if 'PLANT_ID_y' in df.columns:
        df = df.drop(columns=['PLANT_ID_y']).rename(columns={'PLANT_ID_x': 'PLANT_ID'})
        
    return df

# Now call it using just the filenames
if __name__ == "__main__":
    merged_data = load_and_merge_data("Plant_1_Generation_Data.csv", "Plant_1_Weather_Sensor_Data.csv")
    print(merged_data.head())