"""
Survey list
"""
from flask import Blueprint, jsonify, request
import psycopg2
import os
from util.logs import generatelogs

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

getallsurvey_bp = Blueprint("getallsurvey",__name__)

@getallsurvey_bp.route("/getallsurvey",methods=["POST"])
def getallsurvey():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM feedback
        """)
        result = cursor.fetchall()
        messagetype = "Success"
        message = f"List of feedbacks"
        filelocation = "surveycreate.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message":"List of all data hasbeen fetched successfully","data":result})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "surveylist.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
