from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import sys
def ItemImageAdd(str_date):
    """
        Function to add Item Image in POS from SAP API.
        URL : http://myglive.tmicloud.net:8084/api/ItemAttachment
        SAP_API_keys : AcctCode,AcctName,ActType

        ItemCode,ItemName,srcPath,FileName,FileExt
        return: Success
    """
    #------------not completed sudheer--------------
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="pos_main", user="admin", password="tms@123")
            conn.autocommit = True
        except Exception as e:
            return 0
        cur = conn.cursor()
        url = "http://myglive.tmicloud.net:8084/api/ItemAttachment?FDate="
        PARAMS = {'Fdate':str_date}
        res_data = requests.get(url=url,params=PARAMS)
        import pdb; pdb.set_trace()
        if res_data.status_code == 200:
            soup = BeautifulSoup(res_data.text, "xml")
            str_data = soup.string #   To get *list inside  , <string> *[] </string>
            dct_data = json.loads(str_data) # String to Json
            dat_created = datetime.now()
            # if dct_data:

    except Exception as e:
        conn.close()
        return 0

if __name__ == '__main__':
    str_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) >1:
        str_date = sys.argv[1]
    ItemImageAdd(str_date)
