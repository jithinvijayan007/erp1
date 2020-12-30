from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import psycopg2.extras
import sys

def save_batch_data(dct_grn,dct_branch,dct_imei):
    f=open("Goods_Return_Batch_Fail_entry.txt","a")
    f.write("\n\n\t\t=============================================================================================================================\n\n")
    f.write("Date : "+str(datetime.now()))
    f.write("\n\n Batches not entered in grn_details:\n\n")
    f.write(str(dct_grn))
    f.write("\n\nBatches Not entered in branch_stock and branch_stock_imei_details:\n\n")
    f.write(str(dct_branch))
    f.write("\n\nIMEI Not accepted :\n\n")
    f.write(str(dct_imei))
    f.close()

def GoodsReturn(date):
    """
            Function to remove the returned items from grn details and branch stock details.
            return: Success

            code changed to update only if the branch type in 2 or 3, and filter changed with respect to item and imei.


    """
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
        except Exception as e:
            return 0
        #import pdb;pdb.set_trace()
        cur = conn.cursor()
        cur1 = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        lst_imei_updated_final = []
        lst_pk_bint_id_fahad = []
        lst_pk_bint_id_freddy = []
        url = "http://13.71.18.142:8086/api/GoodsReturn"
        PARAMS = {'FDate':date}
        res_data=requests.get(url=url,params=PARAMS)
        if res_data.status_code == 200:
            dct_data=json.loads(res_data.text)
            print(len(dct_data))
            date_now = datetime.now()
            if dct_data:
                lst_imei = []
                lst_batch = []
                lst_imei_not_entered = []
                for item in dct_data:
                    
                    dct_batch = {}
                    lst_batch_data = []
                    # collecting data for grnr_master table
                    cur1.execute("select pk_bint_id from branch where vchr_code='"+item['line'][0]['WhsCode']+"'")
                    grnrm_ins_branch_id=cur1.fetchall()
                    grnrm_vchr_purchase_return_num = "GRNR-"+item['line'][0]['WhsCode']+"-"+str(item['DocNum'])
                    grnrm_dat_purchase = item.get('GRNDate','')
                    grnrm_billed_date = item.get('BillDate','')
                    grnrm_bill_num = item.get('BillNo','')
                    grnrm_bill_total = item.get('DocTotal','')
                    grnr_id = 0
                    str_query_check = "select pk_bint_id from grnr_master where vchr_purchase_return_num = '"+grnrm_vchr_purchase_return_num+"'"
                    cur1.execute(str_query_check)
                    check_data = cur1.fetchall()
                    if check_data:
                        continue
                
                    bln_data_success = True
                    dct_data_batch = {}

                    for lst_data in item['line']:
                        bln_srn_reg = True
                        dct_data_batch1 = {}
                        cur.execute("select pk_bint_id,int_type from branch where upper(vchr_code) = '"+str(lst_data['WhsCode']).upper()+"';")
                        rst_branch = cur.fetchall()
                        if rst_branch and rst_branch[0][1] in [2,3]: 
                            lst_imei = lst_data['IntrSerial']
                            cur1.execute("select imei_status,pk_bint_id from item where vchr_item_code='"+lst_data['ItemCode']+"'")
                            lst_grn_avail = cur1.fetchall()
                            grnrd_int_qty = lst_data.get('Quantity','0')
                            grnrd_int_free = lst_data.get('FreeQty') if lst_data.get('FreeQty') != 'N' else 0
                            grnrd_int_damaged = '1' if lst_data.get('U_DAMAGED') != 'N' else '0'
                            grnrd_json_imei = str(lst_data.get('IntrSerial')).replace("'",'"') if lst_data.get('U_DAMAGED') == 'N' else {}
                            grnrd_json_imei_damaged = str(lst_data.get('IntrSerial')).replace("'",'"') if lst_data.get('U_DAMAGED') != 'N' else {}
                            grnrd_dbl_tax_rate = lst_data.get('TaxRate','')
                            grnrd_dbl_total_amount = lst_data.get('Price','0.00')

                            if lst_grn_avail and lst_grn_avail[0]['imei_status']:
                                cur1.execute("select pk_bint_id,dbl_dealer_cost from item where vchr_item_code='"+lst_data['ItemCode']+"'")
                                grnrd_ins_item_id=cur1.fetchall()

                                grnrd_fk_item_id = grnrd_ins_item_id[0]['pk_bint_id']
                                grnrd_dbl_cost_price = grnrd_ins_item_id[0]['dbl_dealer_cost']

                                if dct_data_batch.get('vchr_purchase_return_num') == None:

                                    dct_data_batch['vchr_purchase_return_num'] = str(grnrm_vchr_purchase_return_num)
                                    dct_data_batch['dat_purchase_return'] = str(grnrm_dat_purchase)
                                    dct_data_batch['fk_branch_id'] = str(grnrm_ins_branch_id[0]['pk_bint_id'])
                                    dct_data_batch['dat_created'] = str(datetime.strftime(date_now,'%Y-%m-%d'))
                                    dct_data_batch['data'] = []

                                dct_data_batch1['fk_item_id'] = str(grnrd_fk_item_id)
                                dct_data_batch1['int_qty'] = str(grnrd_int_qty)
                                dct_data_batch1['dbl_tax_rate'] = str(grnrd_dbl_tax_rate)
                                dct_data_batch1['jsn_imei'] = str(grnrd_json_imei)
                                dct_data_batch1['data'] = []
                            lst_imei_updated = []
                            #  Data from grn_details->>imei_avail
                            if lst_imei:
                                cur.execute("select gd.pk_bint_id,gd.jsn_imei_avail from grn_details as gd join item it on it.pk_bint_id = gd.fk_item_id where (gd.jsn_imei_avail->>'imei_avail')::jsonb?|array"+str(lst_imei)+" and it.vchr_item_code = '"+ str(lst_data['ItemCode']).upper() +"';")
                                lst_grn_avail = cur.fetchall()
                                if lst_grn_avail:
                                    bln_srn_reg = False
                                    lst_value = []
                                    str_values = " "
                                    str_const = '"imei_avail"'
                                    for item in lst_grn_avail:
                                        lst_imei_avail = item[1]['imei_avail']
                                        lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and return_imei_list
                                        lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                                        lst_imei_updated.extend(lst_return_imei)
                                        lst_imei_updated_final.extend(lst_return_imei)

                                        dct_data_recived = {}

                                        dct_data_recived['grn_details_id'] = str(item[0])
                                        dct_data_recived['jsn_imei'] = str(lst_return_imei)
                                        dct_data_recived['jsn_batch_no'] = '{}'
                                        dct_data_recived['int_qty'] = str(len(lst_return_imei))
                                        dct_data_recived['bln_grndetails'] = '1'


                                        dct_data_recived['U_jsn_imei'] = "'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB"
                                        dct_data_recived['U_qty'] = str(len(lst_remains_imei))
                                        dct_data_batch1['data'].append(dct_data_recived)
                           

                            #  Data from grn_details->>imei_dmgd
                            if lst_imei:
                                cur.execute("select gd.pk_bint_id,gd.jsn_imei_dmgd from grn_details as gd join item it on it.pk_bint_id = gd.fk_item_id where (gd.jsn_imei_dmgd->>'imei_damage')::jsonb?|array"+str(lst_imei)+" and it.vchr_item_code ='"+ str(lst_data['ItemCode']).upper() +"';")
                                lst_grn_dmgd = cur.fetchall()

                                

                                if lst_grn_dmgd:
                                    bln_srn_reg = False
                                    lst_value = []
                                    str_values = " "
                                    str_const = '"imei_damage"'
                                    for item in lst_grn_dmgd:
                                        lst_imei_avail = item[1]['imei_damage']
                                        lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and return_imei_list
                                        lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                                        lst_imei_updated.extend(lst_return_imei)
                                        lst_imei_updated_final.extend(lst_return_imei)


                                        dct_data_recived = {}

                                        dct_data_recived['grn_details_id'] = str(item[0])
                                        dct_data_recived['jsn_imei'] = str(lst_return_imei)
                                        dct_data_recived['jsn_batch_no'] = '{}'
                                        dct_data_recived['int_qty'] = str(len(lst_return_imei))
                                        dct_data_recived['bln_grndetails'] = '11'

                                        dct_data_recived['U_jsn_imei'] = "'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB"
                                        dct_data_recived['U_qty'] = str(len(lst_remains_imei))
                                        dct_data_batch1['data'].append(dct_data_recived)


                            # =============================================================================Branch Stock details===================================================================================================

                            #  Data from branch_stock_details->>imei_dmgd
                            # lst_imei = list(set(lst_imei)-set(lst_imei_updated))
                            str_value_imei_details = ""
                            if lst_imei:
                                cur.execute("select bs.pk_bint_id,bs.jsn_imei_dmgd from branch_stock_details as bs join item it on it.pk_bint_id = bs.fk_item_id where (bs.jsn_imei_dmgd->>'imei')::jsonb?|array"+str(lst_imei)+" and it.vchr_item_code ='"+ str(lst_data['ItemCode']).upper() +"';")
                                lst_branch_dmgd = cur.fetchall()

                                if lst_branch_dmgd:
                                    bln_srn_reg = False
                                    lst_value = []
                                    str_values = " "
                                    str_const = '"imei"'
                                    for item in lst_branch_dmgd:
                                        lst_imei_avail = item[1]['imei']
                                        lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and return_imei_list
                                        lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                                        lst_imei_updated.extend(lst_return_imei)
                                        lst_imei_updated_final.extend(lst_return_imei)

                                        dct_data_recived = {}

                                        dct_data_recived['grn_details_id'] = str(item[0])
                                        dct_data_recived['bln_grndetails'] = '22'

                                        dct_data_recived['U_jsn_imei'] = "'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB"
                                        dct_data_recived['U_qty'] = str(len(lst_remains_imei))
                                        dct_data_batch1['data'].append(dct_data_recived)

                            #  Data from branch_stock_details->>imei_avail
                            # lst_imei = list(set(lst_imei)-set(lst_imei_updated))

                            if lst_imei:

                                # branch_stock_details -->imei_available
                                cur.execute("select bs.pk_bint_id,bs.jsn_imei_avail from branch_stock_details as bs join item it on it.pk_bint_id = bs.fk_item_id where (bs.jsn_imei_avail->>'imei')::jsonb?|array"+str(lst_imei)+" and it.vchr_item_code ='"+ str(lst_data['ItemCode']).upper() +"';")
                                lst_branch_avail = cur.fetchall()



                                if lst_branch_avail:
                                    # import pdb; pdb.set_trace().
                                    bln_srn_reg = False
                                    lst_value = []
                                    str_values = " "
                                    str_const = '"imei"'
                                    for item in lst_branch_avail:
                                        lst_imei_avail = item[1]['imei']
                                        lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and lst_imei
                                        lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                                        lst_imei_updated.extend(lst_return_imei) # add the updated imei to  lst_imei_updated
                                        lst_imei_updated_final.extend(lst_return_imei) # add the updated imei to  lst_imei_updated


                                        dct_data_recived = {}

                                        dct_data_recived['grn_details_id'] = str(item[0])
                                        dct_data_recived['bln_grndetails'] = '2'

                                        dct_data_recived['demo_data'] = str(lst_imei_avail)+str(lst_return_imei)

                                        dct_data_recived['U_jsn_imei'] = "'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB"
                                        dct_data_recived['U_qty'] = str(len(lst_remains_imei))
                                        dct_data_batch1['data'].append(dct_data_recived)

                                # branch_stock_imei_details -->imei
                                cur.execute("select bid.pk_bint_id,bid.jsn_imei from branch_stock_imei_details as bid join branch_stock_details bs on bs.pk_bint_id = bid.fk_details_id join item it on it.pk_bint_id = bs.fk_item_id where (bid.jsn_imei->>'imei')::jsonb?|array"+str(lst_imei)+" and it.vchr_item_code ='"+ str(lst_data['ItemCode']).upper() +"';")
                                lst_branch_imei_details = cur.fetchall()

                                if lst_branch_imei_details:
                                    bln_srn_reg = False
                                    lst_value = []
                                    str_values = " "
                                    str_const = '"imei"'
                                    for item in lst_branch_imei_details:
                                        lst_imei_avail = item[1]['imei']
                                        lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and lst_imei
                                        lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))


                                        dct_data_recived = {}

                                        dct_data_recived['grn_details_id'] = str(item[0])
                                        dct_data_recived['jsn_imei'] = str(lst_return_imei)
                                        dct_data_recived['jsn_batch_no'] = '{}'
                                        dct_data_recived['int_qty'] = str(len(lst_return_imei))
                                        dct_data_recived['bln_grndetails'] = '3'

                                        dct_data_recived['U_jsn_imei'] = "'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB"
                                        dct_data_recived['U_qty'] = str(len(lst_remains_imei))

                                        dct_data_batch1['data'].append(dct_data_recived)
                            



                    # LG
                    #         print("Returned IMEI : ",lst_imei_updated)
                        # collecting datas for batch items
                        cur1.execute("select imei_status,pk_bint_id from item where vchr_item_code='"+lst_data['ItemCode']+"'")
                        lst_grn_avail = cur1.fetchall()
                        
                        # import pdb; pdb.set_trace()
                        if lst_grn_avail and not lst_grn_avail[0]['imei_status']:
                            dict_batch = {}
                            dict_batch['id']=lst_grn_avail[0]['pk_bint_id']
                            dict_batch['warehouse'] = lst_data['WhsCode']
                            dict_batch['itemcode'] = lst_data['ItemCode']
                            dict_batch['batch'] = lst_data['IntrSerial'][0]
                            dict_batch['qty'] = lst_data['Quantity']
                            
                            dict_batch['int_qty'] = grnrd_int_qty
                            dict_batch['json_batch'] = grnrd_json_imei if grnrd_json_imei != "{}" else grnrd_json_imei_damaged
                            # dict_batch['json_batch_damaged'] = grnrd_json_imei_damaged
                            dict_batch['dbl_tax_rate'] = grnrd_dbl_tax_rate
                            
                            if dct_batch.get('purchase_num') == None:
                                dct_batch['branch_id'] = grnrm_ins_branch_id[0]['pk_bint_id']
                                dct_batch['purchase_num'] = grnrm_vchr_purchase_return_num
                                dct_batch['dat_purchase'] = grnrm_dat_purchase
                                dct_batch['billed_date'] = grnrm_billed_date
                                dct_batch['bill_num'] = grnrm_bill_num
                                dct_batch['bill_total'] = grnrm_bill_total
                                dct_batch['data'] = []
                            dct_batch['data'].append(dict_batch)
                            
                            lst_pk_bint_id_fahad.append(lst_grn_avail[0]['pk_bint_id'])
                        else:
                            lst_pk_bint_id_freddy.extend(lst_data['IntrSerial'])

                        if bln_srn_reg and lst_grn_avail and lst_grn_avail[0]['imei_status']:
                            lst_imei_not_entered.append(lst_data)
                            bln_data_success = False
                            break
                        else:
                            if dct_data_batch1:
                                # import pdb; pdb.set_trace()
                                dct_data_batch['data'].append(dct_data_batch1)

                    
                    if dct_batch:
                        lst_batch.append(dct_batch)

                    if dct_data_batch and bln_data_success:
                            # inserting data to grnr_master
                            str_query_grnr = "insert into grnr_master (vchr_purchase_return_num, dat_purchase_return, fk_branch_id, dat_created) values('"+str(dct_data_batch['vchr_purchase_return_num'])+"','"+str(dct_data_batch['dat_purchase_return'])+"',"+str(dct_data_batch['fk_branch_id'])+",'"+str(dct_data_batch['dat_created'])+"') returning pk_bint_id"
                            cur1.execute(str_query_grnr)
                            grnr_id = cur1.fetchall()
                            if grnr_id:
                                grnr_id = grnr_id[0]['pk_bint_id']
                            
                            # inserting data to grnr_details
                            for sub_data in dct_data_batch['data']:
                                str_query_grnr = "insert into grnr_details (fk_item_id,fk_master_id,int_qty,dbl_tax_rate,jsn_imei) values("+str(sub_data['fk_item_id'])+","+str(grnr_id)+","+str(sub_data['int_qty'])+","+str(sub_data['dbl_tax_rate'])+",'"+str(sub_data['jsn_imei'])+"') returning pk_bint_id"
                                cur1.execute(str_query_grnr)
                                grnrd_id = cur1.fetchall()
                                if grnrd_id:
                                    grnrd_id = grnrd_id[0]['pk_bint_id']

                                for data in sub_data['data']:
                                    if data['bln_grndetails'] == '1':
                                        cur.execute("update grn_details set int_avail = "+str(data['U_qty'])+",jsn_imei_avail = "+str(data['U_jsn_imei'])+" where pk_bint_id = "+data['grn_details_id'])
                                        str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(data['grn_details_id'])+",'"+str(data['jsn_imei']).replace("'",'"')+"','{}',"+str(data['int_qty'])+")"
                                        cur1.execute(str_query_grnrimeid)
                                    if data['bln_grndetails'] == '11':
                                        cur.execute("update grn_details set int_damaged = "+str(data['U_qty'])+",jsn_imei_dmgd = "+str(data['U_jsn_imei'])+" where pk_bint_id = "+data['grn_details_id'])
                                        str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(data['grn_details_id'])+",'"+str(data['jsn_imei']).replace("'",'"')+"','{}',"+str(data['int_qty'])+")"
                                        cur1.execute(str_query_grnrimeid)
                                    if data['bln_grndetails'] == '2':
                                        cur.execute("update branch_stock_details as bs set int_qty = "+str(data['U_qty'])+",jsn_imei_avail= "+str(data['U_jsn_imei'])+" where pk_bint_id = "+ data['grn_details_id'])
                                    if data['bln_grndetails'] == '22':
                                        cur.execute("update branch_stock_details set jsn_imei_dmgd= "+str(data['U_jsn_imei'])+" where pk_bint_id = "+data['grn_details_id'])
                                    if data['bln_grndetails'] == '3':
                                        cur.execute("update branch_stock_imei_details set int_qty = "+str(data['U_qty'])+",jsn_imei="+str(data['U_jsn_imei'])+" where pk_bint_id = "+data['grn_details_id']+" returning fk_grn_details_id")
                                        grn_id = cur.fetchone()
                                        grn_id = grn_id[0]

                                        str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(grn_id)+",'"+str(data['jsn_imei']).replace("'",'"')+"','{}',"+str(data['int_qty'])+")"
                                        cur1.execute(str_query_grnrimeid)




                                        
                                        
                print("Batch Data")
                if lst_batch:
                    # print(lst_batch)
                    lst_batch_not_updated_in_bsd_bsid = []
                    lst_batch_not_updated_in_grn_details = []
                    for batch_data_main in lst_batch:
                        str_query_check = "select pk_bint_id from grnr_master where vchr_purchase_return_num = '"+batch_data_main['purchase_num']+"'"
                        cur1.execute(str_query_check)
                        check_data = cur1.fetchall()
                        # import pdb; pdb.set_trace()
                        if check_data:
                            continue
                        # import pdb; pdb.set_trace()
                        bln_data_success = True
                        dct_data_batch = {}
                        for batch_data in batch_data_main['data']:
                            cur1.execute("select pk_bint_id from branch where vchr_code='"+batch_data['warehouse']+"'")
                            ins_branch_id=cur1.fetchall()
                            cur1.execute("select pk_bint_id,dbl_dealer_cost from item where vchr_item_code='"+str(batch_data['itemcode'])+"'")
                            itemcode=cur1.fetchall() # ['pk_bint_id','dbl_dealer_cost']

                            int_branch_id=ins_branch_id[0]['pk_bint_id']
                            int_stock_qty=batch_data['qty']

                            # LG
                            bln_srn_reg = True
                            dct_data_batch1 = {}

                            grnrd_id = 0

                            cur1.execute("select gd.vchr_batch_no as batch_no,gd.pk_bint_id,gd.int_avail,gm.fk_branch_id,(select sum(gd.int_avail) from grn_details gd join grn_master gm on gd.fk_purchase_id = gm.pk_bint_id where fk_branch_id="+str(int_branch_id)+" and vchr_batch_no= '"+str(batch_data['batch'])+"') as total_int_avail from grn_details gd join grn_master gm on gd.fk_purchase_id = gm.pk_bint_id where gm.fk_branch_id="+str(int_branch_id)+" and gd.vchr_batch_no= '"+str(batch_data['batch'])+"' and gd.int_avail !=0")
                            ins_branch_data = cur1.fetchall()
                            if ins_branch_data and ins_branch_data[0]['total_int_avail'] >= int_stock_qty and int_stock_qty:
                                # import pdb; pdb.set_trace()
                                bln_srn_reg = False

                                if dct_data_batch.get('vchr_purchase_return_num') == None:

                                    dct_data_batch['vchr_purchase_return_num'] = str(batch_data_main['purchase_num'])
                                    dct_data_batch['dat_purchase_return'] = str(batch_data_main['dat_purchase'])
                                    dct_data_batch['fk_branch_id'] = str(batch_data_main['branch_id'])
                                    dct_data_batch['dat_created'] = str(datetime.strftime(date_now,'%Y-%m-%d'))
                                    dct_data_batch['data'] = []

                                dct_data_batch1['fk_item_id'] = str(itemcode[0]['pk_bint_id'])
                                dct_data_batch1['int_qty'] = str(batch_data['int_qty'])
                                dct_data_batch1['dbl_tax_rate'] = str(batch_data['dbl_tax_rate'])
                                dct_data_batch1['vchr_batch_no'] = str(batch_data['json_batch'])
                                dct_data_batch1['data'] = []

                                int_stock_qty1 = int_stock_qty
                                for data in ins_branch_data:
                                    dct_data_recived = {}
                                    if data['int_avail'] >= int_stock_qty1:

                                        dct_data_recived['grn_details_id'] = str(data['pk_bint_id'])
                                        dct_data_recived['jsn_imei'] = '{}'
                                        dct_data_recived['jsn_batch_no'] = '["'+data['batch_no']+'"]'
                                        dct_data_recived['int_qty'] = int_stock_qty1
                                        dct_data_recived['bln_grndetails'] = True
                                        dct_data_batch1['data'].append(dct_data_recived)
                                        break
                                    elif data['int_avail'] <= int_stock_qty1 and int_stock_qty1 > 0:

                                        dct_data_recived['grn_details_id'] = str(data['pk_bint_id'])
                                        dct_data_recived['jsn_imei'] = '{}'
                                        dct_data_recived['jsn_batch_no'] = '["'+data['batch_no']+'"]'
                                        dct_data_recived['int_qty'] = '0'
                                        dct_data_recived['int_qty_'] = str(data['int_avail'])
                                        dct_data_recived['bln_grndetails'] = True
                                        dct_data_batch1['data'].append(dct_data_recived)


                                        int_stock_qty1 -= data['int_avail']
                                        if int_stock_qty1 <= 0:
                                            break


                            else:
                                batch_data.pop('id','')
                                lst_batch_not_updated_in_grn_details.append(batch_data)

                            if int_stock_qty > 0:
                                

                                cur1.execute("SELECT  bd.jsn_batch_no->>'batch' as batch_no,bd.pk_bint_id as bd_id, bd.int_qty as bd_qty, bid.pk_bint_id as bid_id, bid.int_qty as bid_qty, (SELECT SUM(bsd.int_qty) FROM branch_stock_details bsd JOIN branch_stock_master bsm ON bsd.fk_master_id = bsm.pk_bint_id WHERE fk_branch_id = "+str(int_branch_id)+" AND (bsd.jsn_batch_no->>'batch')::jsonb ?'"+str(batch_data['batch'])+"') AS total_qty from branch_stock_details bd join branch_stock_master bm on bd.fk_master_id  = bm.pk_bint_id join branch_stock_imei_details bid on bid.fk_details_id=bd.pk_bint_id where fk_branch_id = "+str(int_branch_id)+" and bid.int_qty > 0 and (bd.jsn_batch_no->>'batch')::jsonb ?'"+str(batch_data['batch'])+"' and (bid.jsn_batch_no->>'batch')::jsonb ?'"+str(batch_data['batch'])+"' order by bid.pk_bint_id")
                                ins_branch_data1=cur1.fetchall()
                                if ins_branch_data1 and int_stock_qty and ins_branch_data1[0]['total_qty'] >= int_stock_qty:
                                    bln_srn_reg = False

                                    if dct_data_batch.get('vchr_purchase_return_num') == None:

                                        dct_data_batch['vchr_purchase_return_num'] = str(batch_data_main['purchase_num'])
                                        dct_data_batch['dat_purchase_return'] = str(batch_data_main['dat_purchase'])
                                        dct_data_batch['fk_branch_id'] = str(batch_data_main['branch_id'])
                                        dct_data_batch['dat_created'] = str(datetime.strftime(date_now,'%Y-%m-%d'))
                                        dct_data_batch['data'] = []

                                    dct_data_batch1['fk_item_id'] = str(itemcode[0]['pk_bint_id'])
                                    dct_data_batch1['int_qty'] = str(batch_data['int_qty'])
                                    dct_data_batch1['dbl_tax_rate'] = str(batch_data['dbl_tax_rate'])
                                    dct_data_batch1['vchr_batch_no'] = str(batch_data['json_batch'])
                                    dct_data_batch1['data'] = []

                                    int_stock_qty1 = int_stock_qty
                                    for data in ins_branch_data1:
                                        dct_data_recived = {}
                                        if data['bd_qty'] >= int_stock_qty1:

                                            
                                            dct_data_recived['bsd_pk_bint_id'] = data['bd_id']
                                            dct_data_recived['bsimeid_pk_bint_id'] = str(data['bid_id'])
                                            dct_data_recived['jsn_imei'] = '{}'
                                            dct_data_recived['jsn_batch_no'] = data['batch_no']
                                            dct_data_recived['int_qty'] = str(int_stock_qty1)
                                            dct_data_recived['bln_grndetails'] = False
                                            dct_data_batch1['data'].append(dct_data_recived)

                                            break
                                        elif data['bd_qty'] <= int_stock_qty1 and int_stock_qty1 > 0:

                                            
                                            dct_data_recived['bsd_pk_bint_id'] = data['bd_id']
                                            dct_data_recived['bsimeid_pk_bint_id'] = str(data['bid_id'])
                                            dct_data_recived['jsn_imei'] = '{}'
                                            dct_data_recived['jsn_batch_no'] = str(data['batch_no'])
                                            dct_data_recived['int_qty'] = '0'
                                            dct_data_recived['int_qty_'] = str(data['bid_qty'])
                                            dct_data_recived['bln_grndetails'] = False
                                            dct_data_batch1['data'].append(dct_data_recived)
                                            int_stock_qty1 -= data['bid_qty']

                                            if int_stock_qty1 <= 0:
                                                break
                                else:
                                    batch_data.pop('id','')
                                    lst_batch_not_updated_in_bsd_bsid.append(batch_data)

                            if bln_srn_reg:
                                bln_data_success = False
                                break
                            else:
                                # import pdb; pdb.set_trace()
                                dct_data_batch['data'].append(dct_data_batch1)
                        if dct_data_batch and bln_data_success:
                            # inserting data to grnr_master
                            str_query_grnr = "insert into grnr_master (vchr_purchase_return_num, dat_purchase_return, fk_branch_id, dat_created) values('"+str(dct_data_batch['vchr_purchase_return_num'])+"','"+str(dct_data_batch['dat_purchase_return'])+"',"+str(dct_data_batch['fk_branch_id'])+",'"+str(dct_data_batch['dat_created'])+"') returning pk_bint_id"
                            cur1.execute(str_query_grnr)
                            grnr_id = cur1.fetchall()
                            if grnr_id:
                                grnr_id = grnr_id[0]['pk_bint_id']
                            
                            # inserting data to grnr_details
                            for sub_data in dct_data_batch['data']:
                                str_query_grnr = "insert into grnr_details (fk_item_id,fk_master_id,int_qty,dbl_tax_rate,vchr_batch_no) values("+str(sub_data['fk_item_id'])+","+str(grnr_id)+","+str(sub_data['int_qty'])+","+str(sub_data['dbl_tax_rate'])+",'"+str(sub_data['vchr_batch_no'])+"') returning pk_bint_id"
                                cur1.execute(str_query_grnr)
                                grnrd_id = cur1.fetchall()
                                if grnrd_id:
                                    grnrd_id = grnrd_id[0]['pk_bint_id']

                                for data in sub_data['data']:
                                    if data['bln_grndetails']:
                                        if data['int_qty'] == '0':
                                            cur1.execute("update grn_details set int_avail = 0 where pk_bint_id="+str(data['grn_details_id']))

                                            str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(data['grn_details_id'])+",'{}','"+str(data['jsn_batch_no'])+"',"+str(data['int_qty_'])+")"
                                            cur1.execute(str_query_grnrimeid)
                                        else:
                                            cur1.execute("update grn_details set int_avail = int_avail - "+str(data['int_qty'])+" where pk_bint_id="+str(data['grn_details_id']))

                                            str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(data['grn_details_id'])+",'{}','"+str(data['jsn_batch_no'])+"',"+str(data['int_qty'])+")"
                                            cur1.execute(str_query_grnrimeid)
                                        
                                    else:
                                        if data['int_qty'] == '0':
                                            cur1.execute("update branch_stock_details set int_qty = 0 where pk_bint_id="+str(data['bsd_pk_bint_id']))
                                            cur1.execute("update branch_stock_imei_details set int_qty= 0 where pk_bint_id="+str(data['bsimeid_pk_bint_id']+" returning fk_grn_details_id"))
                                            grn_id = cur1.fetchone()['fk_grn_details_id']

                                            str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(grn_id)+",'{}','"+str(data['jsn_batch_no'])+"',"+str(data['int_qty_'])+")"
                                            cur1.execute(str_query_grnrimeid)
                                        else:

                                            cur1.execute("update branch_stock_details set int_qty = int_qty - "+str(data['int_qty'])+" where pk_bint_id="+str(data['bsd_pk_bint_id']))
                                            cur1.execute("update branch_stock_imei_details set int_qty= int_qty - "+str(data['int_qty'])+" where pk_bint_id="+str(data['bsimeid_pk_bint_id']+" returning fk_grn_details_id"))
                                            grn_id = cur1.fetchone()['fk_grn_details_id']

                                            str_query_grnrimeid = "insert into grnr_imei_details (fk_details_id,fk_grn_details_id,jsn_imei,jsn_batch_no,int_qty) values ("+str(grnrd_id)+","+str(grn_id)+",'{}','"+str(data['jsn_batch_no'])+"',"+str(data['int_qty'])+")"
                                            cur1.execute(str_query_grnrimeid)


                cur.close()
                cur1.close()
                conn.close()
                save_batch_data(lst_batch_not_updated_in_grn_details,lst_batch_not_updated_in_bsd_bsid,lst_imei_not_entered)
                print("All Returned IMEI : ",lst_imei_updated_final)
                print("length",len(lst_imei_updated_final))
                return 1
            else:
                print('No Data')
                cur.close()
                cur1.close()
                conn.close()
                return 0

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        cur.close()
        cur1.close()
        conn.close()
        return 0

if __name__ == '__main__':
    date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) == 2:
        date = sys.argv[1]
    GoodsReturn(date)

"""

create table grnr_master(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_purchase_return_num VARCHAR(80),
    dat_purchase_return TIMESTAMP,
    fk_branch_id BIGINT REFERENCES branch(pk_bint_id),-->[warehouses or head office only]
    dat_created TIMESTAMP
);
create table grnr_details(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    fk_item_id BIGINT REFERENCES item(pk_bint_id),
    fk_master_id BIGINT REFERENCES grnr_master(pk_bint_id),
    int_qty INTEGER,
    dbl_tax_rate DOUBLE PRECISION,
    jsn_imei JSONB,-->text,
    vchr_batch_no VARCHAR(80)
);
create table grnr_imei_details(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    fk_details_id BIGINT REFERENCES grnr_details(pk_bint_id),
    fk_grn_details_id BIGINT REFERENCES grn_details(pk_bint_id),
    jsn_imei JSONB,
    jsn_batch_no JSONB,
    int_qty INTEGER
);

"""
