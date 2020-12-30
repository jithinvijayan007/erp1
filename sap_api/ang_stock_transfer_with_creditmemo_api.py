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
import copy

def return_api_call(str_entry,doc_date):
    try:
        db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/myg_pos_live2"
        conn = create_engine(db_connetion_string)
        payment_code = {1:'101010201077',2:'101010301004',5:'101010301017',3:'101010301004'}
        tpl_lst_master_id=conn.execute("select int_document_id from sap_api_track sp join stock_transfer st on sp.int_document_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_from_id where sp.int_type=8 and sp.int_status in ("+str_entry+") and br.vchr_code='AGY' and dat_document::Date = '"+doc_date+"'").fetchall()
        lst_bill_id =[d['int_document_id'] for d in tpl_lst_master_id]
#        import pdb; pdb.set_trace()
        if lst_bill_id:
            str_file = doc_date.replace("-","")+'/CreditMemoIssues.txt'

        print(lst_bill_id)
        for str_id in lst_bill_id:
            try:
                str_id=str(str_id)
                # Query to get sales data
                str_query_data = "select st.pk_bint_id as sales_id,lm.int_code as loc_code,st.vchr_stktransfer_num as doc_num,fk_from_id,st.dat_transfer as doc_date,dbl_rate,ist.fk_item_id,ist.int_qty,dbl_supplier_cost,dbl_dealer_cost,dbl_mrp,dbl_mop,itc.json_tax_master as tax,br.vchr_code as showroom_code,ist.int_qty as quantity,ist.dbl_rate as amount,it.vchr_item_code as item_code,ist.jsn_imei as mnf_serial,ist.jsn_batch_no as jsn_batch_no,brds.vchr_name as brand_name from stock_transfer st join ist_details ist on st.pk_bint_id=ist.fk_transfer_id join item it on it.pk_bint_id=ist.fk_item_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join brands brds on brds.pk_bint_id=it.fk_brand_id join branch br on br.pk_bint_id=st.fk_to_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sap_api_track sap on sap.int_document_id = st.pk_bint_id and sap.int_type=8 where st.pk_bint_id = "+str_id+";"
                rst_sales_data = conn.execute(str_query_data).fetchall()


                # Query to get payment details
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
                #dct_data['Payment Level'] = []
                dct_header = {}
                bln_kfc = False
                dct_all_data=[]
                dct_back_data_date={}
                dbl_total_amount = 0
                for ins_data in rst_sales_data:
                    ins_data = dict(ins_data)
                    if 'MYGOAL_KEY' not in dct_header:
            # ===================================Header Data ===========================================================

                        dct_header['VendorCode'] = 'V01015'
                        dct_header['VendorName'] = '3G Mobile World'
                        dct_header['MYGOAL_KEY'] = ins_data['doc_num'] #ins_data['sales_id']
                        dct_header['ShowRoomID'] = 'AGY'
                        dct_header['BranchID'] = 2
                        dct_header['DocNum'] = ins_data['doc_num']
                        dct_header['BaseDocNum'] = ins_data['doc_num']
                        dct_header['Type'] = 1
                        dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                        dct_header['BaseDocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
#                        dct_data['Header'].append(dct_header)

                        str_log_key_data = "select txt_remarks from sap_api_track where int_type = 8 and int_status in("+str_entry+") and int_document_id ="+str_id+";"
                        rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                        if rst_log_key_details and rst_log_key_details[0]['txt_remarks'] and json.loads(rst_log_key_details[0].values()[0]).get('Log_Key'):
                            dct_header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get('Log_Key')
                        dct_data['Header'].append(dct_header)


            # ====================================Line Data==================================================================================
                    #dbl_total_amount=0
                    dbl_total_amount+=ins_data['amount']*ins_data['int_qty']
                    dct_line_data = {}
                    dct_line_data['ItemCode'] = ins_data['item_code']
                    dct_line_data['Quantity'] = ins_data['int_qty']
                    dct_line_data['WarehouseCode'] = 'AGY'
#                    dct_line_data['CostPrice'] = round(ins_data['amount'],2)
                    dct_line_data['Store'] = 'AGY'
                    dct_line_data['Department'] = ''
                    dct_line_data['Brand'] = '' #ins_data['brand_name']
                    json_tax = ins_data['tax']
                    dbl_tax = json_tax.get(dct_tax['IGST'])
                    json_tax.pop(dct_tax['IGST'])

                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    rst_tax = conn.execute(str_tax_code).fetchall()
                    if rst_tax:
                        rst_tax_code = rst_tax[0][0]
                    else:
                        rst_tax_code = "GST0"
                    dct_line_data['Taxcode']=rst_tax_code
                    dbl_tax = dbl_tax if rst_tax_code != "GST0" else 0
                    dct_line_data['CostPrice'] = round(ins_data['amount']/((100+dbl_tax)/100),2)
                    if ins_data['mnf_serial']['imei']:#Item with imei number
                        str1="select bsd.jsn_imei,bsm.dat_sap_doc_date,bsm.vchr_sap_doc_num from branch_stock_details bsd join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join ist_details ist on ist.pk_bint_id=bsd.fk_transfer_details_id join stock_transfer st on ist.fk_transfer_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_to_id where bsd.int_received>0 and (bsd.jsn_imei->>'imei')::jsonb ?| array"+str(ins_data['mnf_serial']['imei'])+ " and br.vchr_code='AGY' and bsm.vchr_sap_doc_num is not null"
                        rst_back_data = conn.execute(str1).fetchall()
                        for data in rst_back_data:
#                            import pdb;pdb.set_trace()
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
                        str1="select bsd.jsn_batch_no,bsm.dat_sap_doc_date,bsm.vchr_sap_doc_num,bsd.int_received from branch_stock_details bsd join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join ist_details ist on ist.pk_bint_id=bsd.fk_transfer_details_id join stock_transfer st on ist.fk_transfer_id=st.pk_bint_id join branch br on br.pk_bint_id=st.fk_to_id where bsd.int_received>0 and (bsd.jsn_batch_no->>'batch')::jsonb ?| array"+str(ins_data['jsn_batch_no']['batch'])+ " and br.vchr_code='AGY' and bsm.vchr_sap_doc_num is not null"
                        rst_back_data= conn.execute(str1).fetchall()
                        for data in rst_back_data:
                            dct_back_doc_date[data[2]]= str(data[1]).split(' ')[0]
                            if data[2] in dct_back_data_date:
                                if ins_data['item_code'] in dct_back_data_date[data[2]]:
                                    dct_back_data_date[data[2]][ins_data['item_code']].extend(list(set(ins_data['jsn_batch_no']['batch']).intersection(set(data[0]['batch']))))
                                    dct_back_doc_batch_no[data[2]][ins_data['item_code']]+=dct_back_doc_date[data[3]]
                                else:
                                    dct_back_data_date[data[2]][ins_data['item_code']]=list(set(ins_data['jsn_batch_no']['batch']).intersection(set(data[0]['batch'])))
                                    dct_back_doc_batch_no[data[2]]={ins_data['item_code']:data[3]}
                            else:
                                dct_back_data_date[data[2]]={ins_data['item_code']:list(set(ins_data['jsn_batch_no']['batch']).intersection(set(data[0]['batch'])))}
                                dct_back_doc_batch_no[data[2]]={ins_data['item_code']:data[3]}
                    dct_data['Line level'].append(dct_line_data)
                str_query_tcs= "select vchr_code from freight where vchr_category='TCS RECEIVABLE 206C(1H)'"
                rst_freight = conn.execute(str_query_tcs).fetchall()
                dct_data['Freight']=[{"ExpnsCode":-1,"TaxCode":"GST0","LineTotal":0.0}]
                if rst_freight:
                    dct_data['Freight'][0]["ExpnsCode"]=rst_freight[0]['vchr_code']
                    dct_data['Freight'][0]["LineTotal"]= round(dbl_total_amount*0.00075,2)
                dct_org_data={}
                headers = {"Content-type": "application/json"}
                url = 'http://13.71.18.142:8086/api/In/APCreditMemo'
                flag_push=True
                dct_response = ""
                dct_ob_data = copy.deepcopy(dct_data)
                for data in dct_back_data_date:
                    for data_sub in dct_data['Line level']:
                        if data_sub['ItemCode'] not in dct_back_data_date[data]:
                            continue
                        else:
                            for dct_key in dct_back_data_date[data]:
                                if set(dct_back_data_date[data][dct_key]).intersection(set(data_sub['MnfSerial'])):
                                    dct_org_data[data]={}
                                    dct_org_data[data]['Header']= dct_data['Header']
                                    dct_org_data[data]['Freight']= dct_data['Freight']
                                    dct_org_data[data]['Header'][0]['BaseDocNum']=data
                                    dct_org_data[data]['Header'][0]['BaseDocDate']=dct_back_doc_date[data]
                                    dct_line_temp= copy.deepcopy(data_sub)
                                    dct_line_temp['MnfSerial']=list(set(dct_back_data_date[data][dct_key]).intersection(set(data_sub['MnfSerial'])))
                                    if dct_back_doc_batch_no.get(data):
                                        if dct_back_doc_batch_no[data].get(dct_key):
                                                    dct_line_temp['Quantity']= dct_back_doc_batch_no[data].get(dct_key)
                                    else:
                                        dct_line_temp['Quantity']=len(list(set(dct_back_data_date[data][dct_key]).intersection(set(data_sub['MnfSerial']))))
                                    if dct_org_data[data].get('Line level'):
                                        if dct_line_temp in dct_ob_data['Line level']:
                                            dct_ob_data['Line level'].remove(dct_line_temp)
                                        else:
                                           pass  #dct_ob_data['Line level'][0]['Quantity']-=dct_line_temp['Quantity']
                                        dct_org_data[data]['Line Level'].append(dct_line_temp)
                                    else:
                                        if dct_line_temp in dct_ob_data['Line level']:
                                            dct_ob_data['Line level'].remove(dct_line_temp)
                                        else:
                                            pass #dct_ob_data['Line level'][0]['Quantity']-=dct_line_temp['Quantity']
                                        dct_org_data[data]['Line Level']=[dct_line_temp]

                        if not dct_org_data.get(data):
                            continue
                        
                        data_push= json.dumps(dct_org_data[data])
                        print("ID : ",str_id)
                        print("Data : ",data_push,"\n")
                        # str_log_key_data = "select txt_remarks from sap_api_track where int_type = 8 and int_status = -1 and int_document_id ="+str_id+";"
                        # rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                        # print("Error : ",rst_log_key_details[0].values()[0],"\n\n")
 #                       import pdb; pdb.set_trace()
                        print("First Occureence")
                        res_data = requests.post(url,data_push,headers=headers)
                        dct_response=json.loads(res_data.text)
                        #dct_response.pop('message')
                        #str_error_text = json.dumps(dct_response)
                        print(dct_response)
                        if dct_response.get('status')!='success':
                            # break
                            flag_push=False
                        if res_data.status_code == 200:
                            conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=8")
                        elif res_data.status_code == 500:
                            dct_response.pop('message')
                            str_error_text = json.dumps(dct_response)
                            file_object = open(str_file, 'a')
                            file_object.write(data)
                            file_object.write('\n\n')
                            file_object.write(res_data.text)
                            file_object.write('\n\n\n\n')
                            file_object.close()
                            if str_entry == '0':
                                conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(str_id)+" and int_type=8")
                            else:
                                conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(str_id)+" and int_type=8")
                #if dct_data and not dct_back_data_date:
                 #   dct_ob_data['Header']=dct_data['Header']
                  #  dct_ob_data['Line Level'].append(data_sub)
#                    dct_data['Line Level'] = dct_data['Line level']
 #                   dct_data.pop('Line level')
                if dct_ob_data['Line level']:
                    dct_ob_data['Line Level']=dct_ob_data['Line level']
                    dct_ob_data.pop('Line level')
                    data_push= json.dumps(dct_ob_data)

                    print("ID : ",str_id)
                    print("Data : ",data_push,"\n")
#                    import pdb;pdb.set_trace()
                    res_data = requests.post(url,data_push,headers=headers)
                    dct_response=json.loads(res_data.text)
                    #dct_response.pop('message')
                    #str_error_text = json.dumps(dct_response)
                    print(dct_response)
                    if dct_response.get('status')!='success':
                        flag_push=False
                    if res_data.status_code == 200:
                        conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=8")
                    elif res_data.status_code in [500,400]:
                            file_object = open(str_file, 'a')
                            file_object.write(data_push)
                            file_object.write('\n\n')
                            file_object.write(res_data.text)
                            file_object.write('\n\n\n\n')
                            file_object.close()                            
                            dct_response.pop('message')
                            str_error_text = json.dumps(dct_response)
                            if str_entry == '0':
                                conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(str_id)+" and int_type=8")
                            else:
                                conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(str_id)+" and int_type=8")
                if flag_push:
                    conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=8")


            except Exception as e:
                print(e)
                continue
        return True
    except Exception as e:
        raise


if __name__ == '__main__':
    return_api_call()
