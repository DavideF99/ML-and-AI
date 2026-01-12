from fastapi import FastAPI
import joblib
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from src.features.build_features import create_features

app = FastAPI(title="Solar Power Forecasting API")

# Load the model once when the server starts
ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "solar_model.joblib"
model = joblib.load(MODEL_PATH)

# Define the expected input data structure
class PredictionInput(BaseModel):
    DATE_TIME: str
    AMBIENT_TEMPERATURE: float
    MODULE_TEMPERATURE: float
    IRRADIATION: float
    # Note: Our model uses lags, so in a real app 
    # you'd fetch the last known DC_POWER here.
    DC_POWER: float 

@app.post("/predict")
def predict_power(data: PredictionInput):
    # 1. Convert input to DataFrame
    input_df = pd.DataFrame([data.dict()])
    input_df['DATE_TIME'] = pd.to_datetime(input_df['DATE_TIME'])
    
    # 2. Run your existing Feature Engineering
    features_df = create_features(input_df)
    
    # 3. FIX: Fill missing Lag/Rolling features for single row
    # In a real app, you'd pull historical data from a DB.
    # For now, we fill NaNs with the current values provided in the request.
    if features_df.isnull().values.any():
        # Fill lag/rolling temperatures with current temp
        features_df = features_df.fillna({
            'ambient_temperature_lag_1': data.AMBIENT_TEMPERATURE,
            'module_temperature_lag_1': data.MODULE_TEMPERATURE,
            'dc_power_lag_1': data.DC_POWER
        })
        # Fill any remaining NaNs (like rolling means) with current values
        features_df = features_df.ffill().bfill().fillna(0)

    # 4. Prepare for prediction
    cols_to_drop = ['DATE_TIME', 'DC_POWER', 'AC_POWER', 'PLANT_ID']
    X = features_df.drop(columns=[c for c in cols_to_drop if c in features_df.columns])
    
    # Ensure column order matches exactly what the model saw during training
    # (RandomForest relies on specific column order)
    prediction = model.predict(X)
    
    return {
        "prediction_kw": round(float(prediction[0]), 2),
        "input_received": data.dict()
    }