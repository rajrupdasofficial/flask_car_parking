"""
loginsection for admin
"""

from flask import Blueprint,jsonify,request
import os
import psycopg2
import bcrypt
import jwt
from datetime import datetime, timedelta
import pytz
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

adminlogin_bp = Blueprint("adminlogin_bp",__name__)

@adminlogin_bp.route('/admin/login', methods=['POST'])
def adminlogin():
  
    # Extracting user details from request data
    email = request.form.get('email')
    password = request.form.get('password')

    # Basic validation
    if not email or not password:
        messagetype='error'
        message="Email and password are required!"
        filelocation = 'adminlogin.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": "Email and password are required!"}), 400
    
    try:
        # Establish a connection to the PostgreSQL database
          # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()
                # Check if the user exists with the provided email
            cursor.execute("""
                SELECT id, userrole,  password FROM admin WHERE email = %s
            """, (email,))
            result = cursor.fetchone()

            if result is None:
                messagetype='error'
                message="Email not found!"
                filelocation = 'adminlogin.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"error": "Email not found!"}), 404
            
            # Get the stored hashed password, UUID, and username
            stored_id, stored_userrole, stored_hashed_password = result
            
            # Verify the provided password against the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                # Get current time in IST timezone
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_time = datetime.now(ist_timezone)
                
                # Create JWT token payload with expiration time in IST
                token_payload = {
                    'id': stored_id,
                    'email': email,
                    'role':stored_userrole,
                    'exp': (ist_time + timedelta(hours=6)).timestamp()  # Token expires in 1 hour
                }
                
                token = jwt.encode(token_payload, os.getenv('JWT_SECRET'), algorithm='HS256')
                messagetype='success'
                message="Login successful!"
                filelocation = 'adminlogin.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"message": "Login successful!", "token": token,"adminid":stored_id}), 200
            else:
                messagetype='error'
                message="Password does not match!"
                filelocation = 'adminlogin.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"error": "Password does not match!"}), 401

    except Exception as e:
        messagetype='error'
        message=f"error - {e}"
        filelocation = 'adminlogin.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": str(e)}), 500
    # finally:
    #     cursor.close()
