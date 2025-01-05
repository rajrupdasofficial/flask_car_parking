"""
Get all wallet details
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

getwallet_bp = Blueprint('getallwallet',__name__)

@getwallet_bp.route("/getwalletdata",methods=["GET"])
def getallwallet():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM wallet
        """)
        result = cursor.fetchall()

        return jsonify({"message":"get all wallet data","data":result})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "getwallet.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        conn.close()