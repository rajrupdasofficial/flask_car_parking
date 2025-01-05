"""
Get all of the spots data using this route
this route apis will be used in admin dashboard section
"""
from flask import Blueprint, jsonify,request
import psycopg2
import logging
from decouple import config

from util.logs import generatelogs

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

getallspots = Blueprint("/getallspots",methods=['GET'])
def getallspots():
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * from parking_spot
                """)
                parking_spots = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                parking_data = [dict(zip(columns, parking_spot)) for parking_spot in parking_spots]
                messagetype = "success"
                message = "all of the available data"
                filelocation = "getallspots.py"
                generatelogs(messagetype,message,filelocation)
                return jsonify(parking_data),200
    except Exception as e:
        logging.error("Error retrieving all spot data: %s", str(e))
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "getallspots.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    
    finally:
        cursor.close()