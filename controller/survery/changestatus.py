import os
import logging
from flask import Blueprint, jsonify, request
import psycopg2
from util.logs import generatelogs  # Assuming you have a logging utility

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

feedbackstatus_bp = Blueprint("feedbackstatus", __name__)

@feedbackstatus_bp.route("/formstatus", methods=["POST"])
def feedback_form_status():
    id = str(request.form.get("id"))  # Get the ID from form data

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the existing feedback record
        cursor.execute("""
            SELECT * FROM feedback WHERE id = %s
        """, (id,))
        feedback = cursor.fetchone()

        if not feedback:
            return jsonify({"message": "Feedback not found"}), 404

        # Toggle the status at index 6 (isserveytook)
        is_served_yet = feedback[6]  # Accessing isserveytook at index 6
        updated_status = 'true' if is_served_yet == 'false' else 'false'  # Assuming it's stored as 'true'/'false'

        # Update the feedback record with the new status
        cursor.execute("""
            UPDATE feedback SET isserveytook = %s, updatedat = NOW() WHERE id = %s
        """, (updated_status, id))

        conn.commit()

        # Fetch updated feedback to return it
        cursor.execute("""
            SELECT * FROM feedback WHERE id = %s
        """, (id,))
        updated_feedback = cursor.fetchone()

        messagetype = "Success"
        message = "Feedback status has been updated successfully"
        filelocation = "feedback.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"data": updated_feedback}), 200

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {e}"
        filelocation = "feedback.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
