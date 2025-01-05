# client.py

import socketio

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def message_from_server(data):
    print("Response from server:", data)

@sio.event
def disconnect():
    print("Disconnected from the server")

if __name__ == '__main__':
    sio.connect('http://localhost:5000')

    # Send a test message to the server
    sio.emit('message_from_client', {'message': 'Hello, Server!'})

    # Wait for responses before disconnecting
    sio.wait()