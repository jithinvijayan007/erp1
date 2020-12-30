from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import sys
def VendorAPI(dat_cust_created):

    """
            Function to add Vendor Details in POS from SAP API.
            param: dat_cust_created (Vendor created date)

                URL : http://myg.tmicloud.net:85/POSOutbound.asmx/Vendor?Fdate=
                SAP_API_keys : CardCode,CardName,Phone1,MailAddres,GstNo,ZipCode,State

            return: Success

    """
    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_pos_live2", user="admin", password="uDS$CJ8j")
            # conn = psycopg2.connect(host="localhost",database="mydb", user="admin", password="tms@123")
            conn.autocommit = True
        except Exception as e:
            return 0

        cur = conn.cursor()
#        import pdb;pdb.set_trace()
        #url = "http://myglive.tmicloud.net:8084/api/master/Vendor?FDate="+ dat_cust_created
        url = "http://13.71.18.142:8086/api/master/Vendor?FDate=" + dat_cust_created
        res_data = requests.get(url)
        lst_card_code=['C04894','V0924','V01137','V0922','V01080','V02848']
        if res_data.status_code == 200:
            dct_data = res_data.json() # String to Json
            if dct_data:
                for item in dct_data:
                    if item['CardCode'] not in lst_card_code:
                        lst_card_code.append(item['CardCode'])
                        if item['BPType'].upper() =='SUPPLIER':
                            cur.execute(" SELECT * FROM  supplier WHERE vchr_code='"+item['CardCode']+"'")
                            ins_supplier = cur.fetchone()
                            item['StateCode'] = item['StateCode'] if item['StateCode'] else 'KL'
                            cur.execute(" SELECT pk_bint_id FROM states WHERE vchr_code = '"+item['StateCode']+"'")
                            int_states = cur.fetchone()
                            if int_states:
                                fk_state = int_states[0]
                            else:
                                cur.execute("INSERT INTO states(vchr_code,vchr_name) VALUES('"+item['StateCode']+"','"+item['State']+"') RETURNING pk_bint_id")
                                int_states = cur.fetchone()
                                if int_states:
                                    fk_state = int_states[0]

                            if ins_supplier:
                                cur.execute("update address_supplier set fk_states_id="+str(fk_state)+" WHERE fk_supplier_id="+str(ins_supplier[0]))
                                continue
                                #cur.execute("update supplier set is_act_del=2 WHERE vchr_code='"+item['CardCode']+"' and is_act_del=0")

#                            cur.execute(" SELECT pk_bint_id FROM states WHERE vchr_code = '"+item['StateCode']+"'")
 #                           int_states = cur.fetchone()

#                            if int_states:
 #                               fk_state = int_states[0]
  #                          else:
   #                             cur.execute("INSERT INTO states(vchr_code,vchr_name) VALUES('"+item['StateCode']+"','"+item['State']+"') RETURNING pk_bint_id")
                                int_states = cur.fetchone()
                                if int_states:
                                    fk_state = int_states[0]
                            is_act_del= 0 if item.get('validFor')=='Y' else 1
                            int_credit_days=int(item['CreditDays'].split("Days")[0].split(',')[1])+int(item['CreditDays'].split("Month")[0])*30
                            if item.get('Address2'):
                                print('Address 2 exists')
                            #import pdb;pdb.set_trace()
                            cur.execute("INSERT INTO supplier(vchr_name,vchr_gstin,vchr_code,bint_credit_limit,int_credit_days,is_act_del) VALUES('"+item['CardName'][0:50]+"','"+ (item['GSTRegnNo'] or '') +"','"+str(item['CardCode'])+"',"+str(item['CreditLine'])+","+str(int_credit_days)+","+str(is_act_del)+") RETURNING pk_bint_id")
                            ins_supp = cur.fetchone()
                            if ins_supp:
                                fk_supplier=ins_supp[0]
                                Phone2=None
                                if item['Phone1']:
                                    if '-' in item['Phone1']:
                                        phone=item['Phone1'].split('-')
                                        Phone1=phone[0].replace(" ","")
                                        Phone2=phone[1].replace(" ","")
                                    else:

                                        Phone1=item['Phone1'].replace(" ","")

                                else:
                                    Phone1=item['Phone1'] or "0"
                                if not Phone2:
                                    if item.get('Phone2'):
                                        Phone2=item.get('Phone2').replace(" ","")
                                    else:
                                        Phone2=item.get('Phone2') or "0"

                                Email = "'"+item['E_Mail']+"'" if item.get('E_Mail') else 'null'
                                int_zip=item['ZipCode'].replace(" ", "") if item['ZipCode'] else 'null'
                                cur.execute("INSERT INTO Address_Supplier(vchr_email,int_pin_code,vchr_address,bint_phone_no,fk_states_id,fk_supplier_id) VALUES("+str(Email) +","+str(int_zip)+",'"+str(item['Street'])+"',"+str(Phone1)+","+str(fk_state)+","+str(fk_supplier)+") RETURNING pk_bint_id")
                                if item['CardFName']:
                                    # if " " in item['CardFName']:
                                    #
                                    #     contact_name=item['CardFName'].split(' ')[0]
                                    # else:
                                        contact_name=item['CardFName']
                                else:
                                    if item['CardName']:
                                        if ' ' in item['CardName']:


                                            contact_name=item['CardName'].split(' ')[0]
                                        else:
                                            contact_name=item['CardName']
                                cur.execute("INSERT INTO Contact_Person_Supplier(vchr_name,bint_mobile_no,bint_mobile_no2,fk_supplier_id) VALUES('"+str(contact_name)[0:30] +"',"+str(Phone1)+","+str(Phone2)+","+str(fk_supplier)+") RETURNING pk_bint_id")
                                print(item['CardCode'])
        cur.close()
        conn.close()
        return 1
    except Exception as e:
        import pdb;pdb.set_trace()
        exc_type, exc_obj, exc_tb = sys.exc_info()

        cur.close()
        conn.close()
        print(e,str(exc_tb.tb_lineno))
        return 0

if __name__ == '__main__':
    str_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
    if len(sys.argv) >1:
        str_date = sys.argv[1]
    VendorAPI(str_date)
