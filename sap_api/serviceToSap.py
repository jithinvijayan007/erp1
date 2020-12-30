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

def service_invoice_to_sap(lst_service):
    """
    Used to push mygoal pos service data to SAP
    paramerters(to SAP):
            Master data :- MYGOAL_KEY,ShowRoomID,CardCode,CardName,DocDate,DocNum,Type
            Sub details :- ItemCode,Quantity,Amount,TaxCode,Costcenter,MnfSerial,LocCode
    response(from SAP):suceess/failed
    """
    try:
        try:
            # Create connection with sqlalchemy engine
            #db_connetion_string = "postgres://admin:tms@123@localhost/pos_test_new"
            db_connetion_string = "postgres://admin:$m3llyf!$h@localhost/pos_sap"
            conn = create_engine(db_connetion_string)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        try:
            import pdb; pdb.set_trace()
            for str_id in lst_service:
                str_id=str(str_id)
                # Query to get sales data
                str_query_data = "select sm.pk_bint_id as sales_id,sm.dbl_buyback as buyback,sm.jsn_addition as addition,sm.jsn_deduction as deduction,br.vchr_code as showroom_code,br.fk_states_id as branch_state_id,cust.vchr_name as card_name,cust.vchr_gst_no as gst_no,cust.vchr_code as card_code,cust.pk_bint_id as cust_id,cust.fk_state_id as cust_state_id,sm.dat_invoice as doc_date,sm.vchr_invoice_num as doc_num,it.vchr_item_code as item_code,it.pk_bint_id as item_id,itc.vchr_hsn_code as hsn_code,itc.json_tax_master as tax,lm.int_code as loc_code,sd.int_qty as quantity,(sd.dbl_amount-sd.dbl_discount) as amount,sd.json_imei as mnf_serial,sd.vchr_batch batch_no,sd.dbl_tax as tax_amount from sales_master sm join sales_details sd on sm.pk_bint_id=sd.fk_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join item it on it.pk_bint_id = sd.fk_item_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where sm.pk_bint_id = "+str_id+";"
                rst_sales_data = conn.execute(str_query_data).fetchall()

                # Query to get payment details
                #import pdb;pdb.set_trace()
                str_payment_data = "select sm.pk_bint_id as sales_id,br.pk_bint_id as sh_id,br.vchr_code as showroom_code,pd.vchr_reff_number as tr_id,pd.dbl_receved_amt as amount,pd.int_fop as fop,pd.vchr_card_number as card_num,pd.fk_bank_id as bank_id,pd.dat_created_at::DATE as transfer_date,case when pd.int_fop =0 then 'Transfer' when pd.int_fop =1 then 'Cash' when pd.int_fop =2 then 'Transfer' when pd.int_fop =3 then 'Transfer' else 'Other' end as payment_mode from sales_master sm join payment_details pd on sm.pk_bint_id=pd.fk_sales_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where pd.fk_sales_master_id = "+str_id+";"
                rst_payment_details = conn.execute(str_payment_data).fetchall()

                # Query to get advance receipt data
                str_advance_data = "select fk_sales_master_id as sale_id,rc.vchr_receipt_num,rc.dbl_amount from receipt_invoice_matching rim join receipt rc on rim.fk_receipt_id = rc.pk_bint_id where int_pstatus = 0 and int_receipt_type in (1,2) and fk_sales_master_id="+str_id+";"
                rst_advance_details = conn.execute(str_advance_data).fetchall()

                # Query to get bank details
                str_bank_data = "select array_agg(pk_bint_id||':' ||vchr_name) from bank;"
                rst_bank_details = conn.execute(str_bank_data).fetchall()[0][0]
                # create dictionary of bank and pk_bint_id
                dct_bank = {str_bank.split(':')[0]:str_bank.split(':')[1] for str_bank in rst_bank_details}

                str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

                str_account_code_query = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_brand_id '{}' and acm.vchr_category = '{}';"

                dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}

                if not rst_sales_data:
                    print('No data found')
                    return

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
                        if ins_data['branch_state_id'] == ins_data['cust_state_id'] and not ins_data['gst_no']:
                            bln_kfc = True
                        dct_header['MYGOAL_KEY'] = ins_data['sales_id']
                        # dct_header['ShowRoomID'] = "SBM"
                        dct_header['ShowRoomID'] = ins_data['showroom_code']
                        dct_header['CardCode'] = "CASH"
                        dct_header['CardName'] = "Cash"
                        dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                        dct_header['DocNum'] = ins_data['doc_num']

    # ====================================Line Data==================================================================================
                    for i in range(ins_data['quantity']):
                        dct_line_data = {}
                        dct_line_data['ItemCode'] = ins_data['item_code']
                        dct_line_data['Quantity'] = 1
                        dct_line_data['WhsCode'] = ins_data['showroom_code']
                        dct_line_data['Amount'] = round(ins_data['amount'],2)
                        dct_line_data['HSN'] = ins_data['hsn_code']
                        json_tax = ins_data['tax']
                        if bln_kfc:
                            json_tax[dct_tax['KFC']] = 1
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                        dct_line_data['TaxCode'] = rst_tax_code
                        dct_line_data['Costcenter'] = ins_data['showroom_code']
                        dct_line_data['AcctCode'] = ""
                        if ins_data['mnf_serial'] and len(ins_data['mnf_serial']) == (i+1):#Item with imei number
                            dct_line_data['MnfSerial'] = ins_data['mnf_serial'][i]
                        else:#Item with serial number
                            dct_line_data['MnfSerial'] = ins_data['batch_no'] if ins_data['batch_no'] else ""
                        dct_line_data['LocCode'] = ins_data['loc_code']
                        dct_data['Line level'].append(dct_line_data)

                dct_data['Header'].append(dct_header)
                dct_advance = {}
                str_account_code = ""
                # craete dictionary of advance amount
                if rst_advance_details:
                    for ins_adv in rst_advance_details:
                        dct_advance[ins_adv['sale_id']] = {'receipt_num':ins_adv['vchr_receipt_num'],'dbl_amount':ins_adv['dbl_amount']}
                if rst_payment_details:
                    for ins_payment in rst_payment_details:
                        # if not dct_data[ins_payment['sales_id']]['payment_details']:
                        dct_payment = {}
                        dct_payment['BankName'] = ""
                        if ins_payment['bank_id']:
                            dct_payment['BankName'] = dct_bank[str(ins_payment['bank_id'])]
                        dct_payment['ShowRoomID'] = ins_payment['showroom_code']
                        dct_payment['AdvanceReceiptNo'] = -1
                        # Advance Receipt number
                        if ins_payment['sales_id'] in dct_advance:
                            dct_payment['AdvanceReceiptNo'] = dct_advance[ins_payment['sales_id']]['receipt_num']
                        dct_payment['TranId'] = ins_payment['tr_id'] if ins_payment['tr_id'] else ""
                        dct_payment['Currency'] = 'INR'
                        dct_payment['Exchangerate'] = 0
                        # if ins_payment['fop'] != 1:
                        #     dct_payment['Exchangerate'] = 1

                        dct_payment['TransferDate'] = datetime.strftime(ins_payment['transfer_date'],'%Y-%m-%d')
                        dct_payment['PaymentMode'] = ins_payment['payment_mode']
                        if ins_payment['fop'] in [1,0]:
                            str_acc_type = 'CASH A/C'
                            str_branch= "="+str(ins_payment['sh_id'])
                        elif ins_payment['fop'] in [2,3]:
                            str_acc_type = 'Transfer'
                            str_branch='is null'
                        elif ins_payment['fop'] ==5:
                            str_acc_type = 'PATYM'
                            str_branch='is null'
                        rst_acc = conn.execute(str_account_code_query.format(str_branch,str_acc_type)).fetchall()
                        dct_payment['AcctCode'] = ""
                        if rst_acc:
                            dct_payment['AcctCode'] = rst_acc[0][0]
                            str_account_code = rst_acc[0][0]
                        dct_payment['ChequeNum'] = ins_payment['card_num'] if ins_payment['card_num'] else ""
                        dct_payment['Amount'] = ins_payment['amount']
                        # add advance amount with payment details amount
                        if ins_payment['sales_id'] in dct_advance:
                            dct_payment['Amount'] += dct_advance[ins_payment['sales_id']]['dbl_amount']
                        dct_data['Payment Level'].append(dct_payment)


                for dct_line in dct_data['Line level']:
                    dct_line['AcctCode'] = str_account_code
                import pdb; pdb.set_trace()
                # print(ins_payment['fop'])
                url = 'http://myg.tmicloud.net:85/POSOutbound.asmx/In_service_invoice'
                data = json.dumps(dct_data)
                try:
                    res_data = requests.post(url,data={'jsonvalue':data})
                    conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=1")
                    soup = BeautifulSoup(res_data.text,'xml')
                    if res_data.status_code == 200:
                        conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str_id+" and int_type=1")
                    elif res_data.status_code == 500:
                        conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=1")
                    else:
                        conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str_id+" and int_type=1")

                except Exception as e:
                    raise
            return
        except Exception as e:
            raise
    except Exception as e:
        print(str(e))

if __name__ == '__main__':
    service_invoice_to_sap()
