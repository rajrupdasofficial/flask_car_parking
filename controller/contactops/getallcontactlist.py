"""
Get all of the contact list
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

getallcontactlist_bp = Blueprint("getallcontactlist",__name__)

@getallcontactlist_bp.route("/getallcontactlist",methods=["GET"])
def getallcontact():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM contact
        """)
        result = cursor.fetchall()

        messagetype = "success"
        message = "All of the contact data hasbeen fetched successfully"
        filelocation = "getallcontactlist.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"all of the contact data hasbeen fetched","data":result})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "getallcontactlist.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        conn.close()
        cursor.close()