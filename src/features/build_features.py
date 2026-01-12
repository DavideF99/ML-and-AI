import numpy as np
import pandas as pd

def create_features(df):
    """
    Professional feature engineering for Solar Forecasting.
    We use cyclic encoding, lagging, and rolling windows.
    """
    df = df.copy()
    
    # 1. Cyclic Time Encoding
    # Solar output is a daily cycle. Hour 23 and Hour 0 are neighbors.
    hour = df['DATE_TIME'].dt.hour + df['DATE_TIME'].dt.minute / 60.0
    df['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * hour / 24)
    
    # 2. Lag Features (The 'Memory')
    # Use the 'shift' method to show the model what happened 15 mins ago.
    df['dc_power_lag_1'] = df['DC_POWER'].shift(1)
    df['irrad_lag_1'] = df['IRRADIATION'].shift(1)
    
    # 3. Rolling Statistics (The 'Trend')
    # A 1-hour rolling average (4 periods of 15 mins) of irradiation.
    df['irrad_rolling_avg_1h'] = df['IRRADIATION'].rolling(window=4).mean()
    
    # 4. SMART CLEANUP
    # Only drop NaNs if we have more than 1 row (Training mode).
    # If we have 1 row (API mode), we keep it and fill NaNs in main.py.
    if len(df) > 1:
        df = df.dropna()
    
    return df

# Cyclic Encoding: Most beginners use the hour as a number (0–23). A model thinks 0 and 23 are far apart. Using Sin/Cos maps them onto a circle where they are adjacent.

# Lag Features: In renewable energy, the "Persistence" (what happened recently) is often the strongest predictor. By adding dc_power_lag_1, we give our model the ability to "see" the baseline we just calculated.