"""
Delete survey
"""
from flask import Blueprint,jsonify, request
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

deletesurvey_bp = Blueprint("deletesurvey",__name__)

@deletesurvey_bp.route("/deletesurvey",methods =["POST"])
def deletesurvey():
    surveyid  = str(request.form.get("survey"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM feedback WHERE id = %s
        """,(surveyid,))

        messagetype = "Success"
        message = f"feedback data hasbeen deleted successfully"
        filelocation = "surveycreate.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"Feedback data hasbeen deleted"})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "deletesurvey.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
