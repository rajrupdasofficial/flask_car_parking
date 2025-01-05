"""
fetch all of the vehchicle data of a user under a admin
"""
from flask import Blueprint,jsonify,request
import psycopg2
import os
from util.logs import generatelogs




def get_db_conn():
    """Establish a connection to the PostgreSQL"""
    connection = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
    return connection

fetchvehicleadmin_bp = Blueprint("fetchvehicleadmin_bp",__name__)

@fetchvehicleadmin_bp.route("/fetchvehicleadmin",methods = ["POST"])
def fetchvehicleadmin():
    adminid = str(request.form.get('adminid'))

    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM vehicle WHERE adminid = %s
        """,(adminid,))
        result = cursor.fetchall()

        if result is None:
            return jsonify({"error":"The data requested for is not found"})
        uuid, car_name, license_plate_number, car_type, user_uuid, vehiclemodel = result

        normal_payload = {
         "uuid":uuid,
         "carname":car_name,
         "licenseplate":license_plate_number,
         "cartype":car_type,
         "useruuid":user_uuid,
         "vehiclemodel":vehiclemodel   
        }

            
        messagetype = "success"
        message = f"Data fetched successfully"
        filelocation = "fetchasadmin.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message": "Data fetched successfully", "data": normal_payload})

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "fetchasadmin.py"
        generatelogs(messagetype, message, filelocation)        
        return jsonify({"error": str(e)}), 500