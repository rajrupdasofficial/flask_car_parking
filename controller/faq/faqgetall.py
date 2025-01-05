"""
get all faqs
"""
from flask import Blueprint,jsonify,request
import psycopg2
import os
import jwt

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

faqgetall_bp = Blueprint("faqgetall",__name__)

@faqgetall_bp.route("/faqgetall",methods=["GET"])
def faqall():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM faq
        """)
        result = cursor.fetchall()
        # Log success message
        messagetype = "success"
        message = "FAQ create details"
        filelocation = "faqgetall.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"all faqs habeen successfully fetched","data":result})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "faqgetall.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":e})
    finally:
        conn.close()
        cursor.close()