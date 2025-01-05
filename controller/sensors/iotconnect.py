"""
IOT based data saved 
"""
from flask import Blueprint, jsonify,request
from decouple import config
import psycopg2
from psycopg2 import sql
import re

iotcon_bp = Blueprint('iotconnect',__name__)



def conn():
    """Establish a database connection."""
    return psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )


@iotcon_bp.route('/iotcon',methods=['POST'])
def iotconn():
    data = request.json
    mac_address=data.get('mac_address')
    gps_coordinates=data.get('gps_coordinates')
    ip_address = data.get('ip_address')
    try:
        with conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
            INSERT INTO iotconnectors(mac_address,gps_coordinates,ip_address)
                               VALUES(%s,%s,%s)
            """,(mac_address,gps_coordinates,ip_address))
            connection.commit()
        return jsonify({"message":"iot data hasbeen saved successfully"}),201
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
    