from flask import Blueprint, jsonify, request
import psycopg2
import os

from util.logs import generatelogs

updatepsd_bp = Blueprint('updatepsd_bp', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@updatepsd_bp.route('/updatepsd', methods=['POST'])
def updatedetails():
    required_fields = ['id']
    form_data = {field: request.form.get(field) for field in required_fields}
    
    # Check for missing ID
    if form_data['id'] is None:
        return jsonify({"error": "Missing field: id"}), 400

    spoid = str(form_data['id'])
    
    # Prepare for optional fields
    optional_fields = [  'spotname', 'spotdetails', 'spotbookingstatus', 'parkingspaceid','length','width','typeofvehicles']
    update_fields = {}
    
    for field in optional_fields:
        value = request.form.get(field)
        if value is not None:
            update_fields[field] = str(value)

    if not update_fields:
        return jsonify({"error": "No fields to update."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build the SQL query dynamically
        set_clause = ', '.join([f"{field} = %s" for field in update_fields.keys()])
        sql_query = f"UPDATE spotdetails SET {set_clause} WHERE id = %s"
        
        # Execute the update query with parameters
        cursor.execute(sql_query, list(update_fields.values()) + [spoid])
        
        # Commit the changes
        conn.commit()
        
        messagetype = "success"
        message = "data updated successfully"
        filelocation = "updatepsd.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"message": "Spot details updated successfully."}), 200
    
    except Exception as e:
        messagetype = "error"
        message = f"Error - {e}"
        filelocation = "updateps.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()