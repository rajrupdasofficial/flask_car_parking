"""
Delete a user from the database
"""
from flask import Blueprint,jsonify,request
from decouple import config
import psycopg2

from util.logs import generatelogs

deleteuserdata_bp = Blueprint('deleteuserdata_bp',__name__)

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

@deleteuserdata_bp.route('/users/deleteuser',methods=['POST'])
def deleteuser():
    userid  = str(request.form.get('userid'))

    if not userid:
        return jsonify({"error":"User id required to remove user"})
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM users WHERE uuid = %s
                """,(userid))
        messagetype = "success"
        message = f"User with selected id hasbeen deleted"
        filelocation = "deleteuser.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"success":"User with selected id hasbeen deleted"}),200
    except Exception as e:
        print(f'error  {e}')
        messagetype = "error"
        message = f"error - {e}"
        filelocation = "deleteuser.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    
    finally:
        cursor.close()
        conn.close()