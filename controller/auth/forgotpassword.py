"""
reset password module 
this passwordreset module is written using python .

"""

import psycopg2
import bcrypt
import random
import time
import traceback
from flask import Blueprint, request, jsonify
from decouple import config
# from lib.emailqueue import add_email_job
from lib.emailsender import email_sender
from util.logs import generatelogs

# Create a Blueprint for password reset
passwordreset_bp = Blueprint('passwordreset_bp', __name__)

# Temporary storage for OTPs
temp_storage = {}

# Connect to the database
def get_db_connection():
    conn = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    return conn

# Function to log messages (replace with your actual lo mechanism)
def lo(messagetype, message, filelocation):
    print(f"{messagetype}: {message} (Logged from {filelocation})")
    generatelogs(messagetype,message,filelocation)
    

# Password reset logic
@passwordreset_bp.route('/passwordreset', methods=['POST'])
def password_reset_logic():
    email = request.form.get('email')
    otp = request.form.get('otp')
    new_password = request.form.get('newpassword')

    try:
       

        # Step 1: Request OTP
        if email and not otp and not new_password:
            # Check if user exists
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT uuid,name,username FROM users WHERE email = %s;", (email,))
            existing_user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not existing_user:
                lo("error", "No user found with this email.", "forgotpassword.py")
                return jsonify({"message": "No user found with this email."}), 404
            user_name = existing_user[1]
            # Generate a 6-digit OTP
            otp_generated = str(random.randint(100000, 999999))

            # Store the generated OTP and expiration in temporary storage
            temp_storage[email] = {
                'generatedOtp': otp_generated,
                'otpExpiration': time.time() + 15 * 60  # 15 minutes from now
            }

            # Send the OTP via email (simulated here)
            subject = 'OTP for Password Reset'
            text = f"Hello {user_name} Your OTP for password reset is: {otp_generated}"

            # In a real application, you'd call your email queue to send the email
            email_sender(email, subject, text)
            lo("success", f"OTP {otp_generated} sent to {email} for password reset.", "forgotpassword.py")

            return jsonify({"message": "OTP sent to your email for password reset."}), 201

        # Step 2: Verify OTP and reset password
        if otp and new_password and email:
            # Check if email exists in temporary storage
            if email not in temp_storage:
                lo("error", "Session expired or invalid. Please request a new OTP.", "forgotpassword.py")
                return jsonify({"message": "Session expired or invalid. Please request a new OTP."}), 400

            otp_data = temp_storage[email]

            # Ensure otp_data contains expected keys
            if 'otpExpiration' not in otp_data or 'generatedOtp' not in otp_data:
                lo("error", "OTP data is incomplete.", "forgotpassword.py")
                return jsonify({"message": "Invalid OTP data."}), 400
            
            # Check if OTP is expired
            if time.time() > otp_data['otpExpiration']:
                del temp_storage[email]  # Clean up expired session
                lo("error", "OTP has expired.", "forgotpassword.py")
                return jsonify({"message": "OTP has expired."}), 400

            # Check if provided OTP matches
            if otp != otp_data['generatedOtp']:
                lo("error", "Invalid OTP.", "forgotpassword.py")
                return jsonify({"message": "Invalid OTP."}), 400

            # Clear OTP after successful verification
            del temp_storage[email]

            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password in the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s;", (hashed_password, email))
            conn.commit()
            cursor.close()
            conn.close()

            lo("success", f"Password reset successfully for email: {email}", "forgotpassword.py")

            return jsonify({"message": "Password reset successfully."}), 200

        # If neither condition is met, return an error
        lo("error", "Invalid request. Provide either an email to receive an OTP or both an OTP and a new password.", "forgotpassword.py")
        return jsonify({"message": "Invalid request. Provide either an email to receive an OTP or both an OTP and a new password."}), 400

    except Exception as err:
        lo("error", f"Error occurred: {err}\nTraceback: {traceback.format_exc()}", "forgotpassword.py")
        return jsonify({"message": "Internal server error.", "error": str(err)}), 500
    
    finally:
        cursor.close()
        conn.close()