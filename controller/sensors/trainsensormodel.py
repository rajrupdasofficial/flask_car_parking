from flask import Blueprint, jsonify
import psycopg2
from decouple import config
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# Create a Blueprint for the sensor functionality
trainsensormodel_bp = Blueprint('trainsensormodel_bp', __name__)

def get_db_connection():
    """Establish a database connection."""
    try:
        return psycopg2.connect(
            dbname=config('DB_NAME'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            host=config('DB_HOST'),
            port=config('DB_PORT'),
            sslmode='require'
        )
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

@trainsensormodel_bp.route('/trainsensormodel', methods=['GET'])
def filter_out_sensor():
    conn = None
    cursor = None

    model_path = 'vehicle_presence_model.pkl'
    
    if not os.path.exists(model_path):
        print("Model file not found. Training a new model...")
        model = train_model()
        
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model training failed; no model file created.'}), 500
    else:
        print("Retraining and loading existing model...")
        train_model()  # Retrain the model before loading it
        model = joblib.load(model_path)

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to the database.'}), 500
        
        cursor = conn.cursor()

        query = """
            SELECT object_detected, distance_measurement, signal_strength, type 
            FROM sensors 
            WHERE location = 'Location A'  
            ORDER BY RANDOM()  
            LIMIT 180000;
        """
        
        cursor.execute(query)
        sensor_data = cursor.fetchall()

        cleaned_data = clean_data(sensor_data)
        
        if not cleaned_data:
            return jsonify({'error': 'No valid sensor data available for prediction.'}), 404

        # Placeholder response
        return jsonify({'message': 'Sensor data processed successfully.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def clean_data(data):
    """Clean the input data by converting strings to integers and handling errors."""
    cleaned_data = []
    
    for record in data:
        try:
            object_detected = 1 if record[0].lower() == 'true' else 0 if record[0].lower() == 'false' else None
            
            distance_measurement = float(record[1]) if record[1] else None
            signal_strength = float(record[2]) if record[2] else None
            type_value = record[3]
            
            if object_detected is not None and distance_measurement is not None and signal_strength is not None:
                cleaned_record = [object_detected, distance_measurement, signal_strength, type_value]
                cleaned_data.append(cleaned_record)
        except ValueError as ve:
            print(f"ValueError encountered: {ve} - Record: {record}")
    
    return cleaned_data

def train_model():
    """Train the vehicle presence prediction model using historical data from PostgreSQL."""
    conn = None
    cursor = None
    distance_threshold = 50.0  

    try:
        conn = get_db_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor()

        query = """
            SELECT object_detected, distance_measurement, signal_strength, type 
            FROM sensors
            WHERE location = 'Location A'  
            ORDER BY RANDOM()  
            LIMIT 180000;
        """
        
        cursor.execute(query)
        data = cursor.fetchall()

        cleaned_data = clean_data(data)

        if not cleaned_data:
            print("No valid data available for training.")
            return None

        df = pd.DataFrame(cleaned_data, columns=['object_detected', 'distance_measurement', 'signal_strength', 'type'])
        
        df.dropna(inplace=True)

        # Update object_detected logic based on historical context
        df['object_detected'] = df['distance_measurement'].apply(lambda x: 1 if x < distance_threshold else 0)

        # One-hot encode categorical variables
        df = pd.get_dummies(df, columns=['type'], drop_first=True)

        X = df.drop('object_detected', axis=1)
        y = df['object_detected']

        # Handle class imbalance by using stratified sampling in train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=55, stratify=y)

        # Hyperparameter tuning with GridSearchCV
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5],
            'class_weight': ['balanced', None]  # Consider both options for class weight
        }

        grid_search = GridSearchCV(RandomForestClassifier(random_state=55), param_grid, cv=5)
        
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_

        predictions = best_model.predict(X_test)
        
        accuracy = accuracy_score(y_test, predictions)
        
        print(f'Model Accuracy: {accuracy * 100:.2f}%')
        
        # Print classification report and confusion matrix
        print("Classification Report:\n", classification_report(y_test, predictions))
        
        cm = confusion_matrix(y_test, predictions)
        print("Confusion Matrix:\n", cm)

         # Cross-validation scores for better evaluation of model performance
        cv_scores = cross_val_score(best_model, X, y, cv=5)
        print(f'Cross-Validation Scores: {cv_scores}')
        print(f'Mean CV Score: {cv_scores.mean()}')

        joblib.dump(best_model, 'vehicle_presence_model.pkl')
        
    except Exception as e:
         print(f"Error during model training: {str(e)}")
    
    finally:
         if cursor:
             cursor.close()
         if conn:
             conn.close()