"""
Update wallet details

"""
from flask import Blueprint, jsonify, request
import os
import psycopg2
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

updatewallet_bp = Blueprint('updatewalletdetails', __name__)

@updatewallet_bp.route("/updatewallet", methods=["POST"])
def updatewallet():
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = {}
    walletid = str(request.form.get("walletid"))
    balance = str(request.form.get("balance"))
    userid = str(request.form.get("userid"))
    adminid = str(request.form.get("adminid"))

    # Validate required fields
    if not walletid:
        return jsonify({"error": "Wallet ID is required"}), 400

    # Prepare fields for update
    if balance is not None:
        update_fields['balance'] = balance
    if userid is not None:
        update_fields['userid'] = userid
    if adminid is not None:
        update_fields['adminid'] = adminid

    # Check if there are any fields to update
    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    # Construct the SQL UPDATE statement dynamically
    set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
    
    sql_query = f"""
        UPDATE wallets 
        SET {set_clause} 
        WHERE walletid = %s
    """
    
    values = list(update_fields.values()) + [walletid]

    try:
        cursor.execute(sql_query, values)
        conn.commit()
        
        # Log the successful update
        messagetype = "success"
        message = f"Wallet updated successfully"
        filelocation = "updatewallet.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"message": "Wallet updated successfully"}), 200

    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "updatewallet.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500

    finally:
        cursor.close()
        conn.close()