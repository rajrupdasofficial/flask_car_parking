# get details 
from flask import Blueprint, jsonify, request
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

allvehicle_bp = Blueprint("allvehicles",__name__)

@allvehicle_bp.route("/users/allvehicles",methods=["GET"])
def getallvehicles():
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM vehicle
                """)
            allvehicles = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            getdata = [dict(zip(columns,allvehicle)) for allvehicle in allvehicles]
            messagetype = "success"
            message = f"all data hasbeen fetched"
            filelocation = "getdetails.py"
            generatelogs(messagetype,message,filelocation) 
            return jsonify({"data":getdata}),200

    except Exception as e:
        logging.error("Error retrieving all user data: %s", str(e))
        messagetype = "error"
        message = f"{e}"
        filelocation = "getdetails.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()