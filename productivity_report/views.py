from collections import Counter
from aldjemy.core import get_engine
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from POS import ins_logger
from rest_framework.permissions import IsAuthenticated,AllowAny
# from enquiry.models import EnquiryMaster,Flights,AddAttachments,Document,Hotel,Visa,Transport,Package,Forex,Other,TravelInsurance,Rooms,Train
from enquiry.models import EnquiryMaster,AddAttachments,Document
# from software.models import AccountingSoftware,EmployeeManagement,EnquiryTrack,HrSolutions
# from inventory.models import Brands,Items,Products
from products.models import Products
from brands.models import Brands
from item_category.models import Item as Items
from userdetails.models import UserDetails as UserModel
# from kct_package.models import Kct
from customer.models import CustomerDetails as CustomerModel
from branch.models import Branch
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.http import JsonResponse
import random
# from export_excel.views import export_excel
from collections import OrderedDict
from priority.models import Priority
from source.models import Source
from sqlalchemy import case, literal_column, desc, tuple_, select, table, column
from sqlalchemy.orm.session import sessionmaker
import aldjemy
from sqlalchemy.orm import mapper,aliased
from sqlalchemy import and_,func,cast,Date
from sqlalchemy.sql.expression import literal,union_all

# from enquiry.views import fun_mobile
# from enquiry.views import fun_mobile
# from enquiry.views import fun_automobile_data,get_perm_data

from sqlalchemy.types import TypeDecorator,BigInteger
from enquiry_mobile.models import MobileEnquiry, TabletEnquiry, ComputersEnquiry, AccessoriesEnquiry,ItemEnquiry
# from enquiry_solar.models import ProductType,ProductBrand, ProductCategory, ProductCategoryVariant, ProductEnquiry

from collections import OrderedDict
import numpy as np
import time
# from POS.graph import *
from django.db.models import Q
from globalMethods import show_data_based_on_role,get_user_products

EnquiryMasterSA = EnquiryMaster.sa
BranchSA = Branch.sa
CustomerModelSA = CustomerModel.sa
AuthUserSA = User.sa
UserModelSA = UserModel.sa
# FlightsSA = Flights.sa
# AddAttachmentsSA = AddAttachments.sa
DocumentSA = Document.sa
# HotelSA = Hotel.sa
# VisaSA = Visa.sa
# TransportSA = Transport.sa
# PackageSA = Package.sa
# ForexSA = Forex.sa
# OtherSA = Other.sa
# TravelInsuranceSA = TravelInsurance.sa
# RoomsSA = Rooms.sa
# TrainSA = Train.sa
# KctSA = Kct.sa
# PrioritySA=Priority.sa
SourceSA=Source.sa
BrandsSA = Brands.sa
ItemsSA = Items.sa
ProductsSA = Products.sa
ItemEnquirySA = ItemEnquiry.sa

# EnquiryTrackSA = EnquiryTrack.sa
# AccountingSoftwareSA = AccountingSoftware.sa
# HrSolutionsSA = HrSolutions.sa
# EmployeeManagementSA = EmployeeManagement.sa

# ProductTypeSA = ProductType.sa
# ProductBrandSA = ProductBrand.sa
# ProductCategorySA = ProductCategory.sa
# ProductEnquirySA = ProductEnquiry.sa

# MobileEnquirySA = MobileEnquiry.sa
# TabletEnquirySA = TabletEnquiry.sa
# ComputersEnquirySA = ComputersEnquiry.sa
# AccessoriesEnquirySA = AccessoriesEnquiry.sa
BrandsSA=Brands.sa
ItemsSA=Items.sa
def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind = engine)
    return _Session()


class CoerceToInt(TypeDecorator):
    impl = BigInteger

    def process_result_value(self, value, dialect):
        if value is not None:
            value = int(value)
        return value
# Create your views here.


class BrandTypehead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            # int_product_id
            lst_brand = []
            if str_search_term != -1:
                if request.data.get('product_id'):
                    ins_brand = Items.objects.filter(fk_brand__vchr_name__icontains=str_search_term,fk_product = int(request.data.get('product_id')),fk_product__fk_company_id = request.user.userdetails.fk_company_id).values('fk_brand_id','fk_brand__vchr_name').distinct()
                else:
                    ins_brand = Items.objects.filter(fk_brand__vchr_name__icontains=str_search_term).values('fk_brand_id','fk_brand__vchr_name').distinct()
                if ins_brand:
                    for itr_item in ins_brand:
                        dct_brand = {}
                        dct_brand['name'] = itr_item['fk_brand__vchr_name'].capitalize()
                        dct_brand['id'] = itr_item['fk_brand_id']
                        lst_brand.append(dct_brand)
                return Response({'status':'success','data':lst_brand})
            else:
                return Response({'status':'empty','data':lst_brand})
        except Exception as e:
            return Response({'status':'1','data':str(e)})

class ProductTypehead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_product = []
            if str_search_term != -1:
                ins_product = Products.objects.filter(vchr_name__icontains=str_search_term).exclude(vchr_name__in =['GDP','GDEW']).values('pk_bint_id','vchr_name')
                if ins_product:
                    for itr_item in ins_product:
                        dct_product = {}
                        dct_product['name'] = itr_item['vchr_name'].capitalize()
                        dct_product['id'] = itr_item['pk_bint_id']
                        lst_product.append(dct_product)
                return Response({'status':'success','data':lst_product})
            else:
                return Response({'status':'empty','data':lst_product})
        except Exception as e:
            return Response({'status':'1','data':str(e)})

class ProductTypeheadGDP(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_product = []
            if str_search_term != -1:
                ins_product = Products.objects.filter(vchr_product_name__icontains=str_search_term,fk_company_id = request.user.userdetails.fk_company_id).values('id','vchr_product_name')
                if ins_product:
                    for itr_item in ins_product:
                        dct_product = {}
                        dct_product['name'] = itr_item['vchr_product_name'].capitalize()
                        dct_product['id'] = itr_item['id']
                        lst_product.append(dct_product)
                return Response({'status':'success','data':lst_product})
            else:
                return Response({'status':'empty','data':lst_product})
        except Exception as e:
            return Response({'status':'1','data':str(e)})

class PromoterTypehead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            lst_promoter = []
            if str_search_term != -1:
                ins_promoter = UserModel.objects.filter(fk_brand__vchr_brand_name__icontains=str_search_term,fk_company_id = request.user.userdetails.fk_company_id).exclude(fk_brand_id = None).distinct('fk_brand__vchr_brand_name','fk_brand').values('fk_brand__vchr_brand_name','fk_brand')
                # ins_promoter = UserModel.objects.filter(first_name__icontains=str_search_term).values('bint_phone','first_name')
                if ins_promoter:
                    for itr_item in ins_promoter:
                        dct_promoter = {}
                        dct_promoter['name'] = itr_item['fk_brand__vchr_brand_name'].capitalize()
                        dct_promoter['id'] = itr_item['fk_brand']
                        lst_promoter.append(dct_promoter)
                return Response({'status':'success','data':lst_promoter})
            else:
                return Response({'status':'empty','data':lst_promoter})
        except Exception as e:
            return Response({'status':'1','data':str(e)})

class ItemTypehead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_item = []
            if str_search_term != -1:
                ins_item = Items.objects.filter(Q(vchr_item_name__icontains=str_search_term)|Q(vchr_item_code__icontains=str_search_term),fk_product__fk_company_id = request.user.userdetails.fk_company_id).values('id','vchr_item_name','vchr_item_code')
                if ins_item:
                    for itr_item in ins_item:
                        dct_item = {}
                        dct_item['name'] = itr_item['vchr_item_name'].capitalize()
                        dct_item['code'] = itr_item['vchr_item_code'].capitalize()
                        dct_item['id'] = itr_item['id']
                        lst_item.append(dct_item)
                return Response({'status':'success','data':lst_item})
            else:
                return Response({'status':'empty','data':lst_item})
        except Exception as e:
            return Response({'status':'1','data':str(e)})

class ProductivityReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            staffs = []
            start = datetime.now()
            session = Session()
            str_username = request.data.get('username',False)
            bln_assigned_all = request.data.get('all',False)
            blnExcel = request.data.get('excel',False)
            if str_username:
                ins_user = UserModel.objects.get(username = str_username)
            lst_table_data = []
            dat_from_date = datetime.strptime(request.data['date_from'], "%d/%m/%Y").date()
            dat_to_date = datetime.strptime(request.data['date_to'], "%d/%m/%Y").date()
            # dat_from_date = request.data['date_from']
            # dat_to_date = request.data['date_to']
            if request.data.get('staffs'):
                for staffs_id in request.data.get('staffs'):
                    staffs.append(staffs_id['id'])
            if ins_user.fk_company.fk_company_type.vchr_company_type == 'TRAVEL AND TOURISM':
                rst_flight = session.query(literal("Flight").label("vchr_service"),FlightsSA.vchr_enquiry_status.label('vchr_enquiry_status'),FlightsSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_train = session.query(literal("Train").label("vchr_service"),TrainSA.vchr_enquiry_status.label("vchr_enquiry_status"),TrainSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Forex=session.query(literal("Forex").label("vchr_service"),ForexSA.vchr_enquiry_status.label("vchr_enquiry_status"),ForexSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Hotel=session.query(literal("Hotel").label("vchr_service"),HotelSA.vchr_enquiry_status.label("vchr_enquiry_status"),HotelSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Other=session.query(literal("Other").label("vchr_service"),OtherSA.vchr_enquiry_status.label("vchr_enquiry_status"),OtherSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Transport=session.query(literal("Transport").label("vchr_service"),TransportSA.vchr_enquiry_status.label("vchr_enquiry_status"),TransportSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_TravelInsurance=session.query(literal("Travel Insurance").label("vchr_service"),TravelInsuranceSA.vchr_enquiry_status.label("vchr_enquiry_status"),TravelInsuranceSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Visa=session.query(literal("Visa").label("vchr_service"),VisaSA.vchr_enquiry_status.label("vchr_enquiry_status"),VisaSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Package=session.query(literal("Package").label("vchr_service"),PackageSA.vchr_enquiry_status.label("vchr_enquiry_status"),PackageSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_kct = session.query(literal("Kerala City Tour").label("vchr_service"),KctSA.vchr_enquiry_status.label("vchr_enquiry_status"),KctSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_data = rst_flight.union_all(rst_Forex,rst_Hotel,rst_Other,rst_Transport,rst_TravelInsurance,rst_Visa,rst_Package,rst_train,rst_kct).subquery()

# ins_table_data = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company = ins_user.fk_company,dat_created_at__gte = dat_from_date,dat_created_at__lte = dat_to_date).values(                                       'pk_bint_id','vchr_enquiry_num','fk_assigned','fk_assigned__first_name','fk_assigned__last_name','fk_assigned','fk_customer__cust_fname','fk_customer__cust_lname','fk_customer__cust_mobile','vchr_enquiry_priority','vchr_enquiry_source','dat_created_at').order_by('fk_assigned__first_name')
# ins_table_data = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company = ins_user.fk_company,dat_created_at__gte = dat_from_date,dat_created_at__lte = dat_to_date,fk_assigned = request.data['assigned']).values('pk_bint_id','vchr_enquiry_num','fk_customer__cust_fname','fk_customer__cust_lname','fk_customer__cust_mobile','vchr_enquiry_priority','vchr_enquiry_source','dat_created_at','fk_assigned','fk_assigned__first_name','fk_assigned__last_name')


            elif ins_user.fk_company.fk_company_type.vchr_company_type == 'SOFTWARE':
                rst_enquiry_track = session.query(literal("Enquiry Track").label("vchr_service"),EnquiryTrackSA.vchr_enquiry_status.label('vchr_enquiry_status'),EnquiryTrackSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_accounting_software = session.query(literal("Accounting Software").label("vchr_service"),AccountingSoftwareSA.vchr_enquiry_status.label('vchr_enquiry_status'),AccountingSoftwareSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_hr_solutions = session.query(literal("HR Solutions").label("vchr_service"),HrSolutionsSA.vchr_enquiry_status.label('vchr_enquiry_status'),HrSolutionsSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_employee_management = session.query(literal("Employee Management").label("vchr_service"),EmployeeManagementSA.vchr_enquiry_status.label('vchr_enquiry_status'),EmployeeManagementSA.fk_enquiry_master_id.label("FK_Enquery"))

                rst_data = rst_enquiry_track.union_all(rst_accounting_software,rst_hr_solutions,rst_employee_management).subquery()
            elif ins_user.fk_company.fk_company_type.vchr_company_type == 'MOBILE':
                # rst_data = fun_mobile()
                rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),rst_data.c.vchr_service.label("vchr_service"),AuthUserSA.id.label('user_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                                rst_data.c.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                                EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.fk_branch_id.label('fk_branch'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                                CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('vchr_mobile_num'),\
                                EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
                                # PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
                                SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
                                BranchSA.vchr_name.label('branch_name'),\
                                EnquiryMasterSA.fk_branch_id,\
                                rst_data.c.brand_id,\
                                rst_data.c.item_id,\
                                rst_data.c.FK_Enquery,\
                                func.concat(AuthUserSA.first_name, ' ', AuthUserSA.last_name).label('vchr_staff_full_name'),\
                                func.concat(CustomerModelSA.cust_fname, ' ', CustomerModelSA.cust_lname).label('vchr_full_name'),\
                                UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied)\
                                .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                                .join(rst_data,rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id)\
                                .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                                .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                                .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                                .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)
            elif ins_user.fk_company.fk_company_type.vchr_company_type == 'AUTOMOBILE':
                rst_data = fun_automobile_data()
            if not ins_user.fk_company.fk_company_type.vchr_company_type == 'MOBILE':
                rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),rst_data.c.vchr_service.label("vchr_service"),AuthUserSA.id.label('user_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                                    rst_data.c.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                                    EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.fk_branch_id.label('fk_branch'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                                    CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('vchr_mobile_num'),\
                                    EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
                                    # PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
                                    SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
                                    BranchSA.vchr_name.label('branch_name'),\
                                    EnquiryMasterSA.fk_branch_id,
                                    func.concat(AuthUserSA.first_name, ' ', AuthUserSA.last_name).label('vchr_staff_full_name'),\
                                    func.concat(CustomerModelSA.cust_fname, ' ', CustomerModelSA.cust_lname).label('vchr_full_name'))\
                                    .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                                    .join(rst_data,rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id)\
                                    .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                                    .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                    .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                                    .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                                    .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)
            # staff filter
            if request.data.get('staff'):
                rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned.in_(tuple(request.data.get('staff'))))
            '''Assign Variables'''
            lst_barchart_data = []
            lst_barchart_labels = []
            lst_barchart_user_id = []
            lst_bar_booked_data = []
            '''Get with Branch'''
            if request.data.get('branch'):
                rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch'))
            '''Get Assign count'''
            rst_table = rst_table_data.subquery()
            if request.data.get('type') == 'PIE':
                if request.data.get('assigned'):
                    rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_assigned_id == request.data.get('assigned'))
                    rst_table = rst_table_data.subquery()
            rst_bar_data = session.query(rst_table.c.fk_assigned,\
                        rst_table.c.fk_assigned__first_name,\
                        func.count(rst_table.c.fk_assigned).label('count'),\
                        func.count(case([((rst_table.c.vchr_enquiry_status == 'INVOICED'),rst_table.c.fk_assigned)],else_=literal_column("NULL"))).label("booked_count"))\
                .group_by(rst_table.c.fk_assigned, rst_table.c.fk_assigned__first_name).order_by(desc('count'))
            #Check if promoter or resigned employee

            for bar_data in rst_bar_data:
                lst_barchart_user_id.append(bar_data[0])
                lst_barchart_labels.append(bar_data[1])
                lst_barchart_data.append(bar_data[2])
                lst_bar_booked_data.append(bar_data[3])

            # suffled = list(zip(lst_barchart_user_id,lst_bar_booked_data,lst_barchart_labels,lst_barchart_data))
            # random.shuffle(suffled)
            # lst_barchart_user_id,lst_bar_booked_data,lst_barchart_labels,lst_barchart_data= zip(*suffled)
            '''Service Wise Variables'''
            lst_services_all = []
            lst_services_booked_all = []
            lst_services_enquiry_all = []
            rst_service_count_all = session.query(rst_table.c.vchr_service.label('service'),\
                            func.count(rst_table.c.vchr_service).label('count'),\
                            rst_table.c.vchr_enquiry_status.label('status'),\
                            func.count(rst_table.c.vchr_enquiry_status).label('status_count'),\
                            func.count(case([((rst_table.c.vchr_enquiry_status == 'BOOKED'),\
                            rst_table.c.vchr_service)], else_=literal_column("NULL"))).label("booked_count"))\
                            .group_by(rst_table.c.vchr_service, rst_table.c.vchr_enquiry_status)
            rst_service_count_all_query = rst_service_count_all.subquery()
            rst_service_count_new = session.query(rst_service_count_all_query.c.service, func.sum(
                rst_service_count_all_query.c.count,type_=CoerceToInt).label('count')).group_by(rst_service_count_all_query.c.service).order_by(desc('count'))
            for serv in rst_service_count_new:
                lst_services_all.append(serv.service)
                lst_services_enquiry_all.append(serv.count)

            dct_service_count_all = dict(session.query(rst_service_count_all_query.c.service, func.sum(rst_service_count_all_query.c.booked_count, type_=CoerceToInt)).group_by('service'))
            dct_service_booked_all = {'labels':lst_services_all, 'booked_data':lst_services_booked_all, 'all_data':lst_services_enquiry_all}
            dct_status_count_all = dict(session.query(rst_service_count_all_query.c.status, func.sum(rst_service_count_all_query.c.status_count, type_=CoerceToInt).label('count')).group_by('status'))

            # rst_status_count_all = session.query(rst_table.c.vchr_enquiry_status.label('status'),func.count(rst_table.c.vchr_enquiry_status).label('count')).group_by(rst_table.c.vchr_enquiry_status)
            # for status in rst_status_count_all.all():
            #     dct_status_count_all[status.status] = status.count
            '''Mobile version Variables'''
            lst_staff_brand_bar = []
            lst_staff_item_bar = []
            lst_staff_piechart_data = []

            dct_brand_wise = {}
            dct_item_wise = {}
            dct_brand_item_wise = {}
            dct_brand_status_wise = {}
            dct_item_status_wise = {}
            dct_brand_count_all = {}
            dct_item_count_all = {}
            '''Mobile version'''


            rst_user_wise = session.query(func.count(rst_data.c.FK_Enquery).label('count'),\
                                                    rst_data.c.vchr_enquiry_status.label('status'),\
                                                    rst_data.c.vchr_service.label('service'),\
                                                    AuthUserSA.id.label('user_id'))\
                                        .join(EnquiryMasterSA,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
                                        .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .group_by(rst_data.c.vchr_service,rst_data.c.vchr_enquiry_status,AuthUserSA.id)\
                                        .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_from_date,\
                                                cast(EnquiryMasterSA.dat_created_at,Date) <= dat_to_date,\
                                                EnquiryMasterSA.fk_company_id == ins_user.fk_company_id)


            # rst_booked_data = rst_table_data.filter(func.upper(rst_data.c.vchr_enquiry_status) == 'BOOKED').order_by(AuthUserSA.first_name)
            # rst_user_data = session.query(rst_user_wise.c.count.label('count'), rst_user_wise.c.status.label('status'),rst_user_wise.c.service.label('service'),AuthUserSA.first_name.label('first_name'),AuthUserSA.last_name.label('last_name')).join(AuthUserSA,AuthUserSA.id == rst_user_wise.c.user_id)

            dct_user_wise = {}
            for dct_data in rst_user_wise.all():
                user_id = str(dct_data._asdict()['user_id'])

                if user_id in dct_user_wise.keys():
                    if dct_data._asdict()['service'] in dct_user_wise[user_id].keys():
                        dct_user_wise[user_id][dct_data._asdict()['service']][0].append(dct_data._asdict()['status'].upper())
                        dct_user_wise[user_id][dct_data._asdict()['service']][1].append(dct_data._asdict()['count'])
                    else:
                        dct_user_wise[user_id][dct_data._asdict()['service']] = [[dct_data._asdict()['status'].upper()],[dct_data._asdict()['count']]]
                else:
                    dct_user_wise[user_id] = {dct_data._asdict()['service']:[[dct_data._asdict()['status'].upper()],[dct_data._asdict()['count']]]}
            if request.data.get('type') == 'PIE':
                if request.data.get('assigned'):
                    rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_assigned_id == request.data.get('assigned'))
            rst_table_data = rst_table_data.order_by(AuthUserSA.first_name)
            lst_table_data = []

            # dct_service_booked_all = {}
            # dct_status_count_all = {}
            # dct_service_count_all ={}

            # lst_booked_data = []
            # dct_user_data = {}
            dct_staff_service = {}
            dct_staff_status = {}
            print(len(rst_table_data.all()))


            for dct_data in rst_table_data.all():
                dct_temp_data = dct_data._asdict()

                # dct_temp_data['vchr_full_name'] = dct_temp_data['fk_customer__cust_fname']+" "+dct_temp_data['fk_customer__cust_lname']
                # dct_temp_data['vchr_staff_full_name'] = dct_temp_data['fk_assigned__first_name']+" "+dct_temp_data['fk_assigned__last_name']
                dct_temp_data['vchr_created_at'] = dct_temp_data['dat_created_at'].strftime('%d-%m-%Y')
                # dct_temp_data['vchr_mobile_num'] = dct_temp_data['fk_customer__cust_mobile']
                # dct_temp_data['branch_name'] = Branch.objects.get(pk_bint_id = dct_temp_data['fk_branch']).vchr_name
                # dct_temp_data['vchr_enquiry_status'] = dct_temp_data['vchr_enquiry_status'].upper()
                lst_table_data.append(dct_temp_data)
                # print(dct_temp_data['vchr_enquiry_status'])
                # if dct_temp_data['vchr_service'] not in dct_service_booked_all.keys():
                #     dct_service_booked_all[dct_temp_data['vchr_service']] = {'ALL':0, 'BOOKED':0}
                #
                # if dct_temp_data['vchr_enquiry_status'].upper() == 'BOOKED':
                #     lst_booked_data.append(dct_temp_data)
                #     dct_service_booked_all[dct_temp_data['vchr_service']]['BOOKED'] += 1
                #     dct_service_booked_all[dct_temp_data['vchr_service']]['ALL'] += 1
                # else:
                #     dct_service_booked_all[dct_temp_data['vchr_service']]['ALL'] += 1

                # if dct_temp_data['vchr_enquiry_status'].upper() in dct_status_count_all.keys():
                #     dct_status_count_all[dct_temp_data['vchr_enquiry_status'].upper()] += 1
                # else:
                #     dct_status_count_all[dct_temp_data['vchr_enquiry_status'].upper()] = 1

                # if dct_temp_data['vchr_service'] in dct_service_count_all.keys():
                #     dct_service_count_all[dct_temp_data['vchr_service']] += 1
                # else:
                #     dct_service_count_all[dct_temp_data['vchr_service']] = 1

                # if not  dct_temp_data['fk_assigned'] in dct_user_data.keys():
                #     dct_user_data[dct_temp_data['fk_assigned']] = {'total':0,'booked':0, 'first_name':dct_temp_data['fk_assigned__first_name']}
                #
                # dct_user_data[dct_temp_data['fk_assigned']]['total'] += 1
                # if dct_temp_data['vchr_enquiry_status'].upper() == 'BOOKED':
                #     dct_user_data[dct_temp_data['fk_assigned']]['booked'] += 1

                if not dct_temp_data['fk_assigned'] in dct_staff_service.keys():
                    dct_staff_service[dct_temp_data['fk_assigned']] = {}

                if not dct_temp_data['vchr_service'] in dct_staff_service[dct_temp_data['fk_assigned']].keys():
                    dct_staff_service[dct_temp_data['fk_assigned']][dct_temp_data['vchr_service']] = 0

                dct_staff_service[dct_temp_data['fk_assigned']][dct_temp_data['vchr_service']] += 1

                if not dct_temp_data['fk_assigned'] in dct_staff_status.keys():
                    dct_staff_status[dct_temp_data['fk_assigned']] = {}

                if not dct_temp_data['vchr_enquiry_status'].upper() in dct_staff_status[dct_temp_data['fk_assigned']].keys():
                    dct_staff_status[dct_temp_data['fk_assigned']][dct_temp_data['vchr_enquiry_status'].upper()] = 0

                dct_staff_status[dct_temp_data['fk_assigned']][dct_temp_data['vchr_enquiry_status'].upper()] += 1

            print('main loop '+str(datetime.now() - start))
            lst_services_all = []
            lst_services_booked_all = []
            lst_services_enquiry_all = []
            # for key in dct_service_booked_all.keys():
            #     lst_services_all.append(key)
            #     lst_services_booked_all.append(dct_service_booked_all[key]['BOOKED'])
            #     lst_services_enquiry_all.append(dct_service_booked_all[key]['ALL'])

            # dct_service_booked_all = {'labels':lst_services_all, 'booked_data':lst_services_booked_all, 'all_data':lst_services_enquiry_all}
                # else:
                #     if dct_temp_data['vchr_service'] == 'BOOKED':
                #         dct_service_booked_all[dct_temp_data['vchr_service']]['BOOKED'] += 1
                #     else:
                #         dct_service_booked_all[dct_temp_data['vchr_service']]['ALL'] += 1

            # lst_booked_data = []
            # for dct_data in rst_booked_data.all():
            #     dct_temp_data = dct_data._asdict()
            #     dct_temp_data['vchr_full_name'] = dct_temp_data['fk_customer__cust_fname']+" "+dct_temp_data['fk_customer__cust_lname']
            #     dct_temp_data['vchr_staff_full_name'] = dct_temp_data['fk_assigned__first_name']+" "+dct_temp_data['fk_assigned__last_name']
            #     dct_temp_data['vchr_created_at'] = dct_temp_data['dat_created_at'].strftime('%d-%m-%Y')
            #     dct_temp_data['vchr_mobile_num'] = dct_temp_data['fk_customer__cust_mobile']
            #     dct_temp_data['branch_name'] = Branch.objects.get(pk_bint_id = dct_temp_data['fk_branch']).vchr_name
            #     dct_temp_data['vchr_enquiry_status'] = dct_temp_data['vchr_enquiry_status'].upper()
            #     lst_booked_data.append(dct_temp_data)
            # lst_report_data = []
            if request.data['type'] == 'BAR':
                # dct_item = {'first_name':'','total':0,'fk_assigned':0}
                # for itr_item in lst_table_data:
                #     if str(itr_item.get('fk_assigned__first_name')).title() == dct_item['first_name']:
                #         dct_item['total'] += 1
                #     else:
                #         if dct_item['first_name'] != '':
                #             lst_report_data.append(dct_item.copy())
                #         dct_item = {'first_name':str(itr_item.get('fk_assigned__first_name')).title(),'total':1,'fk_assigned':itr_item.get('fk_assigned')}
                # if dct_item['first_name'] != '':
                #     lst_report_data.append(dct_item.copy())
                # random.shuffle(lst_report_data)
                # dct_status_count_all = Counter(tok['vchr_enquiry_status'] for tok in lst_table_data)
                # dct_service_count_all = Counter(tok['vchr_service'] for tok in lst_table_data)
                # print(lst_report_data)
                # print(dct_user_data)
                # lst_barchart_data = []
                # lst_barchart_labels = []
                # lst_barchart_user_id = []
                # bar_booked_labels = []
                # lst_bar_booked_data = []

                # for key in dct_user_data.keys():
                #     lst_barchart_labels.append(dct_user_data[key]['first_name'])
                #     lst_barchart_data.append(dct_user_data[key]['total'])
                #     lst_barchart_user_id.append(int(key))
                #     lst_bar_booked_data.append(dct_user_data[key]['booked'])
                # dct_booked_counts = {}
                # for dct_item in lst_booked_data:
                #     if dct_item['user_id'] in dct_booked_counts.keys():
                #         dct_booked_counts[dct_item['user_id']]['total'] += 1
                #     else:
                #         dct_booked_counts[dct_item['user_id']] = {'first_name':dct_item['fk_assigned__first_name'].title(), 'total':1}
                # bar_booked_labels = []
                # lst_bar_booked_data = []
                # for item in lst_barchart_user_id:
                #     if dct_booked_counts.get(item):
                #         lst_bar_booked_data.append(dct_booked_counts[item]['total'])

                #     else:
                #         lst_bar_booked_data.append(0)

                start = datetime.now()
                lst_staff_piechart_data = []
                for int_staff_id in lst_barchart_user_id:
                    lst_staff_piechart_data.append({int_staff_id:dct_staff_status[int_staff_id]})
                    # count_data = Counter(tok['vchr_enquiry_status'] for tok in lst_table_data if tok.get('fk_assigned') == int_staff_id)
                # lst_staff_status_data = []
                # for dct_item in lst_staff_piechart_data:
                #     dct_temp = dct_item
                #     dct_temp['']

                lst_staff_service_data = []
                lst_staff_service_data_bar = []
                print('user -> service')
                for int_staff_id in lst_barchart_user_id:
                    # count_data = Counter(tok['vchr_service'] for tok in lst_table_data if tok.get('fk_assigned') == int_staff_id)
                    lst_staff_service_data.append({int_staff_id:dct_staff_service[int_staff_id]})
                    lst_staff_service_data_bar.append({int_staff_id:{
                        'services': list(dct_staff_service[int_staff_id].keys()),
                        'count': list(dct_staff_service[int_staff_id].values())
                    }})
                session.close()
                return JsonResponse({ 'status' : 'success','dct_service_booked_all':dct_service_booked_all,'bar_booked_data':lst_bar_booked_data, 'user_wise':dct_user_wise, 'lst_staff_service_data':lst_staff_service_data, 'lst_service_count_all':dct_service_count_all,
                    'lst_barchart_labels':lst_barchart_labels ,  'lst_barchart_data':lst_barchart_data , 'lst_barchart_user_id':lst_barchart_user_id ,
                    'lst_status_count_all': dct_status_count_all , 'lst_staff_piechart_data': lst_staff_piechart_data , 'lst_table_data': lst_table_data,
                                      'dct_brand_count_all': dct_brand_count_all,                    'dct_item_count_all': dct_item_count_all, 'lst_staff_service_data_bar': lst_staff_service_data_bar,
                                      'lst_staff_brand_bar': lst_staff_brand_bar, 'lst_staff_item_bar': lst_staff_item_bar, 'dct_brand_wise': dct_brand_wise, 'dct_item_wise':dct_item_wise,'dct_brand_item_wise':dct_brand_item_wise,'dct_brand_status_wise':dct_brand_status_wise,'dct_item_status_wise':dct_item_status_wise})




            elif request.data['type'] == 'PIE':
                if blnExcel:
                    lst_excel_data = []
                    for dct_data in lst_table_data:
                        dct_temp = OrderedDict()
                        if bln_assigned_all:
                            dct_temp['Staff Name'] = str(dct_data.get('vchr_staff_full_name')).title()
                        dct_temp['Enquiry Date'] = str(datetime.strptime(str(dct_data.get('dat_created_at'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
                        dct_temp['Enquiry Number'] = dct_data.get('vchr_enquiry_num')
                        dct_temp['Customer Name'] = str(dct_data.get('vchr_full_name')).title()
                        dct_temp['Mobile Number'] = str(dct_data.get('vchr_mobile_num'))
                        dct_temp['Service'] = dct_data.get('vchr_service')
                        # dct_temp['Enquiry Priority'] = dct_data.get('vchr_enquiry_priority')
                        dct_temp['Enquiry Source'] = dct_data.get('vchr_enquiry_source')
                        dct_temp['Enquiry Status'] = dct_data.get('vchr_enquiry_status')
                        dct_temp['Branch'] = dct_data.get('branch_name').title()
                        lst_excel_data.append(dct_temp)
                    fromdate =  str(dat_from_date)[:10].split("-")
                    todate =  str(dat_to_date)[:10].split('-')
                    fromdate.reverse()
                    todate.reverse()
                    dat_from_date = "-".join(fromdate)
                    dat_to_date = "-".join(todate)

                    str_all = ''
                    if not bln_assigned_all:
                        str_all += lst_table_data[0].get('vchr_staff_full_name')
                    else:
                        str_all += 'all'


                    if request.data.get('branch'):
                        str_all += '+branch'
                    if request.data.get('staff'):
                        str_all += '+staff'
                    if bln_assigned_all:
                        lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Staff Name'])
                        response = export_excel('productivity',str_all,dat_from_date,dat_to_date,lst_excel_data)
                    else:
                        lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Enquiry Number'])
                        response = export_excel('productivity',str_all,dat_from_date,dat_to_date,lst_excel_data)
                    if response != False:
                        session.close()
                        return JsonResponse({'status': 'success', 'path':response})
                    else:
                        session.close()
                        return JsonResponse({'status': 'failure'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            session.close()
            return Response({'status':'0','data':str(e)})

# class ProductivityReport1(APIView):
#     permission_classes = [AllowAny]
#     @timeit
#     def post(self,request):
#         try:
#             session = Session()
#             str_username = request.data.get('username',False)
#             if str_username:
#                 ins_user = UserModel.objects.get(username = str_username)
#             dat_from_date = datetime.strptime(request.data['fdate'], "%d/%m/%Y").date()
#             dat_to_date = datetime.strptime(request.data['tdate'], "%d/%m/%Y").date()
#             dat_to_date = dat_to_date + timedelta(days = 1)

#             options = {
#                 'status': request.data.get('status',[]),
#                 'branch': [request.data.get('branch'),'fk_branch'],
#                 'assigned': request.data.get('assigned',[]),
#                 'level': 5,
#                 'graphs': ['bar','bar','bar','bar','chart'],
#                 'all_data_labels': [['fk_assigned', 'fk_assigned__first_name'], ['vchr_service'], ['vchr_brand_name'], ['vchr_item_name'], ['vchr_enquiry_status']],
#                 'labels': ['users','service','brand','item','status']
#             }

#             # rst_data = fun_mobile()
#             rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),\
#                             EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
#                             EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),\
#                             EnquiryMasterSA.fk_branch_id.label('fk_branch'),\
#                             EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
#                             EnquiryMasterSA.fk_branch_id,\
#                             AuthUserSA.id.label('user_id'),\
#                             AuthUserSA.first_name.label('fk_assigned__first_name'),\
#                             AuthUserSA.last_name.label('fk_assigned__last_name'),\
#                             func.concat(AuthUserSA.first_name, ' ', AuthUserSA.last_name).label('vchr_staff_full_name'),\
#                             rst_data.c.vchr_service.label("vchr_service"),\
#                             rst_data.c.vchr_enquiry_status,\
#                             rst_data.c.brand_id,\
#                             BrandsSA.vchr_brand_name,\
#                             ItemsSA.vchr_item_name,\
#                             rst_data.c.item_id,\
#                             rst_data.c.FK_Enquery,\
#                             CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
#                             CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),\
#                             CustomerModelSA.cust_mobile.label('vchr_mobile_num'),\
#                             func.concat(CustomerModelSA.cust_fname, ' ', CustomerModelSA.cust_lname).label('vchr_full_name'),\
#                             # PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
#                             SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
#                             BranchSA.vchr_name.label('branch_name'))\
#                             .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
#                             .join(rst_data,rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id)\
#                             .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
#                             .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#                             .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
#                             .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
#                             .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
#                             .join(BrandsSA, rst_data.c.brand_id == BrandsSA.id)\
#                             .join(ItemsSA, rst_data.c.item_id == ItemsSA.id)
#             #staff filter
#             if request.data.get('staff'):
#                 rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned.in_(tuple(request.data.get('staff'))))
#             graph = MakeGraph(rst_table_data, options,session)
#             dct_lst_all_data = graph.getAllData()
#             dct_data = graph.getLevelWiseData(booked=True)
#             # dct_data_booked = graph.getLevelWiseData(booked=False)
#             # dct_lst_table_data = graph.getTableData()
#             session.close()
#             return JsonResponse({'dct_lst_all_data': dct_lst_all_data, 'dct_data': dct_data})

#         except Exception as e:
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             session.close()
#             return Response({'status':'0','data':str(e)})




class ProductProductivityReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            staffs = []
            start = datetime.now()
            session = Session()
            str_username = request.data.get('username',False)
            bln_assigned_all = request.data.get('all',False)
            blnExcel = request.data.get('excel',False)
            if str_username:
                ins_user = UserModel.objects.get(username = str_username)
            lst_table_data = []

            dat_from_date = datetime.strptime(request.data['fromdate'], "%Y-%m-%d").date()
            dat_to_date = datetime.strptime(request.data['todate'], "%Y-%m-%d").date()
            dat_to_date = dat_to_date + timedelta(days = 1)
            if request.data.get('staffs'):
                for staffs_id in request.data.get('staffs'):
                    staffs.append(staffs_id['id'])

            rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),ProductTypeSA.vchr_type_name.label("vchr_service"),AuthUserSA.id.label('user_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                            ProductEnquirySA.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                            EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.fk_branch_id.label('fk_branch'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                            CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('vchr_mobile_num'),ProductBrandSA.vchr_brand_name,ProductCategorySA.vchr_category.label('vchr_item_name'),\
                            EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
                            # PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
                            SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
                            BranchSA.vchr_name.label('branch_name'),\
                            EnquiryMasterSA.fk_branch_id,\
                            func.concat(AuthUserSA.first_name, ' ', AuthUserSA.last_name).label('vchr_staff_full_name'),\
                            func.concat(CustomerModelSA.cust_fname, ' ', CustomerModelSA.cust_lname).label('vchr_full_name'),\
                            UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied)\
                            .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                            .join(ProductEnquirySA,ProductEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                            .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                            .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                            .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                            .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                            .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                            .join(ProductBralst_table_datandSA,ProductBrandSA.pk_bint_id == ProductEnquirySA.fk_brand_id)\
                            .join(ProductCategorySA,ProductCategorySA.pk_bint_id == ProductEnquirySA.fk_category_id)\
                            .join(ProductTypeSA, ProductTypeSA.pk_bint_id == ProductEnquirySA.fk_product_id)
            """Permission wise filter for data"""
            # rst_table_data = get_perm_data(rst_table_data,request.user)

            # staff filter
            if request.data.get('staffs'):
                rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(tuple([i['id'] for i in request.data.get('staffs',[])])))
            '''Assign Variables'''
            lst_barchart_data = []
            lst_barchart_labels = []
            lst_barchart_user_id = []
            lst_bar_booked_data = []
            '''Get with Branch'''
            if request.data.get('branch'):
                rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch'))
            if not rst_table_data.all():
                session.close()
                return Response({'status':'failed','reason':'No data'})

            dct_data={}
            lst_table_data = []
            dct_data['assigne_all']={}
            dct_data['service_all']={}
            dct_data['brand_all']={}
            dct_data['item_all']={}
            dct_data['status_all']={}
            dct_data['assigne_service']={}
            dct_data['assigne_brand']={}
            dct_data['assigne_item']={}
            dct_data['assigne_status']={}
            dct_data['assigne_service_brand']={}
            dct_data['assigne_service_item']={}
            dct_data['assigne_service_status']={}
            dct_data['assigne_service_brand_item']={}
            dct_data['assigne_service_brand_status']={}
            dct_data['assigne_service_brand_item_status']={}

            for ins_data in rst_table_data.all():
                if ins_data.vchr_staff_full_name not in dct_data['assigne_all']:
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Enquiry'] = 1
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] = 0

                    dct_data['assigne_service'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]={}

                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Enquiry'] = 1
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Enquiry']=1
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Enquiry']=1
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Enquiry']=1
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = 0
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] = 0

                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] = 1
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = 1
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] = 1
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] = 1
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] = 1

                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=1
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=1
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=1
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0

                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] = 1
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 1
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale'] = 1

                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=1
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0

                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 1
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1

                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1
                else:
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Enquiry'] += 1
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] += 1
                    if ins_data.vchr_service not in dct_data['assigne_service'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Enquiry'] = 1
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = 1
                    else:
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Enquiry']+=1
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] += 1



                    if ins_data.vchr_brand_name.title() not in dct_data['assigne_brand'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Enquiry']=1
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] = 1
                    else:
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Enquiry']+=1
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] += 1


                    if ins_data.vchr_item_name.title() not in dct_data['assigne_item'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Enquiry']=1
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] = 1
                    else:
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Enquiry']+=1
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] += 1


                    if ins_data.vchr_enquiry_status not in dct_data['assigne_status'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] = 1
                    else:
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Enquiry']+=1
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] += 1



                    if ins_data.vchr_service not in dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status] = {}
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=1
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=1
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 0
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] = 1
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 1
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale'] = 1
                    else:
                        if ins_data.vchr_brand_name.title() not in dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=1
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] = 1
                        else:
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']+=1
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']+= 1

                        if ins_data.vchr_item_name.title() not in dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=1
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=0
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 1
                        else:
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']+=1
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']+= 1

                        if ins_data.vchr_enquiry_status not in dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=1
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale'] = 1
                        else:
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']+=1
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']+= 1

                    if ins_data.vchr_service not in dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=1
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 1
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1

                    else:
                        if ins_data.vchr_brand_name.title() not in dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=1
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                            if ins_data.vchr_enquiry_status == 'BOOKED':
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 1
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1
                        else:
                            if ins_data.vchr_item_name.title() not in dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=1
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                                if ins_data.vchr_enquiry_status == 'BOOKED':
                                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 1
                            else:
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=1
                                if ins_data.vchr_enquiry_status == 'BOOKED':
                                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']+=1
                            if ins_data.vchr_enquiry_status not in dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                                if ins_data.vchr_enquiry_status == 'BOOKED':
                                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=1
                            else:
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=1
                                if ins_data.vchr_enquiry_status == 'BOOKED':
                                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']+=1
                    if ins_data.vchr_service not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name]:
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1
                    elif ins_data.vchr_brand_name.title() not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1
                    elif ins_data.vchr_item_name.title() not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1
                    elif ins_data.vchr_enquiry_status not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=1
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 1
                    else:
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=1
                        if ins_data.vchr_enquiry_status == 'BOOKED':
                            dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']+=1
                if ins_data.vchr_service not in dct_data['service_all']:
                    dct_data['service_all'][ins_data.vchr_service]={}
                    dct_data['service_all'][ins_data.vchr_service]['Enquiry']=1
                    dct_data['service_all'][ins_data.vchr_service]['Sale'] = 0
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['service_all'][ins_data.vchr_service]['Sale'] = 1
                else:
                    dct_data['service_all'][ins_data.vchr_service]['Enquiry']+= 1
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['service_all'][ins_data.vchr_service]['Sale']+= 1
                if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=1
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=1
                else:
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=1
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=1
                if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                    dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=1
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = 1
                else:
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=1
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=1
                if ins_data.vchr_enquiry_status not in dct_data['status_all']:
                    dct_data['status_all'][ins_data.vchr_enquiry_status]={}
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']=1
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale'] = 0
                else:
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']+=1
                    if ins_data.vchr_enquiry_status == 'BOOKED':
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale'] +=1
            # dct_data['table_data']=lst_table_data
            dct_data['assigne_all']=paginate_data(dct_data['assigne_all'],10)
            dct_data['brand_all']=paginate_data(dct_data['brand_all'],10)
            dct_data['item_all']=paginate_data(dct_data['item_all'],10)
            dct_data['service_all']=paginate_data(dct_data['service_all'],10)


            for key in dct_data['assigne_service']:
                    dct_data['assigne_service'][key]=paginate_data(dct_data['assigne_service'][key],10)
            for key in dct_data['assigne_brand']:
                    dct_data['assigne_brand'][key]=paginate_data(dct_data['assigne_brand'][key],10)
            for key in dct_data['assigne_item']:
                    dct_data['assigne_item'][key]=paginate_data(dct_data['assigne_item'][key],10)
            for key in dct_data['assigne_service_brand']:
                for key1 in dct_data['assigne_service_brand'][key]:
                    dct_data['assigne_service_brand'][key][key1]=paginate_data(dct_data['assigne_service_brand'][key][key1],10)
            for key in dct_data['assigne_service_item']:
                for key1 in dct_data['assigne_service_item'][key]:
                    dct_data['assigne_service_item'][key][key1]=paginate_data(dct_data['assigne_service_item'][key][key1],10)
            # import pdb;pdb.set_trace()
            for key in dct_data['assigne_service_brand_item']:
                for key1 in dct_data['assigne_service_brand_item'][key]:
                    for key2 in dct_data['assigne_service_brand_item'][key][key1]:
                        dct_data['assigne_service_brand_item'][key][key1][key2]=paginate_data(dct_data['assigne_service_brand_item'][key][key1][key2],10)

            rst_table=rst_table_data.subquery()
            rst_promoter = session.query(rst_table.c.fk_assigned,\
                        rst_table.c.fk_assigned__first_name,\
                        case([(rst_table.c.fk_brand_id > 0,literal_column("'promoter'"))],else_=literal_column("'not promoter'"))).group_by(rst_table.c.fk_assigned, rst_table.c.fk_assigned__first_name,rst_table.c.fk_brand_id)
            lst_promoter = []
            for itr_item in rst_promoter:
                if itr_item[2] == 'promoter':
                    lst_promoter.append(itr_item[1])

            rst_resigned = session.query(rst_table.c.fk_assigned,\
                        rst_table.c.fk_assigned__first_name,\
                        case([(rst_table.c.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],else_=literal_column("'not resigned'"))).group_by(rst_table.c.fk_assigned, rst_table.c.fk_assigned__first_name,rst_table.c.dat_resignation_applied)
            lst_resigned = []
            for itr_item in rst_resigned:
                if itr_item[2] == 'resigned':
                    lst_resigned.append(itr_item[1])
            dct_data['promoter']=lst_promoter
            dct_data['resigned']=lst_resigned
            session.close()
            return Response({'status': 1,'data':dct_data})
        except Exception as e:
            ins_logger.logger.error(str(e))
            session.close()
            return Response({'status':'0','data':str(e)})



class ProductivityReportMobile(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb;pdb.set_trace()
            staffs = []
            start = datetime.now()
            session = Session()
            # import pdb; pdb.set_trace()
            str_username = request.data.get('username',False)
            bln_assigned_all = request.data.get('all',False)
            blnExcel = request.data.get('excel',False)
            if request.data.get('show_type'):
                str_show_type = 'total_amount'
            else:
                str_show_type = 'int_quantity'
            if str_username:
                ins_user = UserModel.objects.get(username = str_username)
            lst_table_data = []

            dat_from_date = datetime.strptime(request.data['date_from'], "%Y-%m-%d").date()
            dat_to_date = datetime.strptime(request.data['date_to'], "%Y-%m-%d").date()
            # dat_to_date = dat_to_date + timedelta(days = 1)
            if request.data.get('staffs'):
                for staffs_id in request.data.get('staffs'):
                    staffs.append(staffs_id['intId'])
            lst_mviews = request.data['lst_mv']
            # nisam_materilized views
            # import pdb; pdb.set_trace()
            engine = get_engine()
            conn = engine.connect()
            lst_branch_id = []
            str_filter = ''
            lst_staffs = UserModel.objects.filter(fk_group__vchr_name='STAFF')
            """Permission wise filter for data"""
            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES','PRODUCT MANAGER']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                # lst_branch_id = lst_branch_id.append(request.user.userdetails.fk_branch_id)
                lst_staffs = lst_staffs.filter(fk_branch_id=request.user.userdetails.fk_branch_id)
                str_filter += " branch_id ="+str(request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.fk_hierarchy_group_id or request.user.userdetails.fk_group.vchr_name.upper() in ['CLUSTER MANAGER']:
                lst_branch_id=show_data_based_on_role(request)
                str_filter += " branch_id in ("+str(lst_branch_id)[1:-1]+")"
                lst_staffs = lst_staffs.filter(fk_branch_id__in=lst_branch_id)
                # rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            else:
                session.close()
                return Response({'status':'0','reason':'No data'})
            # import pdb;pdb.set_trace()
            if request.user.userdetails.fk_group.vchr_name.upper() in ['PRODUCT MANAGER']:
                lst_product = get_user_products(request.user.id)
                if lst_product:
                    str_filter += " product_id in ("+str(lst_product)[1:-1]+")"

             # '''Get with Branch'''
            if request.data.get('branch'):
                if len(str_filter):
                    str_filter += " AND branch_id = "+str(request.data.get('branch'))
                else:
                    str_filter += " branch_id = "+str(request.data.get('branch'))

            # staff filter
            if request.data.get('staffs'):
                # lst_staffs_id = request.data.get('staffs',[])
                if len(str_filter):
                    str_filter += ' AND user_id in ('+str(staffs)[1:-1]+')'
                else:
                    str_filter += ' user_id in ('+str(staffs)[1:-1]+')'

            # promoters filter
            """new filter based on brand promoter"""
            if request.data.get('promoters'):
                promoters = []
                for data in request.data.get('promoters'):
                    promoters.append(data['id'])
                if len(str_filter):
                    str_filter += ' AND promoter_brand_id in ('+str(promoters)[1:-1]+')'
                else:
                    str_filter += ' promoter_brand_id in ('+str(promoters)[1:-1]+')'


            # product filter
            if request.data.get('product'):
                if len(str_filter):
                    str_filter += " AND product_id = "+str(request.data.get('product'))
                else:
                    str_filter += " product_id = "+str(request.data.get('product'))

            # brand wise filter
            if request.data.get('brand'):
                if len(str_filter):
                    str_filter += " AND brand_id = "+str(request.data.get('brand'))
                else:
                    str_filter += " brand_id = "+str(request.data.get('brand'))

            # promoter wise str_filter
            if request.data.get('promoter'):
                if len(str_filter):

                    str_filter += " AND promoter_brand_id = "+str(request.data.get('promoter'))
                else:
                    str_filter += " promoter_brand_id = "+str(request.data.get('promoter'))

            # import pdb; pdb.set_trace()
            #for getting user corresponding products
            lst_user_id =[]
            lst_user_id.append(request.user.id)

            lst_user_products = get_user_products(lst_user_id)
            if lst_user_products:
                if len(str_filter):
                    str_filter += " AND product_id in ("+str(lst_user_products)[1:-1]+")"
                else:
                    str_filter += " product_id in ("+str(lst_user_products)[1:-1]+")"


            if len(str_filter):
                str_filter += " AND dat_enquiry BETWEEN '"+str(dat_from_date)+"' AND '"+str(dat_to_date)
            else:
                str_filter += " dat_enquiry BETWEEN '"+str(dat_from_date)+"' AND '"+str(dat_to_date)
            if not lst_mviews:
                session.close()
                return Response({"status":"0","reason":"No view list found"})
            query_set = ""
            promoter_query_set = ""
            resign_query_set = ""
            if len(lst_mviews) == 1:
                if request.data['type'].upper() == 'ENQUIRY':
                # if type == 'ENQUIRY':
                    query = "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(int_quantity) as qty,sum(total_amount) as value,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+lst_mviews[0]+" where"+str_filter+"'AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned"
                else:
                    query = "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(int_quantity) as qty,sum(total_amount) as value,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+lst_mviews[0]+" where"+str_filter+"' AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned"
                promoter_query = "select user_id,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name from "+lst_mviews[0]+" where"+str_filter+"' AND promoter='promoter' AND int_company_id = "+str(ins_user.fk_company_id)+" group by user_id,vchr_staff_full_name"
                resign_query = "select user_id,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name from "+lst_mviews[0]+" where"+str_filter+"' AND is_resigned='resigned' AND int_company_id = "+str(ins_user.fk_company_id)+" group by user_id,vchr_staff_full_name"
            else:
                if request.data['type'].upper() == 'ENQUIRY':
                # if type == 'ENQUIRY':
                    for data in lst_mviews:
                        query_set += "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(int_quantity) as qty,sum(total_amount) as value,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+data+" where"+str_filter+"' AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned union "
                        promoter_query_set +="select user_id,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name from "+data+" where"+str_filter+"' AND promoter='promoter' AND int_company_id = "+str(ins_user.fk_company_id)+" group by user_id,vchr_staff_full_name union "
                        resign_query_set += "select user_id,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name from "+data+" where"+str_filter+"' AND is_resigned='resigned' AND int_company_id = "+str(ins_user.fk_company_id)+" group by user_id,vchr_staff_full_name union "
                else:
                    for data in lst_mviews:
                        query_set +="select vchr_enquiry_status,vchr_product_name as vchr_service,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(int_quantity) as qty,sum(total_amount) as value,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+data+" where"+str_filter+"' AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned union "
                        promoter_query_set +="select user_id,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name from "+data+" where"+str_filter+"' AND promoter='promoter' AND int_company_id = "+str(ins_user.fk_company_id)+" group by user_id,vchr_staff_full_name union "
                        resign_query_set += "select user_id,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name from "+data+" where"+str_filter+"' AND is_resigned='resigned' AND int_company_id = "+str(ins_user.fk_company_id)+" group by user_id,vchr_staff_full_name union "
                query = query_set.rsplit(' ', 2)[0]
                promoter_query = promoter_query_set.rsplit(' ', 2)[0]
                resign_query = resign_query_set.rsplit(' ', 2)[0]
            rst_table_data = conn.execute(query).fetchall()

            if not rst_table_data:
                session.close()
                return Response({'status':'0','reason':'No data'})

            """structuring for productivity report new"""
            if request.data['type'].upper() == 'ENQUIRY':
                dct_data = structure_data_for_report_old(request,rst_table_data)
            else:
                dct_data = structure_data_for_report_new(request,rst_table_data)



            # if ins_user.fk_company.fk_company_type.vchr_company_type == 'MOBILE':
                # rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
                # rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
                # rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
                # rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
                #
                # rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
                # rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),rst_data.c.vchr_service.label("vchr_service"),AuthUserSA.id.label('user_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                #                 rst_data.c.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                #                 EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.fk_branch_id.label('fk_branch'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                #                 CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('vchr_mobile_num'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,\
                #                 EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
                #                 PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
                #                 SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
                #                 BranchSA.vchr_name.label('branch_name'),\
                #                 EnquiryMasterSA.fk_branch_id,\
                #                 rst_data.c.brand_id.label('brand_id'),\
                #                 rst_data.c.item_id.label('item_id'),\
                #                 rst_data.c.FK_Enquery,\
                #                 func.concat(AuthUserSA.first_name, ' ', AuthUserSA.last_name).label('vchr_staff_full_name'),\
                #                 func.concat(CustomerModelSA.cust_fname, ' ', CustomerModelSA.cust_lname).label('vchr_full_name'),\
                #                 UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied)\
                #                 .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                #                 .join(rst_data,rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id)\
                #                 .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                #                 .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                #                 .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                #                 .join(PrioritySA, EnquiryMasterSA.fk_priority_id == PrioritySA.pk_bint_id)\
                #                 .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                #                 .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                #                 .join(BrandsSA,BrandsSA.id==rst_data.c.brand_id)\
                #                 .join(ItemsSA,ItemsSA.id==rst_data.c.item_id)
                # rst_table_data = session.query(ItemEnquirySA.vchr_enquiry_status,func.count(ProductsSA.vchr_product_name).label('counts'),ProductsSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name,'',AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),AuthUserSA.id.label('user_id'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied,case([(UserModelSA.fk_brand_id > 0,literal_column("'promoter'"))],else_=literal_column("'not promoter'")).label('is_promoter'),case([(UserModelSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],else_=literal_column("'not resigned'")).label("is_resigned"))\
                # .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_from_date,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_to_date, EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N')\
                # .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                # .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                # .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                # .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                # .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                # .join(ProductsSA,ProductsSA.id == ItemEnquirySA.fk_product_id)\
                # .join(BrandsSA,BrandsSA.id == ItemEnquirySA.fk_brand_id)\
                # .join(ItemsSA,ItemsSA.id == ItemEnquirySA.fk_item_id)\
                # .group_by(ProductsSA.vchr_product_name,BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,ItemEnquirySA.vchr_enquiry_status,AuthUserSA.id,EnquiryMasterSA.fk_assigned_id,UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied)

            # """Permission wise filter for data"""
            # if request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})

            # """Permission wise filter for data"""
            # if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
            #     pass
            # elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})
            #
            # # staff filter
            # if request.data.get('staffs'):
            #     rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(tuple([i['id'] for i in request.data.get('staffs',[])])))
            # '''Assign Variables'''
            # lst_barchart_data = []
            # lst_barchart_labels = []
            # lst_barchart_user_id = []
            # lst_bar_booked_data = []
            # '''Get with Branch'''
            # if request.data.get('branch'):
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch'))
            #
            # if request.data.get('product'):
            #     rst_table_data = rst_table_data.filter(rst_data.c.vchr_service == request.data.get('product'))
            #
            # # if request.data.get('item'):
            # #     rst_table_data = rst_table_data.filter(rst_data.c.item_id == request.data.get('item'))
            #
            # if request.data.get('brand'):
            #     rst_table_data = rst_table_data.filter(rst_data.c.brand_id == request.data.get('brand'))
            #


            rst_promoter = conn.execute(promoter_query).fetchall()
            lst_promoter = []
            for itr_item in rst_promoter:
                # if itr_item[2] == 'promoter':
                #     lst_promoter.append(itr_item[1])
                lst_promoter.append(itr_item.vchr_staff_full_name)

            # rst_resigned = session.query(rst_table.c.fk_assigned,\
            #             rst_table.c.vchr_staff_full_name,\
            #             case([(rst_table.c.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],else_=literal_column("'not resigned'"))).group_by(rst_table.c.fk_assigned, rst_table.c.vchr_staff_full_name,rst_table.c.dat_resignation_applied)
            # import pdb; pdb.set_trace()
            rst_resigned = conn.execute(resign_query).fetchall()
            lst_resigned = []
            for itr_item in rst_resigned:
                # if itr_item[2] == 'resigned':
                #     lst_resigned.append(itr_item[1])
                lst_resigned.append(itr_item.vchr_staff_full_name)
            if request.data['type'].upper() == 'ENQUIRY':
                dct_data['promoter']=lst_promoter
                dct_data['resigned']=lst_resigned
            else:
                dct_data['PROMOTER']=lst_promoter
                dct_data['RESIGNED']=lst_resigned


            session.close()
            return Response({'status': '1','data':dct_data})
            # options = {
            #     'status': request.data.get('status', []),
            #     'branch': [request.data.get('branch'), 'fk_branch'],
            #     'assigned': request.data.get('assigned', []),
            #     'level': 5,
            #     'graphs': ['bar', 'bar', 'bar', 'bar', 'bar'],
            #     'all_data_labels': [['customer_id', 'vchr_staff_full_name'], ['vchr_service'], ['vchr_brand_name'], ['vchr_item_name'], ['vchr_enquiry_status']],
            #     'labels': ['users', 'service', 'brand', 'item', 'status']
            # }

            # graph = MakeGraph(rst_enquiry, options, session,False)
            # dct_lst_all_data = graph.getAllData()
            # dct_data = graph.getLevelWiseData(booked=True)
            # print(rst_enquiry.count())
            # return Response({'status': 'success', 'data': dct_data, 'dct_lst_all_data': dct_lst_all_data})

        except Exception as e:
            ins_logger.logger.error(str(e))
            session.close()
            return Response({'status':'0','data':str(e)})

# def key_sort(tup):
#     key,data = tup
#     return -data['Sale']
# def key_enquiry(tup):
#     try:
#         key,data = tup
#         return -data['Enquiry']
#     except Exception as e:
#         import pdb; pdb.set_trace()

# def paginate_data(request,dct_data,int_page_legth):
#     dct_paged = {}
#     int_count = 1
#     if request.data.get('type') == 'SALES':
#         sorted_dct_data = sorted(dct_data.items(), key= key_sort)
#     else:
#         sorted_dct_data = sorted(dct_data.items(), key= key_enquiry)
#     dct_data = OrderedDict(sorted_dct_data)
#     for key in dct_data:
#         if int_count not in dct_paged:
#             dct_paged[int_count]={}
#             dct_paged[int_count][key]=dct_data[key]
#         elif len(dct_paged[int_count]) < int_page_legth:
#             dct_paged[int_count][key]= dct_data[key]
#         else:
#             int_count += 1
#             dct_paged[int_count] ={}
#             dct_paged[int_count][key] = dct_data[key]
#     return dct_paged

def key_sort1(tup):
    k,d = tup
    return d['Enquiry']

def key_sort(tup):
    k,d = tup
    return d['Sale']

def paginate_data(dct_data, int_page_legth,type):
    dct_paged = {}
    int_count = 1
    if type == 'Sale':
        sorted_dct_data = reversed(sorted(dct_data.items(), key=key_sort))
    if type == 'Enquiry':
        sorted_dct_data = reversed(sorted(dct_data.items(), key=key_sort1))
    dct_data = OrderedDict(sorted_dct_data)
    for key in dct_data:
        if int_count not in dct_paged:
            dct_paged[int_count] = {}
            dct_paged[int_count][key] = dct_data[key]
        elif len(dct_paged[int_count]) < int_page_legth:
            dct_paged[int_count][key] = dct_data[key]
        else:
            int_count += 1
            dct_paged[int_count] = {}
            dct_paged[int_count][key] = dct_data[key]
    return dct_paged

class ProductivityReportTableData(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            staffs = []
            start = datetime.now()
            session = Session()
            str_username = request.data.get('username',False)
            bln_assigned_all = request.data.get('all',False)
            blnExcel = request.data.get('excel',False)
            if str_username:
                ins_user = UserModel.objects.get(username = str_username)
            lst_table_data = []

            dat_from_date = datetime.strptime(request.data['date_from'], "%Y-%m-%d").date()
            dat_to_date = datetime.strptime(request.data['date_to'], "%Y-%m-%d").date()
            # dat_to_date = dat_to_date + timedelta(days = 1)
            if request.data.get('staffs'):
                for staffs_id in request.data.get('staffs'):
                    staffs.append(staffs_id['id'])

            rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),ProductTypeSA.vchr_type_name.label("vchr_service"),AuthUserSA.id.label('user_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                            ProductEnquirySA.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                            EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.fk_branch_id.label('fk_branch'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                            CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('vchr_mobile_num'),ProductBrandSA.vchr_brand_name,ProductCategorySA.vchr_category.label('vchr_item_name'),\
                            EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
                            # PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
                            SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
                            BranchSA.vchr_name.label('branch_name'),\
                            EnquiryMasterSA.fk_branch_id,\
                            (AuthUserSA.first_name+" "+AuthUserSA.last_name).label('staff_full_name'),(CustomerModelSA.cust_fname+" "+CustomerModelSA.cust_lname).label('customer_full_name'),\
                            UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied)\
                            .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                            .join(ProductEnquirySA,ProductEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                            .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                            .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                            .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                            .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                            .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                            .join(ProductBrandSA,ProductBrandSA.pk_bint_id == ProductEnquirySA.fk_brand_id)\
                            .join(ProductCategorySA,ProductCategorySA.pk_bint_id == ProductEnquirySA.fk_category_id)\
                            .join(ProductTypeSA, ProductTypeSA.pk_bint_id == ProductEnquirySA.fk_product_id)

            if request.data.get('staffs'):
                rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(tuple([i['id'] for i in request.data.get('staffs',[])])))
            '''Assign Variables'''
            '''Get with Branch'''
            if request.data.get('branch'):
                rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch'))
            if not rst_table_data.all():
                session.close()
                return Response({'status':'failed','reason':'No data'})
            else:
                session.close()
                return Response({'status':'success','data':list(rst_table_data.all())})
        except Exception as e:
            ins_logger.logger.error(str(e))
            session.close()
            return Response({'status':'0','data':str(e)})

class ProductivityReportMobileTable(APIView):
        permission_classes = [IsAuthenticated]
        def post(self,request):
            try:
                staffs = []
                start = datetime.now()
                session = Session()
                str_username = request.data.get('username',False)
                bln_assigned_all = request.data.get('all',False)
                blnExcel = request.data.get('excel',False)
                if str_username:
                    ins_user = UserModel.objects.get(username = str_username)
                lst_table_data = []

                dat_from_date = datetime.strptime(request.data['date_from'], "%Y-%m-%d").date()
                dat_to_date = datetime.strptime(request.data['date_to'], "%Y-%m-%d").date()
                # dat_to_date = dat_to_date + timedelta(days = 1)
                if request.data.get('staffs'):
                    for staffs_id in request.data.get('staffs'):
                        staffs.append(staffs_id['id'])

                # if ins_user.fk_company.fk_company_type.vchr_company_type == 'MOBILE':
                #     rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
                #     rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
                #     rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
                #     rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
                #
                #     rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
                #     rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),rst_data.c.vchr_service.label("vchr_service"),AuthUserSA.id.label('user_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                #                     rst_data.c.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                #                     EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.fk_branch_id.label('fk_branch'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                #                     CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('vchr_mobile_num'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,\
                #                     EnquiryMasterSA.dat_created_at.label('dat_created_at'),\
                #                     PrioritySA.vchr_priority_name.label('vchr_enquiry_priority'),\
                #                     SourceSA.vchr_source_name.label('vchr_enquiry_source'),\
                #                     BranchSA.vchr_name.label('branch_name'),\
                #                     EnquiryMasterSA.fk_branch_id,\
                #                     rst_data.c.brand_id,\
                #                     rst_data.c.item_id,\
                #                     rst_data.c.FK_Enquery,\
                #                     UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied,(AuthUserSA.first_name+" "+AuthUserSA.last_name).label('staff_full_name'),(CustomerModelSA.cust_fname+" "+CustomerModelSA.cust_lname).label('customer_full_name'))\
                #                     .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                #                     .join(rst_data,rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id)\
                #                     .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                #                     .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                #                     .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                #                     .join(PrioritySA, EnquiryMasterSA.fk_priority_id == PrioritySA.pk_bint_id)\
                #                     .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                #                     .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                #                     .join(BrandsSA,BrandsSA.id==rst_data.c.brand_id)\
                #                     .join(ItemsSA,ItemsSA.id==rst_data.c.item_id)
                #
                # # staff filter
                # if request.data.get('staffs'):
                #     rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(tuple([i['id'] for i in request.data.get('staffs',[])])))
                # '''Assign Variables'''
                # '''Get with Branch'''
                # if request.data.get('branch'):
                #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch'))
                # if not rst_table_data.all():
                #     return Response({'status':'failed','reason':'No data'})
                # else:
                rst_table_data = session.query(ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_product_name.label\
                ('vchr_service')\
                ,func.concat(AuthUserSA.first_name,'',AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.vchr_enquiry_num,\
                EnquiryMasterSA.dat_created_at,EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),\
                BranchSA.vchr_name,AuthUserSA.id.label('user_id'),BrandsSA.vchr_brand_name,\
                ItemsSA.vchr_item_name,UserModelSA.fk_brand_id,UserModelSA.dat_resignation_applied,case([(UserModelSA.fk_brand_id > 0,literal_column("'promoter'"))],else_=literal_column("'not promoter'")).label('is_promoter'),case([(UserModelSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],else_=literal_column("'not resigned'")).label("is_resigned"),(CustomerModelSA.cust_fname+" "+CustomerModelSA.cust_lname).label('customer_full_name'))\
                .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_from_date,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_to_date, EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N')\
                .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                .join(ProductsSA,ProductsSA.id == ItemEnquirySA.fk_product_id)\
                .join(BrandsSA,BrandsSA.id == ItemEnquirySA.fk_brand_id)\
                .join(ItemsSA,ItemsSA.id == ItemEnquirySA.fk_item_id)

            # """Permission wise filter for data"""
            # if request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})

                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                elif request.user.userdetails.fk_hierarchy_group_id or request.user.userdetails.fk_group.vchr_name.upper() in ['CLUSTER MANAGER']:
                    lst_branch=show_data_based_on_role(request)
                    rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})

                # staff filter
                if request.data.get('staffs'):
                    rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(tuple([i['id'] for i in request.data.get('staffs',[])])))
                '''Assign Variables'''
                lst_barchart_data = []
                lst_barchart_labels = []
                lst_barchart_user_id = []
                lst_bar_booked_data = []
                '''Get with Branch'''
                if request.data.get('branch'):
                    rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch'))

                if request.data.get('product'):
                    rst_table_data = rst_table_data.filter(rst_data.c.vchr_service == request.data.get('product'))

                # if request.data.get('item'):
                #     rst_table_data = rst_table_data.filter(rst_data.c.item_id == request.data.get('item'))

                if request.data.get('brand'):
                    rst_table_data = rst_table_data.filter(rst_data.c.brand_id == request.data.get('brand'))

                if not rst_table_data.all():
                    session.close()
                    return Response({'status':'failed','reason':'No data'})
                session.close()
                return Response({'status':'success','data':list(rst_table_data.all())})
            except Exception as e:
                ins_logger.logger.error(str(e))
                session.close()
                return Response({'status':'0','data':str(e)})



"""structuring for productivity report"""
def structure_data_for_report_new(request,rst_table_data):
    try:
        # import pdb; pdb.set_trace()
        dct_data={}
        dct_data['IN_IT'] = {}

        if request.data['type'] == 'Sale':
            dct_data['ASSIGNE_SERVICE_BRAND_ITEM']={}

        elif request.data['type'] == 'Enquiry':
            dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS']={}

        for ins_data in rst_table_data:
            """sales -> productivity report """
            if request.data['type'] == 'Sale':
                if ins_data.vchr_staff_full_name not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE']={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value


                elif ins_data.vchr_service.title() not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryValue'] += ins_data.value


                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value


                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value


                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                elif ins_data.vchr_brand_name.title() not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value


                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                elif ins_data.vchr_item_name not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                else:
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']+=ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']+=ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']+=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']+=ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']+=ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']+=ins_data.value



            elif request.data['type'] == 'Enquiry':
                """enquiry -> productivity report"""
                if ins_data.vchr_staff_full_name not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale']  =  0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale']  =  0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale']  =  0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']  =  0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]  =  {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value



                elif ins_data.vchr_service.title() not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryValue']+= ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale']  =  0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']  =  0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_brand_name.title() not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryValue']+= ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_item_name not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryValue']+= ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']= 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_enquiry_status not in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS']:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryValue']+= ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                else:

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['EnquiryValue']+= ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] += ins_data.value

                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] += ins_data.counts
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] += ins_data.qty
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] += ins_data.value

                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] += ins_data.counts
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] += ins_data.qty
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][ins_data.vchr_staff_full_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] += ins_data.value


            # import pdb; pdb.set_trace()
        if request.data['type'] == 'Sale':

            """top 5 staff->product->brand->item"""
            dct_data['IN_IT']['ASSIGNE'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][i]['Sale']),reverse =True)[0]
            top_assigne = dct_data['IN_IT']['ASSIGNE']
            dct_data['IN_IT']['SERVICE'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][top_assigne]['SERVICE'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][top_assigne]['SERVICE'][i]['Sale']),reverse =True)[0]
            top_service = dct_data['IN_IT']['SERVICE']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][top_assigne]['SERVICE'][top_service]['BRANDS'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][top_assigne]['SERVICE'][top_service]['BRANDS'][i]['Sale']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEM'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][top_assigne]['SERVICE'][top_service]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][top_assigne]['SERVICE'][top_service]['BRANDS'][top_brand]['ITEMS'][i]['Sale']),reverse =True)[0]

            """paginating"""
            for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM']:
                for key1 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE']:
                    for key2 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS']:
                        dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']=paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'],10,request.data['type'])

            for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM']:
                for key1 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE']:
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS']=paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'],10,request.data['type'])

            for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM']:
                dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'] = paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'][key]['SERVICE'],10,request.data['type'])

            dct_data['ASSIGNE_SERVICE_BRAND_ITEM'] = paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM'],10,request.data['type'])


        elif request.data['type'] == 'Enquiry':

            """top 5 staff->product->brand->item->status"""
            dct_data['IN_IT']['ASSIGNE'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][i]['Enquiry']),reverse =True)[0]
            top_assigne = dct_data['IN_IT']['ASSIGNE']
            dct_data['IN_IT']['SERVICE'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][i]['Enquiry']),reverse =True)[0]
            top_service = dct_data['IN_IT']['SERVICE']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][top_service]['BRANDS'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][top_service]['BRANDS'][i]['Enquiry']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEM'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][top_service]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][top_service]['BRANDS'][top_brand]['ITEMS'][i]['Enquiry']),reverse =True)[0]
            top_item = dct_data['IN_IT']['ITEM']
            dct_data['IN_IT']['STATUS'] = sorted(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][top_service]['BRANDS'][top_brand]['ITEMS'][top_item]['STATUS'], key = lambda i: (dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][top_assigne]['SERVICE'][top_service]['BRANDS'][top_brand]['ITEMS'][top_item]['STATUS'][i]['Enquiry']),reverse =True)[0]

            """paginating"""
            # for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS']:
            #     for key1 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
            #         for key2 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']:
            #             for key3 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']:
            #                 dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'][key3]['STATUS']=paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'][key3]['STATUS'],10,request.data['type'])
            #
            # for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS']:
            #     for key1 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
            #         for key2 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']:
            #             dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']=paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'],10,request.data['type'])

            for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS']:
                for key1 in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
                    dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']=paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'],10,request.data['type'])

            for key in dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS']:
                dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'] = paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'],10,request.data['type'])

            dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'] = paginate_data(dct_data['ASSIGNE_SERVICE_BRAND_ITEM_STATUS'],10,request.data['type'])






        return dct_data
    except Exception as msg:
        return str(msg)



def structure_data_for_report_old(request,rst_table_data):
    try:

        dct_data={}
        lst_table_data = []
        dct_data['assigne_all']={}
        dct_data['service_all']={}
        dct_data['brand_all']={}
        dct_data['item_all']={}
        dct_data['status_all']={}
        dct_data['assigne_service']={}
        dct_data['assigne_brand']={}
        dct_data['assigne_item']={}
        dct_data['assigne_status']={}
        dct_data['assigne_service_brand']={}
        dct_data['assigne_service_item']={}
        dct_data['assigne_service_status']={}
        dct_data['assigne_service_brand_item']={}
        dct_data['assigne_service_brand_status']={}
        dct_data['assigne_service_brand_item_status']={}

        # dct_data['service_assigne'] = {}
        # dct_data['brand_assigne'] = {}
        # import pdb; pdb.set_trace()
        for ins_data in rst_table_data:
            # dct_temp = {
            #     'fk_assigne__cust_lname': ins_data.assigne_last_name,'fk_assigne__cust_mobile': ins_data.assigne_mobile,
            #     'fk_assigned__last_name': ins_data.staff_last_name,'vchr_created_at': ins_data.dat_created_at.strftime('%d-%m-%Y'),
            #     'vchr_staff_full_name': ins_data.staff_first_name + ' ' + ins_data.staff_last_name,
            #     'vchr_enquiry_status': ins_data.status,'vchr_service': ins_data.vchr_service,
            #     'vchr_mobile_num': ins_data.assigne_mobile,'vchr_enquiry_num': ins_data.vchr_enquiry_num,
            #     'fk_assigned__first_name': ins_data.staff_first_name,'dat_created_at': ins_data.dat_created_at,
            #     'fk_assigne__cust_fname': ins_data.assigne_first_name,'vchr_enquiry_source': ins_data.vchr_enquiry_source,
            #     'vchr_enquiry_priority': ins_data.vchr_enquiry_priority,
            #     'vchr_full_name': ins_data.assigne_first_name + ' ' + ins_data.assigne_last_name,'pk_bint_id': ins_data.pk_bint_id,
            #     'product':ins_data.vchr_service,
            #     'brand':ins_data.vchr_brand_name.title(),
            #     'item':ins_data.vchr_item_name.title()
            #             }
            # lst_table_data.append( dct_temp.copy())
            # ins_data=ins_data._asdict()
            if ins_data.vchr_staff_full_name not in dct_data['assigne_all']:
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['EnquiryQty'] = ins_data.qty
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['EnquiryValue'] = ins_data.value
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] = 0
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['SaleQty'] = 0
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['SaleValue'] = 0

                dct_data['assigne_service'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_item'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_status'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]={}
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]={}
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]={}

                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Enquiry'] = ins_data.counts
                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['EnquiryQty'] = ins_data.qty
                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['EnquiryValue'] = ins_data.value
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = 0
                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleQty'] = 0
                dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleValue'] = 0
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] = 0
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] = 0
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] = 0
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleValue'] = 0


                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['SaleQty'] = ins_data.qty
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['SaleValue'] = ins_data.value
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = ins_data.counts
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleValue'] = ins_data.value
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']=0
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=0
                dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=0

                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = 0

                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name]={}
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
            else:
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['EnquiryQty'] += ins_data.qty
                dct_data['assigne_all'][ins_data.vchr_staff_full_name]['EnquiryValue'] += ins_data.value
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['SaleQty'] += ins_data.qty
                    dct_data['assigne_all'][ins_data.vchr_staff_full_name]['SaleValue'] += ins_data.value
                if ins_data.vchr_service not in dct_data['assigne_service'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Enquiry'] = ins_data.counts
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['EnquiryQty'] = ins_data.qty
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['EnquiryValue'] = ins_data.value
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = 0
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleQty'] = 0
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleValue'] = 0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] = ins_data.counts
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleValue'] = ins_data.value
                else:
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Enquiry']+=ins_data.counts
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['EnquiryQty']+=ins_data.qty
                    dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['assigne_service'][ins_data.vchr_staff_full_name][ins_data.vchr_service]['SaleValue'] += ins_data.value



                if ins_data.vchr_brand_name.title() not in dct_data['assigne_brand'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value
                else:
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['assigne_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value


                if ins_data.vchr_item_name.title() not in dct_data['assigne_item'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                else:
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['assigne_item'][ins_data.vchr_staff_full_name][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value


                if ins_data.vchr_enquiry_status not in dct_data['assigne_status'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                else:
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                    dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['Sale'] += ins_data.counts
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleQty'] += ins_data.qty
                        dct_data['assigne_status'][ins_data.vchr_staff_full_name][ins_data.vchr_enquiry_status]['SaleValue'] += ins_data.value



                if ins_data.vchr_service not in dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status] = {}
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                else:
                    if ins_data.vchr_brand_name.title() not in dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']=0
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value
                    else:
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                        dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']+= ins_data.counts
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']+= ins_data.qty
                            dct_data['assigne_service_brand'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']+= ins_data.value

                    if ins_data.vchr_item_name.title() not in dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                    else:
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                        dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']+= ins_data.counts
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty']+= ins_data.qty
                            dct_data['assigne_service_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue']+= ins_data.value

                    if ins_data.vchr_enquiry_status not in dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                    else:
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                        dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']+= ins_data.counts
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']+= ins_data.qty
                            dct_data['assigne_service_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']+= ins_data.value

                if ins_data.vchr_service not in dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                else:
                    if ins_data.vchr_brand_name.title() not in dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                    else:
                        if ins_data.vchr_item_name.title() not in dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                        else:
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                            dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                                dct_data['assigne_service_brand_item'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                        if ins_data.vchr_enquiry_status not in dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                        else:
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                            dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                                dct_data['assigne_service_brand_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name]:
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                elif ins_data.vchr_brand_name.title() not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service]:
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                elif ins_data.vchr_item_name.title() not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                elif ins_data.vchr_enquiry_status not in dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value
                else:
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                    dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                        dct_data['assigne_service_brand_item_status'][ins_data.vchr_staff_full_name][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value

            if ins_data.vchr_service not in dct_data['service_all']:
                dct_data['service_all'][ins_data.vchr_service]={}
                # dct_data['service_assigne'][ins_data.vchr_service]={}

                # dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]={}
                # dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                # dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Sale'] = 0

                dct_data['service_all'][ins_data.vchr_service]['Enquiry']=ins_data.counts
                dct_data['service_all'][ins_data.vchr_service]['EnquiryQty']=ins_data.qty
                dct_data['service_all'][ins_data.vchr_service]['EnquiryValue']=ins_data.value
                dct_data['service_all'][ins_data.vchr_service]['Sale'] = 0
                dct_data['service_all'][ins_data.vchr_service]['SaleQty'] = 0
                dct_data['service_all'][ins_data.vchr_service]['SaleValue'] = 0
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['service_all'][ins_data.vchr_service]['Sale'] = ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service]['SaleQty'] = ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service]['SaleValue'] = ins_data.value
                    # dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
            else:
                dct_data['service_all'][ins_data.vchr_service]['Enquiry']+= ins_data.counts
                dct_data['service_all'][ins_data.vchr_service]['EnquiryQty']+= ins_data.qty
                dct_data['service_all'][ins_data.vchr_service]['EnquiryValue']+= ins_data.value
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['service_all'][ins_data.vchr_service]['Sale']+= ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service]['SaleQty']+= ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service]['SaleValue']+= ins_data.value
                # if ins_data.vchr_staff_full_name not in dct_data['service_assigne'][ins_data.vchr_service]:
                #     dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name] = {}
                #     dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                #     dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Sale'] = 0
                #     if ins_data.vchr_enquiry_status == 'INVOICED':
                #         dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
                # else:
                #     dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                #     if ins_data.vchr_enquiry_status == 'INVOICED':
                #         dct_data['service_assigne'][ins_data.vchr_service][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts

            if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=0

                # dct_data['brand_assigne'][ins_data.vchr_brand_name.title()]={}
                # dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]={}
                # dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                # dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Sale'] = 0
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    # dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
            else:
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value

                # if ins_data.vchr_staff_full_name not in dct_data['brand_assigne'][ins_data.vchr_brand_name.title()]:
                #     dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]={}
                #     dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Enquiry'] = ins_data.counts
                #     dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Sale'] = 0
                #
                #     if ins_data.vchr_enquiry_status == 'INVOICED':
                #         dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Sale'] = ins_data.counts
                # else:
                #     dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Enquiry'] += ins_data.counts
                #     if ins_data.vchr_enquiry_status == 'INVOICED':
                #         dct_data['brand_assigne'][ins_data.vchr_brand_name.title()][ins_data.vchr_staff_full_name]['Sale'] += ins_data.counts

            if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = 0
                dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
            else:
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
            if ins_data.vchr_enquiry_status not in dct_data['status_all']:
                dct_data['status_all'][ins_data.vchr_enquiry_status]={}
                dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale'] = 0
                dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
            else:
                dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                if ins_data.vchr_enquiry_status == 'INVOICED':
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale'] +=ins_data.counts
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleQty'] +=ins_data.qty
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleValue'] +=ins_data.value

        # for staff in lst_staffs:
        #     staff_full_name=staff.first_name+' '+staff.last_name
        #     if staff_full_name not in dct_data['assigne_all']:
        #         dct_data['assigne_all'][staff_full_name]={}
        #         dct_data['assigne_all'][staff_full_name]['Enquiry']=0
        #         dct_data['assigne_all'][staff_full_name]['EnquiryQty']=0
        #         dct_data['assigne_all'][staff_full_name]['EnquiryValue']=0
        #         dct_data['assigne_all'][staff_full_name]['Sale']=0
        #         dct_data['assigne_all'][staff_full_name]['SaleQty']=0
        #         dct_data['assigne_all'][staff_full_name]['SaleValue']=0

        dct_data['assigne_all']=paginate_data(dct_data['assigne_all'],10,request.data.get('type','Enquiry'))
        dct_data['brand_all']=paginate_data(dct_data['brand_all'],10,request.data.get('type','Enquiry'))
        dct_data['item_all']=paginate_data(dct_data['item_all'],10,request.data.get('type','Enquiry'))
        dct_data['service_all']=paginate_data(dct_data['service_all'],10,request.data.get('type','Enquiry'))

        # for key in dct_data['service_assigne']:
        #     dct_data['service_assigne'][key]=paginate_data(dct_data['service_assigne'][key],10,request.data.get('type','Enquiry'))
        # for key in dct_data['brand_assigne']:
        #     dct_data['brand_assigne'][key]=paginate_data(dct_data['brand_assigne'][key],10,request.data.get('type','Enquiry'))
        for key in dct_data['assigne_service']:
                dct_data['assigne_service'][key]=paginate_data(dct_data['assigne_service'][key],10,request.data.get('type','Enquiry'))
        for key in dct_data['assigne_brand']:
                dct_data['assigne_brand'][key]=paginate_data(dct_data['assigne_brand'][key],10,request.data.get('type','Enquiry'))
        for key in dct_data['assigne_item']:
                dct_data['assigne_item'][key]=paginate_data(dct_data['assigne_item'][key],10,request.data.get('type','Enquiry'))
        for key in dct_data['assigne_service_brand']:
            for key1 in dct_data['assigne_service_brand'][key]:
                dct_data['assigne_service_brand'][key][key1]=paginate_data(dct_data['assigne_service_brand'][key][key1],10,request.data.get('type','Enquiry'))
        for key in dct_data['assigne_service_item']:
            for key1 in dct_data['assigne_service_item'][key]:
                dct_data['assigne_service_item'][key][key1]=paginate_data(dct_data['assigne_service_item'][key][key1],10,request.data.get('type','Enquiry'))
        # import pdb;pdb.set_trace()
        for key in dct_data['assigne_service_brand_item']:
            for key1 in dct_data['assigne_service_brand_item'][key]:
                for key2 in dct_data['assigne_service_brand_item'][key][key1]:
                    dct_data['assigne_service_brand_item'][key][key1][key2]=paginate_data(dct_data['assigne_service_brand_item'][key][key1][key2],10,request.data.get('type','Enquiry'))
        # import pdb; pdb.set_trace()
        # rst_table=rst_table_data.subquery()
        # rst_promoter = session.query(rst_table.c.fk_assigned,\
        #             rst_table.c.vchr_staff_full_name,\
        #             case([(rst_table.c.fk_brand_id > 0,literal_column("'promoter'"))],else_=literal_column("'not promoter'"))).group_by(rst_table.c.fk_assigned, rst_table.c.vchr_staff_full_name,rst_table.c.fk_brand_id)

        return dct_data
    except Exception as msg:
        return str(msg)
