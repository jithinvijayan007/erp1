from datetime import datetime
import requests
# from bs4 import BeautifulSoup
import json
import psycopg2
import sys
import pandas as pd
def oldInsurance():

    try:
        try:
            conn = None
            conn = psycopg2.connect(host="localhost",database="backtobi", user="admin", password="tms@123")
            conn.autocommit = True
            cur = conn.cursor()
        except Exception as e:
            return e
        # int_type :1-gdp,2-gdew
        int_type = 1
        lst_gdp_without_gdw = []
        pd_data = pd.read_excel('GDEW.xlsx')
        pd_data['Date'] = pd.to_datetime(pd_data['Date']).dt.strftime('%Y-%m-%d')
        pd_data['IMEI Number'] = pd_data['IMEI Number'].astype(str).str.strip("[],'")
        # import pdb; pdb.set_trace()
        # pd_data['IMEI Number'] = pd_data['IMEI Number'].str.strip()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>FILE LOADED<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print("TOTAL DATA : ", len (pd_data))
        for row,col in pd_data.iterrows():
            if col.get('GDP Pack Value'):


                str_imei = col['IMEI Number']
                flt_amount = col['Product Value']
                flt_gdp = col['GDP Pack Value']
                dat_gdp = col['Date']



                cur.execute("select * from old_insurance where vchr_imei = '"+str(col['IMEI Number'])+"'")

                lst_existing_data = cur.fetchall()
                if lst_existing_data:
                    #code to update existing data if gdp for a imei is already present in the table

                    qry_value_data = "dbl_amount = "+str(flt_amount) +" , dat_gdp = '"+ str(dat_gdp) +"' , dbl_gdp = " +str(flt_gdp)
                #
                    cur.execute("update old_insurance set "+qry_value_data+ " where vchr_imei = '"+str(col['IMEI Number'])+"'")

                else:

                    qry_vaue_data = str((str(str_imei),flt_amount,flt_gdp,dat_gdp))

                    cur.execute("insert into old_insurance (vchr_imei,dbl_amount,dbl_gdp,dat_gdp) values "+qry_vaue_data)

            elif col.get('GDEW Pack Value'):

                cur.execute("select * from old_insurance where dat_gdp is not null and vchr_imei = '"+str(col['IMEI Number'])+"'")
                lst_existing_data_gdp = cur.fetchall()
                if lst_existing_data_gdp:
                    #code to update existing data

                    str_imei = col['IMEI Number']
                    flt_amount = col['Product Value']
                    flt_gdew = col['GDEW Pack Value']
                    dat_gdew = col['Date']
                    # dat_gdew ='2020-09-20'

                    qry_vaue_data = "dat_gdew = '"+ str(dat_gdew) +"',dbl_gdew = " +str(flt_gdew)
                    str_querry = "update old_insurance set "+ qry_vaue_data  +"where dat_gdp is not null and vchr_imei = '"+str(col['IMEI Number'])+"'"



                    cur.execute(str_querry)
                else:

                    lst_gdp_without_gdw.append(col['IMEI Number'])

        # # if lst_gdp_without_gdw:
        #     print("gdew not inserted due to missing of gdp ,IMEI es:",lst_gdp_without_gdw)
    except Exception as e:
        # import pdb; pdb.set_trace()
        return 0

oldInsurance()
