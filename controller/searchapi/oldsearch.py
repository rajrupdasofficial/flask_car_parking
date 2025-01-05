

# """
# Search data
# """
# from flask import Blueprint, request,jsonify
# import psycopg2
# import os
# from util.logs import generatelogs
# import logging

# createsearchapi_bp = Blueprint("createsearchapi_bp",__name__)

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)

# # Database connection setup
# def get_db_connection():
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv('DB_NAME'),
#             user=os.getenv('DB_USER'),
#             password=os.getenv('DB_PASSWORD'),
#             host=os.getenv('DB_HOST'),
#             port=os.getenv('DB_PORT')
#         )
#         return conn
        
#     except Exception as e:
#         logging.error(f"Database connection error: {str(e)}")
#         raise

# @createsearchapi_bp.route("/createsearch", methods=["POST"])
# def createsearch():
#     searchquery = str(request.form.get("searchquery"))
    
#     if not searchquery:
#         return jsonify({"error": "Search query cannot be empty."}), 400

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Combined SQL query using JOIN
#         query = """
#         SELECT * FROM public.parking_spot
#         WHERE parking_spot_name ILIKE %s OR parking_spot_location ILIKE %s
#         """
        
#         # Using ILIKE for case-insensitive search
#         cursor.execute(query, (f'%{searchquery}%', f'%{searchquery}%'))
        
#         # Fetch results
#         results = cursor.fetchall()
        
#         # Convert results to a list of dictionaries
#         parking_spots = []
#         parking_spotd  = []
#         for row in results:
#             parking_spot_id = row[0]
#             print(parking_spot_id)
#             cursor.execute("""
#             SELECT * FROM public.spotdetails WHERE parkingspaceid = %s
#                            ORDER BY id ASC 
#             """,(parking_spot_id,))
#             ro = cursor.fetchall()
#             for r in ro:
#                 parking_spotd.append({
#                     "parking_spot_id":r[0],
#                     "spotname":r[1],
#                     "spotdetails":r[2],
#                     "spotbookingstatus":r[3],
#                     "length":r[5],
#                     "width":r[6],
#                     "type of vehicles":r[7]
#                 })
#             parking_spots.append({
#                 "parking_space_id": row[0],  # ID from parking_spot
#                 "parking_space_name": row[1],
#                 "parking_space_location": row[2],
#                 "length": row[3],
#                 "width": row[4],
#                 "total_spots": row[5],
#                 "free_spots": row[6],
#                 "occupied_spots": row[7],
#                 "latitude": row[8],
#                 "longitude": row[9],
#                 "address": row[10],
#                 "number_of_floors": row[14],
#                 "entry_gate_count": row[15],
#                 "exit_gate_count": row[16],
#             })
        
#         cursor.close()
#         conn.close()

#         return jsonify({"parkingspots":parking_spots,"parkingspotdetails":parking_spotd}), 200

#     except Exception as e:
#         logging.error(f"Error during search: {str(e)}")
#         return jsonify({"error": "An error occurred while searching."}), 500