import requests
import json
import urllib.request
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from sqlalchemy import create_engine
from django.http import JsonResponse
import simplejson as json
from bs4 import BeautifulSoup

def bill_api_call(str_entry,doc_date):
    try:
        db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/myg_pos_live2"
        conn = create_engine(db_connetion_string)
        payment_code = {1:'101010201077',2:'101010301004',5:'101010301017',3:'101010301004'}
        tpl_lst_master_id=conn.execute("select int_document_id from sap_api_track sp join stock_transfer st on sp.int_document_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_to_id where sp.int_type=8 and sp.int_status IN ("+str_entry+") and br.vchr_code='AGY' and dat_document::Date = '"+doc_date+"'").fetchall()
        lst_bill_id =[d['int_document_id'] for d in tpl_lst_master_id]
        # print(lst_bill_id)
        if lst_bill_id:
            str_file = doc_date.replace("-","")+'/Ang_BillsIssues.txt'
        for str_id in set(lst_bill_id):
            try:
                str_id=str(str_id)

                str_query_data = "select st.pk_bint_id as sales_id,lm.int_code as loc_code,st.vchr_stktransfer_num as doc_num,fk_from_id,st.dat_transfer as doc_date,dbl_rate,ist.fk_item_id,ist.int_qty,dbl_supplier_cost,dbl_dealer_cost,dbl_mrp,dbl_mop,itc.json_tax_master as tax,br.vchr_code as showroom_code,ist.int_qty as quantity,ist.dbl_rate as amount,it.vchr_item_code as item_code,ist.jsn_imei as mnf_serial,ist.jsn_batch_no as jsn_batch_no,brd.vchr_name as brand_name from stock_transfer st join ist_details ist on st.pk_bint_id=ist.fk_transfer_id join item it on it.pk_bint_id=ist.fk_item_id join brands brd on brd.pk_bint_id=it.fk_brand_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join branch br on br.pk_bint_id=st.fk_from_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sap_api_track sap on sap.int_document_id = st.pk_bint_id and sap.int_type=8 where st.pk_bint_id = "+str_id+";"
                rst_sales_data = conn.execute(str_query_data).fetchall()


                str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

                str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id join branch br on br.pk_bint_id = acm.fk_branch_id where acm.int_status=0 and br.vchr_code ='{}' and acm.vchr_category = '{}';"

                dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}
                # import pdb; pdb.set_trace()
                if not rst_sales_data:
                    print('No data found')
                    return
                dbl_transfer_amount=0
                dct_data = {}
                dct_data['Header'] = []
                dct_data['Line level'] = []
                dct_data['Payment Level'] = []
                dct_header = {}
                bln_kfc = False
                for ins_data in rst_sales_data:
                    ins_data = dict(ins_data)
                    if 'MYGOAL_KEY' not in dct_header:
            # ===================================Header Data ===========================================================

                        dct_header['MYGOAL_KEY'] = ins_data['doc_num']
                        dct_header['ShowRoomID'] = ins_data['showroom_code']
                        dct_header['CardCode'] = "C04984"
                        dct_header['CardName'] = "Angamaly"
                        # dct_header['CustomerName'] = "Angamaly"
                        dct_header["BillTo"]= 'KL'
                        dct_header["ShipTo"]= 'KL'
                        dct_header["Type"]= "REGULAR"
                        dct_header["CustAddr"]= ""
                        dct_header['MobileNumber'] = ""
                        dct_header['BranchID'] = 1
                        dct_header['BpGSTN'] = '32AAIFC578H227'
                        dct_header['DealID'] = ""
                        dct_header['Financier'] = ""
                        dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                        dbl_total_amount=0

                        str_log_key_data = "select txt_remarks from sap_api_track where int_type = 8 and int_status in ("+str_entry+") and int_document_id ="+str_id+";"
                        rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                        if rst_log_key_details and rst_log_key_details[0]['txt_remarks']:
                            dct_header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get('Log_Key')

            # ====================================Line Data==================================================================================
#                    dbl_total_amount+=ins_data['amount']
                    dct_line_data = {}
                    dct_line_data['ItemCode'] = ins_data['item_code']
                    dct_line_data['WhsCode'] = ins_data['showroom_code']
                    dct_line_data['Amount'] = round(ins_data['amount'],2)
                    json_tax = ins_data['tax']

                    # import pdb; pdb.set_trace()
                    LG = json_tax.pop(dct_tax['IGST'])
                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    if conn.execute(str_tax_code).fetchall():
                        rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                    else:
                        rst_tax_code = ""
                    # import pdb; pdb.set_trace()
                    dct_line_data['TaxCode'] = rst_tax_code
                    dbl_tax = int(dct_line_data['TaxCode'].split('T')[1]) if dct_line_data['TaxCode'] else 0
                    dct_line_data['Store'] = ins_data['showroom_code']
                    dct_line_data['Brand'] = ''
                    dct_line_data['Department'] = 'SAL'

                    dct_line_data['Employee'] = ''
                    if ins_data['mnf_serial']['imei'] :
                        dct_line_data['MnfSerial'] = ins_data['mnf_serial']['imei']
                        dct_line_data['Quantity'] =len(ins_data['mnf_serial']['imei'])
                    else:#Item with serial number
                        dct_line_data['MnfSerial'] = ins_data['jsn_batch_no']['batch']
                        dct_line_data['Quantity'] =len(ins_data['jsn_batch_no']['batch'])
                    dct_line_data['Amount'] = round(ins_data['amount']/((100+dbl_tax)/100),2)
                    dct_line_data['LocCode'] = ins_data['loc_code']
                    dct_line_data['SalesDiscount'] = 0
                    dct_line_data['BuyBack'] = 0
                    dbl_total_amount+=ins_data['amount']*dct_line_data['Quantity']
                    dct_data['Line level'].append(dct_line_data)
                dct_data['Header'].append(dct_header)



                dct_payment = {}
                dct_payment['BankName'] = -1
                dct_payment['AdvanceReceiptNo'] = -1
                # Advance Receipt number
                dct_payment['TranId'] = -1

                dct_payment['TransferDate'] = "-1"#datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                dct_payment['PaymentMode'] = 'CASH'
                #str_acc_type = 'CASH A/C'
                #rst_acc = conn.execute(str_account_code.format(ins_data['showroom_code'],str_acc_type)).fetchall()
                dct_payment['AcctCode'] = "-1"
                #if rst_acc:
                 #  dct_payment['AcctCode'] = rst_acc[0][0]
                dct_payment['ChequeNum'] = "-1"
                dct_payment['Amount'] = 0

                # add advance amount with payment details amount


                dct_data['Payment Level'].append(dct_payment)
                str_query_tcs= "select vchr_code from freight where vchr_category='TCS PAYABLE 206C(1H)'"
                rst_freight = conn.execute(str_query_tcs).fetchall()
                dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"GST0","LineTotal":0.0}]
                if rst_freight:
                    dct_data['Freight'][0]["ExpCode"]=rst_freight[0]['vchr_code']
                    dct_data['Freight'][0]["LineTotal"]= round(dbl_total_amount*0.00075,2)
                headers = {"Content-type": "application/json"}
                url = 'http://13.71.18.142:8086/api/In/Bill'
                data = json.dumps(dct_data)
                print("ID : ",str_id)
                print("Data : ",data,"\n")
                # str_log_key_data = "select txt_remarks from sap_api_track where int_type = 8 and int_status = -1 and int_document_id ="+str_id+";"
                # rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                # print("Error : ",rst_log_key_details[0].values()[0],"\n\n")
#                import pdb; pdb.set_trace()
                try:
                    res_data = requests.post(url,data,headers=headers)
                    conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=8")
                    response = json.loads(res_data.text)
                    print(response)
                    #response.pop('message')
                    #str_error_text = json.dumps(response)
                    if response and str(response['status']).upper() == 'SUCCESS':
                        conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=8")
                        conn.execute("update stock_transfer set vchr_sap_doc_num = '"+str(response['sapKey'])+"' where pk_bint_id="+str_id)
                    else:
                        error_message=response.pop('message')
                        str_error_text = json.dumps(response)
                        file_object = open(str_file, 'a')
                        file_object.write(data)
                        file_object.write('\n\n')
                        file_object.write(res_data.text)
                        file_object.write('\n\n\n\n')
                        file_object.close()

                        if str_entry == '0':
                            conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str_id+" and int_type=8")
                        else:
                            conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str_id+" and int_type=8")

                except Exception as e:
                    raise
            except Exception as e:
                print(e)
                continue
        return True
    except Exception as e:
        raise
if __name__ == '__main__':
    bill_api_call()
