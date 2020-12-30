


import requests
import json
import urllib.request
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import sys

def sales_return_to_sale(str_entry,doc_date):
    """
    Used to push mygoal pos sales data to SAP
    paramerters(to SAP):
            Master data :- MYGOAL_KEY,ShowRoomID,CardCode,CardName,DocDate,DocNum,Type
            Sub details :- ItemCode,Quantity,Amount,TaxCode,Costcenter,MnfSerial,LocCode
    response(from SAP):suceess/failed
    """
    try:
        try:
            # Create connection with sqlalchemy engine
            db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/myg_pos_live2"
            # db_connetion_string = "postgres://admin:tms@123@localhost/pos"

            conn = create_engine(db_connetion_string)

        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})

        try:
            str_data = "select jsonb_agg(int_document_id) from sap_api_track where int_type = 6 and int_status in ("+str_entry+") and dat_document::Date = '"+doc_date+"'"
            rst_data = conn.execute(str_data).fetchall()
            str_file = doc_date.replace("-","")+'/SalesReturnIssues.txt'
            #file_open = open(str_file, 'w')
            #file_open.close()
            if rst_data and rst_data[0][0]:
            # if True == True:
                lst_id = set(rst_data[0][0])
                # lst_id = [16603]
                for str_id in lst_id:
                    try:
                        # Query to get sales data
                        #str_id = str(str_id)
                        print(str_id)
                        str_query_data = "select re.pk_bint_id as sales_id,br.vchr_code as showroom_code,br.fk_states_id as branch_state,cust.vchr_name as card_name,cust.fk_state_id as cust_state,pr.vchr_name as product,cust.txt_address as cust_address,cust.int_cust_type as cust_type,st.vchr_code as state_code,lom.int_code as loc,cust.vchr_code as card_code,cust.vchr_gst_no as gst,sr.vchr_invoice_num as return_num,sr.dat_invoice::DATE as return_date,sm.vchr_invoice_num as sale_num,sr.vchr_sap_key as return_id,sm.dat_invoice::DATE as sale_date,it.vchr_item_code as item_code,ic.json_tax_master as tax,re.int_qty as quantity,re.dbl_discount as discount,re.dbl_buyback as buyback,re.dbl_selling_price as amount,re.jsn_imei as imei,bd.vchr_code as brand from sales_return re join sales_master sm on sm.pk_bint_id = re.fk_sales_id join item it on it.pk_bint_id = re.fk_item_id join products pr on pr.pk_bint_id=it.fk_product_id join brands bd on bd.pk_bint_id = it.fk_brand_id join item_category ic on ic.pk_bint_id = it.fk_item_category_id join branch br on br.pk_bint_id= sm.fk_branch_id join location_master lom on br.fk_location_master_id = lom.pk_bint_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join states st on st.pk_bint_id=cust.fk_state_id left outer join sales_master sr on sr.pk_bint_id = re.fk_returned_id where sm.pk_bint_id = "+str(str_id)
                        rst_sales_data = conn.execute(str_query_data).fetchall()
                        str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                        rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

                        dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}

                        if not rst_sales_data:
                            #import pdb;pdb.set_trace()
                            print('No data found in sales return')
                            continue

                        dct_data = {}
                        dct_data['Header'] = []
                        dct_data['Line Level'] = []
                        dct_freight_discount={}
                        dct_freight_buyback={}
                        dct_header = {}
                        bln_kfc = False
                        bln_igst = False
                        for ins_data in rst_sales_data:
                            ins_data = dict(ins_data)
            # ===================================Header Data ===========================================================
            #                   dictionary to save header level data
                            if not dct_data['Header']:
                                if ins_data['branch_state'] != ins_data['cust_state']:
                                    bln_igst = True
                                elif not ins_data['gst']:
                                    bln_kfc = True
                                dct_header['MYGOAL_KEY'] = ins_data['sale_num']
                                dct_header['ShowRoomID'] = ins_data['showroom_code']
                                dct_header['BranchID'] = 1 if dct_header['ShowRoomID'] !='AGY' else 2
                                dct_header['CardCode'] = "CASH" if not ins_data['card_code'] else ins_data['card_code']
                                dct_header['CardName'] = "Cash" if not ins_data['card_code'] else ins_data['card_name']
                                dct_header['DocDate'] = datetime.strftime(ins_data['sale_date'],'%Y-%m-%d')
                                # dct_header['DocDate'] = '2020-04-12'
                                dct_header['InvDate'] = datetime.strftime(ins_data['return_date'],'%Y-%m-%d') if ins_data['return_num'] else ""
                                dct_header["BillTo"]= ins_data['state_code'] if ins_data['state_code'] else 'KL'
                                dct_header["ShipTo"]= ins_data['state_code'] if ins_data['state_code'] else 'KL'
                                dct_header["BpGSTN"]= ins_data['gst'] if ins_data['gst'] else ''
                                dct_header["Type"]= "REGULAR" if ins_data['cust_type'] !=3 else 'SEZ'
                                dct_header["CustAddr"]= ins_data['cust_address']
                                dct_header['InvNum'] = ins_data['return_id'] if ins_data['return_id'] else ""
                                dct_header['PosInvNum'] = ins_data['return_num'] if ins_data['return_num'] else ""
                                str_log_key_data = "select txt_remarks from sap_api_track where int_type = 1 and int_status in (-1,-2) and int_document_id ="+str(str_id)+";"
                                rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                                if rst_log_key_details:
                                    dct_header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get("Log_Key") if json.loads(rst_log_key_details[0]).get("Log_Key") else ""
                                dct_data['Header'].append(dct_header)
            # ====================================Line level Data==================================================================================
                            for imei in ins_data['imei']:
                                dct_line_data = {}
                                dct_line_data['ItemCode'] = ins_data['item_code']
                                dct_line_data['Quantity'] = ins_data['quantity']
                                #dct_line_data['Amount'] = -1*ins_data['amount']
                                #if ins_data['product']=='RECHARGE' or ins_data['item_code'] in ['GDC00001','GDC00002']:
                                 #   dct_line_data['Quantity'],dct_line_data['Amount'] = dct_line_data['Amount'],dct_line_data['Quantity']
                                json_tax = ins_data['tax']
                                dbl_tax=0
                                dbl_tax_to_check=0
                                if ins_data['cust_type'] !=3:
                                    if bln_igst:
                                        json_tax.pop(dct_tax['CGST'],'')
                                        json_tax.pop(dct_tax['SGST'],'')
                                        dbl_tax = json_tax[dct_tax['IGST']]
                                        dbl_tax_to_check= json_tax[dct_tax['IGST']]
                                    elif bln_kfc:
                                        json_tax.pop(dct_tax['IGST'],'')
                                        json_tax[dct_tax['KFC']] = 1
                                        dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                        dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]+1
                                    else:
                                        json_tax.pop(dct_tax['IGST'],'')
                                        dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                        dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                                    rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                                else:
                                    #if bln_igst:
                                    rst_tax_code='IGST0'
                                    #else:
                                     #   rst_tax_code='GST0'
                                rst_tax_code = rst_tax_code if rst_tax_code!='GST0K' else 'GST0'
                                dct_line_data['TaxCode'] = rst_tax_code
                                dct_line_data['Amount'] = -1*((ins_data['amount']+ins_data['discount']+ins_data['buyback'])/((100+dbl_tax)/100))
                                if ins_data['product']=='RECHARGE' or ins_data['item_code'] in ['GDC00001','GDC00002']:
                                    dct_line_data['Quantity'],dct_line_data['Amount'] = dct_line_data['Amount'],dct_line_data['Quantity']
                                dct_line_data['WhsCode'] = ins_data['showroom_code']
                                dct_line_data['Store'] = ins_data['showroom_code']
                                dct_line_data['Department'] = "SAL"
                                dct_line_data['Brand'] = ins_data['brand']
                                dct_line_data['Employee'] = ""
                                dct_line_data['MnfSerial'] = [imei]
                                dct_line_data['LocCode'] = ins_data['loc']
                                dct_line_data['SalesDiscount'] = -1*ins_data['discount'] if ins_data['discount'] else 0
                                dct_line_data['BuyBack'] = -1*ins_data['buyback'] if ins_data['buyback'] else 0
                                if dbl_tax_to_check and (dbl_tax_to_check%1) ==0:
                                   dbl_tax_to_check = int(dbl_tax_to_check)

                                if ins_data['discount'] and rst_tax_code not in dct_freight_discount:

                                    dct_freight_discount[rst_tax_code] = {}
                                    dct_freight_discount[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                                    dct_freight_discount[rst_tax_code]['amount'] = round(ins_data['discount']/((100+dbl_tax)/100),2)
                                elif ins_data['discount']:
                                    dct_freight_discount[rst_tax_code]['amount'] += round(ins_data['discount']/((100+dbl_tax)/100),2)

                                if ins_data['buyback'] and rst_tax_code not in dct_freight_buyback:
                                    dct_freight_buyback[rst_tax_code] = {}
                                    dct_freight_buyback[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                                    dct_freight_buyback[rst_tax_code]['amount'] = round(ins_data['buyback']/((100+dbl_tax)/100),2)
                                elif ins_data['buyback']:
                                    dct_freight_buyback[rst_tax_code]['amount'] += round(ins_data['buyback']/((100+dbl_tax)/100),2)
                                dct_data['Line Level'].append(dct_line_data)

                        dct_data['Freight']=[]
                        if not dct_data['Line Level']:
                            continue
                        if dct_freight_buyback:
                            for str_buy_back in dct_freight_buyback:
                                dct_freight= {}
                                rst_code=conn.execute("select vchr_code from freight where upper(vchr_category)='BUY BACK' and vchr_tax_code='"+dct_freight_buyback[str_buy_back]['tax_code']+"' and int_status=0").fetchall()
                                dct_freight["ExpCode"]=rst_code[0][0] if rst_code else '-1'
                                dct_freight["LineTotal"]=dct_freight_buyback[str_buy_back]['amount']
                                dct_freight["TaxCode"]=str_buy_back
                                dct_freight["Store"]= dct_data['Line Level'][0]["Store"]
                                dct_freight["Department"]= dct_data['Line Level'][0]["Department"]
                                dct_freight["Employees"]= dct_data['Line Level'][0]["Employee"]
                                dct_freight["Brand"]= ""
                                dct_data['Freight'].append(dct_freight)
                        if dct_freight_discount:
                            for str_discount in dct_freight_discount:
                                dct_freight= {}
                                rst_code=conn.execute("select vchr_code from freight where upper(vchr_category)='SALES DISCOUNT' and vchr_tax_code='"+dct_freight_discount[str_discount]['tax_code']+"' and int_status=0").fetchall()
                                dct_freight["ExpCode"]=rst_code[0][0] if rst_code else '-1'
                                dct_freight["LineTotal"]=dct_freight_discount[str_discount]['amount']
                                dct_freight["TaxCode"]=str_discount
                                dct_freight["Store"]= dct_data['Line Level'][0]["Store"]
                                dct_freight["Department"]= dct_data['Line Level'][0]["Department"]
                                dct_freight["Employees"]= dct_data['Line Level'][0]["Employee"]
                                dct_freight["Brand"]= ""
                                dct_data['Freight'].append(dct_freight)
                        if not dct_data['Freight']:
                            dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
                        headers = {"Content-type": "application/json"}
                        data = json.dumps(dct_data)
                        print("\nID : ",str(str_id))
                        print("Data : ",data)

                        # str_log_key_data = "select txt_remarks from sap_api_track where int_type = 6 and int_status = -1 and int_document_id ="+str_id+";"
                        # # import pdb; pdb.set_trace()
                        # rst_log_key_details =conn.execute(str_log_key_data).fetchall()
                        # print("\nError : ",rst_log_key_details[0].values()[0])
#                        import pdb;pdb.set_trace()
                        url = 'http://13.71.18.142:8086/api/In/SalesReturn'
                        try:
                            res_data = requests.post(url,data,headers=headers)
                            conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str(str_id)+" and int_type=6")
                            response = json.loads(res_data.text)
                            print(response)
                            if str(response['status']).upper() == 'SUCCESS':
                                conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=6")
                                conn.execute("update receipt set vchr_sap_key ='"+str(response['sapKey'])+"' where fk_sales_return_id="+str(str_id))
                            else:
                                file_object = open(str_file, 'a')
                                file_object.write(data)
                                file_object.write('\n\n')
                                file_object.write(res_data.text)
                                file_object.write('\n\n\n\n')
                                file_object.close()
                                if str_entry == "0":
                                    conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=6")
                                else:
                                    conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(str_id)+" and int_type=6")

                        except Exception as e:
                            raise

                    except Exception as e:
                        print(e)
                        continue
            return True


        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            raise

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print(str(e))

if __name__ == '__main__':
    sales_return_to_sale()

