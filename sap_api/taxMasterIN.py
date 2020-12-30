import requests
import json
import urllib.request
import psycopg2
import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from bs4 import BeautifulSoup

from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os
from sqlalchemy import create_engine
from django.http import JsonResponse

def update_spec():
    try:
        conn = None
        conn = psycopg2.connect(host="localhost",database="pos", user="admin", password="uDS$CJ8j")
        conn.autocommit = True
        cur = conn.cursor()

    except Exception as e:
        return JsonResponse({'status':'failed','reason':'cannot connect to database'})
    try:
        xml_response_data = requests.get('http://myglive.tmicloud.net:8084/api/master/TaxCode')
        if xml_response_data.status_code == 200:
            lst_response_data = xml_response_data.json()
            # import pdb;pdb.set_trace()
            for ins_tax in lst_response_data:
                str_taxmaster_query = "select * from tax_master where vchr_code ='"+ins_tax['Code']+"';"
                cur.execute(str_taxmaster_query)
                rst_existing_tax = cur.fetchall()
                if not rst_existing_tax:
                    cur.execute("insert into tax_master(vchr_name,bln_active,vchr_code,dbl_rate) values('"+ins_tax['Name'].split('%')[0]+"',true,'"+ins_tax['Code']+"',"+str(ins_tax['Rate'])+");")
                else:
                    cur.execute("update tax_master set vchr_name='"+ins_tax['Name'].split('%')[0]+"',bln_active=true,dbl_rate ="+str(ins_tax['Rate'])+" where vchr_code ='"+ins_tax['Code']+"';")
        print('success')
        cur.close()
        conn.close()
    except Exception as e:
        cur.close()
        conn.close()
        print(e)
        return 0


if __name__ == '__main__':
    update_spec()
