"""
access gps sensor 
"""
from gpsdclient import GPSDClient

with GPSDClient(host="127.0.0.1") as client:
    for result in client.dict_stream(filter=["TPV"]):
        print("Latitude: %s" % result.get("lat", "n/a"))
        print("Longitude: %s" % result.get("lon", "n/a"))