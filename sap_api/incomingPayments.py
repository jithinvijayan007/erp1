import requests
import sys
import psycopg2
from bs4 import BeautifulSoup
import json
from datetime import datetime

def IncomingPayment(today):
    """
        Function to insert Incoming Payement Details into Receipt db_table.
            URL : "http://myg.tmicloud.net:85/POSOutbound.asmx/IncomingPayment?FDate=

            SAP_API_keys : DocDate,CardCode,DocTotal,JrnlMemo,BankCode,DocNum,CASH,CREDIT,CHECK1,TRANS
        return: 1
    """
    try:
        conn = None
        # conn = psycopg2.connect(host="localhost",database="pos_01_10",user="admin",password="tms@123")
        conn = psycopg2.connect(host="localhost",database="pos",user="admin",password="uDS$CJ8j")
        conn.autocommit = True
        cur = conn.cursor()

    except Exception as e:
            print('Cannot connect to database')
            return 0

    try:
        url = "http://myglive.tmicloud.net:8084/api/AdvanceDepositPayment?FDate="+str(today)
        res_data=requests.get(url)
        PARAMS = {'FDate':today}
        if res_data.status_code == 200:
            dct_data = res_data.json()
            if dct_data:
                print(dct_data)
                # ==========================================================================================================
                # To get customer id who exists in table corresponds to the CardCode in given data
                lst_cust_code = tuple([item['CardCode']for item in dct_data])
                #import pdb;pdb.set_trace()
                str_query = "select pk_bint_id,vchr_code from customer_details where vchr_code in ("+str(lst_cust_code)[1:-2]+");"
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
                    cur.execute("select vchr_receipt_num from receipt where vchr_receipt_num='"+data.get('DocNum')+"'")
                    if not cur.fetchone():
                        dat_issue = data.get('DocDate')[:10]
                        if not dct_customer.get(data['CardCode']):
                            lst_customer_not_exist.append(data.get('CardCode'))
                            continue
                        fk_customer_id = dct_customer[data['CardCode']]
                        dbl_amount =  data.get('DocTotal')
                        vchr_remarks = data.get('JrnlMemo')
                        fk_created_id = int_staff
                        int_doc_status = 0
                        dat_created = today
                        int_pstatus =  0
                        int_receipt_type = 5 # Financier
                        vchr_bank =  data.get('BankCode') if data['BankCode'] != None else ""
                        vchr_receipt_num =  data.get('DocNum')
                        vchr_check_num = data.get('CHECKNUM')
                        cur.execute("select dbl_credit_balance from customer_details where pk_bint_id='"+fk_customer_id+"'")
                        rst_cust_details = cur.fetchall()
                        if rst_cust_details:
                            total_balance = rst_cust_details[0][0]+dbl_amount
                            cur.execute("update customer_details set dbl_credit_balance="+str(total_balance)+" where pk_bint_id='"+fk_customer_id+"')
                        if data['CASH']:
                            int_fop = 1
                            insert_query = "INSERT INTO receipt (dat_issue,fk_customer_id,dbl_amount,vchr_remarks,fk_created_id,int_doc_status,dat_created,int_pstatus,int_receipt_type,vchr_bank,vchr_receipt_num,int_fop) VALUES('"+dat_issue+"',"+str(fk_customer_id)+","+str(dbl_amount)+",'"+vchr_remarks+"',"+str(fk_created_id)+",-1,'"+dat_created+"',1,"+str(int_receipt_type)+",'"+vchr_bank+"','"+str(vchr_receipt_num)+"',"+str(int_fop)+") RETURNING pk_bint_id"
                            cur.execute(insert_query)
                            receipt_id = cur.fetchone()
                            if receipt_id:
                                lst_inserted.append(receipt_id[0])
                        if data['CREDIT']:
                            int_fop = 3
                            insert_query = "INSERT INTO receipt (dat_issue,fk_customer_id,dbl_amount,vchr_remarks,fk_created_id,int_doc_status,dat_created,int_pstatus,int_receipt_type,vchr_bank,vchr_receipt_num,int_fop) VALUES('"+dat_issue+"',"+str(fk_customer_id)+","+str(dbl_amount)+",'"+vchr_remarks+"',"+str(fk_created_id)+",-1,'"+dat_created+"',1,"+str(int_receipt_type)+",'"+vchr_bank+"','"+str(vchr_receipt_num)+"',"+str(int_fop)+") RETURNING pk_bint_id"
                            cur.execute(insert_query)
                            receipt_id = cur.fetchone()
                            if receipt_id:
                                lst_inserted.append(receipt_id[0])
                        if data['CHECK1']:
                            int_fop = 4
                            insert_query = "INSERT INTO receipt (dat_issue,fk_customer_id,dbl_amount,vchr_remarks,fk_created_id,int_doc_status,dat_created,int_pstatus,int_receipt_type,vchr_bank,vchr_receipt_num,int_fop,vchr_card_num) VALUES('"+dat_issue+"',"+str(fk_customer_id)+","+str(dbl_amount)+",'"+vchr_remarks+"',"+str(fk_created_id)+",-1,'"+dat_created+"',1,"+str(int_receipt_type)+",'"+vchr_bank+"','"+str(vchr_receipt_num)+"',"+str(int_fop)+","+str(vchr_check_num)+") RETURNING pk_bint_id"
                            cur.execute(insert_query)
                            receipt_id = cur.fetchone()
                            if receipt_id:
                                lst_inserted.append(receipt_id[0])
                        if data['TRANS']: # NEFT
                            int_fop = 6
                            insert_query = "INSERT INTO receipt (dat_issue,fk_customer_id,dbl_amount,vchr_remarks,fk_created_id,int_doc_status,dat_created,int_pstatus,int_receipt_type,vchr_bank,vchr_receipt_num,int_fop) VALUES('"+dat_issue+"',"+str(fk_customer_id)+","+str(dbl_amount)+",'"+vchr_remarks+"',"+str(fk_created_id)+",-1,'"+dat_created+"',1,"+str(int_receipt_type)+",'"+vchr_bank+"','"+str(vchr_receipt_num)+"',"+str(int_fop)+") RETURNING pk_bint_id"
                            cur.execute(insert_query)
                            receipt_id = cur.fetchone()
                            if receipt_id:
                                lst_inserted.append(receipt_id[0])
                    else:
                        print("Data Exists")

                print('Total Count:',count)
                print('Inserted:',lst_inserted)
                print('list_customer_not_exist:',set(lst_customer_not_exist))

        return 1
    except Exception as e:
        print('Error:'+str(e))
        return 0


if __name__ == '__main__':
    str_date = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
    if len(sys.argv) >1:
        str_date = sys.argv[1]
    IncomingPayment(str_date)
