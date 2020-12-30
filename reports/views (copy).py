from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from sqlalchemy.orm import sessionmaker
from django.http import JsonResponse
from rest_framework.response import Response
from django.db.models import Q
from collections import OrderedDict
from datetime import datetime

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
import pandas as pd
from django.conf import settings
import copy

from POS import ins_logger
import sys, os

from transaction.models import Transaction

class DailySalesReport(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()

            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            # dat_from = "2019-01-01"
            # dat_to = "2019-05-29"
            #
            int_cust_id  = request.data.get("intCustomerId")
            int_staff_id =  request.data.get("intStaffId")
            lst_more_filter = request.data.get("lst_moreFilter")
            lst_join = []

            dct_querry_var = {"Date":"dat_invoice","Invoice Number":"vchr_invoice_num","Branch":"branch.vchr_name as vchr_branch_name","Customer":"sales_customer_details.vchr_name as vchr_customer_name","Staff":"auth_user.first_name,auth_user.last_name","Product":"products.vchr_name as vchr_product_name","Brand":"brands.vchr_name as vchr_brand_name","Item":"item.vchr_name as vchr_item_name","Imei/Batch":"json_imei->0 as IMEI,vchr_batch as BATCH",'Item Category':'vchr_item_category',
            'Item Category':'vchr_item_category','Item Group':'vchr_item_group','Tax Value':'dbl_tax','Taxable Value':'dbl_amount as dbl_taxable_value'}
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




            str_querry = "select {selected}, sum(sales_details.dbl_selling_price) as dbl_total_amount,sum(sales_details.int_qty) as int_total_qty,item.vchr_item_code as vchr_item_code from sales_details  join sales_master on sales_details.fk_master_id = sales_master.pk_bint_id join item on sales_details.fk_item_id = item.pk_bint_id "
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

            if not request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','PURCHASE MANAGER']:
                str_filter += "AND sales_master.fk_branch_id = "+str(request.user.userdetails.fk_branch_id)+" "

            if request.data.get('lst_product_id'):
                # str_querry+ = ' AND fk_product_id in '+str(request.data.get('lst_product_id')).replace('[','(').replace("]",")")
                str_querry +=  ' AND fk_product_id in ' +str(request.data.get('lst_product_id')).replace('[','(').replace(']',')')
            if request.data.get("lst_brand_id"):
                str_querry +=  ' AND fk_brand_id in ' +str(request.data.get('lst_brand_id')).replace('[','(').replace(']',')')

            if request.data.get("lst_item_category_id"):

                str_querry +=  ' AND fk_item_category_id in ' +str(request.data.get('lst_item_category_id')).replace('[','(').replace(']',')')

                # str_querry+ = " AND fk_item_category_id in "+str(request.data.get("lst_item_category_id")).replace("[","(")

            if request.data.get("lst_item_group_id"):
                # str_querry+ = " AND  in "+str(request.data.get("lst_item_group_id")).replace("[","(")
                str_querry +=  ' AND fk_item_group_id in ' +str(request.data.get('lst_item_group_id')).replace('[','(').replace(']',')')


            if request.data.get("bln_smart_choice"):

                str_querry += 'and int_sales_status!=2'

            if request.data.get("bln_service"):

                str_querry += 'and int_sales_status!=3'


            str_querry = str_querry + "".join(set(lst_join)) + '{filter} group by {groupby},vchr_item_code order by  dat_invoice DESC'
            str_querry = str_querry.format(selected = ','.join(set(lst_selected)),filter = str_filter,groupby = ','.join(set(lst_group_by)))







            rst_data = conn.execute(str_querry).fetchall()

            if not rst_data:
                return Response({'status':1,'lst_data':[]})

            lst_data = []
            for ins_data in rst_data:

                dct_data = dict(ins_data)

                dct_data['dat_invoice'] = datetime.strftime(dct_data['dat_invoice'],'%d-%m-%Y')

                if 'Imei/Batch' in lst_more_filter:

                    dct_data['imei_batch_number']=dct_data['imei'] if dct_data['imei'] else dct_data['batch']


                if "first_name" in rst_data[0].keys():
                    dct_data['vchr_staff_name'] = ins_data.first_name + " " +ins_data.last_name


                lst_data.append(dct_data)

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

            dct_data_selected = {'Product':'br_data.vchr_product_name',
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


            dct_data_group_by = {
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

            str_query = """select {selected} from (
            select 0 as int_transit,bsid.int_qty as int_qty,CASE WHEN bsid.jsn_imei ->>'imei' ='[]' then NULL else (bsid.jsn_imei->>'imei') END as jsn_imei,
            CASE WHEN bsd.jsn_batch_no ->>'batch' ='[]' then NULL else (bsd.jsn_batch_no->>'batch')::TEXT END as jsn_batch_no ,
                                bsm.dat_stock as dat_branch_stock,(NOW()::DATE-(bsm.dat_stock )::DATE)::INTEGER as int_branch_age,
                                grm.dat_purchase as dat_purchase_stock, (NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age,
                                (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,bsm.dat_stock::DATE as dat_stock ,'BRANCH' as vchr_type
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
                            select 0 as int_transit,(grd.int_avail) as int_qty,CASE WHEN grd.jsn_imei_avail ->>'imei_avail' ='[]' then NULL else (grd.jsn_imei_avail->>'imei_avail') END  as jsn_imei,CASE WHEN COALESCE(grd.vchr_batch_no,'')='' then '' else '["' || vchr_batch_no||'"]' end as jsn_batch_no,
                                (grm.dat_purchase)::DATE as dat_branch_stock,(NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_branch_age,
                                (grm.dat_purchase)::DATE as dat_purchase_stock,(NOW()::DATE-(grm.dat_purchase)::DATE)::INTEGER as int_total_age,
                                (br.vchr_code) as vchr_branch_code,(br.pk_bint_id) as int_branch_id,(br.vchr_name) as vchr_branch_name,
                                (it.vchr_item_code) as vchr_item_code, (it.pk_bint_id) as int_item_id,(it.vchr_name) as vchr_item_name,
                                (bd.vchr_code) as vchr_brand_code,(bd.pk_bint_id) as int_brand_id,(bd.vchr_name) as vchr_brand_name,
                                (pd.pk_bint_id) as int_product_id,(pd.vchr_name) as vchr_product_name,(pd.vchr_code) as vchr_product_code,
                                (itg.pk_bint_id) as int_item_group_id,(itg.vchr_item_group) as vchr_item_group_name,
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,grm.dat_purchase::DATE as dat_stock,'GRN' as vchr_type
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
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'TRANSFER' as vchr_type
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
                                (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'BILLED' as vchr_type
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
                            where stf.int_status in (0)) as br_data """
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
            # else:
            #     str_filter +=' AND br_data.int_branch_id = ' +str(request.user.userdetails.fk_branch_id) +''
            #     str_sales_filter +=' AND br.pk_bint_id = ' +str(request.user.userdetails.fk_branch_id) +''
            # if lst_product_id:
            #     str_filter +=' AND br_data.int_product_id in ('+str(lst_product_id)[1:-1]+')'
            #     str_sales_filter +=' AND pd.pk_bint_id in ('+str(lst_product_id)[1:-1]+')'
            #     dct_export_filter['Products'] = list(Products.objects.filter(pk_bint_id__in = lst_product_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
            # if  lst_brand_id:
            #     str_filter +=' AND br_data.int_brand_id in ('+str(lst_brand_id)[1:-1]+')'
            #     str_sales_filter +=' AND bd.pk_bint_id in ('+str(lst_brand_id)[1:-1]+')'
            #     dct_export_filter['Brands'] = list(Brands.objects.filter(pk_bint_id__in = lst_brand_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
            # if lst_item_group_id:
            #     str_filter +=' AND br_data.int_item_group_id in ('+str(lst_item_group_id)[1:-1]+')'
            #     str_sales_filter +=' AND itg.pk_bint_id in ('+str(lst_item_group_id)[1:-1]+')'
            #     dct_export_filter['Item Groups'] =  list(ItemGroup.objects.filter(pk_bint_id__in = lst_item_group_id).annotate(name=Upper('vchr_item_group')).values_list('name',flat=True))
            #
            # if lst_item_cat_id:
            #     str_filter +=' AND br_data.int_item_cat_id in ('+str(lst_item_cat_id)[1:-1]+')'
            #     str_sales_filter +=' AND itc.pk_bint_id in ('+str(lst_item_cat_id)[1:-1]+')'
            #     dct_export_filter['Item Categories'] =list(ItemCategory.objects.filter(pk_bint_id__in = lst_item_cat_id).annotate(name=Upper('vchr_item_category')).values_list('name',flat=True))
            #
            # if lst_item_id:
            #     str_filter +=' AND br_data.int_item_id in ('+str(lst_item_id)[1:-1]+')'
            #     str_sales_filter +=' AND it.pk_bint_id in ('+str(lst_item_id)[1:-1]+')'
            #     dct_export_filter['Items'] = list(Item.objects.filter(pk_bint_id__in = lst_item_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))
            # if lst_branch_id:
            #     str_filter +=' AND br_data.int_branch_id in ('+ str(lst_branch_id)[1:-1]+')'
            #     str_sales_filter +=' AND br.pk_bint_id in ('+ str(lst_branch_id)[1:-1]+')'
            #     dct_export_filter['Branches'] = list(Branch.objects.filter(pk_bint_id__in = lst_branch_id).annotate(name=Upper('vchr_name')).values_list('name',flat=True))

            # str_filter +=' AND br_data.int_transit >= 0'
            #

            str_query = str_query + '{filter} group by {group_by} '
            str_query = str_query.format(selected = ','.join(set(lst_selected)),filter = str_filter,group_by = ','.join(set(lst_group_by)))

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

                                lst_test.append(dct_data.copy())
                                lst_data.append(dct_data.copy())
                        elif ins_data.jsn_batch_no:
                            dct_data['jsn_batch_no'] = eval(ins_data.jsn_batch_no)[0]
                            # import pdb; pdb.set_trace()
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
            dct_sales_data =  {
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
            rst_sales_data = conn.execute(str_sales_query).fetchall()
            if rst_sales_data:
                lst_rst_sales_data = [dict(x) for x in rst_sales_data]
                lst_sales_data_SALE = [x for x in lst_rst_sales_data if x['vchr_sales_type'] == 'SALE' ]

                lst_sales_data_RETURN =  [x for x in lst_rst_sales_data if x['vchr_sales_type'] == 'RETURN' ]

                lst_rest_stock_data = [dict(x) for x in rst_data]
                lst_keys_sales = list(lst_rst_sales_data[0].keys())
                lst_keys_sales.remove('int_qty')
                lst_keys_sales.remove('vchr_sales_type')
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
                                    (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'TRANSFERRED' as vchr_type
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
                                    (itc.pk_bint_id) as int_item_cat_id,(itc.vchr_item_category) as vchr_item_cat_name,stf.dat_transfer::DATE as dat_stock,'RECIEVED' as vchr_type
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
                                # import pdb; pdb.set_trace()
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

                                    lst_stk_TRANSFERRED.remove(dct_stf_data)


                            elif dct_stf_data['vchr_type']=='RECIEVED':
                                dct_temp_stock_data = {}
                                dct_temp_stf_data = {}
                                for key in lst_stock_transfer_keys:
                                    dct_temp_stock_data[key] = dct_stk_data[key]
                                    dct_temp_stf_data[key] = dct_stf_data[key]
                                if dct_temp_stock_data==dct_temp_stf_data:
                                    dct_stk_data['int_qty'] -= dct_stf_data['int_qty']
                                    # import pdb; pdb.set_trace()
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
            if bln_check:
                if request.data.get('blnExport'):
                    data = stock_export_excel(lst_data,request,dct_export_filter)
                    return Response({'status':1,'dct_data':dct_details,'export_data':data,'bln_branch':bln_branch})
                return Response({'status':1,'dct_data':dct_details,'bln_branch':bln_branch})
            if request.data.get('blnExport'):
                data = stock_export_excel(lst_data,request,dct_export_filter)
                return Response({'status':1,'dct_data':dct_details,'stock_data':lst_data,'export_data':data,'bln_branch':bln_branch})
            #
            return Response({'status':1,'stock_data':lst_data})
        except Exception as msg:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(msg, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})

            return Response({'status':0,'data':str(msg)})

def stock_export_excel(lst_data,request,dct_export_filter):
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
                            'Total': 'int_qty_transit_sum'
                             })

        lst_order = ['Branch','Product','Brand','Item Category','Item Group','Item Code','Item Name','Imei/Batch No','Branch Date','First in Date','Stock','In Transit','Branch Age','Total Age','Total']
        lst_keys = lst_data[0].keys()
        lst_headers  = [x for x in lst_order if dct_data_selected.get(x) in  lst_keys]
        # lst_selected = [dct_data_selected.get(x) for x in lst_data[0].keys() if dct_data_selected.get(x) ]
        # lst_index = [x for x in lst_order if x in lst_selected]

        df = pd.DataFrame(lst_data)
        df = pd.DataFrame(lst_data)

        excel_file = settings.MEDIA_ROOT+'/Branch_stock_report.xlsx'
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
        str_report = 'Branch Stock Report'
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
        if request.user.userdetails.fk_branch.int_type  in [2,3] or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN' :
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
        # data = 'media/Branch_stock.xlsx'
        data = settings.HOSTNAME+'/media/Branch_stock_report.xlsx'
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
                lst_for_show=[{'name':data['vchr_name'],'id':data['pk_bint_id']} for data in qry_lst_branch]
                return Response({'status': 1 , 'bln_show_all':True,'branch':lst_for_show})
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
