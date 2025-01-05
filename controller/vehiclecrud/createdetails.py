from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import pytz
from decouple import config
import uuid
import psycopg2
import logging

from util.logs import generatelogs

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def conn():
    """Establish a connection to the PostgreSQL"""
    connection = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    return connection

create_bp = Blueprint('createvehicledetails', __name__)

@create_bp.route('/createvehicledetails', methods=['POST'])
def createdetails():

    # Extracting vehicle details from incoming data
    carname = request.form.get("carname")
    licenseplatenum = request.form.get("licenseplatenumber")
    cartype = request.form.get("cartype")
    vehiclemodel = request.form.get("vehiclemodel")
    userid = request.form.get("useruuid")

    # Basic details and validation
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM vehicle WHERE license_plate_number = %s
                """, (licenseplatenum,))
                result = cursor.fetchone()
                count = result[0] if result else 0

                if count > 0:
                    return jsonify({"error": "License plate number already exists"}), 409
    except Exception as e:
        messagetype = "error"
        message = f"{e}"
        filelocation = "createdetails.py"
        generatelogs(messagetype,message,filelocation) 
        logging.error("Error checking license plate number: %s", str(e))

        return jsonify({"error": str(e)}), 500

    # Get the current time in UTC as a timezone-aware object
    utc_time = datetime.now(timezone.utc)
    
    # Define the IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')
    
    # Convert UTC to IST
    ist_time = utc_time.astimezone(ist_timezone)
    
    # Format the date and time in ISO format
    created_at = ist_time.isoformat()  # Now in IST
    
    vehicle_data = {
        "uuid": str(uuid.uuid4()),
        "carname": carname,
        "licenseplatenumber": licenseplatenum,
        "cartype": cartype,
        "userid": userid,
        "vehiclemodel":vehiclemodel
    }

    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                # Insert vehicle data into the database
                cursor.execute("""
                    INSERT INTO vehicle (uuid, car_name, license_plate_number, car_type, user_uuid,vehiclemodel)
                    VALUES (%s, %s, %s, %s, %s,%s)
                """, (vehicle_data["uuid"], vehicle_data["carname"], vehicle_data["licenseplatenumber"], vehicle_data["cartype"], vehicle_data["userid"],vehicle_data['vehiclemodel']))
            connection.commit()
            messagetype = "success"
            message = f"Vehicle data has been saved successfully"
            filelocation = "createdetails.py"
            generatelogs(messagetype,message,filelocation)
            return jsonify({"message": "Vehicle data has been saved successfully", "data": licenseplatenum}), 201
    except Exception as e:
        logging.error("Error inserting vehicle data: %s", str(e))
        messagetype = "error"
        message = f"{e}"
        filelocation = "createdetails.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
