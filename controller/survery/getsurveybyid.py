"""
Get survey by id
"""
from flask import Blueprint,jsonify,request
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
getsurveybyid_bp = Blueprint("getsurveybyid",__name__)

@getsurveybyid_bp.route("/getsurveybyid",methods=["POST"])
def getsurveybyid():
    surveyid = str(request.form.get("surveyid"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM feedback WHERE id = %s
            """,(surveyid,))
        result = cursor.fetchone()
        messagetype = "Success"
        message = f"Feedback data hasbeen fetched successfully"
        filelocation = "getsurveybyid.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"Survey result fetched successfully","data":result})

         
        
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "getsurveybyid.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        conn.close()