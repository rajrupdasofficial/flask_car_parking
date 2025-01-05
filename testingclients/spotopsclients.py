import socketio
import random
import time

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def response(data):
    print("Response from the server:", data)

@sio.event
def disconnect():
    print("Disconnected from the server")

def generate_random_data():
    # Generate random data for spot operations
    spotstatus = random.choice(["occupied", "available"])
    spotname = f"Spot-{random.randint(1, 100)}"
    spotdescription = f"This is {spotname}."
    sensorstatus = random.choice(["active", "inactive"])
    
    return {
        "spotstatus": spotstatus,
        "spotname": spotname,
        "spotdescription": spotdescription,
        "sensorstatus": sensorstatus
    }

def testspotops():
    while True:
        # Generate random data
        data = generate_random_data()
        # Emit the data to the server
        sio.emit('spotresops', data)
        # Wait for a moment before sending the next data
        time.sleep(2)  # Adjust the delay as needed

if __name__ == '__main__':
    sio.connect('http://localhost:5000')  # Replace with your server URL if different
    try:
        testspotops()
    except KeyboardInterrupt:
        print("Stopping the client...")
    finally:
        sio.disconnect()