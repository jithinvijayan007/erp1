import requests
from datetime import datetime
import sys
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup


def purchase_invoice_api():
    """
    Used to push anagamaly stock transfer to SAP.It would take data from table Branch Stock Details
    """
    try:
        try:

            import pdb; pdb.set_trace()
            conn = None
            conn = psycopg2.connect(host="localhost",database="nisam_pos", user="admin", password="tms@123")
            conn.autocommit = True
            # cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            # return JsonResponse({'status':'failed','reason':'cannot connect to database'})
            print(str(e))

        # for int_stock_transfer_id in lst_stock_transfer_id:
        import pdb; pdb.set_trace()

        cur.execute("select int_document_id from sap_api_track where int_type=3 and int_status=0")
        tpl_lst_master_id=cur.fetchall()
        lst_st_id =[d['int_document_id'] for d in tpl_lst_master_id]

        for int_id in lst_st_id:
            str_querry = """select sub1.int_qty, brand_name,sub1.jsn_imei,sub1.jsn_batch,sub1.vchr_st_num,sub1.dat_ack, sub1.vchr_comments,sub1.int_key,sub1.vchr_item_code,sub1.vchr_item_name,sub1.dbl_mrp,sub1.vchr_branch_code_from, sub1.vchr_loc_code_from,sub2.vchr_branch_code_to,sub2.vchr_loc_code_to,sub1.tax from( select bsd.int_qty as int_qty,bsd.jsn_imei as jsn_imei ,bsd.jsn_batch_no as jsn_batch,st.vchr_stktransfer_num as vchr_st_num,st.dat_acknowledge as dat_ack ,st.vchr_remarks as vchr_comments,bsm.pk_bint_id as int_key, itm.vchr_item_code as vchr_item_code,itm.vchr_name as vchr_item_name,brd.vchr_name as brand_name,ist.dbl_rate as dbl_mrp, br1.vchr_code as vchr_branch_code_from, lm1.int_code as vchr_loc_code_from,st.pk_bint_id as int_st_id,itc.json_tax_master as tax from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch_stock_details bsd on bsd.fk_transfer_details_id=ist.pk_bint_id join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join item itm on itm.pk_bint_id = ist.fk_item_id join brands brd on brd.pk_bint_id=itm.fk_brand_id join item_category itc on itc.pk_bint_id=itm.fk_item_category_id join branch br1 on br1.pk_bint_id = st.fk_from_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm1 on lm1.pk_bint_id =  br1.fk_location_master_id ) as sub1 join( select br2.vchr_code as vchr_branch_code_to, lm2.int_code as vchr_loc_code_to,st.pk_bint_id as int_st_id from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm2 on lm2.pk_bint_id = br2.fk_location_master_id )     as sub2 on sub2.int_st_id = sub1.int_st_id """
            str_querry  =  str_querry +" where sub1.int_key = " + str(int_id) +" and sub2.vchr_branch_code_to='AGY' group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"

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
            for ins_data in lst_stock_transfer:
                ins_data = dict(ins_data)
                #dct_data = {}
                #dct_data['Header'] = []

                if not dct_header:
                    dct_header['MYGOAL_KEY'] = str(ins_data['int_key'])
                    dct_header['ShowRoomID'] = ins_data['vchr_branch_code_from']
                    dct_header['CardCode'] = 'V01015'
                    dct_header['CardName'] = 'Angamaly'
                    dct_header['DocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                    dct_header['DealID'] = ""
                    dct_header['BranchID'] = 1
                    dct_header['Financier'] =""
                    dct_data['Header'].append(dct_header)
                str_item_query = str_item+ins_data['vchr_item_code']+"'"
                cur.execute(str_item_query)
                rst_item_data = cur.fetchall()
                if rst_item_data and rst_item_data[0]['imei_status']:
                    dct_line={}
                    dct_line['ItemCode'] = ins_data['vchr_item_code']
                    json_tax = ins_data['tax']
                    json_tax.pop('48')
                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    cur.execute(str_tax_code)
                    rst_tax_code = cur.fetchall()[0]['vchr_code']
                    dct_line['TaxCode'] = rst_tax_code
                    dct_line['Quantity'] = ins_data['int_qty']
                    dct_line['MnfSerial'] = ins_data['jsn_imei']['imei']
                    dct_line['Amount'] = ins_data['dbl_mrp']/ins_data['int_qty']
                    dct_line['Store'] = ins_data['vchr_branch_code_from']
                    dct_line['Department'] = 'Finance'
                    dct_line['Brand'] = ins_data['brand_name']
                    dct_data['Line level'].append(dct_line)



                elif rst_item_data and not rst_item_data[0]['imei_status']:
                    dct_line={}
                    dct_line['ItemCode'] = ins_data['vchr_item_code']
                    json_tax = ins_data['tax']
                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    cur.execute(str_tax_code)
                    rst_tax_code = cur.fetchall()[0]['vchr_code']
                    dct_line['TaxCode'] = rst_tax_code
                    dct_line['Quantity'] = ins_data['int_qty']
                    dct_line['MnfSerial'] = ins_data['jsn_batch']['batch']
                    dct_line['Store'] = ins_data['vchr_branch_code_from']
                    dct_line['Department'] = 'Finance'
                    dct_line['Brand'] = ins_data['brand_name']
                    dct_line['Amount'] = ins_data['dbl_mrp']/ins_data['int_qty']
                    dct_data['Line level'].append(dct_line)

            # dct_header['ROW_COUNT'] = len(dct_data['Line level'])
            # dct_data['Header'].append(dct_header)
            import pdb; pdb.set_trace()
            dct_data['Freight']=[{"ExpnsCode":-1,"TaxCode":"","LineTotal":0.0}]
            data = json.dumps(dct_data)
            headers = {"Content-type": "application/json"}
            str_url = "http://myglive.tmicloud.net:8084/api/In/Apinvoice"
            res_data = requests.post(str_url,data,headers=headers)
            dct_response=json.loads(res_data.text)
            cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='Pushed' where int_document_id ="+str(int_id)+" and int_type=3")
            if dct_response['status'].upper() == 'SUCCESS':
                cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+dct_response['transaction']+"' where int_document_id ="+str(int_id)+" and int_type=3")
                cur.execute("update branch_stock_master set vchr_sap_doc_num='"+str(dct_response['sapKey'])+"',dat_sap_doc_date='"+str(datetime.now())+"' where pk_bint_id ="+str(int_id))
            else:
                cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
        return
    except Exception as e:
        print(str(e))








def purchase_return_api():

    try:
        try:
            import pdb; pdb.set_trace()
            conn = None
            conn = psycopg2.connect(host="localhost",database="nisam_pos", user="admin", password="tms@123")
            conn.autocommit = True
            # cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            # return JsonResponse({'status':'failed','reason':'cannot connect to database'})
            print(str(e))

        # for int_stock_transfer_id in lst_stock_transfer_id:
        import pdb; pdb.set_trace()

        cur.execute("select int_document_id from sap_api_track where int_type=3 and int_status=0")
        tpl_lst_master_id=cur.fetchall()
        lst_st_id =[d['int_document_id'] for d in tpl_lst_master_id]
        lst_st_id=lst_st_id[-1:]
        for int_id in lst_st_id:
            str_querry = """select sub1.int_qty, brand_name,sub1.jsn_imei,sub1.jsn_batch,sub1.vchr_st_num,sub1.dat_ack, sub1.vchr_comments,sub1.int_key,sub1.vchr_item_code,sub1.vchr_item_name,sub1.dbl_mrp,sub1.vchr_branch_code_from, sub1.vchr_loc_code_from,sub2.vchr_branch_code_to,sub2.vchr_loc_code_to,sub1.tax from( select bsd.int_qty as int_qty,bsd.jsn_imei as jsn_imei ,bsd.jsn_batch_no as jsn_batch,st.vchr_stktransfer_num as vchr_st_num,st.dat_acknowledge as dat_ack ,st.vchr_remarks as vchr_comments,bsm.pk_bint_id as int_key, itm.vchr_item_code as vchr_item_code,itm.vchr_name as vchr_item_name,brd.vchr_name as brand_name,ist.dbl_rate as dbl_mrp, br1.vchr_code as vchr_branch_code_from, lm1.int_code as vchr_loc_code_from,st.pk_bint_id as int_st_id,itc.json_tax_master as tax from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch_stock_details bsd on bsd.fk_transfer_details_id=ist.pk_bint_id join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join item itm on itm.pk_bint_id = ist.fk_item_id join brands brd on brd.pk_bint_id=itm.fk_brand_id join item_category itc on itc.pk_bint_id=itm.fk_item_category_id join branch br1 on br1.pk_bint_id = st.fk_from_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm1 on lm1.pk_bint_id =  br1.fk_location_master_id ) as sub1 join( select br2.vchr_code as vchr_branch_code_to, lm2.int_code as vchr_loc_code_to,st.pk_bint_id as int_st_id from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm2 on lm2.pk_bint_id = br2.fk_location_master_id )     as sub2 on sub2.int_st_id = sub1.int_st_id """
            str_querry  =  str_querry +" where sub1.int_key = " + str(int_id) +" and sub1.vchr_branch_code_from='AGY' group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"

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
            for ins_data in lst_stock_transfer:
                ins_data = dict(ins_data)
                dct_back_data_date={}
                dct_back_doc_date={}
                dct_back_doc_batch_no={}
                #dct_data = {}
                #dct_data['Header'] = []

                if not dct_header:
                    dct_header['CardCode'] = 'C04984'
                    dct_header['CardName'] = 'Angamaly'
                    dct_header['MYGOAL_KEY'] = str(ins_data['int_key'])
                    dct_header['ShowRoomID'] = ins_data['vchr_branch_code_to']
                    dct_header['InvNum'] = ins_data['vchr_st_num']
                    dct_header['DealID'] = ''
                    dct_header['DocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                    dct_header['InvDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                    dct_header['BranchID'] = 1
                    dct_data['Header'].append(dct_header)
                str_item_query = str_item+ins_data['vchr_item_code']+"'"
                cur.execute(str_item_query)
                rst_item_data = cur.fetchall()
                if rst_item_data and rst_item_data[0]['imei_status']:
                    dct_line={}
                    dct_line['ItemCode'] = ins_data['vchr_item_code']
                    json_tax = ins_data['tax']
                    json_tax.pop('48')
                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    cur.execute(str_tax_code)
                    rst_tax_code = cur.fetchall()[0]['vchr_code']
                    dct_line['TaxCode']=rst_tax_code
                    dct_line['LocCode']=ins_data['vchr_loc_code_to']
                    dct_line['Quantity'] = ins_data['int_qty']
                    dct_line['WhsCode'] = ins_data['vchr_branch_code_to']
                    dct_line['Amount'] = ins_data['dbl_mrp']
                    dct_line['Costcenter'] = ins_data['vchr_branch_code_to']
                    dct_line['Store'] = ins_data['vchr_branch_code_to']
                    dct_line['Department'] = 'Finance'
                    dct_line['Brand'] = ins_data['brand_name']
                    dct_line['Employee'] = ''
                    dct_line['MnfSerial'] = ins_data['jsn_imei']['imei']
                    import pdb; pdb.set_trace()
                    str1="select ist.jsn_imei,st.dat_created,st.vchr_stktransfer_num from ist_details ist join stock_transfer st on st.pk_bint_id=ist.fk_transfer_id join branch br on br.pk_bint_id=st.fk_to_id where (ist.jsn_imei->>'imei')::jsonb ?| array"+str(ins_data['jsn_imei']['imei'])+ " and br.vchr_code='AGY'"
                    cur.execute(str1)
                    rst_back_data =cur.fetchall()
                    dct_data['Line level'].append(dct_line)
                    for data in rst_back_data:
                        dct_back_doc_date[data['vchr_stktransfer_num']]= str(data['dat_created']).split(' ')[0]
                        if data['vchr_stktransfer_num'] in dct_back_data_date:
                            if ins_data['vchr_item_code'] in dct_back_data_date[data['vchr_stktransfer_num']]:
                                dct_back_data_date[data['vchr_stktransfer_num']][ins_data['vchr_item_code']].extend(list(set(data['jsn_imei']['imei']).intersection(set(ins_data['jsn_imei']['imei']))))
                            else:
                                dct_back_data_date[data['vchr_stktransfer_num']][ins_data['vchr_item_code']]=list(set(data['jsn_imei']['imei']).intersection(set(ins_data['jsn_imei']['imei'])))
                        else:
                            dct_back_data_date[data['vchr_stktransfer_num']]={ins_data['vchr_item_code']:list(set(data['jsn_imei']['imei']).intersection(set(ins_data['jsn_imei']['imei'])))}




                elif rst_item_data and not rst_item_data[0]['imei_status']:
                    dct_line={}
                    dct_line['ItemCode'] = ins_data['vchr_item_code']
                    json_tax = ins_data['tax']
                    json_tax.pop('48')
                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    cur.execute(str_tax_code)
                    rst_tax_code = cur.fetchall()[0]['vchr_code']
                    dct_line['TaxCode']=rst_tax_code
                    dct_line['LocCode']=ins_data['vchr_loc_code_to']
                    dct_line['Quantity'] = 1
                    dct_line['WhsCode'] = ins_data['vchr_branch_code_from']
                    dct_line['Amount'] = ins_data['dbl_mrp']
                    # dct_line['Costcenter'] = ins_data['vchr_branch_code_from']
                    dct_line['Store'] = ins_data['vchr_branch_code_from']
                    dct_line['Department'] = ins_data['vchr_branch_code_from']
                    dct_line['Brand'] = ins_data['brand_name']
                    dct_line['Employee'] = ''
                    dct_line['TaxCode'] = rst_tax_code
                    dct_line['MnfSerial'] = ins_data['jsn_batch']['batch']
                    str1="select ist.jsn_batch_no,st.dat_created,st.vchr_stktransfer_num,ist.int_qty from ist_details ist join stock_transfer st on st.pk_bint_id=ist.fk_transfer_id join branch br on br.pk_bint_id=st.fk_to_id where (ist.jsn_batch_no->>'batch')::jsonb ?| array"+str(ins_data['jsn_batch']['batch'])+ " and br.vchr_code='AGY'"
                    cur.execute(str1)
                    rst_back_data =cur.fetchall()
                    for data in rst_back_data:
                        dct_back_doc_date[data['vchr_stktransfer_num']]= str(data['dat_created']).split(' ')[0]
                        if data['vchr_stktransfer_num'] in dct_back_data_date:
                            if ins_data['vchr_item_code'] in dct_back_data_date[data['vchr_stktransfer_num']]:
                                dct_back_data_date[data['vchr_stktransfer_num']][ins_data['vchr_item_code']].extend(list(set(ins_data['jsn_batch']['batch']).intersection(set(data['jsn_batch_no']['batch']))))
                                dct_back_doc_batch_no[data['vchr_stktransfer_num']][ins_data['vchr_item_code']]+=dct_back_doc_date[data['int_qty']]
                            else:
                                dct_back_data_date[data['vchr_stktransfer_num']][ins_data['vchr_item_code']]=list(set(ins_data['jsn_batch']['batch']).intersection(set(data['jsn_batch_no']['batch'])))
                                dct_back_doc_batch_no[data['vchr_stktransfer_num']][ins_data['vchr_item_code']]=dct_back_doc_date[data['int_qty']]
                        else:
                            dct_back_data_date[data['vchr_stktransfer_num']]={ins_data['vchr_item_code']:list(set(ins_data['jsn_batch']['batch']).intersection(set(data['jsn_batch_no']['batch'])))}
                    dct_data['Line level'].append(dct_line)

            # dct_header['ROW_COUNT'] = len(dct_data['Line level'])
            # dct_data['Header'].append(dct_header)
            dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
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
                                dct_org_data[data]['Header'][0]['InvNum']=data
                                dct_org_data[data]['Header'][0]['InvDate']=dct_back_doc_date[data]
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
            data = json.dumps(dct_data)
            headers = {"Content-type": "application/json"}
            str_url = " http://myglive.tmicloud.net:8084/api/In/SalesReturn"
            res_data = requests.post(str_url,data,headers=headers)
            cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='Pushed' where int_document_id ="+str(int_id)+" and int_type=3")
            soup = BeautifulSoup(res_data.text,'xml')
            if res_data.status_code == 200:
                cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
            else:
                cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
        return
    except Exception as e:
        print(str(e))




def purchase_return_api_old():

    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="nisam_pos", user="admin", password="tms@123")
            conn.autocommit = True
            # cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            # return JsonResponse({'status':'failed','reason':'cannot connect to database'})
            print(str(e))

        # for int_stock_transfer_id in lst_stock_transfer_id:
        import pdb; pdb.set_trace()

        cur.execute("select int_document_id from sap_api_track where int_type=3 and int_status=0")
        tpl_lst_master_id=cur.fetchall()
        lst_st_id =[d['int_document_id'] for d in tpl_lst_master_id]

        for int_id in lst_st_id:
            str_querry = """select sub1.int_qty, sub1.jsn_imei,sub1.jsn_batch,sub1.vchr_st_num,sub1.dat_ack, sub1.vchr_comments,sub1.int_key,sub1.vchr_item_code,sub1.vchr_item_name,sub1.dbl_mrp,sub1.vchr_branch_code_from, sub1.vchr_loc_code_from,sub2.vchr_branch_code_to,sub2.vchr_loc_code_to,sub1.tax from( select bsim.int_qty as int_qty,bsim.jsn_imei as jsn_imei ,bsim.jsn_batch_no as jsn_batch,st.vchr_stktransfer_num as vchr_st_num,st.dat_acknowledge as dat_ack ,st.vchr_remarks as vchr_comments,bsm.pk_bint_id as int_key, itm.vchr_item_code as vchr_item_code,itm.vchr_name as vchr_item_name,itm.dbl_mrp as dbl_mrp, br1.vchr_code as vchr_branch_code_from, lm1.int_code as vchr_loc_code_from,st.pk_bint_id as int_st_id,itc.json_tax_master as tax from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch_stock_details bsd on bsd.fk_transfer_details_id=ist.pk_bint_id join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join branch_stock_imei_details bsim on bsim.fk_details_id=bsd.pk_bint_id join item itm on itm.pk_bint_id = ist.fk_item_id join item_category itc on itc.pk_bint_id=itm.fk_item_category_id join branch br1 on br1.pk_bint_id = st.fk_from_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm1 on lm1.pk_bint_id =  br1.fk_location_master_id ) as sub1 join( select br2.vchr_code as vchr_branch_code_to, lm2.int_code as vchr_loc_code_to,st.pk_bint_id as int_st_id from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm2 on lm2.pk_bint_id = br2.fk_location_master_id )     as sub2 on sub2.int_st_id = sub1.int_st_id """
            str_querry  =  str_querry +" where sub1.int_key = " + str(int_id) +" and sub2.vchr_branch_code_to='AGY' group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"

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
            for ins_data in lst_stock_transfer:
                ins_data = dict(ins_data)
                #dct_data = {}
                #dct_data['Header'] = []

                if not dct_header:
                    dct_header['VendorCode'] = 'C04984'
                    dct_header['VendorName'] = 'AGY'
                    dct_header['MYGOAL_KEY'] = str(ins_data['int_key'])
                    dct_header['ShowRoomID'] = ins_data['vchr_branch_code_from']
                    dct_header['DocNum'] = 'AGY'
                    dct_header['BaseDocNum'] = 'AGY'
                    dct_header['Type'] = 1
                    dct_header['WhsCode'] = ins_data['vchr_branch_code_from']
                    dct_header['DocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                    dct_header['BaseDocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                    dct_data['Header'].append(dct_header)
                str_item_query = str_item+ins_data['vchr_item_code']+"'"
                cur.execute(str_item_query)
                rst_item_data = cur.fetchall()
                if rst_item_data and rst_item_data[0]['imei_status']:
                    for imei in ins_data['jsn_imei']['imei']:
                        dct_line={}
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        json_tax = ins_data['tax']
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        cur.execute(str_tax_code)
                        rst_tax_code = cur.fetchall()[0]['vchr_code']
                        dct_line['Quantity'] = 1
                        dct_line['WarehouseCode'] = ins_data['vchr_branch_code_from']
                        dct_line['CostPrice'] = ins_data['dbl_mrp']
                        dct_line['Costcenter'] = ins_data['vchr_branch_code_from']
                        dct_line['TaxCode'] = rst_tax_code
                        dct_line['MnfSerial'] = imei
                        dct_data['Line level'].append(dct_line)



                elif rst_item_data and not rst_item_data[0]['imei_status']:
                    for batch in ins_data['jsn_batch']['batch']:
                        dct_line={}
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        json_tax = ins_data['tax']
                        str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                        cur.execute(str_tax_code)
                        rst_tax_code = cur.fetchall()[0]['vchr_code']
                        dct_line['Quantity'] = 1
                        dct_line['WarehouseCode'] = ins_data['vchr_branch_code_from']
                        dct_line['CostPrice'] = ins_data['dbl_mrp']
                        dct_line['Costcenter'] = ins_data['vchr_branch_code_from']
                        dct_line['TaxCode'] = rst_tax_code
                        dct_line['MnfSerial'] = batch
                        dct_data['Line level'].append(dct_line)

            # dct_header['ROW_COUNT'] = len(dct_data['Line level'])
            # dct_data['Header'].append(dct_header)
            dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
            data = json.dumps(dct_data)
            headers = {"Content-type": "application/json"}
            str_url = "http://myg.tmicloud.net:85/POSOutbound.asmx/In_StockTransfer"
            res_data = requests.post(str_url,data,headers=headers)
            cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='Pushed' where int_document_id ="+str(int_id)+" and int_type=3")
            soup = BeautifulSoup(res_data.text,'xml')
            if res_data.status_code == 200:
                cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
            else:
                cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+soup.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
        return
    except Exception as e:
        print(str(e))



if __name__ == '__main__':
    purchase_return_api()
    # purchase_invoice_api()
