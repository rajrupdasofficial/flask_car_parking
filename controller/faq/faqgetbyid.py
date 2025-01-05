"""
faq get by id 
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

faqgetbyid_bp = Blueprint("faqgetbyid", __name__)

@faqgetbyid_bp.route("/faqgetbyid", methods=['POST'])
def faqgetbyid():
    faqid = str(request.form.get("faqid"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Correctly format the parameter as a tuple
        cursor.execute("""
        SELECT * FROM faq WHERE id = %s
        """, (faqid,))  # Note the comma here

        result = cursor.fetchone()
        
        if result is None:
            return jsonify({"message": "No FAQ found with the given ID."}), 404
        
        messagetype = "success"
        message = "FAQ details retrieved successfully."
        filelocation = "faqgetbyid.py"
        
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"message": "FAQ has been fetched", "data": result}), 200
    
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "faqgetbyid.py"  # Updated to reflect the correct file
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()  # Close cursor first
        conn.close()    # Then close connection