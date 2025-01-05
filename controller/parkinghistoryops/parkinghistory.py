from flask import Blueprint, request, jsonify
import psycopg2
import os
import uuid
from datetime import datetime
from util.logs import generatelogs

parkinghistory_bp = Blueprint("parkinghistory", __name__)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

@parkinghistory_bp.route("/phcreate", methods=["POST"])
def parkinghistory():
    parkingid = str(request.form.get("parkingid"))
    parkingspotid = str(request.form.get("parkingspotid"))
    timefrom = str(request.form.get("timefrom"))
    timeto = str(request.form.get("timeto"))
    userid = str(request.form.get("userid"))
    adminid = str(request.form.get("adminid"))

    # Calculate total time parked
    conn = None
    cursor = None

    try:
        # Convert string times to datetime objects, accepting ISO format
        time_from_dt = datetime.fromisoformat(timefrom)
        time_to_dt = datetime.fromisoformat(timeto)

        # Calculate total time in seconds
        total_time_seconds = (time_to_dt - time_from_dt).total_seconds()

        # Check if the total time is negative
        if total_time_seconds < 0:
            raise ValueError("The 'timeto' must be later than 'timefrom'.")

        # Convert total time to a format suitable for database storage (e.g., seconds)
        total_time = int(total_time_seconds)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO parkinghistory(id, parkingid, parkingspotid, timefrom, timeto, totaltime, userid, adminid)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)    
        """, (str(uuid.uuid4()), parkingid, parkingspotid, timefrom, timeto, total_time, userid, adminid))
        
        conn.commit()

        # Log success message
        messagetype = "success"
        message = "Parking history has been saved"
        filelocation = "parkinghistory.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message": "Parking history has been saved successfully into database"})

    except Exception as e:
        print(f"Error - {e}")
        messagetype = 'error'
        message = f"{e}"
        filelocation = 'parkinghistory.py'
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()