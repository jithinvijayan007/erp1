from django.shortcuts import render
from django.contrib.auth.models import User as AuthUser
from POS.dftosql import Savedftosql
from sqlalchemy import and_,func ,cast,Date,case, literal_column,or_,MetaData,desc
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
from aldjemy.core import get_engine
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from POS import ins_logger
from datetime import datetime
from rest_framework.response import Response
import sys, os

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
# metadata = MetaData()
# metadata.reflect(bind=engine)
# Connection = sessionmaker()
# Connection.configure(bind=engine)
engine = get_engine()
def Session():
    _Session = sessionmaker(bind = engine)
    return _Session()

# Create your views here.

class ListCraditDebit(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            dat_to = request.data.get("datTo") if request.data.get("datTo") else None
            dat_from = request.data.get("datFrom") if request.data.get("datFrom") else None
            lst_branch = request.data.get("lstBanchId")
            str_type = request.data.get("strType")
            conn = engine.connect()
            str_query = "select cus_d.vchr_name, cus_d.int_mobile, slm.dat_invoice,slm.vchr_invoice_num,(CASE WHEN pymtd.int_fop = 2 THEN 'Debit Card' WHEN pymtd.int_fop = 3 THEN 'Credit Card' END) as str_type,bnk.vchr_name as b_name,pymtd.vchr_reff_number, pymtd.dbl_receved_amt,br.vchr_name as br_name,pymtd.vchr_finance_schema from payment_details as pymtd LEFT JOIN sales_master as slm ON pymtd.fk_sales_master_id = slm.pk_bint_id LEFT JOIN sales_customer_details as cus_d ON cus_d.pk_bint_id = slm.fk_customer_id LEFT JOIN bank as bnk ON bnk.pk_bint_id = pymtd.fk_bank_id LEFT JOIN branch as br ON slm.fk_branch_id = br.pk_bint_id WHERE pymtd.int_fop in (2,3)"
            if dat_to:
                str_query +=" AND slm.dat_invoice <= '"+str(dat_to)+"'"
            if dat_from:
                str_query += " AND slm.dat_invoice >= '"+str(dat_from)+"'"
            if request.data.get("strType") == 'credit':
                str_query += " AND pymtd.int_fop = 3"
            if request.data.get("strType") == 'debit':
                str_query += " AND pymtd.int_fop = 2"
            if request.data.get("lstBanchId"):
                str_query += " AND slm.fk_branch_id in ("+str(lst_branch)[1:-1] +")"
            str_query += ' ORDER BY slm.dat_invoice DESC, pymtd.pk_bint_id DESC'
            rst_data = conn.execute(str_query).fetchall()

            lst_data = []
            for data in rst_data:
                dct_data = {}
                if data.dat_invoice:
                    dct_data['dateInvoice'] =  datetime.strftime(data.dat_invoice,'%d-%m-%Y')
                dct_data['strInvoiceNo'] = data.vchr_invoice_num
                dct_data['strCusName'] = data.vchr_name
                dct_data['strCusMob'] = data.int_mobile
                dct_data['strType'] = data.str_type
                dct_data['strBank'] = data.b_name
                dct_data['intAmt'] = data.dbl_receved_amt
                dct_data['strEmi'] = data.vchr_finance_schema
                dct_data['intRefNo'] = data.vchr_reff_number
                dct_data['strBranch'] = data.br_name
                lst_data.append(dct_data)
            return Response({'status':1,'data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','reason':str(e), 'message':"Something went wrong"})
