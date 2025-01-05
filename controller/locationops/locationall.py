from flask import Blueprint, request, jsonify
import psycopg2
import os
import logging

from util.logs import generatelogs

getalllocation_bp = Blueprint("getalllocation_bp",__name__)


# Database connection setup
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
        
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

@getalllocation_bp.route("/getalllocation_bp",methods=["POST"])
def getalllocation():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                SELECT * FROM location
            """)
        result = cursor.fetchall()
        messagetype = "success"
        message = "All data hasbeen fetched successfully"
        filelocation = "locationall.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message":"all data","data":result})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "locationall.py"
        generatelogs(messagetype,message,filelocation)