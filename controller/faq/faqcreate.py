"""
Create faq
"""
from flask import Blueprint,jsonify,request
from datetime import datetime,timezone
import pytz
import os
import uuid
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

faqcreate_bp = Blueprint("faqcreate",__name__)

@faqcreate_bp.route("/faqcreate",methods=["POST"])
def createfaqdetails():
    faqquestion = str(request.form.get("faqquestion"))
    faqdescription = str(request.form.get("faqdescription"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO faq(id,faqquestion,faqdescription)
                       VALUES(%s, %s, %s)
        """,
        (
            str(uuid.uuid4()),
            faqquestion,
            faqdescription
        )
        ) 
        conn.commit()

        # Log success message
        messagetype = "success"
        message = "FAQ create details"
        filelocation = "faqcreate.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message":"Faq hasbeen successfully created"}),201
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "faqcreate.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        conn.close()
        cursor.close()