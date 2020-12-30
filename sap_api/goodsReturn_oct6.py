from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import sys

def GoodsReturn(date):
    """
            Function to remove the returned items from grn details and branch stock details.
            return: Success

    """
    try:
        try:
            conn = None
            #conn = psycopg2.connect(host="localhost",database="myg_pos_live", user="admin", password="A@y2M!9K")
            conn = psycopg2.connect(host="localhost",database="myg_pos_live", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
        except Exception as e:
            return 0

        cur = conn.cursor()
        import pdb;pdb.set_trace()
        url = "http://13.71.18.142:8086/api/GoodsReturn"
        PARAMS = {'FDate':date}
        res_data=requests.get(url=url,params=PARAMS)
        if res_data.status_code == 200:
            #soup = BeautifulSoup(res_data.text, "xml")
            #str_data = soup.string #   To get *list inside  , <string> *[] </string>
            dct_data = json.loads(res_data.text) # String to Json
            if dct_data:
                lst_imei = []
                for item in dct_data:
                    for lst_data in item['line']:
                        lst_imei.extend(lst_data['IntrSerial'])
                #lst_imei = [item['IntrSerial'] for item in dct_data if item['IntrSerial']]
                lst_imei_updated = []
# ===================================================================GRN Details===============================================================================================
                #  Data from grn_details->>imei_avail
                if lst_imei:
                    cur.execute("select pk_bint_id,jsn_imei_avail from grn_details where (jsn_imei_avail->>'imei_avail')::jsonb?|array"+str(lst_imei))
                    lst_grn_avail = cur.fetchall()

                    if lst_grn_avail:
                        lst_value = []
                        str_values = " "
                        str_const = '"imei_avail"'
                        for item in lst_grn_avail:
                            lst_imei_avail = item[1]['imei_avail']
                            lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and return_imei_list
                            lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                            lst_imei_updated.extend(lst_return_imei)

                            str_values += "("+str(item[0])+",'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB,"+str(len(lst_remains_imei))+"),"

                        str_values = str_values[:-1]
                        cur.execute("update grn_details as bs set int_avail = lst_new.qty,jsn_imei_avail = lst_new.imei from (values "+str_values+" ) as lst_new(pk_bint_id,imei,qty) where lst_new.pk_bint_id = bs.pk_bint_id")

                    #for str_batch in lst_imei:
                     #   cur.execute("update grn_details set int_avail = int_avail-1,int_damaged=int_damaged+1 where vchr_batch_no='"+str_batch+"' and int_avail>0")
                      #  cur.execute("update branch_stock_details set int_qty = int_qty-1 where pk_bint_id =(select bsd.pk_bint_id from branch_stock_details bsd join branch_stock_master bm on bsd.fk_master_id=bm.pk_bint_id join branch br on br.pk_bint_id=bm.fk_branch_id where br.int_type in (2,3) and (bsd.jsn_batch_no->>'batch')::jsonb ? '"+str_batch+"' and bsd.int_qty>0 limit 1)")
                       # cur.execute("update branch_stock_imei_details set int_qty = int_qty-1 where pk_bint_id =(select bid.pk_bint_id from branch_stock_imei_details bid join branch_stock_details bsd on bsd.pk_bint_id=bid.fk_details_id join branch_stock_master bm on bsd.fk_master_id=bm.pk_bint_id join branch br on br.pk_bint_id=bm.fk_branch_id where br.int_type in (2,3) and (bid.jsn_batch_no->>'batch')::jsonb ? '"+str_batch+"' and bid.int_qty>0 limit 1)")

                #  Data from grn_details->>imei_dmgd
                lst_imei = list(set(lst_imei)-set(lst_imei_updated))
                if lst_imei:
                    cur.execute("select pk_bint_id,jsn_imei_dmgd from grn_details where (jsn_imei_dmgd->>'imei_damage')::jsonb?|array"+str(lst_imei))
                    lst_grn_dmgd = cur.fetchall()

                    if lst_grn_dmgd:
                        lst_value = []
                        str_values = " "
                        str_const = '"imei_damage"'
                        for item in lst_grn_dmgd:
                            lst_imei_avail = item[1]['imei_damage']
                            lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and return_imei_list
                            lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                            lst_imei_updated.extend(lst_return_imei)

                            str_values += "("+str(item[0])+",'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB,"+str(len(lst_remains_imei))+"),"

                        str_values = str_values[:-1]
                        cur.execute("update grn_details as bs set int_damaged = lst_new.qty,jsn_imei_dmgd = lst_new.imei from (values "+str_values+" ) as lst_new(pk_bint_id,imei,qty) where lst_new.pk_bint_id = bs.pk_bint_id")

# =============================================================================Branch Stock details===================================================================================================
                #  Data from branch_stock_details->>imei_dmgd
                lst_imei = list(set(lst_imei)-set(lst_imei_updated))
                if lst_imei:
                    cur.execute("select pk_bint_id,jsn_imei_dmgd from branch_stock_details where (jsn_imei_dmgd->>'imei')::jsonb?|array"+str(lst_imei))
                    lst_branch_dmgd = cur.fetchall()

                    if lst_branch_dmgd:

                        lst_value = []
                        str_values = " "
                        str_const = '"imei"'
                        for item in lst_branch_dmgd:
                            lst_imei_avail = item[1]['imei']
                            lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and return_imei_list
                            lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                            lst_imei_updated.extend(lst_return_imei)

                            str_values += "("+str(item[0])+",'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB,"+str(len(lst_remains_imei))+"),"

                        str_values = str_values[:-1]
                        cur.execute("update branch_stock_details as bs set jsn_imei_dmgd=lst_new.imei from (values "+str_values+" ) as lst_new(pk_bint_id,imei) where lst_new.pk_bint_id = bs.pk_bint_id")

                #  Data from branch_stock_details->>imei_avail
                lst_imei = list(set(lst_imei)-set(lst_imei_updated))
                if lst_imei:

                    # branch_stock_details -->imei_available
                    cur.execute("select pk_bint_id,jsn_imei_avail from branch_stock_details where (jsn_imei_avail->>'imei')::jsonb?|array"+str(lst_imei))
                    lst_branch_avail = cur.fetchall()

                    
                    
                    if lst_branch_avail:

                        lst_value = []
                        str_values = " "
                        str_const = '"imei"'
                        for item in lst_branch_avail:
                            lst_imei_avail = item[1]['imei']
                            lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and lst_imei
                            lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))
                            lst_imei_updated.extend(lst_return_imei) # add the updated imei to  lst_imei_updated

                            str_values += "("+str(item[0])+",'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB,"+str(len(lst_remains_imei))+"),"

                        str_values = str_values[:-1]
                        cur.execute("update branch_stock_details as bs set int_qty = lst_new.qty,jsn_imei_avail=lst_new.imei from (values "+str_values+" ) as lst_new(pk_bint_id,imei,qty) where lst_new.pk_bint_id = bs.pk_bint_id")
                    
                    
                    # branch_stock_imei_details -->imei
                    cur.execute("select pk_bint_id,jsn_imei from branch_stock_imei_details where (jsn_imei->>'imei')::jsonb?|array"+str(lst_imei))
                    lst_branch_imei_details = cur.fetchall()

                    if lst_branch_imei_details:

                        lst_value = []
                        str_values = " "
                        str_const = '"imei"'
                        for item in lst_branch_imei_details:
                            lst_imei_avail = item[1]['imei']
                            lst_return_imei = list(set(lst_imei) & set(lst_imei_avail)) # common imei in lst_imei_avail and lst_imei
                            lst_remains_imei = list(set(lst_imei_avail)-set(lst_imei))

                            str_values += "("+str(item[0])+",'{"+str_const+":"+str(json.dumps(lst_remains_imei))+"}'::JSONB,"+str(len(lst_remains_imei))+"),"

                        str_values = str_values[:-1]
                        cur.execute("update branch_stock_imei_details as bs set int_qty = lst_new.qty,jsn_imei=lst_new.imei from (values "+str_values+" ) as lst_new(pk_bint_id,imei,qty) where lst_new.pk_bint_id = bs.pk_bint_id")


                print("Returned IMEI : ",lst_imei_updated)
                cur.close()
                conn.close()
                return 1
            else:
                print('No Data')
                cur.close()
                conn.close()
                return 0

    except Exception as e:
        cur.close()
        conn.close()
        return 0

if __name__ == '__main__':
    date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) == 2:
        date = sys.argv[1]
    GoodsReturn(date)
