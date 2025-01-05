"""
Get wallet by id
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

getwalletid_bp = Blueprint('getwalletbyid',__name__)

@getwalletid_bp.route("/getwalletbyid",methods=["POST"])
def getwalletbyid():
    walletid = str(request.form.get("walletid"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM wallet WHERE id = %s
        """,(walletid))
        result = cursor.fetchone()

        return jsonify({"message":"wallet data hasbeen fetched successfully","data":result})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "getwalletbyid.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error":str(e)}),500