"""
Main client websocket
"""
import socketio

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

def testing():
        sio.emit('mainops',{
        'cardetected':'true',
        'distance':'5',
        'sensorid':'sensor1',
        'vehiclelength':'1350',
        'vehiclewidth':'250',
        })

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    print("Testing with mockup data")
    testing()
    sio.wait()
    sio.disconnect()
