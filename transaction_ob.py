import pandas as pd
import psycopg2
from datetime import datetime
import random
import json
import time
def transactionfromexcel():
    try:
        time_start = time.time()
        try:
            # import pdb; pdb.set_trace()
            conn = psycopg2.connect(host="localhost",database="pos3", user="admin", password="tms@123")
            cur = conn.cursor()
            conn.autocommit = True
            df = pd.read_excel("CUSTOMER OB UPDATED.xlsx",header=0,sheet_name="OB PREPARATION")
        except Exception as e:
            return 'cannot read excel'
        lst_no_customer = []
        lst_no_branch = []
        lst_added = []
        no_branch = 0
        cur.execute("select id from auth_user where upper(username) = 'TDXADMIN';")
        int_created_id = cur.fetchone()[0]
        dat_created = '2020-07-01'
        for ind,row in df.iterrows():
            vchr_customer_code = row['Customer code']
            vchr_customer_name = row['Customer name']
            vchr_mobile_num = row['mobile no.']
            vchr_branch_code = row['BRANCH CODE']
            dbl_debit = row['DEBIT']
            dbl_credit = row['CREDIT']

            if str(dbl_debit).upper() == "NAN":
                dbl_debit = 0
            if str(dbl_credit).upper() == "NAN":
                dbl_credit = 0

            # cur.execute("select pk_bint_id,vchr_code from customer_details where upper(vchr_code) = '"+vchr_customer_code.upper()+"';")
            cur.execute("select pk_bint_id,vchr_code from customer_details where int_mobile = '"+str(vchr_mobile_num)+"' and int_cust_type = 4;")
            ins_customer = cur.fetchone()
            if not ins_customer:
                lst_no_customer.append(vchr_customer_code)
            else:
                int_customer_id = ins_customer[0]
                cur.execute("select pk_bint_id from branch where upper(vchr_code) = '"+vchr_branch_code.upper()+"';")
                ins_branch = cur.fetchone()
                if ins_branch:
                    int_branch_id = ins_branch[0]
                    # import pdb; pdb.set_trace()
                    cur.execute("insert into transaction(dat_created,int_accounts_id,int_account_type,dbl_debit,dbl_credit,fk_created_id,vchr_status,fk_financialyear_id,int_type,fk_branch_id) values('"+dat_created+"',"+str(int_customer_id)+",1,"+str(dbl_debit)+","+str(dbl_credit)+","+str(int_created_id)+",'NEW',1,1,"+str(int_branch_id)+");")
                    lst_added.append(vchr_customer_code)
                else:
                    no_branch += 1
                    if vchr_branch_code not in lst_no_branch:
                        lst_no_branch.append(vchr_branch_code)

        print('added - ')
        print(len(lst_added))
        print('no Customer - ')
        print(len(lst_no_customer))
        print('no branch')
        print(no_branch)
        print("success")


        if lst_no_customer:
            dct_excel = {}
            dct_excel['no Customer'] = lst_no_customer
            # create panda model of table data
            df = pd.DataFrame(dct_excel ,index = list(range(1,len(dct_excel['no Customer'])+1)))
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            excel_file = 'transaction_entry_no_customer.xlsx'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df.to_excel(writer,startrow=0, startcol= 0)
            workbook = writer.book
            writer.save()

        if lst_no_branch:
            dct_excel = {}
            dct_excel['no branch'] = lst_no_branch
            # create panda model of table data
            df = pd.DataFrame(dct_excel ,index = list(range(1,len(dct_excel['no branch'])+1)))
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            excel_file = 'transaction_entry_no_branch.xlsx'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df.to_excel(writer,startrow=0, startcol= 0)
            workbook = writer.book
            writer.save()

        print("success")
    except Exception as e:
        import pdb; pdb.set_trace()
        raise

if __name__ == '__main__':
    transactionfromexcel()
