from sqlalchemy import create_engine
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor

def vendorExpense(str_entry,doc_date):
    """
        Function to pass Advance/Deposit Refund Details to SAP by POST method.
        param: Payment pk_bint_id
            SAP_API_Arg : Master:- MYGOAL_KEY,ShowRoomID,CardCode,CardName,MobileNo,IDProofNo,CustAddr,Amount,DocDate,IsDeposit,TransactionType,Type
                            Details:-BankName,AdvanceReceiptNo,TranId,PaymentMode,Currency,Exchangerate,Amount,TransferDate,ChequeNum,LocCode
            SAP_API_return :Success
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
            raise
        #import pdb; pdb.set_trace()
        cur.execute("select array_agg(int_document_id) from sap_api_track where int_type=7 and int_status in ("+str_entry+") and dat_document::Date='"+doc_date+"'")
        rst_id = cur.fetchall()
        str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id join branch br on br.pk_bint_id = acm.fk_branch_id where acm.int_status=0 and br.vchr_code ='{}' and acm.vchr_category = '{}';"
        cur.execute("select array_agg(pk_bint_id||':' ||vchr_name) from bank;")
        rst_bank_details = cur.fetchall()[0]['array_agg']
        # import pdb; pdb.set_trace()
        dct_bank = {str_bank.split(':')[0]:str_bank.split(':')[1] for str_bank in rst_bank_details}

        if rst_id and rst_id[0]['array_agg']:
            str_file = doc_date.replace("-","")+'/CustomerRefundIssues.txt'
            lst_ids = list(set(rst_id[0]['array_agg']))
            for int_id in lst_ids:
                try:
                    # int_payee_type --> 1)Customer 2)Staff 3)Expenses (we take only customer(1))
                    #str_payment_query2 = "select rim.pk_bint_id as refund_id,p.vchr_doc_num as doc_num,p.dbl_amount as amount,rim.dat_created as dat_refund,br.vchr_code as branch_code,lm.int_code as loc,cust.txt_address as address,cust.vchr_name as cust_name,cust.vchr_code as cust_code,cust.int_mobile as cust_mobile,p.vchr_doc_num,p.dat_payment,p.int_payee_type,p.fk_bank_id,p.int_fop,r.vchr_receipt_num from receipt_invoice_matching rim right outer join payment p on p.pk_bint_id=rim.fk_payment_id join receipt r on r.pk_bint_id=rim.fk_receipt_id join branch br on br.pk_bint_id=p.fk_branch_id join customer_details cust on cust.pk_bint_id=r.fk_customer_id join location_master lm on lm.pk_bint_id=br.fk_location_master_id where p.int_payee_type in (1,5) and p.pk_bint_id="+str(int_id)+";"
                    str_payment_query = "select p.vchr_doc_num as doc_num,p.dbl_amount as amount,br.vchr_code as branch_code,lm.int_code as loc,cust.txt_address as address,cust.vchr_name as cust_name,cust.vchr_code as cust_code,cust.int_mobile as cust_mobile,p.vchr_doc_num,p.dat_payment,p.int_payee_type,p.fk_bank_id,p.int_fop from payment p join branch br on br.pk_bint_id=p.fk_branch_id join customer_details cust on cust.pk_bint_id=p.fk_payee_id join location_master lm on lm.pk_bint_id=br.fk_location_master_id where p.int_payee_type = 5 and p.pk_bint_id="+str(int_id)+";"
                    cur.execute(str_payment_query)
                    rst_payment = cur.fetchall()
                    if not rst_payment:
                        str_payment_query = "select p.vchr_doc_num as doc_num,p.int_payee_type,p.dbl_amount as amount,br.vchr_code as branch_code,lm.int_code as loc,sad.vchr_address as address,sup.vchr_name as cust_name,sup.vchr_code as cust_code,bint_phone_no as cust_mobile,p.vchr_doc_num,p.dat_payment,p.int_payee_type,p.fk_bank_id,p.int_fop from  payment p join branch br on br.pk_bint_id=p.fk_branch_id join supplier sup on sup.pk_bint_id=fk_payee_id left outer join address_supplier sad on sad.fk_supplier_id=sup.pk_bint_id join location_master lm on lm.pk_bint_id=br.fk_location_master_id where p.int_payee_type = 6 and p.pk_bint_id="+str(int_id)+";"
                        cur.execute(str_payment_query)
                        rst_payment = cur.fetchall()
                    if rst_payment:
                        
                        rst_payment = dict(rst_payment[0])

                        dct_master_data = {}
                        dct_master_data['Header'] = []
                        dct_master_data['Line level'] = []
                        dct_header = {}
                        dct_line_data = {}
                        dct_details_data = {}
                        # dct_header['MYGOAL_KEY']  = int_id
                        dct_header['MYGOAL_KEY']  = rst_payment['doc_num']
                        dct_header['ShowRoomID']  = rst_payment['branch_code']
                        dct_header['CardCode']  = rst_payment['cust_code'] if rst_payment['cust_code'] else "CASH"
                        dct_header['CardName']  = rst_payment['cust_name'] if rst_payment['cust_code'] else "Cash"
                        dct_header['MobileNo']  = "91"+str(rst_payment['cust_mobile'])[:10]
                        dct_header['IDProofNo']  = -1
                        dct_header['CustAddr']  = rst_payment['address'] or ''
                        dct_header['Amount']  = rst_payment['amount'] or 0
                        dct_header['DocDate']  = datetime.strftime(rst_payment['dat_payment'],'%Y-%m-%d')
                        dct_header['DocType']  = 'S' if rst_payment['int_payee_type']==6 else 'C'
                        dct_header['TransactionType']  = ""
                        dct_master_data['Header'].append(dct_header)



                        dct_details_data['BankName'] = dct_bank[rst_payment['fk_bank_id']] if rst_payment['fk_bank_id'] else ''
                        dct_details_data['TranId'] = "-1"
                        dct_details_data['Amount'] = rst_payment['amount'] or 0
                        dct_details_data['TransferDate'] = datetime.strftime(rst_payment['dat_payment'],'%Y-%m-%d')
                        dct_details_data['LocCode'] = rst_payment['loc']
                        """if intfop 1 -> cash else bank"""
                        if rst_payment['int_fop'] == 1:
                            dct_details_data['PaymentMode'] = 'Cash'
                            dct_details_data['Currency'] = 'INR'
                            dct_details_data['ChequeNum'] = ""
                            dct_details_data['AcctCode'] = "201000101003"
                        else:
                            dct_details_data['PaymentMode'] = 'Transfer'
                            dct_details_data['Currency'] = 'INR'
                            dct_details_data['ChequeNum'] = ""
                            dct_details_data['AcctCode'] = "101010301004"
                        #import pdb;pdb.set_trace()
                        dct_master_data['Line level'] = [dct_details_data]
                        headers = {'Content-type': 'application/json'}
                        data = json.dumps(dct_master_data)
                        print("ID : ",int_id)
                        print("Data : ",data)
#                        import pdb; pdb.set_trace()
                        url = 'http://13.71.18.142:8086/api/In/AdvanceDepositRefund'
                        res_data = requests.post(url,data,headers=headers)
                        cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='Push' where int_document_id ="+str(int_id)+" and int_type=7")
                        response = json.loads(res_data.text)
                        print(response)
                        if response and str(response['status']).upper() == 'SUCCESS': # if Succes
                            cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=7")
                        else:
                            file_object = open(str_file, 'a')
                            file_object.write(data)
                            file_object.write('\n\n')
                            file_object.write(res_data.text)
                            file_object.write('\n\n\n\n')
                            file_object.close()
                            if str_entry == '0':
                                cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=7")
                            else:
                                cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=7")

                except Exception as e:
                    print("Error : ",e)
                    continue
        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(str(e))
        # if len(lst_ids) != lst_ids.index(int_id)+1:
        #     AdvanceRefundMethod(str_entry)
        cur.close()
        conn.close()

if __name__ == '__main__':
    vendorExpense()

