from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2
import logging

from util.logs import generatelogs

# Set up logging
logging.basicConfig(level=logging.INFO)

def conn():
    """Establish a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            dbname=config('DB_NAME'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            host=config('DB_HOST'),
            port=config('DB_PORT'),
            sslmode='require'
        )
        return connection
    except Exception as e:
        logging.error("Database connection failed: %s", e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "updatedetails.py"
        generatelogs(messagetype,message,filelocation) 
        return None

updatevehicle_bp = Blueprint('updatevehicle_bp', __name__)

@updatevehicle_bp.route('/updatevehicledata', methods=['POST'])
def updatedetails():
    userid = request.form.get("userid")
    carname = request.form.get('carname')
    licenseplatenum = request.form.get("licenseplatenumber")
    cartype = request.form.get("cartype")
    vehiclemodel = request.form.get('vehiclemodel')

    # Check if userid is provided
    if not userid:
        return jsonify({"error": "User ID is required"}), 400

    # Prepare the update fields
    update_fields = {}
    
    if licenseplatenum:
        update_fields['license_plate_number'] = licenseplatenum
    if carname:
        update_fields['car_name'] = carname
    if cartype:
        update_fields['cartype'] = cartype
    if vehiclemodel:
        update_fields['vehiclemodel'] = vehiclemodel

    # Check if there are fields to update
    if not update_fields:
        messagetype = "error"
        message = f"No fields to update"
        filelocation = "updatedetails.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": "No fields to update"}), 400

    # Check for existing license plate number if it's being updated
    if 'license_plate_number' in update_fields:
        existing_query = """
            SELECT COUNT(*) FROM vehicle 
            WHERE license_plate_number = %s AND user_uuid != %s;
        """
        try:
            connection = conn()
            if connection is None:
                messagetype = "error"
                message = f"Database connection error"
                filelocation = "updatedetails.py"
                generatelogs(messagetype,message,filelocation) 
                return jsonify({"error": "Database connection error"}), 500
            
            with connection.cursor() as cursor:
                cursor.execute(existing_query, (licenseplatenum, userid))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    messagetype = "error"
                    message = f"License plate number already exists."
                    filelocation = "updatedetails.py"
                    generatelogs(messagetype,message,filelocation) 
                    return jsonify({"error": "License plate number already exists."}), 400
        
        except Exception as e:
            logging.error("Error checking existing license plate: %s", e)
            messagetype = "error"
            message = f"Failed to check existing license plate."
            filelocation = "updatedetails.py"
            generatelogs(messagetype,message,filelocation)
            return jsonify({"error": "Failed to check existing license plate."}), 500
        
        finally:
            if connection:
                connection.close()

    # Construct the SQL query dynamically based on provided fields
    set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
    values = list(update_fields.values())

    # Add user ID for the WHERE clause
    values.append(userid)

    sql_query = f"""
        UPDATE vehicle 
        SET {set_clause} 
        WHERE user_uuid = %s;
    """

    try:
        connection = conn()
        if connection is None:
            messagetype = "error"
            message = f"Database connection error."
            filelocation = "updatedetails.py"
            generatelogs(messagetype,message,filelocation)
            return jsonify({"error": "Database connection error"}), 500
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query, values)
            connection.commit()
        messagetype = "success"
        message = f"Vehicle details updated successfully"
        filelocation = "updatedetails.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"success": "Vehicle details updated successfully"}), 200
    
    except Exception as e:
        logging.error("Error updating vehicle details: %s", e)
        
        # Log detailed error information
        if 'duplicate key value violates unique constraint' in str(e):
            messagetype = "error"
            message = f"Duplicate key value violation."
            filelocation = "updatedetails.py"
            generatelogs(messagetype,message,filelocation) 
            return jsonify({"error": "Duplicate key value violation."}), 400
        
        messagetype = "error"
        message = f"{e}"
        filelocation = "updatedetails.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": "Failed to update vehicle details"}), 500
    
    finally:
        if connection:
            connection.close()