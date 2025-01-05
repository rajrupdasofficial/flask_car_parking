# blueprints/sensor.py
from flask import Blueprint, jsonify
import random
import psycopg2
from decouple import config
import time

ultrasonicsensor = Blueprint('ultrasonicsensor', __name__)

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

@ultrasonicsensor.route('/ultrasonicsensor', methods=['GET'])
def simulate_ultrasonic_sensor():
    # Simulate distance measurement in centimeters (0 to 400 cm)
    distance = random.randint(0, 400)  # Random distance between 0 and 400 cm
    
    # Determine car presence based on distance categories
    if distance < 50:
        car_present = True
        status_message = "Very close: Car is definitely present."
    elif distance < 150:
        car_present = random.random() < 0.8  # 80% chance for close range
        status_message = "Close: High chance a car is present."
    elif distance < 300:
        car_present = random.random() < 0.4  # 40% chance for mid range
        status_message = "Far: Possible car presence."
    else:
        car_present = random.random() < 0.1  # 10% chance for far range
        status_message = "Very far: Unlikely a car is present."

    # Simulate environmental factors
    weather_condition = random.choice(['clear', 'rain', 'fog'])
    if weather_condition == 'fog':
        accuracy_factor = random.uniform(0.5, 1.0)  # Reduced accuracy
        distance *= accuracy_factor
        status_message += " Sensor accuracy reduced due to fog."
    
    # Simulate sensor readings
    battery_level = random.randint(0, 100)          # Battery level percentage
    temperature = random.uniform(-10.0, 50.0)       # Temperature in Celsius
    humidity = random.uniform(20.0, 90.0)            # Humidity percentage
    signal_strength = random.uniform(0.0, 100.0)     # Signal strength percentage
    echo_time = round(random.uniform(0.01, 0.1), 3) # Echo time in seconds (random float)
    calibration_status = random.choice(['calibrated', 'not calibrated']) # Calibration status
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')   # Current timestamp

    # Simulate possible sensor malfunction
    if random.random() < 0.05:  # 5% chance of malfunction
        distance = None           # Set to None for malfunction case
        car_present = None
        status_message = "Sensor malfunction detected."

    # Store data in the database
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Directly format the SQL query with actual values for debugging.
        insert_query = f"""
            INSERT INTO sensors (name, type, location, status, manufacturer, model,
                                 installation_date, last_maintenance_date,
                                 notes, distance_measurement, echo_time,
                                 object_detected, battery_level, temperature,
                                 humidity, signal_strength, timestamp,
                                 calibration_status,firmware_version)
            VALUES (
                'Ultrasonic Sensor',
                'Ultrasonic',
                'Location A',
                'Active',
                'Manufacturer X',
                'Model Y',
                '2024-01-01',
                NULL,
                'Simulated data entry',
                '{str(distance) if distance is not None else ''}',
                '{echo_time}',
                '{str(car_present) if car_present is not None else ''}',
                '{str(battery_level)}',
                '{str(temperature)}',
                '{str(humidity)}',
                '{str(signal_strength)}',
                '{timestamp}',
                '{calibration_status}',
                'V2.5'
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
        'distance': distance,
        'car_present': car_present,
        'status': status_message,
        'weather_condition': weather_condition,
        'battery_level': battery_level,
        'temperature': temperature,
        'humidity': humidity,
        'signal_strength': signal_strength,
        'echo_time': echo_time,
        'calibration_status': calibration_status,
        'timestamp': timestamp,
    })