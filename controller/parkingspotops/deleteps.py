"""
wipe out a parking spot data
"""
from flask import Blueprint,jsonify,request
from decouple import config
import psycopg2

from util.logs import generatelogs

deleteps_bp = Blueprint("deleteps_bp",__name__)

def conn():
    """Establish a connection to the PostgreSQL"""
    connection = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    return connection

@deleteps_bp.route("/deleteps",metods=['POST'])
def deleteps():
    psid = str(request.form.get("psid"))
    if not psid:
        return jsonify({"error":"Selected parking spot hasbeen deleted successfully"})
    
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
            DELETE FROM parking_spot WHERE id = %s
            """,(psid))
        
        messagetype = "success"
        message = "Selected data hasbeen deleted successfully"
        filelocation = "deleteps.py"
        
        generatelogs(messagetype,message,filelocation)
        
        return jsonify({"success":"Selected data hasbeen deleted successfully"})
    except Exception as e:
        print(f"error {e}")
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "deleteps.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        conn.close()