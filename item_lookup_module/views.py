from django.shortcuts import render

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import IsAuthenticated,AllowAny
from exchange_sales.models import ExchangeStock
from django.contrib.auth.models import User
# import datetime
import json
from datetime import datetime, timedelta,date
from branch.models import Branch
import time
from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
# from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date,case, literal_column,or_,MetaData,desc
import sqlalchemy
import calendar
from django.db.models import Q
from purchase.models import GrnMaster,GrnDetails
from item_category.models import Item
from products.models import Products
from brands.models import Brands
from branch_stock.models import BranchStockMaster,BranchStockDetails,BranchStockImeiDetails,NonSaleable
from supplier.models import Supplier
from POS.dftosql import Savedftosql
from invoice.models import SalesMaster,SalesDetails
from POS import ins_logger
from django.db import transaction
import sys, os

import itertools
from internal_stock.models import StockTransfer,IstDetails
from sales_return.models import SalesReturn
from operator import itemgetter
from django.db.models import Sum,Q
from invoice.models import PartialInvoice
from purchase.models import GrnrDetails,GrnrMaster
BranchSA = Branch.sa
GrnDetailsSA = GrnDetails.sa
GrnMasterSA = GrnMaster.sa
BranchStockMasterSA = BranchStockMaster.sa
BranchStockDetailsSA = BranchStockDetails.sa
BranchStockImeiDetailsSA = BranchStockImeiDetails.sa
SupplierSA = Supplier.sa
ItemSA = Item.sa
ProductsSA = Products.sa
BrandsSA = Brands.sa
SalesMasterSA = SalesMaster.sa

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)

SalesDetailsJS = metadata.tables['sales_details']
BranchStockDetailsJS = metadata.tables['branch_stock_details']
GrnDetailsJS = metadata.tables['grn_details']
# def Session():
#     from aldjemy.core import get_engine
#     engine=get_engine()
#     _Session = sessionmaker(bind=engine)
#     return _Session()


class ItemLookupApiOld(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            session = Connection()
            # dat_from = request.data.get('from_date')
            # dat_to = request.data.get('to_date')
            # dat_today = datetime.strftime(datetime.now(),'%Y-%m-%d')
            # int_interval =  (datetime.strptime(dat_to,'%Y-%m-%d') - datetime.strptime(dat_from,'%Y-%m-%d')).days
            # if request.data.get('strImei'):
            str_imei = request.data.get('str_imei')
            str_batch_num = request.data.get('str_batch_num')

            if str_imei:

                if BranchStockDetails.objects.filter(jsn_imei__contains=({'imei':[str(str_imei)]})):
                    rst_enquiry = session.query(SupplierSA.vchr_name.label("supplier_name"),GrnMasterSA.dat_purchase,BranchSA.vchr_name.label("branch_name"),\
                    GrnDetailsJS.c.int_qty.label("int_quantity"),GrnDetailsJS.c.int_free.label('int_free'),GrnDetailsJS.c.dbl_costprice.label('rate'),GrnDetailsJS.c.int_damaged.label('int_damaged'),ItemSA.vchr_name.label('vchr_item'))\
                    .join(GrnMasterSA,GrnMasterSA.fk_supplier_id == SupplierSA.pk_bint_id)\
                    .join(GrnDetailsJS,GrnDetailsJS.c.fk_purchase_id == GrnMasterSA.pk_bint_id)\
                    .join(BranchStockImeiDetailsSA,BranchStockImeiDetailsSA.fk_grn_details_id == GrnDetailsSA.pk_bint_id)\
                    .join(BranchStockDetailsSA,BranchStockDetailsJS.c.pk_bint_id == BranchStockImeiDetailsSA.fk_details_id)\
                    .join(BranchStockMasterSA,BranchStockMasterSA.pk_bint_id == BranchStockDetailsJS.c.fk_master_id)\
                    .join(BranchSA,BranchSA.pk_bint_id == BranchStockMasterSA.fk_branch_id)\
                    .join(ItemSA,GrnDetailsJS.c.fk_item_id == ItemSA.pk_bint_id)\
                    .filter(BranchStockDetailsJS.c.jsn_imei.contains({"imei": [str(str_imei)]}))\
                    .filter(GrnDetailsJS.c.jsn_imei.contains({"imei": [str(str_imei)]})).order_by(desc(BranchStockMasterSA.dat_stock))
                else:
                    rst_enquiry = session.query(SupplierSA.vchr_name.label("supplier_name"),GrnMasterSA.dat_purchase,BranchSA.vchr_name.label("branch_name"),\
                    GrnDetailsJS.c.int_qty.label("int_quantity"),GrnDetailsJS.c.int_free.label('int_free'),GrnDetailsJS.c.dbl_costprice.label('rate'),GrnDetailsJS.c.int_damaged.label('int_damaged'),ItemSA.vchr_name.label('vchr_item'))\
                    .join(GrnMasterSA,GrnMasterSA.fk_supplier_id == SupplierSA.pk_bint_id)\
                    .join(GrnDetailsJS,GrnDetailsJS.c.fk_purchase_id == GrnMasterSA.pk_bint_id)\
                    .join(BranchSA,BranchSA.pk_bint_id == GrnMasterSA.fk_branch_id)\
                    .join(ItemSA,GrnDetailsJS.c.fk_item_id == ItemSA.pk_bint_id)\
                    .filter(GrnDetailsJS.c.jsn_imei.contains({"imei": [str(str_imei)]}))
                    # .join(BranchStockImeiDetailsSA,BranchStockImeiDetailsSA.fk_grn_details_id == GrnDetailsSA.pk_bint_id)\
                    # .join(BranchStockDetailsSA,BranchStockDetailsJS.c.pk_bint_id == BranchStockImeiDetailsSA.fk_details_id)\
                    # .join(BranchStockMasterSA,BranchStockMasterSA.pk_bint_id == BranchStockDetailsJS.c.fk_master_id)\
                    # .filter(BranchStockDetailsJS.c.jsn_imei.contains({"imei": [str(str_imei)]}))\

                dct_enquiry = {}
                dct_enquiry['lst_item_details'] = []
                for ins_enquiry in rst_enquiry.all():
                    dct_item ={}
                    dct_item['int_quantity'] = ins_enquiry.int_quantity
                    dct_item['int_free'] = ins_enquiry.int_free
                    dct_item['int_damaged'] = ins_enquiry.int_damaged
                    dct_item['vchr_item'] = ins_enquiry.vchr_item
                    dct_item['rate'] = ins_enquiry.rate
                    if SalesDetails.objects.filter(json_imei__contains=str(str_imei)).exists():
                        dct_item['current_status'] = 'SOLD'
                    elif BranchStockDetails.objects.filter(jsn_imei_dmgd__contains=({'imei':[str(str_imei)]})):
                        dct_item['current_status'] = 'DAMAGED'
                    elif BranchStockDetails.objects.filter(jsn_imei_avail__contains=({'imei':[str(str_imei)]})) or GrnDetails.objects.filter(jsn_imei_avail__contains=({'imei_avail':[str(str_imei)]})):
                        dct_item['current_status'] = 'STOCK'
                    dct_enquiry['lst_item_details'].append(dct_item)
                    dct_enquiry['str_supplier_name'] = ins_enquiry.supplier_name
                    dct_enquiry['dat_purchase'] = datetime.strftime(ins_enquiry.dat_purchase,'%d-%m-%Y')
                    dct_enquiry['str_branch_name'] = ins_enquiry.branch_name
                    # dct_enquiry['rate'] = ins_enquiry.rate
                    # if SalesDetails.objects.filter(json_imei__contains=str(str_imei)).exists():
                    #     dct_enquiry['current_status'] = 'SOLD'
                    # elif BranchStockDetails.objects.filter(jsn_imei_dmgd__contains=({'imei':[str(str_imei)]})):
                    #     dct_enquiry['current_status'] = 'DAMAGED'
                    # elif BranchStockDetails.objects.filter(jsn_imei_avail__contains=({'imei':[str(str_imei)]})):
                    #     dct_enquiry['current_status'] = 'STOCK'


                if dct_enquiry['lst_item_details']:
                    session.close()
                    return Response({'status':1,'lst_enquiry':dct_enquiry})
                return Response({'status':0})



            if str_batch_num:
                str_null = None
                rst_enquiry = session.query(SupplierSA.vchr_name.label("supplier_name"),GrnMasterSA.vchr_purchase_num,GrnMasterSA.dat_purchase,BranchSA.vchr_name.label("branch_name"),\
                                            GrnDetailsJS.c.int_avail.label("int_avail"),GrnDetailsJS.c.int_qty.label("int_quantity"),GrnDetailsJS.c.int_free.label('int_free'),GrnDetailsJS.c.dbl_costprice.label('rate'),\
                                            GrnDetailsJS.c.int_damaged.label('int_damaged'),ItemSA.vchr_name.label('vchr_item'),ItemSA.vchr_item_code.label('item_code'),BranchStockDetailsJS.c.jsn_imei_dmgd.label('damaged_imei'),\
                                            BranchStockMasterSA.dat_stock,BranchStockDetailsJS.c.int_qty.label('stock_qty'),\
                                            BranchStockDetailsJS.c.jsn_imei.label('total_imei'))\
                            .join(GrnMasterSA,GrnMasterSA.fk_supplier_id == SupplierSA.pk_bint_id)\
                            .join(GrnDetailsJS,GrnDetailsJS.c.fk_purchase_id == GrnMasterSA.pk_bint_id)\
                            .outerjoin(BranchStockImeiDetailsSA,BranchStockImeiDetailsSA.fk_grn_details_id == GrnDetailsSA.pk_bint_id)\
                            .outerjoin(BranchStockDetailsSA,BranchStockDetailsJS.c.pk_bint_id == BranchStockImeiDetailsSA.fk_details_id)\
                            .outerjoin(BranchStockMasterSA,BranchStockMasterSA.pk_bint_id == BranchStockDetailsJS.c.fk_master_id)\
                            .outerjoin(BranchSA,BranchSA.pk_bint_id == BranchStockMasterSA.fk_branch_id)\
                            .join(ItemSA,GrnDetailsJS.c.fk_item_id == ItemSA.pk_bint_id)\
                            .filter(or_(BranchStockDetailsJS.c.jsn_batch_no.contains({"batch": [str(str_batch_num)]}),BranchStockDetailsJS.c.jsn_batch_no==None))\
                            .filter(GrnDetailsJS.c.vchr_batch_no == str_batch_num)
                # .group_by(SupplierSA.vchr_name,GrnMasterSA.dat_purchase,BranchSA.vchr_name,GrnDetailsJS.c.int_qty,GrnDetailsJS.c.int_qty,ItemSA.vchr_code,BranchStockMasterSA.dat_stock,\
                #             GrnDetailsJS.c.int_avail,GrnDetailsJS.c.int_free,GrnDetailsJS.c.dbl_costprice,GrnDetailsJS.c.int_damaged,ItemSA.vchr_name,BranchStockDetailsJS.c.jsn_imei_dmgd)
                if not rst_enquiry.all():
                    session.close()
                    return Response({'status':'0','message':'No data'})
                dct_enquiry = {}
                dct_enquiry['lst_item_details'] = []
                dct_item ={}
                dct_enquiry['dct_stock_details'] = {}
                for ins_enquiry in rst_enquiry.all():
                    if ins_enquiry.item_code not in dct_item:
                        dct_item[ins_enquiry.item_code] = {}
                        dct_item[ins_enquiry.item_code]['int_quantity'] = ins_enquiry.int_quantity
                        dct_item[ins_enquiry.item_code]['int_free'] = ins_enquiry.int_free
                        dct_item[ins_enquiry.item_code]['int_damaged'] = ins_enquiry.int_damaged
                        dct_item[ins_enquiry.item_code]['int_avail'] = ins_enquiry.int_avail
                        dct_item[ins_enquiry.item_code]['vchr_item'] = ins_enquiry.vchr_item
                        dct_item[ins_enquiry.item_code]['item_code'] = ins_enquiry.item_code
                        dct_item[ins_enquiry.item_code]['rate'] = ins_enquiry.rate
                        dct_item[ins_enquiry.item_code]['branch'] = "---"
                        if ins_enquiry.branch_name:
                            dct_item[ins_enquiry.item_code]['branch'] = [ins_enquiry.branch_name.title()]
                    else:
                        if ins_enquiry.branch_name.title() not in dct_item[ins_enquiry.item_code]['branch']:
                            dct_item[ins_enquiry.item_code]['branch'].append(ins_enquiry.branch_name.title())
                    if ins_enquiry.branch_name:
                        if ins_enquiry.item_code not in dct_enquiry['dct_stock_details']:
                            dct_enquiry['dct_stock_details'][ins_enquiry.item_code] = []
                            dct_stock = {}
                            dct_stock['branch'] = ins_enquiry.branch_name.title()
                            dct_stock['dat_stock'] = datetime.strftime(ins_enquiry.dat_stock,'%d-%m-%Y')
                            dct_stock['qty'] = '---'
                            if ins_enquiry.total_imei['imei']:
                                dct_stock['qty'] = len(ins_enquiry.total_imei['imei'])
                            dct_stock['avail_qty'] = ins_enquiry.stock_qty
                            dct_stock['damaged'] = '---'
                            if ins_enquiry.damaged_imei['imei']:
                                dct_stock['damaged'] = len(ins_enquiry.damaged_imei['imei'])
                            dct_enquiry['dct_stock_details'][ins_enquiry.item_code].append(dct_stock)
                        else:
                            dct_stock = {}
                            dct_stock['branch'] = ins_enquiry.branch_name.title()
                            dct_stock['dat_stock'] = datetime.strftime(ins_enquiry.dat_stock,'%d-%m-%Y')
                            dct_stock['qty'] = '---'
                            if ins_enquiry.total_imei['imei']:
                                dct_stock['qty'] = len(ins_enquiry.total_imei['imei'])
                            dct_stock['avail_qty'] = ins_enquiry.stock_qty
                            dct_stock['damaged'] = '---'
                            if ins_enquiry.damaged_imei['imei']:
                                dct_stock['damaged'] = len(ins_enquiry.damaged_imei['imei'])
                            dct_enquiry['dct_stock_details'][ins_enquiry.item_code].append(dct_stock)

                dct_enquiry['lst_item_details'] = dct_item.values()
                for item in dct_enquiry['lst_item_details']:

                    if not item['branch'] == '---':
                        item['branch'] = ','.join(item['branch'])

                dct_enquiry['str_supplier_name'] = ins_enquiry.supplier_name
                dct_enquiry['dat_purchase'] = datetime.strftime(ins_enquiry.dat_purchase,'%d-%m-%Y')
                dct_enquiry['purchase_no'] = ins_enquiry.vchr_purchase_num
                dct_enquiry['batch_no'] = str_batch_num.upper()


            session.close()
            return Response({'status':1,'lst_enquiry':dct_enquiry})


        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class ItemLookupApi1(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb;pdb.set_trace()
            session = Connection()
            str_imei = request.data.get('imeiNum')
            str_batch_num = request.data.get('batchNum')

            if not str_imei and not str_batch_num:
                session.close()
                return Response({'status':0,'message':'No data given to search'})

            if str_imei:
                dct_data = {}
                dct_data['purchase_details'] = {}
                dct_data['item_details']={}
                dct_data['lst_stock'] = []
                dct_data['sale_data'] = []
                if GrnDetails.objects.filter(jsn_imei__contains=({'imei':[str(str_imei)]})):
                    str_imei_status = "IN WAREHOUSE"
                    if GrnDetails.objects.filter(jsn_imei_dmgd__contains=({'imei_damage':[str(str_imei)]})):
                        str_imei_status = "DAMAGED ITEM"
                    rst_purchase = session.query(SupplierSA.vchr_name.label("supplier_name"),GrnMasterSA.vchr_purchase_num.label('grn_num'),\
                                                GrnMasterSA.dat_purchase,BranchSA.vchr_name.label("branch_name"),GrnDetailsJS.c.vchr_batch_no.label('batch_no'),\
                                                GrnDetailsJS.c.dbl_costprice.label('price'),GrnDetailsJS.c.int_qty.label("int_quantity"),\
                                                GrnDetailsJS.c.int_free.label('int_free'),GrnDetailsJS.c.dbl_costprice.label('rate'),\
                                                GrnDetailsJS.c.int_damaged.label('int_damaged'),ItemSA.vchr_name.label('vchr_item'),\
                                                ProductsSA.vchr_name.label('vchr_product'),BrandsSA.vchr_name.label('vchr_brand'),\
                                                GrnMasterSA.dat_created.label('dat_purchase'))\
                                            .join(GrnMasterSA,GrnMasterSA.fk_supplier_id == SupplierSA.pk_bint_id)\
                                            .join(GrnDetailsJS,GrnDetailsJS.c.fk_purchase_id == GrnMasterSA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == GrnMasterSA.fk_branch_id)\
                                            .join(ItemSA,GrnDetailsJS.c.fk_item_id == ItemSA.pk_bint_id)\
                                            .join(ProductsSA,ProductsSA.pk_bint_id == ItemSA.fk_product_id)\
                                            .join(BrandsSA,BrandsSA.pk_bint_id == ItemSA.fk_brand_id)\
                                            .filter(GrnDetailsJS.c.jsn_imei.contains({"imei": [str(str_imei)]}))
                    if rst_purchase.all():
                        ins_purchase =  rst_purchase.first()
                        if ins_purchase.dat_purchase:
                            dat_purchase = datetime.strftime(ins_purchase.dat_purchase,'%Y-%m-%d')
                        else:
                            dat_purchase = ''
                        dct_data['purchase_details']={'batch_no': ins_purchase.batch_no,
                        'branch_name': ins_purchase.branch_name.title(),
                        'dat_purchase': dat_purchase,
                        'grn_num': ins_purchase.grn_num,
                        'price': ins_purchase.price,
                        'costprice': ins_purchase.rate,
                        'supplier_name': ins_purchase.supplier_name.title()}

                        dct_data['item_details']={'vchr_brand': ins_purchase.vchr_brand.title(),
                        'vchr_item': ins_purchase.vchr_item,
                        'vchr_product': ins_purchase.vchr_product.title()
                        }


                    rst_stock = session.query(BranchStockMasterSA.dat_stock.label('dat_stock'),BranchSA.vchr_name.label('branch_name'))\
                                        .join(BranchSA,BranchSA.pk_bint_id == BranchStockMasterSA.fk_branch_id)\
                                        .join(BranchStockDetailsJS,BranchStockDetailsJS.c.fk_master_id == BranchStockMasterSA.pk_bint_id)\
                                        .filter(BranchStockDetailsJS.c.jsn_imei.contains({"imei": [str(str_imei)]})).order_by(BranchStockMasterSA.pk_bint_id)
                    if rst_stock.all():
                        str_imei_status = 'IN STOCK'
                        for ins_stock in rst_stock.all():
                            dct_stock = {}
                            dct_stock['dat_transfer'] = datetime.strftime(ins_stock.dat_stock,'%Y-%m-%d')
                            dct_stock['branch'] = ins_stock.branch_name.title()
                            dct_data['lst_stock'].append(dct_stock)

                    if BranchStockDetails.objects.filter(jsn_imei_dmgd__contains=({'imei':[str(str_imei)]})):
                        str_imei_status = 'DAMAGED'

                    rst_enquiry = session.query(SalesMasterSA.vchr_invoice_num.label('invoice_num'),SalesMasterSA.dat_invoice.label('invoice_date'),\
                                        SalesDetailsJS.c.dbl_selling_price.label('selling_price'),BranchSA.vchr_name.label('vchr_branch'),\
                                        SalesDetailsJS.c.int_sales_status.label('sale_status'))\
                                        .join(SalesDetailsJS,SalesDetailsJS.c.fk_master_id == SalesMasterSA.pk_bint_id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                        .filter(SalesDetailsJS.c.json_imei.contains([str(str_imei)])).order_by(SalesMasterSA.pk_bint_id)
                    if rst_enquiry.all():
                        for ins_sale in rst_enquiry.all():
                            dct_sale = {}
                            dct_sale['invoice_num'] = ins_sale.invoice_num
                            dct_sale['invoice_date'] = datetime.strftime(ins_sale.invoice_date,'%Y-%m-%d')
                            dct_sale['branch'] = ins_sale.vchr_branch.title()
                            dct_sale['selling_price'] = ins_sale.selling_price
                            if ins_sale.sale_status ==1:
                                str_imei_status = 'SOLD'
                            elif not ins_sale.sale_status:
                                str_imei_status = 'RETURNED'
                            dct_data['sale_data'].append(dct_sale)
                    dct_data['item_details']['item_status'] = str_imei_status
                    session.close()
                    return Response({'status':1,'data':dct_data})

                else:
                    session.close()
                    return Response({'status':2,'message':'Item Not purchased yet'})

            elif str_batch_num:
                dct_data = {}
                dct_data['purchase_details'] = {}
                dct_data['item_details']=[]
                dct_data['lst_stock'] = []
                dct_data['sale_data'] = []
                if GrnDetails.objects.filter(vchr_batch_no=str_batch_num):
                    rst_purchase = session.query(SupplierSA.vchr_name.label("supplier_name"),GrnMasterSA.vchr_purchase_num.label('grn_num'),\
                                                GrnMasterSA.dat_purchase,BranchSA.vchr_name.label("branch_name"),GrnDetailsJS.c.vchr_batch_no.label('batch_no'),\
                                                GrnDetailsJS.c.dbl_costprice.label('price'),GrnDetailsJS.c.int_qty.label("int_quantity"),\
                                                GrnDetailsJS.c.int_free.label('int_free'),GrnDetailsJS.c.dbl_costprice.label('rate'),\
                                                GrnDetailsJS.c.int_damaged.label('int_damaged'),ItemSA.vchr_name.label('vchr_item'),\
                                                ProductsSA.vchr_name.label('vchr_product'),BrandsSA.vchr_name.label('vchr_brand'),\
                                                GrnMasterSA.dat_created.label('dat_purchase'))\
                                            .join(GrnMasterSA,GrnMasterSA.fk_supplier_id == SupplierSA.pk_bint_id)\
                                            .join(GrnDetailsJS,GrnDetailsJS.c.fk_purchase_id == GrnMasterSA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == GrnMasterSA.fk_branch_id)\
                                            .join(ItemSA,GrnDetailsJS.c.fk_item_id == ItemSA.pk_bint_id)\
                                            .join(ProductsSA,ProductsSA.pk_bint_id == ItemSA.fk_product_id)\
                                            .join(BrandsSA,BrandsSA.pk_bint_id == ItemSA.fk_brand_id)\
                                            .filter(GrnDetailsJS.c.vchr_batch_no==str_batch_num)
                    if rst_purchase.all():
                        for ins_purchase in rst_purchase.all():
                            if ins_purchase.dat_purchase:
                                dat_purchase = datetime.strftime(ins_purchase.dat_purchase,'%Y-%m-%d')
                            else:
                                dat_purchase = ''
                            dct_data['purchase_details'] = {'batch_no': ins_purchase.batch_no,
                            'branch_name': ins_purchase.branch_name.title(),
                            'dat_purchase': dat_purchase,
                            'grn_num': ins_purchase.grn_num,
                            'price': ins_purchase.price,
                            'costprice': ins_purchase.rate,
                            'supplier_name': ins_purchase.supplier_name.title()}

                            dct_item_details = {}
                            dct_item_details['vchr_brand'] = ins_purchase.vchr_brand.title()
                            dct_item_details['vchr_item'] = ins_purchase.vchr_item
                            dct_item_details['vchr_product'] =  ins_purchase.vchr_product.title()
                            dct_item_details['int_quantity'] = ins_purchase.int_quantity
                            dct_item_details['int_damaged'] = ins_purchase.int_damaged or 0

                            dct_data['item_details'].append(dct_item_details)

                    rst_stock = BranchStockImeiDetails.objects.filter(fk_grn_details__vchr_batch_no = str_batch_num).values('fk_details__fk_master__dat_stock',\
                                                'fk_details__fk_master__fk_branch__vchr_name','fk_details__fk_transfer_details__fk_transfer__fk_from__vchr_name','int_qty','jsn_imei','fk_details__jsn_imei_avail','fk_details__jsn_imei_dmgd',\
                                                'fk_details__fk_transfer_details__fk_transfer__fk_to__vchr_name')


                    if rst_stock.all():
                        str_imei_status = 'IN STOCK'
                        for ins_stock in rst_stock.all():
                            dct_stock = {}
                            dct_stock['dat_transfer'] = datetime.strftime(ins_stock['fk_details__fk_master__dat_stock'],'%Y-%m-%d')
                            dct_stock['branch'] = ins_stock['fk_details__fk_master__fk_branch__vchr_name'].title()
                            dct_stock['qty'] = ins_stock['int_qty']
                            dct_data['lst_stock'].append(dct_stock)



                    rst_enquiry = session.query(SalesMasterSA.vchr_invoice_num.label('invoice_num'),SalesMasterSA.dat_invoice.label('invoice_date'),\
                                        SalesDetailsJS.c.dbl_selling_price.label('selling_price'),BranchSA.vchr_name.label('vchr_branch'),\
                                        SalesDetailsJS.c.int_sales_status.label('sale_status'))\
                                        .join(SalesDetailsJS,SalesDetailsJS.c.fk_master_id == SalesMasterSA.pk_bint_id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                        .filter(SalesDetailsJS.c.vchr_batch == str_batch_num).order_by(SalesMasterSA.pk_bint_id)

                    if rst_enquiry.all():
                        for ins_sale in rst_enquiry.all():
                            dct_sale = {}
                            dct_sale['invoice_num'] = ins_sale.invoice_num
                            dct_sale['invoice_date'] = datetime.strftime(ins_sale.invoice_date,'%Y-%m-%d')
                            dct_sale['branch'] = ins_sale.vchr_branch.title()
                            dct_sale['selling_price'] = ins_sale.selling_price
                            if ins_sale.sale_status ==1:
                                str_imei_status = 'SOLD'
                            elif not ins_sale.sale_status:
                                str_imei_status = 'RETURNED'
                            dct_data['sale_data'].append(dct_sale)

                    session.close()
                    return Response({'status':1,'data':dct_data})


                else:
                    session.close()
                    return Response({'status':2,'message':'Item Not purchased yet'})



        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ItemLookupApi(APIView):
    """ Looksup details of IMEI.
        param : IMEI bnt_number
        return : Dict of Details
    """
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_imei = request.data.get('imeiNum')
            dct_data = {}
            dct_data[str_imei]={}
            dct_data[str_imei]['details'] = []
            bln_smart_choice = request.data.get("blnSmartchoice")
            if str_imei:
                # ====================================================================
                # Purchased
                rst_purchase = GrnDetails.objects.filter(jsn_imei__imei__icontains = str_imei ).values('dbl_ppu','jsn_imei','fk_purchase__vchr_purchase_num','fk_purchase__fk_branch__vchr_name','fk_purchase__fk_supplier__vchr_name','fk_purchase__fk_supplier__vchr_code','fk_item__vchr_name','fk_purchase__dat_purchase','fk_purchase__dat_created')
                if  rst_purchase:
                    for item in rst_purchase:
                        for imei in item['jsn_imei']['imei']:
                            if str_imei in imei:
                                if imei not in dct_data:
                                    dct_data[imei]={}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']
                                    dct_data[imei]['details'] = [
                                                                  { 'date' : datetime.strftime(item['fk_purchase__dat_created'],'%d-%m-%Y') if item['fk_purchase__dat_created'] else None,
                                                                    'dat_key' :item['fk_purchase__dat_created'],
                                                                    'branch' : item['fk_purchase__fk_branch__vchr_name'] ,
                                                                    'action' : 'PURCHASE',
                                                                    'remark' : 'Purchased at '+(item['fk_purchase__fk_branch__vchr_name'] or "--")+' from '+str(item['fk_purchase__fk_supplier__vchr_code'])+' - '+ str(item['fk_purchase__fk_supplier__vchr_name']).upper() + ' with respect to ' + (item['fk_purchase__vchr_purchase_num'] or "--")
                                                                  }
                                                                ]
                                else:
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                    dct_details = {}
                                    dct_details =  { 'date' : datetime.strftime(item['fk_purchase__dat_created'],'%d-%m-%Y'),
                                                     'dat_key' :item['fk_purchase__dat_created'],
                                                     'branch' : item['fk_purchase__fk_branch__vchr_name'] ,
                                                     'action' : 'PURCHASE',
                                                     'remark' : 'Purchased at '+(item['fk_purchase__fk_branch__vchr_name'] or "--")+' from '+str(item['fk_purchase__fk_supplier__vchr_code'])+' - '+ str(item['fk_purchase__fk_supplier__vchr_name']).upper() + ' with respect to ' +  (item['fk_purchase__vchr_purchase_num'] or "--")
                                                    }
                                    dct_data[imei]['details'].append(dct_details)
                            else:
                                continue
                # =======================================================================================================
                # Exchange
                rst_exchange = BranchStockDetails.objects.filter(jsn_imei__imei__icontains = str_imei,fk_transfer_details_id = None).values('fk_master__dat_stock','fk_master__fk_branch__vchr_name','fk_item__vchr_name','jsn_imei')
                if rst_exchange:
                    for item in rst_exchange:
                        for imei in item['jsn_imei']['imei']:
                            if str_imei in imei:
                                if imei not in dct_data:
                                    dct_data[imei]={}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']
                                    dct_data[imei]['details'] = [
                                                                  { 'date' : datetime.strftime(item['fk_master__dat_stock'],'%d-%m-%Y'),
                                                                    'dat_key' :item['fk_master__dat_stock'],
                                                                    'branch' : item['fk_master__fk_branch__vchr_name'] ,
                                                                    'action' : 'EXCHANGE',
                                                                    'remark' : 'Exchange taken at '+item['fk_master__fk_branch__vchr_name']
                                                                  }
                                                                ]
                                else:
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                    dct_details = {}
                                    dct_details =  { 'date' : datetime.strftime(item['fk_master__dat_stock'],'%d-%m-%Y'),
                                                     'dat_key' :item['fk_master__dat_stock'],
                                                     'branch' : item['fk_master__fk_branch__vchr_name'] ,
                                                     'action' : 'EXCHANGE',
                                                     'remark' : 'Exchanged at '+item['fk_master__fk_branch__vchr_name']
                                                    }
                                    dct_data[imei]['details'].append(dct_details)
                            else:
                                continue

                # =====================================================================================================
                # Transfered
                rst_transfer = IstDetails.objects.filter(jsn_imei__imei__icontains = str_imei).values('fk_transfer__dat_transfer','fk_transfer__dat_created','fk_transfer__vchr_stktransfer_num','fk_item__vchr_name','fk_transfer__fk_from__vchr_name','fk_transfer__fk_to__vchr_name','jsn_imei','fk_transfer_id')

                if rst_transfer:
                    for item in rst_transfer:
                        for imei in item['jsn_imei']['imei']:
                            if str_imei in imei:
                                int_status = StockTransfer.objects.filter(pk_bint_id = item['fk_transfer_id']).values('int_status')
                                if imei not in dct_data:
                                    dct_data[imei]={}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']

                                    if int_status[0]['int_status'] == 0:
                                        dct_data[imei]['details'] = [
                                                                      { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                                        'dat_key' : item['fk_transfer__dat_created'],
                                                                        'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                                        'action' : 'BILLED',
                                                                        'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                                      }
                                                                    ]
                                    elif int_status[0]['int_status'] == 1:
                                        dct_data[imei]['details'] = [
                                                                      { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                                        'dat_key' : item['fk_transfer__dat_created'],
                                                                        'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                                        'action' : 'TRANSFERRED',
                                                                        'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                                      }
                                                                    ]
                                    elif int_status[0]['int_status'] == 2:
                                        dct_data[imei]['details'] = [
                                                                      { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                                        'dat_key' : item['fk_transfer__dat_created'],
                                                                        'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                                        'action' : 'RECEIVED',
                                                                        'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                                      }
                                                                    ]
                                    elif int_status[0]['int_status'] == 3:
                                        dct_data[imei]['details'] = [
                                                                      { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                                        'dat_key' : item['fk_transfer__dat_created'],
                                                                        'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                                        'action' : 'ACKNOWLEDGED',
                                                                        'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                                      }
                                                                    ]


                                else:
                                    if int_status[0]['int_status'] == 0:
                                        dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                        dct_details = {}
                                        dct_details =  { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                         'dat_key' : item['fk_transfer__dat_created'],
                                                         'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                         'action' : 'BILLED',
                                                         'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                       }
                                    elif int_status[0]['int_status'] == 1:
                                        dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                        dct_details = {}
                                        dct_details =  { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                         'dat_key' : item['fk_transfer__dat_created'],
                                                         'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                         'action' : 'TRANSFERRED',
                                                         'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                       }
                                    elif int_status[0]['int_status'] == 2:
                                        dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                        dct_details = {}
                                        dct_details =  { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                         'dat_key' : item['fk_transfer__dat_created'],
                                                         'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                         'action' : 'RECEIVED',
                                                         'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                       }
                                    elif int_status[0]['int_status'] == 3:
                                        dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                        dct_details = {}
                                        dct_details =  { 'date' : datetime.strftime(item['fk_transfer__dat_created'],'%d-%m-%Y'),
                                                         'dat_key' : item['fk_transfer__dat_created'],
                                                         'branch' : item['fk_transfer__fk_from__vchr_name'] ,
                                                         'action' : 'ACKNOWLEDGED',
                                                         'remark' : 'Transfered to '+item['fk_transfer__fk_to__vchr_name']+ ' from ' +item['fk_transfer__fk_from__vchr_name']+ ' with respect to ' + item['fk_transfer__vchr_stktransfer_num']
                                                       }
                                    dct_data[imei]['details'].append(dct_details)


                # =============================================================================================================================
                # sales
                rst_sales = SalesDetails.objects.filter(json_imei__icontains = str_imei,int_sales_status = 1).values('fk_master__dat_invoice','fk_master__dat_created','fk_master__vchr_invoice_num','fk_master__fk_customer__vchr_name','fk_master__fk_branch__vchr_name','fk_item__vchr_name','json_imei')
                if rst_sales:
                    for item in rst_sales:
                        for imei in item['json_imei']:
                            if str_imei in imei:
                                if imei not in dct_data:
                                    dct_data[imei]={}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']
                                    dct_data[imei]['details'] = [
                                                                    { 'date' : datetime.strftime(item['fk_master__dat_created'],'%d-%m-%Y'),
                                                                      'dat_key' :item['fk_master__dat_created'],
                                                                      'branch' : item['fk_master__fk_branch__vchr_name'] ,
                                                                      'action' : 'SOLD',
                                                                      'remark' : 'Sold to '+item['fk_master__fk_customer__vchr_name']+ ' with respect to ' + item['fk_master__vchr_invoice_num']
                                                                    }
                                                                ]
                                else:
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                    dct_details = {}
                                    dct_details =   { 'date' : datetime.strftime(item['fk_master__dat_created'],'%d-%m-%Y'),
                                                      'dat_key' :item['fk_master__dat_created'],
                                                      'branch' : item['fk_master__fk_branch__vchr_name'] ,
                                                      'action' : 'SOLD',
                                                      'remark' : 'Sold to '+item['fk_master__fk_customer__vchr_name']+ ' with respect to ' + item['fk_master__vchr_invoice_num']
                                                    }
                                    dct_data[imei]['details'].append(dct_details)
                # ======================================================================================================
                # sales return

                rst_sales = SalesReturn.objects.filter(jsn_imei__icontains = str_imei).values('fk_item__vchr_name','fk_sales__vchr_invoice_num','dat_returned','fk_sales__fk_branch__vchr_name','fk_sales__fk_customer__vchr_name','jsn_imei','dat_created')

                if rst_sales:
                    for item in rst_sales:
                        for imei in item['jsn_imei']:
                            if str_imei in imei:
                                if imei not in dct_data:
                                    dct_data[imei]={}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']
                                    dct_data[imei]['details'] = [
                                                                    { 'date' : datetime.strftime(item['dat_created'],'%d-%m-%Y'),
                                                                      'dat_key' :item['dat_created'],
                                                                      'branch' : item['fk_sales__fk_branch__vchr_name'] ,
                                                                      'action' : 'SALES RETURN',
                                                                      'remark' : 'Sales Return from  '+item['fk_sales__fk_customer__vchr_name']+ ' with respect to ' + item['fk_sales__vchr_invoice_num']
                                                                    }
                                                                ]

                                else:
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                    dct_details = {}
                                    dct_details =  { 'date' : datetime.strftime(item['dat_created'],'%d-%m-%Y'),
                                                     'dat_key' :item['dat_created'],
                                                     'branch' : item['fk_sales__fk_branch__vchr_name'] ,
                                                     'action' : 'SALES RETURN',
                                                     'remark' : 'Sales Return from  '+item['fk_sales__fk_customer__vchr_name']+ ' with respect to ' + item['fk_sales__vchr_invoice_num']
                                                    }
                                    dct_data[imei]['details'].append(dct_details)
                # =================================================================================================================
                # Non saleable and salable
                rst_non_salable = NonSaleable.objects.filter(Q(jsn_non_saleable__icontains = str_imei)|Q(jsn_status_change__icontains = str_imei)).values('pk_bint_id','int_status','jsn_non_saleable','fk_branch__vchr_name','dat_created','dat_updated','fk_item_id__vchr_name','jsn_status_change','fk_created__username','fk_updated__username','vchr_remarks')

                dct_non_sale = {}
                dct_sale = {}
                if rst_non_salable:
                    for item in rst_non_salable:
                        if item['jsn_non_saleable']:
                            for imei in item['jsn_non_saleable']:
                                if str_imei in imei:
                                    # if imei not in dct_non_sale:
                                        if not dct_non_sale.get(imei):
                                            dct_non_sale[imei]={}
                                        dct_non_sale[imei]['item'] = item['fk_item_id__vchr_name']
                                        if not dct_non_sale[imei].get('details'):
                                            dct_non_sale[imei]['details'] = {}
                                        dct_non_sale[imei]['details'][item['dat_created']]  =  { 'date' : datetime.strftime(item['dat_created'],'%d-%m-%Y'),
                                                                                                 'dat_key' : item['dat_created'],
                                                                                                 'branch' : item['fk_branch__vchr_name'] ,
                                                                                                 'action' : 'NON SALEABLE',
                                                                                                 'remark' : 'Changed to Non Saleable by '+ item['fk_created__username']+' due to the reason :'+ item['vchr_remarks']
                                                                                               }

                        if item['jsn_status_change']:
                            for imei in item['jsn_status_change']:
                                if (str_imei in imei)  and (item['int_status']==1):
                                    # if imei not in dct_sale:
                                        if not dct_sale.get(imei):
                                            dct_sale[imei]={}
                                        dct_sale[imei]['item'] = item['fk_item_id__vchr_name']
                                        if not dct_sale[imei].get('details'):
                                            dct_sale[imei]['details'] = {}
                                        dct_sale[imei]['details'][item['dat_updated']] =  { 'date' : datetime.strftime(item['dat_updated'],'%d-%m-%Y'),
                                                                                            'dat_key' : item['dat_updated'],
                                                                                            'branch' : item['fk_branch__vchr_name'] ,
                                                                                            'action' : 'SALEABLE',
                                                                                            'remark' : 'Changed to Saleable by '+ item['fk_updated__username']+' due to the reason :'+ item['vchr_remarks']
                                                                                          }


                # =================================================================================================================

                dct_saleable_nonsaleabe = {}
                bln_saleable = False
                temp = dct_sale
                lst_sales_key = []
                dat_saleable = datetime.now()

                for imei,data in dct_non_sale.items():
                    lst_non_saleable = sorted(data['details'].keys())
                    for item in lst_non_saleable:
                        if imei not in dct_saleable_nonsaleabe :
                           dct_saleable_nonsaleabe[imei] = {}
                           dct_saleable_nonsaleabe[imei]['details'] = {item:data['details'][item]}
                           bln_saleable = False

                        elif (bln_saleable) and (item > dat_saleable):
                           dct_saleable_nonsaleabe[imei]['details'][item] = data['details'][item]
                           bln_saleable = False

                        if imei in dct_sale:
                            if dct_sale[imei]['details']:
                               lst_sales_key = sorted(list(temp[imei]['details'].keys()))
                               dat_saleable = lst_sales_key[0]
                               dct_saleable_nonsaleabe[imei]['details'][lst_sales_key[0]] = temp[imei]['details'][lst_sales_key[0]]
                               del temp[imei]['details'][lst_sales_key[0]]
                               bln_saleable = True

                for element in dct_saleable_nonsaleabe:
                    dct_data[element]['details'].extend([dct_saleable_nonsaleabe[element]['details'][item] for item in dct_saleable_nonsaleabe[element]['details']])

                #---------------------------------------------------------------------------------------------
                #----------------partial invoice (Invoice rejected and Bajaj finance (imei rejected))-----------------------------------------------------------------------------
                ins_partial_inv = PartialInvoice.objects.filter((Q(int_active = -1)|Q(int_status = 11)),json_data__icontains=str(str_imei)).values().first()
                # import pdb;pdb.set_trace()
                if ins_partial_inv :
                    # for ins_partial_inv in ins_partial_inv:
                    for item in ins_partial_inv['json_data']['lst_items']:
                        for imei in  item['json_imei']['imei']:
                            if imei== str(str_imei):
                                if  ins_partial_inv['int_status'] == 11 :
                                    if item['vchr_enquiry_status'] == 'IMEI REJECTED':
                                        dct_info = { 'date' : datetime.strftime(item['dat_created'],'%d-%m-%Y'),
                                                        'dat_key' : ins_partial_inv['dat_created'],
                                                        'branch' : ins_partial_inv['json_data']['str_branch'] ,
                                                        'action' : 'IMEI REJECTED',
                                                        'remark' : 'The imei has rejected due to the reason :'+ (item.get('str_remarks') or item.get('vchr_remarks')or " ")}
                                        if imei not in dct_data:
                                            dct_data[imei]={}
                                            dct_data[imei]['item'] = item['vchr_item_name']
                                            dct_data[imei]['details'] = dct_info
                                        else :
                                            dct_data[imei]['details'].append(dct_info)


                                elif ins_partial_inv['int_active'] == -1:
                                    dct_info = { 'date' : datetime.strftime(ins_partial_inv['dat_created'],'%d-%m-%Y'),
                                                    'dat_key' : ins_partial_inv['dat_created'],
                                                    'branch' : ins_partial_inv['json_data']['str_branch'] ,
                                                    'action' : 'IMEI REJECTED',
                                                    'remark' : 'The imei has rejected due to the reason :'+ ( ins_partial_inv['json_data'].get('str_remarks') or item.get('vchr_remarks')or " ") }
                                    if imei not in dct_data:
                                        dct_data[imei]={}
                                        dct_data[imei]['item'] = item['vchr_item_name']
                                        dct_data[imei]['details'] = dct_info
                                    else :
                                        dct_data[imei]['details'].append(dct_info)

                # import pdb; pdb.set_trace()
                ins_goods_retrun = GrnrDetails.objects.filter(jsn_imei__contains = str(str_imei)).values('jsn_imei','fk_master_id__dat_purchase_return','fk_master_id__fk_branch_id__vchr_name','fk_master_id__vchr_purchase_return_num')
                if ins_goods_retrun:
                    for item in ins_goods_retrun:
                        dct_data[str_imei]['details'] = [{ 'date' : datetime.strftime(item['fk_master_id__dat_purchase_return'],'%d-%m-%Y'),
                                                    'dat_key' : item['fk_master_id__dat_purchase_return'],
                                                    'branch' : item['fk_master_id__fk_branch_id__vchr_name'],
                                                    'action' : 'GOODS RETURN',
                                                    'remark' : 'Goods Retruned whith respect to document number : '+ item['fk_master_id__vchr_purchase_return_num'].split('-')[2]}

                                                    ]

                if bln_smart_choice:
                    ins_exchange_data = ExchangeStock.objects.filter(jsn_imei__icontains = str(str_imei)).values('jsn_imei','dat_exchanged','fk_branch_id__vchr_name','fk_sales_details_id__fk_master_id__fk_customer_id__vchr_name','fk_sales_details_id__fk_master_id__vchr_invoice_num','fk_item__vchr_name')
                    if ins_exchange_data:
                        for item in ins_exchange_data:
                            for imei in item['jsn_imei']:
                                if imei not in dct_data:
                                    dct_data[imei]={}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']


                                    dct_data[imei]['details'] = [{ 'date' : datetime.strftime(item['dat_exchanged'],'%d-%m-%Y'),
                                                                 'dat_key' : item['dat_exchanged'],
                                                                 'branch' : item['fk_branch_id__vchr_name'],
                                                                 'action' : 'EXCHANGE',
                                                                 'remark' : 'Exchange by '+item['fk_sales_details_id__fk_master_id__fk_customer_id__vchr_name'].title()+' with respect to '+item['fk_sales_details_id__fk_master_id__vchr_invoice_num']}

                                                                 ]

                                else:
                                    dct_details = {}
                                    dct_data[imei]['item'] = item['fk_item__vchr_name']#freddy added to test
                                    dct_info = { 'date' : datetime.strftime(item['dat_exchanged'],'%d-%m-%Y'),
                                                 'dat_key' : item['dat_exchanged'],
                                                 'branch' : item['fk_branch_id__vchr_name'],
                                                 'action' : 'EXCHANGE',
                                                 'remark' : 'Exchange by '+item['fk_sales_details_id__fk_master_id__fk_customer_id__vchr_name'].title()+' with respect to '+item['fk_sales_details_id__fk_master_id__vchr_invoice_num']}

                                    dct_data[imei]['details'].append(dct_info)


                ins_service_data = SalesDetails.objects.filter(json_imei = [str(str_imei)],int_sales_status = 3).values('fk_item_id__vchr_item_code','fk_master_id__dat_created','fk_master_id__fk_customer_id__vchr_name','fk_master_id__fk_branch_id__vchr_name','fk_master_id__vchr_remarks','fk_master_id__vchr_invoice_num')
                for item in ins_service_data:
                    vchr_remarks = ''
                    if item['fk_item_id__vchr_item_code'] =='GDC00001':
                        vchr_remarks = 'Item is given for service by '+item['fk_master_id__fk_customer_id__vchr_name'].title()+' with respect to '+item['fk_master_id__vchr_invoice_num']+'(GDOT)'
                    elif item['fk_item_id__vchr_item_code'] =='GDC00002':
                        vchr_remarks = 'Item is given for service by '+item['fk_master_id__fk_customer_id__vchr_name'].title()+' with respect to '+item['fk_master_id__vchr_invoice_num']+'(GDEW)'
                    else:
                        vchr_remarks = 'Item is given for service by '+item['fk_master_id__fk_customer_id__vchr_name'].title()+' with respect to '+item['fk_master_id__vchr_invoice_num']
                    dct_info = { 'date' : datetime.strftime(item['fk_master_id__dat_created'],'%d-%m-%Y'),
                                 'dat_key' : item['fk_master_id__dat_created'],
                                 'branch' : item['fk_master_id__fk_branch_id__vchr_name'],
                                 'action' : 'SERVICE',
                                 'remark' : vchr_remarks}

                    dct_data[str_imei]['details'].append(dct_info)


                # import pdb; pdb.set_trace()
                if dct_data:
                    for imei in dct_data:
                        dct_data[imei]['details'] = sorted(dct_data[imei]['details'], key=itemgetter('dat_key'))

                    return Response({'status':1,'dct_data':dct_data})
                else:
                    return Response({'status':0,'message':'No data'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
