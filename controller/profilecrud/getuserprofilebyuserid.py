from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2
import jwt
from datetime import datetime, timedelta
import pytz
import os  # Import os for file path operations
import base64  # Import base64 for encoding images

from util.logs import generatelogs

# Create a blueprint route
getuserbyid_bp = Blueprint("getuserbyid", __name__)

def get_db_conn():
    """Establish a connection to the PostgreSQL database."""
    connection = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    return connection

@getuserbyid_bp.route('/users/details', methods=['POST'])
def getuserbyid():
    userid = str(request.form.get('userid'))

    if not userid:
        return jsonify({"error": "userid is required"}), 400
    
    try:
                conn = get_db_conn()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT uuid, name, email, phone_number, profilepictures FROM users WHERE uuid = %s
                    """, (userid,)  # Ensure this is a tuple
                )
                result = cursor.fetchone()
                
                if result is None:
                    return jsonify({"error": "The user is not found"}), 404
                
                # Get the data from result
                stored_uuid, stored_name, stored_email, stored_number, profile_picture_path = result
                
                # Check if profile picture exists and read it
                profile_picture_data = None
                if profile_picture_path and os.path.exists(profile_picture_path):
                    with open(profile_picture_path, "rb") as img_file:
                        profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')

                # Prepare response payload
                normal_payload = {
                    "uuid": stored_uuid,
                    "name": stored_name,
                    "email": stored_email,
                    "phonenumber": stored_number,
                    "profile_picture": profile_picture_data  # Include base64 encoded image or None
                }

                messagetype = "success"
                message = f"Data fetched successfully"
                filelocation = "getuserprofilebyuserid.py"
                generatelogs(messagetype, message, filelocation)
                
                return jsonify({"message": "Data fetched successfully", "data": normal_payload})

    except Exception as e:
        print(f"error is -- {e}")   
        messagetype = "error"
        message = f"{e}"
        filelocation = "getuserprofilebyuserid.py"
        generatelogs(messagetype, message, filelocation)        
        return jsonify({"error": str(e)}), 500
