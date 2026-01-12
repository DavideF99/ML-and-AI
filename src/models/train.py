import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import mlflow

def train_model(df):
    """
    Trains a model and logs parameters/metrics to MLflow.
    """
    # 1. Prepare Features and Target
    # We define what we DON'T want as features. 
    # We include the _x and _y variants created during the merge.
    cols_to_drop = [
        'DATE_TIME', 'PLANT_ID', 'DC_POWER', 'AC_POWER', 
        'SOURCE_KEY_x', 'SOURCE_KEY_y', 'DAILY_YIELD', 'TOTAL_YIELD'
    ]
    
    # Filter only the columns that actually exist in the dataframe to avoid KeyErrors
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    
    X = df.drop(columns=existing_drops)
    y = df['DC_POWER']

    # 2. Temporal Split (No Shuffling!)
    split_index = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # 3. Start MLflow Experiment
    with mlflow.start_run():
        # Define Hyperparameters
        params = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
        
        # Initialize and Train
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)

        # Predict and Evaluate
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))

        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "random_forest_model")

        print(f"✅ Training Complete. MAE: {mae:.2f} kW")
        return model, mae