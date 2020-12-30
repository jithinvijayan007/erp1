
import requests
from datetime import datetime
import sys
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup
import copy


def purchase_return_api(str_entry,doc_date):

    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            print(str(e))


        cur.execute("select int_document_id from sap_api_track sap join branch_stock_details bd on bd.fk_master_id=int_document_id join ist_details ist on fk_transfer_details_id=ist.pk_bint_id join stock_transfer st on st.pk_bint_id=fk_transfer_id join branch br on br.pk_bint_id=fk_from_id where br.vchr_code ='AGY' and sap.int_type=3 and sap.int_status in ("+str_entry+") and dat_document::Date = '"+doc_date+"'")
        tpl_lst_master_id=cur.fetchall()
        lst_st_id =[d['int_document_id'] for d in tpl_lst_master_id]
        if lst_st_id:
            str_file = doc_date.replace("-","")+'/AngSalesReturnIssues.txt'
        print(lst_st_id)
#        import pdb; pdb.set_trace()
        for int_id in lst_st_id:
            try:
                str_querry = """select sub1.int_qty, brand_name,sub1.jsn_imei,sub1.jsn_batch,sub1.vchr_st_num,sub1.dat_ack, sub1.vchr_comments,sub1.int_key,sub1.vchr_item_code,sub1.vchr_item_name,sub1.dbl_mrp,sub1.vchr_branch_code_from, sub1.vchr_loc_code_from,sub2.vchr_branch_code_to,sub2.vchr_loc_code_to,sub1.tax from( select bsd.int_received as int_qty,bsd.jsn_imei as jsn_imei ,bsd.jsn_batch_no as jsn_batch,st.vchr_stktransfer_num as vchr_st_num,st.dat_acknowledge as dat_ack ,st.vchr_remarks as vchr_comments,bsm.pk_bint_id as int_key, itm.vchr_item_code as vchr_item_code,itm.vchr_name as vchr_item_name,brd.vchr_name as brand_name,ist.dbl_rate as dbl_mrp, br1.vchr_code as vchr_branch_code_from, lm1.int_code as vchr_loc_code_from,st.pk_bint_id as int_st_id,itc.json_tax_master as tax from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch_stock_details bsd on bsd.fk_transfer_details_id=ist.pk_bint_id join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join item itm on itm.pk_bint_id = ist.fk_item_id join brands brd on brd.pk_bint_id=itm.fk_brand_id join item_category itc on itc.pk_bint_id=itm.fk_item_category_id join branch br1 on br1.pk_bint_id = st.fk_from_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm1 on lm1.pk_bint_id =  br1.fk_location_master_id ) as sub1 join( select br2.vchr_code as vchr_branch_code_to, lm2.int_code as vchr_loc_code_to,st.pk_bint_id as int_st_id from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm2 on lm2.pk_bint_id = br2.fk_location_master_id )     as sub2 on sub2.int_st_id = sub1.int_st_id """
                str_querry  =  str_querry +" where sub1.int_key = " + str(int_id) +" and sub1.int_qty>0 and sub1.vchr_branch_code_from='AGY' group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"

                str_item = "select imei_status from item where vchr_item_code='"
                cur.execute(str_querry)
                lst_stock_transfer = cur.fetchall()

                str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                cur.execute(str_tax_master)
                rst_tax_details=cur.fetchall()
                # rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]
                dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details[0]['array_agg']}

                if not lst_stock_transfer:
                    continue

                dct_data = {}
                dct_data['Header'] = []
                dct_data['Line level'] = []
                dct_header = {}
                dct_back_data_date={}
                dct_back_doc_date={}
                dct_back_doc_num = {}
                dct_back_doc_batch_no={}
                dbl_total_amount = 0
                for ins_data in lst_stock_transfer:
                    ins_data = dict(ins_data)

                    if not dct_header:
                        dct_header['CardCode'] = 'C04984'
                        dct_header['CardName'] = 'Angamaly'
                        dct_header['MYGOAL_KEY'] = ins_data['vchr_st_num']
                        dct_header['ShowRoomID'] = ins_data['vchr_branch_code_to']
                        dct_header['InvNum'] = ins_data['vchr_st_num']
                        dct_header['PosInvNum'] = ins_data['vchr_st_num']
                        dct_header["BillTo"]= 'KL'
                        dct_header["ShipTo"]= 'KL'
                        dct_header["Type"]= "REGULAR"
                        dct_header["CustAddr"]= ''
                        dct_header["BpGSTN"]=''
                        dct_header['DealID'] = ''
                        dct_header['DocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                        dct_header['InvDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                        str_log_key_data = "select txt_remarks from sap_api_track where int_type = 3 and int_status in("+str_entry+") and int_document_id="+str(int_id)
                        cur.execute(str_log_key_data)
                        rst_log_key_details = 0 and cur.fetchall()
                        if rst_log_key_details and rst_log_key_details[0]['txt_remarks'] and json.loads(rst_log_key_details[0]['txt_remarks']).get('Log_Key'):
                            dct_header['Log_Key'] = json.loads(rst_log_key_details[0]['txt_remarks']).get('Log_Key')
                        dct_header['BranchID'] = 1
                        dct_data['Header'].append(dct_header)
                    dbl_total_amount +=ins_data['dbl_mrp']
                    str_item_query = str_item+ins_data['vchr_item_code']+"'"
                    cur.execute(str_item_query)
                    rst_item_data = cur.fetchall()
                    if rst_item_data and rst_item_data[0]['imei_status']:
                        dct_line={}
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        json_tax = ins_data['tax']
                        dbl_tax = json_tax.get(dct_tax['IGST'])
                        json_tax.pop(dct_tax['IGST'])
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        cur.execute(str_tax_code)
                        rst_tax = cur.fetchall()
                        rst_tax_code = rst_tax[0]['vchr_code'] if rst_tax else 'GST0'
                        dbl_tax=dbl_tax if rst_tax_code!= 'GST0' else 0
                        dct_line['TaxCode']=rst_tax_code
                        dct_line['LocCode']=ins_data['vchr_loc_code_to']  #14
                        dct_line['Quantity'] = ins_data['int_qty']
                        dct_line['WhsCode'] = ins_data['vchr_branch_code_to']
                        dct_line['Amount'] = round(ins_data['dbl_mrp']/((100+dbl_tax)/100),2)
                        dct_line['Store'] = ins_data['vchr_branch_code_to']
                        dct_line['Department'] = ''
                        dct_line['Brand'] = '' #ins_data['brand_name']
                        dct_line['Employee'] = ''
                        dct_line['DiscountPercent'] = 0
                        dct_line['SalesDiscount'] = 0
                        dct_line['BuyBack'] = 0
                        dct_line['MnfSerial'] = ins_data['jsn_imei']['imei']
#                        import pdb;pdb.set_trace()
                        str1="select ist.jsn_imei,st.dat_sap_doc_date as dat_created,st.vchr_stktransfer_num as vchr_stktransfer_num,st.vchr_sap_doc_num from ist_details ist join stock_transfer st on st.pk_bint_id=ist.fk_transfer_id join branch br on br.pk_bint_id=st.fk_to_id where (ist.jsn_imei->>'imei')::jsonb ?| array"+str(ins_data['jsn_imei']['imei'])+ " and br.vchr_code='AGY' and st.vchr_sap_doc_num is not null"
                        cur.execute(str1)
                        rst_back_data =cur.fetchall()
                        dct_data['Line level'].append(dct_line)
                        for data in rst_back_data:
                            dct_back_doc_date[data['vchr_sap_doc_num']]= str(data['dat_created']).split(' ')[0]
                            dct_back_doc_num[data['vchr_sap_doc_num']]= data['vchr_stktransfer_num']
                            if data['vchr_sap_doc_num'] in dct_back_data_date:
                                if ins_data['vchr_item_code'] in dct_back_data_date[data['vchr_sap_doc_num']]:
                                    dct_back_data_date[data['vchr_sap_doc_num']][ins_data['vchr_item_code']].extend(list(set(data['jsn_imei']['imei']).intersection(set(ins_data['jsn_imei']['imei']))))
                                else:
                                    dct_back_data_date[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]=list(set(data['jsn_imei']['imei']).intersection(set(ins_data['jsn_imei']['imei'])))
                            else:
                                dct_back_data_date[data['vchr_sap_doc_num']]={ins_data['vchr_item_code']:list(set(data['jsn_imei']['imei']).intersection(set(ins_data['jsn_imei']['imei'])))}




                    elif rst_item_data and not rst_item_data[0]['imei_status']:
                        dct_line={}
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        json_tax = ins_data['tax']
                        dbl_tax= json_tax.get(dct_tax['IGST'],0)
                        json_tax.pop(dct_tax['IGST'])
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        cur.execute(str_tax_code)
                        rst_tax = cur.fetchall()
                        rst_tax_code = rst_tax[0]['vchr_code'] if rst_tax else 'GST0'
                        dbl_tax=dbl_tax if rst_tax_code!= 'GST0' else 0
                        dct_line['TaxCode']=rst_tax_code
                        dct_line['LocCode']= ins_data['vchr_loc_code_to']
                        dct_line['Quantity'] = 1
                        dct_line['WhsCode'] = ins_data['vchr_branch_code_to']
                        dct_line['Amount'] = round(ins_data['dbl_mrp']/((100+dbl_tax)/100),2)
                        dct_line['Store'] = ins_data['vchr_branch_code_to']
                        dct_line['Department'] = "" #ins_data['vchr_branch_code_from']
                        dct_line['Brand'] = '' #ins_data['brand_name']
                        dct_line['Employee'] = ''
                        dct_line['TaxCode'] = rst_tax_code
                        dct_line['DiscountPercent'] = 0
                        dct_line['SalesDiscount'] = 0
                        dct_line['BuyBack'] = 0
                        dct_line['MnfSerial'] = ins_data['jsn_batch']['batch']
                        str1="select ist.jsn_batch_no,st.dat_sap_doc_date as dat_created,st.vchr_stktransfer_num,st.vchr_sap_doc_num,ist.int_qty from ist_details ist join stock_transfer st on st.pk_bint_id=ist.fk_transfer_id join branch br on br.pk_bint_id=st.fk_to_id where (ist.jsn_batch_no->>'batch')::jsonb ?| array"+str(ins_data['jsn_batch']['batch'])+ " and br.vchr_code='AGY' and st.vchr_sap_doc_num is not null"
                        cur.execute(str1)
                        rst_back_data =cur.fetchall()
                        for data in rst_back_data:
                            dct_back_doc_date[data['vchr_sap_doc_num']]= str(data['dat_created']).split(' ')[0]
                            dct_back_doc_num[data['vchr_sap_doc_num']]= data['vchr_stktransfer_num']
                            if data['vchr_sap_doc_num'] in dct_back_data_date:
                                if ins_data['vchr_item_code'] in dct_back_data_date[data['vchr_sap_doc_num']]:
                                    dct_back_data_date[data['vchr_sap_doc_num']][ins_data['vchr_item_code']].extend(list(set(ins_data['jsn_batch']['batch']).intersection(set(data['jsn_batch_no']['batch']))))
                                    dct_back_doc_batch_no[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]+=dct_back_doc_date[data['int_qty']]
                                else:
                                    dct_back_data_date[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]=list(set(ins_data['jsn_batch']['batch']).intersection(set(data['jsn_batch_no']['batch'])))
                                    if data['vchr_sap_doc_num'] in dct_back_doc_batch_no:
                                       if ins_data['vchr_item_code'] in dct_back_doc_batch_no[data['vchr_sap_doc_num']]:
                                           dct_back_doc_batch_no[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]+=data['int_qty']
                                       else:
                                           dct_back_doc_batch_no[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]=data['int_qty']
                            else:
                                dct_back_data_date[data['vchr_sap_doc_num']]={ins_data['vchr_item_code']:list(set(ins_data['jsn_batch']['batch']).intersection(set(data['jsn_batch_no']['batch'])))}
                                if data['vchr_sap_doc_num'] in dct_back_doc_batch_no:
                                       if ins_data['vchr_item_code'] in dct_back_doc_batch_no[data['vchr_sap_doc_num']]:
                                           dct_back_doc_batch_no[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]+=data['int_qty']
                                       else:
                                           dct_back_doc_batch_no[data['vchr_sap_doc_num']][ins_data['vchr_item_code']]=data['int_qty']
                        dct_data['Line level'].append(dct_line)

                dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
                str_query_tcs= "select vchr_code from freight where vchr_category='TCS PAYABLE 206C(1H)'"
                cur.execute(str_query_tcs)
                rst_freight = cur.fetchall()
                dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"GST0","LineTotal":0.0}]
                if rst_freight:
                    dct_data['Freight'][0]["ExpCode"]=rst_freight[0]['vchr_code']
                    dct_data['Freight'][0]["LineTotal"]= round(dbl_total_amount*0.00075,2)
                dct_org_data={}
                flag_push=True
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
                                    dct_org_data[data]['Header'][0]['InvNum']=data
                                    dct_org_data[data]['Header'][0]['PosInvNum']=dct_back_doc_num[data]
                                    dct_org_data[data]['Header'][0]['InvDate']=dct_back_doc_date[data]
                                    dct_line_temp=copy.deepcopy(data_sub)
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
                                            pass
                                        dct_org_data[data]['Line Level'].append(dct_line_temp)
                                    else:
                                        if dct_line_temp in dct_ob_data['Line level']:
                                            dct_ob_data['Line level'].remove(dct_line_temp)
                                        else:
                                            pass
                                        dct_org_data[data]['Line Level']=[dct_line_temp]
                    if not dct_org_data.get(data):
                        continue
                    data_push = json.dumps(dct_org_data[data])
                    headers = {"Content-type": "application/json"}
                    str_url = " http://13.71.18.142:8086/api/In/SalesReturn"
                    print("ID : ",int_id)
                    print("Data : ",data_push,"\n")
                    # str_log_key_data = "select txt_remarks from sap_api_track where int_type = 3 and int_status = -1 and int_document_id ="+str_id+";"
                    # rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                    # print("Error : ",rst_log_key_details[0].values()[0],"\n\n")
 #                   import pdb; pdb.set_trace()
                    res_data = requests.post(str_url,data_push,headers=headers)
                    dct_response=json.loads(res_data.text)
                    print(dct_response)
                    #dct_response.pop('message')
                    #str_error_text = json.dumps(dct_response)
                    if dct_response.get('status')!='success':
                        flag_push=False
                    if res_data.status_code == 200:
                        cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                    elif res_data.status_code in [400,500]:
                        file_object = open(str_file, 'a')
                        file_object.write(data_push)
                        file_object.write('\n\n')
                        file_object.write(res_data.text)
                        file_object.write('\n\n\n\n')
                        file_object.close()

                        dct_response.pop('message')
                        str_error_text = json.dumps(dct_response)
                        if str_entry == '0':
                            cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                        else:
                            cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                        break
                if dct_ob_data['Line level']:
                    
                    dct_ob_data['Line Level']=dct_ob_data['Line level']
                    dct_ob_data.pop('Line level')
                    data_push = json.dumps(dct_ob_data)
                    headers = {"Content-type": "application/json"}
                    str_url = " http://13.71.18.142:8086/api/In/SalesReturn"
                    print("ID : ",int_id)
                    print("Data : ",data_push,"\n")
                    # str_log_key_data = "select txt_remarks from sap_api_track where int_type = 3 and int_status = -1 and int_document_id ="+str_id+";"
                    # rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                    # print("Error : ",rst_log_key_details[0].values()[0],"\n\n")
#                    import pdb;pdb.set_trace()
                    res_data = requests.post(str_url,data_push,headers=headers)
                    dct_response=json.loads(res_data.text)
                    print(dct_response)
                    #dct_response.pop('message')
                    #str_error_text = json.dumps(dct_response)
                    if dct_response.get('status')!='success':
                        flag_push=False
                    if res_data.status_code == 200:
                        cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                    elif res_data.status_code in [400,500]:
                        file_object = open(str_file, 'a')
                        file_object.write(data_push)
                        file_object.write('\n\n')
                        file_object.write(res_data.text)
                        file_object.write('\n\n\n\n')
                        file_object.close()

                        dct_response.pop('message')
                        str_error_text = json.dumps(dct_response)
                        if str_entry == '0':
                            cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                        else:
                            cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str_error_text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                        break
                if flag_push:
                    cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='Pushed' where int_document_id ="+str(int_id)+" and int_type=3")
                    if dct_response.get('status')=='success':
                        cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=3")

            except Exception as e:
                print(e)
                continue

        cur.close()
        conn.close()
        return True
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))

if __name__ == '__main__':
    purchase_return_api()
