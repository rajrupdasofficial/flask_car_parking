"""
faq update 
"""
from flask import Blueprint,jsonify,request
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


faqupdate_bp = Blueprint("faqupdate",__name__)

@faqupdate_bp.route("/faqupdate",method=["POST"])
def updatefaq():
    faqid = str(request.form.get("faqid"))
    faqquestion = str(request.form.get("faqquestion"))
    faqdescription = str(request.form.get("faqdescription"))
    
    update_fields = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if faqquestion is not None:
            update_fields['faqquestion']=faqquestion
        if faqdescription is not None:
            update_fields['faqdescription'] = faqdescription
         # Check if there are any fields to update
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
        sql_query = f"""
        UPDATE faq
        SET {set_clause}
        WHERE id = %s        
        """
        values = list(update_fields.values()) + [faqid]

        cursor.execute(sql_query,values)
        conn.commit()

        return jsonify({"message":"faqs hasbeen updated successfully"}),200
        
    except Exception as e:
        print(e)
        messagetype = "error"
        message = f"Error - {str(e)}"
        filelocation = "faqcreate.py"
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500
    finally:
        conn.close()
        cursor.close()
    