from flask import Blueprint, jsonify, request
import jwt
import psycopg2
import os
from util.logs import generatelogs
import base64

getspotdetailsbyid_bp = Blueprint('getspotdetailsbyid_bp', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@getspotdetailsbyid_bp.route('/getspotdetailsbyid', methods=['POST'])
def spotdetailsbyid():
    spotid = request.form.get("spotid")
    parkingspaceid = request.form.get("parkingspaceid")
    
    # Check if at least one of the parameters is provided
    if not spotid and not parkingspaceid:
        return jsonify({"error": "At least one of 'spotid' or 'parkingspaceid' must be provided"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM spotdetails WHERE "
        conditions = []
        parameters = []

        # Build query based on provided parameters
        if spotid and spotid.lower() != 'none':
            conditions.append("id = %s")
            parameters.append(spotid)
        
        if parkingspaceid and parkingspaceid.lower() != 'none':
            conditions.append("parkingspaceid = %s")
            parameters.append(parkingspaceid)

        if not conditions:
            return jsonify({"error": "Both 'spotid' and 'parkingspaceid' cannot be invalid."}), 400

        query += " OR ".join(conditions)

        cursor.execute(query, tuple(parameters))
        
        result = cursor.fetchone()
        
        if result is None:
            messagetype = 'error'
            message = f"No associated booking found for the given criteria."
            filelocation = 'getspotdetailsbyid.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "No associated booking found"}), 404
        
        qrcodepath = result[9] if result[9] else None  # Assuming index 9 contains the QR code path
        
        # Initialize qrcodedata as None
        qrcodedata = None
        
        # Check if QR code path is valid before checking existence
        if qrcodepath and os.path.exists(qrcodepath):
            with open(qrcodepath, "rb") as img_file:
                try:
                    qrcodedata = base64.b64encode(img_file.read()).decode('utf-8')
                except Exception as e:
                    return jsonify({"error": f"Failed to encode QR code: {str(e)}"}), 500
        else:
            qrcodepath = None  # Set to None if QR code path does not exist

        result_dict = {
            'id': result[0],
            'spotname': result[1],
            'spotdetails': result[2],
            'spotbookingstatus': result[3],
            'parkingspaceid': result[4],
            'length': result[5],
            'width': result[6],
            'typeofvehicles': result[7],
            'adminid': result[8],
            'qrcode': qrcodedata  # Include the base64 encoded QR code here or None
        }

        messagetype = 'success'
        message = "Data fetched successfully"
        filelocation = 'getspotdetailsbyid.py'
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message": "Data fetched successfully", "data": result_dict})
    
    except Exception as e:
        messagetype = 'error'
        message = f"Error - {str(e)}"
        filelocation = 'getspotdetailsbyid.py'
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()
