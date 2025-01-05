"""
Wallet recharge history for a single user
"""
from flask import Blueprint,jsonify,request
import os
import psycopg2

from util.logs import generatelogs

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        sslmode='require'
    )

wrechhisforsu_bp = Blueprint("walletrechhis",__name__)

@wrechhisforsu_bp.route("/wshis",methods=["POST"])
def hiswall():
    userid = str(request.form.get("userid"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM walletreachargehistory WHERE userassociatedid = %s
        """,(userid,))
        
        result = cursor.fetchall()
        print(result)
        messagetype = "success"
        message = "All of the history hasbeen fetched"
        filelocation = "wrechhisforsu.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message":"All of the history","data":result})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "wrechhisforsu.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    finally:
          # Ensure resources are released properly
        if cursor:
            cursor.close()
        if conn:
            conn.close()