import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import sys
from datetime import datetime
# from django.conf import settings


#/branch/addBranchfromsap' app url
#AddBranchFromSap() class name

def ShowRoomDataFromSap(date):
    try:
        conn = None
        conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
        #conn = psycopg2.connect(host="localhost",database="pos_blank", user="admin", password="nisam@123")
        conn.autocommit = True
    except Exception as e:
        return 0
    try:

        # df

        # url = settings.BI_HOSTNAME+'/branch/addBranchfromsap'
        url="http://mygoal.biz:5555/branch/addBranchfromsap/" #please comment when production
        # date ='2019-12-01'
        dict_bi_data={}
        list_bi_data=[]
        cur = conn.cursor()
        str_url = 'http://13.71.18.142:8086/api/master/Warehouse'
        PARAMS = {'Fdate':date}
        res_data = requests.get(str_url,params=PARAMS)
        import pdb;pdb.set_trace()
        lst_data = res_data.json()
        lst_known_keys = ['InaugurationDate','U_TYPE','Longitude', 'GSTRegnNo', 'U_CATEGORY', 'U_TERRITORY', 'StoreEmail', 'StoreCode', 'U_REGION', 'Latitude', 'StockLimit', 'Location', 'U_STATUS', 'StorePhone', 'StoreName', 'StoreAddress']
        lst_unknown_keys = ['Space']

        # str_query_exists = "select pk_bint_id from company_details where vchr_code = 'MYG';"
        # cur.execute(str_query_exists)
        # fk_company_id = cur.fetchall()


        for dct_data in lst_data:
            if dct_data['StoreCode']!='MCOW':
                #import pdb;pdb.set_trace()
                continue
            dict_bi_data ={}
            vchr_branch_code = dct_data['StoreCode']
            str_territory="null"
            dct_data['StateCode'] = dct_data['StateCode'] if dct_data['StateCode'] else 'KL'
            if dct_data['Territory']:
                str_territory=dct_data['Territory']
            cur.execute(" SELECT pk_bint_id FROM states WHERE vchr_code = '"+dct_data['StateCode']+"'")
            int_states = cur.fetchone()

            if int_states:
                fk_state = int_states[0]
            else:
                cur.execute("SELECT pk_bint_id FROM states WHERE vchr_code = 'KL'")
                int_states = cur.fetchone()
                if int_states:
                    fk_state = int_states[0]

            if vchr_branch_code:
                str_query_exists = "select * from branch where vchr_code = '"+vchr_branch_code+"';"
                cur.execute(str_query_exists)
                ins_branch_exists = cur.fetchall()
                if not ins_branch_exists:
                    dat_inauguration = 'null'
                    int_type = 1
                    if dct_data['Type']=='WAREHOUSE':
                        int_type = 3
                    elif dct_data['Type']=='HEAD OFFICE':
                        int_type = 2
                    flt_latitude = 'null'
                    flt_longitude = 'null'
                    str_email = 'null'
                    str_name = 'null'
                    str_address = 'null'
                    str_phone = 'null'
                    bint_stock_limit = 'null'
                    str_code = vchr_branch_code
                    fk_location_master_id = 'null'
                    gst_no = dct_data.get('GSTNo') or 'null'

                    if dct_data['InaugurationDate']:
                        dat_inauguration = "'"+dct_data['InaugurationDate']+"'"
                    if dct_data['StoreName']:
                        str_name = "'"+dct_data['StoreName']+"'"
                    if dct_data['StoreAddress']:
                        str_address = "'"+dct_data['StoreAddress']+"'"
                    if dct_data['StoreEmail']:
                        str_email = "'"+dct_data['StoreEmail']+"'"
                    if dct_data['StorePhone']:
                        str_phone = "'"+dct_data['StorePhone']+"'"
                    if dct_data['Latitude']:
                        flt_latitude = "'"+dct_data['Latitude']+"'"
                    if dct_data['Longitude']:
                        flt_longitude = "'"+dct_data['Longitude']+"'"
                    if dct_data['StockLimit']:
                        bint_stock_limit = "'"+dct_data['StockLimit']+"'"

                    vchr_location_master = dct_data['Location']
                    cur.execute("select pk_bint_id from location_master where upper(vchr_location) = '"+str(vchr_location_master.upper())+"';")
                    ins_location_master = cur.fetchall()
                    if ins_location_master:
                        fk_location_master_id = ins_location_master[0][0]

                    str_query_insert = "INSERT INTO branch (vchr_code,vchr_name,vchr_address,vchr_email,vchr_phone,bint_stock_limit,flt_latitude,flt_longitude,dat_inauguration,fk_location_master_id,vchr_gstno,fk_states_id,int_type) VALUES ('"+str_code+"',"+str_name+","+str_address+","+str_email+","+str_phone+","+bint_stock_limit+","+flt_latitude+","+flt_longitude+","+dat_inauguration+","+str(fk_location_master_id)+",'"+str(gst_no)+"',"+str(fk_state)+","+str(int_type)+")"
                    cur.execute(str_query_insert)
                else:
                    dat_inauguration = 'null'
                    int_type = 1
                    if dct_data['Type']=='WAREHOUSE':
                        int_type = 3
                    elif dct_data['Type']=='HEAD OFFICE':
                        int_type = 2
                    flt_latitude = 0
                    flt_longitude = 0
                    str_email = 'null'
                    str_name = 'null'
                    str_address = 'null'
                    str_phone = 'null'
                    bint_stock_limit = 'null'
                    str_code = vchr_branch_code
                    fk_location_master_id = 'null'

                    if dct_data['InaugurationDate']:
                        dat_inauguration = "'"+dct_data['InaugurationDate']+"'"
                    if dct_data['StoreName']:
                        str_name = "'"+dct_data['StoreName']+"'"
                    if dct_data['StoreAddress']:
                        str_address = "'"+dct_data['StoreAddress']+"'"
                    if dct_data['StoreEmail']:
                        str_email = "'"+dct_data['StoreEmail']+"'"
                    if dct_data['StorePhone']:
                        str_phone = "'"+dct_data['StorePhone']+"'"
                    if dct_data['Latitude']:
                        flt_latitude = dct_data['Latitude']
                    if dct_data['Longitude']:
                        flt_longitude = dct_data['Longitude']
                    if dct_data['StockLimit']:
                        bint_stock_limit = dct_data['StockLimit']

                    gst_no = dct_data.get('GSTNo') or 'null'
                    vchr_location_master = dct_data['Location']
                    cur.execute("select pk_bint_id from location_master where upper(vchr_location) = '"+str(vchr_location_master.upper())+"';")
                    ins_location_master = cur.fetchall()
                    if ins_location_master:
                        fk_location_master_id = ins_location_master[0][0]
                    str_query_insert = """UPDATE branch set vchr_name="""+str_name+""",vchr_address="""+str_address+""",vchr_email="""+str_email+""",vchr_phone="""+str_phone+""",bint_stock_limit="""+str(bint_stock_limit)+""",flt_latitude="""+str(flt_latitude)+""",flt_longitude="""+str(flt_longitude)+""",dat_inauguration="""+str(dat_inauguration)+""",fk_location_master_id="""+str(fk_location_master_id)+""",vchr_gstno='"""+gst_no+"""',fk_states_id="""+str(fk_state)+""",int_type="""+str(int_type)+""" where vchr_code='"""+vchr_branch_code+"""'"""
                    cur.execute(str_query_insert)
                dict_bi_data['StoreCode']=dct_data['StoreCode']
                dict_bi_data['StoreName']=str_name
                dict_bi_data['StroreAddress']=str_address
                dict_bi_data["Email"]=str_email
                dict_bi_data["phone"]=str_phone
                dict_bi_data['flt_latitude']=flt_latitude
                dict_bi_data['flt_longitude']=flt_longitude
                dict_bi_data["TerritoryName"]=str_territory
                list_bi_data.append(dict_bi_data)
        cur.close()
        conn.close()
        if list_bi_data:
            res_post_data = requests.post(url,json={"branch_data":list_bi_data})
            print(res_post_data.text)


    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))
        return 0

if __name__ == '__main__':
    str_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) >1:
        str_date = sys.argv[1]
    ShowRoomDataFromSap(str_date)
