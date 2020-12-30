from datetime import datetime
import requests
import json
import psycopg2
import sys
from psycopg2.extras import RealDictCursor

def freightDate():
    """
            Function to remove the returned items from grn details and branch stock details.
            return: Success

    """
    try:
        try:
            conn = None
            # conn = psycopg2.connect(host="localhost",database="pos_sap", user="admin", password="uDS$CJ8j")
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)
        except Exception as e:
            return 0


        # url = "http://myglive.tmicloud.net:8084/api/Freight"
        url = 'http://13.71.18.142:8086/api/Freight'
        # PARAMS = {'FDate':date}
        # res_data=requests.get(url=url,params=PARAMS)
        res_data=requests.get(url=url)
        if res_data.status_code == 200:
            dct_data = json.loads(res_data.text) # String to Json
            if dct_data:
                for data in dct_data:
                    lst_name_split = data['ExpnsName'].split('-')
                    str_category = lst_name_split[0]
                    str_tax_code = "'"+lst_name_split[1]+"'" if len(lst_name_split)>1 else 'null'
                    cur.execute("select * from freight where vchr_code='"+str(data['ExpnsCode'])+"'")
                    if cur.fetchall():
                        cur.execute("update freight set vchr_tax_code="+str_tax_code+",vchr_category='"+str_category+"' where vchr_code='"+str(data['ExpnsCode'])+"'")
                    else:
                        cur.execute("insert into freight (vchr_code,vchr_tax_code,vchr_category,int_status) values('"+str(data['ExpnsCode'])+"',"+str_tax_code+",'"+str_category+"',0)")
            else:
                print('no data')
                cur.close()
                conn.close()
                return 0
        cur.close()
        conn.close()
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))
        return 0

if __name__=='__main__':
    freightDate()
