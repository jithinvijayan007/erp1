import sys
import requests
import json
import psycopg2
from datetime import datetime
import time
from psycopg2.extras import RealDictCursor
import os
from sqlalchemy import create_engine
cla
    """    Used to send indirect discount details to sap    """
    try:
        time_start = time.time()
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="pos_ob", user="admin", password="$m3llyf!$h")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            return ({'status':'failed','reason':'cannot connect to database'})
