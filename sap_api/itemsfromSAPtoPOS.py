import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import json
import time
import pandas as pd
# date = '2019-08-01'
def itemsfromsap(date):
    """
    Used to push mygoal advance/deposit data to SAP
    paramerters(to SAP):
    response(from SAP):suceess/failed
    """
    try:
        time_start = time.time()
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor()

        except Exception as e:
            raise
#        import pdb; pdb.set_trace()
        #url = 'http://myglive.tmicloud.net:8084/api/master/Item'
        url = 'http://13.71.18.142:8086/api/master/Item'
        PARAMS = {'FDate':date}
        cur = conn.cursor()
        res_data=requests.get(url=url,params=PARAMS)
        if res_data.status_code == 200:
            str_data = res_data.json()
            if str_data:
                dct_data = str_data
                if dct_data:
                    lst_all_keys = dct_data[0].keys()
                    lst_known_keys = ['BrandName','ProductName','ITEMTYPE','BatchNum','SERIALNO','Status','ProductCategory','ItemCategory', 'Image Path','U_MODELNO1','U_MODELNO','U_SARRATE','U_TYPE','validFor', 'U_SUPPLIERS', 'U_ITEMTYPE','SerialNum','U_BRAND','ItemName','U_PRODUCTCATEGORY','HsnCode', 'ItemCode', 'U_ITEMCATEGORY', 'U_CATEGORY', 'U_GST','ItmsGrpNam']
                    lst_unknown_keys = ['InvntryUom','BuyUnitMsr','SalUnitMsr']
                    lst_specifications_keys = list(set(lst_all_keys) - set(lst_known_keys) - set(lst_unknown_keys))
                    # lst_specifications_keys=[data.split("U_")[1].upper() for data in lst_specifications_keys if "U_" in data]
                    lst_specifications_keys = [data.split('U_')[1].upper() if 'U_' in data else data.upper() for data in lst_specifications_keys]
                    str_query_data = "select vchr_name,bln_status,pk_bint_id from specifications;"
                    cur.execute(str_query_data)
                    rst_sales_data = cur.fetchall()
                    rst_sales_data = list(rst_sales_data)
                    dct_specification_id={data[0].upper():data[2] for data in rst_sales_data}

                    """adding specifications to table"""
                    for ins_spec in lst_specifications_keys:

                            if ins_spec not in dct_specification_id.keys():
                                cur.execute("INSERT INTO specifications(vchr_name) VALUES('"+ins_spec+"') returning pk_bint_id")
                                dct_specification_id[ins_spec]=cur.fetchall()[0][0]
                            elif ins_spec in dct_specification_id.keys():
                                ins_update = cur.execute("UPDATE specifications SET bln_status = True WHERE vchr_name = '"+ins_spec+"'")

                    cur.execute("select vchr_name,pk_bint_id from specifications;")
                    dct_spec_all = dict(cur.fetchall())
                    lst_updated = []
                    lst_added = []
                    lst_error_code = []
                    lst_error_reason = []

                    for item in dct_data:
                        try:

                            """specification"""
                            lst_null_keys = [ ]
                            for data in item:
                                if item[data] == 'NIL' or item[data] == None:
                                    if 'U_' in data :
                                        lst_null_keys.append(data.split("U_")[1].upper())
                                    else:
                                        lst_null_keys.append(data.upper())
                            # lst_null_keys= [data.split("U_")[1].upper() for data in item if (item[data]=='NIL' or item[data]== None) ]
                            lst_required_keys=list(set(lst_specifications_keys)-set(lst_null_keys))
                            # dct_specs={(key.split("U_")[1]).lower():value if 'U_' in key else key:value for key,value in item.items() }
                            # dct_specs={data.split("U_")[1].lower() else data.lower():item[data]  for data in item  if "U_" in data else data.lower()}
                            dct_specs={}
                            for data in item:
                                if 'U_' in data:
                                    dct_specs[data.split('U_')[1].upper()]=item[data]
                                else:
                                    dct_specs[data.upper()]=item[data]
                            # dct_specs={data.split}

                            dct_specs={ data : dct_specs[data]  for data in dct_specs if data in lst_required_keys }
                            dct_specs = {dct_spec_all[data]:dct_specs[data] for data in dct_specs if data in lst_required_keys}
                            lst_specs = list(dct_specs.keys())

                            """category"""
                            str_U_CATEGORY="DEFAULT1"
                            if not str_U_CATEGORY :
                                str_U_CATEGORY = "DEFAULT1"
                            elif str(str_U_CATEGORY).upper() == "NIL":
                                str_U_CATEGORY = "DEFAULT2"
                            elif str(str_U_CATEGORY).upper() == "0":
                                str_U_CATEGORY = "DEFAULT3"

                            cur.execute("SELECT pk_bint_id FROM category WHERE vchr_name = '"+str_U_CATEGORY+"';")
                            ins_category_check = cur.fetchall()
                            if not ins_category_check:
                                cur.execute("INSERT INTO category(vchr_name,dat_created) values('"+str_U_CATEGORY+"','"+str(datetime.now())+"') returning pk_bint_id;")
                                category_id = cur.fetchone()[0]
                            else:
                                category_id = ins_category_check[0][0]

                            """products"""
                            str_U_PRODUCTCATEGORY=item.get('ITEMTYPE')

                            if not str_U_PRODUCTCATEGORY:
                                str_U_PRODUCTCATEGORY = 'DEFAULT1'
                            elif str(str_U_PRODUCTCATEGORY).upper() == 'NAN':
                                str_U_PRODUCTCATEGORY = 'DEFAULT2'
                            elif str(str_U_PRODUCTCATEGORY).upper() == '0':
                                str_U_PRODUCTCATEGORY = 'DEFAULT3'

                            str_ItmsGrpNam=item.get('ItemCategory') or 'Salable'
                            if str_ItmsGrpNam.upper() == "SPARE":
                                int_sales = 2
                            else:
                                int_sales = 1

                            cur.execute("SELECT pk_bint_id,vchr_name,int_status FROM products WHERE vchr_name = '"+str_U_PRODUCTCATEGORY+"' ;")
                            ins_product_check = cur.fetchall()
                            if ins_product_check:
                                ins_update = cur.execute("UPDATE products SET int_status = 0,int_sales = '"+str(int_sales)+"',fk_category_id = '"+str(category_id)+"'  WHERE vchr_name = '"+str_U_PRODUCTCATEGORY+"';")
                                products_id = ins_product_check[0][0]
                            else:
                                cur.execute("insert into products(vchr_name,dat_created,fk_category_id) values('"+str_U_PRODUCTCATEGORY+"','"+str(datetime.now())+"','"+str(category_id)+"') returning pk_bint_id;")
                                products_id = cur.fetchone()[0]


                            """brands"""
                            str_U_BRAND=item.get('BrandName')
                            if not str_U_BRAND:
                                str_U_BRAND = "DEFAULT1"
                            elif str(str_U_BRAND).upper() == "NIL":
                                str_U_BRAND = "DEFAULT2"
                            elif str(str_U_BRAND).upper() == "0":
                                str_U_BRAND = "DEFAULT3"

                            cur.execute("SELECT pk_bint_id,vchr_name,int_status FROM brands WHERE vchr_name = '"+str_U_BRAND+"';")
                            ins_brand_check = cur.fetchall()
                            if not ins_brand_check:
                                cur.execute("insert into brands (vchr_name) values('"+str_U_BRAND+"') returning pk_bint_id;")
                                brands_id = cur.fetchone()[0]
                            else:
                                brands_id = ins_brand_check[0][0]

                            """tax master"""
                            cur.execute("select array_agg(vchr_name||':' ||pk_bint_id) from tax_master where vchr_name in ('CGST','SGST','IGST')")
                            tax_master_details = cur.fetchall()[0][0]
                            dct_tax_data = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in tax_master_details}
                            dct_tax = {}
                            if item.get('U_GST'):
                                dct_tax[dct_tax_data['CGST']] = item.get('U_GST')/2
                                dct_tax[dct_tax_data['SGST']] = item.get('U_GST')/2
                                dct_tax[dct_tax_data['IGST']] = item.get('U_GST')
                                # vchr_gst_code = "GST"+str(int(item.get('U_GST')))
                                # cur.execute("SELECT pk_bint_id,jsn_tax_master FROM sap_tax_master WHERE vchr_code = '"+vchr_gst_code+"';")
                                # ins_sap_tax_master = cur.fetchall()
                                # dct_tax = ins_sap_tax_master[0][1]
                            dct_tax = json.dumps(dct_tax)

                            """item category"""
                            str_U_ITEMCATEGORY=item.get('ItemCategory')
                            if not str_U_ITEMCATEGORY:
                                str_U_ITEMCATEGORY = "DEFAULT1"
                            elif str(str_U_ITEMCATEGORY).upper() == "NIL":
                                str_U_ITEMCATEGORY = "DEFAULT2"
                            elif str(str_U_ITEMCATEGORY).upper() == "0":
                                str_U_ITEMCATEGORY = "DEFAULT3"

                            str_HSN_Code=item.get('HsnCode') or ''
                            cur.execute("select pk_bint_id from item_category where vchr_item_category='"+str_U_ITEMCATEGORY+"'")
                            ins_item_category_check = cur.fetchall()
                            if ins_item_category_check:
                                #cur.execute("UPDATE item_category SET json_tax_master = '"+str(dct_tax)+"',json_specification_id = '"+str(lst_specs)+"',vchr_hsn_code = '"+str_HSN_Code+"', int_status = 0 WHERE vchr_item_category = '"+str_U_ITEMCATEGORY+"';")
                                item_category_id = ins_item_category_check[0][0]
                            else:
                                cur.execute("INSERT INTO item_category(vchr_item_category,json_tax_master,json_specification_id,dat_created,vchr_hsn_code) values('"+str_U_ITEMCATEGORY+"','"+str(dct_tax)+"','"+str(lst_specs)+"','"+str(datetime.now())+"','"+str_HSN_Code+"') returning pk_bint_id;")
                                item_category_id = cur.fetchone()[0]


                            """item group"""
                            str_ItmsGrpNam=item.get('U_MODELNO')
                            if not str_ItmsGrpNam :
                                str_ItmsGrpNam = "DEFAULT1"
                            elif str(str_ItmsGrpNam).upper() == "NIL":
                                str_ItmsGrpNam = "DEFAULT2"
                            elif str(str_ItmsGrpNam).upper() == "0":
                                str_ItmsGrpNam = "DEFAULT3"
                            cur.execute("SELECT pk_bint_id,int_status FROM item_group WHERE vchr_item_group = '"+str_ItmsGrpNam+"';")
                            ins_item_group_check = cur.fetchall()
                            if ins_item_group_check:
                                item_group_id = ins_item_group_check[0][0]
                                if ins_item_group_check[0][1] < 0:
                                    cur.execute("UPDATE item_group SET int_status = 0,dat_updated = '"+str(datetime.now())+"' WHERE vchr_item_group = '"+str_ItmsGrpNam+"';")

                            else:
                                cur.execute("insert into item_group (vchr_item_group,dat_created) values('"+str_ItmsGrpNam+"','"+str(datetime.now())+"') returning pk_bint_id;")
                                item_group_id = cur.fetchone()[0]

                            """item"""
                            str_ItemName=item.get('ItemName')
                            if not str_ItemName :
                                str_ItemName = "DEFAULT1"
                            elif str(str_ItemName).upper() == "NIL":
                                str_ItemName = "DEFAULT2"
                            elif str(str_ItemName).upper() == "0":
                                str_ItemName = "DEFAULT3"

                            str_ItemCode=item.get('ItemCode')
                            fk_product_id = products_id
                            fk_brand_id = brands_id
                            fk_item_category_id = item_category_id
                            fk_item_group = item_group_id
                            str_Image_Path = item.get('Image Path')
                            if not str_Image_Path:
                                str_Image_Path = ''
                            str_validFor = item.get('validFor') or 'Y'
                            json_specification_id = json.dumps(dct_specs)
                            imei_status = False
                            if item.get('SERIALNO') == 'Y':
                                imei_status = True
                            elif item.get('BatchNum') == 'Y':
                                imei_status = False
                            if str_validFor.upper() == 'Y':
                                sale_status = True
                            else:
                                sale_status = False

                            cur.execute("SELECT pk_bint_id FROM item WHERE vchr_item_code = '"+str(str_ItemCode)+"';")
                            ins_item_master = cur.fetchall()
                            if ins_item_master:
                                int_item_id = ins_item_master[0][0]

                                cur.execute("update item set vchr_name = '"+str_ItemName+"' ,\
                                        fk_product_id = '"+str(fk_product_id)+"',\
                                        fk_brand_id = '"+str(fk_brand_id)+"',\
                                        vchr_item_code = '"+str_ItemCode+"',\
                                        fk_item_category_id = '"+str(fk_item_category_id)+"',\
                                        fk_item_group_id = '"+str(fk_item_group)+"',\
                                        json_specification_id = '"+json_specification_id+"',\
                                        imei_status = '"+str(imei_status)+"',\
                                        sale_status = '"+str(sale_status)+"',\
                                        int_status = 0,\
                                        image1 = '"+str_Image_Path+"',\
                                        dat_updated = '"+str(datetime.now())+"' where pk_bint_id = '"+str(int_item_id)+"';")

                                lst_updated.append(int_item_id)
                            else:
                                cur.execute("insert into item(vchr_name,fk_product_id,fk_brand_id,vchr_item_code,fk_item_category_id,fk_item_group_id,json_specification_id,imei_status,sale_status,dat_created,dbl_supplier_cost,dbl_dealer_cost,dbl_mrp,dbl_mop,image1)\
                                                    values('"+str_ItemName+"','"+str(fk_product_id)+"','"+str(fk_brand_id)+"','"+str_ItemCode+"','"+str(fk_item_category_id)+"','"+str(fk_item_group)+"','"+json_specification_id+"','"+str(imei_status)+"','"+str(sale_status)+"','"+str(datetime.now())+"',0,0,0,0,'"+str_Image_Path+"');")
                                lst_added.append(str_ItemCode)

                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            exc_tb.tb_lineno
                            # import pdb; pdb.set_trace()
                            lst_error_code.append(str_ItemCode)
                            lst_error_reason.append(str(e))
                            pass





        print('added - ')
        print(len(lst_added))
        print('updated - ')
        print(len(lst_updated))
        print(time.time()-time_start)
        print('successfully imported')
        cur.close()
        conn.close()

        if lst_error_code:
            #creating dataframes
            df_item = pd.DataFrame({'ITEM CODE':lst_error_code,'REASON':lst_error_reason})
            #creating and writing to excel
            excel_file = 'itemsMaster_error_from_api.xlsx'
            file_name_export = excel_file
            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_item.to_excel(writer,sheet_name='Sheet1',index=True, startrow=0,startcol=0)
            writer.save()

    except Exception as e:
        cur.close()
        print(str(e))
        conn.close()
        # import pdb; pdb.set_trace()
        raise


if __name__ == '__main__':
    date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) == 2:
        date = sys.argv[1]
    itemsfromsap(date)
