"""
login.py for user authentication

"""

from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2
import bcrypt
import jwt  # Import the PyJWT library
from datetime import datetime, timedelta  # Import timedelta for adding duration
import pytz
import os

from util.logs import generatelogs


login_bp = Blueprint('login', __name__)



def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


@login_bp.route('/users/login', methods=['POST'])
def login():
  
    
    # Extracting user details from request data
    email = request.form.get('email')
    password = request.form.get('password')

    # Basic validation
    if not email or not password:
        messagetype='error'
        message="Email and password are required!"
        filelocation = 'login.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": "Email and password are required!"}), 400
    
    try:
        # Establish a connection to the PostgreSQL database
          # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()
                # Check if the user exists with the provided email
            cursor.execute("""
                SELECT uuid, userrole, adminid, password FROM users WHERE email = %s
            """, (email,))
            result = cursor.fetchone()

            if result is None:
                messagetype='error'
                message="Email not found!"
                filelocation = 'login.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"error": "Email not found!"}), 404
            
            # Get the stored hashed password, UUID, and username
            stored_uuid, stored_userrole, stored_adminid, stored_hashed_password = result
            
            # Verify the provided password against the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                # Get current time in IST timezone
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_time = datetime.now(ist_timezone)
                
                # Create JWT token payload with expiration time in IST
                token_payload = {
                    'uuid': stored_uuid,
                    'email': email,
                    'role':stored_userrole,
                    'adminid':stored_adminid,
                    'exp': (ist_time + timedelta(hours=6)).timestamp()  # Token expires in 1 hour
                }
                
                token = jwt.encode(token_payload, config('JWT_SECRET'), algorithm='HS256')
                messagetype='success'
                message="Login successful!"
                filelocation = 'login.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"message": "Login successful!", "token": token,"userid":stored_uuid}), 200
            else:
                messagetype='error'
                message="Password does not match!"
                filelocation = 'login.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"error": "Password does not match!"}), 401

    except Exception as e:
        messagetype='error'
        message=f"error - {e}"
        filelocation = 'login.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": str(e)}), 500
    # finally:
    #     cursor.close()
