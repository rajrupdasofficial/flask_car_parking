"""
Get all of the parking history
"""
from flask import Blueprint, jsonify
import psycopg2
import os
from util.logs import generatelogs

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        sslmode='require'
    )

getallparkinghistory_bp = Blueprint("getallparkinghistory", __name__)

@getallparkinghistory_bp.route("/getallparkinghistory", methods=["GET"])
def getallparkinghistory():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM parkinghistory    
        """)
        
        result = cursor.fetchall()
        
        # Convert seconds to hours, minutes, and seconds
        formatted_result = []
        for row in result:
            # Assuming the total time is at index 5 (adjust if needed)
            total_time_seconds = int(row[5])  # Ensure total_time is an integer
            
            hours, remainder = divmod(total_time_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Create a new row with formatted time
            formatted_row = list(row)  # Convert tuple to list to modify it
            formatted_row[5] = f"{hours}h {minutes}m {seconds}s"  # Replace total_time with formatted string
            
            formatted_result.append(formatted_row)

        messagetype = "success"
        message = "Parking history data has been fetched"
        filelocation = "getallparkinghistory.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message": "All of the history data has been fetched", "data": formatted_result})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "getallparkinghistory.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()