"""
user signup single way module
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import pytz
from decouple import config
import psycopg2
import bcrypt
import uuid
import re
import os

from util.logs import generatelogs  # Import regex for validation

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

adminsignup_bp = Blueprint('adminsignup', __name__)

# Function to validate email
def is_valid_email(email):
    # Simple regex for validating email format
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@adminsignup_bp.route('/admin/signup', methods=['POST'])
def adminsignup():
    # Extracting user details from request data
    name = str(request.form.get('name'))  # Retaining name field
    email = str(request.form.get('email'))
    phonenumber = str(request.form.get("phonenumber"))
    password = str(request.form.get('password'))

    # Basic validation
    if email and password:
        if not is_valid_email(email):
            messagetype = 'error'
            message = "Invalid email format!"
            filelocation = 'signup.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "Invalid email format!"}), 400
        
        # Check if the email already exists
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM admin WHERE email = %s
            """, (email,))
            count = cursor.fetchone()[0]  # Get the count of matching records
            cursor.execute("""
                SELECT COUNT(*) FROM admin WHERE phonenumber = %s
                """,(phonenumber,))
            phcount = cursor.fetchone()[0]

            if count > 0:
                messagetype = 'error'
                message = "Email already exists!"
                filelocation = 'adminsignup.py'
                generatelogs(messagetype, message, filelocation)
                return jsonify({"error": "Email already exists!"}), 400
            if phcount >0:
                return jsonify({"error":"Phone number already exists"}),400

        except Exception as e:
            messagetype = 'error'
            message = f"{e}"
            filelocation = 'adminsignup.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": str(e)}), 500

        # Get the current time in UTC as a timezone-aware object
        utc_time = datetime.now(timezone.utc)
        
        # Define the IST timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        
        # Convert UTC to IST
        ist_time = utc_time.astimezone(ist_timezone)
        
        # Format the date and time in ISO format
        created_at = ist_time.isoformat()  # Now in IST
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create a user document to insert into PostgreSQL
        admin_data = {
  # Generate a UUID for the new user
            "name": name,
            "email": email,
            "password": hashed_password.decode('utf-8'),  # Store the hashed password as a string
            "created_at": created_at,  # Use IST time here (optional)
            "phone_number": phonenumber,
        }
        
        try:
            # Establish a connection to the PostgreSQL database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert user data into the database
            cursor.execute("""
                INSERT INTO admin ( name, email, password, createdat, phonenumber, userrole)
                VALUES ( %s, %s, %s, %s, %s, %s)
            """, (admin_data['name'], admin_data['email'], admin_data['password'], admin_data['created_at'], admin_data['phone_number'],  'admin'))
            
            conn.commit()  # Commit the transaction
            
            messagetype = 'success'
            message = "Signup successful"
            filelocation = 'adminsignup.py'
            generatelogs(messagetype, message, filelocation)
            
            return jsonify({"message": "Signup successful", "name": name}), 201
        
        except Exception as e:
            messagetype = 'error'
            message = f"{e}"
            filelocation = 'adminsignup.py'
            generatelogs(messagetype, message, filelocation)
            
            return jsonify({"error": str(e)}), 500
    
    else:
        messagetype = 'error'
        message = "Email and password are required!"
        filelocation = 'adminsignup.py'
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": "Email and password are required!"}), 400
