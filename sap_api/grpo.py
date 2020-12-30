from datetime import datetime
import requests
import psycopg2
import json
from psycopg2.extras import RealDictCursor
import os


#------------------ Not Completed (Sudheesh) ----------------------------

def GRPO_sapre_part(str_entry,doc_date):
    """
        Function to pass GRPO(Spare parts) Details to SAP by POST method.
        param: SalesMaster pk_bint_id

            SAP_API_Arg :
                    Master:- MYGOAL_KEY,ShowRoomID,CardCode,CardName,DocDate,DocNum,Type
                    Details:- ItemCode,Quantity,Amount,TaxCode,Mnfserial,Costcenter,LocCode
            SAP_API_return :Success

        return: 1 for success , 0 for fail

    """
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
#            conn = psycopg2.connect(host="localhost",database="pos_db", user="admin", password="tms@123")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        
        cur.execute("select int_document_id from sap_api_track where int_type=15 and int_status!=2 and dat_document::DATE='"+doc_date+"' order by int_document_id")
        rst_grn = cur.fetchall()
        lst_grn_id = [str(i['int_document_id']) for i in rst_grn] if rst_grn else []
#        lst_grn_id =['5960']  #,'7569','5960','7626','7653','7504','7301','7224']
        print(lst_grn_id)
        if lst_grn_id:
            str_file=doc_date.replace("-","")+'/Grpo.txt'
            #str_file="CombinedBillsIssues.txt"
#            file_object = open(str_file, 'w')
 #           file_object.close()
#        import pdb;pdb.set_trace()
        for str_id in lst_grn_id:
            try:
                cur.execute("select jsn_imei,int_qty,dbl_ppu,dbl_dscnt_perunit,vchr_batch_no,imei_status,br.vchr_code as branch,gm.dat_purchase,it.vchr_item_code,ve.vchr_code as vendor,ve.vchr_name as vendor_name,json_tax_master,vchr_purchase_num,bd.vchr_code as brand,br.fk_states_id as branch_state,adve.fk_states_id as supplier_state,it.dbl_mop as mop from grn_master gm join grn_details gd on gd.fk_purchase_id=gm.pk_bint_id join branch br on br.pk_bint_id=gm.fk_branch_id join item it on it.pk_bint_id=gd.fk_item_id join item_category itc on itc.pk_bint_id=it.fk_item_category_id join brands bd on bd.pk_bint_id=it.fk_brand_id join supplier ve on ve.pk_bint_id=gm.fk_supplier_id left outer join address_supplier adve on ve.pk_bint_id=adve.fk_supplier_id where br.vchr_code = 'MCH' and gm.pk_bint_id="+str_id)
                rst_grn_details = cur.fetchall()
                if not rst_grn_details:
 #               import pdb;pdb.set_trace()
                    continue

                dct_data = {}
                dct_data['Header'] = []
                dct_data['Line Level'] = []
                dct_data['Freight']=[]
                str_tax_master = "select array_agg(vchr_name||':' ||pk_bint_id) from tax_master"
                cur.execute(str_tax_master)
                rst_tax_details = cur.fetchall()[0]['array_agg']
                dct_tax = {str_tax.split(':')[0]:str_tax.split(':')[1] for str_tax in rst_tax_details}
                bln_kfc = False
                bln_igst = False
                dct_freight_discount={}
#            import pdb;pdb.set_trace()
                for ins_data in rst_grn_details:
                    json_tax=ins_data['json_tax_master']
                    if ins_data['branch_state'] and ins_data['supplier_state'] and ins_data['branch_state'] != ins_data['supplier_state']:
                        bln_igst = True
                    dbl_tax=0
                    dbl_tax_to_check=0
                    if bln_igst:
                        if dct_tax['CGST'] in json_tax or dct_tax['SGST'] in json_tax:
                            json_tax.pop(dct_tax['CGST'])
                            json_tax.pop(dct_tax['SGST'])
                                
                        if dct_tax['IGST'] in json_tax:
                            dbl_tax = json_tax[dct_tax['IGST']]
                            dbl_tax_to_check= json_tax[dct_tax['IGST']]

                    else:
                        if dct_tax['IGST'] in json_tax :
                            json_tax.pop(dct_tax['IGST'])
                            dbl_tax = json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                            dbl_tax_to_check= json_tax[dct_tax['CGST']]+json_tax[dct_tax['SGST']]
                    str_tax_code = "select vchr_code from sap_tax_master where jsn_tax_master = '"+str(json.dumps(json_tax))+"';"
                    cur.execute(str_tax_code)
                    rst_tax_code = cur.fetchall()[0]['vchr_code']
                    dct_line_data= {}
                    dct_line_data["Amount"] = ((ins_data['dbl_ppu']+ins_data['dbl_dscnt_perunit'])/((100+dbl_tax_to_check)/100))*ins_data['int_qty']
                    dct_line_data["Brand"] = ins_data['brand']
                    dct_line_data["Department"] = ''
                    dct_line_data["ItemCode"] = ins_data['vchr_item_code']
                    if ins_data['imei_status']:
                        dct_line_data["MnfSerial"] = ins_data['jsn_imei']['imei']
                    else:  #if not dct_line_data["MnfSerial"]:
                        dct_line_data["MnfSerial"] = [ins_data['vchr_batch_no']]
                    dct_line_data["Quantity"] = ins_data['int_qty']
                    dct_line_data["Store"] = ins_data['branch']
                    dct_line_data["TaxCode"] = rst_tax_code
                    dct_line_data["WhsCode"] = ins_data['branch']
#                if not dct_line_data["MnfSerial"]:
#                    import pdb;pdb.set_trace()
#                    print(ins_data)
                    dct_data['Line Level'].append(dct_line_data)

                    if dbl_tax_to_check and (dbl_tax_to_check%1) ==0:
                        dbl_tax_to_check = int(dbl_tax_to_check)
                        
                    if ins_data['dbl_dscnt_perunit'] and rst_tax_code not in dct_freight_discount:

                        dct_freight_discount[rst_tax_code] = {}
                        dct_freight_discount[rst_tax_code]['tax_code'] = str(dbl_tax_to_check) if dbl_tax_to_check==0 or dbl_tax_to_check>10 else '0'+str(dbl_tax_to_check)
                        dct_freight_discount[rst_tax_code]['amount'] = round(ins_data['dbl_dscnt_perunit']/((100+dbl_tax)/100),3)
                    elif ins_data['dbl_dscnt_perunit']:
                        dct_freight_discount[rst_tax_code]['amount'] += round(ins_data['dbl_dscnt_perunit']/((100+dbl_tax)/100),3)
                dct_header={}
                dct_header["BranchID"]= 1 if ins_data['branch']!='AGY' else 2
                dct_header["CardCode"]= ins_data['vendor']
                dct_header["CardName"]= ins_data['vendor_name']
                dct_header["DocDate"]= datetime.strftime(ins_data['dat_purchase'],'%Y-%m-%d')
                dct_header["MYGOAL_KEY"]= ins_data['vchr_purchase_num']
                dct_header["ShowRoomID"]= ins_data['branch']
                dct_data['Header'] = [dct_header]

                if dct_freight_discount:
                    for str_discount in dct_freight_discount:
                        dct_freight= {}
                        cur.execute("select vchr_code from freight where upper(vchr_category)='SALES DISCOUNT' and vchr_tax_code='"+dct_freight_discount[str_discount]['tax_code']+"' and int_status=0")
                        rst_code=cur.fetchall()
                        dct_freight["ExpCode"]=rst_code[0]['vchr_code'] if rst_code else '-1'
                        dct_freight["LineTotal"]=(-1)*dct_freight_discount[str_discount]['amount']
                        dct_freight["TaxCode"]=str_discount
                    # dct_freight["Store"]= dct_data['Line level'][0]["Store"]
                    # dct_freight["Department"]= dct_data['Line level'][0]["Department"]
                    # dct_freight["Employees"]= dct_data['Line level'][0]["Employee"]
                    # dct_freight["Brand"]= ""
                        dct_data['Freight'].append(dct_freight)
                if not dct_data['Freight']:
                    dct_data['Freight']=[{"ExpCode":-1,"TaxCode":"","LineTotal":0.0}]
            
                url='http://13.71.18.142:8086/api/In/GRPO'
                data=json.dumps(dct_data)
                headers = {"Content-type": "application/json"}
                res_data = requests.post(url,data,headers=headers)
                cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=15")
                response = json.loads(res_data.text)
                print(response)
                print(data)
                if str(response['status']).upper() == 'SUCCESS':
                    cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=15")
                else:
                    file_object = open(str_file, 'a')
                    file_object.write(data)
                    file_object.write('\n\n')
                    file_object.write(res_data.text)
                    file_object.write('\n\n\n\n')
                    file_object.close()
                    cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=15")
            except Exception as e:
                print(str(e))
                continue
        cur.close()
        conn.close()
        return True
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))



if __name__ == '__main__':
    GRPO_sapre_part()
