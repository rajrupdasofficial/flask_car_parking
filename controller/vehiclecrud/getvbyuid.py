"""
Get vehicle by user id 
"""
from flask import Blueprint,jsonify,request
import os
import psycopg2

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

getvbyid_bp = Blueprint("getbyid",__name__)

@getvbyid_bp.route("/getvbyid",methods=["POST"])
def getvbyid():
    userid = str(request.form.get("userid"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM vehicle WHERE  user_uuid = %s
        """,(userid,))

        result = cursor.fetchone()
           
        messagetype = "success"
        message = "Vehicle data hasbeen fetched by id"
        filelocation = "getvbyid.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"vehicle data hasbeen fetched successfully","data":result})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "Userspecifichs.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
