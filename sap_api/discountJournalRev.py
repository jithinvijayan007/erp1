import sys
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
from datetime import datetime
import time
from psycopg2.extras import RealDictCursor
import os
from sqlalchemy import create_engine
def discountJournal():
    """    Used to send indirect discount details to sap    """
    try:
        time_start = time.time()
        try:
            conn = None
            # conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="tms@123")
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            return ({'status':'failed','reason':'cannot connect to database'})
        cur.execute("select array_agg(int_document_id) from sap_api_track where int_type=16 and int_status!=2")
        # str_account_code="select coa.vchr_acc_code,coa.vchr_acc_name from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where int_status=0 and fk_branch_id="
        rst_id = cur.fetchall()
        dct_master_data = {}
#        import pdb;pdb.set_trace()
        str_account_code="select coa.vchr_acc_code,coa.vchr_acc_name from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.bint_id where int_status=0 and fk_branch_id="
        if rst_id:
            for int_id in rst_id[0]['array_agg']:
                str_id = str(int_id)
                cur.execute("select sd.fk_sales_id as master_id,sd.pk_bint_id as detail_id,sd.dbl_indirect_discount as discount_amount,cust.vchr_code as cust_code,cust.vchr_name as card_name,cust.fk_state_id as cust_state,cust.txt_address as cust_address,sm.dat_invoice::DATE as dat_invoice,sm.dat_created::DATE as dat_created,br.pk_bint_id as branch_id,br.vchr_code as branch_code,locm.int_code as location_code,sm.vchr_invoice_num as journal_num from sales_return sd join sales_master sm on sm.pk_bint_id = sd.fk_sales_id join branch br on br.pk_bint_id = sm.fk_branch_id join sales_customer_details cust on cust.pk_bint_id=sm.fk_customer_id join location_master locm on locm.pk_bint_id = br.fk_location_master_id  and sm.pk_bint_id ="+str_id+";")
                dct_discount = cur.fetchall()
                # dct_discount = dict(ins_discount)
                dct_master_data = {}
                for data in dct_discount:
                    if data['master_id'] not in dct_master_data:
                        dct_master_data[data['master_id']] = {}
                        dct_master_data[data['master_id']]['branch_code'] = data['branch_code']
                        dct_master_data[data['master_id']]['dat_invoice'] = data['dat_invoice']
                        dct_master_data[data['master_id']]['dat_created'] = data['dat_created']
                        dct_master_data[data['master_id']]['journal_num'] = data['journal_num']
                        dct_master_data[data['master_id']]['debit_acc_name'] = data['cust_name'] if data['cust_code'] else 'Cash'
                        dct_master_data[data['master_id']]['debit_acc_code'] = data['cust_code'] if data['cust_code'] else 'CASH'
                        dct_master_data[data['master_id']]['details'] = {}
                        dct_master_data[data['master_id']]['details'][data['detail_id']] = {}
                        dct_master_data[data['master_id']]['details'][data['detail_id']]['discount_amount'] = data['discount_amount']
                        dct_master_data[data['master_id']]['details'][data['detail_id']]['location_code'] = data['location_code']
                    elif data['detail_id'] not in dct_master_data[data['master_id']]['details']:
                        dct_master_data[data['master_id']]['details'][data['detail_id']] = {}
                        dct_master_data[data['master_id']]['details'][data['detail_id']]['discount_amount'] = data['discount_amount']
                        dct_master_data[data['master_id']]['details'][data['detail_id']]['location_code'] = data['location_code']

                dct_master={}
                for ins_data in dct_master_data:

                    dct_master = {}
                    dct_master['Header'] = []
                    dct_master['Line Level'] = []

                    dct_header = {}
                    dct_header['Reference'] = ins_data or ""
                    dct_header['MYGOAL_KEY'] = dct_master_data[ins_data]['journal_num']
                    dct_header['ShowRoomID'] = dct_master_data[ins_data]['branch_code']
                    dct_header['BranchID'] = 1 if dct_header['ShowRoomID'] !='AGY' else 2
                    dct_header['DocDate'] = datetime.strftime(dct_master_data[ins_data]['dat_invoice'],'%Y-%m-%d')
                    dct_header['RefDate'] = datetime.strftime(dct_master_data[ins_data]['dat_created'],'%Y-%m-%d')

                    dct_master['Header'].append(dct_header)
                    for ins_detail in dct_master_data[ins_data]['details']:
                        dct_line_data = {}
                        dct_line_data['CreditAcctCode'] =  "701130101003"
                        dct_line_data['CreditAcctName'] = "Discount Voucher Given A/c"
                        dct_line_data['Credit'] = dct_master_data[ins_data]['details'][ins_detail]['discount_amount']
                        dct_line_data['DebitAcctCode'] = dct_master_data[ins_data]['debit_acc_code']
                        dct_line_data['DebitAcctName'] = dct_master_data[ins_data]['debit_acc_name']
                        dct_line_data['Store'] = dct_master_data[ins_data]['branch_code']
                        dct_line_data['Department'] = "SAL"
                        dct_line_data['Brand'] = ""
                        dct_line_data['Employee'] = ""
                        dct_line_data['Debit'] = dct_master_data[ins_data]['details'][ins_detail]['discount_amount']
                        dct_line_data['LocCode'] = dct_master_data[ins_data]['details'][ins_detail]['location_code']

                        dct_master['Line Level'].append(dct_line_data)
                url = 'http://13.71.18.142:8086/api/In/JournalEntry'
                data=json.dumps(dct_master)
                headers = {"Content-type": "application/json"}
                res_data = requests.post(url,data,headers=headers)
                cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='pushed' where int_document_id ="+str_id+" and int_type=16")
                response = json.loads(res_data.text)
                if str(response['status']).upper() =='SUCCESS':
                    cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=16")
                else:
                    cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=16")
            return
    except Exception as e:
        raise





if __name__ == '__main__':
    discountJournal()
