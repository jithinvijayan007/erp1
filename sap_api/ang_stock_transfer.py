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
from smartChoice import smart_choice_to_pos
from serviceToSap import service_invoice_to_sap
def bills_to_sap_agy():
    """
    Used to push mygoal pos sales data to SAP where angamaly stock transfer take place
    paramerters(to SAP):
            Master data :- MYGOAL_KEY,ShowRoomID,CardCode,CardName,DocDate,DocNum,Type
            Sub details :- ItemCode,Quantity,Amount,TaxCode,Costcenter,MnfSerial,LocCode
    response(from SAP):suceess/failed
    """
    try:
        try:
            # import pdb;pdb.set_trace()
            # Create connection with sqlalchemy engine
            db_connetion_string = "postgres://admin:tms@123@localhost/nisam_pos"
            # db_connetion_string = "postgres://admin:$m3llyf!$h@localhost/pos_data"
            conn = create_engine(db_connetion_string)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        try:
            import pdb;pdb.set_trace()
            tpl_lst_master_id=conn.execute("select int_document_id from sap_api_track sp join stock_transfer st on sp.int_document_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_to_id where sp.int_type=8 and sp.int_status=0 and br.vchr_code='AGY'").fetchall()
            lst_bill_id =[d['int_document_id'] for d in tpl_lst_master_id]
            # if lst_bill_id:
            #     bill_api_call(lst_bill_id)
            # import pdb; pdb.set_trace()
            tpl_lst_master_id=conn.execute("select int_document_id from sap_api_track sp join stock_transfer st on sp.int_document_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_from_id where sp.int_type=8 and sp.int_status=0 and br.vchr_code='AGY'").fetchall()
            lst_return_id =[d['int_document_id'] for d in tpl_lst_master_id]
            import pdb; pdb.set_trace()
            if lst_return_id:
                return_api_call(lst_return_id)


            return
        except Exception as e:
            raise
    except Exception as e:
        print(str(e))

def bill_api_call(lst_bill_id):
    try:
        db_connetion_string = "postgres://admin:tms@123@localhost/nisam_pos"
        # db_connetion_string = "postgres://admin:$m3llyf!$h@localhost/pos_data"
        import pdb; pdb.set_trace()
        conn = create_engine(db_connetion_string)
        payment_code = {1:'101010201077',2:'101010301004',5:'101010301017',3:'101010301004'}
        for str_id in lst_bill_id:
            str_id=str(str_id)
            # Query to get sales data
            # str_query_data = "select sm.pk_bint_id as sales_id,sm.dbl_buyback as buyback,sm.jsn_addition as addition,sm.jsn_deduction as deduction,br.vchr_code as showroom_code,br.fk_states_id as branch_state_id,cust.vchr_name as card_name,cust.vchr_gst_no as gst_no,cust.vchr_code as card_code,cust.pk_bint_id as cust_id,cust.fk_state_id as cust_state_id,sm.dat_invoice as doc_date,sm.vchr_invoice_num as doc_num,it.vchr_item_code as item_code,it.pk_bint_id as item_id,itc.json_tax_master as tax,lm.int_code as loc_code,ist.int_qty as quantity,(sd.dbl_amount-sd.dbl_discount) as amount,sd.json_imei as mnf_serial,sd.vchr_batch batch_no,sd.dbl_tax as tax_amount from sales_master sm join sales_details sd on sm.pk_bint_id=sd.fk_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join item it on it.pk_bint_id = sd.fk_item_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where sm.pk_bint_id = "+str_id+";"

            str_query_data = "select st.pk_bint_id as sales_id,lm.int_code as loc_code,st.vchr_stktransfer_num as doc_num,fk_from_id,st.dat_transfer as doc_date,dbl_rate,ist.fk_item_id,ist.int_qty,dbl_supplier_cost,dbl_dealer_cost,dbl_mrp,dbl_mop,itc.json_tax_master as tax,br.vchr_code as showroom_code,ist.int_qty as quantity,ist.dbl_rate as amount,it.vchr_item_code as item_code,ist.jsn_imei as mnf_serial,ist.jsn_batch_no as jsn_batch_no,brd.vchr_name as brand_name from stock_transfer st join ist_details ist on st.pk_bint_id=ist.fk_transfer_id join item it on it.pk_bint_id=ist.fk_item_id join brands brd on brd.pk_bint_id=it.fk_brand_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join branch br on br.pk_bint_id=st.fk_from_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sap_api_track sap on sap.int_document_id = st.pk_bint_id and sap.int_type=8 where st.pk_bint_id = "+str_id+";"
            rst_sales_data = conn.execute(str_query_data).fetchall()

            # Query to get payment details
            # import pdb;pdb.set_trace()

            str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
            rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

            str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id join branch br on br.pk_bint_id = acm.fk_branch_id where acm.int_status=0 and br.vchr_code ='{}' and acm.vchr_category = '{}';"

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

                    dct_header['MYGOAL_KEY'] = ins_data['doc_num']
                    # dct_header['ShowRoomID'] = "SBM"
                    dct_header['ShowRoomID'] = ins_data['showroom_code']
                    dct_header['CardCode'] = "C04984"
                    dct_header['CardName'] = "Angamaly"
                    # dct_header['CardName'] = "MOHAMMED YOOSUF"
                    dct_header['BranchID'] = 1
                    dct_header['BpGSTN'] = '32AAIFC578H227'
                    dct_header['DealID'] = ""
                    dct_header['Financier'] = ""
                    dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                    dbl_total_amount=0
                    # dct_header['DocNum'] = ins_data['doc_num']
                    # dct_header['Type'] = 'Invoice'

        # ====================================Line Data==================================================================================
                    # for i in range(ins_data['quantity']):
                dbl_total_amount+=ins_data['amount']
                dct_line_data = {}
                dct_line_data['ItemCode'] = ins_data['item_code']
                dct_line_data['WhsCode'] = ins_data['showroom_code']
                # dct_line_data['WhsCode'] = "SBM"
                dct_line_data['Amount'] = round(ins_data['amount'],2)
                json_tax = ins_data['tax']

                json_tax.pop('48')
                str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                dct_line_data['TaxCode'] = rst_tax_code
                dct_line_data['Store'] = ins_data['showroom_code']
                # dct_line_data['Brand'] = ins_data['brand_name']
                dct_line_data['Brand'] = ''
                dct_line_data['Department'] = 'Finance'

                dct_line_data['Employee'] = ''
                if ins_data['mnf_serial']['imei'] :
                    dct_line_data['MnfSerial'] = ins_data['mnf_serial']['imei']
                    dct_line_data['Quantity'] =len(ins_data['mnf_serial']['imei'])
                else:#Item with serial number
                    dct_line_data['MnfSerial'] = ins_data['jsn_batch_no']['batch']
                    dct_line_data['Quantity'] =len(ins_data['jsn_batch_no']['batch'])
                dct_line_data['Amount'] = ins_data['amount']/dct_line_data['Quantity']
                dct_line_data['LocCode'] = ins_data['loc_code']
                dct_data['Line level'].append(dct_line_data)
            import pdb; pdb.set_trace()
            dct_data['Header'].append(dct_header)



            dct_payment = {}
            dct_payment['BankName'] = -1
            dct_payment['AdvanceReceiptNo'] = -1
            # Advance Receipt number
            dct_payment['TranId'] = -1

            dct_payment['TransferDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
            dct_payment['PaymentMode'] = 'CASH'
            str_acc_type = 'CASH A/C'
            rst_acc = conn.execute(str_account_code.format(ins_data['showroom_code'],str_acc_type)).fetchall()
            dct_payment['AcctCode'] = ""
            if rst_acc:
                dct_payment['AcctCode'] = rst_acc[0][0]
            dct_payment['ChequeNum'] = -1
            dct_payment['Amount'] = dbl_total_amount

            # add advance amount with payment details amount


            import pdb; pdb.set_trace()
            dct_data['Payment Level'].append(dct_payment)
            # print(ins_data['fop'])
            dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
            headers = {"Content-type": "application/json"}
            url = 'http://myglive.tmicloud.net:8084/api/In/Bill'
            data = json.dumps(dct_data)
            try:
                res_data = requests.post(url,data,headers=headers)
                conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=1")
                response = json.loads(res_data.text)
                if response['status'] == 'SUCCESS':
                    conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=1")
                else:
                    conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=1")

            except Exception as e:
                raise
    except Exception as e:
        raise




def return_api_call(lst_bill_id):
    try:
        # import pdb; pdb.set_trace()
        db_connetion_string = "postgres://admin:tms@123@localhost/nisam_pos"
        # db_connetion_string = "postgres://admin:$m3llyf!$h@localhost/pos_data"
        conn = create_engine(db_connetion_string)
        payment_code = {1:'101010201077',2:'101010301004',5:'101010301017',3:'101010301004'}
        for str_id in lst_bill_id:
            str_id=str(str_id)
            # Query to get sales data
            # str_query_data = "select sm.pk_bint_id as sales_id,sm.dbl_buyback as buyback,sm.jsn_addition as addition,sm.jsn_deduction as deduction,br.vchr_code as showroom_code,br.fk_states_id as branch_state_id,cust.vchr_name as card_name,cust.vchr_gst_no as gst_no,cust.vchr_code as card_code,cust.pk_bint_id as cust_id,cust.fk_state_id as cust_state_id,sm.dat_invoice as doc_date,sm.vchr_invoice_num as doc_num,it.vchr_item_code as item_code,it.pk_bint_id as item_id,itc.json_tax_master as tax,lm.int_code as loc_code,ist.int_qty as quantity,(sd.dbl_amount-sd.dbl_discount) as amount,sd.json_imei as mnf_serial,sd.vchr_batch batch_no,sd.dbl_tax as tax_amount from sales_master sm join sales_details sd on sm.pk_bint_id=sd.fk_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join item it on it.pk_bint_id = sd.fk_item_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where sm.pk_bint_id = "+str_id+";"

            str_query_data = "select st.pk_bint_id as sales_id,lm.int_code as loc_code,st.vchr_stktransfer_num as doc_num,fk_from_id,st.dat_transfer as doc_date,dbl_rate,ist.fk_item_id,ist.int_qty,dbl_supplier_cost,dbl_dealer_cost,dbl_mrp,dbl_mop,itc.json_tax_master as tax,br.vchr_code as showroom_code,ist.int_qty as quantity,ist.dbl_rate as amount,it.vchr_item_code as item_code,ist.jsn_imei as mnf_serial,ist.jsn_batch_no as jsn_batch_no,brds.vchr_name as brand_name from stock_transfer st join ist_details ist on st.pk_bint_id=ist.fk_transfer_id join item it on it.pk_bint_id=ist.fk_item_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join brands brds on brds.pk_bint_id=it.fk_brand_id join branch br on br.pk_bint_id=st.fk_to_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sap_api_track sap on sap.int_document_id = st.pk_bint_id and sap.int_type=8 where st.pk_bint_id = "+str_id+";"
            rst_sales_data = conn.execute(str_query_data).fetchall()


            # Query to get payment details
            # import pdb;pdb.set_trace()

            str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
            rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

            str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id join branch br on br.pk_bint_id = acm.fk_branch_id where acm.int_status=0 and br.vchr_code ='{}' and acm.vchr_category = '{}';"

            dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}

            if not rst_sales_data:
                print('No data found')
                return
            dct_back_data_doc={}
            dct_back_doc_date={}
            dct_back_doc_batch_no={}
            dct_data = {}
            dct_data['Header'] = []
            dct_data['Line level'] = []
            dct_data['Payment Level'] = []
            dct_header = {}
            bln_kfc = False
            dct_all_data=[]

            for ins_data in rst_sales_data:
                dct_back_data_date={}
                ins_data = dict(ins_data)
                if 'MYGOAL_KEY' not in dct_header:
        # ===================================Header Data ===========================================================

                    dct_header['VendorCode'] = 'V01015'
                    dct_header['VendorName'] = 'Angamaly'
                    dct_header['MYGOAL_KEY'] = ins_data['sales_id']
                    # dct_header['ShowRoomID'] = "SBM"
                    dct_header['ShowRoomID'] = ins_data['showroom_code']
                    dct_header['BranchID'] = 1
                    dct_header['DocNum'] = ins_data['doc_num']
                    dct_header['BaseDocNum'] = ""
                    dct_header['Type'] = 1
                    dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                    dct_header['BaseDocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')



        # ====================================Line Data==================================================================================
                dbl_total_amount=0
                # import pdb; pdb.set_trace()
                # for i in range(ins_data['quantity']):
                dbl_total_amount+=ins_data['amount']
                dct_line_data = {}
                dct_line_data['ItemCode'] = ins_data['item_code']
                dct_line_data['Quantity'] = 1
                dct_line_data['WarehouseCode'] = ins_data['showroom_code']
                # dct_line_data['WhsCode'] = "SBM"
                dct_line_data['CostPrice'] = round(ins_data['amount'],2)
                dct_line_data['Store'] = ins_data['showroom_code']
                dct_line_data['Department'] = 'Finance'
                dct_line_data['Brand'] = ins_data['brand_name']
                json_tax = ins_data['tax']
                json_tax.pop('48')
                # import pdb; pdb.set_trace()

                str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                # dct_line_data['TaxCode'] = rst_tax_code
                if ins_data['mnf_serial']['imei']:#Item with imei number
                    # import pdb; pdb.set_trace()
                    str1="select bsd.jsn_imei,bsm.dat_sap_doc_date,bsm.vchr_sap_doc_num from branch_stock_details bsd join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join ist_details ist on ist.pk_bint_id=bsd.fk_transfer_details_id join stock_transfer st on ist.fk_transfer_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_to_id where (bsd.jsn_imei->>'imei')::jsonb ?| array"+str(ins_data['mnf_serial']['imei'])+ " and br.vchr_code='AGY'"
                    rst_back_data = conn.execute(str1).fetchall()
                    # import pdb; pdb.set_trace()
                    for data in rst_back_data:
                        dct_back_doc_date[data[2]]= str(data[1]).split(' ')[0]
                        if data[2] in dct_back_data_date:
                            if ins_data['item_code'] in dct_back_data_date[data[2]]:
                                dct_back_data_date[data[2]][ins_data['item_code']].extend(list(set(data[0]['imei']).intersection(set(ins_data['mnf_serial']['imei']))))
                            else:
                                dct_back_data_date[data[2]][ins_data['item_code']]=list(set(data[0]['imei']).intersection(set(ins_data['mnf_serial']['imei'])))
                        else:
                            dct_back_data_date[data[2]]={ins_data['item_code']:list(set(data[0]['imei']).intersection(set(ins_data['mnf_serial']['imei'])))}


                    dct_line_data['MnfSerial'] = ins_data['mnf_serial']['imei']
                else:#Item with serial number
                    dct_line_data['MnfSerial'] = ins_data['jsn_batch_no']['batch']
                    str1="select bsim.jsn_batch_no,bsm.dat_sap_doc_date,bsm.vchr_sap_doc_num,bsim.int_qty from branch_stock_details bsd join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join ist_details ist on ist.pk_bint_id=bsd.fk_transfer_details_id join stock_transfer st on ist.fk_transfer_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_to_id join branch_stock_imei_details bsim on bsim.fk_details_id=bsd.pk_bint_id where (bsd.jsn_batch_no->>'batch')::jsonb ?| array"+str(ins_data['jsn_batch_no']['batch'])+ " and br.vchr_code='AGY'"
                    rst_back_data= conn.execute(str1).fetchall()
                    for data in rst_back_data:
                        dct_back_doc_date[data[2]]= str(data[1]).split(' ')[0]
                        if data[2] in dct_back_data_date:
                            if ins_data['item_code'] in dct_back_data_date[data[2]]:
                                dct_back_data_date[data[2]][ins_data['item_code']].extend(list(set(ins_data['jsn_batch_no']['batch']).intersection(set(data[0]['batch']))))
                                dct_back_doc_batch_no[data[2]][ins_data['item_code']]+=dct_back_doc_date[data[3]]
                            else:
                                dct_back_data_date[data[2]][ins_data['item_code']]=list(set(ins_data['jsn_batch_no']['batch']).intersection(set(data[0]['batch'])))
                                dct_back_doc_batch_no[data[2]][ins_data['item_code']]=dct_back_doc_date[data[3]]
                        else:
                            dct_back_data_date[data[2]]={ins_data['item_code']:list(set(ins_data['jsn_batch_no']['batch']).intersection(set(data[0]['batch'])))}
                            # dct_back_data_date[data[2]]={ins_data['item_code']]:dct_back_doc_date[data[3]]}
                # dct_line_data['LocCode'] = ins_data['loc_code']
                dct_data['Line level'].append(dct_line_data)
                dct_data['Header'].append(dct_header)
                dct_org_data={}
                import pdb; pdb.set_trace()
                for data in dct_back_data_date:
                    flag_push=True
                    for data_sub in dct_data['Line level']:
                        if data_sub['ItemCode'] not in dct_back_data_date[data]:
                            continue
                        else:
                            for dct_key in dct_back_data_date[data]:
                                if set(dct_back_data_date[data][dct_key]).intersection(set(data_sub['MnfSerial'])):
                                    dct_org_data[data]={}
                                    dct_org_data[data]['Header']= dct_data['Header']
                                    dct_org_data[data]['Header'][0]['BaseDocNum']=data
                                    dct_org_data[data]['Header'][0]['BaseDocDate']=dct_back_doc_date[data]
                                    dct_line_temp=data_sub
                                    dct_line_temp['MnfSerial']=list(set(dct_back_data_date[data][dct_key]).intersection(set(data_sub['MnfSerial'])))
                                    if dct_back_doc_batch_no.get(data):
                                        if dct_back_doc_batch_no[data].get(dct_key):
                                                    dct_line_temp['Quantity']= dct_back_doc_batch_no[data].get(dct_key)
                                    else:
                                        dct_line_temp['Quantity']=len(list(set(dct_back_data_date[data][dct_key]).intersection(set(data_sub['MnfSerial']))))
                                    if dct_org_data[data].get('Line level'):
                                        dct_org_data[data]['Line Level'].append(dct_line_temp)
                                    else:
                                        dct_org_data[data]['Line Level']=[dct_line_temp]

                    headers = {"Content-type": "application/json"}
                    url = 'http://myglive.tmicloud.net:8084/api/In/APCreditMemo'
                    data= json.dumps(dct_org_data)
                    res_data = requests.post(url,data,headers=headers)
                    dct_response=json.loads(res_data.text)
                    if dct_response.get('status')!='SUCCESS':
                        flag_push=False
                        if res_data.status_code == 200:
                            conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str(str_id)+" and int_type=3")
                        elif res_data.status_code == 500:
                            conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=3")
                if flag_push:
                    conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=3")



        return
    except Exception as e:
        raise

            #     import pdb; pdb.set_trace()
            #     headers = {"Content-type": "application/json"}
            #     lst_all_data.append(dct_data)
            #
            #
            #
            #         # if not dct_data[ins_payment['sales_id']]['payment_details']:
            # dct_payment = {}
            # dct_payment['BankName'] = ""
            # dct_payment['ShowRoomID'] = ins_data['showroom_code']
            # dct_payment['AdvanceReceiptNo'] = -1
            # # Advance Receipt number
            # dct_payment['TranId'] = -1
            # dct_payment['Currency'] = 'INR'
            # dct_payment['Exchangerate'] = 0
            # # if ins_payment['fop'] != 1:
            # #     dct_payment['Exchangerate'] = 1
            #
            # dct_payment['TransferDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
            # dct_payment['PaymentMode'] = 'CASH'
            # str_acc_type = 'CASH A/C'
            # rst_acc = conn.execute(str_account_code.format(ins_data['showroom_code'],str_acc_type)).fetchall()
            # dct_payment['AcctCode'] = ""
            # if rst_acc:
            #     dct_payment['AcctCode'] = rst_acc[0][0]
            # dct_payment['ChequeNum'] = ""
            # dct_payment['Amount'] = 0
            #
            # # add advance amount with payment details amount
            #
            #
            # import pdb; pdb.set_trace()
            # dct_data['Payment Level'].append(dct_payment)
            # # print(ins_data['fop'])
            # headers = {"Content-type": "application/json"}
            # url = 'http://myglive.tmicloud.net:8084/api/In/APCreditMemo'
            # res_data = requests.post(url,data,headers=headers)
            # dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
            # data = json.dumps(dct_data)
            # try:
            #     res_data = requests.post(url,data={'jsonvalue':data})
            #     conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=1")
            #     soup = BeautifulSoup(res_data.text,'xml')
            #     if res_data.status_code == 200:
            #         conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str_id+" and int_type=1")
            #     elif res_data.status_code == 500:
            #         conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=1")
            #     else:
            #         conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str_id+" and int_type=1")
            #
            # except Exception as e:
            #     raise
            #
            #

if __name__ == '__main__':
    bills_to_sap_agy()
