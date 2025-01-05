"""
fetch parking history by its id
"""
from flask import Blueprint,request,jsonify
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

fetchphadmin_bp = Blueprint("fetchphadmin_bp",__name__)

@fetchphadmin_bp.route("/fetchphadmin",methods=["POST"])
def fetchphadmin():
    adminid = str(request.form.get('adminid'))
    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM public.parkinghistory WHERE adminid = %s
            """
        ,(adminid,))
        result = cursor.fetchall()
        
        messagetype = "success"
        message = f"Data fetched successfully"
        filelocation = "fetchphadmin.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message":"Data fetched successfully","data":result})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{str(e)}"
        filelocation = "fetchphadmin.py"
        generatelogs(messagetype, message, filelocation)