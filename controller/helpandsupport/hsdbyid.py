"""
Get help and support by id
"""
from flask import Blueprint, jsonify,request
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

hsdbyid_bp = Blueprint("hsdbyid",__name__)

@hsdbyid_bp.route("/gethsbyid",methods=['POST'])
def hsdbyid():
    hsid = str(request.form.get("hsid"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM HelpandSupport WHERE id = %s
        """,(hsid,))
        result = cursor.fetchone()
        if result is None:
            return jsonify({"message":"No Help and Support found with the given id"})
        
        messagetype = "success"
        message = "Help and Support data hasbeen retrive successfully."
        filelocation = "hsbyid.py"

        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"Help and support data hasbeen fetched successfully","data":result})
        
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "hsbyid.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()