from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2
import jwt
from datetime import datetime, timedelta
import pytz
import bcrypt  # Import bcrypt for password hashing
import os  # For handling file paths
from werkzeug.utils import secure_filename  # For securing file names
import uuid  # Import uuid to generate unique filenames
import base64

from util.logs import generatelogs

update_bp = Blueprint('update_bp', __name__)

# Define where to store profile pictures
UPLOAD_FOLDER = os.path.join('uploads', 'profile_pictures')  # Ensure this folder exists
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image extensions

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def conn():
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

@update_bp.route("/users/update", methods=['POST'])
def updateuser():
    # Access UUID from form data
    uuid_value = request.form.get('uuid')
    
    if not uuid_value:
        return jsonify({"error": "UUID is required"}), 400

    email = request.form.get('email')
    name = request.form.get('name')
    old_password = request.form.get("old_password")  # New field for old password
    new_password = request.form.get("new_password")  # New field for new password
    phonenumber = request.form.get('phonenumber')

    # Prepare a dictionary of fields to update
    update_fields = {}
    
    # Connect to database to fetch the current hashed password
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE uuid = %s", (uuid_value,))
                result = cursor.fetchone()
                
                if not result:
                    return jsonify({"error": "User not found"}), 404
                
                stored_hashed_password = result[0]

                # Check if new password is provided without old password
                if new_password and not old_password:
                    return jsonify({"error": "Old password is required to update the password"}), 400

                # Verify old password
                if old_password and not bcrypt.checkpw(old_password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                    return jsonify({"error": "Wrong old password provided"}), 403

                # Update fields only if provided
                if email:
                    update_fields['email'] = email
                if name:
                    update_fields['name'] = name
                if new_password:  # Use new password only if provided
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    update_fields['password'] = hashed_new_password.decode('utf-8')  # Store as string
                if phonenumber:
                    update_fields['phone_number'] = phonenumber

                # Handle profile picture upload if present in request.files
                profile_picture_data = None
                if 'profilepicture' in request.files:
                    file = request.files['profilepicture']
                    
                    if file and allowed_file(file.filename):
                        new_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
                        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                        file.save(filepath)
                        update_fields['profilepictures'] = filepath
                        
                        with open(filepath, "rb") as img_file:
                            profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')

                # Check if there are fields to update
                if not update_fields:
                    return jsonify({"error": "No fields to update"}), 400

                # Build the SQL query dynamically
                set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
                sql_query = f"UPDATE users SET {set_clause} WHERE uuid = %s"
                
                values = list(update_fields.values())
                values.append(uuid_value)

                cursor.execute(sql_query, values)
                connection.commit()

                # Fetch updated user information
                cursor.execute(
                    "SELECT uuid, name, email, phone_number, profilepictures FROM users WHERE uuid = %s", (uuid_value,)
                )
                updated_user = cursor.fetchone()
                
                if not updated_user:
                    return jsonify({"error": "User not found after update"}), 404
                
                stored_uuid, stored_name, stored_email, stored_phone_number, stored_profilepicture = updated_user
                
                messagetype = "success"
                message = "User updated successfully"
                filelocation = "updateuserprofile.py"
                generatelogs(messagetype,message,filelocation)

                return jsonify({
                    "message": "User updated successfully",
                    "updated_user": {
                        "uuid": stored_uuid,
                        "name": stored_name,
                        "email": stored_email,
                        "phone_number": stored_phone_number,
                        "profile_picture": profile_picture_data or stored_profilepicture
                    }
                }), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        messagetype = "error"
        message = str(e)
        filelocation = "updateuserprofile.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": str(e)}), 500
