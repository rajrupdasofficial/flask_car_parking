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


def test_car_detection_ops(carisdetected, distance, gpscoordinates,lengthoftheobject):
    sio.emit('cardsoc',{
        'carisdetected':carisdetected,
        'distance':distance,
        'gpscoordinates':gpscoordinates,
        'lengthoftheobject':lengthoftheobject  
    })

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    print("Testing with some mockup data")
    test_car_detection_ops('yes','5','22.88,88.20','90m')

    sio.wait()
    sio.disconnect()