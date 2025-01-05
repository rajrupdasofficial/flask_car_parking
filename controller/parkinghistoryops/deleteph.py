"""
Delete a parking history
"""
from flask import Blueprint,jsonify,request
import psycopg2
import os
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

phdel_bp = Blueprint("phdel_bp",__name__)

@phdel_bp.route("/deleteparkinghistory",methods=["POST"])
def deleteph():
    conn = None
    cursor = None
    
    phid  = str(request.form.get("phid"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE from parkinghistory WHERE id = %s
        """,(phid,))

        messagetype = "success"
        message = "Parking history hasbeen retrive successfully"
        filelocation = "deleteph.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"Data hasbeen deleted successfully"})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "deleteph.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)
    finally:
        conn.close()
        cursor.close()