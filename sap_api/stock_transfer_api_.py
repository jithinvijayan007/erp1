
import requests
from datetime import datetime
import sys
import psycopg2
import json

from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup


def stock_transfer_api(str_entry,doc_date):

    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            # conn = psycopg2.connect(host="localhost",database="pos_sap", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)

        except Exception as e:
            print(str(e))
        cur.execute("select int_document_id from sap_api_track where int_type=3 and int_status in ("+str_entry+") and dat_document::Date = '"+doc_date+"' order by int_document_id")
        tpl_lst_master_id=cur.fetchall()
        lst_st_id =[d['int_document_id'] for d in tpl_lst_master_id]
        str_file = doc_date.replace("-","")+'/STockTransferIssues.txt'
        for int_id in set(lst_st_id):
            try:
#                import pdb; pdb.set_trace()
                str_querry = """select sub1.int_qty, sub1.jsn_imei,sub1.jsn_batch,sub1.vchr_st_num,sub1.dat_ack, sub1.vchr_comments,sub1.int_key,sub1.vchr_item_code,sub1.vchr_item_name,sub1.dbl_mop,sub1.vchr_branch_code_from, sub1.vchr_loc_code_from,sub2.vchr_branch_code_to,sub2.vchr_loc_code_to,sub1.brand as brand from( select bsd.int_received as int_qty,bsd.jsn_imei as jsn_imei ,bsd.jsn_batch_no as jsn_batch,st.vchr_stktransfer_num as vchr_st_num,st.dat_acknowledge as dat_ack ,st.vchr_remarks as vchr_comments,bsm.pk_bint_id as int_key, itm.vchr_item_code as vchr_item_code,itm.vchr_name as vchr_item_name,itm.dbl_mop as dbl_mop, br1.vchr_code as vchr_branch_code_from, lm1.int_code as vchr_loc_code_from,st.pk_bint_id as int_st_id,bd.vchr_name as brand from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch_stock_details bsd on bsd.fk_transfer_details_id=ist.pk_bint_id join branch_stock_master bsm on bsm.pk_bint_id=bsd.fk_master_id join branch_stock_imei_details bsim on bsim.fk_details_id=bsd.pk_bint_id join item itm on itm.pk_bint_id = ist.fk_item_id join brands bd on bd.pk_bint_id=itm.fk_brand_id join branch br1 on br1.pk_bint_id = st.fk_from_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm1 on lm1.pk_bint_id =  br1.fk_location_master_id ) as sub1 join( select br2.vchr_code as vchr_branch_code_to, lm2.int_code as vchr_loc_code_to,st.pk_bint_id as int_st_id from ist_details ist join stock_transfer st on st.pk_bint_id = ist.fk_transfer_id join branch br2 on br2.pk_bint_id = st.fk_to_id join location_master lm2 on lm2.pk_bint_id = br2.fk_location_master_id )     as sub2 on sub2.int_st_id = sub1.int_st_id """
                str_querry  =  str_querry +" where sub1.vchr_branch_code_from !='AGY' and sub2.vchr_branch_code_to !='AGY' and sub1.int_qty > 0 and sub1.int_key = " + str(int_id) +"group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"

                str_item = "select imei_status from item where vchr_item_code='"
                cur.execute(str_querry)
                lst_stock_transfer = cur.fetchall()
                # import pdb; pdb.set_trace()
                # print(int_id)
                if not lst_stock_transfer:
                    continue

                dct_data = {}
                dct_data['Header'] = []
                dct_data['Line Level'] = []
                dct_header = {}
                for ins_data in lst_stock_transfer:
                    ins_data = dict(ins_data)

                    if not dct_header:
                        dct_header['Comments'] = ins_data['vchr_comments'][:70] if ins_data['vchr_comments'] else ''
                        dct_header['MYGOAL_KEY'] = ins_data['vchr_st_num']
                        dct_header['ShowRoomID'] = ins_data['vchr_branch_code_from']
                        dct_header['DocDate'] = datetime.strftime(ins_data['dat_ack'],'%Y-%m-%d')
                        # dct_header['DocDate'] = '2020-04-12'
                        dct_header['FromLocation'] = str(ins_data['vchr_loc_code_from'])
                        dct_header['FromShowRoom'] = str(ins_data['vchr_branch_code_from'])
                        dct_header['ToLocation'] = str(ins_data['vchr_loc_code_to'])
                        dct_header['ToShowRoom'] = str(ins_data['vchr_branch_code_to'])
                        dct_data['Header'].append(dct_header)
                    str_item_query = str_item+ins_data['vchr_item_code']+"'"
                    cur.execute(str_item_query)
                    rst_item_data = cur.fetchall()
                    #import pdb;pdb.set_trace()
                    if rst_item_data and rst_item_data[0]['imei_status']:
                        dct_line={}
                        dct_line['UoM'] = 1
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        dct_line['Dscription'] = ins_data['vchr_item_name']
                        dct_line['Quantity'] = ins_data['int_qty']
                        dct_line['MnfSerial'] = ins_data['jsn_imei']['imei'] if ins_data['jsn_imei']['imei'] else ins_data['jsn_batch']['batch']
                        #dct_line['MnfSerial'] = [str_imei.strip() for str_imei in lst_imei]
                        if len(dct_line['MnfSerial']) >= 1 and dct_line['MnfSerial'][0]:
                           dct_line['MnfSerial'] = [str_imei.strip() for str_imei in dct_line['MnfSerial']]
                        #dct_line['MnfSerial'] = [dct_line['MnfSerial'][0].strip()]
                        dct_line['MRP'] = ins_data['dbl_mop']
                        dct_line['ExpDate'] = ''
                        dct_data['Line Level'].append(dct_line)
                        #if len(dct_line['MnfSerial'])>1:
                           #print([dct_line['MnfSerial'][0]+'.'],"Imei's")
                           #import pdb;pdb.set_trace()
                    elif rst_item_data and not rst_item_data[0]['imei_status']:

                        dct_line={}
                        dct_line['UoM'] = 1
                        dct_line['ItemCode'] = ins_data['vchr_item_code']
                        dct_line['Dscription'] = ins_data['vchr_item_name']
                        dct_line['Quantity'] = ins_data['int_qty']
                        dct_line['MnfSerial'] = ins_data['jsn_batch']['batch'] if ins_data['jsn_batch']['batch'] else ins_data['jsn_imei']['imei']
                        #dct_line['MnfSerial'] = [dct_line['MnfSerial'][0].strip()]
                        if len(dct_line['MnfSerial']) >= 1 and dct_line['MnfSerial'][0]:
                           dct_line['MnfSerial'] = [str_imei.strip() for str_imei in dct_line['MnfSerial']] 
                        dct_line['MRP'] = ins_data['dbl_mop']
                        dct_line['ExpDate'] = ''
                        dct_data['Line Level'].append(dct_line)

                headers = {'Content-type': 'application/json'}
                data = json.dumps(dct_data)
                if dct_data['Header'][0].get('MYGOAL_KEY') in ['STN-IJK-0068','STN-RAM-0069']:
                    print('STN-TPVD-0128')
                    import pdb; pdb.set_trace()
                print("ID : ",int_id)
                print("Data : ",data,"\n")
                #str_log_key_data = "select txt_remarks from sap_api_track where int_type = 3 and int_status = -1 and int_document_id ="+str(int_id)+";"
                #cur.execute(str_log_key_data)
                #rst_log_key_details = cur.fetchall()
                
                #print("Error : ",rst_log_key_details[0]['txt_remarks'],"\n\n")
#                import pdb; pdb.set_trace()
                if dct_data['Header'][0]['MYGOAL_KEY']=='STN-PNR-0152':
                    import pdb; pdb.set_trace()
                    print(dct_data['Header'][0]['MYGOAL_KEY'])
                str_url = "http://13.71.18.142:8086/api/In/StockTransfers"
                res_data = requests.post(str_url,data,headers=headers)
                cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"',txt_remarks='Pushed' where int_document_id ="+str(int_id)+" and int_type=3")
                responses = json.loads(res_data.text)
                print(responses)
                if str(responses['status']).upper() == 'SUCCESS':
                    cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str(int_id)+" and int_type=3")
                else:
                    file_object = open(str_file, 'a')
                    file_object.write(data)
                    file_object.write('\n\n')
                    file_object.write(res_data.text)
                    file_object.write('\n\n\n\n')
                    file_object.close()
                    #responses.pop('message')
                    #str_error_text = json.dumps(responses)

                    if str_entry == "0":
                        cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(res_data.text).replace("\'","\"")+"' where int_document_id ="+str(int_id)+" and int_type=3")
                    else:
                        cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+str(res_data.text).replace("\'","\"")+"' where int_document_id ="+str(int_id)+" and int_type=3")

            except Exception as e:
                print(e)
                continue

        cur.close()
        conn.close()
        #file_object.close()
        return True
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))

if __name__ == '__main__':
    stock_transfer_api()
