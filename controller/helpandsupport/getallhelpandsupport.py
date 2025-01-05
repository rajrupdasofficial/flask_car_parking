from flask import Blueprint,jsonify
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

getallhelp_bp = Blueprint("getallhelp",__name__)

@getallhelp_bp.route("/getallhelp", methods=['GET'])
def getallhelp():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM HelpandSupport
        """)
        
        result = cursor.fetchall()
        
        messagetype = "success"
        message = "Get all help and support"
        filelocation = "getallhelpandsupport.py"
        
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"All help and support hasbeen fetched successfully","data":result})
        
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "createhelpandsupport.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500 
    
    finally:
        cursor.close()
        conn.close()       