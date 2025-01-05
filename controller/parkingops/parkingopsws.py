"""
parking spot management operation in realtime using websocket
"""

# websocket.py
from flask_socketio import SocketIO, emit

from util.logs import generatelogs

def register_socket_events(socketio):
    @socketio.on('parkingoperationmanagement')
    def handle_parking_management(data):
        print(f"Received data: {data}")  # Make sure you're receiving data correctly
        try:
            parkingspotav = data.get("parkingspotav")
            iscarpresent = data.get("iscarpresent")
            distancefromthecar = data.get("distancefromthecar")

            if parkingspotav not in ['yes', 'no']:
                response_message = "Invalid value for parkingspotav. Expected 'yes' or 'no'."
            elif iscarpresent not in ['yes', 'no']:
                response_message = "Invalid value for iscarpresent. Expected 'yes' or 'no'."
            else:
                if parkingspotav == 'yes' and iscarpresent == 'yes':
                    response_message = "Parking spot is already occupied."
                elif parkingspotav == 'yes' and iscarpresent == 'no':
                    response_message = "Parking spot is available."
                else:
                    response_message = "Invalid input data."

            print(f"Emitting response: {response_message}")  # Debug the message before emitting
            messagetype='success'
            message=f"Parking operations are working using websocket  {response_message}"
            filelocation = 'parkingopsws.py'
            generatelogs(messagetype,message,filelocation)
            emit('response', {'status': 'success', 'data': response_message})  # Emitting response
        except Exception as e:
            print(f"Error occurred: {e}")
            messagetype='error'
            message=f"{e}"
            filelocation = 'parkingopsws.py'
            generatelogs(messagetype,message,filelocation)
            emit('response', {'status': 'error', 'data': str(e)})