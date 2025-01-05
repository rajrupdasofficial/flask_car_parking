"""
Dynamic razor pay ops 
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

dynamicrazorpay_bp = Blueprint("dynamicrazorpay_bp",__name__)

@dynamicrazorpay_bp.route()
def dynamicrazorpays():
    pass