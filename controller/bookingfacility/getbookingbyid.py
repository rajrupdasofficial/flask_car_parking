"""
Get booking by its id
"""
from flask import Blueprint, request, jsonify
import psycopg2
import os
import jwt
from decouple import config
from datetime import datetime

from util.logs import generatelogs

getbookingbyid_bp = Blueprint('getbookingbyid_bp', __name__)

# Database connection setup
def conn():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@getbookingbyid_bp.route('/getbookingbyid', methods=['POST'])
def getbookingbyid():
    bookingid = str(request.form.get('bookingid'))
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                # Corrected SQL query with FROM clause
                cursor.execute("""
                    SELECT id, uid, useruid, isbooked, bookingtimefrom, bookingtimeto 
                    FROM bookings WHERE uid = %s
                """, (bookingid,))  # Ensure this is a tuple
                
                result = cursor.fetchone()
                
                if result is None:
                    messagetype='error'
                    message=f"Associated booking with the id is not found"
                    filelocation = 'getbookingid.py'
                    generatelogs(messagetype,message,filelocation)
                    return jsonify({"error": "Associated booking with the id is not found"}), 404
                
                # Convert result to a dictionary for easier manipulation
                result_dict = {
                    "id": result[0],
                    "uid": result[1],
                    "useruid": result[2],
                    "isbooked": result[3],
                    "bookingtimefrom": result[4].isoformat() if isinstance(result[4], datetime) else result[4],
                    "bookingtimeto": result[5].isoformat() if isinstance(result[5], datetime) else result[5]
                }
                
                # Prepare JWT token with the result data
                token_payload = {
                    "data": result_dict
                }
                token = jwt.encode(token_payload, config('JWT_SECRET'), algorithm='HS256')
                messagetype='success'
                message=f"Data fetched successfully"
                filelocation = 'getbookingid.py'
                generatelogs(messagetype,message,filelocation)
                return jsonify({"message": "Data fetched successfully", "token": token, "data": result_dict})
    
    except Exception as e:
        print(f"Error: {e}")
        messagetype='error'
        message=f"{e}"
        filelocation = 'getbookingid.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        