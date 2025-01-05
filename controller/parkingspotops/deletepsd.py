"""
delete a perticular parking spot from a parking location for example delete 
"ABS-220" parking sport from a total parking space "BNS-0"
"""
from flask import Blueprint, request, jsonify
import psycopg2
import os

from util.logs import generatelogs

deletepsd_bp = Blueprint('deletepsd_bp',__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@deletepsd_bp.route('/deletepsd',methods=['POST'])
def deletepsdfun():
    psdid = str(request.form.get('psdid'))

    if not psdid:
        messagetype='error'
        message=f"psdid is required to remove the item"
        filelocation = 'deletepsd.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":"psdid is required to remove the item"})
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM spotdetails WHERE = %s
            """,(psdid))
        cursor.execute()
        
        messagetype = "success"
        message = "Selected data hasbeen deleted successfully"
        filelocation = "deletepsd.py"
        generatelogs(messagetype,message,filelocation)

        return jsonify({"success":"Selected data hasbeen deleted successfully "})
    
    except Exception as e:
        print(f"error {e}")
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "deletepsd.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    
    finally:
        cursor.close()
        conn.close()