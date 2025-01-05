from flask import Blueprint, request, jsonify
import psycopg2
import os
import logging
from datetime import datetime
from uuid import uuid4
from lib.emailsender import email_sender
from util.logs import generatelogs

# Create a new blueprint for bookings
createbooking_bp = Blueprint('createbooking', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


# Database connection setup
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

# Function to generate a custom random UID (placeholder)
def generate_custom_random_uid():
    return str(uuid4())

@createbooking_bp.route('/spotbookings', methods=['POST'])
def charger_bookings():
    useruid = str(request.form.get('useruid'))
    bookingtimefrom = str(request.form.get('bookingtimefrom'))
    bookingtimeto = str(request.form.get('bookingtimeto'))
    parkingno = str(request.form.get("parkingno"))
    parkingspotno = str(request.form.get("parkingspotno"))
    adminid = str(request.form.get("adminid"))
    # Assume booking times are received in IST and stored as such
    ist_booking_time_from = datetime.fromisoformat(bookingtimefrom)
    ist_booking_time_to = datetime.fromisoformat(bookingtimeto)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user info
        cursor.execute("SELECT email, name FROM users WHERE uuid = %s", (useruid,))
        userinfo = cursor.fetchone()
        
        if not userinfo:
            generatelogs('error', "User not found", 'bookingcreate.py')
            return jsonify({"message": "User not found"}), 404
        
        email, username = userinfo

        # Check if the parking spot is already booked during the requested time
        cursor.execute("""
            SELECT id FROM bookings 
            WHERE parkingno = %s AND parkingspotno = %s 
            AND (bookingtimefrom < %s AND bookingtimeto > %s)
        """, (parkingno, parkingspotno, ist_booking_time_to, ist_booking_time_from))

        existing_spot_booking = cursor.fetchone()

        if existing_spot_booking:
            # If the spot is already booked, return an error message
            generatelogs('error', "Parking spot is already booked", 'bookingcreate.py')
            return jsonify({"message": "This parking spot is already booked during the requested time."}), 409
        
        # Create a new booking entry since no previous bookings exist for this user and time
        new_uid = generate_custom_random_uid()
        
        cursor.execute("""
            INSERT INTO bookings (useruid, isbooked, bookingtimefrom, bookingtimeto, remindersent, adminid ,parkingno, parkingspotno) 
            VALUES ( %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (useruid, True, ist_booking_time_from, ist_booking_time_to,False,adminid ,parkingno, parkingspotno))
        
        result = cursor.fetchone()
        conn.commit()

        logging.info("Booking created successfully")
        generatelogs('success', "Booking created successfully", 'bookingcreate.py')

        # Send confirmation email with IST times for display purposes
        subject = "Spot Booking Confirmation"
        text = f"""
        Hi {username},

        Your Parking spot has been booked successfully from {ist_booking_time_from.isoformat()} to {ist_booking_time_to.isoformat()}.

        Best Regards,

        Team Transev.
        """ 
        email_sender(email, subject, text)

        return jsonify({"message": "Spot booked successfully", "result": result}), 201

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        generatelogs('error', f"{e}", 'bookingcreate.py')
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()