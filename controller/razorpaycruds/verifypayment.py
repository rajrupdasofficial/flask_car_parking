from flask import Blueprint, jsonify, request
import os
import psycopg2
import uuid

verifypayment_bp = Blueprint('verifypayment', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@verifypayment_bp.route("/verifypayment", methods=['POST'])
def verifypayment():
    data = request.get_json() 
    razorpay_payment_id = str(data.get('razorpay_payment_id'))
    userid = str(data.get('userid'))
    walletid = str(data.get('walletid'))
    chargeruid = str(data.get('chargeruid'))
    price = str(data.get('price'))

    if razorpay_payment_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if the wallet exists
            cursor.execute("SELECT * FROM wallet WHERE id = %s", (walletid,))
            walletfind = cursor.fetchone()

            if not walletfind:
                return jsonify({"message": "Error: No wallet data found"}), 404

            # Check if the user exists in userProfile
            cursor.execute("SELECT uuid, username, email FROM users WHERE uuid = %s", (userid,))
            findAppUserProfile = cursor.fetchone()

            if not findAppUserProfile:
                return jsonify({"message": "No data found for user"}), 404

            # Calculate the new balance
            current_balance = float(walletfind[2])  # Assuming balance is at index 2
            new_balance = current_balance + float(price)

            # Update the wallet balance
            cursor.execute("""
                UPDATE wallet 
                SET balance = %s, isrechergedone = true, recharger_made_by_which_user = %s 
                WHERE id = %s
            """, (new_balance, userid, walletid))
            
            # Create a new record in the wallet recharge history table
            cursor.execute("""
                INSERT INTO walletreachargehistory (id, userassociatedid, previousbalance, balanceleft, addedbalance, numberofrecharge) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), userid, current_balance, new_balance, price, "1"))

            # Create a transaction record
            cursor.execute("""
                INSERT INTO transactiondetails (id, paymentid, userid, price, walletid) 
                VALUES (%s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), razorpay_payment_id, userid, price, walletid))

            conn.commit()

            return jsonify({
                "message": "Wallet recharge done",
                "actualprice": price,
                "transactionDetails": {
                    "paymentid": razorpay_payment_id,
                    "userid": userid,
                    "price": price,
                    "chargeruid": chargeruid,
                    "walletid": walletid,
                }
            }), 201
            
        except Exception as e:
            print(e)
            return jsonify({"message": f"Internal server error"- {e}}), 500
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    else:
        return jsonify({"message": "Missing payment ID"}), 400
