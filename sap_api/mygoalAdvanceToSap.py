
# from rest_framework.response import Response
from sqlalchemy import create_engine
import json
import requests
from datetime import datetime
from django.http import JsonResponse
from bs4 import BeautifulSoup
import psycopg2

def advance_to_sap(str_entry,doc_date):
    """
    Used to push mygoal advance/deposit data to SAP
    paramerters(to SAP):
                Master data :- MYGOAL_KEY,ShowRoomID,CardName,,CardCode,MobileNo,CustAddr,,DocDate,,Amount,TransactionType
                Sub details :- PaymentMode,BankName,TranId,AdvanceReceiptNo,Amount,Currency
    response(from SAP):suceess/failed
    """


    try:
        try:
            # db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/pos_sap"
            db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/myg_pos_live2"
            conn = create_engine(db_connetion_string)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        #GET RECEIPT data
        #str_file="Receipts"+doc_date.replace('-','')+".txt"
        str_file = doc_date.replace("-","")+'/ReceiptsIssues.txt'
        #file_object.close()
        rst_id = conn.execute("select array_agg(int_document_id) from sap_api_track where int_type in (4,5) and int_status in ("+str_entry+") and dat_document::Date = '"+doc_date+"'").fetchall()
        str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id  where acm.int_status=0 and acm.fk_branch_id {} and acm.vchr_category = '{}';"
#        rst_id =[{'array_agg':[82]}]
        if rst_id and rst_id[0]['array_agg']:
            print("Token 1")
            for int_id in rst_id[0]['array_agg']:
                print("Token 2")
                try:
                    str_id = str(int_id)
                    rst_receipt_data=conn.execute("SELECT r.pk_bint_id as pk_bint_id,b.pk_bint_id as b_id,b.vchr_code as b_vchr_code,c.vchr_name vchr_name,c.vchr_code c_vchr_code,c.int_mobile int_mobile,c.txt_address txt_address,r.dat_created dat_created,\
                    r.dbl_amount dbl_amount,r.int_fop int_fop,r.vchr_bank vchr_bank,r.vchr_card_num as cheque_num,r.vchr_transaction_id vchr_transaction_id,r.vchr_receipt_num vchr_receipt_num,\
                    r.int_receipt_type int_receipt_type,lm.int_code as loc from receipt r join customer_details c on r.fk_customer_id=c.pk_bint_id join userdetails u on u.user_ptr_id=r.fk_created_id join branch b on b.pk_bint_id=u.fk_branch_id join location_master lm on lm.pk_bint_id=b.fk_location_master_id where r.pk_bint_id="+str_id+";").fetchall()
                    lst_form=['Cash','Debit Card','Credit Card','Cheque','RTGS','NEFT','PAYTM','PAYTM MALL','BHARATH QR']
                    lst_mode=['Cash','Debit Card','Credit Card','Cheque','Transfer','Transfer','Transfer','Transfer','Bharath QR']
                    dct_data={}
                    for data in rst_receipt_data:
                        if lst_form[data['int_fop']-1] == 'Cash':
                            str_acc_type = 'CASH A/C'
                            str_branch = "="+str(data['b_id'])
                        elif lst_form[data['int_fop']-1] in ['Debit Card','Credit Card']:
                            str_acc_type = 'TRANSFER'
                            str_branch = "is null"
                        elif lst_form[data['int_fop']-1] in ['Cheque','RTGS','NEFT']:
                            str_acc_type = 'CNR'
                            str_branch = "is null"

                        elif lst_form[data['int_fop']-1] in ['BHARATH QR']:
                            str_acc_type = 'BHARATH QR'
                            str_branch = "is null"
                        elif lst_form[data['int_fop']-1] in ['PAYTM MALL']:
                            str_acc_type = 'PAYTM MALL'
                            str_branch = "is null"
                        else:
                            str_acc_type = 'PAYTM'
                            str_branch = "is null"
                            #rst_acc = conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id  where acm.int_status=0 and acm.fk_branch_id is null and acm.vchr_category ='PAYTM'").fetchall()
                        #if lst_form[data['int_fop']-1] != 'PAYTM':
                        rst_acc = conn.execute(str_account_code.format(str_branch,str_acc_type)).fetchall()
                        acc_code = ""
                        if rst_acc:
                            acc_code = rst_acc[0]['vchr_acc_code']
                        data = dict(data)
                        if not data["cheque_num"]:
                            data["cheque_num"] = '-1'
                        header= {
                        "MYGOAL_KEY":data['vchr_receipt_num'],
                        "ShowRoomID":data['b_vchr_code'] or '',
                        "CustomerName":data['vchr_name'][:15],
                        "MobileNumber":data['int_mobile'],
                        "BranchID": 1 if data['b_vchr_code'] !='AGY' else 2,
                        "CardCode":data['c_vchr_code'] or 'CASH',
                        "CardName":data['vchr_name'] if data['c_vchr_code'] else 'Cash',
                        "MobileNo":'91'+str(data['int_mobile']),
                        "CustAddr":data['txt_address'],
                        "Log_Key":"",
                        "DocDate":datetime.strftime(data['dat_created'],'%Y-%m-%d'),
                        # "DocDate":'2020-04-12'
                        "TransactionType":"Advance",
                        }

                        str_log_key_data = "select txt_remarks from sap_api_track where int_type in (4,5) and int_status in (-1,-2) and int_document_id ="+str_id+";"
                        rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                        if rst_log_key_details:
                            header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get("Log_Key") if json.loads(rst_log_key_details[0].values()[0]).get("Log_Key") else ""

                        Line_level={
                        "Amount":data['dbl_amount'],
                        "LocCode":data["loc"],
                        "Store":data['b_vchr_code'],
                        "Department": "SAL",
                        "Brand": "",
                        "SACCode":"-404", #SAC provided from myg(by Avin) it is a constant value(Test Entries For AR Downpayment 99009900)
                        "TaxCode":"GST0",
                        "AcctCode":"201000101003" }

                        payment_level = {
                        "BankName":data['vchr_bank'].upper() if data.get('vchr_bank') else '-1',
                		"TranId":data['vchr_transaction_id'] if data['vchr_transaction_id'] else -1,
                		"Currency":"INR",
                		"TransferDate":datetime.strftime(data['dat_created'],'%Y-%m-%d'),
                		"PaymentMode":lst_mode[data['int_fop']-1],
                		"ChequeNum":data['vchr_transaction_id'] if lst_form[data['int_fop']-1] =='Cheque' else data["cheque_num"],
                		"AcctCode":acc_code,
                		"Amount":data['dbl_amount']
                        }

                        dct_data['Header'] = [header]
                        dct_data['Line level'] = [Line_level]
                        dct_data['Payment Level'] = [payment_level]
                    data = json.dumps(dct_data)
                    print("ID : ",str_id)
                    print("Data : ",data)
 #                   import pdb; pdb.set_trace()
                    url = 'http://13.71.18.142:8086/api/In/AdvancePayment'
                    headers = {"Content-type": "application/json"}
                    try:
                        res_data = requests.post(url,data,headers=headers)
                        conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type in(4,5)")
                        response = json.loads(res_data.text)
                        print(response)
                        if str(response['status']).upper() == 'SUCCESS':
                            conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type in(4,5)")
                            conn.execute("update receipt set vchr_sap_key ='"+str(response['sapKey'])+"' where pk_bint_id="+str_id)
                        else:
                            file_object = open(str_file, 'a')
                            file_object.write(data)
                            file_object.write('\n\n')
                            file_object.write(res_data.text)
                            file_object.write('\n\n\n\n')
                            file_object.close()
                            response.pop('message')
                            str_error_text = json.dumps(response)
                            if str_entry == "0":
                                conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str_id+" and int_type in(4,5)")
                            else:
                                conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str_id+" and int_type in(4,5)")

                    except Exception as e:
                        raise
                except Exception as e:
                    print(e)
                    continue

        conn.dispose()
 # file_object.close()
        return True
    except Exception as e:
        conn.dispose()
        raise



if __name__ == '__main__':
    advance_to_sap()
