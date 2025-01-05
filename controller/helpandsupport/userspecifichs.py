"""
User specific history
"""
from flask import Blueprint,jsonify,request
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

userspecifichs_bp = Blueprint("userspecifichs_bp",__name__)

@userspecifichs_bp.route("/userspecifichs",methods=["POST"])
def userspecifichs():
    useremail = str(request.form.get("useremail"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * from HelpandSupport WHERE email = %s    
        """,(useremail,))

        result = cursor.fetchone()
        
        if result is None:
            return jsonify({"message":"No data hasbeen found"}),404
        
        messagetype = "success"
        message = "User specific help and support data hasbeen fetched"
        filelocation = "Userspecifichs.py"
        generatelogs(messagetype, message, filelocation)

        return jsonify({"message":"Help and support data hasbeen fetched successfully","data":result}),200        

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "Userspecifichs.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()