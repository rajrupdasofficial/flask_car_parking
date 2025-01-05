from flask import Blueprint, jsonify, request
import random
import psycopg2
from decouple import config
import time

infratest_bp = Blueprint('infratest', __name__)

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

class InfraredSensor:
    """A class representing an infrared sensor."""
    
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id

    def read_sensor(self):
        """Simulate reading from the infrared sensor."""
        return random.uniform(20.0, 100.0)

    def is_object_detected(self):
        """Simulate object detection based on random chance."""
        return random.random() < 0.3

class SensorTestSimulator:
    """A class to simulate testing of the infrared sensor."""
    
    def __init__(self, sensor):
        self.sensor = sensor

    def run_tests(self, num_tests=10):
        """Run multiple tests on the infrared sensor."""
        results = []
        
        for _ in range(num_tests):
            reading = self.sensor.read_sensor()
            object_detected = self.sensor.is_object_detected()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            results.append({
                'timestamp': timestamp,
                'sensor_id': self.sensor.sensor_id,
                'reading': reading,
                'object_detected': object_detected
            })
            
        return results

@infratest_bp.route('/infratest', methods=['POST'])
def test_sensor():
    """API endpoint to test the infrared sensor."""
    data = request.get_json()
    
    # Get number of tests from request or use default
    num_tests = data.get('num_tests', 5)
    
    # Initialize the sensor and simulator
    sensor = InfraredSensor(sensor_id="IR-001")
    simulator = SensorTestSimulator(sensor)
    
    # Run tests and get results
    test_results = simulator.run_tests(num_tests=num_tests)

    # Store data in the database
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare to insert data directly into SQL query
        batch_size = 100  # Define the batch size
        insert_data = []  # List to hold values for batch insertion
        
        for result in test_results:
            insert_data.append((
                'IR Sensor',               # name
                'Infrared',               # type
                'Location A',             # location
                'Active',                 # status
                'Manufacturer X',         # manufacturer
                'Model Y',                # model
                time.strftime("%Y-%m-%d"),  # installation_date (today's date)
                None,                     # last_maintenance_date (optional)
                'Test note',              # notes
                result['reading'],        # distance_measurement (simulated reading)
                None,                     # echo_time (optional)
                result['object_detected'],# object_detected (boolean)
                random.randint(0, 100),   # battery_level (random percentage)
                round(random.uniform(-10.0, 50.0), 2),  # temperature (random float)
                round(random.uniform(20.0, 90.0), 2),   # humidity (random float)
                round(random.uniform(0.0, 100.0), 2),   # signal_strength (random float)
                result['timestamp'],      # timestamp from results
                random.choice(["calibrated", "not calibrated"])  # calibration_status (random choice)
            ))

            # If we reach the batch size, execute the insert query
            if len(insert_data) >= batch_size:
                insert_query = """
                    INSERT INTO sensors (name, type, location, status, manufacturer, model,
                                         installation_date, last_maintenance_date,
                                         notes, distance_measurement, echo_time,
                                         object_detected, battery_level, temperature,
                                         humidity, signal_strength, timestamp,
                                         calibration_status)
                    VALUES %s
                """
                
                execute_values(cursor, insert_query, insert_data)  # Use psycopg2.extras.execute_values for batch insert
                insert_data.clear()  # Clear the list for the next batch
        
        # Insert any remaining records that didn't fill a complete batch
        if insert_data:
            insert_query = """
                INSERT INTO sensors (name, type, location, status, manufacturer, model,
                                     installation_date, last_maintenance_date,
                                     notes, distance_measurement, echo_time,
                                     object_detected, battery_level, temperature,
                                     humidity, signal_strength, timestamp,
                                     calibration_status)
                VALUES %s
            """
            execute_values(cursor, insert_query, insert_data)

        conn.commit()  # Commit changes to the database
        
    except Exception as e:
        print(f'error',str(e))
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return jsonify(test_results), 200

from psycopg2.extras import execute_values
