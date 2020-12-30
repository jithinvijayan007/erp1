import requests
from datetime import datetime
import sys
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup


def purchase_invoice_api(str_entry,doc_date):
    """
    Used to push anagamaly stock transfer to SAP.It would take data from table Branch Stock Details
    """
    try:
        try:

            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            print(str(e))

        cur.execute("select int_document_id from sap_api_track where int_type=3 and int_status in ("+str_entry+") and dat_document::Date = '"+doc_date+"'")
        tpl_lst_master_id=cur.fetchall()
        lst_st_id =[d['int_document_id'] for d in tpl_lst_master_id]
        if lst_st_id:
            str_file = doc_date.replace("-","")+'/APinvoiceIssues.txt'

        for int_id in lst_st_id:
            try:
                str_querry = """select sub1.int_qty, brand_name,sub1.jsn_imei,sub1.jsn_batch,sub1.vchr_st_num,sub1.dat_ack, sub1.vchr_comments,sub1.int_key,sub1.vchr_item_code,sub1.vchr_item_name,sub1.dbl_mrp,sub1.vchr_branch_code_from, sub1.vchr_loc_code_from,sub2.vchr_branch_code_to,sub2.vchr_loc_code_to,sub1.tax from( select bsd.int_received as int_qty,bsd.jsn_imei as jsn_imei ,bsd.jsn_batch_no as jsn_batch,st.vchr_stktransfer_num as vchr_st_num,st.dat_acknowledge as dat_ack ,st.vchr_remarks as vchr_comments,bsm.pk_bint_id as int_key, itm.vchr_item_code as vchr_item_code,itm.vchr_name as vchr_item_name,brd.vchr_name as brand_name,ist.dbl_rate as dbl_mrp, br1.vchr_code as vchr_branch_code_from, lm1.int_code as vchr_loc_code_from,st.pk_bint_id as int_st_id,itc.json_tax_master as tax from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch_stock_details bsd on bsd.fk_transfer_details_id=ist.pk_bint_id join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join item itm on itm.pk_bint_id = ist.fk_item_id join brands brd on brd.pk_bint_id=itm.fk_brand_id join item_category itc on itc.pk_bint_id=itm.fk_item_category_id join branch br1 on br1.pk_bint_id = st.fk_from_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm1 on lm1.pk_bint_id =  br1.fk_location_master_id ) as sub1 join( select br2.vchr_code as vchr_branch_code_to, lm2.int_code as vchr_loc_code_to,st.pk_bint_id as int_st_id from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm2 on lm2.pk_bint_id = br2.fk_location_master_id )     as sub2 on sub2.int_st_id = sub1.int_st_id """
                str_querry  =  str_querry +" where sub1.int_key = " + str(int_id) +" and sub2.vchr_branch_code_to='AGY' group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"

                str_item = "select imei_status from item where vchr_item_code='"
                cur.execute(str_querry)
                lst_stock_transfer = cur.fetchall()

                str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                cur.execute(str_tax_master)
                rst_tax_details=cur.fetchall()
                dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details[0]['array_agg']}
                if not lst_stock_transfer:
                    continue

                dct_data = {}
                dct_data['Header'] = []
                dct_data['Line level'] = []
                dct_header = {}
                dbl_total_amount=0
                for ins_data in lst_stock_transfer:
                    ins_data = dict(ins_data)

                    if not dct_header:
                        dct_header['MYGOAL_KEY'] = ins_data['vchr_st_num']
                        dct_header['ShowRoomID'] = 'AGY'
                        dct_header['CardCode'] = 'V01015'
                        dct_header['CardName'] = '3GH Mobile World'
                        dct_header['DocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                        dct_header['DealID'] = ""
                        dct_header['BranchID'] = 2
                        dct_header['Financier'] =""
                        dct_header['BaseDocNum'] = ins_data['vchr_st_num']
                        dct_header['BaseDocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                        str_log_key_data = "select txt_remarks from sap_api_track where int_type = 8 and int_status in("+str_entry+") and int_document_id="+str(int_id)
                        cur.execute(str_log_key_data)
                        rst_log_key_details = cur.fetchall()
                        if rst_log_key_details and rst_log_key_details[0]['txt_remarks']:
                            dct_header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get('Log_Key')

                        dct_data['Header'].append(dct_header)
                    dbl_total_amount+=ins_data['dbl_mrp']*ins_data['int_qty']
                    str_item_query = str_item+ins_data['vchr_item_code']+"'"
                    cur.execute(str_item_query)
                    rst_item_data = cur.fetchall()
                    if rst_item_data and rst_item_data[0]['imei_status']:
                        dct_line={}
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        json_tax = ins_data['tax']
                        dbl_tax = json_tax.get(dct_tax['IGST']) or 0
                        json_tax.pop(dct_tax['IGST'])
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        cur.execute(str_tax_code)
                        rst_tax=cur.fetchall()
                        rst_tax_code = rst_tax[0]['vchr_code'] if rst_tax else ""
                        dbl_tax = dbl_tax if rst_tax_code else 0
                        dct_line['TaxCode'] = rst_tax_code
                        dct_line['Quantity'] = ins_data['int_qty']
                        dct_line['MnfSerial'] = ins_data['jsn_imei']['imei']
                        dct_line['Amount'] = round(ins_data['dbl_mrp']/((100+dbl_tax)/100),2)
                        dct_line['Store'] = 'AGY'
                        dct_line['Department'] = 'SAL'
                        dct_line['Brand'] = '' #ins_data['brand_name']
                        
                        dct_data['Line level'].append(dct_line)



                    elif rst_item_data and not rst_item_data[0]['imei_status']:
                        dct_line={}
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        json_tax = ins_data['tax']
                        dbl_tax = json_tax.get(dct_tax['IGST']) or 0
                        json_tax.pop(dct_tax['IGST'])
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        cur.execute(str_tax_code)
                        rst_tax=cur.fetchall()
                        rst_tax_code = rst_tax[0]['vchr_code'] if rst_tax else ""
                        dct_line['TaxCode'] = rst_tax_code
                        dbl_tax = dbl_tax if rst_tax_code else 0
                        dct_line['Quantity'] = ins_data['int_qty']
                        dct_line['MnfSerial'] = ins_data['jsn_batch']['batch']
                        dct_line['Store'] = 'AGY'
                        dct_line['Department'] = 'SAL'
                        dct_line['Brand'] = ''  #ins_data['brand_name']
                        dct_line['Amount'] = round(ins_data['dbl_mrp']/((100+dbl_tax)/100),2)
                        dct_data['Line level'].append(dct_line)

                str_query_tcs= "select vchr_code from freight where vchr_category='TCS RECEIVABLE 206C(1H)'"
                cur.execute(str_query_tcs)
                rst_freight = cur.fetchall()
                dct_data['Freight']=[{"ExpnsCode":-1,"TaxCode":"GST0","LineTotal":0.0}]
                if rst_freight:
                    dct_data['Freight'][0]["ExpnsCode"]=rst_freight[0]['vchr_code']
                    dct_data['Freight'][0]["LineTotal"]= round(dbl_total_amount*0.00075,2)
                data = json.dumps(dct_data)
                headers = {"Content-type": "application/json"}
                str_url = "http://13.71.18.142:8086/api/In/Apinvoice"
                print("ID : ",int_id)
                print("Data : ",data,"\n")
#                import pdb; pdb.set_trace()
                res_data = requests.post(str_url,data,headers=headers)
                dct_response=json.loads(res_data.text)
                print(dct_response)
                #dct_resposne.pop('message')
                #str_error_text = json.dumps(dct_response)
                cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(res_data.text)+"' where int_document_id ="+str(int_id)+" and int_type=3")
                if str(dct_response['status']).upper() == 'SUCCESS':
                    cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(res_data.text)+"' where int_document_id ="+str(int_id)+" and int_type=3")
                    cur.execute("update branch_stock_master set vchr_sap_doc_num='"+str(dct_response['sapKey'])+"',dat_sap_doc_date='"+str(datetime.now())+"' where pk_bint_id ="+str(int_id))
                else:
                    dct_response.pop('message')
                    str_error_text = json.dumps(dct_response)
                    file_object = open(str_file, 'a')
                    file_object.write(data)
                    file_object.write('\n\n')
                    file_object.write(res_data.text)
                    file_object.write('\n\n\n\n')
                    file_object.close()
                    response.pop('message')
                    if str_entry == '0':
                        cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(str_error_text)+"' where int_document_id ="+str(int_id)+" and int_type=3")
                    else:
                        cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(str_error_text)+"' where int_document_id ="+str(int_id)+" and int_type=3")
            except Exception as e:
                print(str(e))
                continue
        return True
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    purchase_invoice_api()
