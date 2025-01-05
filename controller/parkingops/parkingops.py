# from flask import Blueprint, request, jsonify
# import psycopg2
# from decouple import config
# import os
# from uuid import uuid4
# from flask_socketio import SocketIO, emit

# socketio = SocketIO()

# parking_bp = Blueprint('parking', __name__)

# def get_db_connection():
#     conn = psycopg2.connect(
#         dbname=os.getenv('DB_NAME'),
#         user=os.getenv('DB_USER'),
#         password=os.getenv('DB_PASSWORD'),
#         host=os.getenv('DB_HOST'),
#         port=os.getenv('DB_PORT')
#     )
#     return conn

# def generate_custom_random_uid():
#     return str(uuid4())

# @socketio.on('parkingoperationmanagement',namespace='/parking')
# def handle_parking_management(data):
#     print(f"Received data: {data}")  # Make sure you're receiving data correctly
#     try:
#         parkingspotav = data.get("parkingspotav")
#         iscarpresent = data.get("iscarpresent")
#         distancefromthecar = data.get("distancefromthecar")

#         if parkingspotav not in ['yes', 'no']:
#             response_message = "Invalid value for parkingspotav. Expected 'yes' or 'no'."
#         elif iscarpresent not in ['yes', 'no']:
#             response_message = "Invalid value for iscarpresent. Expected 'yes' or 'no'."
#         else:
#             if parkingspotav == 'yes' and iscarpresent == 'yes':
#                 response_message = "Parking spot is already occupied."
#             elif parkingspotav == 'yes' and iscarpresent == 'no':
#                 response_message = "Parking spot is available."
#             else:
#                 response_message = "Invalid input data."

#         print(f"Emitting response: {response_message}")  # Debug the message before emitting
#         emit('response', {'status': 'success', 'data': response_message})  # Emitting response
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         emit('response', {'status': 'error', 'data': str(e)})
