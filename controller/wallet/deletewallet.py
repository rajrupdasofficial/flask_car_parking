"""
Delete wallet details
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

deletewallet_bp = Blueprint("deletewalletdetails",__name__)

@deletewallet_bp.route("/deletewallet",methods=["POST"])
def deletewallet():
    walletid = str(request.form.get("walletid"))

    if not walletid:
        return jsonify({"error":"Wallet id is required"}),400
    try:

        conn = get_db_connection()
        cursor = conn.cursor()
    
        cursor.execute("""
            DELETE FROM wallet WHERE id = %s
            """,(walletid))
        messagetype='success'
        message= "Wallet data hasbeen deleted successfully"
        filelocation = 'deletewallet.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"message":"Wallet data hasbeen deleted successfully"}),200

    except Exception as e:
        print(f"error {e}")
        messagetype='error'
        message=f"{e}"
        filelocation = 'deletewallet.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        conn.close()
        cursor.close()
