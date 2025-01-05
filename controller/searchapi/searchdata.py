from flask import Blueprint, request, jsonify
import psycopg2
import os
import logging

# Create blueprints
search_bp = Blueprint("search_bp", __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database connection setup
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
        
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise


@search_bp.route("/search/city", methods=["POST"])
def search_city_or_state():
    searchquery = str(request.form.get("searchquery"))
    
    if not searchquery:
        return jsonify({"error": "Search query cannot be empty."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the search query matches a state
        cursor.execute("""
            SELECT id, name FROM state WHERE name ILIKE %s;
        """, (f'%{searchquery}%',))

        state_results = cursor.fetchall()

        response_data = []

        if state_results:
            # If it's a state, get its ID and count of cities in that state
            for state in state_results:
                state_id = state[0]
                state_name = state[1]

                # Count cities in the found state
                cursor.execute("""
                    SELECT * FROM city WHERE districtid = %s;
                """, (state_id,))
                
                cityname = cursor.fetchall()
                
                

                response_data.append({
                    "type": "state",
                    "id": state_id,
                    "name": state_name,
                    "city_name": cityname  # Number of cities in this state
                })

        # Now search for cities matching the query
        cursor.execute("""
            SELECT 'city' AS type, id, name FROM city WHERE name ILIKE %s;
        """, (f'%{searchquery}%',))

        city_results = cursor.fetchall()
        
        for row in city_results:
            response_data.append({
                "type": row[0],  # 'city'
                "id": row[1],
                "name": row[2]
            })

        if not response_data:
            return jsonify({"error": "No matching city or state found."}), 404

        return jsonify({"results": response_data}), 200

    except Exception as e:
        logging.error(f"Error during search: {str(e)}")
        return jsonify({"error": "An error occurred while searching."}), 500




@search_bp.route("/search/location", methods=["POST"])
def search_location():
    # Retrieve optional parameters from the request
    searchquery = str(request.form.get("searchquery", ""))
    city_id = request.form.get("city_id")
    districtid = request.form.get("districtid")

    # Validate that at least one parameter is provided
    if not searchquery and not city_id and not districtid:
        return jsonify({"error": "At least one search parameter must be provided."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build the base query and parameters list
        query = """
            SELECT id, name, localaddress, city_id, districtid FROM location 
            WHERE 1=1
        """
        params = []

        # Add conditions based on provided parameters
        if searchquery:
            query += " AND (name ILIKE %s OR localaddress ILIKE %s)"
            params.extend([f'%{searchquery}%', f'%{searchquery}%'])

        if city_id:
            query += " AND city_id = %s"
            params.append(city_id)

        if districtid:
            query += " AND districtid = %s"
            params.append(districtid)

        # Execute the constructed query
        cursor.execute(query, tuple(params))
        
        locations = cursor.fetchall()
        
        if not locations:
            return jsonify({"error": "No matching locations found."}), 404
        
        # Convert results to a list of dictionaries
        location_list = [{
            "location_id": row[0],
            "name": row[1],
            "localaddress": row[2],
            "city_id": row[3],
            "districtid": row[4]
        } for row in locations]

        return jsonify({"locations": location_list}), 200

    except Exception as e:
        logging.error(f"Error during location search: {str(e)}")
        return jsonify({"error": "An error occurred while searching for locations."}), 500

@search_bp.route("/search/parking_spots", methods=["POST"])
def get_parking_spots():
    location_ids = request.form.get("searchquery")  # Expecting a single string of location IDs separated by commas
    parking_spot_name = request.form.get("parking_spot_name")  # New optional parameter
    parking_spot_location = request.form.get("parking_spot_location")  # New optional parameter
    
    if not location_ids and not parking_spot_name and not parking_spot_location:
        return jsonify({"error": "At least one search parameter must be provided."}), 400
    
    # Split the location IDs into a tuple for SQL query
    # location_ids_tuple = tuple(location_ids.split(',')) if location_ids else None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Base query
        query = """
            SELECT * FROM parking_spot 
            WHERE 1=1
        """
        params = []

        # Add conditions based on provided parameters
        if location_ids:
            query += "AND locationid ILIKE %s"
            params.append(f'%{location_ids}%')

        if parking_spot_name:
            query += " AND parking_spot_name ILIKE %s"  # Correct column name
            params.append(f'%{parking_spot_name}%')

        if parking_spot_location:
            query += " AND parking_spot_location ILIKE %s"  # Correct column name
            params.append(f'%{parking_spot_location}%')

        # Execute the constructed query
        cursor.execute(query, tuple(params))
        
        parking_spots = cursor.fetchall()

        # Convert results to a list of dictionaries
        parking_spot_list = []
        
        for spot in parking_spots:
            parking_spot_list.append({
                "parking_spot_id": spot[0],
                "parking_spot_name": spot[1],  # Correct field name in response
                "parking_spot_location": spot[2],  # Correct field name in response
                # Add other relevant fields as necessary
            })

        cursor.close()
        conn.close()

        return jsonify({"parking_spots": parking_spot_list}), 200

    except Exception as e:
        logging.error(f"Error during fetching parking spots: {str(e)}")
        return jsonify({"error": "An error occurred while fetching parking spots."}), 500
