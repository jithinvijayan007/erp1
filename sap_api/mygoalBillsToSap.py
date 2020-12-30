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
# from serviceToSap import service_invoice_to_sap
from collections import OrderedDict
import sys

def bills_to_sap(str_entry,doc_date):
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
            # db_connetion_string = "postgres://admin:uDS$CJ8j@localhost/pos_sap"
            conn = create_engine(db_connetion_string)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        try:
            str_file = doc_date.replace("-","")+'/BillsIssues.txt'
            lst_smt_chc = []
            rst_smt_chce = conn.execute("select array_agg(int_document_id) as lst_id from sap_api_track sat join sales_details sd on sd.fk_master_id = sat.int_document_id where sat.int_type=1 and int_status in ("+str_entry+") and sd.int_sales_status=2 and dat_document::Date = '"+doc_date+"';").fetchall()
            if rst_smt_chce and rst_smt_chce[0][0]:
                lst_smt_chc = set(rst_smt_chce[0]['lst_id'])
                print('Smart choice --------------------------------------------------------------------------------------------------------')
                #lst_smt_chc={106842,108034,106839,107307,106191}
                #lst_smt_chc={109737,111650,111774}
                success_smart_choice = False
                while not success_smart_choice:
                    success_smart_choice = smart_choice_to_pos(lst_smt_chc,str_entry,doc_date)
            tpl_lst_master_id=conn.execute("select int_document_id from sap_api_track where int_type=1 and int_status in ("+str_entry+") and dat_document::Date = '"+doc_date+"';").fetchall()
            lst_bill_id =[d['int_document_id'] for d in tpl_lst_master_id]
            #lst_bill_id=[108932,115586,108848,108716,108852,108986,115742,109377,106678,106399,105971,106393,106761,107110,105641,106930,105831,107233,108131,105890,107409,107771,107917,108092,107808,106494,108401,108544,108534,109104,106522,109711,108687,108580,109703,109693,116824,109713,107700,109687,116573,106263,109094,108886,106925,109708,109698,109717,109689,108911,108724,109294,109009,108897,109836,109607,109379,110059,110309,109851,110498,111059,110386,110471,110537,110569,110616,110506,111054,108980,111298,108760,108808,111280,108763,108832,109200,109263,109426,109402,109327,109429,109462,109558,109507,109508,109493,109575,109629,109622,109630,109665,109767,110119,109743,109802,110167,110233,110135,109779,110154,110256,109852,110156,110189,109048,109019,109516,109051,109055,109235,109069,109224,109226,109276,108910,109360,109253,109435,109332,110087,109732,110053,110024,109730,110080,110124,110142,110108,110214,110212,110226,109869,110113,110181,110005,109945,109966,109985,110000,110022,109982,110025,110615,110707,108699,110418,110447,110331,110543,110505,110520,110307,110587,110579,110869,110584,110683,110789,110877,110885,110633,110538,110667,110670,110671,110668,110619,110623,110564,110634,110899,110845,110872,110720,110786,111148,110934,110956,110914,110996,110994,111007,111024,108949,111162,111011,111197,111220,111023,111237,111185,111218,111340,111322,111527,111777,111370,111368,111377,111646,111243,111420,111302,111311,111431,111485,111490,111627,111512,111771,111586,111611,111620,111784,109163,111803,111674,111711,111734,109291,110225,109351,110227,109865,110407,110426,110976]
            #lst_bill_id=[109094,109622]
            #lst_bill_id=[105574,107722,107564,107068,106794,106703,107343,107588,106741,107593,106126,107790,108230,109005,108971,108277,111331,106975,109892,109900,109217,109725,109847,110405,109339,111546,109203,109041,109513,109463,109593,109583,108891,109633,109663,110235,109763,109614,109626,109837,109192,109876,109342,109441,110061,110063,109456,110439,110343,110741,110881,109938,110368,110442,110452,110648,110382,110570,110606,110959,110646,110705,110462,110457,110602,110535,110936,110847,110852,110883,110925,111299,111165,111229,108877,111164,111053,111186,111267,111374,111329,111305,111727,111278,111334,111553,111547,111338,111348,111580,111585,111622,111596,111744,111660,111408,111835,111124,109348,109382,109529,111590,111127,108739,111001,111509]
            #lst_bill_id=[]    
            print("Bill Sales ---------------------------------------------------------------------------------------------")
            print(len(lst_bill_id),"Bills to push")
            conn.execute("update sales_master SET jsn_deduction=jsn_deduction-'162' where (jsn_deduction->>'162')::numeric= 0")
            conn.execute("update sales_master SET jsn_deduction=jsn_deduction-'118' where (jsn_deduction->>'118')::numeric= 0")
            conn.execute("update sales_master SET jsn_deduction=jsn_deduction-'273' where (jsn_deduction->>'273')::numeric= 0")
            rst_freight = conn.execute("select array_agg(vchr_category||':'||vchr_code) from freight").fetchall()[0][0]
            dct_freight_data = {str_freight.split(':')[0]:str_freight.split(':')[1] for str_freight in rst_freight}
            for str_id in set(lst_bill_id):
                #time.sleep(5)
                try:
                    if str_id not in lst_smt_chc:
                        str_id=str(str_id)
                        # Query to get sales data

                        str_query_data = "select sm.int_sale_type,sm.pk_bint_id as sales_id,pr.vchr_name as product,sm.jsn_deduction as deduction,sm.jsn_addition as addition,sd.dbl_buyback as buyback,br.vchr_code as showroom_code,br.fk_states_id as branch_state_id,br.pk_bint_id as sh_id,cust.vchr_name as card_name,cust.int_mobile as cust_mobile,cust.int_cust_type as cust_type,cust.vchr_gst_no as gst_no,cust.txt_address as cust_address,cust.vchr_code as card_code,cust.pk_bint_id as cust_id,cust.fk_state_id as cust_state_id,st.vchr_code as state_code,cust.int_cust_type as cust_type,sm.dat_invoice as doc_date,sm.vchr_invoice_num as doc_num,it.vchr_item_code as item_code,it.imei_status,it.pk_bint_id as item_id,itc.json_tax_master as tax,lm.int_code as loc_code,sd.int_qty as quantity,(sd.dbl_selling_price) as amount,sd.json_imei as mnf_serial,sd.vchr_batch batch_no,sd.dbl_tax as tax_amount,sd.dbl_discount as discount,bd.vchr_code as brand,pd.vchr_name as product from sales_master sm join sales_details sd on sm.pk_bint_id=sd.fk_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join location_master lm on lm.pk_bint_id = br.fk_location_master_id join sales_customer_details cust on cust.pk_bint_id = sm.fk_customer_id join states st on st.pk_bint_id=cust.fk_state_id join item it on it.pk_bint_id = sd.fk_item_id join brands bd on bd.pk_bint_id=it.fk_brand_id join products pd on pd.pk_bint_id=it.fk_product_id join item_category itc on itc.pk_bint_id = it.fk_item_category_id join products pr on pr.pk_bint_id=it.fk_product_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where sm.pk_bint_id = "+str_id+" and sd.int_sales_status=1;"
                        rst_sales_data = conn.execute(str_query_data).fetchall()
                        print(rst_sales_data,"Result set")
                        if not rst_sales_data:
                            continue
                        # Query to get payment details
                        str_payment_data = "select sm.pk_bint_id as sales_id,br.pk_bint_id as sh_id,br.vchr_code as showroom_code,pd.vchr_name as fin_code,pd.vchr_reff_number as tr_id,pd.dbl_receved_amt as amount,pd.int_fop as fop,pd.vchr_card_number as card_num,pd.fk_bank_id as bank_id,pd.dat_created_at::DATE as transfer_date,case when pd.int_fop =0 then 'Financier-Payment' when pd.int_fop =1 then 'Cash' when pd.int_fop =2 then 'Debit Card' when pd.int_fop =3 then 'Credit Card' when pd.int_fop =5 then 'PAYTM' when pd.int_fop =6 then 'PAYTM MALL' when pd.int_fop = 7 then 'Bharath QR' else 'Cheque' end as payment_mode from sales_master sm join payment_details pd on sm.pk_bint_id=pd.fk_sales_master_id join branch br on br.pk_bint_id=sm.fk_branch_id join sap_api_track sap on sap.int_document_id = sm.pk_bint_id and sap.int_type=1 where pd.int_fop!=4 and pd.fk_sales_master_id = "+str_id+";"
                        rst_payment_details = conn.execute(str_payment_data).fetchall()

                        # Query to get advance receipt data
                        str_advance_data = "select rim.fk_sales_master_id as sale_id,rc.pk_bint_id as adv_no,rc.int_fop as fop,rc.vchr_sap_key,rim.dbl_amount from receipt_invoice_matching rim join receipt rc on rim.fk_receipt_id = rc.pk_bint_id where int_pstatus = 0 and fk_sales_return_id is null and int_receipt_type in (1,2) and rim.dbl_amount > 0 and rim.fk_sales_master_id="+str_id+";"
                        rst_advance_details = conn.execute(str_advance_data).fetchall()

                        # Query to get bank details
                        str_bank_data = "select array_agg(pk_bint_id||':' ||vchr_name) from bank;"
                        rst_bank_details = conn.execute(str_bank_data).fetchall()[0][0]
                        # create dictionary of bank and pk_bint_id
                        dct_bank = {str_bank.split(':')[0]:str_bank.split(':')[1] for str_bank in rst_bank_details}

                        str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                        rst_tax_details = conn.execute(str_tax_master).fetchall()[0][0]

                        str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id {} and acm.vchr_category = '{}';"

                        dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}

                        if not rst_sales_data:
                            print('No data found')
                            continue

                        dct_data = OrderedDict()
                        dct_data['Header'] = []
                        dct_data['Line level'] = []
                        dct_data['Payment Level'] = []
                        dct_freight_discount={}
                        dct_freight_buyback={}
                        dct_header = {}
                        bln_kfc = False
                        bln_igst = False
                        dbl_buyback = 0
                        str_fin_code = ""
                        str_deal_id = ""
                        for ins_data in rst_sales_data:
                            ins_data = dict(ins_data)
            #                 if 'MYGOAL_KEY' not in dct_header:
                            if 'Log_Key' not in dct_header:
            # # ===================================Header Data ===========================================================
                                if ins_data['branch_state_id'] != ins_data['cust_state_id']:
                                    bln_igst = True
                                elif not ins_data['gst_no']:
                                    bln_kfc = True
                                if ins_data['int_sale_type'] == 2:
                                    card_code = 'AMAZONE'
                                    card_name = 'Amazon Customer'
                                elif ins_data['int_sale_type'] == 3:
                                    card_code = 'FLIPKART'
                                    card_name = 'Flipkart Customer'
                                elif ins_data['int_sale_type'] == 4:
                                    card_code = 'E-COMMERCE'
                                    card_name = 'E-commerce Customer'
                                elif ins_data['card_code']:
                                    card_code = ins_data['card_code']
                                    card_name = ins_data['card_name']
                                else:
                                    card_code = "CASH"
                                    card_name = "Cash"
                                dct_header['MYGOAL_KEY'] = ins_data['doc_num']
                                dct_header['ShowRoomID'] = ins_data['showroom_code']
                                dct_header['CardCode'] = card_code
                                dct_header['CardName'] = card_name
                                dct_header['CustomerName'] = ins_data['card_name']
                                dct_header["BillTo"]= ins_data['state_code'] if ins_data['state_code'] else 'KL'
                                dct_header["ShipTo"]= ins_data['state_code'] if ins_data['state_code'] else 'KL'
                                dct_header["Type"]= "REGULAR" if ins_data.get('cust_type') !=3 else 'SEZ'
                                dct_header["CustAddr"]= ins_data['cust_address']
                                dct_header['MobileNumber'] = ins_data['cust_mobile']
                                dct_header['BpGSTN'] = ins_data['gst_no'] if ins_data['gst_no'] else ""
                                dct_header['DealID'] = ""
                                dct_header['Log_Key'] = ""
                                dct_header['Financier'] = ""
                                dct_header['BranchID'] = 1 if ins_data['showroom_code']!='AGY' else 2
                                dct_header['DealID'] = ""

                                dct_header['Log_Key'] = ""

                                # # fetching log_key from sap_api_track
                                # if int_entry == '-1':
                                str_log_key_data = "select txt_remarks from sap_api_track where int_type = 1 and int_status in (-1,-2) and int_document_id ="+str_id+";"
                                rst_log_key_details = conn.execute(str_log_key_data).fetchall()
                                if rst_log_key_details:
                                    dct_header['Log_Key'] = json.loads(rst_log_key_details[0].values()[0]).get("Log_Key") if json.loads(rst_log_key_details[0].values()[0]).get("Log_Key") else ""

                                dct_header['DocDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                                # dct_header['DocDate'] = '2020-04-12'
                                jsn_addition = ins_data['addition']
                                jsn_deduction = ins_data['deduction']
            # ====================================Line Data==================================================================================
                            dct_line_data = {}
                            dct_line_data['ItemCode'] = ins_data['item_code']
                            dct_line_data['Quantity'] = ins_data['quantity']
                            #dct_line_data['DiscountPercent'] = (ins_data['discount']/ins_data['amount'])*100 if ins_data['discount'] else 0
                            dct_line_data['DiscAmnt'] = ins_data['discount'] if ins_data['discount'] else 0
                            # dct_line_data['Amount'] = round(ins_data['amount'],2)


                            json_tax = ins_data['tax']
                            if ins_data.get('cust_type') !=3:
                                dbl_tax=0
                                dbl_tax_to_check=0
                                if bln_igst:
                                    if dct_tax['CGST'] in json_tax or dct_tax['SGST'] in json_tax:
                                        json_tax.pop(dct_tax['CGST'],'')
                                        json_tax.pop(dct_tax['SGST'],'')

                                    if dct_tax['IGST'] in json_tax:
                                        dbl_tax = json_tax[dct_tax['IGST']]
                                        dbl_tax_to_check= json_tax[dct_tax['IGST']]

                                elif bln_kfc:
                                    if dct_tax['IGST'] in json_tax :
                                        json_tax.pop(dct_tax['IGST'],'')
                                        json_tax[dct_tax['KFC']] = 1
                                        dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                        dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]+1
                                else:
                                    if dct_tax['IGST'] in json_tax :
                                        json_tax.pop(dct_tax['IGST'],'')
                                        dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                        dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                                str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                                # import pdb; pdb.set_trace()
                                if conn.execute(str_tax_code).fetchall():
                                    rst_tax_code = conn.execute(str_tax_code).fetchall()[0][0]
                                    # print(conn.execute(str_tax_code).fetchall()[0][0])
                                elif not  json_tax or ins_data['item_code'] in ['REC00006','REC00007','REC00008']:
                                    if bln_igst:
                                        rst_tax_code = "IGST0"
                                    elif bln_kfc:
                                        rst_tax_code = "GST0"
                                    else:
                                        rst_tax_code = "GST0"

                                    print(rst_tax_code)

                                    # import pdb; pdb.set_trace()
                            else:
                                dbl_tax_to_check = 0
                                dbl_tax = 0
                                #if bln_igst:
                                rst_tax_code = 'IGST0'
                                #else:
                                #rst_tax_code = 'GST0'

                            #import pdb;pdb.set_trace()
                            dct_line_data['Amount'] = round((ins_data['amount']+ins_data['discount']+ins_data['buyback'])/((100+dbl_tax)/100),2)
                            if ins_data['product'] =='RECHARGE' or ins_data['item_code'] in ['GDC00001','GDC00002']:
                                dct_line_data['Quantity'],dct_line_data['Amount']=dct_line_data['Amount'],dct_line_data['Quantity']
                            dct_line_data['TaxCode'] = rst_tax_code if rst_tax_code != 'GST0K' else 'GST0'
                            dct_line_data['Store'] = ins_data['showroom_code']
                            dct_line_data['Department'] = "SAL"
                            # print(ins_data['item_code'])
                            if ins_data['brand']:
                                dct_line_data['Brand'] = ins_data['brand'].upper().replace(" ", "") if ins_data['brand'].upper() != 'MYG' else 'myG'
                            else:
                                dct_line_data['Brand'] = ""
                            dct_line_data['Employee'] = "" #MYGC-935
                            #if ins_data['doc_num'] == 'I-TPVD-8744':
                               #import pdb;pdb.set_trace()
                            if ins_data['imei_status']:#Item with imei number
                                dct_line_data['MnfSerial'] = ins_data['mnf_serial']
                                if len(dct_line_data['MnfSerial']) >= 1 and dct_line_data['MnfSerial'][0] and ins_data['product'] not in ['SERVICE','RECHARGE','SIM']:
                                    #if not ins_data['mnf_serial'][0]: 
                                    #    file_ptr =open("ImeiMissing.txt",'a')
                                    #    file_ptr.write(ins_data['doc_num']+'\n')
                                    #    file_ptr.close()
                                    dct_line_data['MnfSerial'] = [str_imei.strip() for str_imei in dct_line_data['MnfSerial']]
                                #dct_line_data['MnfSerial'] = [ins_data['mnf_serial'][0].lstrip()]
                                #if len(ins_data['mnf_serial']) >1:
                                 #   print(ins_data['mnf_serial'],"Imei")
                                  #  import pdb;pdb.set_trace()
                            else:#Item with serial number
                                dct_line_data['MnfSerial'] = [ins_data['mnf_serial'][0]]
                                if len(dct_line_data['MnfSerial']) >= 1 and dct_line_data['MnfSerial'][0] and ins_data['product'] not in ['SERVICE','RECHARGE','SIM']:
                                      #if not ins_data['mnf_serial'][0]: 
                                      #   file_ptr =open("ImeiMissing.txt",'a')
                                      #   file_ptr.write(ins_data['doc_num']+'\n')
                                      #   file_ptr.close()
                                      dct_line_data['MnfSerial'] = [str_imei.strip() for str_imei in dct_line_data['MnfSerial']]
                                #dct_line_data['MnfSerial'] = [ins_data['mnf_serial'][0].lstrip()]

                            if ins_data['product'] in ['SERVICE','RECHARGE','CARE PLUS','SIM']: #['SRV00002','GDC00002','GDC00001'] or :#service item
                                dct_line_data['MnfSerial'] = []
                            dct_line_data['LocCode'] = ins_data['loc_code']
                            dct_line_data['SalesDiscount'] = ins_data['discount'] if ins_data['discount'] else 0
                            dct_line_data['BuyBack'] = ins_data['buyback'] if ins_data['buyback'] else 0
                            if dbl_tax_to_check and (dbl_tax_to_check%1) ==0:
                               dbl_tax_to_check = int(dbl_tax_to_check)

                            if ins_data['discount'] and rst_tax_code not in dct_freight_discount:

                                dct_freight_discount[rst_tax_code] = {}
                                dct_freight_discount[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                                dct_freight_discount[rst_tax_code]['amount'] = round(ins_data['discount']/((100+dbl_tax)/100),3)
                            elif ins_data['discount']:
                                dct_freight_discount[rst_tax_code]['amount'] += round(ins_data['discount']/((100+dbl_tax)/100),3)

                            if ins_data['buyback'] and rst_tax_code not in dct_freight_buyback:
                                dct_freight_buyback[rst_tax_code] = {}
                                dct_freight_buyback[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                                dct_freight_buyback[rst_tax_code]['amount'] = round(ins_data['buyback']/((100+dbl_tax)/100),3)
                            elif ins_data['buyback']:
                                dct_freight_buyback[rst_tax_code]['amount'] += round(ins_data['buyback']/((100+dbl_tax)/100),3)

                            dct_data['Line level'].append(dct_line_data)
                        dct_data['Header'].append(dct_header)
                        dct_advance = {}

                        # craete dictionary of advance amount
                        if ins_data.get('cust_type') in [1,2]:
                            dct_data['Payment Level'] = [{"BankName": -1, "AdvanceReceiptNo": -1, "TranId": -1, "TransferDate": "", "PaymentMode": "", "AcctCode": "", "ChequeNum": -1, "Amount":-1}]
                        else:
                            dct_data['Payment Level'] = [{"BankName": -1, "AdvanceReceiptNo": -1, "TranId": -1, "TransferDate": "", "PaymentMode": "", "AcctCode": "", "ChequeNum": -1, "Amount":-1}]
                            if rst_advance_details:
                                dct_data['Payment Level'] = []
                                for ins_adv in rst_advance_details:
                                    dct_advance[ins_adv['sale_id']] = {'receipt_num':ins_adv['vchr_sap_key'],'dbl_amount':ins_adv['dbl_amount']}
                                    dct_payment = {}
                                    dct_payment['BankName'] = -1
                                    dct_payment['AdvanceReceiptNo'] = ins_adv['vchr_sap_key']
                                    dct_payment['TranId'] = -1
                                    dct_payment['TransferDate'] = datetime.strftime(ins_data['doc_date'],'%Y-%m-%d')
                                    dct_payment['PaymentMode'] = "Customer-Advance"
                                    dct_payment['ChequeNum'] = -1
                                    dct_payment['Amount'] = ins_adv['dbl_amount']
                                    #import pdb;pdb.set_trace()
                                    if ins_adv['fop'] == 1:
                                        str_acc_type = 'CASH A/C'
                                        str_branch= "="+str(ins_data['sh_id'])
                                    elif ins_adv['fop'] in [2,3,4,5,6]:
                                        str_acc_type = 'TRANSFER'
                                        str_branch='is null'
                                    elif ins_adv['fop'] ==7:
                                        rst_acc = conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id is null and acm.vchr_category = 'PAYTM'").fetchall()
                                    elif ins_adv['fop'] ==8:
                                        str_acc_type = 'PAYTM MALL'
                                        str_branch='is null'
                                    elif ins_adv['fop'] ==9:
                                        str_acc_type = 'BHARATH QR'
                                        str_branch='is null'
                                    #if ins_adv[']:
                                    if not ins_adv['fop'] ==7:
                                        rst_acc = conn.execute(str_account_code.format(str_branch,str_acc_type)).fetchall()
                                    dct_payment['AcctCode'] = ""
                                    if rst_acc:
                                        dct_payment['AcctCode'] = rst_acc[0][0]
                                    dct_data['Payment Level'].append(dct_payment)

                            if rst_payment_details:
                                if not rst_advance_details:
                                    dct_data['Payment Level'] = []
                                for ins_payment in rst_payment_details:
                                    dct_payment = {}
                                    dct_payment['BankName'] = -1
                                    if ins_payment['bank_id']:
                                        dct_payment['BankName'] = dct_bank[str(ins_payment['bank_id'])]
                                    dct_payment['AdvanceReceiptNo'] = -1
                                    # Advance Receipt number
                                    # if 0 and ins_payment['sales_id'] in dct_advance:
                                    #     dct_payment['AdvanceReceiptNo'] = dct_advance[ins_payment['sales_id']]['receipt_num']
                                    dct_payment['TranId'] = ins_payment['tr_id'] if ins_payment['tr_id'] else -1

                                    dct_payment['TransferDate'] = datetime.strftime(ins_payment['transfer_date'],'%Y-%m-%d')
                                    dct_payment['PaymentMode'] = ins_payment['payment_mode']
                                    if ins_payment['fop'] == 0:
                                        str_fin_code = ins_payment['fin_code']
                                        str_deal_id = ins_payment['tr_id']
                                    if ins_payment['fop'] in [1,0]:
                                        str_acc_type = 'CASH A/C'
                                        str_branch= "="+str(ins_payment['sh_id'])
                                    elif ins_payment['fop'] in [2,3,4]:
                                        str_acc_type = 'TRANSFER'
                                        str_branch='is null'
                                    elif ins_payment['fop'] ==5:
                                        rst_acc = conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id is null and acm.vchr_category = 'PAYTM'").fetchall()
                                    elif ins_payment['fop'] ==6:
                                        str_acc_type = 'PAYTM MALL'
                                        str_branch='is null'
                                    elif ins_payment['fop'] == 7:
                                        str_acc_type = 'BHARATH QR'
                                        str_branch = 'is null'
                                    if ins_payment['fop'] !=5:
                                        rst_acc = conn.execute(str_account_code.format(str_branch,str_acc_type)).fetchall()
                                    dct_payment['AcctCode'] = ""
                                    if rst_acc:
                                        dct_payment['AcctCode'] = rst_acc[0][0]
                                    dct_payment['ChequeNum'] = ins_payment['card_num'] if ins_payment['card_num'] else -1
                                    dct_payment['Amount'] = ins_payment['amount'] if ins_payment['amount']  else 0
                                    # add advance amount with payment details amount
                                    #if 0 and ins_payment['sales_id'] in dct_advance:
                                        #dct_payment['Amount'] += dct_advance[ins_payment['sales_id']]['dbl_amount']
                                    if ins_payment['fop'] !=4:
                                        dct_data['Payment Level'].append(dct_payment)
                        #import pdb;pdb.set_trace()
                        if str_fin_code:
                            dct_data['Header'][0]['Financier'] = str_fin_code
                            dct_data['Header'][0]['DealID']= str_deal_id
                        dct_data['Freight']=[]
                        if jsn_addition:
                            for ins_addition in jsn_addition:
                                dct_freight= {}

                                #add_acc_code=conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where acm.pk_bint_id="+ins_addition).fetchall()[0][0]
                                add_acc_code=conn.execute("select upper(vchr_acc_name) from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where acm.pk_bint_id="+ins_addition).fetchall()[0][0]
                                dct_freight["ExpCode"]=dct_freight_data[add_acc_code]
#                                dct_freight["ExpCode"]=6
                                dct_freight["LineTotal"]=float(jsn_addition[ins_addition])
                                dct_freight["LineTotal"]=round(dct_freight["LineTotal"],2)
                                dct_freight["TaxCode"]="GST0"
                                dct_freight["Store"]= dct_data['Line level'][0]["Store"]
                                dct_freight["Department"]= dct_data['Line level'][0]["Department"]
                                dct_freight["Employees"]= dct_data['Line level'][0]["Employee"]
                                dct_freight["Brand"]= ""
                                if float(jsn_addition[ins_addition]) :
                                    dct_data['Freight'].append(dct_freight)
                        if jsn_deduction:
                            for ins_deduction in jsn_deduction:
                                dct_freight= {}
                                #add_acc_code=conn.execute("select vchr_acc_code from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where acm.pk_bint_id="+ins_deduction).fetchall()[0][0]
                                add_acc_code=conn.execute("select upper(vchr_acc_name) from chart_of_accounts coa join accounts_map acm on acm.fk_coa_id=coa.pk_bint_id where acm.pk_bint_id="+ins_deduction).fetchall()[0][0]
                                dct_freight["ExpCode"]=dct_freight_data[add_acc_code]
 #                               dct_freight["ExpCode"]=6
                                dct_freight["LineTotal"]=(-1)*float(jsn_deduction[ins_deduction])
                                dct_freight["LineTotal"]=round(dct_freight["LineTotal"],2)
                                dct_freight["TaxCode"]="GST0"
                                dct_freight["Store"]= dct_data['Line level'][0]["Store"]
                                dct_freight["Department"]= dct_data['Line level'][0]["Department"]
                                dct_freight["Employees"]= dct_data['Line level'][0]["Employee"]
                                dct_freight["Brand"]= ""
                                if float(jsn_deduction[ins_deduction]):
                                    dct_data['Freight'].append(dct_freight)
                        if dct_freight_buyback:
                            for str_buy_back in dct_freight_buyback:
                                dct_freight= {}
                                rst_code=conn.execute("select vchr_code from freight where upper(vchr_category)='BUY BACK' and vchr_tax_code='"+dct_freight_buyback[str_buy_back]['tax_code']+"' and int_status=0").fetchall()
                                dct_freight["ExpCode"]=rst_code[0][0] if rst_code else '-1'
                                dct_freight["LineTotal"]=(-1)*float(dct_freight_buyback[str_buy_back]['amount'])
                                dct_freight["LineTotal"]=round(dct_freight["LineTotal"],2)
                                dct_freight["TaxCode"]=str_buy_back
                                dct_freight["Store"]= dct_data['Line level'][0]["Store"]
                                dct_freight["Department"]= dct_data['Line level'][0]["Department"]
                                dct_freight["Employees"]= dct_data['Line level'][0]["Employee"]
                                dct_freight["Brand"]= ""
                                dct_data['Freight'].append(dct_freight)
                        if dct_freight_discount:
                            for str_discount in dct_freight_discount:
                                dct_freight= {}
                                rst_code=conn.execute("select vchr_code from freight where upper(vchr_category)='SALES DISCOUNT' and vchr_tax_code='"+dct_freight_discount[str_discount]['tax_code']+"' and int_status=0").fetchall()
                                dct_freight["ExpCode"]=rst_code[0][0] if rst_code else '-1'
                                dct_freight["LineTotal"]=(-1)*float(dct_freight_discount[str_discount]['amount'])
                                dct_freight["LineTotal"]=round(dct_freight["LineTotal"],2)
                                dct_freight["TaxCode"]=str_discount
                                dct_freight["Store"]= dct_data['Line level'][0]["Store"]
                                dct_freight["Department"]= dct_data['Line level'][0]["Department"]
                                dct_freight["Employees"]= dct_data['Line level'][0]["Employee"]
                                dct_freight["Brand"]= ""
                                dct_data['Freight'].append(dct_freight)
                        if not dct_data['Freight']:
                            dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
                        headers = {"Content-type": "application/json"}
                        if ins_data['doc_num'] in ['I-CHL-7681']:
                            print(dct_data)
                            import pdb;pdb.set_trace()
#                        dct_data['Payment Level'] = [{"BankName": -1, "AdvanceReceiptNo": -1, "TranId": -1, "TransferDate": "", "PaymentMode": "", "AcctCode": "", "ChequeNum": -1, "Amount":-1}]
                        data = json.dumps(dct_data)
                        url = 'http://13.71.18.142:8086/api/In/Bill'
                        print("ID : ",str_id)
                        print("Data : ",data,"\n")
                        print("Pushed at ",datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
#                        import pdb;pdb.set_trace()
                        try:
                            res_data = requests.post(url,data,headers=headers)
                            conn.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=1")
                            response = json.loads(res_data.text)
                            print("Response : ",response)
                            if str(response['status']).upper() == 'SUCCESS':
                                conn.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(res_data.text)+"' where int_document_id ="+str_id+" and int_type=1")
                                conn.execute("update sales_master set vchr_sap_key='"+str(response['sapKey'])+"',dat_sap_doc_date='"+str(datetime.now())+"' where pk_bint_id="+str_id)
                            else:
                                file_object = open(str_file, 'a')
                                file_object.write(data)
                                file_object.write('\n\n')
                                file_object.write(res_data.text)
                                file_object.write('\n\n\n\n')
                                file_object.close()
                                response.pop('message')
                                str_error_text = json.dumps(response)
                                if str_entry == '0':
                                    conn.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(str_error_text)+"' where int_document_id ="+str_id+" and int_type=1")
                                else:
                                    conn.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(str_error_text)+"' where int_document_id ="+str_id+" and int_type=1")

                        except Exception as e:
                            raise

                except Exception as e:
                    #import pdb;pdb.set_trace()
                    print(rst_advance_details)
                    print(rst_payment_details)
                    print(e)
                    #file_object = open(str_file, 'a')
                    #file_object.write(data)
                    #file_object.write('\n\n')
                    #file_object.write(res_data.text)
                    #file_object.write('\n\n\n\n')
                    #file_object.close()
                    continue

            conn.dispose()
            #file_object.close()
            return True
        except Exception as e:
            conn.dispose()
            raise
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        # import pdb; pdb.set_trace()
        print(str(e))

if __name__ == '__main__':
    bills_to_sap()
