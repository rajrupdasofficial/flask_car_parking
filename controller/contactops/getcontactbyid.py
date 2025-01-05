"""
Get contact by id
"""
from flask import Blueprint,jsonify,request
import os
import psycopg2
from uuid import uuid4

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

getcontactbyid_bp = Blueprint("getcontactbyid",__name__)

@getcontactbyid_bp.route("/getcontact",methods=["POST"])
def getcontactbyid():
    contactid = str(request.form.get("contactid"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM contact WHERE id = %s
        """,(contactid,))
        
        result = cursor.fetchone()

        if result is None:
            return jsonify({"message":"Data associated with the id doesnot exist"})
         
        messagetype = "success"
        message = "contact details retrieved successfully."
        filelocation = "getcontactbyid.py"
        generatelogs(messagetype,message,filelocation)
        
        return({"message":"Contact details hasbeen retrive successfully","data":result})
    
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "getcontactbyid.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)

        return jsonify({"error":str(e)}),500
    
    finally:
        cursor.close()
        conn.close()