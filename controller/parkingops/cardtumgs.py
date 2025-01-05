"""
Car presence detection using magnetic sensor.
"""
from flask_socketio import emit
import os
import psycopg2
import jwt
from util.logs import generatelogs

def get_db_connection():
    """Establish a database connection."""
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )

def cardtumgf(socketio):
    @socketio.on("cardtumgroute")
    def handle_cardtumgf(data):
        print(f"Received data: {data}")
        
        # Check if data is a dictionary
        if not isinstance(data, dict):
            error_message = "Received data is not in the expected format (dict)."
            print(error_message)
            generatelogs('error', error_message, 'cardtumgs.py')
            emit('response', {'status': 'error', 'message': error_message})
            return
        
        try:
            # Extract token from the received data
            clienttoken = data.get('token')
            if not clienttoken:
                raise ValueError("No token provided.")

            # Decode the JWT token
            decodetoken = jwt.decode(clienttoken, os.getenv("JWT_SECRET"), algorithms=['HS256'])

            # Prepare token data for response
            token_data = {
                'parkinglocation': decodetoken.get('parkinglocation'),
                'parkingarea': decodetoken.get('parkingarea'),
                'psno': decodetoken.get('psno'),
                'iscarpresent': decodetoken.get('iscarpresent'),
                'sensorid': decodetoken.get('sensorid'),
                'sensorstatus': decodetoken.get('sensorstatus'),
                'paymentstatus': decodetoken.get('paymentstatus')
            }

            # Re-encode the token if necessary (optional)
            new_token = jwt.encode(token_data, os.getenv("JWT_SECRET"), algorithm='HS256')

            # Log success message
            messagetype = 'success'
            message = f"Car detection and presence: {token_data}"
            filelocation = 'cardtumgs.py'
            generatelogs(messagetype, message, filelocation)

            # Emit success response back to client
            emit('response', {
                'status': 'success',
                'message': 'Car has been detected',
                'data': token_data,
                'new_token': new_token  # Send back the new token if applicable
            })

        except jwt.ExpiredSignatureError:
            error_message = "Token has expired."
            print(error_message)
            generatelogs('error', error_message, 'cardtumgs.py')
            emit('response', {'status': 'error', 'message': error_message})

        except jwt.InvalidTokenError as e:
            error_message = f"Invalid token: {str(e)}"
            print(error_message)
            generatelogs('error', error_message, 'cardtumgs.py')
            emit('response', {'status': 'error', 'message': error_message})

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            messagetype = 'error'
            message = f"{str(e)}"
            filelocation = 'cardtumgs.py'
            generatelogs(messagetype, message, filelocation)
            emit('response', {'status': 'error', 'message': str(e)})