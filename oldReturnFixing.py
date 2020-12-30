from sqlalchemy import create_engine
import json
import requests
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

def batchstockcorrection():
    
    try:
        try:
            conn = None
            # conn = psycopg2.connect(host="localhost",database="pos", user="admin", password="uDS$CJ8j")
            conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="nisam@123")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)
        except Exception as e:
            raise
        cur.execute("select sr.pk_bint_id,jsn_imei from sales_return sr join item it on it.pk_bint_id=sr.fk_item_id where fk_product_id !=29 and imei_status=false and fk_returned_id is null order by 1")
        rst_return =cur.fetchall()
        lst_batch=[]
        if rst_return:
            for ins_return in rst_return:
                if ins_return['jsn_imei'][0] == "2265653'":
                    continue
                jsn_imei = json.dumps({"imei":[]})
                jsn_imei_avail = json.dumps({"imei_avail":[]})
                jsn_batch = json.dumps({"batch":[ins_return['jsn_imei'][0]]})
                cur.execute("select gd.pk_bint_id from grn_details gd join item it on it.pk_bint_id=gd.fk_item_id where imei_status=false and (jsn_imei->>'imei')::jsonb ? '"+ins_return['jsn_imei'][0]+"' order by 1 limit 1")
                rst_grn=cur.fetchall()
                if rst_grn:
                    int_grn_id = rst_grn[0]['pk_bint_id']
                    cur.execute("update grn_details set jsn_imei='"+jsn_imei+"',jsn_imei_avail='"+jsn_imei_avail+"',int_avail=0,vchr_batch_no='"+ins_return['jsn_imei'][0]+"' where pk_bint_id="+str(int_grn_id))
                    cur.execute("select bd.pk_bint_id from branch_stock_details bd join item it on it.pk_bint_id=bd.fk_item_id where imei_status=false and (jsn_imei->>'imei')::jsonb ? '"+ins_return['jsn_imei'][0]+"' order by 1 limit 1")
                    int_bd_id=cur.fetchall()[0]['pk_bint_id']
                    cur.execute("update branch_stock_details set jsn_imei='"+jsn_imei+"',jsn_imei_avail='"+jsn_imei+"',jsn_batch_no='"+jsn_batch+"' where pk_bint_id="+str(int_bd_id))
                    cur.execute("select pk_bint_id from branch_stock_imei_details where fk_details_id="+str(int_bd_id))
                    rst_bid_id = cur.fetchall()
                    if rst_bid_id:
                        int_bid_id = rst_bid_id[0]['pk_bint_id']
                        cur.execute("update branch_stock_imei_details set fk_grn_details_id="+str(int_grn_id)+",jsn_imei='"+jsn_imei+"',jsn_imei_reached='"+jsn_imei+"',jsn_batch_no='"+jsn_batch+"',jsn_batch_reached='"+jsn_batch+"' where pk_bint_id="+str(int_bid_id))
                    else:
                        cur.execute("insert into branch_stock_imei_details(fk_details_id,fk_grn_details_id,jsn_imei,jsn_imei_reached,jsn_batch_no,jsn_batch_reached,int_received,int_qty) values("+str(int_bd_id)+","+str(int_grn_id)+",'"+jsn_imei+"','"+jsn_imei+"','"+jsn_batch+"','"+jsn_batch+"',1,1)")
                else:
                    lst_batch.append(ins_return['jsn_imei'][0])
            print("batch not corrected"+str(lst_batch))
            cur.close()
            conn.close()
            return "Success"
        else:
            print("Nodata")
            cur.close()
            conn.close()
            return "Success"
    except Exception as e:
        conn.rollback()
        import pdb;pdb.set_trace()
        cur.close()
        conn.close()
        print(str(e))

if __name__=='__main__':
    batchstockcorrection()