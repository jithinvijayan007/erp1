import sys
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
from datetime import datetime
import time
import pandas as pd
# date = '2019-08-01'
def pricelistfromsap(date):
    """
    Used to save price_list data to pos
    paramerters(to SAP):
    response(from SAP):suceess/failed
    """
    try:
        time_start = time.time()
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="pos", user="admin", password="tms@123")
            # conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor()
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})

        #import pdb;pdb.set_trace()  
        #url = 'http://myglive.tmicloud.net:8084/api/master/PriceList'
        url = 'http://13.71.18.142:8086/api/master/PriceList'
        #PARAMS = {'FDate':'2000-05-10'}
        PARAMS = {'FDate':date}

        res_data=requests.get(url=url,params=PARAMS)

        if res_data.status_code == 200:
            dct_data = res_data.json()
            if dct_data:
                lst_added = []
                lst_updated = []
                lst_error_reason = []
                lst_error_code = []
                for item in dct_data:
                    try:
                        dbl_mrp = item.get('MRP') or 0
                        dbl_mop = item.get('MOP') or 0
                        dbl_cost_price = item.get('CostPrice') or 0
                        dbl_dealer_price = item.get('DealerPrice') or 0
                        dbl_sup_amt = item.get('CostPrice') or 0
                        str_itemCode= item.get('ItemCode')
                        dat_effective_from = item.get('DateEffective')
                        dbl_myg_price = item.get('MSP') or 0

                        """getting details from item"""
                        str_query_data = "select pk_bint_id,dbl_mrp,dbl_mop,dbl_supplier_cost,dbl_dealer_cost,dbl_myg_amount from item where vchr_item_code = '"+str_itemCode+"';"
                        cur.execute(str_query_data)
                        rst_item_id = cur.fetchall()

                        if rst_item_id:
                            int_item_id = rst_item_id[0][0]
                            dbl_item_mrp = rst_item_id[0][1]
                            dbl_item_mop = rst_item_id[0][2]
                            dbl_item_supplier_cost = rst_item_id[0][3]
                            dbl_item_dealer_cost = rst_item_id[0][4]
                            dbl_item_myg_price = rst_item_id[0][5]

                            """if price is price list doesn't match with price in item"""
                            if dbl_item_myg_price!=dbl_myg_price or dbl_mrp != dbl_item_mrp or dbl_mop != dbl_item_mop or dbl_sup_amt != dbl_item_supplier_cost or dbl_dealer_price != dbl_item_dealer_cost:
                                ins_item_update = cur.execute("UPDATE item SET dbl_myg_amount = "+str(dbl_myg_price)+",dbl_mrp = '"+str(dbl_mrp)+"',dbl_mop = '"+str(dbl_mop)+"',dbl_supplier_cost = '"+str(dbl_sup_amt)+"', dbl_dealer_cost = '"+str(dbl_dealer_price)+"',dat_updated = '"+str(datetime.now())+"' WHERE pk_bint_id = '"+str(int_item_id)+"'; ")

                            """checking if item in price list is present"""
                            cur.execute("select pk_bint_id from price_list where fk_item_id = '"+str(int_item_id)+"';")
                            rst_price_list = cur.fetchall()

                            if rst_price_list:
                                int_price_list = rst_price_list[0][0]
                                cur.execute("UPDATE price_list SET  dbl_my_amt="+str(dbl_myg_price)+",dbl_mrp = '"+str(dbl_mrp)+"',dbl_mop = '"+str(dbl_mop)+"',dbl_cost_amnt = '"+str(dbl_cost_price)+"',dat_efct_from='"+ str(dat_effective_from) +"', dbl_dealer_amt = '"+str(dbl_dealer_price)+"',dbl_supp_amnt = '"+str(dbl_sup_amt)+"',dat_created = '"+str(datetime.now())+"' WHERE pk_bint_id = '"+str(int_price_list)+"' returning pk_bint_id;")
                                int_id = cur.fetchone()
                                lst_updated.append(str_itemCode)

                            else:
                                cur.execute("INSERT INTO price_list(dbl_my_amt,dbl_mrp,dbl_mop,dbl_cost_amnt,dbl_dealer_amt,dbl_supp_amnt,fk_item_id,dat_created,dat_efct_from) VALUES("+str(dbl_myg_price)+",'"+str(dbl_mrp)+"','"+str(dbl_mop)+"','"+str(dbl_cost_price)+"','"+str(dbl_dealer_price)+"','"+str(dbl_sup_amt)+"','"+str(int_item_id)+"','"+str(datetime.now())+"','"+str(dat_effective_from)+"') returning pk_bint_id;")
                                int_id = cur.fetchone()
                                lst_added.append(str_itemCode)


                        else:
                            lst_error_code.append(str_itemCode)
                            lst_error_reason.append(str("no item"))

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        exc_tb.tb_lineno
                        # import pdb; pdb.set_trace()
                        lst_error_code.append(str_itemCode)
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
                    excel_file = 'price_list_error_from_api.xlsx'
                    file_name_export = excel_file
                    writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
                    df_item.to_excel(writer,sheet_name='Sheet1',index=True, startrow=0,startcol=0)
                    writer.save()

            else:
                print("no data")
        else:
            print("error from sap")
        cur.close()
        conn.close()
        return 1

    except Exception as e:
        cur.close()
        conn.close()
        raise


if __name__ == '__main__':
    date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) == 2:
        date = sys.argv[1]
    pricelistfromsap(date)
