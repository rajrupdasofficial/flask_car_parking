from flask import Blueprint, jsonify, request
import psycopg2
import os
from util.logs import generatelogs

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

createhps_bp = Blueprint("createhps", __name__)

@createhps_bp.route("/createhps", methods=['POST'])
def createhpsfun():
    required_fields = [
        "name", "email", "phonenumber", "message", "associatedadminid"
    ]
    
    form_data = {field: request.form.get(field) for field in required_fields}
    
    # Check for missing fields
    for field, value in form_data.items():
        if value is None:
            return jsonify({"error": f"Missing field: {field}"}), 400
        
    name = str(form_data["name"])
    email = str(form_data["email"])
    phonenumber = str(form_data["phonenumber"])
    message = str(form_data["message"])
    associatedadminid = str(form_data["associatedadminid"])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO HelpandSupport (name, email, phonenumber, message, adminid)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, phonenumber, message, associatedadminid))
        
        conn.commit()
        
        messagetype = "success"
        message = "Help and Support has been created successfully"
        filelocation = "createhelpandsupport.py"
        
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message": "Help and support has been created successfully"}), 200

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "createhelpandsupport.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
