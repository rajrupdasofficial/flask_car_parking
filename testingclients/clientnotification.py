"""
notification status check confirmation channel
"""
import socketio
import random
import uuid

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def response(data):
    print("Response from the server",data)

@sio.event
def disconnect():
    print("Disconnected from the server")

def test_channel():
    sio.emit('bookingconfchannel', {
        "parkingspotid": str(uuid.uuid4()),  # Convert UUID to string if needed
        'detectionstatus': 'yes',
        'confirmationstatus': 'yes'
    })

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    print("Testing started")
    test_channel()
    sio.wait()  # This will keep the program running to receive responses
    # Optionally, you can disconnect after tests are done
    sio.disconnect()