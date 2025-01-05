from flask import Blueprint, jsonify, request
import os
import psycopg2
import random
import razorpay
import logging
import traceback

from util.logs import generatelogs

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Set up Razorpay client
razorpay_client = razorpay.Client(auth=(os.getenv("RAZOR_PAY_KEY"), os.getenv("RAZOR_PAY_SECRET")))

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn
def create_payment(payment_details):
    # Destructure required fields from payment_details
    customer_name = payment_details['name']
    customer_email = payment_details['email']
    price = payment_details['price']

    print("Razorpay captured price", price)

    # Create an order in Razorpay
    order_data = {
        "amount": price * 100,  # Amount in paise (multiply by 100 to convert to paise)
        "currency": "INR",
        "receipt": f"receipt_{random.randint(1000, 9999)}",  # Unique receipt ID
        "notes": {
            "address": 'Amount for wallet recharge'  # Use customerAddress for address if needed
        }
    }

    try:
        order = razorpay_client.order.create(data=order_data)

        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()

        # Insert payment details into the database (example table structure)
        insert_query = """
            INSERT INTO payments (order_id, customer_name, customer_email, amount, currency)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (order['id'], customer_name, customer_email, order['amount'], order['currency']))
        conn.commit()

        # Return order details to the caller
        return {
            "id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "key_id": os.getenv("RAZOR_PAY_KEY"),
            "name": 'Transmogrify Global Pvt. Ltd',
            "description": 'Payment for Total Revenue',
            "image": 'https://cdn.statically.io/img/transmogriffy.com/wp-content/uploads/2022/03/TWLD5456.jpg?w=1280&quality=100&f=auto',
            "prefill": {
                "name": customer_name,
                "email": customer_email,
                "contact": '',  # Assuming contact is not provided; you may want to add this if available
            },
            "theme": {
                "color": "#F37254"
            }
        }
    except Exception as e:
        print('Error creating payment:', e)
        raise Exception(f"Payment creation failed - {str(e)}")  # More informative error message
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Blueprint setup for wallet recharge
initwalletrecharge_bp = Blueprint('initwalletrecharge', __name__)

@initwalletrecharge_bp.route('/initwalletrecharge', methods=['POST', 'OPTIONS'])
def initwalletrecharge():
    if request.method == 'OPTIONS':
        response = jsonify({"message": "CORS preflight response"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    data = request.get_json()  # Use get_json() to handle JSON data
    userid = str(data.get("userid"))
    walletid = str(data.get("walletid"))
    price = float(data.get("price"))

    if price <= 0.0:
        messagetype = "error"
        message = "Price must be greater than zero"
        filelocation = "initwalletrecharge.py"
        generatelogs(messagetype, message, filelocation)
        return jsonify({"message": message}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM wallet WHERE id = %s    
        """, (walletid,))
        
        walletfind = cursor.fetchone()
        
        if not walletfind:
            messagetype = "error"
            message = "Error: No data found"
            filelocation = "initwalletrecharge.py"
            generatelogs(messagetype, message, filelocation)
            return jsonify({"message": message}), 404
        
        cursor.execute("""
            SELECT name, email FROM users WHERE uuid = %s
        """, (userid,))
        
        finduser = cursor.fetchone()
        
        if not finduser:
            messagetype = "error"
            message = "Error: User not found"
            filelocation = "initwalletrecharge.py"
            generatelogs(messagetype, message, filelocation)
            return jsonify({"message": message}), 404
        
        paymentdetails = {
            "name": finduser[0],
            "email": finduser[1],
            "price": price
        }
        
        # Calling the payment intent function and handling potential errors
        try:
            order_details = create_payment(paymentdetails)  # Call create_payment here
            
            messagetype = "success"
            message = "Wallet recharge done"
            
            return jsonify({"message": message, "order_details": order_details})

        except Exception as e:
            logging.error(f"Payment creation failed: {str(e)}", exc_info=True)  # Log detailed error information
            return jsonify({"message": str(e)}), 500

    except Exception as e:
        logging.error(f"Error in initwalletrecharge: {str(e)}", exc_info=True)  # Log error with traceback
        messagetype = "error"
        message = "An error occurred during processing."
        
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message": str(e)}), 500
