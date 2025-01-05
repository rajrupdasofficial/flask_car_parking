"""
fetch faq details by admin
"""
from flask import Blueprint,jsonify,request
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

fetchfaqasadmin_bp = Blueprint("fetchfaqasadmin_bp",__name__)

@fetchfaqasadmin_bp.route("/fetchfaqasadmin",methods=["POST"])
def fetchfaqasadmin():
    adminid = str(request.form.get("adminid"))

    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM feedback adminid = %s
        """,(adminid,))

        result = cursor.fetchall()
                  
        messagetype = "success"
        message = f"Data fetched successfully"
        filelocation = "fetchfaqasadmin.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message":"Data fetched successfully","data":result})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "fetchfaqasadmin.py"
        generatelogs(messagetype, message, filelocation)        
        return jsonify({"error": str(e)}), 500