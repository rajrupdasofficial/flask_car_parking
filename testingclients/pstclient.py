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

def test_parking_operation(parkingspotav, iscarpresent, distancefromthecar):
    sio.emit('parkingoperationmanagement',{
         'parkingspotav': parkingspotav,
        'iscarpresent': iscarpresent,
        'distancefromthecar': distancefromthecar
    })

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
     # Test cases
    print("Testing with an occupied parking spot:")
    test_parking_operation('yes', 'yes', '10')  # Expect: "Parking spot is already occupied"

    print("\nTesting with an available parking spot:")
    test_parking_operation('yes', 'no', '10')  # Expect: "Parking spot is available"

    print("\nTesting with invalid input:")
    test_parking_operation('', '', '')  # Expect: "Invalid input data"

    # Wait for responses before disconnecting
    sio.wait()  # This will keep the program running to receive responses
    # Optionally, you can disconnect after tests are done
    sio.disconnect()