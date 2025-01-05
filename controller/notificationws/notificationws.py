"""
send notification and receive confirmation
"""
from flask_socketio import emit
import os
import uuid
import os
import jwt

from util.logs import generatelogs

def bookingconfchannel(socketio):
    @socketio.on('bookingconfchannel')
    def handel_operation(data):
        print(f"Received data:{data}")
        try:
            # parkingid = data.get("parkingid")
            parkingspotid = data.get("parkingspotid")
            detectionstatus = data.get("detectionstatus")
            confirmationstatus = data.get("confirmationstatus")
            if detectionstatus == "No" or None:
                emit("response",{'status':'rejected','message':'No car hasbeen'})
            if confirmationstatus == "No" or None:
                emit('response',{'status':'rejected','message':'Confirmation not accepted'})
            if confirmationstatus == 'Yes':
                emit('response',{'status':'accepted','message':'user request confirmed'})
            token_data = {
                'parkingid':str(uuid.uuid4()),
                'parkingspotid':parkingspotid,
                'detectionstatus':detectionstatus,
                'confirmationstatus':confirmationstatus
            }
            token = jwt.encode(token_data,os.getenv('JWT_SECRET'),algorithm='HS256')
            messagetype='success'
            message= f"Notification send success {token_data}"
            filelocation = 'spotops.py'
            generatelogs(messagetype,message,filelocation)
            emit('response',{'status':'success','data':token_data,'tokendata':token})
        except Exception as e:
            print(f"Error occurred : {str(e)}")
            messagetype='error'
            message=f"{e}"
            filelocation = 'spotops.py'
            generatelogs(messagetype,message,filelocation)
            emit('response',{'status':'error','data':str(e)})