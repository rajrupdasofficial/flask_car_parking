"""
get a parking spot details by it's id from database
"""

from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2
import base64
import os
import json

from util.logs import generatelogs

getpsbyid_bp = Blueprint("getpsbyid_bp", __name__)

def conn():
    """Establish a connection to the PostgreSQL database."""
    connection = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    return connection

@getpsbyid_bp.route("/getspotbyid", methods=['POST'])  # Changed to POST for compatibility with form data
def getpsbyid():
    psid = request.form.get('psid')  # Use form data for POST requests

    if not psid:
        return jsonify({"error": "Parking spot ID is required"}), 400
    
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM parking_spot WHERE id = %s
                    """,
                    (psid,)  # Pass as a tuple
                )
                result = cursor.fetchone()

                if result is None:
                    return jsonify({"error": "Parking spot not found"}), 404
                
                # Convert result to a dictionary for better response formatting
                columns = [desc[0] for desc in cursor.description]
                spot_data = dict(zip(columns, result))
                
                # Decode pictures from JSON and encode them in base64
                if 'pspicture' in spot_data and spot_data['pspicture']:
                    pspicture_json = json.loads(spot_data['pspicture'])
                    encoded_pictures = []  # List to hold encoded picture data

                    for picture in pspicture_json:
                        picture_path = picture['path']
                        if os.path.exists(picture_path):  # Check if the file exists
                            with open(picture_path, 'rb') as img_file:
                                encoded_data = base64.b64encode(img_file.read()).decode('utf-8')
                                encoded_pictures.append({
                                    "data": encoded_data  # Add base64 data here
                                })
                        else:
                            encoded_pictures.append({
                                "data": None  # Handle missing files gracefully
                            })

                    # Update the JSON field with base64 encoded data
                    spot_data['pspicture'] = encoded_pictures
                
                messagetype = "success"
                message = "Data fetched successfully"
                filelocation = "getpsbyid.py"
                generatelogs(messagetype,message,filelocation)
                
                return jsonify({"message": "Data fetched successfully", "data": spot_data}), 200
        
    except Exception as e:
        print(f"Error: {e}")  
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "getpsbyid.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": "An error occurred while fetching the parking spot."}), 500
    finally:
        cursor.close()