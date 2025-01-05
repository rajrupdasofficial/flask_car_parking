"""
Survey create
"""

from flask import Blueprint, jsonify, request
import psycopg2
import os
from util.logs import generatelogs

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

surveycreate_bp = Blueprint("surveycreate", __name__)

@surveycreate_bp.route("/createsurvey", methods=["POST"])
def surveycreate():
    required_fields = [
        'name', "email", "ratingnumber", "feedbackmessage", "associatedadminid", "feedbacktype"
    ]
    form_data = {field: request.form.get(field) for field in required_fields}
    
    # Check for missing fields
    for field, value in form_data.items():
        if value is None:
            return jsonify({"error": f"Missing field: {field}"}), 400
        
    name = str(form_data["name"])
    email = str(form_data["email"])
    ratingnumber = str(form_data["ratingnumber"])
    feedbackmessage = str(form_data["feedbackmessage"])
    associatedadminid = str(form_data["associatedadminid"])
    feedbacktype = str(form_data["feedbacktype"])

    # Set issurveytook to 'true'
    issurveytook = 'true'

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Complete INSERT statement including issurveytook
        cursor.execute("""
            INSERT INTO public.feedback (
                name, email, ratingnumber, feedbackmessage, associatedadminid, issurveytook, feedbacktype 
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (name, email, ratingnumber, feedbackmessage, associatedadminid, issurveytook, feedbacktype))
        
        # Fetch the newly created ID (optional)
        # new_id = cursor.fetchone()[0]
        # Commit the transaction
        conn.commit()
        messagetype = "Success"
        message = f"Feedback submitted successfully"
        filelocation = "surveycreate.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message": "Feedback submitted successfully"}), 201
        
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "surveycreate.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()
