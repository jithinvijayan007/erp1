import sys
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import pandas as pd
from datetime import datetime
import time

def pricelistfromexcel(date):
    """
    Used to save price_list data to pos
    paramerters(to SAP):
    response(from SAP):suceess/failed
    """
    try:
        # import pdb; pdb.set_trace()
        time_start = time.time()
        try:
            conn = psycopg2.connect(host="localhost",database="pos_sap_new", user="admin", password="tms@123")
            cur = conn.cursor()
            conn.autocommit = True
            df = pd.read_excel("Main master.xlsx",header=0,sheet_name="price lisit")
        except Exception as e:
            return 'cannot read excel'

        lst_added = []
        lst_item = []
        lst_index =[]
        lst_no_item = []
        lst_error_reason = []
        lst_no_item_index =[]
        for ind,row in df.iterrows():
            try:
                dbl_mrp = row['MRP']
                dbl_mop = row['MOP']
                dbl_cost_price = row['Cost Price']
                dbl_dealer_price = row['Dealer Price']
                dbl_sup_amt = row['MSP']
                str_itemCode= row['Item No./SAP CODE']

                """getting details from item"""
                str_query_data = "select pk_bint_id,dbl_mrp,dbl_mop,dbl_supplier_cost,dbl_dealer_cost from item where vchr_item_code = '"+str_itemCode+"';"
                cur.execute(str_query_data)
                rst_item_id = cur.fetchall()

                if rst_item_id:
                    int_item_id = rst_item_id[0][0]
                    dbl_item_mrp = rst_item_id[0][1]
                    dbl_item_mop = rst_item_id[0][2]
                    dbl_item_supplier_cost = rst_item_id[0][3]
                    dbl_item_dealer_cost = rst_item_id[0][4]

                    """if price is price list doesn't match with price in item"""
                    if dbl_mrp != dbl_item_mrp or dbl_mop != dbl_item_mop or dbl_sup_amt != dbl_item_supplier_cost or dbl_dealer_price != dbl_item_dealer_cost:
                        ins_item_update = cur.execute("UPDATE item SET dbl_mrp = '"+str(dbl_mrp)+"',dbl_mop = '"+str(dbl_mop)+"',dbl_supplier_cost = '"+str(dbl_sup_amt)+"',dbl_dealer_cost = '"+str(dbl_dealer_price)+"',dat_updated = '"+str(datetime.now())+"' WHERE pk_bint_id = '"+str(int_item_id)+"'; ")

                    """checking if item in price list is present"""
                    cur.execute("select pk_bint_id from price_list where fk_item_id = '"+str(int_item_id)+"';")
                    rst_price_list = cur.fetchall()

                    if rst_price_list:
                        int_price_list = rst_price_list[0][0]
                        cur.execute("UPDATE price_list SET dbl_mrp = '"+str(dbl_mrp)+"',dbl_mop = '"+str(dbl_mop)+"',dbl_cost_amnt = '"+str(dbl_cost_price)+"',dbl_dealer_amt = '"+str(dbl_dealer_price)+"',dbl_supp_amnt = '"+str(dbl_sup_amt)+"',dat_created = '"+str(datetime.now())+"' WHERE fk_item_id = '"+str(int_price_list)+"' returning pk_bint_id;")
                        int_id = cur.fetchone()

                    else:
                        cur.execute("INSERT INTO price_list(dbl_mrp,dbl_mop,dbl_cost_amnt,dbl_dealer_amt,dbl_supp_amnt,fk_item_id,dat_created) VALUES('"+str(dbl_mrp)+"','"+str(dbl_mop)+"','"+str(dbl_cost_price)+"','"+str(dbl_dealer_price)+"','"+str(dbl_sup_amt)+"','"+str(int_item_id)+"','"+str(datetime.now())+"') returning pk_bint_id;")
                        int_id = cur.fetchone()


                    lst_added.append(str_itemCode)


                else:
                    lst_no_item.append(str_itemCode)
                    lst_no_item_index.append(ind)

            except Exception as e:
                lst_item.append(str_itemCode)
                lst_error_reason.append(str(e))
                lst_index.append(ind)
                pass

        print("added - ")
        print(len(lst_added))
        print(time.time()-time_start)
        if lst_item or lst_no_item:
            #creating dataframes
            df_error = pd.DataFrame({'INDEX_NUM':lst_index,'ITEM CODE':lst_item,'REASON':lst_error_reason})
            df_no_item = pd.DataFrame({'INDEX_NUM':lst_no_item_index,'ITEM CODE':lst_no_item})
            #creating and writing to excel
            excel_file = 'pricelist_error.xlsx'
            file_name_export = excel_file
            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_error.to_excel(writer,sheet_name='error',index=True, startrow=0,startcol=0)
            df_no_item.to_excel(writer,sheet_name='no item',index=True, startrow=0,startcol=0)
            writer.save()



    except Exception as e:
        raise


if __name__ == '__main__':
    pricelistfromexcel(sys.argv)
