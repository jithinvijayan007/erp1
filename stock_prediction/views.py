from django.shortcuts import render

# Create your views here.
from collections import Counter
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import OrderedDict
import copy
from django.conf import settings
from rest_framework.permissions import IsAuthenticated,AllowAny
# from user_app.models import UserModel
from django.contrib.auth.models import User
# import datetime
from datetime import datetime, timedelta,date
from branch.models import Branch
import time
from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
# from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date,case, literal_column,or_,MetaData
import sqlalchemy
from sqlalchemy.sql.expression import literal,union_all
import calendar
import pandas as pd
import numpy as np
from purchase.models import GrnMaster,GrnDetails
from branch_stock.models import BranchStockMaster,BranchStockDetails,BranchStockImeiDetails
from invoice.models import SalesMaster,SalesDetails
from item_category.models import Item
from brands.models import Brands
from supplier.models import Supplier
# from POS.dftosql import Savedftosql
from POS import ins_logger
import sys, os
from django.db.models import Q,F,CharField,Case,When,Value,Sum

BranchSA = Branch.sa
GrnDetailsSA = GrnDetails.sa
GrnMasterSA = GrnMaster.sa
BranchStockMasterSA = BranchStockMaster.sa
BranchStockDetailsSA = BranchStockDetails.sa
BranchStockImeiDetailsSA = BranchStockImeiDetails.sa
SupplierSA = Supplier.sa
SalesDetailsSA = SalesDetails.sa
SalesMasterSA = SalesMaster.sa
BrandsSA = Brands.sa
ItemsSA = Item.sa



# sqlalobj = Savedftosql('','')
# engine = sqlalobj.engine
# metadata = MetaData()
# metadata.reflect(bind=engine)
# Connection = sessionmaker()
# Connection.configure(bind=engine)

# BranchStockDetailsJS = metadata.tables['branch_stock_details']
# GrnDetailsJS = metadata.tables['grn_details']
def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()


class StockPrediction(APIView):
    def post(self,request):
        try:
            session = Session()
            # import pdb;pdb.set_trace()
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')
            # dat_from = '2019-05-03'
            # dat_to = '2019-05-05'
            lst_branch = request.data.get('lstBranch')
            lst_item = request.data.get('lstItem')
            dat_today = datetime.strftime(datetime.now(),'%Y-%m-%d')
            int_interval =  (datetime.strptime(dat_to,'%Y-%m-%d') - datetime.strptime(dat_from,'%Y-%m-%d')).days
            if not int_interval:
                int_interval = 1
            rst_stock_details = session.query(ItemsSA.pk_bint_id.label('item_id'),BranchSA.vchr_name.label('branch'),\
                                ItemsSA.vchr_name.label('item'),BranchSA.pk_bint_id.label('branch_id'),\
                                func.sum(func.coalesce(BranchStockDetailsSA.int_qty,0)).label('int_stock_qty'))\
                                .outerjoin(BranchStockDetailsSA,BranchStockDetailsSA.fk_item_id == ItemsSA.pk_bint_id)\
                                .join(BranchStockMasterSA,BranchStockMasterSA.pk_bint_id == BranchStockDetailsSA.fk_master_id)\
                                .join(BranchSA,BranchSA.pk_bint_id == BranchStockMasterSA.fk_branch_id)\
                                .group_by(ItemsSA.pk_bint_id,BranchSA.vchr_name,BranchSA.pk_bint_id,ItemsSA.vchr_name).subquery()

            rst_sales_details = session.query(ItemsSA.pk_bint_id.label('item_id'),BranchSA.vchr_name.label('branch'),\
                                ItemsSA.vchr_name.label('item'),BranchSA.pk_bint_id.label('branch_id'),\
                                func.sum(func.coalesce(SalesDetailsSA.int_qty,0)).label('int_sale_qty'))\
                                .outerjoin(SalesDetailsSA,SalesDetailsSA.fk_item_id == ItemsSA.pk_bint_id)\
                                .join(SalesMasterSA,SalesMasterSA.pk_bint_id == SalesDetailsSA.fk_master_id)\
                                .join(BranchSA,BranchSA.pk_bint_id == SalesMasterSA.fk_branch_id)\
                                .group_by(ItemsSA.pk_bint_id,BranchSA.vchr_name,BranchSA.pk_bint_id,ItemsSA.vchr_name).subquery()

            rst_stock_sale = session.query(rst_stock_details.c.item,rst_stock_details.c.branch,rst_stock_details.c.int_stock_qty,\
                                rst_sales_details.c.int_sale_qty)\
                                .outerjoin(rst_sales_details,and_(rst_stock_details.c.item_id == rst_sales_details.c.item_id,rst_stock_details.c.branch_id == rst_sales_details.c.branch_id))

            if lst_branch:
                rst_stock_sale = rst_stock_sale.filter(rst_stock_details.c.branch_id.in_(lst_branch),rst_sales_details.c.branch_id.in_(lst_branch))
            if lst_item:
                rst_stock_sale = rst_stock_sale.filter(rst_stock_details.c.item_id.in_(lst_item),rst_sales_details.c.item_id.in_(lst_item))


            if not rst_stock_sale.all():
                session.close()
                return Response({'status':'empty','message':'No data'})

            lst_data =[]
            int_rol = 1
            if request.data.get('intMsid'):
                int_rol = int(request.data.get('intMsid'))
            for ins_data in rst_stock_sale.all():
                dct_data = {}
                dct_data['branch'] = ins_data.branch.title()
                dct_data['item'] = ins_data.item.title()
                dct_data['avg_sale'] = 0
                if ins_data.int_sale_qty:
                    dct_data['avg_sale'] = ins_data.int_sale_qty/int_interval
                dct_data['stock_in_demand'] = dct_data['avg_sale']*int_rol
                # dct_data['stock_needed'] = dct_data['avg_sale']*int_rol
                dct_data['current_stock'] = ins_data.int_stock_qty
                dct_data['stock_needed'] = 0
                dct_data['bln_stock'] = False

                if (dct_data['stock_in_demand']-dct_data['current_stock'])>0:
                    dct_data['stock_needed'] = dct_data['stock_in_demand']-dct_data['current_stock']
                    dct_data['bln_stock'] = True
                lst_data.append(dct_data)
            session.close()
            return Response({'status':'1','data':lst_data})


        except Exception as e:
            session.close()
            return Response({'status':'0','message':str(e)})



class ItemTypeahead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_items = []
            if str_search_term != -1:
                ins_items = Item.objects.filter(Q(vchr_name__icontains=str_search_term)\
                | Q(vchr_item_code__icontains=str_search_term),int_status = 0).values('pk_bint_id','vchr_name','vchr_item_code')
                if ins_items:
                    for itr_item in ins_items:
                        dct_item = {}
                        # dct_item['code'] = itr_item['vchr_code'].upper()
                        dct_item['name'] = itr_item['vchr_name'].title()+'-'+itr_item['vchr_item_code'].upper()
                        dct_item['id'] = itr_item['pk_bint_id']
                        lst_items.append(dct_item)
                return Response({'status':'1','data':lst_items})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class BranchList(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_branch =[]
            lst_branch = list(Branch.objects.filter(int_status =0).values('pk_bint_id','vchr_name','vchr_code','fk_states_id'))
            return Response({'status':'1','lst_branch':lst_branch})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})
