#gps sensor data get from table
from flask import Blueprint,jsonify,request
import os
import psycopg2

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

getgpssensor_bp = Blueprint('getgpssensor_bp',__name__)

@getgpssensor_bp.route('/getgpsdata',methods=['GET'])
def getgpsdata():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
                SELECT * FROM gps_sensor_data
            """
        )
        all_gps_data = cursor.fetchall()
        messagetype = "success"
        message = f"gps data has been saved successfully"
        filelocation = "gpsdataget.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"message":"all of the gps data hasbeen fetched successfully","data":all_gps_data}),200
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "gpsdataget.py"
        generatelogs(messagetype,message,filelocation) 