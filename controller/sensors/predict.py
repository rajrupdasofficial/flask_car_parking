from flask import Blueprint, jsonify
import psycopg2
from decouple import config
import joblib
import pandas as pd
import math
from time import time

# Create a Blueprint for the prediction functionality
predict_bp = Blueprint('predict_bp', __name__)

def get_db_connection():
    """Establish a database connection."""
    return psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )

def fetch_all_sensor_data(parking_lot, limit=3000):
    """Fetch sensor data for a specific parking lot, ordered randomly and limited by the provided limit."""
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query for random 3000 records (or a smaller subset)
        query = """
            SELECT object_detected, distance_measurement, signal_strength, type 
            FROM sensors
            WHERE location = %s  
            ORDER BY RANDOM()  -- Randomize the order of records
            LIMIT %s;  -- Limit to the number of records specified
        """
        
        cursor.execute(query, (parking_lot, limit))
        sensor_data = cursor.fetchall()  # Fetch the records

        return sensor_data

    except Exception as e:
        print(f"Error fetching sensor data: {str(e)}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@predict_bp.route('/predict', methods=['GET'])
def predict():
    """Endpoint to make predictions based on all sensor data from a specified parking lot."""
    parking_lot = "Location A"  # Can be dynamically passed as a query parameter if needed
    batch_size = 100  # Process data in batches of 100 to improve performance

    # Fetch sensor data from the database
    sensor_data = fetch_all_sensor_data(parking_lot, limit=3000)

    if not sensor_data:
        return jsonify({'error': 'No sensor data available for this parking lot.'}), 404

    try:
        # Load the trained model (ensure this path is correct)
        model_path = 'vehicle_presence_model.pkl'
        model = joblib.load(model_path)

        # Prepare features for prediction
        predictions = []
        
        # Retrieve the feature names expected by the model
        model_columns = model.feature_names_in_.tolist()

        # Batch processing
        total_records = len(sensor_data)
        batches = math.ceil(total_records / batch_size)  # Calculate the number of batches
        print(f"Processing {total_records} records in {batches} batches...")

        start_time = time()  # Track total processing time
        
        # Process in batches
        for batch_num in range(batches):
            # Determine the slice of data for this batch
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_records)
            batch_data = sensor_data[start_idx:end_idx]
            
            # Prepare input data for predictions
            input_batch = pd.DataFrame(batch_data, columns=['object_detected', 'distance_measurement', 'signal_strength', 'type'])
            input_batch['distance_measurement'] = input_batch['distance_measurement'].apply(lambda x: float(x) if x else 0.0)
            input_batch['signal_strength'] = input_batch['signal_strength'].apply(lambda x: float(x) if x else 0.0)

            # Convert categorical 'type' into dummy/indicator variables (same as during training)
            input_batch = pd.get_dummies(input_batch, columns=['type'], drop_first=True)

            # Ensure that the input features match exactly what the model expects
            missing_cols = set(model_columns) - set(input_batch.columns)
            for col in missing_cols:
                input_batch[col] = 0  # Add missing columns with zero values

            # Reorder columns to match the model
            input_batch = input_batch[model_columns]

            # Make predictions for the batch
            predictions_batch = model.predict(input_batch)
            
            # Append the predictions
            for i, record in enumerate(batch_data):
                presence_status = 'Vehicle Present' if predictions_batch[i] == 1 else 'No Vehicle'
                predictions.append({
                    'distance_measurement': record[1],
                    'signal_strength': record[2],
                    'type': record[3],
                    'presence_status': presence_status,
                })

        end_time = time()  # End tracking
        print(f"Total time taken for prediction: {end_time - start_time:.2f} seconds")

        # Return the predictions as a JSON response
        return jsonify(predictions)

    except Exception as e:
        print(f"Error during prediction: {str(e)}")  # Improved error logging
        return jsonify({'error': str(e)}), 500