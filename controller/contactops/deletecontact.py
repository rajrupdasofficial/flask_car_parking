"""
Delete contact details
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
deletecontact_bp = Blueprint("deletecontact",__name__)

@deletecontact_bp.route("/deletecontact",methods=["POST"])
def deletecontact():
    contactid = str(request.form.get("contactid"))
    
    if not contactid:
        return jsonify({"error":"contact id is required"}),400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM contact WHERE id = %s
        """,(contactid,))
        
        messagetype='success'
        message= "Contact data hasbeen deleted successfully"
        filelocation = 'deletecontact.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"message":"Contact data hasbeen deleted successfully"}),200

    except Exception as e:
        print(e)
        messagetype='error'
        message=f"{e}"
        filelocation = 'deletewallet.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        conn.close()
        cursor.close()