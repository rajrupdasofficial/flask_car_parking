from flask import Blueprint, jsonify
from decouple import config
import psycopg2
from psycopg2.extras import RealDictCursor

allsensors_bp = Blueprint('allsensors', __name__)

def conn():
    """Establish a database connection."""
    return psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )

@allsensors_bp.route('/allsensors', methods=['GET'])
def allsensorsdata():
    try:
        with conn() as connection:
            with connection.cursor(name='server_cursor', cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM sensors;")
                
                sensors_data = []
                batch_size = 5000  # Increase batch size
                
                while True:
                    batch = cursor.fetchmany(batch_size)
                    if not batch:
                        break
                    sensors_data.extend(batch)

                return jsonify(sensors_data), 200
                
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()