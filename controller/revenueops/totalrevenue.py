from flask import Blueprint, request, jsonify
import psycopg2
import logging
import os

# Create a blueprint for transaction details
total_revenue_bp = Blueprint('total_revenue_bp', __name__)


def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@total_revenue_bp.route('/total-revenue', methods=['POST'])
def total_revenue():
    user_id = str(request.form.get('userId'))  # Assuming userId is passed in the request body

    try:
        # Connect to the PostgreSQL database
         # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all records for the specified user
        query = """
            SELECT addedbalance FROM walletrechargehistory 
            WHERE userassociatedid = %s;
        """
        cursor.execute(query, (user_id,))
        
        # Fetch all records
        records = cursor.fetchall()

        # Calculate the total added balance by converting strings to floats
        total_added_balance = sum(float(record[0]) if record[0] is not None else 0 for record in records)

        # Log and return the result
        logging.info(f"Total added balance for user {user_id}: {total_added_balance}")

        return jsonify({'totalrevenues': total_added_balance}), 200

    except Exception as error:
        print(error)
        
        # Log error details
        logging.error(f"Error calculating total revenue for user {user_id}: {error}")

        return jsonify({'message': "Internal server error"}), 500

    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
