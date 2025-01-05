"""
car detection using magnetic sensor
client section
"""
import socketio
import random
import time
import uuid
import jwt
import os
import json  # Import json module for manual conversion

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def response(data):
    print(f"Prediction Result: Car Presence: {data}")

@sio.event
def disconnect():
    print("Disconnected from the server.")

def test_cardtumgs():
    parkinglocation = "Kolkata"
    parkingarea = "dum dum"
    psno = str(uuid.uuid4())
    iscarpresent = random.randint(0, 1)
    sensorid = str(uuid.uuid4())
    sensorstatus = random.randint(0, 1)
    paymentstatus = random.randint(0, 1)
    
    token_payload = {
        'parkinglocation': parkinglocation,
        'parkingarea': parkingarea,
        'psno': psno,
        'iscarpresent': iscarpresent,
        'sensorid': sensorid,
        'sensorstatus': sensorstatus,
        'paymentstatus': paymentstatus
    }
    
    token = jwt.encode(token_payload, os.getenv('JWT_SECRET'), algorithm='HS256')
    
    # Return a dictionary instead of using jsonify
    return {"token": token}

def testops():
    while True:
        data = test_cardtumgs()
        # Convert the data to JSON format before emitting
        sio.emit('cardtumgroute', data)
        
        time.sleep(0.4)

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    try:
        testops()
    except KeyboardInterrupt:
        print("Stopping the client...")
    finally:
        sio.disconnect()