"""
get all of the spot data to show in the admin section 
"""
from flask import Blueprint,request,jsonify
import psycopg2
import os


from util.logs import generatelogs

spotdetailsall_bp = Blueprint('spotdetailsall_bp',__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@spotdetailsall_bp.route('/spotdetailsall', methods=['GET'])
def spotdetailsall():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM spotdetails
        """)
        
        allthedetails = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        datos = [dict(zip(columns,allthedetail)) for allthedetail in allthedetails]
        messagetype='success'
        message=f"all data hasbeen fetched successfully"
        filelocation = 'spotdetailsall.py'
        generatelogs(messagetype,message,filelocation)

        return jsonify({"message":"all the data hasbeen fetched successfully","data":datos}),200

    except Exception as e:
        print(f"Error - {e}")

        messagetype='error'
        message=f"{e}"
        filelocation = 'spotdetailsall.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        conn.close()