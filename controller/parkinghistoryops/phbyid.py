"""
Get parking history details by id 
"""

from flask import Blueprint, jsonify, request
import psycopg2
import os
from util.logs import generatelogs
import jwt

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        sslmode='require'
    )

phbyid_bp = Blueprint("phbyid", __name__)

@phbyid_bp.route("/phbyid", methods=["POST"])
def phbyid():
    conn = None
    cursor = None
    phid = str(request.form.get("parkinghid"))
    print(phid)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM parkinghistory WHERE id = %s
        """, (phid,))

        result = cursor.fetchone()

        # Check if result is None and handle it
        if result is None:
            return jsonify({"message": "No data found with the given id"}), 404

        # Assuming the total time is at index 5 (adjust if needed)
        total_time_seconds = int(result[5])  # Ensure total_time is an integer
        
        # Convert seconds to hours, minutes, and seconds
        hours, remainder = divmod(total_time_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Create a formatted time string
        formatted_time = f"{hours}h {minutes}m {seconds}s"

        # Create a response with formatted time
        response_data = {
            "id": result[0],  # Adjust based on your actual table structure
            "parkingid": result[1],
            "parkingspotid": result[2],
            "timefrom": result[3],
            "timeto": result[4],
            "totaltime": formatted_time,  # Replace total_time with formatted string
            "userid": result[6],
            "adminid": result[7]
            # Add more fields as necessary based on your table structure
        }

        token = jwt.encode(response_data,os.getenv("JWT_SECRET"),algorithm='HS256')

        messagetype = "success"
        message = "Parking history has been retrieved successfully"
        filelocation = "phbyid.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message": "Parking history has been retrieved successfully", "data": response_data,"token":token})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "phbyid.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()