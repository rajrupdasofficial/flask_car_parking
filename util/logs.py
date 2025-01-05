"""
create logs
"""
import psycopg2
import os
from uuid import uuid4
import logging

logging.basicConfig(level=logging.INFO)
def getconn():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

def gen_uid():
    return str(uuid4())

def generatelogs(messagetype,message,filelocation):
    newuid = gen_uid()
    try:
        conn = getconn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO logs(id,messagetype,message,filelocation)
            VALUES( %s, %s, %s, %s)
            """,(newuid,messagetype,message,filelocation))
        conn.commit()
        print(f"messagetype - {messagetype}, message - {message}, filelocation - {filelocation}")
    except Exception as e:
        print(f"logging error {e}")
    # finally:
    #     cursor.close()