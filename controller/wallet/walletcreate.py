from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import os
import psycopg2
import logging
import uuid

from util.logs import generatelogs

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        sslmode='require'
    )

walletcreate_bp = Blueprint('walletcreate', __name__)

@walletcreate_bp.route('/createwallet', methods=['POST'])
def createwallet():
    userid = str(request.form.get("userid"))
    balance = "0"
    associatedadminid = 'yyyy'  # Consider making this dynamic if needed

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if a wallet already exists for the given userid
        cursor.execute("""
            SELECT COUNT(*) FROM wallet WHERE userid = %s
        """, (userid,))
        wallet_count = cursor.fetchone()[0]
        
        if wallet_count > 0:
            # Log message for existing wallet
            messagetype = "error"
            message = "Wallet already exists for this user"
            filelocation = "walletcreate.py"
            generatelogs(messagetype, message, filelocation)
            
            return jsonify({"error": "A wallet already exists for this user."}), 409
        
        # Insert new wallet data if no existing wallet found
        cursor.execute("""
            INSERT INTO wallet(id, userid, balance, adminid)
            VALUES (%s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),  # Ensure UUID is a string
            userid,
            balance,
            associatedadminid
        ))
        
        conn.commit()
        
        # Log success message
        messagetype = "success"
        message = "New wallet data has been inserted successfully"
        filelocation = "walletcreate.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message": "Wallet data has been created successfully"}), 201
    
    except Exception as e:
        # Log error message
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "walletcreate.py"
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Ensure resources are released properly
        if cursor:
            cursor.close()
        if conn:
            conn.close()