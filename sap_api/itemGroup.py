from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2

def ItemGroupAdd():
    """
            Function to add Item Group in POS from SAP API.
                URL : http://myglive.tmicloud.net:8084/api/master/Itemgroup
                SAP_API_keys : AcctCode,AcctName,ActType
            return: Success
    """
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="pos", user="admin", password="uDS$CJ8j")
            # conn = psycopg2.connect(host="localhost",database="pos_sap", user="admin", password="tms@123")
            conn.autocommit = True
        except Exception as e:
            return 0
        cur = conn.cursor()
        url = "http://myglive.tmicloud.net:8084/api/master/Itemgroup"
        res_data = requests.get(url)
        if res_data.status_code == 200:
            dct_data = res_data.json() # String to Json
            dat_created = datetime.now()
            if dct_data:
                cur.execute("select pk_bint_id from category where vchr_name='DEFAULT2'")
                rst_category = cur.fetchall()
                ins_category=None
                if rst_category:
                    ins_category=rst_category[0][0]
                for item in dct_data:
                    int_type=0
                    if item['ItemClass']==1:
                        int_type=1

                    cur.execute(" select * from  products where upper(vchr_name)='"+item['ItmsGrpNam'].upper()+"'")
                    ins_item_group = cur.fetchall()
                    if ins_item_group:
                        str_query = "UPDATE products set vchr_code='"+str(item['ItmsGrpCod'])+"',int_type="+str(int_type)+" where upper(vchr_name)='"+item['ItmsGrpNam'].upper()+"'"
                        ins_item_group = cur.execute(str_query)
                    else:
                        str_query = "INSERT INTO products(vchr_name,vchr_code,dat_created,int_status,fk_category_id,int_type,int_sales) VALUES('"+item['ItmsGrpNam']+"','"+str(item['ItmsGrpCod'])+"','"+str(dat_created)+"',0,"+str(ins_category)+","+str(int_type)+",0)"
                        ins_item_group = cur.execute(str_query)
                conn.close()
                return 1
        cur.close()
        conn.close()
    except Exception as e:
        conn.close()
        return 0

if __name__ == '__main__':
    ItemGroupAdd()
