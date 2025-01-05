"""
Get all of the saved bookings
"""
from flask import Blueprint,request,jsonify
import psycopg2
from decouple import config
import logging

from util.logs import generatelogs

logging.basicConfig(level=logging.DEBUG)

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

getbookings_bp = Blueprint('getbookings_bp',__name__)

@getbookings_bp.route('/getbookings',methods=['POST'])
def getbookings():
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * from Bookings
                """)
            bookings = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            bookingdata = [dict(zip(columns,booking)) for booking in bookings]
            messagetype='success'
            message=f"all data hasbeen fetched successfully"
            filelocation = 'getbookings.py'
            generatelogs(messagetype,message,filelocation)
            return jsonify({"message":"all data hasbeen fetched successfully","data":bookingdata}),200

    except Exception as e:
        logging.error("Error inserting vehicle data: %s",str(e))
        messagetype='error'
        message=f"{e}"
        filelocation = 'getbookings.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    
    finally:
        cursor.close()