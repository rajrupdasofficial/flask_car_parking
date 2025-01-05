from flask import Blueprint, jsonify, request
import os
import psycopg2
import logging

# Create a blueprint for expenses
expenses_bp = Blueprint('expenses', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@expenses_bp.route('/expenses', methods=['GET'])
def expenses():

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user details
        cursor.execute("SELECT uid, name FROM users")
        users_details = cursor.fetchall()

        # Create a map for quick lookup of user details by uid
        user_map = {user[0]: user[1] for user in users_details}

        # Fetch transaction details where userid matches any uid from users
        cursor.execute("SELECT paymentid, price, userid FROM transactionsdetails WHERE userid IN %s", (tuple(user_map.keys()),))
        transactions = cursor.fetchall()

        # Enrich transactions with corresponding usernames
        enriched_transactions = [
            {
                'paymentid': transaction[0],
                'price': transaction[1],
                'userid': transaction[2],
                'username': user_map.get(transaction[2], None)  # Get username or None if not found
            } for transaction in transactions
        ]

        # Send response back to client
        return jsonify({
            "transactions": enriched_transactions
        }), 200

    except Exception as error:
        print("Error fetching data:", error)
        return jsonify({"error": "An error occurred while fetching data."}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
