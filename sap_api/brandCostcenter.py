import requests
import json
import psycopg2
from datetime import datetime
import sys
def pricelistfromsap(date):
    """
    Used to save price_list data to pos
    paramerters(to SAP):
    response(from SAP):suceess/failed
    """
    try:
        try:
            conn = None
            # conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="tms@123")
            conn = psycopg2.connect(host="localhost",database="myg_pos_live", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor()
        except Exception as e:
            print(str(e))

        url = 'http://13.71.18.142:8086/api/master/CostCenters'
        # PARAMS = {'Fdate':'2019-08-01'}
        PARAMS = {'FDate':date}

        res_data=requests.get(url=url,params=PARAMS)

        if res_data.status_code == 200:
            dct_data = res_data.json()
            if dct_data:
                lst_cost_center = [a for a in dct_data if a['DimName'].upper()=='BRAND']
                for brand in lst_cost_center:
                    str_query_data = "select pk_bint_id from brands where upper(vchr_name) = '"+brand['PrcName']+"'"
                    cur.execute(str_query_data)
                    rst_brand = cur.fetchall()

                    if rst_brand:
                        ins_brand_update = cur.execute("UPDATE brands SET vchr_code = '"+brand['PrcCode']+"' WHERE upper(vchr_name) = '"+brand['PrcName']+"' ")
                    else:
                        cur.execute("INSERT INTO brands(vchr_code,vchr_name,int_status) VALUES('"+brand['PrcCode']+"','"+brand['PrcName']+"',0)")
        cur.close()
        conn.close()
        return 1

    except Exception as e:
        cur.close()
        conn.close()
        raise


if __name__ == '__main__':
    date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) == 2:
        date = sys.argv[1]
    pricelistfromsap(date)
