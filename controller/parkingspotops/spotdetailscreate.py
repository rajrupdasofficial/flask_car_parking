from flask import Blueprint, request, jsonify
import psycopg2
import os
from uuid import uuid4
import qrcode
from util.logs import generatelogs

createspotdetails_bp = Blueprint('createspotdetails_bp', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

# Function to generate a custom random UID
def generate_custom_random_uid():
    return str(uuid4())

@createspotdetails_bp.route('/createspotdetails', methods=['POST'])
def createspotdetails():
    required_fields = [
        'spotname', 'spotdetails', 'spotbookingstatus', 'parkingspaceid', 'length', 'width', 'typeofvehicles', 'adminid'
    ]
    form_data = {field: request.form.get(field) for field in required_fields}
    
    # Check for missing fields
    for field, value in form_data.items():
        if value is None:
            return jsonify({"error": f"Missing field: {field}"}), 400

    spotname = str(form_data['spotname'])
    spotdetails = str(form_data['spotdetails'])
    spotbookingstatus = str(form_data['spotbookingstatus'])
    parkingspaceid = str(form_data['parkingspaceid'])
    length = str(form_data['length'])
    width = str(form_data['width'])
    typeofvehicles = str(form_data['typeofvehicles'])
    adminid = str(form_data['adminid'])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count how many times spot details have been created for this parkingspaceid
        cursor.execute("""
            SELECT COUNT(*) FROM spotdetails WHERE parkingspaceid = %s
        """, (parkingspaceid,))
        count_spot_details = cursor.fetchone()[0]

        # Get the total spots available for the given parkingspaceid
        cursor.execute("""
            SELECT total_spots FROM parking_spot WHERE id = %s
        """, (parkingspaceid,))
        total_spots_result = cursor.fetchone()

        if total_spots_result is None:
            return jsonify({"error": "Invalid parkingspaceid."}), 400
        
        total_spots = total_spots_result[0]

        # Check if the count exceeds total spots
        if int(count_spot_details) >= int(total_spots):
            return jsonify({"error": "Cannot create more spot details than available spots."}), 400

        new_uid = generate_custom_random_uid()
        
        # Generate QR code with relevant information
        qr_data = {
            "spotdetailsid": new_uid,
            "spotname": spotname,
            "spotdetails": spotdetails,
            "spotbookingstatus": spotbookingstatus,
            "parkingspaceid": parkingspaceid,
            "length": length,
            "width": width,
            "typeofvehicles": typeofvehicles,
            "adminid": adminid
        }
        
        qr_code_img = qrcode.make(str(qr_data))
        
        # Save QR code image to a file (customize the path as needed)
        qr_code_path = f"uploads/qrcodes/{new_uid}.png"
        qr_code_img.save(qr_code_path)

        # Insert new spot details into the database including qrcode_path
        cursor.execute("""
            INSERT INTO spotdetails (id, spotname, spotdetails, spotbookingstatus, parkingspaceid, length, width, typeofvehicles, adminid, qrcodes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_uid,
            spotname,
            spotdetails,
            spotbookingstatus,
            parkingspaceid,
            length,
            width,
            typeofvehicles,
            adminid,
            qr_code_path  # Save the QR code path here
        ))
        
        conn.commit()

        messagetype = "success"
        message = "New parking spot details data has been inserted successfully"
        
        generatelogs(messagetype, message, "spotdetailscreate.py")
        
        return jsonify({"message": "Spot details have been created successfully", "qr_code_path": qr_code_path})
    
    except Exception as e:
        messagetype = "error"
        message = f"Error - {e}"
        
        generatelogs(messagetype, message, "spotdetailscreate.py")
        
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

@createspotdetails_bp.route('/getspotdetails/<spot_id>', methods=['GET'])
def get_spot_details(spot_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to retrieve spot details including QR code path
        cursor.execute("""
            SELECT * FROM spotdetails WHERE id = %s
        """, (spot_id,))
        
        spot_details = cursor.fetchone()

        if not spot_details:
            return jsonify({"error": "Spot not found."}), 404
        
        # Assuming spot_details is a tuple with all columns
        response = {
            "id": spot_details[0],
            "spotname": spot_details[1],
            "spotdetails": spot_details[2],
            "spotbookingstatus": spot_details[3],
            "parkingspaceid": spot_details[4],
            "length": spot_details[5],
            "width": spot_details[6],
            "typeofvehicles": spot_details[7],
            "adminid": spot_details[8],
            "qrcode_path": spot_details[9]  # Retrieve the QR code path
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()
