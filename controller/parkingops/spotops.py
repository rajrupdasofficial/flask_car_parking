# spot operations
"""
detect per spot operations using websocket and evaluate if a car hasbeen present or not 
if the car is present then return message spot is occupied
"""
from flask_socketio import SocketIO,emit
from uuid import uuid4
import jwt
import os

from util.logs import generatelogs

def spotresops(socketio):
    @socketio.on('spotresops')
    def handel_spotops(data):
        print(f"Received data:{data}")
        try:
            spotstatus = data.get("spotstatus")
            spotname = data.get("spotname")
            spotdescription = data.get("spotdescription")
            sensorstatus = data.get("sensorstatus")
            # spotuid = data.get("spotuid")
            
            # response_messages = None
            # if spotstatus == "occupied":
            #     response_messages = "parking spot is occupied"
            token_data={
                'spotstatus':spotstatus,
                'spotname':spotname,
                'spotdescription':spotdescription,
                'spotuid':str(uuid4()),
                'sensorstatus':sensorstatus
            }
            token = jwt.encode(token_data,os.getenv('JWT_SECRET'),algorithm='HS256')
            messagetype='success'
            message= f"Spot Operations success {token_data}"
            filelocation = 'spotops.py'
            generatelogs(messagetype,message,filelocation)
            emit('response',{'status':'success','data':token_data,'tokendata':token})
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            messagetype='error'
            message=f"{e}"
            filelocation = 'spotops.py'
            generatelogs(messagetype,message,filelocation)
            emit('response',{'status':'error','data':str(e)})
        