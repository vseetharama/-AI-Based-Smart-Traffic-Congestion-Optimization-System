# Phase 1 Prediction Module

This folder contains a modular LSTM-based traffic prediction pipeline for Version 2.

## What it does
- Loads historical traffic data from the existing MongoDB collection `traffic_logs`
- Prepares features for LSTM training
- Trains a simple regression model for future vehicle count prediction
- Saves the model and scaler for reuse
- Provides a prediction service that can be integrated later into the backend workflow

## Required package versions
- Python: 3.12.x
- numpy: 1.26.4
- pandas: 2.2.3
- scikit-learn: 1.3.2
- tensorflow: 2.16.2
- pymongo: 4.17.0
- python-dotenv: 1.2.2

## Training instructions
1. Activate the project virtual environment.
2. Install the required packages if missing.
3. Ensure the MongoDB connection settings are available in the backend environment.
4. Run the training entry point from the backend folder:
   `python -m prediction.train`

## How to retrain the model
- Re-run the training command above after new traffic data is logged.
- The model and scaler are saved in the backend/models directory.
- The current training workflow writes the files `traffic_predictor.keras` and `scaler.pkl`.

## How predictions work
- The pipeline loads recent traffic history from the existing MongoDB `traffic_logs` collection.
- Features such as vehicle count, waiting time, recommended green time, density, hour, and weekday are prepared.
- A sliding window of recent values is fed into the LSTM model.
- The model predicts the next vehicle count and returns it as a structured result.

## Troubleshooting
- If pandas raises a DLL import error, reinstall a compatible pandas build for the active Python version.
- If TensorFlow is missing, install the CPU build that matches your Python version.
- If the model cannot be loaded, make sure the `.keras` and `.pkl` files exist in `backend/models`.
- If MongoDB access fails, verify that the backend `.env` file contains a valid `MONGODB_URI` and `DATABASE_NAME`.

## Important note
This is implemented incrementally and does not modify the current upload, YOLO,
dashboard, analytics, or controller logic.
