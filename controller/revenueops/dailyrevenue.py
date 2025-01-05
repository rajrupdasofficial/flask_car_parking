from flask import Blueprint, jsonify
import psycopg2
from datetime import datetime, timedelta
import os

# Create a blueprint for revenue calculations
today_revenue_blueprint = Blueprint('today_revenue', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


@today_revenue_blueprint.route('/todayrevenue', methods=['GET'])
def today_revenue():
    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get today's date and set start and end of the day
        today = datetime.now()
        start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
        end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)

        # Query to fetch records created today
        query = """
            SELECT addedbalance FROM walletreachargehistory 
            WHERE created_at >= %s AND created_at <= %s;
        """
        cursor.execute(query, (start_of_day, end_of_day))
        
        # Fetch all records
        records = cursor.fetchall()

        # Calculate total revenue
        total_revenue = sum(float(record[0]) for record in records if record[0] is not None)

        # Send the total revenue as a response
        return jsonify({"message": "Here is the total revenue for today", "data": total_revenue})

    except Exception as error:
        print(f"Error: {error}")
        return jsonify({'error': 'An error occurred while calculating revenue.'}), 500

    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
