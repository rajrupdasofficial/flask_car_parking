"""
fetch all of the wallet data as admin

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

fetchwasadmin_bp = Blueprint("fetchwasadmin",__name__)

@fetchwasadmin_bp.route("/fetchwasadmin",methods=["POST"])
def fetchwasadmin():
    adminid = str(request.form.get('adminid'))
    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM wallet adminid = %s
        """,(adminid,))
        result = cursor.fetchall()
        if result is None:
            return jsonify({"error":"The data requested for is not found"})
        # stored_id,userid,balance,isrechargedone,rmbwu = result

        # normal_payload = {
        #     "uuid":stored_id,
        # }

                
        messagetype = "success"
        message = f"Data fetched successfully"
        filelocation = "fetchwasadmin.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message": "Data fetched successfully", "data": result})


    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"{e}"
        filelocation = "fetchwasadmin.py"
        generatelogs(messagetype, message, filelocation)        
        return jsonify({"error": str(e)}), 500
