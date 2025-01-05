# location_create.py
from flask import Blueprint, jsonify, request
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        sslmode='require'
    )

location_create_bp = Blueprint("location_create", __name__)

@location_create_bp.route("/add_location", methods=["POST"])
def add_location():
    state_name = str(request.form.get("statename"))
    city_name = str(request.form.get("cityname"))
    location_name = str(request.form.get("locationname"))
    local_address = str(request.form.get("localaddress", ""))  # Default to empty string if not provided

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the district already exists
        cursor.execute("SELECT id FROM state WHERE name = %s;", (state_name,))
        district_id = cursor.fetchone()

        if district_id is None:
            # Insert the district if it does not exist
            cursor.execute("""
                INSERT INTO state (name)
                VALUES (%s)
                RETURNING id;
            """, (state_name,))
            state_id = cursor.fetchone()[0]  # Get the newly created district ID
        else:
            state_id = district_id[0]  # Use existing district ID

        # Check if the city already exists in the same district
        cursor.execute("SELECT id FROM city WHERE name = %s AND districtid = %s;", (city_name, district_id))
        city_id = cursor.fetchone()

        if city_id is None:
            # Insert the city if it does not exist
            cursor.execute("""
                INSERT INTO city (name, districtid)
                VALUES (%s, %s)
                RETURNING id;
            """, (city_name, district_id))
            city_id = cursor.fetchone()[0]  # Get the newly created city ID
        else:
            city_id = city_id[0]  # Use existing city ID

        # Insert the new location into the database
        cursor.execute("""
            INSERT INTO location (name, city_id, localaddress, districtid)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            location_name,
            city_id,
            local_address,
            state_id
        ))
        locationid = cursor.fetchone()[0]
        conn.commit()

        return jsonify({"message": "Location has been successfully created","id":locationid}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
