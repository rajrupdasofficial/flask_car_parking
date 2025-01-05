from flask import Blueprint, jsonify, request
from decouple import config
import psycopg2

from util.logs import generatelogs

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

deleteby_bp = Blueprint("delete_bp", __name__)

@deleteby_bp.route("/deletevehicle", methods=['POST'])
def deletevehicledata():
    vehicleuid = str(request.form.get("vehicleuid"))

    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM vehicle WHERE uuid = %s
                    """,
                    (vehicleuid,)  # Wrap vehicleuid in a tuple
                )
                connection.commit()  # Ensure changes are committed
        messagetype = "success"
        message = f"Vehicle data has been deleted successfully"
        filelocation = "deletebyid.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"success": "Vehicle data has been deleted successfully"})
    except Exception as e:
        print(f'Error: {e}')
        messagetype = "error"
        message = f"{e}"
        filelocation = "deletebyid.py"
        generatelogs(messagetype,message,filelocation) 
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()