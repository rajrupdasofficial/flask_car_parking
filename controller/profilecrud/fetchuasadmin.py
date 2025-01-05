"""
Check which user under which admin 
"""
from flask import Blueprint,jsonify,request
import psycopg2
import os
from util.logs import generatelogs
import base64


def get_db_conn():
    """Establish a connection to the PostgreSQL"""
    connection = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
    return connection

fetchadmin_bp = Blueprint("fetchadmin",__name__)

@fetchadmin_bp.route("/fetchuserbyadmin",methods=["POST"])
def fetchadminfun():
    adminid = str(request.form.get('adminid'))

    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT uuid, name, email, phone_number, profilepictures FROM users WHERE adminid = %s
        """,(adminid,))
        result = cursor.fetchall()

        if result is None:
            return jsonify({"error":"The user is not found"})
        # Get the data from result
        stored_uuid, stored_name, stored_email, stored_number, profile_picture_path = result
                # Check if profile picture exists and read it
        profile_picture_data = None
        if profile_picture_path and os.path.exists(profile_picture_path):
            with open(profile_picture_path, "rb") as img_file:
                profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        normal_payload = {
                "uuid": stored_uuid,
                "name": stored_name,
                "email": stored_email,
                "phonenumber": stored_number,
                "profile_picture": profile_picture_data  # Include base64 encoded image or None
            }
        
        
        messagetype = "success"
        message = f"Data fetched successfully"
        filelocation = "fetchasadmin.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message": "Data fetched successfully", "data": normal_payload})
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "getuserprofilebyuserid.py"
        generatelogs(messagetype, message, filelocation)        
        return jsonify({"error": str(e)}), 500