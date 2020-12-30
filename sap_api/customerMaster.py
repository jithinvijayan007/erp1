from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import sys
def CustomerAPI(dat_cust_created):

    """
            Function to add Customer Details in POS from SAP API.
            param: dat_cust_created (Customer created date)

                URL : http://myg.tmicloud.net:85/POSOutbound.asmx/CustomerMaster?Fdate=
                SAP_API_keys : CustCode,CustName,Phone1,MailAddres,GstNo,ZipCode,CustState

            return: Success

    """
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            #conn = psycopg2.connect(host="localhost",database="pos_live", user="admin", password="tms@123")
            conn.autocommit = True
        except Exception as e:
            return 0

        cur = conn.cursor()
        url = "http://13.71.18.142:8086/api/master/customer?FDate="+ dat_cust_created
        res_data = requests.get(url)
        lst_card_code=[]
        if res_data.status_code == 200:
            dct_data = res_data.json() # String to Json
            if dct_data:
                for item in dct_data:
                    if item['CustCode'] not in lst_card_code:
                        lst_card_code.append(item['CustCode'])
                        if item['GroupName'].upper() =='DOMESTIC':
                            cur.execute(" SELECT * FROM  supplier WHERE vchr_code='"+item['CustCode']+"'")
                            ins_supplier = cur.fetchone()

                            if ins_supplier:
                                cur.execute("update supplier set is_act_del=2 WHERE vchr_code='"+item['CustCode']+"' and is_act_del=0")

                            cur.execute(" SELECT pk_bint_id FROM states WHERE vchr_code = '"+item['StateCode']+"'")
                            int_states = cur.fetchone()

                            if int_states:
                                fk_state = int_states[0]
                            else:
                                cur.execute("INSERT INTO states(vchr_code,vchr_name) VALUES('"+item['StateCode']+"','"+item['CustState']+"') RETURNING pk_bint_id")
                                int_states = cur.fetchone()
                                if int_states:
                                    fk_state = int_states[0]
                            is_act_del= 0 if item.get('Phone2')=='Y' else 1
                            int_credit_days=int(item['CreditDays'].split("Days")[0].split(',')[1])+int(item['CreditDays'].split("Month")[0])*30
                            if item.get('Address2'):
                                print('Address 2 exists')
                            cur.execute("INSERT INTO supplier(vchr_name,vchr_gstin,vchr_code,bint_credit_limit,int_credit_days,is_act_del) VALUES('"+item['CustName'][0:50]+"','"+ (item['GstNo'] or '') +"','"+str(item['CustCode'])+"',"+str(item['CreditLine'])+","+str(int_credit_days)+","+str(is_act_del)+") RETURNING pk_bint_id")
                            ins_supp = cur.fetchone()
                            if ins_supp:
                                fk_supplier=ins_supp[0]
                                Phone2=None
                                if item['CustMobile1']:
                                    if '/' in item['CustMobile1']:
                                        phone=item['CustMobile1'].split('/')
                                        Phone1=phone[0].replace(" ","")
                                        Phone2=phone[1].replace(" ","")
                                    else:

                                        Phone1=item['CustMobile1'].replace(" ","")

                                else:
                                    Phone1=item['CustMobile1'] or "0"
                                if not Phone2:
                                    if item.get('CustMobile2'):
                                        Phone2=item.get('CustMobile2').replace(" ","")
                                    else:
                                        Phone2=item.get('CustMobile2') or "0"


                                int_zip=item['ZipCode'] or 'NULL'
                                cur.execute("INSERT INTO Address_Supplier(vchr_email,int_pin_code,vchr_address,bint_phone_no,fk_states_id,fk_supplier_id) VALUES('"+str(item['CustEmail']) +"',"+str(int_zip)+",'"+str(item['Street'])+"',"+str(Phone1)+","+str(fk_state)+","+str(fk_supplier)+") RETURNING pk_bint_id")
                                if item['CardFName']:
                                    # if " " in item['CardFName']:
                                    #
                                    #     contact_name=item['CardFName'].split(' ')[0]
                                    # else:
                                        contact_name=item['CardFName']
                                else:
                                    if item['CustName']:
                                        if ' ' in item['CustName']:


                                            contact_name=item['CustName'].split(' ')[0]
                                        else:
                                            contact_name=item['CustName']
                                cur.execute("INSERT INTO Contact_Person_Supplier(vchr_name,bint_mobile_no,bint_mobile_no2,fk_supplier_id) VALUES('"+str(contact_name)[0:30] +"',"+str(Phone1)+","+str(Phone2)+","+str(fk_supplier)+") RETURNING pk_bint_id")
                        elif item['GroupName'].upper() in ['FINANCIAR']:
                            cur.execute(" SELECT * FROM  financiers WHERE vchr_code='"+item['CustCode']+"'")
                            ins_financier = cur.fetchone()

                            if ins_financier:
                                cur.execute("update financiers set bln_active=false WHERE vchr_code='"+item['CustCode']+"'")
                            vchr_name = item['CustName']
                            vchr_code = item['CustCode']
                            cur.execute("INSERT INTO financiers(vchr_code,vchr_name,bln_active) VALUES('"+vchr_code+"','"+vchr_name+"',true) RETURNING pk_bint_id")
                            ins_financier = cur.fetchone()
                            if not ins_financier:
                                print('data not inserted')
                        elif item['GroupName'].upper() in ['CUSTOMERS','CREDITCUSTOMER','CORPORATECUSTOMER','SEZ']:
                            try:
                                # import pdb;pdb.set_trace()
                                cust_mobile = item['CustMobile1'].replace(" ","") if item.get('CustMobile1') else 0
                                try:
                                    int(cust_mobile)
                                except Exception as e:
                                    continue
                                if cust_mobile and 'E' not in cust_mobile and '.' not in cust_mobile:
                                    cur.execute(" SELECT dbl_credit_limit,dbl_credit_balance,pk_bint_id FROM  customer_details WHERE vchr_code='"+item['CustCode']+"'")
                                    ins_customer = cur.fetchone()
                                    int_cust_type = 'null'
                                    int_cust_type = 4
                                    if item['GroupName'].upper() == 'CORPORATECUSTOMER':
                                        int_cust_type = 1
                                    elif item['GroupName'].upper() == 'CREDITCUSTOMER':
                                        int_cust_type = 2
                                    elif item['GroupName'].upper() == 'SEZ':
                                        int_cust_type = 3
                                    if ins_customer:
                                        if item['ZipCode']:
                                            cur.execute(" SELECT pk_bint_id FROM  location WHERE vchr_pin_code='"+item['ZipCode']+"'")
                                            int_location = cur.fetchone()
                                            if int_location:
                                                print(int_location)
                                                fk_location = int_location[0]
                                            else:
                                                cur.execute("INSERT INTO location(vchr_pin_code) VALUES('"+item['ZipCode']+"') RETURNING pk_bint_id")
                                                int_location = cur.fetchone()
                                                if int_location:
                                                    print(int_location)
                                                    fk_location = int_location[0]
                                        else:
                                            fk_location='null'
                                        # import pdb; pdb.set_trace()
                                        cur.execute(" SELECT pk_bint_id FROM states WHERE vchr_code ='"+item['StateCode']+"'")
                                        int_states = cur.fetchone()

                                        if int_states:
                                            print(int_states)
                                            fk_state = int_states[0]
                                        else:
                                            cur.execute("INSERT INTO states(vchr_code,vchr_name) VALUES('"+item['StateCode']+"','"+item['CustState']+"') RETURNING pk_bint_id")
                                            int_states = cur.fetchone()
                                            if int_states:
                                                print(int_states)
                                                fk_state = int_states[0]
                                        vchr_gst = "'"+item.get('GstNo')+"'" if item.get('GstNo') else 'null'
                                        vchr_email = "'"+item.get('CustEmail')+"'" if item.get('CustEmail') else 'null'
                                        CustAddress = "'"+item.get('CustAddress')+"'" if item.get('CustAddress') else 'null'
                                        print(ins_customer)
                                        dbl_credit_balance = ins_customer[1]
                                        str_limit_change = item.get('CreditLine',0.0) - ins_customer[0]
                                        dbl_credit_balance = dbl_credit_balance + str_limit_change
                                        cur.execute("update customer_details set vchr_name='"+item['CustName']+"',txt_address="+CustAddress+",vchr_gst_no="+vchr_gst+",fk_location_id="+str(fk_location)+",fk_state_id="+str(fk_state)+",int_cust_type="+str(int_cust_type)+",int_mobile="+str(cust_mobile)+",dbl_credit_limit="+str(item['CreditLine'])+",dbl_credit_balance="+str(dbl_credit_balance)+" where vchr_code ='"+item['CustCode']+"'")
                                        cur.execute("select vchr_name,txt_address,vchr_gst_no,fk_location_id,fk_state_id,int_cust_type,int_mobile,dbl_purchase_amount from sales_customer_details where vchr_code='"+item['CustCode']+"' order by 1 desc limit 1")
                                        ins_sale_cust=cur.fetchall()[0]
                                        if ins_sale_cust[0]!=item['CustName'] or ins_sale_cust[1]!=CustAddress or ins_sale_cust[2]!=vchr_gst or ins_sale_cust[3]!=fk_location or ins_sale_cust[4]!=fk_state or ins_sale_cust[5]!=int_cust_type or ins_sale_cust[6]!=cust_mobile:
                                            cur.execute("INSERT INTO sales_customer_details(vchr_name,fk_customer_id,txt_address,vchr_gst_no,fk_location_id,fk_state_id,vchr_code,int_cust_type,int_mobile,dbl_purchase_amount) VALUES('"+item['CustName']+"',"+str(ins_customer[2])+","+CustAddress+","+vchr_gst+","+str(fk_location)+","+str(fk_state)+",'"+item['CustCode']+"',"+str(int_cust_type)+","+str(cust_mobile)+",0) RETURNING pk_bint_id")
                                        # continue
                                        # cur.execute("update customer_details set int_cust_type ="+str(int_cust_type)+" WHERE vchr_code='"+item['CustCode']+"'")
                                    else:

                                        if item['ZipCode']:
                                            cur.execute(" SELECT pk_bint_id FROM  location WHERE vchr_pin_code='"+item['ZipCode']+"'")
                                            int_location = cur.fetchone()
                                            if int_location:
                                                fk_location = int_location[0]
                                            else:

                                                cur.execute("INSERT INTO location(vchr_pin_code) VALUES('"+item['ZipCode']+"') RETURNING pk_bint_id")
                                                int_location = cur.fetchone()
                                                if int_location:
                                                    fk_location = int_location[0]
                                        else:
                                            fk_location='null'
                                        cur.execute(" SELECT pk_bint_id FROM states WHERE vchr_code ='"+item['StateCode']+"'")
                                        int_states = cur.fetchone()

                                        if int_states:
                                            fk_state = int_states[0]
                                        else:
                                            cur.execute("INSERT INTO states(vchr_code,vchr_name) VALUES('"+item['StateCode']+"','"+item['CustState']+"') RETURNING pk_bint_id")
                                            int_states = cur.fetchone()
                                            if int_states:
                                                fk_state = int_states[0]
                                        vchr_email = "'"+item.get('CustEmail')+"'" if item.get('CustEmail') else 'null'
                                        CustAddress = "'"+item.get('CustAddress')+"'" if item.get('CustAddress') else 'null'
                                        vchr_gst = "'"+item.get('GstNo')+"'" if item.get('GstNo') else 'null'
                                        cur.execute("INSERT INTO customer_details(vchr_name,txt_address,vchr_gst_no,fk_location_id,fk_state_id,vchr_code,int_cust_type,int_mobile,dbl_credit_limit,dbl_credit_balance,dbl_purchase_amount) VALUES('"+item['CustName']+"',"+CustAddress+","+vchr_gst+","+str(fk_location)+","+str(fk_state)+",'"+item['CustCode']+"',"+str(int_cust_type)+","+str(cust_mobile)+","+str(item['CreditLine'])+","+str(item['CreditLine'])+",0) RETURNING pk_bint_id")
                                        ins_cust = cur.fetchone()
                                        if ins_cust:
                                            cur.execute("INSERT INTO sales_customer_details(vchr_name,fk_customer_id,txt_address,vchr_gst_no,fk_location_id,fk_state_id,vchr_code,int_cust_type,int_mobile,dbl_purchase_amount) VALUES('"+item['CustName']+"',"+str(ins_cust[0])+","+CustAddress+","+vchr_gst+","+str(fk_location)+","+str(fk_state)+",'"+item['CustCode']+"',"+str(int_cust_type)+","+str(cust_mobile)+",0) RETURNING pk_bint_id")
                            except Exception as e:
                                #import pdb;pdb.set_trace()
                                print(item)            # continue


        cur.close()
        conn.close()
        return 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()

        cur.close()
        conn.close()
        print(e,str(exc_tb.tb_lineno))
        return 0

if __name__ == '__main__':
    str_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    #str_date = '2020-06-01'
    if len(sys.argv) >1:
        str_date = sys.argv[1]
    CustomerAPI(str_date)
