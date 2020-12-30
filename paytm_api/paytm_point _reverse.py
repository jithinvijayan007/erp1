import requests
from datetime import datetime,timedelta
import psycopg2
import psycopg2.extras
import json


HOST =  'localhost'
USER = 'admin'
PORT = 5432
DATABASE = 'fahad_pos4'
PASSWORD = 'tms@123'

OUT_BOND_URL  = "http://mqst.mloyalpos.com/Service.svc/REVERSE_POINTS_BY_TRANSACTION_ID"
HEADER = {'userid':'mob_usr','pwd':'@pa$$w0rd'}

time_filter = datetime.now() - timedelta(minutes=45)
# import pdb; pdb.set_trace()

try:
    con = psycopg2.connect(host = HOST,
    user = USER,
    port = PORT,
    database= DATABASE,
    password = PASSWORD)

    cursor = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    QUERY = "select vchr_ref_num as ref,pk_bint_id as id from paytm_point_data where int_status = 0 and dat_created >= '"+str(time_filter)+"'"
    cursor.execute(QUERY)
    dct_data = cursor.fetchall()
    if dct_data:
        for ref_num in dct_data:
            dct_data = {'objClass':{"transaction_id":ref_num['ref']}}
            pytm_request = requests.post(OUT_BOND_URL,json =dct_data,headers = HEADER)
            if pytm_request.status_code == 200:
                pytm_request = pytm_request.json()['REVERSE_POINTS_BY_TRANSACTION_IDResult']
                if pytm_request['Success']:
                    QUERY = "update paytm_point_data set int_status = -1 where pk_bint_id = "+str(ref_num['id'])
                    cursor.execute(QUERY)

except Exception as e:
    print('error')
finally:
    con.close()
    