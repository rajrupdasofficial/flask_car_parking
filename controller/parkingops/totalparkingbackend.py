"""
total parking solution

parking operation demonstration using websocket 

realtime data evaluation using machine learning model
"""
from flask_socketio import emit
import joblib
import os
import pandas as pd
import psycopg2
from uuid import uuid4

from util.logs import generatelogs


def get_db_connection():
    """Establish a database connection."""
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password= os.getenv('DB_PASSWORD'),
        host= os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )



# Load the trained model once at startup
model_path = 'vehicle_presence_model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)

def totalparkingsol(socketio):
    @socketio.on('totalparkingsol')
    def handle_total_ops(data):
        print(f"Received data: {data}")
        try:
            # Extracting data from the incoming JSON object
            pkspname = data.get("pkspname") 
            pkspno = data.get("pkspno")
            distance = data.get("distance")
            signal_strength = data.get("signal_strength", 0)  # Default value if not provided
            type_magnetic = data.get("type_Magnetic", 0)      # Default value if not provided
            type_ultrasonic = data.get("type_Ultrasonic", 0)   # Default value if not provided
            
            # Prepare input for prediction with all necessary features
            input_data = pd.DataFrame([[
                distance,
                signal_strength,
                type_magnetic,
                type_ultrasonic
            ]], columns=['distance_measurement', 'signal_strength', 'type_Magnetic', 'type_Ultrasonic'])
            
            # Make prediction using the loaded model
            prediction = model.predict(input_data)
            
            # Interpret prediction result
            carpresence = 'Present' if prediction[0] == 1 else 'Not Present'
            
            #save the live data in data base
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO dandp(id,pkspname,pkspno,distance,signal_strength,type_magnetic,type_ultrasonic,carpresence)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """,(
                (str(uuid4()),pkspname,pkspno,distance,signal_strength,type_magnetic,type_ultrasonic,carpresence)
            ))
            conn.commit()

            messagetype='success'
            message=f"parking operation is working realtime {carpresence}"
            filelocation = 'totalparkingbackend.py'
            generatelogs(messagetype,message,filelocation)
            # Emit the result back to the client
            emit('response', {
                'pkspname': pkspname,
                'pkspno': pkspno,
                'carpresence': carpresence
            })
        
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            messagetype='error'
            message=f"{e}"
            filelocation = 'totalparkingbackend.py'
            generatelogs(messagetype,message,filelocation)
            emit('error', {'message': str(e)})
        # finally:
        #     cursor.close()
        #     conn.close()
