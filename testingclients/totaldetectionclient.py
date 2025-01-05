"""
Total detection
"""
import socketio
import random
import time
import pandas as pd

# Create a Socket.IO client
sio = socketio.Client()

# Define the event handler for when the connection is established
@sio.event
def connect():
    print("Connected to the server.")

# Define the event handler for receiving prediction results
@sio.event
def response(data):
    print(f"Prediction Result: Car Presence: {data['carpresence']} (Space: {data['pkspname']} {data['pkspno']})")

# Define the event handler for errors
@sio.event
def error(data):
    print(f"Error: {data['message']}")

# Define the event handler for disconnection
@sio.event
def disconnect():
    print("Disconnected from the server.")

def generate_random_distance():
    # Generate a random distance between 0 and 100 meters
    return random.uniform(0, 100)

def test_parking_spot_operations():
    pkspname = "Parking A"
    pkspno = "1"
    
    while True:
        # Generate a random distance
        distance = generate_random_distance()
        
        # Prepare data for emission
        data_to_send = {
            'pkspname': pkspname,
            'pkspno': pkspno,
            'distance': distance,
            'signal_strength': random.uniform(0, 100),  # Example value; adjust as necessary
            'type_Magnetic': random.choice([0, 1]),     # Example binary feature; adjust as necessary
            'type_Ultrasonic': random.choice([0, 1])     # Example binary feature; adjust as necessary
        }

        # Check if all required features are present before emitting
        required_features = ['distance', 'signal_strength', 'type_Magnetic', 'type_Ultrasonic']
        
        if all(feature in data_to_send for feature in required_features):
            sio.emit('totalparkingsol', data_to_send)
        else:
            print("Error: Missing required features.")

        # Wait for a moment before sending the next data
        time.sleep(0.05)  # Adjust the delay as needed

if __name__ == '__main__':
    sio.connect('http://localhost:5000')  # Change this URL if your server runs on a different host/port
    try:
        test_parking_spot_operations()
    except KeyboardInterrupt:
        print("Stopping the client...")
    finally:
        sio.disconnect()