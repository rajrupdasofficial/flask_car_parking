"""
Create and Save contact details
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

createcontact_bp = Blueprint("createcontact",__name__)

@createcontact_bp.route("/contactus",methods=["POST"])
def contactus():

    firstname = str(request.form.get("firstname"))
    lastname = str(request.form.get("lastname"))
    email = str(request.form.get("email"))
    messages = str(request.form.get("messages"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO contact(id,firstname,lastname,email,messages)
        VALUES(%s, %s, %s, %s, %s)    
        """,(str(uuid4()),firstname,lastname,email,messages))
        
        conn.commit()
        
        # Log success message
        messagetype = "success"
        message = "Contact details hasbeen saved"
        filelocation = "createcontact.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"Contact details hasbeen saved successfully"}),200
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "createcontact.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        conn.close()
        cursor.close()