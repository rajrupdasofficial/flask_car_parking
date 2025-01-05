from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2
import uuid
import base64
import os
import json
from datetime import datetime, timedelta
import pytz
import jwt

from util.logs import generatelogs

updateps_bp = Blueprint('updateps_bp', __name__)

UPLOAD_FOLDER = os.path.join('uploads', 'parkingspot')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@updateps_bp.route("/updateps", methods=['POST'])
def updateps():
    psid = request.form.get('psid')
    
    # Validate required fields
    if not psid:
        return jsonify({"error": "ID is required"}), 400

    # Collecting fields to update
    update_fields = {}
    
    # Check for each field and add to update_fields if present
    for field in ['parking_spot_name', 'parking_spot_location', 'length', 'width',
                  'total_spots', 'free_spots', 'occupied_spots', 'latitude',
                  'longitude', 'address','number_of_floors','entry_gate_count','exit_gate_count']:
        value = request.form.get(field)
        if value is not None:
            update_fields[field] = value

    pspicture_data = []
    
    # Handle picture uploads
    if 'pspicture' in request.files:
        files = request.files.getlist('pspicture')  # Get list of uploaded files
        
        if len(files) > 10:
            messagetype = "error"
            message = "You cannot upload more than 10 pictures."
            filelocation = "updateps.py"
            generatelogs(messagetype,message,filelocation)
            return jsonify({"error": "You cannot upload more than 10 pictures."}), 400
        
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    new_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
                    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                    file.save(filepath)

                    # Store only the file path
                    pspicture_data.append({
                        "path": filepath
                    })
                    messagetype = "success"
                    message = "file appended successfully"
                    filelocation = "updateps.py"
                    generatelogs(messagetype,message,filelocation)
                except Exception as e:
                    messagetype = "error"
                    message = f"error - {e}"
                    filelocation = "updateps.py"
                    generatelogs(messagetype,message,filelocation)
                    return jsonify({"error": f"Failed to process file {file.filename}: {str(e)}"}), 500

    # Store only paths in the database (if needed)
    if pspicture_data:
        update_fields['pspicture'] = json.dumps(pspicture_data)  # Store paths as JSON string

    if not update_fields:
        return jsonify({"error": "No fields updated"}), 400
    
    set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
    
    sql_query = f"UPDATE parking_spot SET {set_clause} WHERE id = %s"
    
    values = list(update_fields.values())
    values.append(psid)

    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, values)
                connection.commit()

                cursor.execute("SELECT * FROM parking_spot WHERE id = %s", (psid,))
                updated_data = cursor.fetchone()
                
                if not updated_data:
                    messagetype = "error"
                    message = f"No data found after modification"
                    filelocation = "updateps.py"
                    generatelogs(messagetype,message,filelocation)
                    return jsonify({"error": "No data found after modification"}), 404
                
                # Convert result to a dictionary for better response formatting
                columns = [desc[0] for desc in cursor.description]
                spot_data = dict(zip(columns, updated_data))

                # Prepare base64 encoded data for response
                if 'pspicture' in spot_data and spot_data['pspicture']:
                    try:
                        pspicture_json = json.loads(spot_data['pspicture'])
                        for picture in pspicture_json:
                            picture_path = picture['path']
                            if os.path.exists(picture_path):  # Check if the file exists
                                with open(picture_path, 'rb') as img_file:
                                    picture['data'] = base64.b64encode(img_file.read()).decode('utf-8')
                            else:
                                picture['data'] = None  # Handle missing files gracefully

                        # Update the JSON field with base64 encoded data for response only
                        spot_data['pspicture'] = pspicture_json
                    except json.JSONDecodeError as e:
                        messagetype = "error"
                        message = f"Error - {e}"
                        filelocation = "updateps.py"
                        generatelogs(messagetype,message,filelocation)
                        return jsonify({"error": "Failed to decode pictures data"}), 500

                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_time = datetime.now(ist_timezone)
                
                # Create JWT token payload with expiration time in IST
                token_payload = {
                    'parking_spot_name': spot_data['parking_spot_name'],
                    'parking_spot_location': spot_data['parking_spot_location'],
                    'length': spot_data['length'],
                    'width': spot_data['width'],
                    'total_spots': spot_data['total_spots'],
                    'free_spots': spot_data['free_spots'],
                    'occupied_spots': spot_data['occupied_spots'],
                    'latitude': spot_data['latitude'],
                    'longitude': spot_data['longitude'],
                    'address': spot_data['address'],
                    'number_of_floors': spot_data['number_of_floors'],
                    'entry_gate_count': spot_data['entry_gate_count'],
                    'exit_gate_count':spot_data['exit_gate_count'],
                    'exp': (ist_time + timedelta(hours=1)).timestamp()
                }
                
                token = jwt.encode(token_payload, config('JWT_SECRET'), algorithm='HS256')

                messagetype = "success"
                message = "data updated successfully"
                filelocation = "updateps.py"
                generatelogs(messagetype,message,filelocation)
                
                return jsonify({
                    "message": "Data has been updated successfully",
                    "token": token,
                    "updated_data": spot_data  # Return updated parking spot data including pictures
                }), 200

    except Exception as e:
        print(f"Error -- {e}")
        messagetype = "error"
        message = f"Error - {e}"
        filelocation = "updateps.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()