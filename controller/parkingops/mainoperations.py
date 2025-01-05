"""
Total simulation of parking operation backend section
"""
from flask_socketio import SocketIO,emit
import os
import psycopg2
import time
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

def mainops(socketio):
    @socketio.on("mainops")
    def handelops(data):
        cardetected = data.get("cardetected")
        distance = data.get("distance")
        sensorid = data.get("sensorid")
        vehicledetcted = data.get("vehicledetcted")
        vehiclelength =  data.get("vehiclelength")
        vehiclewidth = data.get("vehiclewidth")
        # typeofvehicles = data.get("typeofvehicles")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
            SELECT id from parking_spot WHERE sensorid = %s
            """,(sensorid,))
            
            parkingspotid = cursor.fetchone()
            print("parking spot id",parkingspotid)
            cursor.execute("""
                SELECT id FROM spotdetails WHERE parkingspaceid = %s
            """,(parkingspotid,))
            spotdetailsid = cursor.fetchone()
            print("spot details id",spotdetailsid)

            # if parkingspotid or spotdetailsid == '':
            #     emit('response',{'status':'error',"message":"no parking details found"})           
            
            cursor.execute("""
            SELECT isbooked FROM bookings WHERE parkingno = %s AND parkingspotno = %s
            """,(parkingspotid,spotdetailsid))

            isbookedc = cursor.fetchone()
            print("isbooked",isbookedc)
            
            # if cardetected not in ['true','false']:
            #     emit('response',{'status':'error',"message":"Invalid data received. Expected true or false"})
            # if isbookedc:
            #     emit ('response',{'status':'info',"message":"This spot is already booked"})
            #     time.sleep(3)
            #     emit('response',{"status":'success',"message":f"Redirecting the vehicle to a unoccupied parking spot"})
            #     time.sleep(3)
            #     cursor.execute("""
            #     SELECT parkingspotno FROM bookings WHERE isbooked= FALSE
            #     """)
            #     parkingspotnum  = cursor.fetchone()
            #     emit ('response',{'status':'success',"message":f"New assigned spot for the vehicle is {parkingspotnum}"})
            #     time.sleep(2)
            #     emit('response',{'status':'info',"message":'please follow the display screen for the direction'})   
            # else:
            if vehicledetcted:
                emit('response',{'status':'success',"message":"vehicledetcted detected"})
            if vehiclelength and vehiclewidth:
                time.sleep(3)
                emit('response',{'status':'busy','message':'Searching for a appropriate spot'})
                time.sleep(2)
                cursor.execute("""
                    SELECT id FROM spotdetails
                    WHERE length > %s AND width > %s
                """,(vehiclelength, vehiclewidth))
                suitable_spots = cursor.fetchone()
                time.sleep(1)
                cursor.execute("""
                    SELECT typeofvehicles FROM spotdetails
                    WHERE length > %s AND width > %s
                """,(vehiclelength, vehiclewidth))
                typeofvehicles = cursor.fetchone()
                emit('response',{"status":"info","message":f"Your vehicle type is {typeofvehicles}"})
                emit('response',{'status':'info',"message":f"Available spot for parking is - {suitable_spots}"})
                emit('response',{'status':'info',"message":"Please follow the displayed directions for parking"})
        except Exception as e:
            print(f"Error occurred: {e}")
            messagetype='error'
            message=f"{e}"
            filelocation = 'mainoperations.py'
            generatelogs(messagetype,message,filelocation)
            emit('response', {'status': 'error', 'data': str(e)})