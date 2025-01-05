"""
detect car usng sensor data realtime
"""
from flask_socketio import SocketIO,emit
import os
import psycopg2

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

def cardetectionfunc(socketio):
    @socketio.on('cardsoc')
    def handelcardec(data):
        try:
            carisdetcted = data.get("carisdetected")
            distance = data.get("distance")
            gpscoordinates = data.get("gpscoordinates")
            lengthoftheobject = data.get("lengthoftheobject")
            if carisdetcted == 'yes':
                response_message = "Car has detcted using the ultra sonic sensor"
            if distance == "5":
                response_message = "The car is 5 meter away from the parking location"
            if gpscoordinates:
                response_message = f"The gps coordinate is {gpscoordinates}"
            if lengthoftheobject:
                response_message = f"The length of the object is {lengthoftheobject}"
            else:
                response_message = "given data is invalid"
            print(f"Emitting response: {response_message}")
            messagetype='success'
            message= f"Car detection is working {response_message}"
            filelocation = 'cardetection.py'
            generatelogs(messagetype,message,filelocation)
            emit('response',{'status':'success','data':response_message})
        except Exception as e:
            print(f"Error occurred: {e}")
            messagetype='error'
            message=f"{e}"
            filelocation = 'cardetection.py'
            generatelogs(messagetype,message,filelocation)
            emit('response', {'status': 'error', 'data': str(e)})