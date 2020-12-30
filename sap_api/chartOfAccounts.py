from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2


def ChartOfAccount():
    """
            Function to add Accounts in POS from SAP API.

                URL : http://myglive.tmicloud.net:8084/api/master/ChartofAccounts
                SAP_API_keys : AcctCode,AcctName,ActType

            return: Success

    """
    try:

        try:
            conn = None
            # conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="tms@123")
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
        except Exception as e:
            return 0

        cur = conn.cursor()
        url = "http://13.71.18.142:8086/api/master/ChartofAccounts"
        res_data = requests.get(url)
        if res_data.status_code == 200:
            dct_data = res_data.json() # String to Json
            if dct_data:
                for item in dct_data:

                    cur.execute(" SELECT * FROM  chart_of_accounts WHERE vchr_acc_code='"+item['AcctCode']+"'")
                    ins_account = cur.fetchone()
                    if ins_account: # if AcctCode already exists
                        continue
                    else:
                        # Insert new data
                        str_query = " INSERT INTO chart_of_accounts(vchr_acc_code,vchr_acc_name) VALUES('"+item['AcctCode']+"','"+item['AcctName']+"')"
                        ins_account = cur.execute(str_query)
        cur.close()
        conn.close()
        return 1

    except Exception as e:
        cur.close()
        conn.close()
        return 0

if __name__ == '__main__':
     ChartOfAccount()
