"""
delete a spot booking manually
"""
from flask import Blueprint,jsonify,request
from decouple import config
import psycopg2

from util.logs import generatelogs

deletebooking_bp=Blueprint('deletebooking_bp',__name__)

def conn():
    """Establish a connection to the PostgreSQL"""
    connection = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    return connection

@deletebooking_bp.route("/deletebooking",metods=['POST'])
def deletebooking():
    bookingid = str(request.form.get('bookingid'))

    if not bookingid:
        messagetype='error'
        message=f"Booking id required to remove the item"
        filelocation = 'deletebooking.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":"Booking id required to remove the item"})
    
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM bookings WHERE uid = %s
                """,(bookingid))
        messagetype='success'
        message=f"Data deleted successfully"
        filelocation = 'deletebooking.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"success":"Data deleted successfully"})
    except Exception as e:
        print(f"error {e}")
        messagetype='error'
        message=f"{e}"
        filelocation = 'deletebooking.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()