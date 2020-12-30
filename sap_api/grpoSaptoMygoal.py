import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import sys
from datetime import datetime,timedelta

# conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="tms@123")
conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
conn.autocommit = True
cur = conn.cursor()
# NEW
# ------------------------------------------------------------------------
def grpo_from_sap(date):
    try:
        #import pdb;pdb.set_trace()
        #date='2020-05-13'
        #str_url = "http://myglive.tmicloud.net:8084/api/GRPO?FDate="+str(date)
        str_url = "http://13.71.18.142:8086/api/GRPO?FDate="+str(date)
        res_data = requests.get(str_url)
        dct_data = res_data.json()
        lst_na_item=[]
        if dct_data:
            str_supplier_details = "select su.pk_bint_id,su.int_po_expiry_days,su.int_batch_no_offset,su.int_credit_days,fk_states_id from supplier su where vchr_code ='"
            srt_branch = "select pk_bint_id,fk_states_id from branch where int_type in (2,3) and vchr_code not in ('MCH') and vchr_code = '"
            str_item_details = "select pk_bint_id,imei_status from item where vchr_item_code = '"
            for ins_data in dct_data:
                str_item_exists = "select * from grn_master where vchr_purchase_num ='"+str(ins_data['DocNum'])+"';"
                cur.execute(str_item_exists)
                rst_item_exists = cur.fetchall()
                bln_continue = True
                if not rst_item_exists:
                    str_branch_query = srt_branch+ins_data['WhsCode']+"'"
                    cur.execute(str_branch_query)
                    rst_branch = cur.fetchall()
                    if not rst_branch:
                       continue
                    rst_branch = rst_branch[0]
                    str_supplier_query = str_supplier_details+ins_data['VendorCode']+"'"
                    cur.execute(str_supplier_query)
                    print(ins_data['VendorCode'])
                    rst_suplier = cur.fetchall()[0]

                    ins_data['BillNo'] = ins_data['BillNo'] if ins_data['BillNo'] else ins_data['DocNum']
                    if not ins_data['BillImages'][0]:
                        ins_data['BillImages'] = ['null']
                    fk_po_id = 'null'
                    dbl_addition = 0
                    dbl_deduction = 0
                    if ins_data['Freight']:
                        dbl_deduction=0
                        dbl_addition=0
                    cur.execute("insert into grn_master(vchr_purchase_num,dat_purchase,fk_supplier_id,fk_branch_id,fk_po_id,int_doc_status,dbl_roundoff_value,int_approve,vchr_bill_no,dat_bill,dbl_bill_amount,vchr_bill_image,dbl_addition,dbl_deduction,dat_created,dbl_total) values('"+ins_data['DocNum']+"','"+str(ins_data['GRNDate'])+"',"+str(rst_suplier[0])+","+str(rst_branch[0])+","+fk_po_id+",1,"+str(ins_data['RoundDif'])+",2,'"+ins_data['BillNo']+"','"+str(ins_data['TaxDate'])+"',"+str(ins_data['DocTotal'])+",'"+ins_data['BillImages'][0]+"',"+str(dbl_addition)+","+str(dbl_deduction)+",'"+str(ins_data['GRNDate'])+"',"+str(ins_data['DocTotal'])+") RETURNING pk_bint_id;")
                    fk_purchase_id = cur.fetchone()[0]

                    for ins_item in ins_data['line']:
                        if not bln_continue:
                            continue
                        str_item_query = str_item_details+ins_item['ItemCode']+"'"
                        cur.execute(str_item_query)
                        rst_item_id = cur.fetchall()
                        if rst_item_id:
                            int_item_id = rst_item_id[0][0]
                            bln_imei_status = rst_item_id[0][1]
                            ins_item['FreeQty'] = ins_item['FreeQty'] if ins_item['FreeQty'] !='N' else 0
                            ins_item['Quantity']=ins_item['Quantity']+ins_item['FreeQty']
                            ins_item['TaxRate']=ins_item['TaxRate'] if ins_item['TaxRate'] else 0
                            if rst_branch[1] == rst_suplier[4]:
                                jsn_tax = {'SGST':(ins_item['Price']/100)*(ins_item['TaxRate']/2),'CGST':(ins_item['Price']/100)*(ins_item['TaxRate']/2),'SGST%':ins_item['TaxRate']/2,'CGST%':ins_item['TaxRate']/2,'IGST':0.0,'IGST%':0.0}
                                dbl_tax = jsn_tax['SGST'] * ins_item['Quantity'] + jsn_tax['CGST'] * ins_item['Quantity']
                            else:
                                jsn_tax = {'SGST':0.0,'CGST':0.0,'SGST%':0.0,'CGST%':0.0,'IGST':(ins_item['Price']/100)*ins_item['TaxRate'],'IGST%':ins_item['TaxRate']}
                                dbl_tax = jsn_tax['IGST'] * ins_item['Quantity']
                                # dbl_ppu = round(ins_data['Price'] + jsn_tax['IGST'] + (ins_data['Price']/100)*ins_data['DiscPrcnt'],2)
                            if bln_imei_status:
                                jsn_imei = {"imei":ins_item['IntrSerial']}
                                jsn_imei_avail = {"imei_avail":ins_item['IntrSerial']}
                                vchr_batch_num = ""
                                #ins_item['Quantity'] = ins_item['Quantity']/len(ins_item['jsn_imei'])
                            else:
                                jsn_imei = {"imei":[]}
                                jsn_imei_avail = {"imei_avail":[]}
                                vchr_batch_num = ins_item['IntrSerial'][0]
                            dbl_ppu = round(ins_item['Price'] +(ins_item['Price']/100)*ins_item['TaxRate']- (ins_item['Price']/100)*ins_item['DiscPrcnt'],2)
                            dbl_discount_per= round((ins_item['Price']/100)*ins_item['DiscPrcnt'],2)
                            dbl_discount_sum = dbl_discount_per * ins_item['Quantity']
                            dbl_total_item = dbl_ppu * ins_item['Quantity']
                            cur.execute("insert into grn_details(fk_item_id,fk_purchase_id,int_qty,int_free,int_avail,int_damaged,dbl_costprice,dbl_dscnt_percent,dbl_dscnt_perunit,dbl_discount,jsn_tax,dbl_tax,dbl_ppu,dbl_total_amount,vchr_batch_no,jsn_imei,jsn_imei_avail,dbl_perpie_aditn,dbl_perpie_dedctn) values("+str(int_item_id)+","+str(fk_purchase_id)+","+str(ins_item['Quantity'])+","+str(ins_item['FreeQty'])+","+str(ins_item['Quantity'])+",0,"+str(ins_item['Price'])+","+str(ins_item['DiscPrcnt'])+","+str(dbl_discount_per)+","+str(dbl_discount_sum)+",'"+json.dumps(jsn_tax)+"',"+str(dbl_tax)+","+str(round(ins_item['Price'],2))+","+str(round(ins_item['Price']*ins_item['Quantity'],2))+",'"+vchr_batch_num+"','"+json.dumps(jsn_imei)+"','"+json.dumps(jsn_imei_avail)+"',0.0,0.0)")
                        else:
                            cur.execute("delete from grn_details where fk_purchase_id="+str(fk_purchase_id))
                            cur.execute("delete from grn_master where pk_bint_id="+str(fk_purchase_id))
                            lst_na_item.append(ins_item['ItemCode'])
                            bln_continue=False
                            print(ins_item['ItemCode'])
        cur.close()
        conn.close()
        return 0
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))

if __name__ == '__main__':
    str_date = datetime.strftime(datetime.now()-timedelta(minutes=20),'%Y-%m-%d %H:%M') #datetime.strftime(datetime.now(),'%Y-%m-%d')
    str_date = str_date+':00'
    if len(sys.argv) >1:
        str_date = sys.argv[1]
    grpo_from_sap(str_date)
