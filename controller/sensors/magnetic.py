# blueprints/sensor.py

from flask import Blueprint, jsonify
import random
import psycopg2
from decouple import config
import time

magnetic_sensor_bp = Blueprint('magnetic_sensor_bp', __name__)

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

@magnetic_sensor_bp.route('/magnetic', methods=['GET'])
def simulate_magnetic_sensor():
    # Simulate distance measurement in meters (0.1 to 10.0 meters)
    distance_measurement = random.uniform(0.1, 10.0)  # Random distance between 0.1 and 10.0 meters
    echo_time = random.uniform(0.01, 0.1)  # Simulated echo time in seconds
    object_detected = random.choice([True, False])  # Randomly detect an object
    
    # Simulate additional readings
    battery_level = random.randint(0, 100)  # Battery level percentage
    temperature = random.uniform(-10.0, 50.0)  # Temperature in Celsius
    humidity = random.uniform(20.0, 90.0)  # Humidity percentage
    signal_strength = random.uniform(0.0, 100.0)  # Signal strength percentage
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp
    calibration_status = random.choice(['calibrated', 'not calibrated'])  # Calibration status
    firmware_version = 'v1.0'  # Firmware version

    # Store data in the database
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Directly format the SQL query with actual values for debugging
        insert_query = f"""
            INSERT INTO sensors (
                name, type, location, status, manufacturer, model,
                installation_date, last_maintenance_date,
                notes, distance_measurement, echo_time,
                object_detected, battery_level, temperature,
                humidity, signal_strength, timestamp,
                calibration_status, firmware_version)
            VALUES (
                '{'Magnetic Sensor'}', 
                '{'Magnetic'}', 
                '{'Location A'}', 
                '{'Active'}', 
                '{'SensorCorp'}', 
                '{'Model SC-2023'}', 
                '{time.strftime('%Y-%m-%d')}', 
                '', 
                'Simulated data entry', 
                '{distance_measurement}', 
                '{echo_time}', 
                '{str(object_detected).lower()}', 
                '{battery_level}', 
                '{temperature}', 
                '{humidity}', 
                '{signal_strength}', 
                '{timestamp}', 
                '{calibration_status}', 
                '{firmware_version}'
            )
        """

        print(f"Executing query: {insert_query}")  # Debugging line
        
        cursor.execute(insert_query)

        conn.commit()
        
    except Exception as e:
        print(f"Error inserting data into database: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return jsonify({
        'distance_measurement': str(distance_measurement),
        'echo_time': str(echo_time),
        'object_detected': str(object_detected),
        'battery_level': str(battery_level),
        'temperature': str(temperature),
        'humidity': str(humidity),
        'signal_strength': str(signal_strength),
        'timestamp': timestamp,
        'calibration_status': calibration_status,
        'firmware_version': firmware_version
    })