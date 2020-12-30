import sys
import psycopg2
import requests
import json
from datetime import datetime
import os
from bs4 import BeautifulSoup
from psycopg2.extras import RealDictCursor

def expense_to_sap(str_entry,doc_date):
    try:
        try:
            conn = None
            # conn = psycopg2.connect(host="localhost",database="pos_sap", user="admin", password="uDS$CJ8j")
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            conn.autocommit = True
            cur = conn.cursor(cursor_factory = RealDictCursor)
        except Exception as e:
            raise
        lst_expense = []
        str_expense_query = "SELECT array_agg(int_document_id) as lst_id from sap_api_track where int_status in ("+str_entry+") and int_type=7 and dat_document::Date = '"+doc_date+"'"
        cur.execute(str_expense_query)
        rst_expense_id = cur.fetchall()
        str_account_code = "select vchr_acc_code from chart_of_accounts coa join accounts_map acm on coa.pk_bint_id = acm.fk_coa_id where acm.int_status=0 and acm.fk_branch_id {} and acm.vchr_category = '{}';"
        dct_acc_code = {'contra_common':'101010101010','contra_ang':'101010101013','incentive_common':'701160101002'}
        if rst_expense_id and rst_expense_id[0]['lst_id']:
            str_file = doc_date.replace("-","")+'/ExpenseIssues.txt'
            lst_expense = rst_expense_id[0]['lst_id']

            for str_id in lst_expense:
                try:
                    str_id= str(str_id)
                    # import pdb; pdb.set_trace()
                    str_expense = "select p.pk_bint_id as exp_id,p.vchr_doc_num as expn_no,p.dat_payment as expn_date,p.vchr_remarks as expn_remark,case when int_fop=1 then 'Cash' else 'Transfer' end as expn_mode,p.dbl_amount expn_amount,br.vchr_code as showroom_code,br.pk_bint_id as sh_id,lm.int_code as loc,coa.vchr_acc_code as acc_code,coa.vchr_acc_name as acc_name, au.username as emp_code from payment p join branch br on br.pk_bint_id=p.fk_branch_id join location_master lm on lm.pk_bint_id=br.fk_location_master_id join accounts_map am on am.pk_bint_id=p.fk_accounts_map_id join auth_user au on au.id=p.fk_created_id  join chart_of_accounts coa on coa.pk_bint_id=am.fk_coa_id where p.pk_bint_id="+str_id

                    # str_expense = "select p.pk_bint_id as exp_id,p.vchr_doc_num as expn_no,p.dat_payment as expn_date,p.vchr_remarks as expn_remark,case when int_fop=1 then 'Cash' else 'Transfer' end as expn_mode,p.dbl_amount expn_amount,br.vchr_code as showroom_code,br.pk_bint_id as sh_id,lm.int_code as loc,coa.vchr_acc_code as acc_code,coa.vchr_acc_name as acc_name,au.username as emp_code from payment p join branch br on br.pk_bint_id=p.fk_branch_id join auth_user au on au.id=p.fk_created_id join location_master lm on lm.pk_bint_id=br.fk_location_master_id full outer join accounts_map am on am.pk_bint_id=p.fk_accounts_map_id full outer join chart_of_accounts coa on coa.pk_bint_id=am.fk_coa_id where p.pk_bint_id = "+str_id
                    cur.execute(str_expense)
                    rst_expense = cur.fetchall()
                    # import pdb; pdb.set_trace()
                    if rst_expense:
                        dct_data={}
                        dct_data['Header'] =[]
                        dct_data["Line Level"]=[]
                        dct_data["Payment Level"]=[]
                        dct_header = {}
                        for ins_data in rst_expense:
                            ins_data = dict(ins_data)
                            if not dct_header:
                                dct_header["ShowRoomID"]=ins_data['showroom_code']
                                dct_header["BranchID"]= 1 if  dct_header['ShowRoomID'] !='AGY' else 2
                                dct_header["DocDate"]= datetime.strftime(ins_data['expn_date'],'%Y-%m-%d')
                                # dct_header["DocDate"]= '2020-04-12'
                                dct_header["MYGOAL_KEY"]=ins_data['expn_no']
                                dct_data['Header'].append(dct_header)
                            dct_line_data={}
                            dct_line_data['AcctCode'] = ins_data['acc_code']
                            dct_line_data['AcctName'] = ins_data['acc_name']
                            dct_line_data['CardName'] = 'RINSHADP' #ins_data['acc_name']
                            dct_line_data['Reference'] = ins_data['exp_id']
                            dct_line_data['Dscription'] = ins_data['expn_remark'][:50]
                            dct_line_data['Currency'] = 'INR'
                            dct_line_data['Amount'] = ins_data['expn_amount']
                            dct_line_data['Remarks'] = ins_data['expn_remark'][:50]
                            dct_line_data['LocCode'] = ins_data['loc']
                            dct_line_data['Store']=ins_data['showroom_code']
                            dct_line_data['Department']="SAL"
                            dct_line_data['Brand']=""
                            dct_line_data['Employee']="" # ins_data['emp_code'][5:]
                            dct_data["Line Level"].append(dct_line_data)
                            dct_payment={}
                            if ins_data['expn_mode'].upper() == 'CASH':
                                str_acc_type = 'CASH A/C'
                                str_branch= "="+str(ins_data['sh_id'])
                                cur.execute(str_account_code.format(str_branch,str_acc_type))
                                rst_acc = cur.fetchall()
                                dct_payment["AcctCode"] = ""
                                if rst_acc:
                                    dct_payment['AcctCode'] = rst_acc[0]['vchr_acc_code']
                            else:
                                if dct_line_data['Store']=='AGY':
                                    dct_payment['AcctCode'] = '101010101009'
                                else:
                                    dct_payment['AcctCode'] = '201000201001'
                                str_acc_type = 'TRANSFER'
                                str_branch='is null'
                            dct_payment["PaymentMode"]= ins_data['expn_mode']
                            dct_payment["BankName"] = ""
                            # dct_payment["AcctCode"] = ins_data['acc_code']
                            dct_payment["Amount"] = ins_data['expn_amount']
                            dct_payment["TranId"] = -1
                            dct_payment["ChequeNum"] = -1
                            dct_payment["TransferDate"] = datetime.strftime(ins_data['expn_date'],'%Y-%m-%d')
                            dct_data["Payment Level"].append(dct_payment)

                        # url = 'http://myglive.tmicloud.net:8084/api/In/Expenses'
                        data = json.dumps(dct_data)
                        print("ID : ",str_id)
                        print("Data : ",data)


                        # str_log_key_data = "select txt_remarks from sap_api_track where int_type = 7 and int_status = -1 and int_document_id ="+str(int_id)+";"
                        # cur.execute(str_log_key_data)
                        # rst_log_key_details = cur.fetchall()
                        # print("Error : ",rst_log_key_details)
                        # import pdb; pdb.set_trace()
                        url = 'http://13.71.18.142:8086/api/In/Expenses'
                        headers = {"Content-type": "application/json"}
                        try:
                            res_data = requests.post(url,data,headers=headers)
                            cur.execute("update sap_api_track set int_status=1,dat_push='"+str(datetime.now())+"' where int_document_id ="+str_id+" and int_type=7")
                            response = json.loads(res_data.text)
                            print(response)
                            if response and str(response['status']).upper() == 'SUCCESS':
                                cur.execute("update sap_api_track set int_status=2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=7")
                            else:
                                file_object = open(str_file, 'a')
                                file_object.write(data)
                                file_object.write('\n\n')
                                file_object.write(res_data.text)
                                file_object.write('\n\n\n\n')
                                file_object.close()
                                if str_entry == '0':
                                    cur.execute("update sap_api_track set int_status=-1,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=7")
                                else:
                                    cur.execute("update sap_api_track set int_status=-2,dat_push='"+str(datetime.now())+"',txt_remarks='"+res_data.text+"' where int_document_id ="+str_id+" and int_type=7")

                        except Exception as e:
                            raise

                except Exception as e:
                    print(e)
                    continue
        cur.close()
        conn.close()
        return True
    except Exception as e:
        cur.close()
        conn.close()
        print(str(e))

if __name__=='__main__':
    expense_to_sap()
