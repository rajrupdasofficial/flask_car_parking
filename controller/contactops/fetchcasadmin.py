"""
Fetch contacts as admin
"""
from flask import Blueprint, jsonify, request
import psycopg2
import os
from util.logs import generatelogs


def get_db_conn():
    """Establish a connection to the PostgreSQL"""
    connection = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
    return connection

fetchcasadmin_bp = Blueprint("fetchcasadmin",__name__)

@fetchcasadmin_bp.route("/fetchcasadmin_bp",methods=["POST"])
def fetchcasadmin():
    adminid = str(request.form.get('adminid'))

    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM contact WHERE adminid = %s
        """,(adminid,))

        result = cursor.fetchall()
        if result is None:
            return jsonify({"error":"The data requested for is not found"})
        
        stored_id,firstname,lastname,email,messages = result

        normal_payload = {
            "uid":stored_id,
            "firstname":firstname,
            "lastname":lastname,
            "email":email,
            "messages":messages
        }

        messagetype = "success"
        message = f"Data fetched successfully"
        filelocation = "fetchcasadmin.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message": "Data fetched successfully", "data": normal_payload})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "fetchcasadmin.py"
        generatelogs(messagetype, message, filelocation)        
        return jsonify({"error": str(e)}), 500