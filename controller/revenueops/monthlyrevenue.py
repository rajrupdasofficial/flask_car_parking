from flask import Blueprint, jsonify
import psycopg2
from datetime import datetime, timedelta
import os

# Create a blueprint for revenue calculations
monthly_revenue_blueprint = Blueprint('monthly_revenue', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@monthly_revenue_blueprint.route('/monthlyrevenue', methods=['GET'])
def monthly_revenue():
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get today's date and calculate start and end of the month
        today = datetime.now()
        
        # Handle December case
        if today.month == 12:
            start_of_month = datetime(today.year, today.month, 1)
            end_of_month = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            start_of_month = datetime(today.year, today.month, 1)
            end_of_month = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)

        # Query to fetch records created this month
        query = """
            SELECT addedbalance FROM walletreachargehistory 
            WHERE created_at >= %s AND created_at <= %s;
        """
        cursor.execute(query, (start_of_month, end_of_month))
        
        # Fetch all records
        records = cursor.fetchall()

        # Calculate total revenue
        total_revenue = sum(float(record[0]) for record in records if record[0] is not None)

        # Send the total revenue as a response
        return jsonify({'data': total_revenue})

    except Exception as error:
        print(f"Error: {error}")
        return jsonify({'error': 'An error occurred while calculating monthly revenue.'}), 500

    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
