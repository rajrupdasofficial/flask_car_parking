"""
delete one faq data
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

deletefaq_bp = Blueprint("deletefaq",__name__)

@deletefaq_bp.route("/deletefaq",methods=["POST"])
def deletefaq():
    deletefaqid = str(request.form.get("deletefaqid"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM faq WHERE id = %s
        """,(
            deletefaqid
        ))
        conn.commit()
        
        messagetype = "success"
        message = f"Faq data has been deleted successfully"
        filelocation = "deletefaq.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"success":"Faq data hasbeen deleted successfully"})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "deletefaq.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        cursor.close()