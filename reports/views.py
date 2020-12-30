from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from sqlalchemy.orm import sessionmaker
from django.http import JsonResponse
from rest_framework.response import Response
from django.db.models import Q
from collections import OrderedDict
from datetime import datetime,time

from branch_stock.models import BranchStockMaster,BranchStockDetails,BranchStockImeiDetails
from internal_stock.models import StockRequest,IsrDetails,StockTransfer,IstDetails,TransferHistory,TransferModeDetails,StockTransferImeiDetails,\
PurchaseRequest,PurchaseRequestDetails
from item_category.models import ItemCategory,TaxMaster,Item
from item_group.models import ItemGroup
from branch.models import Branch
from brands.models import Brands
from products.models import Products,Specifications
from django.db.models import F
from django.db.models.functions import Upper
from purchase.models import GrnMaster,GrnDetails
from aldjemy.core import get_engine
from datetime import datetime,timedelta,date
from customer.models import CustomerDetails,SalesCustomerDetails
from django.contrib.postgres.fields.jsonb import KeyTransform
from global_methods import get_user_privileges,get_price_perm
import pandas as pd
from django.conf import settings
import copy
from os import path
from POS import ins_logger
import sys, os

from transaction.models import Transaction


from branch_stock.models import NonSaleable

from purchase.models import GrnDetails
# LG
import psycopg2.extras
try:
    userName = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    host = settings.DATABASES['default']['HOST']
    database = settings.DATABASES['default']['NAME']
    conn = psycopg2.connect(host=host,database=database, user=userName, password=password)
    # conn = psycopg2.connect(host="localhost",database="bi", user="admin", password="tms@123")
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    conn.autocommit = True
except Exception as e:
    print ("Cannot connect to Data Base..")

class DailySalesReport(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()
            # import pdb; pdb.set_trace()
            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            # dat_from = "2019-01-01"
            # dat_to = "2019-05-29"
            #
            int_cust_id  = request.data.get("intCustomerId")
            int_staff_id =  request.data.get("intStaffId")
            lst_more_filter = request.data.get("lst_moreFilter")
            lst_join = []

            dct_querry_var = {"Date":"dat_invoice",
            "Invoice Number":"vchr_invoice_num",
            "Branch":"branch.vchr_name as vchr_branch_name",
            "Customer":"sales_customer_details.vchr_name as vchr_customer_name",
            "Staff":"auth_user.first_name,auth_user.last_name",
            "Product":"products.vchr_name as vchr_product_name",
            "Brand":"brands.vchr_name as vchr_brand_name",
            "Item":"item.vchr_name as vchr_item_name",
            "Item Code":"item.vchr_item_code as vchr_item_code",
            "Imei/Batch":"json_imei->0 as IMEI,vchr_batch as BATCH",
            'Item Category':'vchr_item_category',
            'Item Category':'vchr_item_category',
            'Item Group':'vchr_item_group',
            'Tax Value':'dbl_tax',
            'Taxable Value':'dbl_amount as dbl_taxable_value',
            'Buyback' :'sales_details.dbl_buyback',
            'Discount':'sales_details.dbl_discount',
            'Indirect Discount':'sales_details.dbl_indirect_discount'}


            dct_join_data = {'Branch':' join branch on sales_master.fk_branch_id = branch.pk_bint_id' ,
                        'Product':' join products on item.fk_product_id = products.pk_bint_id',
                         'Brand':' join brands on item.fk_brand_id = brands.pk_bint_id' ,
                         'Customer':' left join sales_customer_details on sales_master.fk_customer_id = sales_customer_details.pk_bint_id' ,
                         'Staff' :' join auth_user on sales_master.fk_staff_id = auth_user.id',
                         'Item Category':'join item_category  on item_category.pk_bint_id=item.fk_item_category_id',
                         'Item Group':'join item_group on item_group.pk_bint_id=item.fk_item_category_id',

                         }

            if lst_more_filter:
                lst_selected = [data[1] for data in dct_querry_var.items() if data[0] in lst_more_filter]
                lst_group_by = [data[1].rsplit(" ",1)[-1] for data in dct_querry_var.items() if data[0] in lst_more_filter]
                lst_join = [dct_join_data[i] for i in lst_more_filter if i in dct_join_data.keys() ]
            else :
                lst_selected = ['dat_invoice']
                lst_group_by = ['dat_invoice']
                lst_more_filter = []
            #

            '''for adding imei and batch no. from the more filter, IMEI wasn't present in  lst_group_by'''
            if 'Imei/Batch' in lst_more_filter:
                lst_group_by.append('IMEI')



            '''dat_invoice in more filter is not mandatory anymore,
                hence dat_invoice is added to lst_group_by and lst_selected for
                 selecting dat_invoice in query and grouping it in query'''

            if 'dat_invoice' not in lst_group_by:
                lst_group_by.append('dat_invoice')

            if 'dat_invoice' not in lst_selected:
                lst_selected.append('dat_invoice')

            #
            # import pdb;pdb.set_trace()


            str_querry = "select {selected}, sum(sales_details.dbl_selling_price) as dbl_total_amount,sum(sales_details.int_qty) as int_total_qty,int_sales_status from sales_details  join sales_master on sales_details.fk_master_id = sales_master.pk_bint_id join item on sales_details.fk_item_id = item.pk_bint_id "
            #

            # "join branch on sales_master.fk_branch_id = branch.pk_bint_id"
            # if
            #  join products on item.fk_product_id = products.pk_bint_id
            #  join brands on item.fk_brand_id = brands.pk_bint_id
            #  join customer_details on sales_master.fk_customer_id = customer_details.pk_bint_id
            #  join auth_user on sales_master.fk_staff_id = auth_user.id
            #  join branch on sales_master.fk_branch_id = branch.pk_bint_id

            """DATE WISE FILTER"""
            str_filter = " WHERE dat_invoice:: DATE BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"'"
            """CUSTOMER WISE"""
            if int_cust_id:

                str_filter += "AND sales_master.fk_customer_id = "+str(int_cust_id)+" "
                # lst_selected.append("sales_customer_details.vchr_name as vchr_customer_name")
                # lst_group_by.append(" vchr_customer_name")
                if 'Customer' not in lst_more_filter:
                    str_querry += dct_join_data ['Customer']


            """STAFF WISE"""
            if int_staff_id:
                str_filter += "AND sales_master.fk_staff_id = "+str(int_staff_id)+" "
                # lst_selected.append("auth_user.first_name,auth_user.last_name")
                # lst_group_by.append("auth_user.first_name,auth_user.last_name")
                if 'Staff' not in lst_more_filter:
                    str_querry += dct_join_data ['Staff']

            # if not request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','PURCHASE MANAGER']:
            #     str_filter += "AND sales_master.fk_branch_id = "+str(request.user.userdetails.fk_branch_id)+" "

            if request.data.get('lstProduct'):
                # str_querry+ = ' AND fk_product_id in '+str(request.data.get('lst_product_id')).replace('[','(').replace("]",")")
                str_filter +=  ' AND fk_product_id in ' +str(request.data.get('lstProduct')).replace('[','(').replace(']',')')
            if request.data.get("lstBrand"):
                str_filter +=  ' AND fk_brand_id in ' +str(request.data.get('lstBrand')).replace('[','(').replace(']',')')

            if request.data.get("lstItemCategory"):

                str_filter +=  ' AND fk_item_category_id in ' +str(request.data.get('lstItemCategory')).replace('[','(').replace(']',')')

                # str_querry+ = " AND fk_item_category_id in "+str(request.data.get("lst_item_category_id")).replace("[","(")

            if request.data.get("lstItemGroup"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_filter +=  ' AND fk_item_group_id in ' +str(request.data.get('lstItemGroup')).replace('[','(').replace(']',')')

            if request.data.get("lstItem"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_filter +=  ' AND fk_item_id in ' +str(request.data.get('lstItem')).replace('[','(').replace(']',')')

            if request.data.get("lstBranch"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_filter +=  ' AND fk_branch_id in ' +str(request.data.get("lstBranch")).replace('[','(').replace(']',')')


            if request.data.get("bln_smart_choice"):

                str_filter += "and fk_product_id !=(select pk_bint_id from products where vchr_name ilike 'smart choice') "

            if request.data.get("bln_service"):

                str_filter += "and fk_master_id not in ( select sales_master.pk_bint_id from sales_master join sales_details on fk_master_id=sales_master.pk_bint_id where int_sales_status=3 and dat_invoice:: DATE BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"') "
            if request.data.get('strImeiBatch'):
                # str_filter += "and vchr_batch= '"+str(request.data.get('strImeiBatch'))+"' "
                str_filter += "and (json_imei->>0 = '"+str(request.data.get('strImeiBatch'))+"' or vchr_batch= '"+str(request.data.get('strImeiBatch'))+"')"
                # str_filter += "and json_imei->>0 ='"+str(request.data.get('strImeiBatch'))+"' "
            str_filter += ' and int_sales_status!=3'

            # -----------------------------------------------------------------------------------------
            '''USER PRIVILEGES'''
            dct_privilege = get_user_privileges(request)
            if dct_privilege:
                if dct_privilege.get('lst_branches'):
                    str_filter += ' AND fk_branch_id IN ('+str(dct_privilege['lst_branches'])[1:-1]+')'
                else:

                    str_filter += "AND sales_master.fk_branch_id = "+str(request.user.userdetails.fk_branch_id)+" "
                if dct_privilege.get('lst_products'):
                    str_filter += ' AND fk_product_id IN ('+str(dct_privilege['lst_products'])[1:-1]+')'
                if dct_privilege['lst_item_groups']:
                    str_filter += ' AND fk_item_group_id IN ('+str(dct_privilege['lst_item_groups'])[1:-1]+')'
            elif not request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','PURCHASE MANAGER']:
                str_filter += "AND sales_master.fk_branch_id = "+str(request.user.userdetails.fk_branch_id)+" "
            # ------------------------------------------------------------------------------------------
            str_querry = str_querry + "".join(set(lst_join)) + '{filter} group by {groupby},int_sales_status order by  dat_invoice DESC'
            str_querry = str_querry.format(selected = ','.join(set(lst_selected)),filter = str_filter,groupby = ','.join(set(lst_group_by)))
            rst_data = conn.execute(str_querry).fetchall()
            if request.data.get('blnExport'):
                if not rst_data:
                    return Response({'status':0,'message':'No Data'})

            if not rst_data:
                return Response({'status':1,'lst_data':[]})

            lst_data = []
            for ins_data in rst_data:

                dct_data = dict(ins_data)
                if dct_data['int_sales_status']==0:
                    dct_data['int_total_qty']=dct_data['int_total_qty'] * -1

                dct_data['dat_invoice'] = datetime.strftime(dct_data['dat_invoice'],'%d-%m-%Y')

                if 'Imei/Batch' in lst_more_filter:

                    dct_data['imei_batch_number']=dct_data['imei'] if dct_data['imei'] else dct_data['batch']


                if "first_name" in rst_data[0].keys():
                    dct_data['vchr_staff_name'] = ins_data.first_name + " " +ins_data.last_name

                lst_data.append(dct_data)
            if request.data.get('blnExport'):
                if dat_from:
                    datFrom_obj = datetime.strptime(dat_from, "%Y-%m-%d")
                    dat_from = datetime.strftime(datFrom_obj, "%d-%m-%Y")
                if dat_to:
                    datTo_obj = datetime.strptime(dat_to, "%Y-%m-%d")
                    dat_to = datetime.strftime(datTo_obj, "%d-%m-%Y")
                str_name = request.user.userdetails.first_name +' ' +request.user.userdetails.last_name
                file_name = 'DaillySalesDownload/daily_sales_' + datetime.strftime(datetime.now(), "%d-%m-%Y_%H_%M_%S_%f") + '.xlsx'
                dbl_taxable_sum = 0.0
                dbl_tax_sum = 0.0
                dbl_amt_sum = 0.0
                int_qnty_sum = 0
                if not path.exists(settings.MEDIA_ROOT + '/DaillySalesDownload/'):
                    os.mkdir(settings.MEDIA_ROOT + '/DaillySalesDownload/')
                writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
                workbook = writer.book
                head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
                head_style.set_pattern(1)
                head_style.set_bg_color('#bfbfbf')
                head_style.set_align('vcenter')

                row_style = workbook.add_format({'font_size':11, 'text_wrap': True})
                row_style.set_align('vcenter')
                worksheet = workbook.add_worksheet()

                title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
                title_style.set_align('vcenter')
                title_style.set_pattern(1)
                title_style.set_bg_color('#ffe0cc')
                worksheet.merge_range('A1+:L1', 'Daily Sales Report', title_style)
                worksheet.merge_range('A2+:C2', 'From Date    :' + dat_from, row_style)
                worksheet.merge_range('A3+:C3', 'To Date       :' + dat_to, row_style)
                worksheet.merge_range('A4+:C4', 'Taken By     :' + str_name, row_style)
                worksheet.set_row(0, 30)
                worksheet.protect('',{'autofilter':True})
                int_row = 5
                worksheet.write(int_row, 0, 'DATE', head_style)
                worksheet.write(int_row, 1, 'QUANTITY', head_style)
                worksheet.set_column(0, 1, 13)
                worksheet.write(int_row, 2, 'AMOUNT', head_style)
                worksheet.set_column(2, 2, 15)
                int_column = 3

                if lst_data[0].get('dbl_taxable_value') or lst_data[0].get('dbl_taxable_value') == 0.0:
                    worksheet.write(int_row, int_column, 'Taxable Value', head_style)
                    worksheet.set_column(int_column, int_column, 15)
                    int_taxable_comn = int_column
                    int_column += 1
                if lst_data[0].get('dbl_tax') or lst_data[0].get('dbl_tax') == 0.0:
                    worksheet.write(int_row, int_column, 'Tax Value', head_style)
                    worksheet.set_column(int_column, int_column, 15)
                    int_tax_comn = int_column
                    int_column += 1
                if lst_data[0].get('vchr_brand_name'):
                    worksheet.write(int_row, int_column, 'Brand', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('vchr_invoice_num'):
                    worksheet.write(int_row, int_column, 'INV No', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('vchr_product_name'):
                    worksheet.write(int_row, int_column, 'Product', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('vchr_staff_name'):
                    worksheet.write(int_row, int_column, 'Staff', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('imei_batch_number'):
                    worksheet.write(int_row, int_column, 'Imei/Batch', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('vchr_item_code'):
                    worksheet.write(int_row, int_column, 'Item Code', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('vchr_item_name'):
                    worksheet.write(int_row, int_column, 'Item', head_style)
                    worksheet.set_column(int_column, int_column, 30)
                    int_column += 1
                if lst_data[0].get('vchr_customer_name'):
                    worksheet.write(int_row, int_column, 'Customer', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('vchr_branch_name'):
                    worksheet.write(int_row, int_column, 'Branch', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('dbl_buyback') or lst_data[0].get('dbl_buyback')== 0.0:
                    worksheet.write(int_row, int_column, 'BuyBack', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('dbl_discount') or lst_data[0].get('dbl_discount') == 0.0:
                    worksheet.write(int_row, int_column, 'Discount', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                if lst_data[0].get('dbl_indirect_discount') or lst_data[0].get('dbl_indirect_discount') == 0.0:
                    worksheet.write(int_row, int_column, 'Indirect Discount', head_style)
                    worksheet.set_column(int_column, int_column, 20)
                    int_column += 1
                worksheet.set_row(int_row, 25)
                for ins_data in lst_data:
                    int_row += 1
                    worksheet.write(int_row, 0, ins_data['dat_invoice'], row_style)
                    worksheet.write(int_row, 1, ins_data['int_total_qty'], row_style)
                    int_qnty_sum += ins_data['int_total_qty']
                    worksheet.write(int_row, 2, ins_data['dbl_total_amount'], row_style)
                    dbl_amt_sum += ins_data['dbl_total_amount']
                    int_column = 3
                    if lst_data[0].get('dbl_taxable_value') or lst_data[0].get('dbl_taxable_value') == 0.0:
                        worksheet.write(int_row, int_column, ins_data['dbl_taxable_value'], row_style)
                        dbl_taxable_sum += ins_data['dbl_taxable_value']
                        int_column += 1
                    if lst_data[0].get('dbl_tax') or lst_data[0].get('dbl_tax') == 0.0:
                        worksheet.write(int_row, int_column, ins_data['dbl_tax'], row_style)
                        dbl_tax_sum += ins_data['dbl_tax']
                        int_column += 1
                    if lst_data[0].get('vchr_brand_name'):
                        worksheet.write(int_row, int_column, ins_data['vchr_brand_name'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_invoice_num'):
                        worksheet.write(int_row, int_column, ins_data['vchr_invoice_num'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_product_name'):
                        worksheet.write(int_row, int_column, ins_data['vchr_product_name'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_staff_name'):
                        worksheet.write(int_row, int_column, ins_data['vchr_staff_name'], row_style)
                        int_column += 1
                    if lst_data[0].get('imei_batch_number'):
                        worksheet.write(int_row, int_column, ins_data['imei_batch_number'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_item_code'):
                        worksheet.write(int_row, int_column, ins_data['vchr_item_code'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_item_name'):
                        worksheet.write(int_row, int_column, ins_data['vchr_item_name'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_customer_name'):
                        worksheet.write(int_row, int_column, ins_data['vchr_customer_name'], row_style)
                        int_column += 1
                    if lst_data[0].get('vchr_branch_name'):
                        worksheet.write(int_row, int_column, ins_data['vchr_branch_name'], row_style)
                        int_column += 1
                    if lst_data[0].get('dbl_buyback') or lst_data[0].get('dbl_buyback')== 0.0:
                        worksheet.write(int_row, int_column, ins_data['dbl_buyback'], row_style)
                        int_column += 1
                    if lst_data[0].get('dbl_discount') or lst_data[0].get('dbl_discount') == 0.0:
                        worksheet.write(int_row, int_column, ins_data['dbl_discount'], row_style)
                        int_column += 1
                    if lst_data[0].get('dbl_indirect_discount') or lst_data[0].get('dbl_indirect_discount') == 0.0:
                        worksheet.write(int_row, int_column, ins_data['dbl_indirect_discount'], row_style)
                        int_column += 1
                    worksheet.set_row(int_row, 25, row_style)
                int_row += 1
                worksheet.write(int_row,0 , 'Total', row_style)
                worksheet.write(int_row,1 , int_qnty_sum, row_style)
                worksheet.write(int_row,2 , round(dbl_amt_sum, 2), row_style)
                if lst_data[0].get('dbl_taxable_value') or lst_data[0].get('dbl_taxable_value') == 0.0:
                    worksheet.write(int_row,int_taxable_comn , round(dbl_taxable_sum,2), row_style)
                if lst_data[0].get('dbl_tax') or lst_data[0].get('dbl_tax') == 0.0:
                    worksheet.write(int_row,int_tax_comn , round(dbl_tax_sum,2), row_style)
                writer.save()
                lst_data = []
                return Response({'status':1,'lst_data':lst_data,'export_data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
            else:
                return Response({'status':1,'lst_data':lst_data})
        except Exception as msg:
            return Response({'status':0,'data':str(msg)})





class CustomerTypeahead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            #
            str_search_term = request.data.get('term',-1)
            lst_customer = []
            if str_search_term != -1:
                ins_customer = SalesCustomerDetails.objects.filter(Q(vchr_name__icontains=str_search_term) | Q(int_mobile__icontains=str_search_term)).values('pk_bint_id','vchr_name','int_mobile')[:10]
                if ins_customer:
                    for itr_item in ins_customer:
                        dct_customer = {}
                        dct_customer['name'] = itr_item['vchr_name'] + ' - ' + str(itr_item['int_mobile'])
                        dct_customer['id'] = itr_item['pk_bint_id']
                        dct_customer['phone'] = itr_item['int_mobile']
                        lst_customer.append(dct_customer)
                return Response({'status':1,'data':lst_customer})

        except Exception as e:
            return Response({'result':0,'reason':e})


class DailyBranchStockReport(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()
            bln_check = request.data.get("blnCheck")
            # bln_check = False
            # import pdb; pdb.set_trace()
            dat_stock = request.data.get('date')
            # dat_stock = '2020-02-03'
            lst_product_id = request.data.get('lstProduct')
            lst_brand_id = request.data.get('lstBrand')
            lst_item_group_id = request.data.get('lstItemGroup')
            lst_item_cat_id = request.data.get('lstItemCategory')
            lst_item_id = request.data.get('lstItem')
            lst_branch_id = request.data.get('lstBranch')
            lst_more_filter = request.data.get('lst_more_filter') or []
            dct_export_filter  = {}
            dct_filter_non_saleable = {}
            # import pdb; pdb.set_trace()
            dct_price_perm_dat = get_price_perm(request.user.id)
            # dct_price_perm_dat = {'bln_mrp':True, 'bln_mop':True, 'bln_dp':True, 'bln_cost_price':True}

            #


            # lst_more_filter =  ['Product', 'Brand', 'Stock']
            # lst_product_id = [12,14]
            bln_branch = False
            dct_details = {}
            ins_product = list(Products.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            ins_item_category = list(ItemCategory.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_item_category')).values('id','name'))
            ins_brands = list(Brands.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            # ins_items = list(Item.objects.annotate(id=F('pk_bint_id'),name=F('vchr_name')).values('id','name'))
            ins_item_group = list(ItemGroup.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_item_group')).values('id','name'))

            if request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN':
                ins_branch = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
                dct_details['branch']=ins_branch
                bln_branch = True

            dct_details['product']=ins_product
            dct_details['item_category']=ins_item_category
            dct_details['brand']=ins_brands
            # dct_details['item']=ins_items
            dct_details['item_group']=ins_item_group

            # lst_more_filter = ['Product','Brand','Item','ItemCategory','ItemGroup','Branch','Imei']
            if 'Imei' in lst_more_filter:
                lst_more_filter.extend(['Type','Branch_age','DateBranchStock','TotalAge','DateFirstIn'])
                if  'Item' not in lst_more_filter:
                    lst_more_filter.extend(['Item','ItemCode'])
            if 'Price' in lst_more_filter:
                lst_more_filter.append('Item')

            dct_data_selected = {'Price':",".join(["br_data."+x[0].replace('bln_','dbl_') for x in dct_price_perm_dat.items() if x[1] == True]),
                                 'Product':'br_data.vchr_product_name',
                                 'Brand':'br_data.vchr_brand_name',
                                 'Item':"br_data.vchr_item_name" ,
                                 'ItemCode':"br_data.vchr_item_code",
                                 'ItemCategory':'br_data.vchr_item_cat_name',
                                 'ItemGroup':'br_data.vchr_item_group_name',
                                 'Branch':'UPPER(br_data.vchr_branch_name) as vchr_branch_name',
                                 'Type':'br_data.vchr_type',
                                 'Branch_age':'br_data.int_branch_age',
                                 'DateBranchStock':"to_char(br_data.dat_branch_stock::DATE, 'DD/MM/YYYY') as dat_branch_stock",
                                 'TotalAge':'br_data.int_total_age',
                                 'DateFirstIn':"to_char(br_data.dat_purchase_stock::DATE, 'DD/MM/YYYY') as dat_purchase_stock",
                                 'Imei':"br_data.int_item_id,br_data.jsn_imei,br_data.jsn_batch_no,to_char(br_data.dat_branch_stock::DATE, 'DD/MM/YYYY') as dat_branch_stock,br_data.int_branch_age,to_char(br_data.dat_purchase_stock::DATE, 'DD/MM/YYYY') as dat_purchase_stock,br_data.int_total_age"}
            lst_selected = [x[1] for x in dct_data_selected.items() if x[0] in lst_more_filter ]


            dct_data_group_by = {'Price':",".join(["br_data."+x[0].replace('bln_','dbl_') for x in dct_price_perm_dat.items() if x[1] == True]),
                                'Product':'br_data.vchr_product_name',
                                'Brand':'br_data.vchr_brand_name',
                                'Item':"vchr_item_name,br_data.vchr_item_code",
                                'ItemCode':"br_data.vchr_item_code",
                                'ItemCategory':'br_data.vchr_item_cat_name',
                                'ItemGroup':'br_data.vchr_item_group_name',
                                'Branch':'br_data.vchr_branch_name',
                                'Type':'br_data.vchr_type',
                                'Branch_age':'br_data.int_branch_age',
                                'DateBranchStock':'br_data.dat_branch_stock',
                                'TotalAge':'br_data.int_total_age',
                                'DateFirstIn':'br_data.dat_purchase_stock',
                                'Imei' :'br_data.int_item_id,br_data.jsn_imei,br_data.jsn_batch_no'
                                }

            lst_group_by = [x[1] for x in dct_data_group_by.items() if x[0] in lst_more_filter ]

            if 'Imei' in lst_more_filter:
                lst_group_by.append('br_data.vchr_type')
                lst_selected.append('br_data.vchr_type')
            str_query = """select {selected} from (select 0 as int_transit,bsid.int_qty as int_qty,CASE WHEN bsid.jsn_imei ->>'imei' ='[]' then NULL else (bsid.jsn_imei->>'imei') END as jsn_imei,CASE WHEN bsd.jsn_batch_no ->>'batch' ='[]' then NULL else (bsd.jsn_batch_no->>'batch')::TEXT END as jsn_batch_no ,
                                bsm.dat_stock as dat_branch_stock,(NOW()::DATE-(bsm.dat_stock )::DATE)::INTEGER as int_branch_age,
                                grm.dat_purchase as dat_purchase_stock, (NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age,
                                (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,bsm.dat_stock::DATE as dat_stock ,'BRANCH' as vchr_type,
                                it.dbl_mrp as dbl_mrp,it.dbl_mop as dbl_mop,it.dbl_dealer_cost as dbl_dp,it.dbl_supplier_cost as dbl_cost_price

                            from branch_stock_imei_details bsid
                            join branch_stock_details bsd on bsid.fk_details_id = bsd.pk_bint_id
                            join grn_details grd on bsid.fk_grn_details_id = grd.pk_bint_id
                            join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                            join branch_stock_master bsm on bsd.fk_master_id =bsm.pk_bint_id
                            join branch br on bsm.fk_branch_id = br.pk_bint_id
                            join item it on bsd.fk_item_id = it.pk_bint_id
                            join brands bd on bd.pk_bint_id =it.fk_brand_id
                            join products pd on pd.pk_bint_id = it.fk_product_id
                            join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                            join item_category itc on itc.pk_bint_id = it.fk_item_category_id
                        UNION ALL
                            select 0 as int_transit,(grd.int_avail) as int_qty,CASE WHEN grd.jsn_imei_avail ->>'imei_avail' ='[]' then NULL else (grd.jsn_imei_avail->>'imei_avail') END  as jsn_imei,(CASE WHEN COALESCE(grd.vchr_batch_no,'')='' then NULL else regexp_replace('["'|| vchr_batch_no||'"]', '\t', '', 'g') end) as jsn_batch_no,
                                (grm.dat_purchase)::DATE as dat_branch_stock,(NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_branch_age,
                                (grm.dat_purchase)::DATE as dat_purchase_stock,(NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age,
                                (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,grm.dat_purchase::DATE as dat_stock,'GRN' as vchr_type,
                                it.dbl_mrp as dbl_mrp,it.dbl_mop as dbl_mop,it.dbl_dealer_cost as dbl_dp,it.dbl_supplier_cost as dbl_cost_price
                            from grn_details grd
                            join grn_master grm on grd.fk_purchase_id = grm.pk_bint_id
                            join branch br on grm.fk_branch_id = br.pk_bint_id
                            join item it on grd.fk_item_id = it.pk_bint_id
                            join brands bd on bd.pk_bint_id =it.fk_brand_id
                            join products pd on pd.pk_bint_id = it.fk_product_id
                            join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                            join item_category itc on itc.pk_bint_id = it.fk_item_category_id
                        UNION ALL
                            select stid.int_qty as int_transit, 0 as int_qty,CASE WHEN stid.jsn_imei ->>'imei' ='[]' then NULL else (stid.jsn_imei->>'imei') END  as jsn_imei,
                                CASE WHEN stid.jsn_batch_no ->>'batch' ='[]' then NULL else  (ist.jsn_batch_no->>'batch')::TEXT END as jsn_batch_no,
                                NULL as dat_branch_stock,NULL as int_branch_age,grm.dat_purchase as dat_purchase_stock, (NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age ,
                                (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'TRANSFER' as vchr_type,
                                it.dbl_mrp as dbl_mrp,it.dbl_mop as dbl_mop,it.dbl_dealer_cost as dbl_dp,it.dbl_supplier_cost as dbl_cost_price
                            from stock_transfer_imei_details stid
                            join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                            join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                            join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                            join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                            join branch br on br.pk_bint_id = stf.fk_to_id
                            join item it on ist.fk_item_id = it.pk_bint_id
                            join brands bd on bd.pk_bint_id =it.fk_brand_id
                            join products pd on pd.pk_bint_id = it.fk_product_id
                            join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                            join item_category itc on itc.pk_bint_id = it.fk_item_category_id
                            where stf.int_status in (1,2)
                        UNION ALL
                            select  0 as int_transit,stid.int_qty as int_qty,CASE WHEN stid.jsn_imei ->>'imei' ='[]' then NULL else (stid.jsn_imei->>'imei') END  as jsn_imei,
                                CASE WHEN stid.jsn_batch_no ->>'batch' ='[]' then NULL else  (ist.jsn_batch_no->>'batch')::TEXT END as jsn_batch_no,
                                NULL as dat_branch_stock,NULL as int_branch_age,grm.dat_purchase as dat_purchase_stock, (NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age ,
                                (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'BILLED' as vchr_type,
                                it.dbl_mrp as dbl_mrp,it.dbl_mop as dbl_mop,it.dbl_dealer_cost as dbl_dp,it.dbl_supplier_cost as dbl_cost_price
                            from stock_transfer_imei_details stid
                            join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                            join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                            join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                            join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                            join branch br on br.pk_bint_id = stf.fk_from_id
                            join item it on ist.fk_item_id = it.pk_bint_id
                            join brands bd on bd.pk_bint_id =it.fk_brand_id
                            join products pd on pd.pk_bint_id = it.fk_product_id
                            join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                            join item_category itc on itc.pk_bint_id = it.fk_item_category_id
                            where stf.int_status in (0)) as br_data WHERE (int_qty>0 or int_transit>0) AND br_data.dat_stock <= '"""+ str(dat_stock)+"""'"""
            str_filter = ''
            str_sales_filter = ''
            lst_selected.append('sum(br_data.int_qty) as int_qty,sum(br_data.int_transit) as int_transit')
            # if not request.user.userdetails.fk_branch.int_type not in [2,3] :
            #     str_filter +=' AND br_data.int_branch_id = ' +str(request.user.userdetails.fk_branch_id) +''
            # else:
            #     str_filter +=' AND br_data.int_branch_id in '+str(tuple(lst_branch_id))+''
            # if request.user.userdetails.fk_branch.int_type  in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','PURCHASE MANAGER'] :
            #     if lst_branch_id:
            #         str_filter +=' AND br_data.int_branch_id in ('+ str(lst_branch_id)[1:-1]+')'
            #         str_sales_filter += 'AND br.pk_bint_id in ('+ str(lst_branch_id)[1:-1]+')'
            #
            #         dct_filter_non_saleable['fk_branch_id__in']= lst_branch_id
            #
            # else:
            #     str_filter +=' AND br_data.int_branch_id = ' +str(request.user.userdetails.fk_branch_id) +''
            #     str_sales_filter +=' AND br.pk_bint_id = ' +str(request.user.userdetails.fk_branch_id) +''
            #     dct_filter_non_saleable['fk_branch_id']= str(request.user.userdetails.fk_branch_id)

            if lst_product_id:
                str_filter +=' AND br_data.int_product_id in ('+str(lst_product_id)[1:-1]+')'
                str_sales_filter +=' AND pd.pk_bint_id in ('+str(lst_product_id)[1:-1]+')'
                dct_export_filter['Products'] = list(Products.objects.filter(pk_bint_id__in = lst_product_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
            if  lst_brand_id:
                str_filter +=' AND br_data.int_brand_id in ('+str(lst_brand_id)[1:-1]+')'
                str_sales_filter +=' AND bd.pk_bint_id in ('+str(lst_brand_id)[1:-1]+')'
                dct_export_filter['Brands'] = list(Brands.objects.filter(pk_bint_id__in = lst_brand_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))


            if lst_item_group_id:
                str_filter +=' AND br_data.int_item_group_id in ('+str(lst_item_group_id)[1:-1]+')'
                str_sales_filter +=' AND itg.pk_bint_id in ('+str(lst_item_group_id)[1:-1]+')'
                dct_export_filter['Item Groups'] =  list(ItemGroup.objects.filter(pk_bint_id__in = lst_item_group_id).annotate(name=Upper('vchr_item_group')).values_list('name',flat=True))

            if lst_item_cat_id:
                str_filter +=' AND br_data.int_item_cat_id in ('+str(lst_item_cat_id)[1:-1]+')'
                str_sales_filter +=' AND itc.pk_bint_id in ('+str(lst_item_cat_id)[1:-1]+')'
                dct_export_filter['Item Categories'] =list(ItemCategory.objects.filter(pk_bint_id__in = lst_item_cat_id).annotate(name=Upper('vchr_item_category')).values_list('name',flat=True))

            if lst_item_id:
                str_filter +=' AND br_data.int_item_id in ('+str(lst_item_id)[1:-1]+')'
                str_sales_filter +=' AND it.pk_bint_id in ('+str(lst_item_id)[1:-1]+')'
                dct_export_filter['Items'] = list(Item.objects.filter(pk_bint_id__in = lst_item_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
            if lst_branch_id:
                str_filter +=' AND br_data.int_branch_id in ('+ str(lst_branch_id)[1:-1]+')'
                str_sales_filter +=' AND br.pk_bint_id in ('+ str(lst_branch_id)[1:-1]+')'
                dct_export_filter['Branches'] = list(Branch.objects.filter(pk_bint_id__in = lst_branch_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))


                dct_filter_non_saleable['fk_branch_id__in']= lst_branch_id

            if request.data.get('strImeiBatch'):
                # (jsn_imei->>'imei')::jsonb ?|Array['359972080145722'];
                str_filter +=" AND ((br_data.jsn_imei)::jsonb ?|Array[ '"+str(request.data.get('strImeiBatch'))+"'] or (br_data.jsn_batch_no)::jsonb ?|Array[ '"+str(request.data.get('strImeiBatch'))+"'])"
                str_sales_filter +=" AND ((sd.json_imei)::jsonb ?|Array[ '"+str(request.data.get('strImeiBatch'))+"'] or sd.vchr_batch= '"+str(request.data.get('strImeiBatch'))+"')"
            # str_filter +=' AND br_data.int_transit >= 0'
            #
            '''DROP DOWN FOR NON-SALEABLE AND SALEABLE ITEMS'''
            lst_status_change_imei=NonSaleable.objects.filter(**dct_filter_non_saleable).extra(select={'imei':'jsonb_array_elements(jsn_status_change)'}).values_list('imei',flat=True)
            lst_non_saleable_imei=NonSaleable.objects.filter(**dct_filter_non_saleable).extra(select={'imei':'jsonb_array_elements(jsn_non_saleable)'}).values_list('imei',flat=True).exclude(jsn_non_saleable__has_any_keys=list(lst_status_change_imei))
            dct_imeis= {imei :None for imei in lst_non_saleable_imei}
            str_query = str_query + '{filter} group by {group_by} '

            # -----------------------------------------------------------------------------------------
            '''USER PRIVILEGES'''
            dct_privilege = get_user_privileges(request)
            if dct_privilege:
                if dct_privilege.get('lst_branches'):
                    if len(dct_privilege['lst_branches']):
                        bln_branch = True
                        dct_details['branch'] = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
                    str_filter += ' AND br_data.int_branch_id IN ('+str(dct_privilege['lst_branches'])[1:-1]+')'
                    str_sales_filter += ' AND br.pk_bint_id IN ('+str(dct_privilege['lst_branches'])[1:-1]+')'

                    dct_export_filter['Branches'] = list(Branch.objects.filter(pk_bint_id__in = dct_privilege['lst_branches']).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
                    if lst_branch_id:
                        dct_export_filter['Branches'] = list(Branch.objects.filter(pk_bint_id__in = dct_privilege['lst_branches']).filter(pk_bint_id__in = lst_branch_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))

                else :
                    str_filter +=' AND br_data.int_branch_id = ' +str(request.user.userdetails.fk_branch_id) +''
                    str_sales_filter +=' AND br.pk_bint_id = ' +str(request.user.userdetails.fk_branch_id) +''
                    dct_filter_non_saleable['fk_branch_id']= str(request.user.userdetails.fk_branch_id)

                if dct_privilege.get('lst_products'):
                    str_filter += ' AND br_data.int_product_id IN ('+str(dct_privilege['lst_products'])[1:-1]+')'
                    str_sales_filter += ' AND pd.pk_bint_id IN ('+str(dct_privilege['lst_products'])[1:-1]+')'
                    # dct_export_filter['Products'] = list(Products.objects.filter(pk_bint_id__in = dct_privilege['lst_products']).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
                if dct_privilege['lst_item_groups']:
                    str_filter += ' AND br_data.int_item_group_id IN ('+str(dct_privilege['lst_item_groups'])[1:-1]+')'
                    str_sales_filter += ' AND itg.pk_bint_id IN ('+str(dct_privilege['lst_item_groups'])[1:-1]+')'
                    # dct_export_filter['Item Groups'] =  list(ItemGroup.objects.filter(pk_bint_id__in = dct_privilege['lst_item_groups']).annotate(name=Upper('vchr_item_group')).values_list('name',flat=True))
            elif not request.user.userdetails.fk_branch.int_type  in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() not in ['ADMIN','PURCHASE MANAGER'] :
                str_filter +=' AND br_data.int_branch_id = ' +str(request.user.userdetails.fk_branch_id) +''
                str_sales_filter +=' AND br.pk_bint_id = ' +str(request.user.userdetails.fk_branch_id) +''
                dct_filter_non_saleable['fk_branch_id']= str(request.user.userdetails.fk_branch_id)
            # -----------------------------------------------------------------------------------------
            str_query = str_query.format(selected = ','.join(set(lst_selected)),filter = str_filter,group_by = ','.join(set(lst_group_by)))
            #
            rst_data = conn.execute(str_query).fetchall()
            lst_data = []
            lst_test = []
            if not rst_data:
                return Response({'status':0,'reason':'No Data'})
            asd =datetime.now()
            int_count =0
            for ins_data in rst_data:
                dct_data =  copy.deepcopy(dict(ins_data))
                if 'Imei' in lst_more_filter:
                    if ins_data.vchr_type =='TRANSFER':

                        if ins_data.jsn_imei:
                            lst_jsn_imei= copy.deepcopy(eval(ins_data.jsn_imei))
                            for jsn_imei in lst_jsn_imei:
                                dct_data['jsn_imei'] = jsn_imei
                                dct_data['int_transit'] = 1
                                dct_data['int_qty'] = 0

                                if 'int_qty' in  dct_data and 'int_transit' in dct_data:
                                    dct_data['int_qty_transit_sum']=dct_data['int_qty'] + dct_data['int_transit']
                                # import pdb;pdb.set_trace()
                                if request.data.get('strImeiBatch'):
                                    if request.data.get('strImeiBatch') == jsn_imei:
                                        lst_test.append(dct_data.copy())
                                        lst_data.append(dct_data.copy())
                                else:
                                    lst_test.append(dct_data.copy())
                                    lst_data.append(dct_data.copy())
                        elif ins_data.jsn_batch_no:
                            dct_data['jsn_batch_no'] = eval(ins_data.jsn_batch_no)[0]
                            # #
                            if 'int_qty' in  dct_data and 'int_transit' in dct_data:
                                dct_data['int_qty_transit_sum']=dct_data['int_qty'] + dct_data['int_transit']

                            # import pdb;pdb.set_trace()

                            lst_data.append(dct_data.copy())
                            # int_qty  = ins_data.int_qty
                            # for int_count in range(ins_data.int_qty):
                            #     dct_data['jsn_batch_no'] = ins_data.jsn_batch_no[0]
                            #     dct_data['int_transit'] = 1
                            #     dct_data['int_qty'] = 0
                            #     lst_data.append(dct_data.copy())


                    else:
                        if ins_data.jsn_imei:
                            lst_jsn_imei= copy.deepcopy(eval(ins_data.jsn_imei))
                            for jsn_imei in lst_jsn_imei:
                                dct_data['jsn_imei'] = jsn_imei
                                dct_data['int_qty'] = 1

                                if 'int_qty' in  dct_data and 'int_transit' in dct_data:
                                    dct_data['int_qty_transit_sum']=dct_data['int_qty'] + dct_data['int_transit']

                                # import pdb;pdb.set_trace()
                                if request.data.get('strImeiBatch'):
                                    if request.data.get('strImeiBatch') == jsn_imei:
                                        lst_data.append(dct_data.copy())
                                else:
                                    lst_data.append(dct_data.copy())

                        elif ins_data.jsn_batch_no:
                            dct_data['jsn_batch_no'] = eval(ins_data.jsn_batch_no)[0]

                            if 'int_qty' in  dct_data and 'int_transit' in dct_data:
                                dct_data['int_qty_transit_sum']=dct_data['int_qty'] + dct_data['int_transit']

                            # import pdb;pdb.set_trace()

                            lst_data.append(dct_data.copy())
                            # int_qty  = ins_data.int_qty
                            # for int_count in range(ins_data.int_qty):
                            #     dct_data['jsn_batch_no'] = ins_data.jsn_batch_no[0]
                            #     dct_data['int_qty'] = 1
                            #     lst_data.append(dct_data.copy())
                else:

                    if 'int_qty' in  dct_data and 'int_transit' in dct_data:
                        dct_data['int_qty_transit_sum']=dct_data['int_qty'] + dct_data['int_transit']

                    # import pdb;pdb.set_trace()

                    lst_data.append(dct_data.copy())
            temp = [ x.pop('vchr_type') for x in lst_data if 'vchr_type' in  x]
            #
            #-----------------------------------------------------------------------------------------
            #-----------------SALE,RETURN-------------------------------------------------------------------------

            #
            str_sales_group_by_price_perm = ",".join(["it."+x[0].replace('bln_','dbl_') for x in dct_price_perm_dat.items() if x[1] == True])
            str_sales_group_by_price_perm = str_sales_group_by_price_perm.replace('it.dbl_cost_price','it.dbl_supplier_cost')
            str_sales_group_by_price_perm = str_sales_group_by_price_perm.replace('it.dbl_dp','it.dbl_dealer_cost')
            str_sales_select_by_price_perm = str_sales_group_by_price_perm.replace('it.dbl_dealer_cost','it.dbl_dealer_cost as dbl_dp')
            str_sales_select_by_price_perm = str_sales_select_by_price_perm.replace('it.dbl_supplier_cost','it.dbl_supplier_cost as dbl_cost_price')

            dct_sales_data =  {  'Price':str_sales_select_by_price_perm,
                                 'Product':'pd.vchr_name as vchr_product_name' ,
                                 'Brand':'bd.vchr_name as vchr_brand_name',
                                 'Item':"it.vchr_name as vchr_item_name" ,
                                 'ItemCode':"it.vchr_item_code as vchr_item_code",
                                 'ItemCategory':'itc.vchr_item_category as vchr_item_cat_name',
                                 'ItemGroup':'itg.vchr_item_group   as vchr_item_group_name',
                                 'Branch':'UPPER(br.vchr_name) as vchr_branch_name',
                                 'Imei':"it.pk_bint_id as int_item_id,sd.json_imei as jsn_imei ,sd.vchr_batch as jsn_batch_no"
                                 }
            lst_sales_data_selected = [x[1] for x in dct_sales_data.items() if x[0] in lst_more_filter ]
            dct_sales_data_group_by = {
                                'Price':str_sales_group_by_price_perm,
                                'Product':'pd.vchr_name ' ,
                                'Brand':'bd.vchr_name ',
                                'Item':"it.vchr_name " ,
                                'ItemCode':"it.vchr_item_code ",
                                'ItemCategory':'itc.vchr_item_category ',
                                'ItemGroup':'itg.vchr_item_group   ',
                                'Branch':'UPPER(br.vchr_name) ',
                                'Imei':"it.pk_bint_id ,sd.json_imei,sd.vchr_batch"
                                }

            lst_sales_data_group_by = [x[1] for x in dct_sales_data_group_by.items() if x[0] in lst_more_filter ]
            lst_sales_data_group_by.append('vchr_sales_type')

            str_sales_query = """select {selected}, sum(sd.int_qty) as int_qty,
                                CASE WHEN sd.int_sales_status = 1 then 'SALE' WHEN sd.int_sales_status = 0 then 'RETURN' end as vchr_sales_type
                                from sales_details sd
                                join sales_master sm on sd.fk_master_id = sm.pk_bint_id
                                join branch br on sm.fk_branch_id = br.pk_bint_id
                                join item it on sd.fk_item_id = it.pk_bint_id
                                join brands bd on bd.pk_bint_id =it.fk_brand_id
                                join products pd on pd.pk_bint_id = it.fk_product_id
                                join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                                join item_category itc on itc.pk_bint_id = it.fk_item_category_id WHERE pd.vchr_name != 'SERVICE' and sm.dat_invoice > '"""+ str(dat_stock)+"""'"""
            str_sales_query = str_sales_query + '{filter} group by {group_by} '
            str_sales_query = str_sales_query.format(selected = ','.join(set(lst_sales_data_selected)),filter = str_sales_filter,group_by = ','.join(set(lst_sales_data_group_by)))
            #
            rst_sales_data = conn.execute(str_sales_query).fetchall()

            if rst_sales_data:
                lst_rst_sales_data = [dict(x) for x in rst_sales_data]

                lst_sales_data_SALE=[]
                lst_sales_data_RETURN=[]
                for x in lst_rst_sales_data:
                     if x['vchr_sales_type'] == 'SALE' :
                        x['int_qty_transit_sum']=x['int_qty']
                        lst_sales_data_SALE.append(x)
                for x in lst_rst_sales_data:
                     if x['vchr_sales_type'] == 'RETURN' :
                        x['int_qty_transit_sum']=x['int_qty']

                        lst_sales_data_RETURN.append(x)
                #
                lst_rest_stock_data = [dict(x) for x in rst_data]
                lst_keys_sales = list(lst_rst_sales_data[0].keys())
                lst_keys_sales.remove('int_qty')
                lst_keys_sales.remove('vchr_sales_type')
                # if 'dbl_mop' in some_list: some_list.remove('dbl_mop')
                # if 'dbl_mrp' in some_list: some_list.remove('dbl_mrp')
                # if 'dbl_dealer_cost' in some_list: some_list.remove('dbl_dealer_cost')
                # if 'dbl_supplier_cost' in some_list: some_list.remove('dbl_supplier_cost')

                lst_sale_data_imei = []
                lst_return_data_imei = []
                if 'jsn_imei' in lst_keys_sales:
                    lst_sales_data_SALE =[]
                    lst_sales_data_RETURN = []
                    for dct_sales in lst_rst_sales_data :
                        if dct_sales['vchr_sales_type'] == 'SALE':

                            if dct_sales['jsn_imei']:
                                lst_imei =  copy.deepcopy(dct_sales['jsn_imei'])
                                for imei in lst_imei:
                                    dct_sale_temp = dct_sales.copy()
                                    dct_sale_temp['jsn_imei'] = imei
                                    dct_sale_temp['int_qty'] = 1
                                    dct_sale_temp['int_transit'] = 0
                                    dct_sale_temp['int_qty_transit_sum']=dct_sale_temp['int_qty'] + dct_sale_temp['int_transit']
                                    if 'vchr_sales_type' in dct_sales.keys():
                                        dct_sale_temp.pop('vchr_sales_type')
                                    if request.data.get('strImeiBatch'):
                                        if request.data.get('strImeiBatch') == imei:
                                            lst_sale_data_imei.append(dct_sale_temp)
                                    else:
                                        lst_sale_data_imei.append(dct_sale_temp)

                            elif dct_sales['jsn_batch_no']:
                                dct_sales['int_transit'] = 0
                                if 'int_qty' in  dct_sales and 'int_transit' in dct_sales:
                                    dct_sales['int_qty_transit_sum']=dct_sales['int_qty'] + dct_sales['int_transit']

                                if 'vchr_sales_type' in dct_sales.keys():
                                    dct_sales.pop('vchr_sales_type')
                                lst_sale_data_imei.append(dct_sales)

                        elif dct_sales['vchr_sales_type'] == 'RETURN':
                            for dct_stock_data in lst_data:

                                if dct_sales['jsn_imei']:
                                    lst_imei =  copy.deepcopy(dct_sales['jsn_imei'])
                                    for imei in  lst_imei:
                                        if imei == dct_stock_data['jsn_imei']:
                                            if request.data.get('strImeiBatch'):
                                                if request.data.get('strImeiBatch') == imei:
                                                    lst_return_data_imei.append(dct_stock_data)
                                            else:
                                                lst_return_data_imei.append(dct_stock_data)

                                elif dct_sales['jsn_batch_no']:
                                    if dct_stock_data['jsn_batch_no']:
                                        if dct_sales['jsn_batch_no'] == dct_stock_data['jsn_batch_no']:
                                            dct_stock_data['int_qty'] -= dct_sales['int_qty']
                                            dct_stock_data['int_qty_transit_sum'] -= dct_sales['int_qty']


                else:
                    for dct_sales in lst_rst_sales_data :
                        # if dct_sales['vchr_item_code']=='MOB01504':
                        #     # import pdb;pdb.set_trace()
                        for dct_stock_data in lst_data:
                            if not  dct_sales.get('vchr_sales_type'):
                                continue
                            if dct_sales['vchr_sales_type'] == 'SALE':

                                dct_sales_temp_check = {}
                                dct_stock_temp_check = {}
                                for key in lst_keys_sales:
                                    dct_sales_temp_check[key] = dct_sales[key]
                                    dct_stock_temp_check[key] = dct_stock_data[key]
                                if dct_sales_temp_check ==  dct_stock_temp_check:
                                    dct_stock_data['int_qty']+= dct_sales['int_qty']
                                    dct_stock_data['int_qty_transit_sum']+= dct_sales['int_qty']

                                    lst_sales_data_SALE.remove(dct_sales)

                            elif dct_sales['vchr_sales_type'] == 'RETURN':
                                dct_sales_temp_check = {}
                                dct_stock_temp_check = {}

                                for key in lst_keys_sales:
                                    dct_sales_temp_check[key] = dct_sales[key]
                                    dct_stock_temp_check[key] = dct_stock_data[key]
                                if dct_sales_temp_check ==  dct_stock_temp_check:
                                    dct_stock_data['int_qty']-= dct_sales['int_qty']

                                    dct_stock_data['int_qty_transit_sum']-= dct_sales['int_qty']

                #
                #-----------------------------------------------------------
                if lst_sales_data_SALE:

                    temp = [  x.pop("vchr_sales_type") for x in lst_sales_data_SALE]
                    lst_stocked_out =  [  x.update({'int_transit':0}) for x in lst_sales_data_SALE]
                    # import pdb;pdb.set_trace()

                    lst_data.extend(lst_sales_data_SALE)
                if lst_return_data_imei:
                    for dct_data in lst_return_data_imei:
                        lst_data.remove(dct_data)
                    pass
                if not lst_data:
                    return Response({'status':0,'reason':'No Data'})
                if lst_sale_data_imei:
                    lst_main_data_keys = list(lst_data[0].keys())
                    lst_sales_data_keys = list(lst_sale_data_imei[0].keys())
                    lst_keys_needed = list((set(lst_main_data_keys)-set(lst_sales_data_keys))| (set(lst_sales_data_keys)-set(lst_main_data_keys)))
                    dct_new_keys = {key:"" for key in lst_keys_needed}
                    for dct_data in lst_sale_data_imei:
                         dct_data.update(dct_new_keys)
                    # import pdb;pdb.set_trace()

                    lst_data.extend(lst_sale_data_imei)
            #------------------------------------------------------------------------------------------
            #-------------------------STOCK TRANSFER --(FROM,TO)------------------------------------------------------------------------
            str_stk_trnsfr_query ="""select {selected},br_data.vchr_type from (select 0 as int_transit, stid.int_qty as int_qty,CASE WHEN stid.jsn_imei ->>'imei' ='[]' then NULL else (stid.jsn_imei->>'imei') END  as jsn_imei,
                                    CASE WHEN stid.jsn_batch_no ->>'batch' ='[]' then NULL else  (ist.jsn_batch_no->>'batch')::TEXT END as jsn_batch_no,
                                    NULL as dat_branch_stock,NULL as int_branch_age,grm.dat_purchase as dat_purchase_stock, (NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age ,
                                    (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                    (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                    (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                    (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                    (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                    (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'TRANSFERRED' as vchr_type,
                                    it.dbl_mrp as dbl_mrp,it.dbl_mop as dbl_mop,it.dbl_dealer_cost as dbl_dp,it.dbl_supplier_cost as dbl_cost_price
                                from stock_transfer_imei_details stid
                                join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                                join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                                join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                                join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                                join branch br on br.pk_bint_id = stf.fk_from_id
                                join item it on ist.fk_item_id = it.pk_bint_id
                                join brands bd on bd.pk_bint_id =it.fk_brand_id
                                join products pd on pd.pk_bint_id = it.fk_product_id
                                join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                                join item_category itc on itc.pk_bint_id = it.fk_item_category_id
                                where stf.int_status in (1)
                            UNION ALL
                            select 0 as int_transit, stid.int_qty as int_qty,CASE WHEN stid.jsn_imei ->>'imei' ='[]' then NULL else (stid.jsn_imei->>'imei') END  as jsn_imei,
                                    CASE WHEN stid.jsn_batch_no ->>'batch' ='[]' then NULL else  (ist.jsn_batch_no->>'batch')::TEXT END as jsn_batch_no,
                                    NULL as dat_branch_stock,NULL as int_branch_age,grm.dat_purchase as dat_purchase_stock, (NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age ,
                                    (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                    (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                    (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                    (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                    (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                    (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'RECIEVED' as vchr_type,
                                    it.dbl_mrp as dbl_mrp,it.dbl_mop as dbl_mop,it.dbl_dealer_cost as dbl_dp,it.dbl_supplier_cost as dbl_cost_price
                                from stock_transfer_imei_details stid
                                join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                                join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                                join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                                join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                                join branch br on br.pk_bint_id = stf.fk_to_id
                                join item it on ist.fk_item_id = it.pk_bint_id
                                join brands bd on bd.pk_bint_id =it.fk_brand_id
                                join products pd on pd.pk_bint_id = it.fk_product_id
                                join item_group itg on itg.pk_bint_id = it.fk_item_group_id
                                join item_category itc on itc.pk_bint_id = it.fk_item_category_id
                                where stf.int_status in (3)) as br_data WHERE br_data.dat_stock > '"""+ str(dat_stock)+"""'"""
            lst_group_by.append('br_data.vchr_type')
            lst_selected.append('br_data.vchr_type')
            str_stk_trnsfr_query = str_stk_trnsfr_query + '{filter} group by {group_by} '
            str_stk_trnsfr_query = str_stk_trnsfr_query.format(selected = ','.join(set(lst_selected)),filter = str_filter,group_by = ','.join(set(lst_group_by)))
            #
            rst_stock_transfer_data = conn.execute(str_stk_trnsfr_query).fetchall()

            lst_stk_TRANSFERRED =[]
            lst_stf_TRANSFERRED_imei =[]
            lst_stf_RECIEVED_imei = []
            if rst_stock_transfer_data:
                lst_dict_stock_transfer_data = [dict(x) for x in rst_stock_transfer_data]
                lst_stock_transfer_keys = list(lst_dict_stock_transfer_data[0].keys())
                lst_stock_transfer_keys.remove('int_qty')
                lst_stock_transfer_keys.remove('int_transit')
                lst_stock_transfer_keys.remove('vchr_type')
                lst_stk_TRANSFERRED = [x for x in lst_dict_stock_transfer_data if x['vchr_type'] == 'TRANSFERRED']
                lst_stk_RECIEVED =  [x for x in lst_dict_stock_transfer_data if x['vchr_type'] == 'RECIEVED']
                lst_stf_TRANSFERRED_imei =[]
                lst_stf_RECIEVED_imei = []
                if 'jsn_imei' in lst_stock_transfer_keys:
                    lst_stk_TRANSFERRED =[]
            #-------------------------------------------------------------------
            #-------------------------STOCK TRANSFER------------------------------------------
                if 'jsn_imei' in lst_stock_transfer_keys:
                    for  dct_stf_data in lst_dict_stock_transfer_data:
                        if  dct_stf_data['vchr_type']=='TRANSFERRED':
                            if dct_stf_data['jsn_imei']:
                                lst_imei =  copy.deepcopy(eval(dct_stf_data['jsn_imei']))
                                # #
                                if type(lst_imei) != list:
                                    continue
                                if lst_imei[0] == [] or lst_imei[0] == ''  :
                                    continue


                                for imei in lst_imei:
                                    dct_stf_temp= {}
                                    dct_stf_temp = dct_stf_data.copy()
                                    dct_stf_temp['jsn_imei'] = imei
                                    dct_stf_temp['int_qty'] = 1
                                    dct_stf_temp['int_transit'] = 0

                                    dct_sale_temp['int_qty_transit_sum']=dct_sale_temp['int_qty'] + dct_sale_temp['int_transit']


                                    if 'vchr_type' in dct_stf_data.keys():
                                        dct_stf_temp.pop('vchr_type')
                                    lst_stf_TRANSFERRED_imei.append(dct_stf_temp.copy())
                            elif dct_stf_data['jsn_batch_no']:
                                for dct_stk_data in lst_data:
                                    if dct_stf_data['jsn_batch_no'] == dct_stk_data['jsn_batch_no']:
                                        dct_stk_data['int_qty'] += dct_stf_data['int_qty']

                                        dct_stk_data['int_qty_transit_sum']+=dct_stf_data['int_qty']

                        elif dct_stf_data['vchr_type']=='RECIEVED':

                            if dct_stf_data['jsn_imei']:
                                lst_imei =  copy.deepcopy(eval(dct_stf_data['jsn_imei']))
                                for imei in lst_imei:
                                    dct_stf_temp = {}
                                    dct_stf_temp = dct_stf_data.copy()
                                    dct_stf_temp['jsn_imei'] = imei
                                    dct_stf_temp['int_qty'] = 1
                                    dct_stf_temp['int_transit'] = 0

                                    dct_sale_temp['int_qty_transit_sum']=dct_sale_temp['int_qty'] + dct_sale_temp['int_transit']

                                    if 'vchr_type' in dct_stf_temp.keys():
                                        dct_stf_temp.pop('vchr_type')
                                    lst_stf_RECIEVED_imei.append(dct_stf_temp.copy())
                            elif dct_stf_data['jsn_batch_no']:
                                for dct_stk_data in lst_data:
                                    if dct_stf_data['jsn_batch_no'] == dct_stk_data['jsn_batch_no']:
                                        dct_stk_data['int_qty'] -= dct_stf_data['int_qty']
                                        # import pdb;pdb.set_trace()
                                        dct_stk_data['int_qty_transit_sum']-=dct_stf_data['int_qty']

                #with out imei
                else:
                    for  dct_stf_data in lst_dict_stock_transfer_data:

                        for dct_stk_data in lst_data:
                            if dct_stf_data['vchr_type']=='TRANSFERRED':
                                dct_temp_stock_data = {}
                                dct_temp_stf_data = {}
                                for key in lst_stock_transfer_keys:
                                    dct_temp_stock_data[key] = dct_stk_data[key]
                                    dct_temp_stf_data[key] = dct_stf_data[key]
                                if dct_temp_stock_data==dct_temp_stf_data:
                                    dct_stk_data['int_qty'] += dct_stf_data['int_qty']

                                    dct_stk_data['int_qty_transit_sum']+=dct_stf_data['int_qty']

                                    if dct_stf_data in lst_stk_TRANSFERRED:
                                        lst_stk_TRANSFERRED.remove(dct_stf_data)



                            elif dct_stf_data['vchr_type']=='RECIEVED':
                                dct_temp_stock_data = {}
                                dct_temp_stf_data = {}
                                for key in lst_stock_transfer_keys:
                                    dct_temp_stock_data[key] = dct_stk_data[key]
                                    dct_temp_stf_data[key] = dct_stf_data[key]
                                if dct_temp_stock_data==dct_temp_stf_data:
                                    dct_stk_data['int_qty'] -= dct_stf_data['int_qty']
                                    # #
                                    dct_stk_data['int_qty_transit_sum']-=dct_stf_data['int_qty']









            #---------------------------------------------------------------------------
            if  lst_stk_TRANSFERRED :
                lst_data.extend(lst_stk_TRANSFERRED)
                pass

            if lst_stf_TRANSFERRED_imei:
                lst_data.extend(lst_stf_TRANSFERRED_imei)
                pass
            if lst_stf_RECIEVED_imei:
                for dct_data_recieved_imei in lst_stf_RECIEVED_imei:
                    for dct_stock in lst_data:
                        if dct_data in lst_data:
                            #need to check
                            lst_data.remove(dct_data)
            lst_saleable=[]
            if 'Imei' in lst_more_filter and request.data.get('int_saleable') in [1,2]:
                for data in lst_data:
                     if request.data.get('int_saleable') == 1:

                         if data.get('jsn_imei') in dct_imeis:
                             lst_saleable.append(data)
                     elif request.data.get('int_saleable') == 2:
                         if data.get('jsn_imei') not in dct_imeis:
                             lst_saleable.append(data)
                lst_data=lst_saleable



            if bln_check:
                if request.data.get('blnExport'):
                    data = stock_export_excel(lst_data,request,dct_export_filter)
                    return Response({'status':1,'dct_data':dct_details,'export_data':data,'bln_branch':bln_branch,'dct_price_perm_data':dct_price_perm_dat})
                return Response({'status':1,'dct_data':dct_details,'bln_branch':bln_branch,'dct_price_perm_data':dct_price_perm_dat})
            if request.data.get('blnExport'):
                data = stock_export_excel(lst_data,request,dct_export_filter,bln_branch)
                return Response({'status':1,'dct_data':dct_details,'stock_data':lst_data,'export_data':data,'bln_branch':bln_branch,'dct_price_perm_data':dct_price_perm_dat})
            #
            return Response({'status':1,'stock_data':lst_data})
        except Exception as msg:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(msg, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})

            return Response({'status':0,'data':str(msg)})

def stock_export_excel(lst_data,request,dct_export_filter,bln_branch):
    try:
        sheet_name1 = 'Sheet1'

        # Create a Pandas dataframe from some data.

        # if request.data.get('export') =='BRANCH' or request.data.get('blnExcessStock'):
        #     df['Branch'] = df['branch']
        #     del df['branch']
        dct_data_selected = OrderedDict({
                            'Branch':'vchr_branch_name',
                            'Product':'vchr_product_name',
                            'Brand': 'vchr_brand_name',
                            'Item Category': 'vchr_item_cat_name',
                            'Item Group': 'vchr_item_group_name',
                            'Item Code': 'vchr_item_code',
                            'Item Name': 'vchr_item_name',
                            'Imei/Batch No': 'jsn_imei',
                            'Stock': 'int_qty',
                            'Branch Date': 'dat_branch_stock',
                            'First in Date': 'dat_purchase_stock',
                            'In Transit': 'int_transit',
                            'Branch Age': 'int_branch_age',
                            'Total Age': 'int_total_age',
                            'Total': 'int_qty_transit_sum',
                            'MRP' :'dbl_mrp',
                            'MOP' :'dbl_mop',
                            'Dealer Price':'dbl_dp',
                            'Cost Price':'dbl_cost_price'
                             })

        lst_order = ['Branch','Product','Brand','Item Category','Item Group','Item Code','Item Name','Imei/Batch No','MRP', 'MOP', 'Dealer Price', 'Cost Price', 'Branch Date','First in Date','Stock','In Transit','Branch Age','Total Age','Total']
        lst_keys = lst_data[0].keys()
        lst_headers  = [x for x in lst_order if dct_data_selected.get(x) in  lst_keys]
        # lst_selected = [dct_data_selected.get(x) for x in lst_data[0].keys() if dct_data_selected.get(x) ]
        # lst_index = [x for x in lst_order if x in lst_selected]

        # df = pd.DataFrame(lst_data)
        df = pd.DataFrame(lst_data)
        str_dat_now=datetime.strftime(datetime.now(),'%d-%m-%Y_%H:%M:%S')
        excel_file = settings.MEDIA_ROOT+'/Branch_stock_report_'+str_dat_now+'.xlsx'
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

        df['S.No'] = list(range(1,len(df.index)+1))
        if 'int_item_id' in  lst_keys:
            del df['int_item_id']

        if 'vchr_type' in  lst_keys:
            del df['vchr_type']
        # if 'jsn_batch_no' in  lst_keys:
        #     del df['jsn_batch_no']
        for vchr_headers in lst_headers:
            df[vchr_headers] = df[dct_data_selected.get(vchr_headers)]
            del df[dct_data_selected.get(vchr_headers)]

        if 'Imei/Batch No' in  lst_headers:
            df['Imei/Batch No'] = df['Imei/Batch No'].fillna(df['jsn_batch_no'])
            del df['jsn_batch_no']
        # for vchr_header in lst_selected:
        #     df[vchr_header]  =

        # df['Item'] = df['item']
        # del df['item']
        # df['Totat Sale'] = df['total_sale']
        # del df['total_sale']
        # df['Sale per Day'] = df['sale_per_day']
        # del df['sale_per_day']
        # df['Current Stock'] = df['current_stock']
        # del df['current_stock']
        # df['Stock as on Date'] = df['stock_as_on_date']
        # del df['stock_as_on_date']
        # df['Stock in Demand'] = df['stock_in_demand']
        # del df['stock_in_demand']
        # df['Stock Needed'] = df['stock_needed']
        # del df['stock_needed']

        # df.sort_values('Stock Needed').to_excel(writer,index=False, sheet_name=sheet_name1,startrow=6, startcol=0)
        # df['First in Date'] ='15/10/2019'
        # df=df.append(df.sum(numeric_only=True), ignore_index=True)
        # df.loc['Total', 'A']= df['A'].sum()
        # df.loc[len(df), ['S.No','Stock','In Transit','Total']]= ['', '','','']

        df.loc[len(df), ['S.No','Stock','In Transit','Total']]= ['Total', df['Stock'].sum(),df['In Transit'].sum(),df['Total'].sum()]

        df.index = pd.RangeIndex(start=1, stop=df.shape[0]+1, step=1)
        df.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=13, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name1]
        cell_format = workbook.add_format({'bold':True,'align': 'center'})


        merge_format1 = workbook.add_format({
            'bold': 20,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size':23
            })

        merge_format2 = workbook.add_format({
        'bold': 4,
        'border': 1,
        'align': 'left',
        'valign': 'vleft',
        'font_size':12
        })
        merge_format3 = workbook.add_format({
        'bold': 6,
        'border': 1,
        'align': 'left',
        'valign': 'vleft',
        'font_size':16
        })
        for i,width in enumerate(get_col_widths(df)):
            worksheet.set_column(i-1, i-1, width)
        # str_report = 'Stock Needed'
        # if request.data.get('export') =='BRANCH':

        lst_saleable=['Not Saleable','Saleable']
        str_report = 'Branch Stock Report' if request.data.get('int_saleable') not in [1,2] else 'Branch Stock Report - ' + lst_saleable[request.data.get('int_saleable')-1]
        worksheet.merge_range('A1+:S2', str_report, merge_format1)
        worksheet.merge_range('A2+:S3',"",merge_format2)
        worksheet.merge_range('A5+:S4',"REPORT DATE : "+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'),merge_format3)
        worksheet.merge_range('A6+:S5',"",merge_format2)
        lst_all_filters = ['Products','Brands','Item Groups','Item Categories','Items','Branches']
        for str_filter in lst_all_filters  :
            if str_filter not in dct_export_filter.keys():
                dct_export_filter[str_filter] = ['ALL']
        #
        # worksheet.merge_range('A6+:F7',"FILTERS          : " +", ".join(lst_filter),merge_format3)
        worksheet.merge_range('A7+:S7',"PRODUCTS             : " +", ".join(dct_export_filter.get('Products')),merge_format2)
        worksheet.merge_range('A8+:S8',"BRANDS                 : " +", ".join(dct_export_filter.get('Brands')),merge_format2)
        worksheet.merge_range('A9+:S9',"ITEM GROUPS        : " +", ".join(dct_export_filter.get('Item Groups')),merge_format2)
        worksheet.merge_range('A10+:S10',"ITEM CATEGORIES  : " +", ".join(dct_export_filter.get('Item Categories')),merge_format2)
        worksheet.merge_range('A11+:S11',"ITEMS                    : " +", ".join(dct_export_filter.get('Items')),merge_format2)
        if request.user.userdetails.fk_branch.int_type  in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' or bln_branch :
            worksheet.merge_range('A12+:S12',"BRANCHES             : " +", ".join(dct_export_filter.get('Branches')),merge_format2)
        else:
            worksheet.merge_range('A12+:S12',"BRANCH                 : " +request.user.userdetails.fk_branch.vchr_name.upper(),merge_format2)
        worksheet.merge_range('A13+:S13',"",merge_format2)
        # if dct_export_filter:
        #     lst_filter = [str(x[0]) +': ['+",".join(x[1])+']' for x in dct_export_filter.items()]
            # Products
            # Brands
            # Item Groups
            # Item Categories
            # Items
            # Branchs
            # if  'Branchs' in dct_export_filter.keys():
            #     worksheet.merge_range('A6+:F7',"Filters          : " +", ".join(lst_filter),merge_format3)

        # worksheet.protect()
        writer.save()
        # if request.data.get('export') =='BRANCH':
        data = settings.HOSTNAME+'/media/Branch_stock_report_'+str_dat_now+'.xlsx'
        # data = excel_file
        return data
    except Exception as msg:
        # import pdb;pdb.set_trace()
        return Response({'status':0,'data':str(msg)})

def get_col_widths(dataframe):
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]



class ClientOutstandingReport(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            if request.data.get('onLoad') and  request.user.userdetails.fk_group.vchr_name not in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','STAFF']:
                qry_lst_branch=Branch.objects.values('vchr_name','pk_bint_id')
                bln_branch = False
                if request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN':
                    bln_branch = True
                dct_privilege = get_user_privileges(request)
                if dct_privilege:
                    if len( dct_privilege['lst_branches'])>1:
                        bln_branch = True

                lst_for_show=[{'name':data['vchr_name'],'id':data['pk_bint_id']} for data in qry_lst_branch]
                return Response({'status': 1 , 'bln_show_all':True,'branch':lst_for_show,'bln_branch':bln_branch})
            engine = get_engine()
            conn = engine.connect()

            str_query="""select Case WHEN sum(dbl_debit-dbl_credit)<0 THEN ABS(sum(dbl_debit-dbl_credit)) ELSE 0 end AS dbl_credit,Case WHEN sum(dbl_debit-dbl_credit)>0 THEN sum(dbl_debit-dbl_credit) ELSE 0 end AS dbl_debit, UPPER(cd.vchr_name) as vchr_customer_name,UPPER(br.vchr_name) as vchr_branch_name,int_cust_type,Case WHEN int_cust_type=1 THEN 'CO'WHEN int_cust_type=2 THEN 'CR' WHEN int_cust_type=3 THEN 'SEZ' WHEN int_cust_type=4 THEN 'CA'    end AS vchr_cust_type,cd.int_mobile as int_mobile from transaction tr join customer_details cd on tr.int_accounts_id=cd.pk_bint_id join branch br on tr.fk_branch_id=br.pk_bint_id where int_account_type = 1 {filter} group by vchr_customer_name,vchr_branch_name,int_cust_type,int_mobile order by vchr_branch_name;"""
            lst_filter=[]
            # Transaction.objects.filter(int_account_type = 1,**dct_filter).extra()
            # if request.user.userdetails.fk_group.vchr_name in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
            if request.user.userdetails.fk_group.vchr_name in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                lst_filter.append('fk_branch_id='+str(request.user.userdetails.fk_branch_id))
                lst_branch=Branch.objects.filter(pk_bint_id=request.user.userdetails.fk_branch_id).values_list('vchr_name',flat=True)

            elif request.data.get('lstBranchId'):
                lst_branch=Branch.objects.filter(pk_bint_id__in=request.data.get('lstBranchId')).values_list('vchr_name',flat=True)
                lst_filter.append('fk_branch_id in '+str(request.data.get('lstBranchId')).replace('[','(').replace(']',')'))
            else:
                lst_branch=['All']
            if request.data.get('intCustType') and request.data.get('intCustType')!=-3:

                lst_filter.append('int_cust_type = '+str(request.data.get('intCustType')))
            if request.data.get('datAsOn'):
                str_dat_as_on=str(request.data.get('datAsOn').split('T')[0])
                lst_filter.append("dat_created::DATE <= '"+str_dat_as_on+"'")
            if request.data.get('intMobileNo'):

                lst_filter.append('cd.int_mobile = '+str(request.data.get('intMobileNo')))

            lst_filter[0]='AND '+lst_filter[0]
            str_query = str_query.format(filter = ' AND '.join(lst_filter))

            rst_data = conn.execute(str_query).fetchall()

            lst_data=[]
            int_credit_total=0
            int_debit_total=0
            for data in rst_data:
                dct_data={}
                if data[0] or data[1]:
                    dct_data['dbl_credit']=round(data[0],2)
                    int_credit_total +=data[0]
                    dct_data['dbl_debit']=round(data[1],2)
                    int_debit_total+=data[1]
                    dct_data['vchr_customer_name']=str(data[6] or '')+" - "+(data[2] or '') + " ("+(data[5] or '')+")"
                    dct_data['vchr_branch_name']=data[3]

                    lst_data.append(dct_data)

            if not lst_data:
                return Response({'status':0,'reason':'No Data'})


            int_balance_amount=round(int_debit_total-int_credit_total,2)
            int_credit=0
            int_debit=0
            if int_balance_amount<=0:
                int_credit=abs(int_balance_amount)
            if int_balance_amount>=0:
                int_debit=int_balance_amount



            if request.data.get('blnExport'):

                sheet_name1 = 'Sheet1'

                str_dat_as_on=datetime.strftime(datetime.strptime(str_dat_as_on,'%Y-%m-%d'),'%d-%m-%Y')
                str_dat_today=datetime.strftime(datetime.today().date(),'%d-%m-%Y')

                df = pd.DataFrame(lst_data)

                lst_headers_order =['CUSTOMER NAME','BRANCH NAME','DEBIT','CREDIT']

                dct_data_selected={'CUSTOMER NAME':'vchr_customer_name','CREDIT':'dbl_credit','DEBIT': 'dbl_debit','BRANCH NAME':'vchr_branch_name'}
                for vchr_headers in lst_headers_order:
                    df[vchr_headers] = df[dct_data_selected.get(vchr_headers)]
                    del df[dct_data_selected.get(vchr_headers)]

                # df.loc[len(df), ['CUSTOMER NAME','DEBIT','CREDIT']]= ['', '','']
                df.loc[len(df), ['CUSTOMER NAME','DEBIT','CREDIT']]= [' ',' ',' ']

                df.loc[len(df), ['CUSTOMER NAME','DEBIT','CREDIT']]= ['Total',int_debit,int_credit]


                excel_file = settings.MEDIA_ROOT+'/client_outstanding.xlsx'
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

                df.index = pd.RangeIndex(start=1, stop=df.shape[0]+1, step=1)
                df.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=13, startcol=0)

                workbook = writer.book
                worksheet = writer.sheets[sheet_name1]

                merge_format1 = workbook.add_format({
                    'bold': 20,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size':23
                    })

                merge_format2 = workbook.add_format({
                'bold': 4,
                'border': 1,
                'align': 'left',
                'valign': 'vleft',
                'font_size':12
                })
                merge_format3 = workbook.add_format({
                'bold': 6,
                'border': 1,
                'align': 'left',
                'valign': 'vleft',
                'font_size':16
                })

                str_report = 'Client Outstanding Report'
                worksheet.merge_range('A1+:D2', str_report, merge_format1)

                # worksheet.merge_range('A2+:B2',"",merge_format2)
                worksheet.merge_range('A7+:B7',"AS ON DATE : "+str_dat_as_on,merge_format2)
                worksheet.merge_range('C7+:D7',"REPORT DATE : "+str_dat_today,merge_format2)

                # worksheet.merge_range('A6+:D5',"",merge_format2)
                worksheet.merge_range('A8+:B8',"BRANCHES             : " +", ".join(lst_branch),merge_format2)
                worksheet.merge_range('C8+:D8',"TAKEN BY             : " +request.user.userdetails.first_name.title()+' '+request.user.userdetails.last_name.title(),merge_format2)

                # worksheet.merge_range('A8+:S7',"",merge_format2)
                # import pdb;pdb.set_trace()
                for i,width in enumerate(get_col_widths(df)):
                    worksheet.set_column(i-1, i-1, width)
                # worksheet.set_column(0, 0, 50)
                worksheet.set_column(1, 1, 25)
                #
                worksheet.set_column(2, 2, 20)
                worksheet.set_column(3, 3, 20)

                writer.save()
                return Response({'status':1,'int_credit_total':int_credit,'int_debit_total':int_debit,'export': settings.HOSTNAME+'/media/client_outstanding.xlsx'})

                # return Response({'status':1,'data':lst_data,'int_credit_total':int_credit_total,'int_debit_total':int_debit_total,'export': settings.HOSTNAME+'/media/client_statement.xlsx'})
            return Response({'status':1,'data':lst_data,'int_credit_total':int_credit,'int_debit_total':int_debit})
        except Exception as msg:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(msg, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(msg)})


class DetailedSalesReport(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    def get(self,request):
        try:
            cur.execute("SELECT pk_bint_id,vchr_name FROM branch order by vchr_name;")
            branch = cur.fetchall()
            lst_branch = []
            for data in branch:
                dct_branch = {}
                dct_branch["Name"] = data['vchr_name'].upper()
                dct_branch["Id"] = data['pk_bint_id']
                lst_branch.append(dct_branch)
            bln_branch = False
            if request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN':
                bln_branch = True
            dct_privilege = get_user_privileges(request)
            if dct_privilege:
                if len( dct_privilege['lst_branches'])>1:
                    bln_branch = True



            return Response({"status":1,"data":lst_branch,'bln_branch':bln_branch})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0,"data":"Oops.... Something Went Wrong!!...."})

    def post(self,request):
        # {"datFrom":"2019-07-01", "datTo":"2020-07-01","lstBranch":[2,3]}
        try:
            dat_date_from = request.data.get('datFrom') or datetime.strftime(datetime.now(),'%Y-%m-%d')
            dat_date_to = request.data.get('datTo') or datetime.strftime(datetime.now(),'%Y-%m-%d')
            lst_branches = request.data.get('lstBranch') or []
            str_filter = ""
            dct_privilege = get_user_privileges(request)
            lst_branches_id = []

            #------------------------------------------------------------------------------------------------------------------------------
            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN'):
                if request.user.userdetails.fk_group.vchr_name.upper() in ["BRANCH MANAGER","ASSISTANT BRANCH MANAGER","ASM1","ASM2","ASM3","ASM4"]:
                    lst_branches_id = [request.user.userdetails.fk_branch_id]
                    str_filter += "and b.pk_bint_id in ("+str(lst_branches_id)[1:-1]+") "
                elif dct_privilege:
                    if dct_privilege.get('lst_branches'):
                        lst_branches_id = dct_privilege['lst_branches']
                        str_filter += "and b.pk_bint_id in ("+str(lst_branches_id)[1:-1]+") "
                    else:
                        lst_branches_id = [request.user.userdetails.fk_branch_id]
                        str_filter += "and b.pk_bint_id in ("+str(lst_branches_id)[1:-1]+") "

                    if dct_privilege.get('lst_products'):

                        str_filter += "AND prd.pk_bint_id in ("+str(dct_privilege['lst_products'])[1:-1]+") "

                else:
                    lst_branches_id = [request.user.userdetails.fk_branch_id]
                    str_filter += "and b.pk_bint_id in ("+str(lst_branches_id)[1:-1]+")"


            if lst_branches:
                str_filter += " and b.pk_bint_id in ("+str(lst_branches)[1:-1]+")"
            int_cust_id=request.data.get('intCustomerId')
            int_staff_id=request.data.get('intStaffId')
            # Filters
            lst_more_filter=[]
            """CUSTOMER WISE"""
            if int_cust_id:

                str_filter += "AND sm.fk_customer_id = "+str(int_cust_id)+" "

            """STAFF WISE"""
            if int_staff_id:
                str_filter += "AND sm.fk_staff_id = "+str(int_staff_id)+" "


            if request.data.get('lstProduct'):
                str_filter +=  ' AND it.fk_product_id in ' +str(request.data.get('lstProduct')).replace('[','(').replace(']',')')
            if request.data.get("lstBrand"):
                str_filter +=  ' AND it.fk_brand_id in ' +str(request.data.get('lstBrand')).replace('[','(').replace(']',')')

            if request.data.get("lstItemCategory"):

                str_filter +=  ' AND it.fk_item_category_id in ' +str(request.data.get('lstItemCategory')).replace('[','(').replace(']',')')


            if request.data.get("lstItemGroup"):
                str_filter +=  ' AND it.fk_item_group_id in ' +str(request.data.get('lstItemGroup')).replace('[','(').replace(']',')')

            if request.data.get("lstItem"):
                str_filter +=  ' AND sd.fk_item_id in ' +str(request.data.get('lstItem')).replace('[','(').replace(']',')')

            if request.data.get("bln_smart_choice"):

                str_filter += "and it.fk_product_id !=(select pk_bint_id from products where vchr_name ilike 'smart choice') "

            if request.data.get("bln_service"):
                str_filter += "and sd.fk_master_id not in ( select sales_master.pk_bint_id from sales_master join sales_details on fk_master_id=sales_master.pk_bint_id where int_sales_status=3 and dat_invoice:: DATE BETWEEN '"+str(dat_date_from)+"' AND '"+str(dat_date_to)+"') "

            # Filters
            #------------------------------------------------------------------------------------------------------------------------------
            # #


            # str_query = "SELECT date, time, invoice_number, branch, customer_name, customer_mobile, STRING_AGG(fin.vchr_name,',') as financier, ROUND(SUM(CASE WHEN pd.int_fop = 0 THEN pd.dbl_finance_amt ELSE 0 END)::NUMERIC,2) as finance, ROUND(SUM(CASE WHEN pd.int_fop = 1 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as cash, ROUND(SUM(CASE WHEN pd.int_fop = 2 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as debit_card, ROUND(SUM(CASE WHEN pd.int_fop = 3 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as credit_card, ROUND(SUM(CASE WHEN pd.int_fop = 4 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as receipt, ROUND(SUM(CASE WHEN pd.int_fop = 7 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as bharath_qr, approved_credit, emi, customer_type, CASE WHEN val.total_value < 0 THEN (val.total_value + val.indirect_discount) ELSE val.total_value END AS total_value, exchange, discount, indirect_discount, buyback, addition, deduction FROM(SELECT sm.pk_bint_id as pk_bint_id, sm.dat_created::DATE AS date, sm.dat_created::Time as time, sm.vchr_invoice_num AS invoice_number, b.vchr_name AS branch, UPPER(scustd.vchr_name) as customer_name, scustd.int_mobile as customer_mobile, CASE WHEN pi.json_updated_data is not null then pi.json_updated_data::jsonb->>'dbl_balance_amt'||'.00' ELSE '0.00' END as approved_credit, CASE WHEN pi.json_data is not null then pi.json_data::jsonb->>'vchr_finance_schema' ELSE '' END as emi, CASE WHEN scustd.int_cust_type = 1 THEN 'Corporate Customer' WHEN scustd.int_cust_type = 2 THEN 'Credit Customer' WHEN scustd.int_cust_type = 3 THEN 'Sez Customer' WHEN scustd.int_cust_type = 4 THEN 'Cash Customer' ELSE 'Cash Customer' END as customer_type, CASE WHEN sm.dbl_total_amt is not null THEN ROUND(sm.dbl_total_amt::NUMERIC,2) ELSE (ROUND(SUM(sd.dbl_amount)::NUMERIC,2)) END as total_value, ROUND(SUM(CASE WHEN sd.int_sales_status = 2 THEN sd.dbl_amount ELSE 0 END)::NUMERIC,2) as exchange, ROUND(sm.dbl_discount::NUMERIC,2) as discount, ROUND(SUM(CASE WHEN sd.dbl_indirect_discount is not null THEN sd.dbl_indirect_discount ELSE 0 END)::NUMERIC,2) as indirect_discount, ROUND(SUM(Sd.dbl_buyback)::NUMERIC,2)  as buyback, sm.jsn_addition  as addition, sm.jsn_deduction  as deduction FROM sales_details sd JOIN sales_master sm ON sd.fk_master_id = sm.pk_bint_id LEFT JOIN branch b ON b.pk_bint_id = sm.fk_branch_id LEFT JOIN item it ON it.pk_bint_id = sd.fk_item_id LEFT JOIN products prd ON prd.pk_bint_id = it.fk_product_id LEFT JOIN brands brd ON brd.pk_bint_id = it.fk_brand_id LEFT JOIN sales_customer_details scustd ON scustd.pk_bint_id = sm.fk_customer_id LEFT JOIN customer_details custd ON custd.pk_bint_id =  scustd.fk_customer_id LEFT JOIN partial_invoice pi ON pi.fk_invoice_id = sm.pk_bint_id WHERE sm.dat_created::DATE BETWEEN '"+dat_date_from+"' and '"+dat_date_to+"'"+str_filter+" GROUP BY sm.pk_bint_id,sm.dat_created,sm.vchr_invoice_num,b.vchr_name,scustd.vchr_name,scustd.int_mobile,pi.json_updated_data,pi.json_data,scustd.int_cust_type,sm.dbl_total_amt,sm.dbl_discount,sm.jsn_addition,sm.jsn_deduction) AS val LEFT JOIN payment_details pd ON val.pk_bint_id = pd.fk_sales_master_id LEFT JOIN (select vchr_name,vchr_code from financiers where bln_active = 't') AS fin ON fin.vchr_code = pd.vchr_name GROUP BY date,time,invoice_number,branch,customer_name,customer_mobile,approved_credit,emi,customer_type,total_value,exchange,discount,indirect_discount,buyback,addition,deduction ORDER BY invoice_number;"

            str_query = """SELECT
                date,
                time,
                invoice_number,
                branch,
                staff,
                customer_name,
                customer_mobile,
                STRING_AGG(CASE WHEN fin.vchr_name IS NOT NULL AND fin_name != 'BAJAJ ONLINE,!' THEN fin.vchr_name ELSE fin_name END,',!') as financier,
                ROUND(SUM(CASE WHEN pd.int_fop = 0 THEN pd.dbl_finance_amt ELSE 0 END)::NUMERIC,2) as finance,
                ROUND(SUM(CASE WHEN pd.int_fop = 1 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as cash,
                ROUND(SUM(CASE WHEN pd.int_fop = 2 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as debit_card,
                ROUND(SUM(CASE WHEN pd.int_fop = 3 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as credit_card,
                ROUND(SUM(CASE WHEN pd.int_fop = 4 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as receipt,
                ROUND(SUM(CASE WHEN pd.int_fop = 7 THEN pd.dbl_receved_amt ELSE 0 END)::NUMERIC,2) as bharath_qr,
                approved_credit,
                STRING_AGG(CASE WHEN pd.vchr_finance_schema is not null THEN pd.vchr_finance_schema ELSE emi END,',') as emi,
                customer_type,
                -- CASE WHEN val.total_value < 0 THEN (val.total_value + val.indirect_discount) ELSE val.total_value END AS total_value,
                total_value,
                exchange,
                discount,
                indirect_discount,
                buyback,
                addition,
                deduction,
                delivery_order_num
                FROM(SELECT
                    sm.pk_bint_id as pk_bint_id,
                    sm.dat_created::DATE AS date,
                    sm.dat_created::Time as time,
                    sm.vchr_invoice_num AS invoice_number,
                    au.first_name || ' ' || au.last_name as staff,
                    b.vchr_name AS branch,
                    UPPER(scustd.vchr_name) as customer_name,
                    scustd.int_mobile as customer_mobile,
                    CASE
                        WHEN sm.int_sale_type = 1 THEN 'BAJAJ ONLINE,!'
                        WHEN sm.int_sale_type = 2 THEN 'AMAZON'
                        WHEN sm.int_sale_type = 3 THEN 'FLIPKART'
                        WHEN sm.int_sale_type = 4 THEN 'E-COMMERCE'
                        ELSE CASE WHEN pi.json_data::jsonb->>'vchr_finance_name' IS NOT NULL THEN pi.json_data::jsonb->>'vchr_finance_name' ELSE '' END
                    END as fin_name,
                    CASE WHEN pi.json_updated_data is not null then pi.json_updated_data::jsonb->>'dbl_balance_amt'||'.00' ELSE '0.00' END as approved_credit,
                    CASE WHEN pi.json_data is not null then pi.json_data::jsonb->>'vchr_finance_schema' ELSE '' END as emi,
                    CASE WHEN scustd.int_cust_type = 1 THEN 'Corporate Customer'
                        WHEN scustd.int_cust_type = 2 THEN 'Credit Customer'
                        WHEN scustd.int_cust_type = 3 THEN 'Sez Customer'
                        WHEN scustd.int_cust_type = 4 THEN 'Cash Customer'
                        ELSE 'Cash Customer'
                    END as customer_type,
                    SUM(sd.dbl_selling_price)::NUMERIC AS total_value,
                    -- CASE WHEN sm.dbl_total_amt is not null THEN ROUND(sm.dbl_total_amt::NUMERIC,2) ELSE (ROUND(SUM(sd.dbl_selling_price)::NUMERIC,2)) END as total_value,
                    -- CASE WHEN sm.dbl_total_amt is not null THEN ROUND(sm.dbl_total_amt::NUMERIC,2) ELSE (ROUND(SUM(sd.dbl_amount)::NUMERIC,2)) END as total_value,
                    ROUND(SUM(CASE WHEN sd.int_sales_status = 2 THEN sd.dbl_selling_price ELSE 0 END)::NUMERIC,2) as exchange,
                    ROUND(sm.dbl_discount::NUMERIC,2) as discount,
                    ROUND(SUM(CASE WHEN sd.dbl_indirect_discount is not null THEN sd.dbl_indirect_discount ELSE 0 END)::NUMERIC,2) as indirect_discount,
                    ROUND(SUM(Sd.dbl_buyback)::NUMERIC,2)  as buyback,
                    sm.jsn_addition  as addition,
                    sm.jsn_deduction  as deduction,
                    pi.json_data::jsonb->'vchr_fin_ordr_num' as delivery_order_num
                    FROM sales_details sd
                        JOIN sales_master sm ON sd.fk_master_id = sm.pk_bint_id
                        LEFT JOIN branch b ON b.pk_bint_id = sm.fk_branch_id
                        LEFT JOIN item it ON it.pk_bint_id = sd.fk_item_id
                        LEFT JOIN products prd ON prd.pk_bint_id = it.fk_product_id
                        LEFT JOIN brands brd ON brd.pk_bint_id = it.fk_brand_id
                        LEFT JOIN sales_customer_details scustd ON scustd.pk_bint_id = sm.fk_customer_id
                        LEFT JOIN customer_details custd ON custd.pk_bint_id =  scustd.fk_customer_id
                        LEFT JOIN partial_invoice pi ON pi.fk_invoice_id = sm.pk_bint_id
                        LEFT JOIN auth_user au on au.id = sm.fk_staff_id
                    WHERE sm.dat_created::DATE BETWEEN '"""+dat_date_from+"""' and '"""+dat_date_to+"""'"""+str_filter+"""
                    GROUP BY sm.pk_bint_id,sm.dat_created,sm.vchr_invoice_num,au.first_name,au.last_name,b.vchr_name,scustd.vchr_name,scustd.int_mobile,pi.json_updated_data,pi.json_data,scustd.int_cust_type,sm.dbl_total_amt,sm.dbl_discount,sm.jsn_addition,sm.jsn_deduction) AS val
                    LEFT JOIN payment_details pd ON val.pk_bint_id = pd.fk_sales_master_id
                    LEFT JOIN (select vchr_name,vchr_code from financiers where bln_active = 't') AS fin ON fin.vchr_code = pd.vchr_name
                -- where  deduction::text != '{}'
                GROUP BY date,time,invoice_number,staff,branch,customer_name,customer_mobile,approved_credit,customer_type,total_value,exchange,discount,indirect_discount,buyback,addition,deduction,delivery_order_num
                ORDER BY invoice_number"""


            # I-KNB-2211
            # WHERE sm.dat_created::DATE BETWEEN '"+dat_date_from+"' and '"+dat_date_to+"'"+str_filter+"
            cur.execute(str_query)
            # print(str_query)
            rst_data = cur.fetchall()
            if rst_data:
                try:
                    # import pdb; pdb.set_trace()
                    str_query_add_ded="select pk_bint_id,vchr_category from accounts_map"
                    cur.execute(str_query_add_ded)
                    rst_data_add_ded = cur.fetchall()
                    dct_add_ded = {}
                    if rst_data_add_ded:
                        for data in rst_data_add_ded:
                            dct_add_ded[data['pk_bint_id']] = data['vchr_category']

                    dct_report = {'Slno':[],'Date':[],'Time':[],'Invoice Number':[],'Branch':[],'Staff':[],'Customer Name':[],'Customer Mobile':[],'Financier':[],'Finance':[],'Cash':[],'Debit Card':[],'Credit Card':[],'Advance Receipt':[],'Bharath Qr':[],'Approved Credit':[],'Customer Type':[],'Total Value':[],'Discount':[],'Indirect Discount':[],'Buyback':[],'Addition':[],'Deduction':[],'Exchange':[],'EMI':[], 'Delivery Order No.':[]}
                    i = 1
                    columns=['Slno','Date','Time','Invoice Number','Branch','Staff','Customer Name','Customer Mobile','Financier','Finance','Delivery Order No.','Cash','Debit Card','Credit Card','Advance Receipt','Bharath Qr','Approved Credit','EMI','Customer Type','Total Value','Exchange','Discount','Indirect Discount','Buyback','Addition','Deduction']
                    # import pdb; pdb.set_trace()
                    lst_new_header_add = []
                    lst_new_header_ded = []
                    # total = 0
                    for data in rst_data:
                        # import pdb; pdb.set_trace()
                        sum_addiction = 0
                        sum_deduction = 0
                        add_ded_value = 0

                        lst_add_item = []
                        for key,addiction in data['addition'].items():
                            try:
                                if int(addiction) > 0:
                                    if dct_report.get(dct_add_ded[int(key)]+" (ADDITION)") == None:
                                        dct_report[dct_add_ded[int(key)]+" (ADDITION)"] = []
                                        columns.append(dct_add_ded[int(key)]+" (ADDITION)")
                                        lst_new_header_add.append(dct_add_ded[int(key)]+" (ADDITION)")
                                        len_ = len(dct_report['Branch'])
                                        for i in range(len_):
                                            dct_report[dct_add_ded[int(key)]+" (ADDITION)"].append('0')
                                    dct_report[dct_add_ded[int(key)]+" (ADDITION)"].append(addiction)
                                    lst_add_item.append(dct_add_ded[int(key)]+" (ADDITION)")
                                    sum_addiction += int(addiction)
                            except Exception as e:
                                sum_addiction += 0
                                continue

                        lst_ded_item = []
                        for key,deduction in data['deduction'].items():
                            try:
                                if int(deduction) > 0:
                                    if dct_report.get(dct_add_ded[int(key)]+" (DEDUCTION)") == None:
                                        dct_report[dct_add_ded[int(key)]+" (DEDUCTION)"] = []
                                        columns.append(dct_add_ded[int(key)]+" (DEDUCTION)")
                                        lst_new_header_ded.append(dct_add_ded[int(key)]+" (DEDUCTION)")
                                        len_ = len(dct_report['Branch'])
                                        for i in range(len_):
                                            dct_report[dct_add_ded[int(key)]+" (DEDUCTION)"].append('0')
                                    dct_report[dct_add_ded[int(key)]+" (DEDUCTION)"].append(deduction)
                                    lst_ded_item.append(dct_add_ded[int(key)]+" (DEDUCTION)")
                                    sum_deduction += int(deduction)
                            except Exception as e:
                                sum_deduction += 0
                                continue

                        for header in lst_new_header_ded:
                            if header not in lst_ded_item and dct_report.get(header) != None:
                                dct_report[header].append('0')

                        for header in lst_new_header_add:
                            if header not in lst_add_item and dct_report.get(header) != None:
                                dct_report[header].append('0')
                        # import pdb; pdb.set_trace()
                        emi = ''
                        str_emi = ''
                        emi = set(data['emi'].split(',')) if data['emi'] else ''
                        for emi1 in emi:
                            if emi1 != 'None':
                                str_emi += emi1+','


                        dct_report['Slno'].append(i)
                        dct_report['Date'].append(datetime.strftime(data['date'],'%d-%m-%Y'))
                        dct_report['Time'].append(time.strftime(data['time'],'%I:%M:%S %P'))
                        dct_report['Invoice Number'].append(data['invoice_number'])
                        dct_report['Staff'].append(data['staff'].title())
                        dct_report['Branch'].append(data['branch'])
                        dct_report['Customer Name'].append(data['customer_name'])
                        dct_report['Customer Mobile'].append(data['customer_mobile'])
                        dct_report['Financier'].append(data['financier'].split(',!')[0])
                        dct_report['Finance'].append(data['finance'])
                        dct_report['Cash'].append(data['cash'])
                        dct_report['Debit Card'].append(data['debit_card'])
                        dct_report['Credit Card'].append(data['credit_card'])
                        dct_report['Advance Receipt'].append(data['receipt'])
                        dct_report['Bharath Qr'].append(data['bharath_qr'])
                        dct_report['Approved Credit'].append(data['approved_credit'])
                        dct_report['Customer Type'].append(data['customer_type'])
                        dct_report['Total Value'].append(data['total_value'])
                        dct_report['Exchange'].append(data['exchange'])
                        dct_report['EMI'].append(str_emi[:-1])
                        dct_report['Discount'].append(data['discount'])
                        dct_report['Indirect Discount'].append(data['indirect_discount'])
                        dct_report['Buyback'].append(data['buyback'])
                        dct_report['Addition'].append(sum_addiction)
                        dct_report['Deduction'].append(sum_deduction)
                        dct_report['Delivery Order No.'].append(data.get('delivery_order_num',''))

                        # total += data['total_value']
                        i = i+1


                    # print("sales : ",total)
                    # import pdb; pdb.set_trace()
                    df = pd.DataFrame(dct_report)
                    str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_detailedsailsreport.xlsx'
                    filename =settings.MEDIA_ROOT+'/'+str_file


                    # if(os.path.exists(filename)):
                    #     os.remove(filename)

                    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                    workbook = writer.book
                    cell_format = workbook.add_format()
                    cell_format.set_align('center')
                    cell_format1 = workbook.add_format()
                    cell_format1.set_align('left')
                    df.to_excel(writer,index=False, sheet_name='Detailed Sales Report',columns=columns,startrow=6, startcol=0)
                    worksheet = writer.sheets['Detailed Sales Report']
                    merge_format1 = workbook.add_format({
                        'bold': 20,
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_size':23
                        })

                    merge_format2 = workbook.add_format({
                    'bold': 6,
                    'border': 1,
                    'align': 'left',
                    'valign': 'vleft',
                    'font_size':13
                    })
                    worksheet.merge_range('A1+:S2', 'Detailed Sales Report', merge_format1)
                    worksheet.merge_range('A4+:D4', 'Taken By               :  '+request.user.username, merge_format2)
                    worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)

                    # i=str(i+2)
                    # worksheet.write('F'+i, 'Total:-',cell_format)
                    # worksheet.write('G'+i, sum_soldprice_mrp,cell_format)
                    # worksheet.write('H'+i, sum_dp,cell_format)
                    # worksheet.write('I'+i, sum_servicecahrge,cell_format)
                    # worksheet.write('J'+i, sum_spareprofit,cell_format)
                    # worksheet.write('K'+i, sum_profittax,cell_format)
                    # worksheet.write('L'+i, sum_netprofitonjob,cell_format)

                    worksheet.set_column('B:B', 15,cell_format)
                    worksheet.set_column('C:C', 15,cell_format)
                    worksheet.set_column('D:D', 25,cell_format)
                    worksheet.set_column('E:E', 20,cell_format)
                    worksheet.set_column('F:F', 28,cell_format1)
                    worksheet.set_column('G:G', 28,cell_format1)
                    worksheet.set_column('H:H', 16,cell_format)
                    worksheet.set_column('I:I', 20,cell_format)
                    worksheet.set_column('J:J', 15,cell_format)
                    worksheet.set_column('K:K', 15,cell_format)
                    worksheet.set_column('L:L', 15,cell_format)
                    worksheet.set_column('M:M', 15,cell_format)
                    worksheet.set_column('N:N', 15,cell_format)
                    worksheet.set_column('O:O', 15,cell_format)
                    worksheet.set_column('P:P', 20,cell_format)
                    worksheet.set_column('Q:Q', 15,cell_format)
                    worksheet.set_column('R:R', 15,cell_format)
                    worksheet.set_column('S:S', 14,cell_format)
                    worksheet.set_column('T:T', 15,cell_format)
                    worksheet.set_column('U:U', 15,cell_format)
                    worksheet.set_column('V:V', 15,cell_format)
                    worksheet.set_column('W:W', 15,cell_format)
                    worksheet.set_column('X:X', 15,cell_format)
                    worksheet.set_column('Y:Y', 15,cell_format)
                    worksheet.set_column('Z:Z', 15,cell_format)
                    range_ = len(lst_new_header_add) + len(lst_new_header_ded)
                    A={2:"Z:Z",3:"AA:AA",4:"AB:AB",5:"AC:AC",6:"AD:AD",7:"AE:AE",8:"AF:AF",9:"AG:AG",10:"AH:AH",11:"AI:AI",12:"AJ:AJ",13:"AK:AK",14:"AL:AL",15:"AM:AM",16:"AN:AN",17:"AO:AO",18:"AP:AP",19:"AQ:AQ",20:"AR:AR",21:"AS:AS",22:"AT:AT",23:"AU:AU",24:"AV:AV",25:"AW:AW",26:"AX:AX",27:"AY:AY",28:"AZ:AZ"}
                    for i in range(range_):
                        worksheet.set_column(A[i+3], 15,cell_format)


                    # import pdb; pdb.set_trace()
                    writer.save()
                    return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                except Exception as e:
                    # #
                    return JsonResponse({'status':'0','message':e})
            else:
                return Response({"status":"0", "message":"No Data..."})

        except Exception as e:
            # import pdb; pdb.set_trace()
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":"0", "message":"Some Thing Went Wrong !!..."+str(e)})

def get_branch():
    try:
        cur.execute("SELECT pk_bint_id,vchr_name FROM branch order by vchr_name;")
        branch = cur.fetchall()
        lst_branch = []
        for data in branch:
            dct_branch = {}
            dct_branch["name"] = data['vchr_name'].upper()
            dct_branch["id"] = data['pk_bint_id']
            lst_branch.append(dct_branch)

        # cur.execute("select pk_bint_id,vchr_name from item where vchr_item_code in ('GDC00001','GDC00002');")
        # rst_type = cur.fetchall()
        # lst_type =[]
        # for data in rst_type:
        #     dct_type = {}
        #     dct_type["type"] = data['vchr_name'].upper()
        #     dct_type['id'] = data['pk_bint_id']
        #     lst_type.append(dct_type)

        return {"status":1,"branch":lst_branch}
    except Exception as e:
        return {"status":0,"data":"Oops.... Something Went Wrong!!...."}

class gdotreport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            cur.execute("SELECT pk_bint_id,vchr_name FROM branch order by vchr_name;")
            branch = cur.fetchall()
            lst_branch = []
            for data in branch:
                dct_branch = {}
                dct_branch["name"] = data['vchr_name'].upper()
                dct_branch["id"] = data['pk_bint_id']
                lst_branch.append(dct_branch)


            bln_branch = False
            if request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN':
                bln_branch = True
            dct_privilege = get_user_privileges(request)
            if dct_privilege:
                if len( dct_privilege['lst_branches'])>1:
                    bln_branch = True

            # cur.execute("select pk_bint_id,vchr_name from item where vchr_item_code in ('GDC00001','GDC00002');")
            # rst_type = cur.fetchall()
            # lst_type =[]
            # for data in rst_type:
            #     dct_type = {}
            #     dct_type["type"] = data['vchr_name'].upper()
            #     dct_type['id'] = data['pk_bint_id']
            #     lst_type.append(dct_type)

            return Response({"status":1,"branch":lst_branch,'bln_branch':bln_branch})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0,"data":"Oops.... Something Went Wrong!!...."})

    def post(self,request):
        # {"datFrom":"2020-07-01", "datTo":"2020-07-01","lstBranch":[2,3],"bln_download":True}
        # {"datFrom":"2019-07-01","bln_download":"True"}
        # {"datFrom":"2019-07-01","lstBranch":[64],"type":[2]}
        """keys in
                datFrom
                datTo
                lstBranch
                type

            Keys Ou
                    date
                    branch
                    type
                    discount
                    indirectDiscount
                    tax
                    packageAmount
                    packageProfit
                    netProfit
        """
        try:

            dat_date_from = request.data.get('datFrom',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            lst_branches = request.data.get('lstBranch') or []
            lst_type = request.data.get('lstType',[])
            str_filter = ""

            dct_privilege = get_user_privileges(request)
            lst_branches_prevl = []


            str_type = ""
            # #
            for data in lst_type:
                if data == 1:
                    str_type += "'GDC00001',"
                elif data == 2:
                    str_type += "'GDC00002',"

            if lst_branches and str_type:
                str_filter = "WHERE b.pk_bint_id in ("+str(lst_branches)[1:-1]+") AND itm.vchr_item_code in ("+str_type[:-1]+") "
            elif lst_branches:
                str_filter = "WHERE b.pk_bint_id in ("+str(lst_branches)[1:-1]+") AND itm.vchr_item_code in ('GDC00001','GDC00002') "
            elif str_type:
                str_filter = "WHERE itm.vchr_item_code in ("+str_type[:-1]+") "
            else:
                str_filter = "WHERE itm.vchr_item_code in ('GDC00001','GDC00002') "
            #----------------------USer Privilage-----------------------------------------------------------------------------------------

            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN'):
                if request.user.userdetails.fk_group.vchr_name.upper() in ["BRANCH MANAGER","ASSISTANT BRANCH MANAGER","ASM1","ASM2","ASM3","ASM4"]:
                    lst_branches_prevl = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND b.pk_bint_id in ("+str(lst_branches_prevl)[1:-1]+") "
                elif dct_privilege:
                    if dct_privilege.get('lst_branches'):
                        lst_branches_prevl = dct_privilege['lst_branches']
                        str_filter += "AND b.pk_bint_id in ("+str(lst_branches_prevl)[1:-1]+") "
                    else:
                        lst_branches_prevl = [request.user.userdetails.fk_branch_id]
                        str_filter += "AND b.pk_bint_id in ("+str(lst_branches_prevl)[1:-1]+") "

                    if dct_privilege.get('lst_products'):

                        str_filter += "AND pr.pk_bint_id in ("+str(dct_privilege['lst_products'])[1:-1]+") "


                else :

                    lst_branches_prevl = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND b.pk_bint_id in ("+str(lst_branches_prevl)[1:-1]+") "


            #---------------------------------------------------------------------------------------------------------------

            if request.data.get('bln_download'):
                str_query = "SELECT sd.pk_bint_id, sm.dat_created::DATE AS date, b.vchr_name AS branch, CASE WHEN itm.vchr_item_code = 'GDC00001' THEN 'GDP' WHEN itm.vchr_item_code = 'GDC00002' THEN 'GDEW' END AS vchr_name, ROUND(sd.dbl_discount::NUMERIC) AS discount, ROUND(sd.dbl_indirect_discount::NUMERIC) AS indirect_discount, ROUND(sd.dbl_tax::NUMERIC) AS tax, ROUND((sd.dbl_selling_price + sd.dbl_discount + sd.dbl_buyback)::NUMERIC) AS package_amount, ROUND((((sd.dbl_selling_price + sd.dbl_discount + sd.dbl_buyback)*40)/100)::NUMERIC) AS package_profit, ROUND(((((sd.dbl_selling_price + sd.dbl_discount + sd.dbl_buyback)*40)/100) - (sd.dbl_indirect_discount + sd.dbl_tax + sd.dbl_discount + sd.dbl_buyback))::NUMERIC) AS net_profit FROM sales_details sd JOIN sales_master sm ON sm.pk_bint_id = sd.fk_master_id JOIN branch b ON sm.fk_branch_id = b.pk_bint_id JOIN item itm ON itm.pk_bint_id = sd.fk_item_id join products pr on pr.pk_bint_id=itm.fk_product_id  "+str_filter+" AND sm.dat_created::DATE  between '"+dat_date_from+"' and '"+dat_date_to+"' ORDER BY b.vchr_name;"

                # print(str_query)
                cur.execute(str_query)
                rst_data = cur.fetchall()

                if rst_data:
                    try:
                        count = 0
                        dct_report = {'Slno':[],'Date':[],'Branch':[],'Type':[],'Quantity':[],'Discount':[],'Indirect Discount':[],'Tax':[],'Package Sold Price':[],'Package Profit':[],'Net Profit':[]}
                        for data in rst_data:
                            count += 1
                            dct_report['Slno'].append(count)
                            dct_report['Date'].append(datetime.strftime(data['date'],'%d-%m-%Y'))
                            dct_report['Branch'].append(data['branch'])
                            dct_report['Type'].append(data['vchr_name'])
                            dct_report['Quantity'].append('1')
                            dct_report['Discount'].append(data['discount'])
                            dct_report['Indirect Discount'].append(data['indirect_discount'])
                            dct_report['Tax'].append(data['tax'])
                            dct_report['Package Sold Price'].append(data['package_amount'])
                            dct_report['Package Profit'].append(data['package_profit'])
                            dct_report['Net Profit'].append(data['net_profit'])

                        df = pd.DataFrame(dct_report)
                        str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_gdotsailsprofitreport.xlsx'
                        filename =settings.MEDIA_ROOT+'/'+str_file

                        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                        workbook = writer.book
                        cell_format = workbook.add_format()
                        cell_format.set_align('center')
                        cell_format1 = workbook.add_format()
                        cell_format1.set_align('left')
                        df.to_excel(writer,index=False, sheet_name='GDOT Sales Profit Report',columns=['Slno','Date','Branch','Type','Quantity','Package Sold Price','Package Profit','Discount','Indirect Discount','Tax','Net Profit'],startrow=6, startcol=0)
                        worksheet = writer.sheets['GDOT Sales Profit Report']
                        merge_format1 = workbook.add_format({
                            'bold': 20,
                            'border': 1,
                            'align': 'center',
                            'valign': 'vcenter',
                            'font_size':23
                            })

                        merge_format2 = workbook.add_format({
                        'bold': 6,
                        'border': 1,
                        'align': 'left',
                        'valign': 'vleft',
                        'font_size':13
                        })
                        worksheet.merge_range('A1+:J2', 'GDOT Sales Profit Report', merge_format1)
                        worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
                        worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)

                        worksheet.set_column('B:B', 15,cell_format1)
                        worksheet.set_column('C:C', 15,cell_format1)
                        worksheet.set_column('D:D', 25,cell_format)
                        worksheet.set_column('E:E', 20,cell_format)
                        worksheet.set_column('F:F', 28,cell_format)
                        worksheet.set_column('G:G', 16,cell_format)
                        worksheet.set_column('H:H', 15,cell_format)
                        worksheet.set_column('I:I', 15,cell_format)
                        worksheet.set_column('J:J', 15,cell_format)
                        writer.save()
                        return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                    except Exception as e:
                        return JsonResponse({'status':'0','data':e})


            str_query = "SELECT sd.pk_bint_id, sm.dat_created::DATE AS date, b.vchr_name AS branch, CASE WHEN itm.vchr_item_code = 'GDC00001' THEN 'GDP' WHEN itm.vchr_item_code = 'GDC00002' THEN 'GDEW' END AS vchr_name, ROUND(sd.dbl_discount::NUMERIC) AS discount, ROUND(sd.dbl_indirect_discount::NUMERIC) AS indirect_discount, ROUND(sd.dbl_tax::NUMERIC) AS tax, ROUND((sd.dbl_selling_price + sd.dbl_discount + sd.dbl_buyback)::NUMERIC) AS package_amount, ROUND((((sd.dbl_selling_price + sd.dbl_discount + sd.dbl_buyback)*40)/100)::NUMERIC) AS package_profit, ROUND(((((sd.dbl_selling_price + sd.dbl_discount + sd.dbl_buyback)*40)/100) - (sd.dbl_indirect_discount + sd.dbl_tax + sd.dbl_discount + sd.dbl_buyback))::NUMERIC) AS net_profit FROM sales_details sd JOIN sales_master sm ON sm.pk_bint_id = sd.fk_master_id JOIN branch b ON sm.fk_branch_id = b.pk_bint_id JOIN item itm ON itm.pk_bint_id = sd.fk_item_id  join products pr on pr.pk_bint_id=itm.fk_product_id  "+str_filter+" AND sm.dat_created::DATE  between '"+dat_date_from+"' and '"+dat_date_to+"' ORDER BY b.vchr_name;"

            # print(str_query)
            cur.execute(str_query)
            rst_data = cur.fetchall()
            lst_data = []

            if rst_data:
                for data in rst_data:
                    dct_temp = {}
                    dct_temp['qty'] = 1
                    dct_temp['branch'] = data['branch']
                    dct_temp['type'] = data['vchr_name']
                    dct_temp['discount'] = data['discount']
                    dct_temp['indirectDiscount'] = data['indirect_discount']
                    dct_temp['tax'] = data['tax']
                    dct_temp['packageAmount'] = data['package_amount']
                    dct_temp['packageProfit'] = data['package_profit']
                    dct_temp['netProfit'] = data['net_profit']
                    lst_data.append(dct_temp)

            if lst_data:
                return Response({"status":1,"data":lst_data})
            else:
                return Response({"status":0, "data":"No Data..."})

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0, "data":"Some Thing Went Wrong !!..."+str(e)})

class RechargeProfitReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:

            data = get_branch()
            if data['status'] == 1:
                return Response({"status":1,"branch":data['branch']})
            else:
                return Response({"status":0,"data":"NO Data..."})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0,"data":"Oops.... Something Went Wrong!!...."})

    def post(self,request):
        # {"datFrom":"2020-07-01", "datTo":"2020-07-01","lstBranch":[2,3],"bln_download":"True"}
        # {"datFrom":"2019-07-01","bln_download":"True"}
        # {"datFrom":"2019-07-01","bln_download":"True"}
        # {"datFrom":"2019-07-01","lstBranch":[64],"type":[2]}
        try:

            dat_date_from = request.data.get('datFrom',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            selected_branch = request.data.get('lstBranch') or []
            str_filter = ""
            lst_branches = []
            dct_privilege = get_user_privileges(request)

            #---------------------------------------------------------------
            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN'):
                if request.user.userdetails.fk_group.vchr_name.upper() in ["BRANCH MANAGER","ASSISTANT BRANCH MANAGER","ASM1","ASM2","ASM3","ASM4"]:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND b.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                elif dct_privilege:

                    if dct_privilege.get('lst_branches'):
                        lst_branches = dct_privilege['lst_branches']
                        str_filter += "AND b.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                    else:
                        lst_branches = [request.user.userdetails.fk_branch_id]
                        str_filter += "AND b.pk_bint_id in ("+str(lst_branches)[1:-1]+") "

                    if dct_privilege.get('lst_products'):

                        str_filter += "AND pr.pk_bint_id in ("+str(dct_privilege['lst_products'])[1:-1]+") "


                else:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND b.pk_bint_id in ("+str(lst_branches)[1:-1]+") "



            #----------------------------------------------------------------
            if selected_branch:
                str_filter += "AND b.pk_bint_id in ("+str(selected_branch)[1:-1]+") "


            if request.data.get('bln_download'):
                str_query = """SELECT
                    branch,
                    type,
                    SUM(discount) AS discount,
                    SUM(indirect_discount) AS indirect_discount,
                    SUM(0) AS tax,
                    SUM(package_amount) AS package_amount,
                    SUM(package_profit) AS package_profit,
                    SUM(net_profit) AS net_profit,
                    SUM(count) AS count
                    FROM(SELECT
                        b.vchr_name AS branch,
                        case when (itm.vchr_item_code = 'REC00007') then 'POSTPAID'
                            when (itm.vchr_item_code in ('REC00004','REC00001','REC00003','REC00010')) then  'PREPAID AND DTH'
                            when (itm.vchr_item_code in ('REC00006')) then 'KSEB'
                            when (itm.vchr_item_code in ('REC00008')) then 'MONEY TRANSFER' end as type,
                        ROUND(sd.dbl_discount::NUMERIC,2) AS discount,
                        ROUND(sd.dbl_indirect_discount::NUMERIC,2) AS indirect_discount,
                        ROUND((sd.dbl_selling_price + sd.dbl_discount)::NUMERIC,2) AS package_amount,
                        CASE WHEN (itm.vchr_item_code in ('REC00004','REC00001','REC00003','REC00010')) then ROUND((((sd.dbl_selling_price + sd.dbl_discount)*1)/100)::NUMERIC,2) ELSE 0 END as package_profit,
                        ROUND(((CASE WHEN (itm.vchr_item_code in ('REC00004','REC00001','REC00003','REC00010')) then ROUND((((sd.dbl_selling_price + sd.dbl_discount)*1)/100)::NUMERIC,2) ELSE 0 END) - (sd.dbl_indirect_discount + sd.dbl_discount))::NUMERIC,2) AS net_profit,
                        1 AS count
                        FROM sales_details sd
                            JOIN sales_master sm ON sm.pk_bint_id = sd.fk_master_id
                            JOIN branch b ON sm.fk_branch_id = b.pk_bint_id
                            JOIN item itm ON itm.pk_bint_id = sd.fk_item_id
                        WHERE itm.vchr_item_code IN ('REC00004','REC00001','REC00003','REC00010','REC00006','REC00008','REC00007')
                        """+str_filter+""" AND sm.dat_created::DATE  between '"""+dat_date_from+"""' and '"""+dat_date_to+"""') as val
                    GROUP BY branch,type
                    ORDER BY branch; """

                # print(str_query)
                cur.execute(str_query)
                rst_data = cur.fetchall()

                if rst_data:
                    try:
                        count = 0
                        dct_report = {'Slno':[],'Recharge Type':[],'Branch':[],'Discount':[],'Indirect Discount':[],'Tax':[],'Recharge Value':[],'Profit':[],'Net Profit':[],'QTY':[]}
                        for data in rst_data:
                            count += 1
                            dct_report['Slno'].append(count)
                            dct_report['Branch'].append(data['branch'])
                            dct_report['Recharge Type'].append(data['type'])
                            dct_report['Discount'].append(data['discount'])
                            dct_report['Indirect Discount'].append(data['indirect_discount'])
                            dct_report['Tax'].append(data['tax'])
                            dct_report['Recharge Value'].append(data['package_amount'])
                            dct_report['Profit'].append(data['package_profit'])
                            dct_report['Net Profit'].append(data['net_profit'])
                            dct_report['QTY'].append(data['count'])

                        # #
                        df = pd.DataFrame(dct_report)
                        str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_rechargeprofitreport.xlsx'
                        filename =settings.MEDIA_ROOT+'/'+str_file

                        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                        workbook = writer.book
                        cell_format = workbook.add_format()
                        cell_format.set_align('center')
                        cell_format1 = workbook.add_format()
                        cell_format1.set_align('left')
                        df.to_excel(writer,index=False, sheet_name='Recharge Profit Report',columns=['Slno','Branch','Recharge Type','Recharge Value','Profit','Discount','Indirect Discount','Tax','Net Profit','QTY'],startrow=6, startcol=0)
                        worksheet = writer.sheets['Recharge Profit Report']
                        merge_format1 = workbook.add_format({
                            'bold': 20,
                            'border': 1,
                            'align': 'center',
                            'valign': 'vcenter',
                            'font_size':23
                            })

                        merge_format2 = workbook.add_format({
                        'bold': 6,
                        'border': 1,
                        'align': 'left',
                        'valign': 'vleft',
                        'font_size':13
                        })
                        worksheet.merge_range('A1+:J2', 'Recharge Profit Report', merge_format1)
                        worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
                        worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
                        worksheet.set_column('B:B', 18,cell_format1)
                        worksheet.set_column('C:C', 18,cell_format1)
                        worksheet.set_column('D:D', 18,cell_format)
                        worksheet.set_column('E:E', 17,cell_format)
                        worksheet.set_column('F:F', 16,cell_format)
                        worksheet.set_column('G:G', 20,cell_format)
                        worksheet.set_column('H:H', 15,cell_format)
                        worksheet.set_column('I:I', 15,cell_format)
                        worksheet.set_column('J:J', 15,cell_format)
                        worksheet.set_column('K:K', 15,cell_format)
                        writer.save()
                        return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                        return JsonResponse({'status':'0','data':e})



            str_query = """SELECT
                branch,
                type,
                SUM(discount) AS discount,
                SUM(indirect_discount) AS indirect_discount,
                SUM(0) AS tax,
                SUM(package_amount) AS package_amount,
                SUM(package_profit) AS package_profit,
                SUM(net_profit) AS net_profit,
                SUM(count) AS count
                FROM(SELECT
                    b.vchr_name AS branch,
                    case when (itm.vchr_item_code = 'REC00007') then 'POSTPAID'
                        when (itm.vchr_item_code in ('REC00004','REC00001','REC00003','REC00010')) then  'PREPAID AND DTH'
                        when (itm.vchr_item_code in ('REC00006')) then 'KSEB'
                        when (itm.vchr_item_code in ('REC00008')) then 'MONEY TRANSFER' end as type,
                    ROUND(sd.dbl_discount::NUMERIC,2) AS discount,
                    ROUND(sd.dbl_indirect_discount::NUMERIC,2) AS indirect_discount,
                    ROUND((sd.dbl_selling_price + sd.dbl_discount)::NUMERIC,2) AS package_amount,
                    CASE WHEN (itm.vchr_item_code in ('REC00004','REC00001','REC00003','REC00010')) then ROUND((((sd.dbl_selling_price + sd.dbl_discount)*1)/100)::NUMERIC,2) ELSE 0 END as package_profit,
                    ROUND(((CASE WHEN (itm.vchr_item_code in ('REC00004','REC00001','REC00003','REC00010')) then ROUND((((sd.dbl_selling_price + sd.dbl_discount)*1)/100)::NUMERIC,2) ELSE 0 END) - (sd.dbl_indirect_discount + sd.dbl_discount))::NUMERIC,2) AS net_profit,
                    1 AS count
                    FROM sales_details sd
                        JOIN sales_master sm ON sm.pk_bint_id = sd.fk_master_id
                        JOIN branch b ON sm.fk_branch_id = b.pk_bint_id
                        JOIN item itm ON itm.pk_bint_id = sd.fk_item_id
                    WHERE itm.vchr_item_code IN ('REC00004','REC00001','REC00003','REC00010','REC00006','REC00008','REC00007')
                    """+str_filter+""" AND sm.dat_created::DATE  between '"""+dat_date_from+"""' and '"""+dat_date_to+"""') as val
                GROUP BY branch,type
                ORDER BY branch; """

            # print(str_query)
            cur.execute(str_query)
            rst_data = cur.fetchall()
            lst_data = []

            if rst_data:
                for data in rst_data:
                    dct_temp = {}
                    dct_temp['qty'] = data['count']
                    dct_temp['type'] = data['type']
                    dct_temp['discount'] = data['discount']
                    dct_temp['indirectDiscount'] = data['indirect_discount']
                    dct_temp['tax'] = data['tax']
                    dct_temp['packageAmount'] = data['package_amount']
                    dct_temp['packageProfit'] = data['package_profit']
                    dct_temp['netProfit'] = data['net_profit']
                    lst_data.append(dct_temp)

            if lst_data:
                return Response({"status":1,"data":lst_data})
            else:
                return Response({"status":0, "data":"No Data..."})

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0, "data":"Some Thing Went Wrong !!..."+str(e)})


class ProductProfitReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            data = get_branch()
            if data['status'] == 1:
                return Response({"status":1,"branch":data['branch']})
            else:
                return Response({"status":1,"data":"NO Data..."})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0,"data":"Oops.... Something Went Wrong!!...."})

    def post(self,request):
        # {"datFrom":"2019-07-01", "datTo":"2020-07-01","lstBranch":[2,3],"bln_download":"True"}
        # {"datFrom":"2019-07-01","bln_download":"True"}
        # {"datFrom":"2019-07-01","bln_download":"True"}
        # {"datFrom":"2019-07-01","lstBranch":[64],"type":[2]}
        try:

            dat_date_from = request.data.get('datFrom',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            lst_selected_branch = request.data.get('lstBranch') or []
            lst_branches = []
            str_filter = ""
            dct_privilege = get_user_privileges(request)
            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN'):
                if request.user.userdetails.fk_group.vchr_name.upper() in ["BRANCH MANAGER","ASSISTANT BRANCH MANAGER","ASM1","ASM2","ASM3","ASM4"]:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "b.pk_bint_id in ("+str(lst_branches)[1:-1]+") AND "
                elif dct_privilege:

                    if dct_privilege.get('lst_branches'):
                        lst_branches = dct_privilege['lst_branches']
                        str_filter += "b.pk_bint_id in ("+str(lst_branches)[1:-1]+") AND "
                    else:
                        lst_branches = [request.user.userdetails.fk_branch_id]
                        str_filter += "b.pk_bint_id in ("+str(lst_branches)[1:-1]+") AND "

                    if dct_privilege.get('lst_products'):
                        str_filter += " pd.pk_bint_id in ("+str(dct_privilege['lst_products'])[1:-1]+")  AND"
                else:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "b.pk_bint_id in ("+str(lst_branches)[1:-1]+") AND "







            if lst_selected_branch:
                str_filter += " b.pk_bint_id in ("+str(lst_selected_branch)[1:-1]+") AND "

            if request.data.get('bln_download'):

                str_query = """ SELECT
                    branch,
                    vchr_name AS product,
                    ROUND(SUM(discount)::NUMERIC,2) AS discount,
                    ROUND(SUM(indirect_discount)::NUMERIC,2) AS indirect_discount,
                    ROUND(SUM(net_value)::NUMERIC,2) AS net_value,
                    ROUND(SUM(taxable_value)::NUMERIC,2) AS taxable_value,
                    ROUND(SUM(dp_tax)::NUMERIC,2) AS dp_tax,
                    ROUND(SUM((taxable_value - dp_tax))::NUMERIC,2) as profit,
                    ROUND(SUM(((taxable_value - dp_tax) - indirect_discount))::NUMERIC,2) as net_profit
                    FROM(
                        SELECT
                        b.vchr_name as branch,
                        pd.vchr_name,
                        ROUND(sd.dbl_discount::NUMERIC,2) AS discount,
                        ROUND(sd.dbl_indirect_discount::NUMERIC,2) AS indirect_discount,
                        ROUND((sd.dbl_selling_price)::NUMERIC,2) AS net_value,
                        ROUND((sd.dbl_selling_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC)) AS taxable_value,
                        CASE WHEN sd.dbl_selling_price < 0 THEN
                                ROUND((sd.dbl_dealer_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC)::NUMERIC,2)*-1
                            ELSE
                                ROUND((sd.dbl_dealer_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC)::NUMERIC,2)
                        END AS dp_tax
                        FROM sales_details sd
                            JOIN sales_master sm on sm.pk_bint_id = sd.fk_master_id
                            JOIN branch b ON sm.fk_branch_id = b.pk_bint_id
                            JOIN item itm ON itm.pk_bint_id = sd.fk_item_id
                            JOIN products pd ON pd.pk_bint_id = itm.fk_product_id
                            JOIN item_category ic ON ic.pk_bint_id = itm.fk_item_category_id
                            WHERE itm.vchr_item_code not in ('REC00004','REC00001','REC00003','REC00010','REC00006','REC00008','REC00007','GDC00001','GDC00002')
                            AND sd.int_sales_status != 2 AND sd.int_sales_status != 3 AND pd.vchr_name NOT IN ('SPARE','SMART CHOICE','SERVICE')
                            AND """+str_filter+""" sm.dat_created::DATE  between '"""+dat_date_from+"""' and '"""+dat_date_to+"""' ) as val
                    GROUP BY branch,vchr_name
                    ORDER BY branch;"""

                # print(str_query)
                cur.execute(str_query)
                rst_data = cur.fetchall()

                if rst_data:
                    try:
                        count = 0
                        dct_report = { 'Slno':[], 'Branch':[], 'Product':[], 'Net Value':[], 'Taxable Value':[], 'DP-Tax':[], 'Profit':[], 'Indirect Discount':[], 'Net Profit':[], 'Direct Discount':[] }
                        for data in rst_data:
                            count += 1
                            dct_report['Slno'].append(count)
                            dct_report['Branch'].append(data['branch'])
                            dct_report['Product'].append(data['product'])
                            dct_report['Net Value'].append(data['net_value'])
                            dct_report['Taxable Value'].append(data['taxable_value'])
                            dct_report['DP-Tax'].append(data['dp_tax'])
                            dct_report['Profit'].append(data['profit'])
                            dct_report['Indirect Discount'].append(data['indirect_discount'])
                            dct_report['Net Profit'].append(data['net_profit'])
                            dct_report['Direct Discount'].append(data['discount'])

                        # #
                        df = pd.DataFrame(dct_report)
                        str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_productprofitreport.xlsx'
                        filename =settings.MEDIA_ROOT+'/'+str_file

                        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                        workbook = writer.book
                        cell_format = workbook.add_format()
                        cell_format.set_align('right')
                        cell_format1 = workbook.add_format()
                        cell_format1.set_align('left')
                        df.to_excel(writer,index=False, sheet_name='Product Profit Report',columns=['Slno', 'Branch', 'Product', 'Net Value', 'Taxable Value', 'DP-Tax', 'Profit', 'Indirect Discount', 'Net Profit', 'Direct Discount'],startrow=6, startcol=0)
                        worksheet = writer.sheets['Product Profit Report']
                        merge_format1 = workbook.add_format({
                            'bold': 20,
                            'border': 1,
                            'align': 'center',
                            'valign': 'vcenter',
                            'font_size':23
                            })

                        merge_format2 = workbook.add_format({
                        'bold': 6,
                        'border': 1,
                        'align': 'left',
                        'valign': 'vleft',
                        'font_size':13
                        })
                        worksheet.merge_range('A1+:J2', 'Product Profit Report', merge_format1)
                        worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
                        worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
                        worksheet.set_column('B:B', 18,cell_format1)
                        worksheet.set_column('C:C', 18,cell_format)
                        worksheet.set_column('D:D', 18,cell_format)
                        worksheet.set_column('E:E', 17,cell_format)
                        worksheet.set_column('F:F', 16,cell_format)
                        worksheet.set_column('G:G', 20,cell_format)
                        worksheet.set_column('H:H', 15,cell_format)
                        worksheet.set_column('I:I', 15,cell_format)
                        worksheet.set_column('J:J', 15,cell_format)
                        writer.save()
                        return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                        return JsonResponse({'status':'0','data':e})


            str_query = """ SELECT
                branch,
                vchr_name AS product,
                ROUND(SUM(discount)::NUMERIC,2) AS discount,
                ROUND(SUM(indirect_discount)::NUMERIC,2) AS indirect_discount,
                ROUND(SUM(net_value)::NUMERIC,2) AS net_value,
                ROUND(SUM(taxable_value)::NUMERIC,2) AS taxable_value,
                ROUND(SUM(dp_tax)::NUMERIC,2) AS dp_tax,
                ROUND(SUM((taxable_value - dp_tax))::NUMERIC,2) as profit,
                ROUND(SUM(((taxable_value - dp_tax) - indirect_discount))::NUMERIC,2) as net_profit
                FROM(
                    SELECT
                    b.vchr_name as branch,
                    pd.vchr_name,
                    ROUND(sd.dbl_discount::NUMERIC,2) AS discount,
                    ROUND(sd.dbl_indirect_discount::NUMERIC,2) AS indirect_discount,
                    ROUND((sd.dbl_selling_price)::NUMERIC,2) AS net_value,
                    ROUND((sd.dbl_selling_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC)) AS taxable_value,
                    CASE WHEN sd.dbl_selling_price < 0 THEN
                            ROUND((sd.dbl_dealer_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC)::NUMERIC,2)*-1
                        ELSE
                            ROUND((sd.dbl_dealer_price / ('1.' || sd.dbl_tax_percentage)::NUMERIC)::NUMERIC,2)
                    END AS dp_tax
                    FROM sales_details sd
                        JOIN sales_master sm on sm.pk_bint_id = sd.fk_master_id
                        JOIN branch b ON sm.fk_branch_id = b.pk_bint_id
                        JOIN item itm ON itm.pk_bint_id = sd.fk_item_id
                        JOIN products pd ON pd.pk_bint_id = itm.fk_product_id
                        JOIN item_category ic ON ic.pk_bint_id = itm.fk_item_category_id
                        WHERE itm.vchr_item_code not in ('REC00004','REC00001','REC00003','REC00010','REC00006','REC00008','REC00007','GDC00001','GDC00002')
                        AND sd.int_sales_status != 2 AND sd.int_sales_status != 3 AND pd.vchr_name NOT IN ('SPARE','SMART CHOICE','SERVICE')
                        AND """+str_filter+""" sm.dat_created::DATE  between '"""+dat_date_from+"""' and '"""+dat_date_to+"""' ) as val
                GROUP BY branch,vchr_name
                ORDER BY branch;"""


            # print(str_query)
            cur.execute(str_query)
            rst_data = cur.fetchall()
            lst_data = []

            if rst_data:
                for data in rst_data:
                    dct_temp = {}
                    dct_temp['Product'] = data.get('product')
                    dct_temp['NetValue'] = data.get('net_value')
                    dct_temp['TaxableValue'] = data.get('taxable_value')
                    dct_temp['DP-Tax'] = data.get('dp_tax')
                    dct_temp['Profit'] = data.get('profit')
                    dct_temp['IndirectDiscount'] = data.get('indirect_discount')
                    dct_temp['NetProfit'] = data.get('net_profit')
                    dct_temp['DirectDiscount'] = data.get('discount')
                    lst_data.append(dct_temp)

            if lst_data:
                return Response({"status":1,"data":lst_data})
            else:
                return Response({"status":0, "data":"No Data..."})

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({"status":0, "data":"Some Thing Went Wrong !!..."+str(e)})



class BranchStockHistory(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            dct_details = {}
            bln_branch = False
            ins_product = list(Products.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            ins_item_category = list(ItemCategory.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_item_category')).values('id','name'))
            ins_brands = list(Brands.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            # ins_items = list(Item.objects.annotate(id=F('pk_bint_id'),name=F('vchr_name')).values('id','name'))
            ins_item_group = list(ItemGroup.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_item_group')).values('id','name'))

            if request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN':
                ins_branch = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
                dct_details['branch']=ins_branch
                bln_branch = True
            dct_details['product']=ins_product
            dct_details['item_category']=ins_item_category
            dct_details['brand']=ins_brands
            dct_details['item_group']=ins_item_group
            return Response({"status":0,"data":dct_details,'bln_branch':bln_branch})
        except Exception as e:
            return Response({"status":0,"data":'no data'})


    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()
            bln_check = request.data.get("blnCheck")
            # bln_check = False
            dat_from = request.data.get('fromDate')
            dat_to = request.data.get('toDate')
            # dat_from = '2020-03-19'
            # dat_to = '2020-08-20'

            lst_product_id = request.data.get('lstProduct')
            lst_brand_id = request.data.get('lstBrand')
            lst_item_group_id = request.data.get('lstItemGroup')
            lst_item_cat_id = request.data.get('lstItemCategory')
            int_item_id = request.data.get('intItemId')
            lst_branch_id = request.data.get('lstBranch')
            lst_more_filter = request.data.get('lst_more_filter') or []
            dct_export_filter  = {}
            # lst_more_filter =  ['Product', 'Brand', 'Stock']
            # lst_product_id = [12,14]
            bln_branch = False
            dct_details = {}
            ins_product = list(Products.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            ins_item_category = list(ItemCategory.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_item_category')).values('id','name'))
            ins_brands = list(Brands.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            # ins_items = list(Item.objects.annotate(id=F('pk_bint_id'),name=F('vchr_name')).values('id','name'))
            ins_item_group = list(ItemGroup.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_item_group')).values('id','name'))

            if request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN':
                ins_branch = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
                dct_details['branch']=ins_branch
                bln_branch = True
            dct_details['product']=ins_product
            dct_details['item_category']=ins_item_category
            dct_details['brand']=ins_brands
            dct_details['item_group']=ins_item_group



            #-------------------------------------------------------------------------------------------------------------------
            str_filter = ''

            if request.user.userdetails.fk_branch.int_type  in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' :
                lst_branch = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
                if lst_branch_id:
                    str_filter +=' AND br.pk_bint_id in ('+ str(lst_branch_id)[1:-1]+')'


            else:
                str_filter +=' AND br.pk_bint_id = ' +str(request.user.userdetails.fk_branch_id) +''
            # if lst_product_id:
            #     str_filter +=' AND in ('+str(lst_product_id)[1:-1]+')'
            # if  lst_brand_id:
            #     str_filter +=' AND br_data.int_branch_id in ('+str(lst_brand_id)[1:-1]+')'

            if int_item_id:
                str_filter +=' AND it.pk_bint_id = ' + str(int_item_id)
            if lst_branch_id:
                str_filter +=' AND br.pk_bint_id in ('+ str(lst_branch_id)[1:-1]+')'

            dat_from = "'" + dat_from +"'"
            dat_to = "'" + dat_to +"'"
            # #
            str_grn_master_querry = """ select sum(grd.int_qty) as int_qty,
                                    (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                    (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                    'GRN' as vchr_type
                                    from grn_details grd
                                    join grn_master grm on grd.fk_purchase_id = grm.pk_bint_id
                                    join branch br on grm.fk_branch_id = br.pk_bint_id
                                    join item it on grd.fk_item_id = it.pk_bint_id
                                    where grm.dat_created::DATE <={dat_from} {filter}
                                    group by br.pk_bint_id,it.pk_bint_id"""

            str_grn_master_querry = str_grn_master_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_grn_master_stock = conn.execute(str_grn_master_querry).fetchall()

            str_grn_return_querry = """ select sum(grnr.int_qty) as int_qty,
                                    (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                    (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                    'GRN' as vchr_type
                                    from grnr_details grnr
                                    join grnr_master gr_ms on grnr.fk_master_id = gr_ms.pk_bint_id
                                    join branch br on gr_ms.fk_branch_id = br.pk_bint_id
                                    join item it on grnr.fk_item_id = it.pk_bint_id
                                    where gr_ms.dat_purchase_return::DATE <={dat_from} {filter}
                                    group by br.pk_bint_id,it.pk_bint_id"""

            str_grn_return_querry = str_grn_return_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_grn_return_stock = conn.execute(str_grn_return_querry).fetchall()







            str_branch_stock_querry = """select sum(bsid.int_received) as int_qty,
                                      (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                      (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                      'BRANCH' as vchr_type

                                      from branch_stock_imei_details bsid
                                      join branch_stock_details bsd on bsid.fk_details_id = bsd.pk_bint_id
                                      join branch_stock_master bsm on bsd.fk_master_id =bsm.pk_bint_id
                                      join branch br on bsm.fk_branch_id = br.pk_bint_id
                                      join item it on bsd.fk_item_id = it.pk_bint_id
                                      join brands bd on bd.pk_bint_id =it.fk_brand_id
                                      where bsm.dat_stock::DATE <={dat_from} {filter}
                                      group by br.pk_bint_id,it.pk_bint_id"""
            str_branch_stock_querry = str_branch_stock_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_branch_stock = conn.execute(str_branch_stock_querry).fetchall()




            str_stock_transfer_querry =   """ select sum(stid.int_qty) as int_qty,
                                            (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                            (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                            'TRANSFER' as vchr_type
                                            from stock_transfer_imei_details stid
                                            join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                                            join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                                            join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                                            join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                                            join branch br on br.pk_bint_id = stf.fk_from_id
                                            join item it on ist.fk_item_id = it.pk_bint_id
                                            where stf.int_status in (1,2,3) and  stf.dat_transfer::DATE <={dat_from} {filter}
                                            group by br.pk_bint_id,it.pk_bint_id  """

            str_stock_transfer_querry = str_stock_transfer_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_stock_transfer= conn.execute(str_stock_transfer_querry).fetchall()



            str_stock_recieved_querry = """ select sum(stid.int_qty) as int_qty,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        'RECIEVED' as vchr_type
                                        from stock_transfer_imei_details stid
                                        join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                                        join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                                        join branch br on br.pk_bint_id = stf.fk_to_id
                                        join item it on ist.fk_item_id = it.pk_bint_id
                                        where stf.int_status in (3) and   stf.dat_transfer::DATE <= {dat_from} {filter}
                                        group by br.pk_bint_id,it.pk_bint_id  """


            str_stock_recieved_querry = str_stock_recieved_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_stock_recieved = conn.execute(str_stock_recieved_querry).fetchall()


            str_stock_sales_querry =  """select sum(sd.int_qty) as int_qty,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        'SALE' as vchr_type

                                        from sales_details sd
                                        join sales_master sm on sd.fk_master_id = sm.pk_bint_id
                                        join branch br on sm.fk_branch_id = br.pk_bint_id
                                        join item it on sd.fk_item_id = it.pk_bint_id
                                        join brands bd on bd.pk_bint_id =it.fk_brand_id
                                        join products pd on it.fk_product_id = pd.pk_bint_id
                                        WHERE pd.vchr_name != 'SERVICE'  and  sd.int_sales_status = 1 and sm.dat_invoice <= {dat_from} {filter}
                                        group by br.pk_bint_id,it.pk_bint_id """

            str_stock_sales_querry = str_stock_sales_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_sales = conn.execute(str_stock_sales_querry).fetchall()


            str_stock_return_querry = """select sum(sr.int_qty) as int_qty,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        'RETURN' as vchr_type
                                        from sales_return sr
                                        join sales_master sm on sr.fk_returned_id = sm.pk_bint_id
                                        join branch br on sm.fk_branch_id = br.pk_bint_id
                                        join item it on sr.fk_item_id = it.pk_bint_id
                                        join products pd on it.fk_product_id = pd.pk_bint_id
                                        WHERE  sm.dat_invoice <= {dat_from} {filter}
                                        group by br.pk_bint_id,it.pk_bint_id"""
            str_stock_return_querry = str_stock_return_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data_return = conn.execute(str_stock_return_querry).fetchall()
            dct_opening_stock= {}
            dct_opening_stock['vchr_type'] =  None
            dct_opening_stock['vchr_action'] =  'OPENING STOCK'
            dct_opening_stock['int_qty'] =  0
            dct_opening_stock['vchr_doc_num'] =  None
            dct_opening_stock['vchr_branch_transac'] =  None
            dct_opening_stock['dat_transac'] = 'OPENING STOCK'
            dct_opening_stock['vchr_branch_name_from_transac'] = None
            if rst_data_grn_master_stock:
                dct_opening_stock['int_qty'] += rst_data_grn_master_stock[0].int_qty
            if rst_data_grn_return_stock:
                dct_opening_stock['int_qty'] -= rst_data_grn_return_stock[0].int_qty

            if rst_data_branch_stock:
                dct_opening_stock['int_qty'] += rst_data_branch_stock[0].int_qty


            if rst_data_stock_transfer:
                dct_opening_stock['int_qty'] -= rst_data_stock_transfer[0].int_qty

            # if rst_data_stock_recieved:
            #     dct_opening_stock['int_qty'] += rst_data_stock_recieved[0].int_qty

            if rst_data_sales:
                dct_opening_stock['int_qty'] -= rst_data_sales[0].int_qty

            if rst_data_return:
                dct_opening_stock['int_qty'] += rst_data_return[0].int_qty

            # str_opening_stock_querry = """select sum(br_data.int_qty) as int_opening_stock,
            #                   sum(br_data.int_transit) as int_opening_transit,br_data.vchr_item_code as vchr_item_code ,
            #                   br_data.vchr_item_name as vchr_item_name, br_data.int_item_id as int_item_id,
            #                   br_data.vchr_branch_code as vchr_branch_code,br_data.int_branch_id as int_branch_id
            #
            #                   from
            #                   (select  sum(0) as int_transit,sum(bsid.int_received) as int_qty,
            #                             (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
            #                             (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
            #                             'BRANCH' as vchr_type
            #
            #                             from branch_stock_imei_details bsid
            #                             join branch_stock_details bsd on bsid.fk_details_id = bsd.pk_bint_id
            #                             join branch_stock_master bsm on bsd.fk_master_id =bsm.pk_bint_id
            #                             join branch br on bsm.fk_branch_id = br.pk_bint_id
            #                             join item it on bsd.fk_item_id = it.pk_bint_id
            #                             join brands bd on bd.pk_bint_id =it.fk_brand_id
            #                             where bsm.dat_stock::DATE <={dat_from}
            #                             group by br.pk_bint_id,it.pk_bint_id
            #
            #                             UNION All
            #
            #                             select sum(0) as int_transit,sum(grd.int_qty) as int_qty,
            #                             (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
            #                             (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
            #                             'GRN' as vchr_type
            #                             from grn_details grd
            #                             join grn_master grm on grd.fk_purchase_id = grm.pk_bint_id
            #                             join branch br on grm.fk_branch_id = br.pk_bint_id
            #                             join item it on grd.fk_item_id = it.pk_bint_id
            #                             where grm.dat_created::DATE <={dat_from}
            #                             group by br.pk_bint_id,it.pk_bint_id
            #
            #
            #                             UNION ALL
            #
            #                             select sum(0) as int_transit, 0-sum(stid.int_qty) as int_qty,
            #                             (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
            #                             (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
            #                             'TRANSFER' as vchr_type
            #                             from stock_transfer_imei_details stid
            #                             join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
            #                             join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
            #                             join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
            #                             join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
            #                             join branch br on br.pk_bint_id = stf.fk_from_id
            #                             join item it on ist.fk_item_id = it.pk_bint_id
            #                             where stf.int_status in (0,1,2,3) and  stf.dat_transfer::DATE <='2020-08-05'
            #                             group by br.pk_bint_id,it.pk_bint_id
            #
            #
            #
            #                             UNION ALL
            #
            #                             select sum(0) as int_transit, sum(stid.int_qty) as int_qty,
            #                             (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
            #                             (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
            #                             'RECIEVED' as vchr_type
            #                             from stock_transfer_imei_details stid
            #                             join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
            #                             join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
            #                             join branch br on br.pk_bint_id = stf.fk_to_id
            #                             join item it on ist.fk_item_id = it.pk_bint_id
            #                             where stf.int_status in (3) and   stf.dat_transfer::DATE <{dat_from}
            #                             group by br.pk_bint_id,it.pk_bint_id
            #
            #                             UNION ALL
            #
            #                             select  sum(0) as int_transit, 0-sum(sd.int_qty) as int_qty,
            #                             (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
            #                             (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
            #                             'SALE' as vchr_type
            #
            #                             from sales_details sd
            #                             join sales_master sm on sd.fk_master_id = sm.pk_bint_id
            #                             join branch br on sm.fk_branch_id = br.pk_bint_id
            #                             join item it on sd.fk_item_id = it.pk_bint_id
            #                             join brands bd on bd.pk_bint_id =it.fk_brand_id
            #                             join products pd on it.fk_product_id = pd.pk_bint_id
            #                             WHERE pd.vchr_name != 'SERVICE'  and  sd.int_sales_status = 1 and sm.dat_invoice <= {dat_from}
            #                             group by br.pk_bint_id,it.pk_bint_id
            #
            #                             UNION ALL
            #
            #                             select  sum(0) as int_transit, sum(sd.int_qty) as int_qty,
            #                             (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
            #                             (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
            #                             'RETURN' as vchr_type
            #                             from sales_details sd
            #                             join sales_master sm on sd.fk_master_id = sm.pk_bint_id
            #                             join branch br on sm.fk_branch_id = br.pk_bint_id
            #                             join item it on sd.fk_item_id = it.pk_bint_id
            #                             join products pd on it.fk_product_id = pd.pk_bint_id
            #                             WHERE pd.vchr_name != 'SERVICE' and  sd.int_sales_status = 0  and sm.dat_invoice <= {dat_from}
            #                             group by br.pk_bint_id,it.pk_bint_id) as br_data
            #                             where (br_data.int_qty>0 or br_data.int_transit>0) {filter}
            #                             group by br_data.vchr_item_code,br_data.vchr_item_name,br_data.int_item_id,br_data.vchr_branch_code,br_data.int_branch_id """


            # str_opening_stock_querry = str_opening_stock_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            # rst_data_opennnig_stock = conn.execute(str_opening_stock_querry).fetchall()
            # dct_opening_stock= {}
            # dct_opening_stock['vchr_type'] =  None
            # dct_opening_stock['vchr_action'] =  'OPENING STOCK'
            # dct_opening_stock['int_qty'] =  0
            # dct_opening_stock['vchr_doc_num'] =  None
            # dct_opening_stock['vchr_branch_transac'] =  None
            # dct_opening_stock['dat_transac'] = 'OPENING STOCK'
            # dct_opening_stock['vchr_branch_name_from_transac'] = None
            # if rst_data_opennnig_stock:
            #     dct_opening_stock['int_qty'] = rst_data_opennnig_stock[0].int_opening_stock
            #


            # import pdb; pdb.set_trace()
            str_stck_history_querry ="""
                                        select
                                        transac_data.int_brand_id,transac_data.vchr_brand_name,transac_data.int_product_id,transac_data.vchr_product_name,
                                        transac_data.int_qty as int_qty,transac_data.vchr_doc_num as vchr_doc_num,to_char( transac_data.dat_transac, 'DD-MON-YYYY') as dat_transac ,
                                        transac_data.vchr_item_code as vchr_item_code_transac,transac_data.int_item_id as int_item_id_transac,transac_data.vchr_item_name as vchr_item_name_transac ,
                                        transac_data.int_branch_id as int_branch_id_cur,transac_data.vchr_branch_name as vchr_branch_name_cur,
                                        transac_data.vchr_branch_transac,transac_data.vchr_type,transac_data.vchr_action
                                        from

                                        (select sum(COALESCE(grd.int_qty,0)) as int_qty,grm.vchr_purchase_num as vchr_doc_num,grm.dat_created as dat_transac,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,(br.vchr_name) as vchr_branch_transac,br.pk_bint_id as int_filter_branch_id,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                        (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,

                                        'PURCHASED' as vchr_type,'PURCHASED' as vchr_action
                                        from grn_details grd
                                        join grn_master grm on grd.fk_purchase_id = grm.pk_bint_id
                                        join branch br on grm.fk_branch_id = br.pk_bint_id
                                        join item it on grd.fk_item_id = it.pk_bint_id
                                        join brands bd on bd.pk_bint_id =it.fk_brand_id
                                        join products pd on pd.pk_bint_id = it.fk_product_id
                                        where pd.vchr_name != 'SERVICE' and grm.dat_created::DATE BETWEEN {dat_from} and {dat_to}
                                        group by br.pk_bint_id,it.pk_bint_id,grm.vchr_purchase_num,grm.dat_created,bd.pk_bint_id,pd.pk_bint_id

                                        UNION ALL

                                        select (0-sum(sd.int_qty)) as int_qty,sm.vchr_invoice_num as vchr_doc_num,sm.dat_invoice as dat_transac,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,(br.vchr_name) as vchr_branch_transac,br.pk_bint_id as int_filter_branch_id,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                        (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                        'SALE' as vchr_type,'SOLD' as vchr_action

                                        from sales_details sd
                                        join sales_master sm on sd.fk_master_id = sm.pk_bint_id
                                        join branch br on sm.fk_branch_id = br.pk_bint_id
                                        join item it on sd.fk_item_id = it.pk_bint_id
                                        join brands bd on bd.pk_bint_id =it.fk_brand_id
                                        join products pd on pd.pk_bint_id = it.fk_product_id
                                        WHERE pd.vchr_name != 'SERVICE'  and  sd.int_sales_status = 1 and sm.dat_invoice BETWEEN {dat_from} and {dat_to}
                                        group by br.pk_bint_id,it.pk_bint_id,sm.vchr_invoice_num,sm.dat_invoice,bd.pk_bint_id,pd.pk_bint_id

                                        UNION ALL

                                        select sum(sd.int_qty) as int_qty,sm.vchr_invoice_num as vchr_doc_num,sm.dat_invoice as dat_transac,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,(br.vchr_name) as vchr_branch_transac,br.pk_bint_id as int_filter_branch_id,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                        (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                        'SALES RETURN' as vchr_type ,'SALES RETURN' as vchr_action
                                        from sales_details sd
                                        join sales_master sm on sd.fk_master_id = sm.pk_bint_id
                                        join branch br on sm.fk_branch_id = br.pk_bint_id
                                        join item it on sd.fk_item_id = it.pk_bint_id
                                        join brands bd on bd.pk_bint_id =it.fk_brand_id
                                        join products pd on pd.pk_bint_id = it.fk_product_id
                                        WHERE pd.vchr_name != 'SERVICE' and  sd.int_sales_status = 0 and sm.dat_invoice BETWEEN {dat_from} and {dat_to}
                                        group by br.pk_bint_id,it.pk_bint_id,sm.vchr_invoice_num,sm.dat_invoice,bd.pk_bint_id,pd.pk_bint_id


                                        UNION ALL

                                        select (0-sum(stid.int_qty)) as int_qty,stf.vchr_stktransfer_num as vchr_doc_num,stf.dat_transfer as dat_transac,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,(brc.vchr_name) as vchr_branch_transac,br.pk_bint_id as int_filter_branch_id,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                        (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                        'OUTWARD STOCK TRANSFER' as vchr_type,'TRANSFERRED' as vchr_action
                                        from stock_transfer_imei_details stid
                                        join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                                        join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                                        join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                                        join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                                        join branch br on br.pk_bint_id = stf.fk_from_id
                                        join branch brc on brc.pk_bint_id = stf.fk_to_id
                                        join item it on ist.fk_item_id = it.pk_bint_id
                                        join brands bd on bd.pk_bint_id =it.fk_brand_id
                                        join products pd on pd.pk_bint_id = it.fk_product_id
                                        where stf.int_status in (1,2,3) and  stf.dat_transfer BETWEEN {dat_from} and {dat_to}
                                        group by brc.pk_bint_id,br.pk_bint_id,it.pk_bint_id,stf.vchr_stktransfer_num,stf.dat_transfer,bd.pk_bint_id,pd.pk_bint_id

                                        UNION ALL

                                        select sum(COALESCE(grd.int_qty,0))*-1 as int_qty,
                                        grm.vchr_purchase_return_num as vchr_doc_num,
                                        grm.dat_purchase_return as dat_transac,
                                        (br.vchr_code) as vchr_branch_code,
                                        (br.pk_bint_id) as int_branch_id,
                                        (br.vchr_name) as vchr_branch_name,
                                        (br.vchr_name) as vchr_branch_transac,
                                        br.pk_bint_id as int_filter_branch_id,
                                        (it.vchr_item_code) as vchr_item_code,
                                        (it.pk_bint_id) as int_item_id,
                                        (it.vchr_name) as vchr_item_name,
                                        (bd.vchr_code) as vchr_brand_code,
                                        (bd.pk_bint_id) as int_brand_id,
                                        (bd.vchr_name) as vchr_brand_name,
                                        (pd.pk_bint_id) as int_product_id,
                                        (pd.vchr_name) as vchr_product_name,
                                        (pd.vchr_code) as vchr_product_code,
                                        'GOODS RETURN' as vchr_type,'GOODS RETURN' as vchr_action
                                        from grnr_details grd
                                            join grnr_master grm on grd.fk_master_id = grm.pk_bint_id
                                            join branch br on grm.fk_branch_id = br.pk_bint_id
                                            join item it on grd.fk_item_id = it.pk_bint_id
                                            join brands bd on bd.pk_bint_id =it.fk_brand_id
                                            join products pd on pd.pk_bint_id = it.fk_product_id
                                        where grm.dat_purchase_return::DATE BETWEEN {dat_from} and {dat_to}
                                        group by br.pk_bint_id,it.pk_bint_id,grm.vchr_purchase_return_num,grm.dat_purchase_return,bd.pk_bint_id,pd.pk_bint_id

                                        UNION ALL

                                        select sum(stid.int_qty) as int_qty,stf.vchr_stktransfer_num as vchr_doc_num,stf.dat_transfer as dat_transac,
                                        (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,(brc.vchr_name) as vchr_branch_transac,br.pk_bint_id as int_filter_branch_id,
                                        (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                        (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                        (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                        'INWARD STOCK TRANSFER' as vchr_type,'TRANSFERRED' as vchr_action
                                        from stock_transfer_imei_details stid
                                        join grn_details grd on stid.fk_grn_details_id = grd.pk_bint_id
                                        join grn_master  grm on grd.fk_purchase_id = grm.pk_bint_id
                                        join ist_details ist on  stid.fk_details_id = ist.pk_bint_id
                                        join stock_transfer stf on ist.fk_transfer_id = stf.pk_bint_id
                                        join branch br on br.pk_bint_id = stf.fk_to_id
                                        join branch brc on brc.pk_bint_id = stf.fk_from_id
                                        join item it on ist.fk_item_id = it.pk_bint_id
                                        join brands bd on bd.pk_bint_id =it.fk_brand_id
                                        join products pd on pd.pk_bint_id = it.fk_product_id
                                        where stf.int_status in (3) and  stf.dat_transfer BETWEEN {dat_from} and {dat_to}
                                        group by brc.pk_bint_id, br.pk_bint_id,it.pk_bint_id,stf.vchr_stktransfer_num,stf.dat_transfer,bd.pk_bint_id,pd.pk_bint_id
                                        ) as transac_data where true = true {filter} order by transac_data.dat_transac """



            #--------------------------------------------------------------------------------------------------------------------
            str_filter = ''
            if request.user.userdetails.fk_branch.int_type  in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' :
                lst_branch = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
                if lst_branch_id:
                    str_filter +=' AND transac_data.int_filter_branch_id in ('+ str(lst_branch_id)[1:-1]+')'
            else:
                str_filter +=' AND transac_data.int_filter_branch_id = ' +str(request.user.userdetails.fk_branch_id) +''
            if lst_product_id:
                str_filter +=' AND transac_data.int_product_id in ('+str(lst_product_id)[1:-1]+')'
            if  lst_brand_id:
                str_filter +=' AND transac_data.int_brand_id in ('+str(lst_brand_id)[1:-1]+')'
            if int_item_id:
                str_filter +=' AND transac_data.int_item_id = ' + str(int_item_id)
            if lst_branch_id:
                str_filter +=' AND transac_data.int_filter_branch_id in ('+ str(lst_branch_id)[1:-1]+')'



            str_stck_history_querry = str_stck_history_querry.format(dat_from = dat_from,dat_to = dat_to,filter = str_filter)
            rst_data = conn.execute(str_stck_history_querry).fetchall()

            rst_data.insert(0,dct_opening_stock)
            return Response({'status':1,'data':rst_data})





        except Exception as msg:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(msg, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(msg)})







class PurchaseReport(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()


            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            # dat_from = "2019-01-01"
            # dat_to = "2019-05-29"
            #
            int_supp_id  = request.data.get("intSupplierId")
            int_staff_id =  request.data.get("intStaffId")
            lst_more_filter = request.data.get("lst_moreFilter")
            lst_join = []

            dct_querry_var = {"Date":"dat_purchase","Purchase Number":"vchr_purchase_num","Branch":"branch.vchr_name as vchr_branch_name","Vendor":"supplier.vchr_name as vchr_supplier_name","Staff":"auth_user.first_name,auth_user.last_name","Product":"products.vchr_name as vchr_product_name","Brand":"brands.vchr_name as vchr_brand_name","Item":"item.vchr_name as vchr_item_name","Item Code":"item.vchr_item_code as vchr_item_code","Imei/Batch":"jsn_imei->'imei' as IMEI, vchr_batch_no as BATCH",'Item Category':'vchr_item_category','Item Group':'vchr_item_group'}
            dct_join_data = {'Branch':' join branch on grn_master.fk_branch_id = branch.pk_bint_id' ,
                        'Product':' join products on item.fk_product_id = products.pk_bint_id',

                         'Brand':' join brands on item.fk_brand_id = brands.pk_bint_id' ,
                         'Vendor':' join supplier on grn_master.fk_supplier_id = supplier.pk_bint_id' ,
                         'Staff' :' join auth_user on grn_master.fk_created_id = auth_user.id',
                         'Item Category':'join item_category  on item_category.pk_bint_id=item.fk_item_category_id',
                         'Item Group':'join item_group on item_group.pk_bint_id=item.fk_item_category_id',

                         }

            if lst_more_filter:
                lst_selected = [data[1] for data in dct_querry_var.items() if data[0] in lst_more_filter]
                lst_group_by = [data[1].rsplit(" ",1)[-1] for data in dct_querry_var.items() if data[0] in lst_more_filter]
                lst_join = [dct_join_data[i] for i in lst_more_filter if i in dct_join_data.keys() ]
            else :
                lst_selected = ['dat_purchase']
                lst_group_by = ['dat_purchase']
                lst_more_filter = []
            #

            '''for adding imei and batch no. from the more filter, IMEI wasn't present in  lst_group_by'''
            if 'Imei/Batch' in lst_more_filter:
                lst_group_by.append('IMEI')



            '''dat_invoice in more filter is not mandatory anymore,
                hence dat_invoice is added to lst_group_by and lst_selected for
                 selecting dat_invoice in query and grouping it in query'''

            if 'dat_purchase' not in lst_group_by:
                lst_group_by.append('dat_purchase')

            if 'dat_purchase' not in lst_selected:
                lst_selected.append('dat_purchase')

            #
            # import pdb;pdb.set_trace()


            # str_querry = "select {selected}, sum(sales_details.dbl_selling_price) as dbl_total_amount,sum(sales_details.int_qty) as int_total_qty,int_sales_status from sales_details  join sales_master on sales_details.fk_master_id = sales_master.pk_bint_id join item on sales_details.fk_item_id = item.pk_bint_id "
            #
            str_querry = 'select {selected},sum(int_qty) as int_qty,sum(dbl_tax*int_qty) as tax_value,sum(dbl_supplier_cost*int_qty) as dbl_taxable_value,sum(dbl_total_amount)  as dbl_total_amount from grn_master  join grn_details  on   grn_details.fk_purchase_id=grn_master.pk_bint_id join item on grn_details.fk_item_id = item.pk_bint_id'
            # "join branch on sales_master.fk_branch_id = branch.pk_bint_id"
            # if
            #  join products on item.fk_product_id = products.pk_bint_id
            #  join brands on item.fk_brand_id = brands.pk_bint_id
            #  join customer_details on sales_master.fk_customer_id = customer_details.pk_bint_id
            #  join auth_user on sales_master.fk_staff_id = auth_user.id
            #  join branch on sales_master.fk_branch_id = branch.pk_bint_id

            """DATE WISE FILTER"""
            str_filter = " WHERE dat_purchase:: DATE BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"'"
            """CUSTOMER WISE"""
            if int_supp_id:

                str_filter += "AND grn_master.fk_supplier_id = "+str(int_supp_id)+" "
                # lst_selected.append("sales_customer_details.vchr_name as vchr_customer_name")
                # lst_group_by.append(" vchr_customer_name")
                if 'Vendor' not in lst_more_filter:
                    str_querry += dct_join_data ['Vendor']


            """STAFF WISE"""
            if int_staff_id:
                str_filter += "AND grn_master.fk_created_id = "+str(int_staff_id)+" "
                # lst_selected.append("auth_user.first_name,auth_user.last_name")
                # lst_group_by.append("auth_user.first_name,auth_user.last_name")
                if 'Staff' not in lst_more_filter:
                    str_querry += dct_join_data ['Staff']

            if not request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','PURCHASE MANAGER','ACCOUNTS MANAGER-SCHEMES AND CLAIMS']:
                str_filter += "AND grn_master.fk_branch_id = "+str(request.user.userdetails.fk_branch_id)+" "

            if request.data.get('lstProduct'):
                # str_querry+ = ' AND fk_product_id in '+str(request.data.get('lst_product_id')).replace('[','(').replace("]",")")
                str_filter +=  ' AND fk_product_id in ' +str(request.data.get('lstProduct')).replace('[','(').replace(']',')')
            if request.data.get("lstBrand"):
                str_filter +=  ' AND fk_brand_id in ' +str(request.data.get('lstBrand')).replace('[','(').replace(']',')')

            if request.data.get("lstItemCategory"):

                str_filter +=  ' AND fk_item_category_id in ' +str(request.data.get('lstItemCategory')).replace('[','(').replace(']',')')

                # str_querry+ = " AND fk_item_category_id in "+str(request.data.get("lst_item_category_id")).replace("[","(")

            if request.data.get("lstItemGroup"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_filter +=  ' AND fk_item_group_id in ' +str(request.data.get('lstItemGroup')).replace('[','(').replace(']',')')

            if request.data.get("lstItem"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_filter +=  ' AND fk_item_id in ' +str(request.data.get('lstItem')).replace('[','(').replace(']',')')

            if request.data.get("lstBranch"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_filter +=  ' AND fk_branch_id in ' +str(request.data.get("lstBranch")).replace('[','(').replace(']',')')




            str_querry = str_querry + "".join(set(lst_join)) + '{filter} group by {groupby} order by  dat_purchase DESC'
            str_querry = str_querry.format(selected = ','.join(set(lst_selected)),filter = str_filter,groupby = ','.join(set(lst_group_by)))




            rst_data = conn.execute(str_querry).fetchall()

            if not rst_data:
                return Response({'status':1,'lst_data':[]})

            lst_data = []
            for ins_data in rst_data:

                dct_data =dct_data_transfer= dict(ins_data)

                if "first_name" in rst_data[0].keys():
                    dct_data['vchr_staff_name'] = ins_data.first_name + " " +ins_data.last_name


                dct_data_transfer = dct_data.copy()
                dct_data['dat_purchase'] = datetime.strftime(dct_data['dat_purchase'],'%d-%m-%Y')
                if 'imei' in dct_data:
                    dct_data.pop('imei')
                dct_data.pop('tax_value')
                dct_data.pop('int_qty')
                dct_data.pop('dbl_taxable_value')
                dct_data.pop('dbl_total_amount')
                if 'batch' in dct_data:
                    dct_data.pop('batch')





                if 'Imei/Batch' in lst_more_filter:
                    for imei2 in dct_data_transfer['imei']:
                        dct_item = {}
                        dct_item['imei_batch_number']=imei2
                        dct_item['dat_purchase'] = dct_data['dat_purchase']
                        dct_item['quantity'] = 1
                        dct_item['tax_value'] =  dct_data_transfer['tax_value'] /dct_data_transfer['int_qty']
                        dct_item['dbl_taxable_value'] =  dct_data_transfer['dbl_taxable_value'] /dct_data_transfer['int_qty']
                        dct_item['dbl_total_amount'] =  dct_data_transfer['dbl_total_amount'] /dct_data_transfer['int_qty']

                        lst_data.append(dct_item)
                    # import pdb;pdb.set_trace()
                    if dct_data_transfer['batch']:
                        dct_item = {}
                        dct_item['imei_batch_number']=dct_data_transfer['batch']
                        dct_item['dat_purchase'] = dct_data['dat_purchase']
                        dct_item['quantity'] = dct_data_transfer['int_qty']
                        dct_item['tax_value'] =  dct_data_transfer['tax_value']
                        dct_item['dbl_taxable_value'] =  dct_data_transfer['dbl_taxable_value']
                        dct_item['dbl_total_amount'] =  dct_data_transfer['dbl_total_amount']

                        lst_data.append(dct_item)

                else:
                    dct_item = {}
                    dct_item['dat_purchase'] = dct_data['dat_purchase']
                    dct_item['quantity'] = dct_data_transfer['int_qty']
                    dct_item['tax_value'] =  dct_data_transfer['tax_value']
                    dct_item['dbl_taxable_value'] =  dct_data_transfer['dbl_taxable_value']
                    dct_item['dbl_total_amount'] =  dct_data_transfer['dbl_total_amount']







                    lst_data.append(dct_item)

            return Response({'status':1,'lst_data':lst_data})
        except Exception as msg:
            return Response({'status':0,'data':str(msg)})




# class PurchaseReport(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#                 lst_gnr_details = []
#                 dat_from = request.data.get("datFrom")
#                 dat_to= request.data.get("datTo")
#                 lst_branch=[request.user.userdetails.fk_branch_id]
#                 if request.user.userdetails.fk_group.vchr_name.upper() =='ADMIN':
#                     lst_branch = list(Branch.objects.filter().values_list('pk_bint_id',flat=True))
#                 lst_gnr_details = list(GrnDetails.objects.filter(fk_purchase__dat_purchase__date__gte=dat_from,fk_purchase__dat_purchase__date__lte=dat_to,fk_purchase__fk_branch_id__in=lst_branch).exclude(fk_purchase__int_doc_status__in = [-1,4]).extra(select={'date_purchase':"to_char(grn_master.dat_purchase, 'DD-MM-YYYY')"}).values('fk_purchase.pk_bint_id','fk_purchase.vchr_purchase_num','fk_purchase.date_purchase','fk_purchase.dbl_total','fk_purchase.fk_supplier__vchr_name','fk_purchase.fk_branch__vchr_name','fk_purchase.int_approve').order_by('-dat_purchase','-pk_bint_id'))
#                 return Response({'status':'1','data':lst_gnr_details})


class SmartChoiceReport(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dat_date_from = request.data.get('datFrom',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            engine = get_engine()
            conn = engine.connect()
            lst_selected_branch = request.data.get('lstBranch')
            lst_branches =[]
            str_filter = ''
            dct_privilege = get_user_privileges(request)
            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN'):
                if request.user.userdetails.fk_group.vchr_name.upper() in ["BRANCH MANAGER","ASSISTANT BRANCH MANAGER","ASM1","ASM2","ASM3","ASM4"]:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                elif dct_privilege:

                    if dct_privilege.get('lst_branches'):
                        lst_branches = dct_privilege['lst_branches']
                        str_filter += "AND  br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                    else:
                        lst_branches = [request.user.userdetails.fk_branch_id]
                        str_filter += "AND  br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                    if dct_privilege.get('lst_products'):
                        str_filter += "AND  pr.pk_bint_id in ("+str(dct_privilege['lst_products'])[1:-1]+") "
                else :
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND  br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "



            if lst_selected_branch:
                str_filter +=' AND br.pk_bint_id in ('+ str(lst_selected_branch)[1:-1]+')'

            str_query1 ="select br.vchr_name,jsonb_array_elements_text(sd.json_imei) as str_imei,sd.int_qty,item.vchr_item_code,item.vchr_name as item_name,brands.vchr_name as brand_name,br.vchr_name as branch_name,sd.dbl_selling_price as purchase_value from sales_details sd join sales_master sm on sd.fk_master_id=sm.pk_bint_id join item on sd.fk_item_id = item.pk_bint_id join products pr on pr.pk_bint_id=item.fk_product_id join brands on item.fk_brand_id=brands.pk_bint_id join branch br on br.pk_bint_id=sm.fk_branch_id where sd.int_sales_status=2 "
            str_query2 ="select br.vchr_name,jsonb_array_elements_text(sd.json_imei) as str_imei,sd.int_qty,item.vchr_item_code,item.vchr_name,brands.vchr_name,sd.dbl_selling_price as sale_value from sales_details sd join sales_master sm on sd.fk_master_id=sm.pk_bint_id join item on sd.fk_item_id = item.pk_bint_id join brands on item.fk_brand_id=brands.pk_bint_id join branch br on br.pk_bint_id=sm.fk_branch_id join products pr on pr.pk_bint_id=item.fk_product_id where sd.int_sales_status=1 and pr.vchr_name='SMART CHOICE' AND sm.dat_created::DATE  between '"+dat_date_from+"' and '"+dat_date_to+"'"
            str_query = "select sale.sale_value,smart_choice.purchase_value,smart_choice.int_qty,smart_choice.item_name,smart_choice.brand_name,smart_choice.str_imei,smart_choice.branch_name,SUM(sale.sale_value+smart_choice.purchase_value) as profit  from ("+str_query1+str_filter+")  smart_choice INNER JOIN ("+str_query2+str_filter+")  sale ON smart_choice.str_imei=sale.str_imei GROUP BY sale.sale_value,smart_choice.purchase_value,smart_choice.int_qty,smart_choice.item_name,smart_choice.brand_name,smart_choice.str_imei,smart_choice.branch_name"
            rst_data = conn.execute(str_query).fetchall()
            lst_data=[]
            for data in rst_data:
                dct_temp = {}
                dct_temp['quantity'] = data['int_qty']
                dct_temp['branch'] = data['branch_name']
                dct_temp['item'] = data['item_name']
                dct_temp['brand'] = data['brand_name']
                dct_temp['imei'] = data['str_imei']
                dct_temp['sold_value'] = data['sale_value']
                dct_temp['purchase_value'] = -data['purchase_value']
                dct_temp['profit']=data['profit']
                lst_data.append(dct_temp)
            if request.data.get('bln_download'):


                if lst_data:
                    try:
                        count = 0
                        dct_report = {'Slno':[],'Branch':[],'Brand':[],'Item':[],
                                'Imei':[],'Quantity':[],'Sold Value':[],'Purchase Value':[],'Profit':[]}
                        for data in lst_data:
                            count += 1
                            dct_report['Slno'].append(count)
                            dct_report['Branch'].append(data['branch'])
                            dct_report['Brand'].append(data['brand'])
                            dct_report['Item'].append(data['item'])
                            dct_report['Imei'].append(data['imei'])
                            dct_report['Quantity'].append(data['quantity'])
                            dct_report['Sold Value'].append(data['sold_value'])
                            dct_report['Purchase Value'].append(data['purchase_value'])
                            dct_report['Profit'].append(data['profit'])

                        df = pd.DataFrame(dct_report)
                        str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_smartchoicereport.xlsx'
                        filename =settings.MEDIA_ROOT+'/'+str_file

                        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                        workbook = writer.book
                        cell_format = workbook.add_format()
                        cell_format.set_align('center')
                        cell_format1 = workbook.add_format()
                        cell_format1.set_align('left')
                        df.to_excel(writer,index=False, sheet_name='SmartChoice Profit Report',columns=['Slno','Branch','Brand','Item','Imei','Quantity','Sold Value','Purchase Value','Profit'],startrow=6, startcol=0)
                        worksheet = writer.sheets['SmartChoice Profit Report']
                        merge_format1 = workbook.add_format({
                            'bold': 20,
                            'border': 1,
                            'align': 'center',
                            'valign': 'vcenter',
                            'font_size':23
                            })

                        merge_format2 = workbook.add_format({
                        'bold': 6,
                        'border': 1,
                        'align': 'left',
                        'valign': 'vleft',
                        'font_size':13
                        })
                        worksheet.merge_range('A1+:I2', 'SmartChoice Profit Report', merge_format1)
                        worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
                        worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
                        worksheet.set_column('B:B', 15,cell_format1)
                        worksheet.set_column('C:C', 15,cell_format1)
                        worksheet.set_column('D:D', 35,cell_format)
                        worksheet.set_column('E:E', 30,cell_format)
                        worksheet.set_column('F:F', 15,cell_format)
                        worksheet.set_column('G:G', 15,cell_format)
                        worksheet.set_column('H:H', 15,cell_format)
                        worksheet.set_column('I:I', 15,cell_format)
                        writer.save()
                        return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                    except Exception as e:
                        return JsonResponse({'status':'0','message':e})
                else:
                    return Response({"status":1, "message":"No Data..."})
            if lst_data:
                return Response({"status":1,"data":lst_data})
            else:
                return Response({"status":1, "message":"No Data...","data":[]})
        except Exception as msg:
            return Response({'status':0,'data':str(msg)})


class SmartChoiceSaleReport(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dat_date_from = request.data.get('datFrom',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            dat_date_to = request.data.get('datTo',datetime.strftime(datetime.now(),'%Y-%m-%d'))
            engine = get_engine()
            conn = engine.connect()
            lst_branch_id = request.data.get('lstBranch')
            str_filter = ''
            dct_privilege = get_user_privileges(request)

            if not (request.user.userdetails.fk_branch.int_type in [2,3] or request.user.userdetails.fk_group.vchr_name=='ADMIN'):
                if request.user.userdetails.fk_group.vchr_name.upper() in ["BRANCH MANAGER","ASSISTANT BRANCH MANAGER","ASM1","ASM2","ASM3","ASM4"]:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "

                elif dct_privilege :

                    if dct_privilege.get('lst_branches'):
                        lst_branches = dct_privilege['lst_branches']
                        str_filter += "AND  br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                    else:
                        lst_branches = [request.user.userdetails.fk_branch_id]
                        str_filter += "AND br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "
                    if dct_privilege.get('lst_products'):
                        str_filter += "AND pr.pk_bint_id in ("+str(dct_privilege['lst_products'])[1:-1]+") "


                else:
                    lst_branches = [request.user.userdetails.fk_branch_id]
                    str_filter += "AND br.pk_bint_id in ("+str(lst_branches)[1:-1]+") "









            if lst_branch_id:
                str_filter +=' AND br.pk_bint_id in ('+ str(lst_branch_id)[1:-1]+')'

            # str_query1 ="select br.vchr_name,jsonb_array_elements_text(sd.json_imei) as str_imei,sd.int_qty,item.vchr_item_code,item.vchr_name as item_name,brands.vchr_name as brand_name,br.vchr_name as branch_name,sd.dbl_selling_price as purchase_value from sales_details sd join sales_master sm on sd.fk_master_id=sm.pk_bint_id join item on sd.fk_item_id = item.pk_bint_id join brands on item.fk_brand_id=brands.pk_bint_id join branch br on br.pk_bint_id=sm.fk_branch_id where sd.int_sales_status=2 AND sm.dat_created::DATE  between '"+dat_date_from+"' and '"+dat_date_to+"'"
            str_query ="select sm.dat_created,br.vchr_name,jsonb_array_elements_text(sd.json_imei) as str_imei,sd.int_qty,sm.vchr_invoice_num as invoice_num,item.vchr_item_code,item.vchr_name as item_name,brands.vchr_name as brand_name,br.vchr_name as branch_name,sd.dbl_selling_price as sale_value,cd.vchr_name as cust_name,cd.int_mobile as cust_no from sales_details sd join sales_master sm on sd.fk_master_id=sm.pk_bint_id join item on sd.fk_item_id = item.pk_bint_id join brands on item.fk_brand_id=brands.pk_bint_id join branch br on br.pk_bint_id=sm.fk_branch_id join products pr on pr.pk_bint_id=item.fk_product_id join sales_customer_details cd on cd.pk_bint_id=sm.fk_customer_id where sd.int_sales_status=1 and pr.vchr_name='SMART CHOICE' AND sm.dat_created::DATE  between '"+dat_date_from+"' and '"+dat_date_to+"'"
            # str_query = "select sale.sale_value,smart_choice.purchase_value,smart_choice.int_qty,smart_choice.item_name,smart_choice.brand_name,smart_choice.str_imei,smart_choice.branch_name,SUM(sale.sale_value+smart_choice.purchase_value) as profit  from ("+str_query1+str_filter+")  smart_choice INNER JOIN ("+str_query2+str_filter+")  sale ON smart_choice.str_imei=sale.str_imei GROUP BY sale.sale_value,smart_choice.purchase_value,smart_choice.int_qty,smart_choice.item_name,smart_choice.brand_name,smart_choice.str_imei,smart_choice.branch_name"
            rst_data = conn.execute(str_query+str_filter).fetchall()
            lst_data=[]
            for data in rst_data:
                dct_temp = {}
                dct_temp['dat_invoice'] = data['dat_created']
                dct_temp['invoice_num'] = data['invoice_num']
                dct_temp['cust_name'] = data['cust_name']
                dct_temp['cust_no'] = data['cust_no']
                dct_temp['quantity'] = data['int_qty']
                dct_temp['branch'] = data['branch_name']
                dct_temp['item'] = data['item_name']
                dct_temp['brand'] = data['brand_name']
                dct_temp['imei'] = data['str_imei']
                dct_temp['sold_value'] = data['sale_value']
                lst_data.append(dct_temp)
            if request.data.get('bln_download'):


                if lst_data:
                    try:
                        count = 0
                        dct_report = {'Slno':[],'Date':[],'Invoice No':[],'Branch':[],'Customer Name':[],'Customer Ph.':[],
                        'Brand':[],'Item':[],'Imei':[],'Quantity':[],'Sale Value':[]}
                        for data in lst_data:
                            count += 1
                            dct_report['Date'].append(data['dat_invoice'].strftime('%d/%m/%Y'))
                            dct_report['Invoice No'].append(data['invoice_num'])
                            dct_report['Customer Name'].append(data['cust_name'])
                            dct_report['Customer Ph.'].append(data['cust_no'])
                            dct_report['Slno'].append(count)
                            dct_report['Branch'].append(data['branch'])
                            dct_report['Brand'].append(data['brand'])
                            dct_report['Item'].append(data['item'])
                            dct_report['Imei'].append(data['imei'])
                            dct_report['Quantity'].append(data['quantity'])
                            dct_report['Sale Value'].append(data['sold_value'])


                        df = pd.DataFrame(dct_report)
                        str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_smartchoicesalereport.xlsx'
                        filename =settings.MEDIA_ROOT+'/'+str_file

                        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                        workbook = writer.book
                        merge_format1 = workbook.add_format({
                            'bold': 20,
                            'border': 1,
                            'align': 'center',
                            'valign': 'vcenter',
                            'font_size':23
                            })

                        merge_format2 = workbook.add_format({
                        'bold': 6,
                        'border': 1,
                        'align': 'left',
                        'valign': 'vleft',
                        'font_size':13
                        })
                        cell_format = workbook.add_format()
                        cell_format.set_align('center')
                        cell_format1 = workbook.add_format()
                        cell_format1.set_align('left')
                        df.to_excel(writer,index=False, sheet_name='SmartChoice Sale Report',columns=['Slno','Date','Invoice No','Branch','Customer Name','Customer Ph.','Brand','Item','Imei','Quantity','Sale Value'],startrow=6, startcol=0)
                        worksheet = writer.sheets['SmartChoice Sale Report']
                        worksheet.merge_range('A1+:K2', 'SmartChoice Sale Report', merge_format1)
                        worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
                        worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
                        worksheet.set_column('B:B', 15,cell_format1)
                        worksheet.set_column('C:C', 15,cell_format1)
                        worksheet.set_column('D:D', 15,cell_format)
                        worksheet.set_column('E:E', 25,cell_format)
                        worksheet.set_column('F:F', 15,cell_format)
                        worksheet.set_column('G:G', 15,cell_format)
                        worksheet.set_column('H:H', 35,cell_format)
                        worksheet.set_column('I:I', 30,cell_format)
                        worksheet.set_column('K:K', 15,cell_format)
                        writer.save()
                        return JsonResponse({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})

                    except Exception as e:
                        return JsonResponse({'status':'0','message':e})
                else:
                    return Response({"status":1, "message":"No Data..."})
            if lst_data:
                return Response({"status":1,"data":lst_data})
            else:
                return Response({"status":1, "message":"No Data...","data":[]})
        except Exception as msg:
            return Response({'status':0,'data':str(msg)})
