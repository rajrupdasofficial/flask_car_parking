from flask import Blueprint, jsonify, request
import psycopg2
import logging
from decouple import config

from util.logs import generatelogs

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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

allusers_bp = Blueprint("allusers", __name__)

@allusers_bp.route("/users/allusers", methods=['GET'])
def getalldetails():
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT  uuid ,username, name,email FROM users
                """)
                
                # Fetch all results
                users = cursor.fetchall()
                
                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description]
                
                # Create a list of dictionaries for each user
                user_data = [dict(zip(columns, user)) for user in users]
                
                messagetype = "success"
                message = f"Data fetched successfully"
                filelocation = "getuserprofilebyuserid.py"
                generatelogs(messagetype,message,filelocation)
                
                return jsonify({"data":user_data}), 200
                
    except Exception as e:
        logging.error("Error retrieving all user data: %s", str(e))
        messagetype = "error"
        message = f"{e}"
        filelocation = "getuserprofilebyuserid.py"
        generatelogs(messagetype,message,filelocation)    
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()