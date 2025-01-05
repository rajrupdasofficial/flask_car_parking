"""
create a parking spot location and save necessary details.
"""
from flask import Blueprint, request, jsonify
import psycopg2
import os
from uuid import uuid4
from util.logs import generatelogs

createspot_bp = Blueprint('createspot', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

# Function to generate a custom random UID
def generate_custom_random_uid():
    return str(uuid4())

@createspot_bp.route("/createspot", methods=['POST'])
def create_spot():
    # Retrieve form data and check for missing fields
    required_fields = [
        "parking_spot_name", "parking_spot_location", "length", "width",
        "total_spots", "free_spots", "occupied_spots", "latitude",
        "longitude", "address", "userid", "number_of_floors",
        "entry_gate_count", "exit_gate_count","locationid"
    ]
    
    form_data = {field: request.form.get(field) for field in required_fields}
    
    # Check for missing fields
    for field, value in form_data.items():
        if value is None:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Convert all values to string (if necessary)
    parking_spot_name = str(form_data["parking_spot_name"])
    parking_spot_location = str(form_data["parking_spot_location"])
    length = str(form_data["length"])
    width = str(form_data["width"])
    total_spots = str(form_data["total_spots"])
    free_spots = str(form_data["free_spots"])
    occupied_spots = str(form_data["occupied_spots"])
    latitude = str(form_data["latitude"])
    longitude = str(form_data["longitude"])
    address = str(form_data["address"])
    userid = str(form_data["userid"])
    number_of_floors = str(form_data["number_of_floors"])
    entry_gate_count = str(form_data['entry_gate_count'])
    exit_gate_count = str(form_data['exit_gate_count'])
    locationid = str(form_data['locationid'])
    
    associatedadminid = 'yyyy'  # Ensure this is correct based on your logic

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        new_uid = generate_custom_random_uid()
        
        cursor.execute("""
            INSERT INTO parking_spot (id, parking_spot_name, parking_spot_location, length,
                                       width, total_spots, free_spots, occupied_spots,
                                       latitude, longitude, address, userid,
                                       associatedadminid, number_of_floors,
                                       entry_gate_count, exit_gate_count, locationid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s)
        """, (new_uid, parking_spot_name, parking_spot_location,
              length, width, total_spots,
              free_spots, occupied_spots,
              latitude, longitude,
              address, userid,
              associatedadminid,
              number_of_floors,
              entry_gate_count,
              exit_gate_count, locationid))
        
        conn.commit()

        messagetype = "success"
        message = "New parking spot data has been inserted successfully"
        filelocation = "createspot.py"
        
        generatelogs(messagetype,message,filelocation)
        
        return jsonify({"message": "Parking spot has been created successfully"})

    except Exception as e:
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "createspot.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()