import requests
import sys
import psycopg2
from bs4 import BeautifulSoup
import json
from datetime import datetime

def FinancierPayment():
    """
        Function to insert Financier Payement Details into Receipt db_table.
            URL : "http://myg.tmicloud.net:85/POSOutbound.asmx/FinancierPayment
            SAP_API_keys : DocDate,CardCode,DocTotal,JrnlMemo,BankCode,DocNum,CASH,CREDIT,CHECK1,TRANS
        return: 1
    """
    try:
        conn = None
        conn = psycopg2.connect(host="localhost",database="pos_test",user="admin",password="uDS$CJ8j")
        conn.autocommit = True
        cur = conn.cursor()

    except Exception as e:
            print('Cannot connect to database')
            return 0

    try:
        url = "http://myg.tmicloud.net:85/POSOutbound.asmx/FinancierPayment"
        today = datetime.strftime(datetime.now(),'%Y-%m-%d')
        PARAMS = {'FDate':today}
        # PARAMS = {'Fdate':""} Uncomment for all data
        res_data=requests.get(url=url,params=PARAMS)
        if res_data.status_code == 200:
            soup = BeautifulSoup(res_data.text, "xml")
            str_data = soup.string
            if str_data:
                dct_data = json.loads(str_data)
                # ==========================================================================================================
                # To get customer id who exists in table corresponds to the CardCode in given data
                lst_cust_code = tuple([item['CardCode']for item in dct_data])
                str_query = "select pk_bint_id,vchr_code from customer_details where vchr_code in "+str(lst_cust_code)+";"
                cur.execute(str_query)
                lst_customer_details = cur.fetchall()
                dct_customer = {}
                if lst_customer_details:
                    dct_customer = {customer[1]:customer[0] for customer in lst_customer_details}
                else:
                    print('CardCode Not Exists')
                    return 0
                #  To get fk_created_id , here admin considered as fk_created
                cur.execute("select user_ptr_id from userdetails where fk_group_id = (select pk_bint_id from groups where vchr_name = 'ADMIN') limit 1;")
                tup_admin = cur.fetchone()
                if tup_admin:
                    int_staff = tup_admin[0]
                # ==========================================================================================================
                lst_inserted = []
                lst_customer_not_exist = []
                count = 0
                for data in dct_data:
                    count +=1
                    dat_issue = data['DocDate'][:10]
                    if not dct_customer.get(data['CardCode']):
                        lst_customer_not_exist.append(data['CardCode'])
                        continue
                    fk_customer_id = dct_customer[data['CardCode']]
                    dbl_amount =  data['DocTotal']
                    vchr_remarks = data['JrnlMemo']
                    fk_created_id = int_staff
                    int_doc_status = 0
                    dat_created = today
                    int_pstatus =  0
                    int_receipt_type = 5 # Financier
                    vchr_bank =  data['BankCode']
                    vchr_receipt_num =  data['DocNum']

                    if data['CASH']:
                        int_fop = 1
                    elif data['CREDIT']:
                        int_fop = 3
                    elif data['CHECK1']:
                        int_fop = 4
                    elif data['TRANS']: # NEFT
                        int_fop = 6

                    insert_query = "INSERT INTO receipt (dat_issue,fk_customer_id,dbl_amount,vchr_remarks,fk_created_id,int_doc_status,dat_created,int_pstatus,int_receipt_type,vchr_bank,vchr_receipt_num,int_fop) VALUES('"+dat_issue+"',"+str(fk_customer_id)+","+str(dbl_amount)+",'"+vchr_remarks+"',"+str(fk_created_id)+","+str(int_doc_status)+",'"+dat_created+"',"+str(int_pstatus)+","+str(int_receipt_type)+",'"+vchr_bank+"','"+str(vchr_receipt_num)+"',"+str(int_fop)+") RETURNING pk_bint_id"
                    cur.execute(insert_query)
                    receipt_id = cur.fetchone()
                    if receipt_id:
                        lst_inserted.append(receipt_id[0])

        print('Total Count:',count)
        print('Inserted:',lst_inserted)
        print('list_customer_not_exist:',set(lst_customer_not_exist))
        return 1
    except Exception as e:
        print('Error:'+str(e))
        return 0


if __name__ == '__main__':
    FinancierPayment()
    print('Inserted Successfully')
