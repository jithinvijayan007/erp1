import requests
from bs4 import BeautifulSoup
import json
import psycopg2


# conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="tms@123")
conn = psycopg2.connect(host="localhost",database="myg_pos_live", user="admin", password="uDS$CJ8j")
conn.autocommit = True
cur = conn.cursor()


def location_master():
    res_data = requests.get('http://13.71.18.142:8086/api/master/Location')

    dct_data = res_data.json()
    for ins_data in dct_data:
        cur.execute("SELECT * FROM location_master WHERE int_code="+str(ins_data['Code'])+" and vchr_location='"+ins_data['Location']+"'")
        if not cur.fetchall():
            cur.execute("INSERT INTO location_master(int_code, vchr_location) VALUES("+str(ins_data['Code'])+",'"+ins_data['Location']+"')")
        else:
            cur.execute("UPDATE location_master set vchr_location='"+ins_data['Location']+"' where  int_code ="+str(ins_data['Code']))

    cur.close()
    conn.close()
location_master()
