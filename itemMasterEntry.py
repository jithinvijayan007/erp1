import pandas as pd
import psycopg2
from datetime import datetime
import random
import json
import time
"""works only for the first time to change the apx code to sap code"""
def itemsfromexcelsap():
    try:
        time_start = time.time()
        try:
            conn = psycopg2.connect(host="localhost",database="pos_blank", user="admin", password="nisam@123")
            cur = conn.cursor()
            conn.autocommit = True
            df = pd.read_excel("MAIN_MASTER.xlsx",header=0,sheet_name="Sheet1")
        except Exception as e:
            return 'cannot read excel'


        lst_known_keys = ['Apx Code','Item No.','Item Description','Group Name','Serial No. Management','HSN','SAC Code','Brand','PRODUCT CATEGORY','ITEM CATEGORY','GST','Purchase Item','Inventory Item','Sales Item']
        lst_unknown_keys = ['Foreign Name','Valuation Method','Manage Batch No. [Yes/No]','Manufacturer','Set G/L Accounts By','#']

        lst_updated = []
        lst_added = []
        lst_error_code = []
        lst_error_reason = []
        lst_index = []
        for ind,row in df.iterrows():
            try:
                #import pdb;pdb.set_trace()
                vchr_current_item_code = str(row['APX Code'])
                if str(vchr_current_item_code).upper() == 'NAN' or str(vchr_current_item_code).upper() == 'NILL':
                    lst_error_code.append(row['Item No.'])
                    lst_error_reason.append("item apx code is nan or nill")
                    lst_index.append(ind + 2)
                else:
                    lst_all_keys = row.keys()
                    lst_specifications_keys = list(set(lst_all_keys) - set(lst_known_keys) - set(lst_unknown_keys))
                    lst_specs = []
                    dct_specs = {}


                    """specifications"""
                    for ins_spec in lst_specifications_keys:
                        cur.execute("SELECT pk_bint_id,vchr_name,bln_status FROM specifications WHERE vchr_name = '"+ins_spec+"';")
                        ins_specification = cur.fetchall()

                        if ins_specification:
                            if not ins_specification[0][2]:
                                ins_update = cur.execute("UPDATE specifications SET bln_status = True WHERE vchr_name = '"+ins_spec+"';")
                            if not str(row[ins_spec]).upper() == 'NIL':
                                if not str(row[ins_spec]).upper() == 'NAN':
                                    lst_specs.append(ins_specification[0][0])
                                    dct_specs[str(ins_specification[0][0])] = row[ins_spec]
                        else:
                            cur.execute("INSERT INTO specifications(vchr_name,bln_status) VALUES('"+ins_spec+"',True) returning pk_bint_id;")
                            int_spec_id = cur.fetchone()
                            if not str(row[ins_spec]).upper() == 'NIL':
                                lst_specs.append(int_spec_id[0])
                                dct_specs[str(int_spec_id[0])] = row[ins_spec]
                    #import pdb;pdb.set_trace()
                    dct_specs = json.dumps(dct_specs)
                    lst_specs = json.dumps(lst_specs)
                    """products"""
                    vchr_product_name = str(row['Group Name'])
                    if str(vchr_product_name).upper() == 'NIL':
                        vchr_product_name = 'DEFAULT1'
                    elif str(vchr_product_name).upper() == 'NAN':
                        vchr_product_name = 'DEFAULT2'
                    elif str(vchr_product_name).upper() == '0':
                        vchr_product_name = 'DEFAULT3'

                    cur.execute("SELECT pk_bint_id,vchr_name,int_status FROM products WHERE vchr_name = '"+vchr_product_name+"' ;")
                    ins_product = cur.fetchall()
                    #if sparPRODUCT CATEGORYe product is service else sales
                    if row['PRODUCT CATEGORY'].upper() == "SPARE":
                        int_sales = 2
                    else:
                        int_sales = 1

                    if ins_product:
                        ins_update = cur.execute("UPDATE products SET int_status = 0,int_sales = '"+str(int_sales)+"'  WHERE vchr_name = '"+vchr_product_name+"';")
                        int_product_id = ins_product[0][0]
                    else:
                        """category"""
                        vchr_category_name = 'DEFAULT1'
                        if str(vchr_category_name).upper() == "NAN" :
                            vchr_category_name = "DEFAULT1"
                        elif str(vchr_category_name).upper() == "NIL":
                            vchr_category_name = "DEFAULT2"
                        elif str(vchr_category_name).upper() == "0":
                            vchr_category_name = "DEFAULT3"
                        cur.execute("SELECT pk_bint_id FROM category WHERE vchr_name = '"+vchr_category_name+"';")
                        ins_category = cur.fetchall()
                        if not ins_category:
                            cur.execute("INSERT INTO category(vchr_name,dat_created) values('"+vchr_category_name+"','"+str(datetime.now())+"') returning pk_bint_id;")
                            int_category_id = cur.fetchone()[0]
                        else:
                            int_category_id = ins_category[0][0]

                        cur.execute("INSERT INTO products(vchr_name,fk_category_id,dat_created)values('"+vchr_product_name+"','"+str(int_category_id)+"','"+str(datetime.now())+"') returning pk_bint_id; ")
                        int_product_id = cur.fetchone()[0]

                    """brands"""
                    vchr_brand_name =  str(row['Brand'])
                    if str(vchr_brand_name).upper() == "NAN" :
                        vchr_brand_name = "DEFAULT1"
                    elif str(vchr_brand_name).upper() == "NIL":
                        vchr_brand_name = "DEFAULT2"
                    elif str(vchr_brand_name).upper() == "0":
                        vchr_brand_name = "DEFAULT3"
                    cur.execute("SELECT pk_bint_id,vchr_name,int_status FROM brands WHERE vchr_name = '"+vchr_brand_name+"';")
                    ins_brand = cur.fetchall()

                    if not ins_brand:
                        cur.execute("INSERT INTO brands(vchr_name) values('"+vchr_brand_name+"') returning pk_bint_id;")
                        int_brand_id = cur.fetchone()[0]
                    else:
                        int_brand_id = ins_brand[0][0]




                    """tax master"""

                    cur.execute("select array_agg(vchr_name||':' ||pk_bint_id) from tax_master where vchr_name in ('CGST','SGST','IGST')")
                    tax_master_details = cur.fetchall()[0][0]
                    dct_tax_data = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in tax_master_details}
                    dct_tax = {}
                    if row['GST']:
                        dct_tax[dct_tax_data['CGST']] = row['GST']/2
                        dct_tax[dct_tax_data['SGST']] = row['GST']/2
                        dct_tax[dct_tax_data['IGST']] = row['GST']

                    # cur.execute("SELECT pk_bint_id,jsn_tax_master,dbl_rate FROM sap_tax_master WHERE vchr_code = '"+"GST"+str(int(row['GST']))+"';")
                    # ins_sap_tax_master = cur.fetchall()
                    # dbl_rate = ins_sap_tax_master[0][2]
                    # dct_tax = ins_sap_tax_master[0][1]
                    dct_tax = json.dumps(dct_tax)

                    """item category"""
                    vchr_item_category = str(row['ITEM CATEGORY'])
                    if str(vchr_item_category).upper() == "NAN" :
                        vchr_item_category = "DEFAULT1"
                    elif str(vchr_item_category).upper() == "NIL":
                        vchr_item_category = "DEFAULT2"
                    elif str(vchr_item_category).upper() == "0":
                        vchr_item_category = "DEFAULT3"

                    vchr_hsn_code = str(row['HSN'])
                    if str(vchr_hsn_code).upper() == "NAN":
                        vchr_hsn_code = ""
                    vchr_sac_code = str(row['SAC Code'])
                    if str(vchr_sac_code).upper() == "NAN":
                        vchr_sac_code = ""

                    cur.execute("SELECT pk_bint_id FROM item_category WHERE vchr_item_category = '"+vchr_item_category+"';")
                    ins_item_category = cur.fetchall()

                    if ins_item_category:
                        int_item_category_id = ins_item_category[0][0]
                        cur.execute("UPDATE item_category SET json_tax_master = '"+str(dct_tax)+"',json_specification_id = '"+str(lst_specs)+"',vchr_hsn_code = '"+vchr_hsn_code+"',vchr_sac_code = '"+vchr_sac_code+"' , int_status = 0 WHERE vchr_item_category = '"+vchr_item_category+"';")
                    else:
                        cur.execute("INSERT INTO item_category(vchr_item_category,json_tax_master,json_specification_id,dat_created,vchr_hsn_code,vchr_sac_code) values('"+vchr_item_category+"','"+str(dct_tax)+"','"+str(lst_specs)+"','"+str(datetime.now())+"','"+vchr_hsn_code+"','"+vchr_sac_code+"') returning pk_bint_id;")
                        int_item_category_id = cur.fetchone()[0]

                    """item group"""
                    vchr_item_group = str(row['MODEL NO'])
                    if str(vchr_item_group).upper() == "NAN" :
                        vchr_item_group = "DEFAULT1"
                    elif str(vchr_item_group).upper() == "NIL":
                        vchr_item_group = "DEFAULT2"
                    elif str(vchr_item_group).upper() == "0":
                        vchr_item_group = "DEFAULT3"
                    cur.execute("SELECT pk_bint_id,int_status FROM item_group WHERE vchr_item_group = '"+vchr_item_group+"';")
                    ins_item_group = cur.fetchall()

                    if ins_item_group:
                        int_group_id = ins_item_group[0][0]
                        if ins_item_group[0][1] < 0:
                            cur.execute("UPDATE item_group SET int_status = 0,dat_updated = '"+str(datetime.now())+"' WHERE vchr_item_group = '"+vchr_item_group+"';")

                    else:
                        cur.execute("INSERT INTO item_group(vchr_item_group,dat_created) VALUES('"+vchr_item_group+"','"+str(datetime.now())+"') returning pk_bint_id;")
                        int_group_id = cur.fetchone()[0]


                    """item"""
                    str_item_name = row['Item Description']
                    if str(str_item_name).upper() == "NAN" :
                        str_item_name = "DEFAULT1"
                    elif str(str_item_name).upper() == "NIL":
                        str_item_name = "DEFAULT2"
                    elif str(str_item_name).upper() == "0":
                        str_item_name = "DEFAULT3"

                    fk_product_id = int_product_id
                    fk_brand_id = int_brand_id
                    vchr_current_item_code = str(row['APX Code'])
                    vchr_sap_code = str(row['Item No.'])
                    fk_item_category_id = int_item_category_id
                    fk_item_group = int_group_id
                    json_specification_id = json.dumps(dct_specs)
                    if row['Serial No. Management'].upper() == 'Y':
                        imei_status = True
                    else:
                        imei_status = False
                    if row['Sales Item'].upper() == 'Y' and row['Purchase Item'].upper() == 'Y' and row['Inventory Item'].upper() == 'Y':
                        sale_status = True
                    else:
                         sale_status = False


                    cur.execute("SELECT pk_bint_id FROM item WHERE vchr_item_code = '"+str(vchr_sap_code)+"';")
                    ins_item_master = cur.fetchall()

                    if ins_item_master:
                        int_item_id = ins_item_master[0][0]
                        cur.execute("update item set vchr_name = '"+str_item_name+"' ,\
                                    fk_product_id = '"+str(fk_product_id)+"',\
                                    fk_brand_id = '"+str(fk_brand_id)+"',\
                                    vchr_item_code = '"+vchr_sap_code+"',\
                                    fk_item_category_id = '"+str(fk_item_category_id)+"',\
                                    fk_item_group_id = '"+str(fk_item_group)+"',\
                                    json_specification_id = '"+json_specification_id+"',\
                                    imei_status = '"+str(imei_status)+"',\
                                    sale_status = '"+str(sale_status)+"',\
                                    int_status = 0,\
                                    dat_updated = '"+str(datetime.now())+"',\
                                    vchr_old_item_code = '"+str(vchr_current_item_code)+"' where pk_bint_id = '"+str(int_item_id)+"';")

                        lst_updated.append(vchr_current_item_code)

                    else:
                        cur.execute("insert into item(vchr_name,fk_product_id,fk_brand_id,vchr_item_code,fk_item_category_id,fk_item_group_id,json_specification_id,imei_status,sale_status,dat_created,vchr_old_item_code,dbl_supplier_cost,dbl_dealer_cost,dbl_mrp,dbl_mop)\
                                                values('"+str_item_name+"','"+str(fk_product_id)+"','"+str(fk_brand_id)+"','"+vchr_sap_code+"','"+str(fk_item_category_id)+"','"+str(fk_item_group)+"','"+json_specification_id+"','"+str(imei_status)+"','"+str(sale_status)+"','"+str(datetime.now())+"','"+str(vchr_current_item_code)+"',0,0,0,0);")

                        lst_added.append(vchr_current_item_code)



            except Exception as e:
                lst_error_code.append(row['Item No.'])
                lst_error_reason.append(str(e))
                lst_index.append(ind + 2)
                pass

        print('added - ')
        print(len(lst_added))
        # print(lst_added)
        print('updated - ')
        print(len(lst_updated))
        print(time.time()-time_start)
        # print(lst_updated)
        print('successfully imported')
        cur.close()
        conn.close()

        if lst_error_code:
            #creating dataframes
            df_item = pd.DataFrame({'INDEX_NUM':lst_index,'ITEM CODE':lst_error_code,'REASON':lst_error_reason})
            #creating and writing to excel
            excel_file = 'itemsMaster_error.xlsx'
            file_name_export = excel_file
            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_item.to_excel(writer,sheet_name='Sheet1',index=True, startrow=0,startcol=0)
            writer.save()


    except Exception as e:
        raise

if __name__ == '__main__':
    itemsfromexcelsap()
