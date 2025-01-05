"""
GPS sensors
"""
from flask import Blueprint, jsonify,request
import os
import psycopg2
from uuid import uuid4

from util.logs import generatelogs

def get_db_conn():
    """Establish a database connection."""
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )

gpssensor_bp = Blueprint('gpssensor_bp',__name__)

@gpssensor_bp.route("/getsensor",methods=['POST'])
def gpssensor():
    latitude  = str(request.form.get("latitude"))
    longitude  = str(request.form.get("longitude"))
    accuracy = str(request.form.get("accuracy"))
    altitude = str(request.form.get("altitude"))
    speed = str(request.form.get("speed"))
    heading = str(request.form.get("heading"))
    provider = str(request.form.get("provider"))
    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute(
        """
            INSERT INTO gps_sensor_data (id,latitude,longitude,accuracy,altitude,speed,heading,provider)
        """,(str(uuid4()),latitude,longitude,accuracy,altitude,speed,heading,provider))
        conn.commit()
        messagetype = "success"
        message = f"gps data has been saved successfully"
        filelocation = "gpssensorops.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"message":"gps data hasbeen saved successfully"}),201
    except Exception as e:
        print(f"{e}")
        messagetype = "error"
        message = f"{e}"
        filelocation = "gpssensorops.py"
        generatelogs(messagetype,message,filelocation) 
    finally:
        cursor.close()
        conn.close()
