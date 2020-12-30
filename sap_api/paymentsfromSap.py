import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import json
import time
import pandas as pd
# date = '2019-08-01'
def paymentsfromsap(date):
    """
    Used to pull mygoal data from SAP
    paramerters(to SAP):
    response(from SAP):suceess/failed
    """
    try:
        # import pdb; pdb.set_trace()
        time_start = time.time()
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="pos", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor()

        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})


        url = 'http://myg.tmicloud.net:85/POSOutbound.asmx/HO_Expense_Payment'

        PARAMS = {'FDate':date}
        # PARAMS = {'Fdate':'2019-10-10'}

        cur = conn.cursor()
        res_data=requests.get(url=url,params=PARAMS)

        if res_data.status_code == 200:
            soup = BeautifulSoup(res_data.text, "xml")
            str_data = soup.string
            if str_data:
                dct_data = json.loads(str_data)
                if dct_data:
                    for item in dct_data:
                        dbl_amount=item['SumApplied']
                        vchr_description=item['Descrip']
                        vchr_code=item['AcctCode']
                        doc_date=item['DocDate']
                        int_tran_id=item['TransId']
                        str_insert="INSERT INTO sap_payment (vchr_code,vchr_description,dbl_amount,int_type,int_tran_id,doc_date) VALUES ('"+str(vchr_code)+"','"+str(vchr_description)+"',"+str(dbl_amount)+','+'1'+','+str(int_tran_id)+",'"+str(doc_date).split('T')[0]+"')"
                        cur.execute(str_insert)


    except Exception as e:
        raise


if __name__ == '__main__':
    date = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
    if len(sys.argv) == 2:
        date = sys.argv[1]
    paymentsfromsap(date)
