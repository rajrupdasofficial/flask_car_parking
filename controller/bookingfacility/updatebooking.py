from flask import Blueprint, request, jsonify
import psycopg2
import os
import logging
from datetime import datetime
from util.logs import generatelogs

# Create a new blueprint for updating bookings
updatebooking_bp = Blueprint('updatebooking_bp', __name__)

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

@updatebooking_bp.route("/updatebookings", methods=['POST'])
def update_booking():
    bookingid = request.form.get('bookingid')
    userid = request.form.get("userid")
    bookingtimefrom = request.form.get('bookingtimefrom')
    bookingtimeto = request.form.get('bookingtimeto')
    parkingno = request.form.get('parkingno')
    parkingspotno = request.form.get('parkingspotno')

    # Check if userid is provided
    if not userid or not bookingid:
        return jsonify({"error": "User ID and Booking ID are required"}), 400

    # Prepare the update fields
    update_fields = {}
    
    if bookingtimefrom:
        try:
            ist_booking_time_from = datetime.fromisoformat(bookingtimefrom)
            update_fields['bookingtimefrom'] = ist_booking_time_from
        except ValueError:
            return jsonify({"error": "Invalid format for bookingtimefrom. Use ISO format."}), 400
            
    if bookingtimeto:
        try:
            ist_booking_time_to = datetime.fromisoformat(bookingtimeto)
            update_fields['bookingtimeto'] = ist_booking_time_to
        except ValueError:
            return jsonify({"error": "Invalid format for bookingtimeto. Use ISO format."}), 400
            
    # Check if parkingno is set to be removed or updated
    if parkingno == "remove":  # Explicitly remove parking number
        update_fields['parkingno'] = None
    elif parkingno:  # Update with new value if provided
        update_fields['parkingno'] = parkingno
        
    # Check if parkingspotno is set to be removed or updated
    if parkingspotno == "remove":  # Explicitly remove parking spot number
        update_fields['parkingspotno'] = None
    elif parkingspotno:  # Update with new value if provided
        update_fields['parkingspotno'] = parkingspotno

    # Check if there are fields to update
    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    # Construct the SQL query dynamically based on provided fields
    set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
    
    # Add user ID and booking ID for the WHERE clause
    values = list(update_fields.values()) + [userid, bookingid]

    sql_query = f"""
        UPDATE bookings 
        SET {set_clause} 
        WHERE useruid = %s AND id = %s;
    """

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql_query, values)
            conn.commit()

            if cursor.rowcount == 0:
                generatelogs('error', "No booking found with the provided ID", 'updatebooking.py')
                return jsonify({"message": "No booking found with the provided ID"}), 404
            
            generatelogs('success', "Booking updated successfully", 'updatebooking.py')
            return jsonify({"message": "Booking updated successfully"}), 200
    
    except Exception as e:
        logging.error(f"Error updating booking details: {str(e)}")
        
        # Log detailed error information
        generatelogs('error', f"{e}", 'updatebooking.py') 
        return jsonify({"error": "Failed to update booking details"}), 500
    
    finally:
        if conn:
            conn.close()