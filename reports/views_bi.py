import operator
import time
# from staff_rating.models import StaffRating
# from collections import Counter
# from urlcheck.models import UserLogDetails
from groups.models import Groups
from company_permissions.models import SubCategory
# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from userdetails.models import UserDetails as UserModel
from customer.models import CustomerDetails as CustomerModel
from django.contrib.auth.models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import case, literal_column
# import aldjemy
# import json
from datetime import datetime
from datetime import timedelta
from enquiry.models import EnquiryMaster, Document
from branch.models import Branch
from zone.models import Zone
from territory.models import Territory
from location.models import Country as Countries
# from enquiry.views import fun_travels_data,fun_software_data,fun_automobile_data
# from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry,ItemEnquiry
from enquiry_mobile.models import ItemEnquiry
# from enquiry.views import fun_travels_data,fun_software_data
# from inventory.models import Products,Brands,Items
from item_category.models import Item as Items
from products.models import Products
from brands.models import Brands
from company.models import Company as CompanyDetails
from titlecase import titlecase
from sqlalchemy import desc
from groups.models import Groups
from enquiry_print.views import enquiry_print
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from export_excel.views import export_excel
from collections import OrderedDict
import pandas as pd
from aldjemy.core import get_engine
# from software.models import AccountingSoftware,EmployeeManagement,EnquiryTrack,HrSolutions
from django.db.models import Q
# from auto_mobile.models import SedanEnquiry,SuvEnquiry,HatchbackEnquiry
# from enquiry_solar.models import ProductType,ProductBrand, ProductCategory, ProductCategoryVariant, ProductEnquiry
# from location.models import Location
from globalMethods import show_data_based_on_role,get_user_products,get_branch_on_permission
from vincent.colors import brews
import random
from django.conf import settings
# from enquiry_mobile.tasks import email_sent
from collections import OrderedDict

import pandas as pd
from vincent.colors import brews
from django.db.models import F
from django.db.models.functions import Upper
# -------------------------------------
from django.shortcuts import render
import pandas as pd
from collections import OrderedDict
import operator
from django.core.mail import EmailMultiAlternatives
from os import path,makedirs,remove,listdir
from adminsettings.models import AdminSettings
# from service.models import JobMaster,ItemService,JobSpareDetails
from invoice.models import PaymentDetails
from zone.models import Zone
import psycopg2.extras

# LocationSA=Location.sa
CustomerSA = CustomerModel.sa
UserSA=UserModel.sa
AuthUserSA = User.sa
# ProductTypeSA = ProductType.sa
# ProductBrandSA = ProductBrand.sa
# ProductCategorySA = ProductCategory.sa
# ProductEnquirySA=ProductEnquiry.sa
# UserLogDetailsSA= UserLogDetails.sa
SubCategorySA = SubCategory.sa
GroupsSA = Groups.sa

# JobMasterSA = JobMaster.sa
# JobSpareDetailsSA = JobSpareDetails.sa
# ItemServiceSA = ItemService.sa

EnquiryMasterSA = EnquiryMaster.sa
# FlightsSA = Flights.sa
# TrainSA = Train.sa
# ForexSA = Forex.sa
# VisaSA = Visa.sa
# OtherSA = Other.sa
# HotelSA=Hotel.sa
# RoomSA=Rooms.sa
# OtherSA=Other.sa
# TransportSA=Transport.sa
# TravelInsuranceSA=TravelInsurance.sa
# PackageSA=Package.sa
BranchSA = Branch.sa
# MobileEnquirySA = MobileEnquiry.sa
# TabletEnquirySA = TabletEnquiry.sa
# ComputersEnquirySA = ComputersEnquiry.sa
# AccessoriesEnquirySA = AccessoriesEnquiry.sa
ProductSA = Products.sa
ItemsSA=Items.sa
BrandsSA=Brands.sa
ItemEnquirySA =ItemEnquiry.sa
TerritorySA = Territory.sa
# HatchbackEnquirySA = HatchbackEnquiry.sa
# SedanEnquirySA = SedanEnquiry.sa
# SuvEnquirySA = SuvEnquiry.sa

# EnquiryTrackSA = EnquiryTrack.sa
# AccountingSoftwareSA = AccountingSoftware.sa
# HrSolutionsSA = HrSolutions.sa
# EmployeeManagementSA = EmployeeManagement.sa

PaymentDetailsSA = PaymentDetails.sa
ZoneSA = Zone.sa
engine = get_engine()

# try:
#     # import pdb; pdb.set_trace()
#     userName = settings.DATABASES['default']['USER']
#     password = settings.DATABASES['default']['PASSWORD']
#     host = settings.DATABASES['default']['HOST']
#     database = settings.DATABASES['default']['NAME']
#     conn = psycopg2.connect(host=host,database=database, user=userName, password=password)
#     # conn = psycopg2.connect(host="localhost",database="bi", user="admin", password="tms@123")
#     cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
#     conn.autocommit = True
# except Exception as e:
#     print ("Cannot connect to Data Base..")

def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

def get_col_widths(dataframe):
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


class UserLogDetailsReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            dat_from = request.data.get('date_from')
            dat_to = request.data.get('dat_to')
            session = Session()
            rst_data = session.query(AuthUserSA.first_name,AuthUserSA.last_name,GroupsSA.vchr_name.label('group'),AuthUserSA.id.label('user_id'),\
            func.sum(UserLogDetailsSA.int_count).label('count'),SubCategorySA.vchr_sub_category_name.label('module'),\
            BranchSA.vchr_name.label('branch'))\
            .join(UserSA,UserSA.user_ptr_id==AuthUserSA.id)\
            .join(GroupsSA,GroupsSA.pk_bint_id==UserSA.fk_group_id)\
            .join(UserLogDetailsSA,UserLogDetailsSA.fk_user_id==AuthUserSA.id)\
            .join(SubCategorySA,SubCategorySA.pk_bint_id==UserLogDetailsSA.fk_module_id)\
            .outerjoin(BranchSA,BranchSA.pk_bint_id==UserSA.fk_branch_id)\
            .filter(func.DATE(UserLogDetailsSA.dat_start_active)>=dat_from,func.DATE(UserLogDetailsSA.dat_start_active)<=dat_to)\
            .group_by(AuthUserSA.first_name,AuthUserSA.last_name,GroupsSA.vchr_name,SubCategorySA.vchr_sub_category_name,AuthUserSA.id,BranchSA.vchr_name)

            if request.data.get_list('lst_branch_id',[]):
                rst_data = rst_data.filter(BranchSA.pk_bint_id.in_(request.data.get_list('lst_branch_id',[])))
            if request.data.get_list('lst_user_id',[]):
                rst_data = rst_data.filter(AuthUserSA.id.in_(request.data.get_list('lst_user_id')))
            if request.data.get_list('lst_group_id',[]):
                rst_data = rst_data.filter(GroupsSA.pk_bint_id.in_(request.data.get_list('lst_group_id')))
            if not rst_data.all():
                session.close()
                return Response({'status':'failed','reason':'No data'})

            dct_log_data= {}
            for ins_data in rst_data.all():
                if str(ins_data.user_id) not in dct_log_data:
                    dct_log_data[str(ins_data.user_id)]={}
                    dct_log_data[str(ins_data.user_id)]['user']=(ins_data.first_name+' '+ins_data.last_name).title()
                    dct_log_data[str(ins_data.user_id)]['group']=ins_data.group.title()
                    dct_log_data[str(ins_data.user_id)]['branch']=ins_data.branch.title() if ins_data.branch else None
                    dct_log_data[str(ins_data.user_id)]['module_details']= []
                    dct_module = {}
                    dct_module['module'] = ins_data.module.title()
                    dct_module['count']= ins_data.count
                    dct_log_data[str(ins_data.user_id)]['module_details'].append(dct_module)
                else:
                    dct_module = {}
                    dct_module['module'] = ins_data.module.title()
                    dct_module['count']= ins_data.count
                    dct_log_data[str(ins_data.user_id)]['module_details'].append(dct_module)
            lst_log_details = list(dct_log_data.values())
            return Response({'status':'success','data':lst_log_details})
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})

class BranchTypehead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_branch = []
            if str_search_term != -1:
                ins_branch = Branch.objects.filter(Q(vchr_code__icontains=str_search_term)| Q(vchr_name__icontains=str_search_term)).values('pk_bint_id','vchr_code', 'vchr_name')
                if ins_branch:
                    for itr_item in ins_branch:
                        dct_branch = {}
                        dct_branch['code'] = itr_item['vchr_code']
                        dct_branch['name'] = itr_item['vchr_name']
                        dct_branch['id'] = itr_item['pk_bint_id']
                        lst_branch.append(dct_branch)
                return Response({'status':'success','data':lst_branch})
            else:
                return Response({'status':'empty','data':lst_branch})
        except Exception as e:
            return JsonResponse({'result':'failed','reason':e})

class NewCustomerReport(APIView):
    # permission_classes = [IsAuthenticated]
    # def post(self,request):
    #     try:
    #         user_id = request.data.get('user_id',-1)
    #         blnExcel = request.data.get('excel',False)
    #         if  user_id == -1:
    #             return JsonResponse({'status':'failed','data':'this usr not registered'})
    #         user_id = UserModel.objects.get(id = int(request.data.get('user_id'))).id
    #         company_id = UserModel.objects.get(id = user_id).fk_company_id
    #
    #
    #
    #         dat_from = request.data.get('date_from')
    #         # dat_to = request.data.get('dat_to')
    #         dat_to = (datetime.strptime(request.data.get('date_to'),'%a %b %d %Y') + timedelta(1)).strftime('%a %b %d %Y')
    #         # test = datetime.strptime(dat_to,'%a %b %d %Y')
    #         # import pdb; pdb.set_trace()
    #         session = Session()
    #
    #         if request.data.get('branch_id'):
    #             int_branch_id = int(request.data.get('branch_id'))
    #             rst_data = session.query(CustomerSA.cust_fname.label('cust_fname'),CustomerSA.cust_lname.label('cust_lname'),CustomerSA.cust_customertype.label('cust_type'),CustomerSA.cust_contactsrc.label('cust_contact'),\
    #                                 CustomerSA.dat_created.label('cust_registered_date'),AuthUserSA.first_name.label('staff_fname'),AuthUserSA.last_name.label('staff_lname') , BranchSA.vchr_name.label('branch_name'),LocationSA.vchr_name.label("location"))\
    #                                 .filter(CustomerSA.dat_created<=dat_to,CustomerSA.dat_created>=dat_from,CustomerSA.fk_company_id == company_id,BranchSA.pk_bint_id == int_branch_id)\
    #                                 .join(AuthUserSA,CustomerSA.fk_user_id == AuthUserSA.id)\
    #                                 .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
    #                                 .join(BranchSA, UserSA.fk_branch_id == BranchSA.pk_bint_id)\
    #                                 .outerjoin(LocationSA,LocationSA.pk_bint_id==CustomerSA.fk_location_id)
    #         else:
    #             rst_data = session.query(CustomerSA.cust_fname.label('cust_fname'),CustomerSA.cust_lname.label('cust_lname'),CustomerSA.cust_customertype.label('cust_type'),CustomerSA.cust_contactsrc.label('cust_contact'),\
    #                                 CustomerSA.dat_created.label('cust_registered_date'),AuthUserSA.first_name.label('staff_fname'),AuthUserSA.last_name.label('staff_lname') , BranchSA.vchr_name.label('branch_name'),LocationSA.vchr_name.label("location"))\
    #                                 .filter(CustomerSA.dat_created<=dat_to,CustomerSA.dat_created>=dat_from,CustomerSA.fk_company_id == company_id)\
    #                                 .join(AuthUserSA,CustomerSA.fk_user_id == AuthUserSA.id)\
    #                                 .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
    #                                 .join(BranchSA, UserSA.fk_branch_id == BranchSA.pk_bint_id)\
    #                                 .outerjoin(LocationSA,LocationSA.pk_bint_id==CustomerSA.fk_location_id)
    #
    #         rst_data = rst_data.order_by(desc(CustomerSA.dat_created))
    #         """Permission wise filter for data"""
    #         if request.user.usermodel.fk_group.vchr_name.upper()=='ADMIN':
    #             pass
    #         elif request.user.usermodel.fk_group.vchr_name.upper()=='BRANCH MANAGER':
    #             rst_data = rst_data.filter(BranchSA.pk_bint_id == request.user.usermodel.fk_branch_id)
    #         elif request.user.usermodel.int_area_id:
    #             lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
    #             rst_data = rst_data.filter(BranchSA.pk_bint_id.in_(lst_branch))
    #         else:
    #             return Response({'status':'failed','reason':'No data'})
    #
    #         if request.data.get('customerType') and request.data.get('customerType') != 'ALL':
    #             rst_data = rst_data.filter(CustomerSA.cust_customertype == request.data.get('customerType'))
    #
    #
    #         if request.data.get('source') and request.data.get('source') != 'ALL':
    #             rst_data = rst_data.filter(CustomerSA.cust_contactsrc == request.data.get('source'))
    #         lst_data = []
    #         for dct_temp in rst_data.all():
    #             lst_data.append(dct_temp._asdict())
    #         # ins_customer = list(CustomerModel.objects.filter())
    #         if request.data.get('branch_id'):
    #             ins_branchs = Branch.objects.filter(pk_bint_id = request.data.get('branch_id')).values('vchr_name')
    #             str_branch_name = ins_branchs[0]['vchr_name']
    #         else:
    #             str_branch_name = 'All'
    #         if blnExcel:
    #             lst_excel_data = []
    #             for dct_data in lst_data:
    #                 dct_temp = OrderedDict()
    #                 dct_temp['Registered Date'] = str(datetime.strptime(str(dct_data.get('cust_registered_date'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
    #                 dct_temp['Customer Name'] = (dct_data.get('cust_fname') + " " + dct_data.get('cust_lname')).title()
    #                 dct_temp['Customer Type'] = str(dct_data.get('cust_type'))
    #                 dct_temp['Staff Name'] = (dct_data.get('staff_fname') + " " + dct_data.get('staff_lname')).title()
    #                 dct_temp['Branch Name'] = str(dct_data.get('branch_name')).title()
    #                 lst_excel_data.append(dct_temp)
    #             from_date = datetime.strptime(request.data.get('dat_from'),'%a %b %d %Y').strftime('%d-%m-%Y')
    #             to_date = datetime.strptime(request.data.get('dat_to'),'%a %b %d %Y').strftime('%d-%m-%Y')
    #             # print(to_date)
    #             # to_date = datetime.datetime.strptime((test + datetime.timedelta(1)).strftime('%d-%m-%Y'),'%d-%m-%Y')
    #             # print(to_date)
    #             lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Registered Date'])
    #             response = export_excel('new customer',str_branch_name,from_date,to_date,lst_excel_data)
    #             if response != False:
    #                 return JsonResponse({'status': 'success', 'path':response})
    #             else:
    #                 return JsonResponse({'status': 'failure'})
    #         else:
    #             return JsonResponse({'status':'success','data':lst_data})
    #     except Exception as msg:
    #         # print(msg)
    #         return JsonResponse({'status':'failed','data':str(msg)})
    def post(self,request):
        try:
            session = Session()
            date_from = datetime.strptime(request.data.get('date_from'),'%a %b %d %Y')
            date_to = datetime.strptime(request.data.get('date_to'),'%a %b %d %Y')
            rst_data = ''
            if request.data.get('show_type'):
                rst_data = session.query(ItemEnquirySA.vchr_enquiry_status,func.sum(ItemEnquirySA.dbl_amount).label('counts'),func.sum(ItemEnquirySA.int_quantity).label('qty'),func.sum(ItemEnquirySA.dbl_amount).label('value'),BranchSA.vchr_name.label('vchr_branch_name'),func.concat(CustomerSA.cust_fname,' ',CustomerSA.cust_lname).label('vchr_customer_name'),ProductSA.vchr_product_name,BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,CustomerSA.dat_created)\
                                .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                .join(ProductSA,ItemEnquirySA.fk_product_id == ProductSA.id)\
                                .join(BrandsSA,ItemEnquirySA.fk_brand_id == BrandsSA.id)\
                                .join(ItemsSA,ItemEnquirySA.fk_item_id == ItemsSA.id)\
                                .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                                .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= date_from,cast(EnquiryMasterSA.dat_created_at,Date) <= date_to)\
                                .group_by(ItemEnquirySA.vchr_enquiry_status,BranchSA.vchr_name,CustomerSA.cust_fname,CustomerSA.cust_lname,ProductSA.vchr_product_name,BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,CustomerSA.dat_created)\
                                .order_by(CustomerSA.dat_created.desc())
            else:
                rst_data = session.query(ItemEnquirySA.vchr_enquiry_status,func.sum(ItemEnquirySA.int_quantity).label('counts'),func.sum(ItemEnquirySA.int_quantity).label('qty'),func.sum(ItemEnquirySA.dbl_amount).label('value'),BranchSA.vchr_name.label('vchr_branch_name'),func.concat(CustomerSA.cust_fname,' ',CustomerSA.cust_lname).label('vchr_customer_name'),ProductSA.vchr_product_name,BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,CustomerSA.dat_created)\
                                .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                .join(ProductSA,ItemEnquirySA.fk_product_id == ProductSA.id)\
                                .join(BrandsSA,ItemEnquirySA.fk_brand_id == BrandsSA.id)\
                                .join(ItemsSA,ItemEnquirySA.fk_item_id == ItemsSA.id)\
                                .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                                .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= date_from,cast(EnquiryMasterSA.dat_created_at,Date) <= date_to)\
                                .group_by(ItemEnquirySA.vchr_enquiry_status,BranchSA.vchr_name,CustomerSA.cust_fname,CustomerSA.cust_lname,ProductSA.vchr_product_name,BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,CustomerSA.dat_created)\
                                .order_by(CustomerSA.dat_created.desc())

            if request.user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','GENERAL MANAGER SALES','COUNTRY HEAD']:
                pass
            elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                rst_data = rst_data.filter(BranchSA.pk_bint_id == request.user.usermodel.fk_branch_id)
            elif request.user.usermodel.int_area_id:
                lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
                rst_data = rst_data.filter(BranchSA.pk_bint_id.in_(lst_branch))
            else:
                session.close()
                return Response({'status':'failed','reason':'No data'})

            if request.data.get('branch_id'):
                rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id == request.data.get('branch_id'))

            # import pdb; pdb.set_trace()
            #for getting user corresponding products
            lst_user_id =[]
            lst_user_id.append(request.user.id)
            lst_user_products = get_user_products(lst_user_id)
            if lst_user_products:
                rst_data = rst_data.filter(ProductSA.id.in_(lst_user_products))


            # import pdb; pdb.set_trace()
            if not rst_data.all():
                session.close()
                return Response({'status':'failed','reason':'No data'})

            dct_data = {}
            dct_data['branch_all'] = {}
            dct_data['customer_all'] = OrderedDict()
            dct_data['product_all'] = {}
            dct_data['brand_all'] = {}
            dct_data['item_all'] = {}
            dct_data['status_all'] = {}
            dct_data['branch_customer'] = {}
            dct_data['branch_product'] = {}
            dct_data['branch_brand'] = {}
            dct_data['branch_item'] = {}
            dct_data['branch_status'] = {}
            dct_data['branch_customer_product'] = {}
            dct_data['branch_customer_brand'] = {}
            dct_data['branch_customer_item'] = {}
            dct_data['branch_customer_status'] = {}
            dct_data['branch_customer_product_brand'] = {}
            dct_data['branch_customer_product_item'] = {}
            dct_data['branch_customer_product_status'] = {}
            dct_data['branch_customer_product_brand_item'] = {}
            dct_data['branch_customer_product_brand_status'] = {}
            dct_data['branch_customer_product_brand_item_status'] = {}

            for ins_data in rst_data:
                if ins_data.vchr_branch_name.title() not in dct_data['branch_all']:
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['Sale'] = 0
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['SaleQty'] = 0
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['Sale'] = 0
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['SaleValue'] = 0

                    dct_data['branch_product'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['Sale'] = 0
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['SaleQty'] = 0
                    dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['SaleValue'] = 0

                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()] = {}
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0

                    dct_data['branch_item'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()] = {}
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0

                    dct_data['branch_status'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                    dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Sale'] = 0
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()] = {}
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()] = {}
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                    dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()] = {}
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0

                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()] = {}
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                else:
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['branch_all'][ins_data.vchr_branch_name.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_customer_name.title() not in dct_data['branch_customer'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['Sale'] = 0
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['SaleValue'] = 0
                    else:
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['Enquiry'] += ins_data.counts
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['branch_customer'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_product_name.title() not in dct_data['branch_product'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['Sale'] = 0
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['SaleQty'] = 0
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['SaleValue'] = 0
                    else:
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] += ins_data.counts
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['branch_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_brand_name.title() not in dct_data['branch_brand'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()] = {}
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    else:
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['branch_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_item_name.title() not in dct_data['branch_item'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()] = {}
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    else:
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['branch_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_enquiry_status.title() not in dct_data['branch_status'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                    else:
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] += ins_data.counts
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['branch_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_customer_name.title() not in dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()] = {}
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()] = {}
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Sale'] = 0
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['SaleValue'] = 0
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                        dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                    else:
                        if ins_data.vchr_product_name.title() not in dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Sale'] = 0
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['SaleValue'] = 0
                        else:
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['Enquiry'] += ins_data.counts
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryQty'] += ins_data.qty
                            dct_data['branch_customer_product'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]['EnquiryValue'] += ins_data.value

                        if ins_data.vchr_brand_name.title() not in dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()] = {}
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                        else:
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                            dct_data['branch_customer_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                        if ins_data.vchr_item_name.title() not in dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()] = {}
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                        else:
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                            dct_data['branch_customer_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                        if ins_data.vchr_enquiry_status.title() not in dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                        else:
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] += ins_data.counts
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] += ins_data.qty
                            dct_data['branch_customer_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_customer_name.title() not in dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()] = {}
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                    else:
                        if ins_data.vchr_product_name.title() not in dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()] = {}
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                        else:
                            if ins_data.vchr_brand_name.title() not in dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]:
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Sale'] = 0
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                            else:
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                                dct_data['branch_customer_product_brand'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                            if ins_data.vchr_item_name.title() not in dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]:
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()] = {}
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                            else:
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                                dct_data['branch_customer_product_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                            if ins_data.vchr_enquiry_status.title() not in dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]:
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                            else:
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] += ins_data.counts
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] += ins_data.qty
                                dct_data['branch_customer_product_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_customer_name.title() not in dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                    else:
                        if ins_data.vchr_product_name.title() not in dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                        else:
                            if ins_data.vchr_brand_name.title() not in dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]:
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                                dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                                dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                            else:
                                if ins_data.vchr_item_name.title() not in dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]:
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale'] = 0
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                                else:
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                                    dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                                if ins_data.vchr_enquiry_status.title() not in dct_data['branch_customer_product_brand_item'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]:
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                                else:
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] += ins_data.counts
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] += ins_data.qty
                                    dct_data['branch_customer_product_brand_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_customer_name.title() not in dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()]:
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()] = {}
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                    else:
                        if ins_data.vchr_product_name.title() not in dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()]:
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()] = {}
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                            dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                        else:
                            if ins_data.vchr_brand_name.title() not in dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()]:
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()] = {}
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                                dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                            else:
                                if ins_data.vchr_item_name.title() not in dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()]:
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                                    dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                                else:
                                    if ins_data.vchr_enquiry_status.title() not in dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()] = {}
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                                    else:
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['Enquiry'] += ins_data.counts
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] += ins_data.qty
                                        dct_data['branch_customer_product_brand_item_status'][ins_data.vchr_branch_name.title()][ins_data.vchr_customer_name.title()][ins_data.vchr_product_name.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] += ins_data.value

                if ins_data.vchr_customer_name.title() not in dct_data['customer_all']:
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()] = {}
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['Sale'] = 0
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['SaleQty'] = 0
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['SaleValue'] = 0
                else:
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['customer_all'][ins_data.vchr_customer_name.title()]['EnquiryValue'] += ins_data.value

                if ins_data.vchr_product_name.title() not in dct_data['product_all']:
                    dct_data['product_all'][ins_data.vchr_product_name.title()] = {}
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['Sale'] = 0
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['SaleQty'] = 0
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['SaleValue'] = 0
                else:
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['product_all'][ins_data.vchr_product_name.title()]['EnquiryValue'] += ins_data.value

                if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                else:
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                    dct_data['item_all'][ins_data.vchr_item_name.title()] = {}
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                else:
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                if ins_data.vchr_enquiry_status.title() not in dct_data['status_all']:
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()] = {}
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['Enquiry'] = ins_data.counts
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] = ins_data.value
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['Sale'] = 0
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['SaleQty'] = 0
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['SaleValue'] = 0
                else:
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['Enquiry'] += ins_data.counts
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['status_all'][ins_data.vchr_enquiry_status.title()]['EnquiryValue'] += ins_data.value

            dct_data['branch_all'] = paginate_data1(dct_data['branch_all'],10)
            dct_data['customer_all'] = paginate_data1(dct_data['customer_all'],10)
            dct_data['product_all'] = paginate_data1(dct_data['product_all'],10)
            dct_data['brand_all'] = paginate_data1(dct_data['brand_all'],10)
            dct_data['item_all'] = paginate_data1(dct_data['item_all'],10)

            for key in dct_data['branch_customer']:
                dct_data['branch_customer'][key] = paginate_data1(dct_data['branch_customer'][key],10)

            for key in dct_data['branch_product']:
                dct_data['branch_product'][key] = paginate_data1(dct_data['branch_product'][key],10)

            for key in dct_data['branch_brand']:
                dct_data['branch_brand'][key] = paginate_data1(dct_data['branch_brand'][key],10)

            for key in dct_data['branch_item']:
                dct_data['branch_item'][key] = paginate_data1(dct_data['branch_item'][key],10)

            for key in dct_data['branch_customer_product']:
                for key1 in dct_data['branch_customer_product'][key]:
                    dct_data['branch_customer_product'][key][key1]=paginate_data1(dct_data['branch_customer_product'][key][key1],10)

            for key in dct_data['branch_customer_brand']:
                for key1 in dct_data['branch_customer_brand'][key]:
                    dct_data['branch_customer_brand'][key][key1]=paginate_data1(dct_data['branch_customer_brand'][key][key1],10)

            for key in dct_data['branch_customer_item']:
                for key1 in dct_data['branch_customer_item'][key]:
                    dct_data['branch_customer_item'][key][key1]=paginate_data1(dct_data['branch_customer_item'][key][key1],10)

            for key in dct_data['branch_customer_product_brand']:
                for key1 in dct_data['branch_customer_product_brand'][key]:
                    for key2 in dct_data['branch_customer_product_brand'][key][key1]:
                        dct_data['branch_customer_product_brand'][key][key1][key2]=paginate_data1(dct_data['branch_customer_product_brand'][key][key1][key2],10)

            for key in dct_data['branch_customer_product_item']:
                for key1 in dct_data['branch_customer_product_item'][key]:
                    for key2 in dct_data['branch_customer_product_item'][key][key1]:
                        dct_data['branch_customer_product_item'][key][key1][key2]=paginate_data1(dct_data['branch_customer_product_item'][key][key1][key2],10)

            for key in dct_data['branch_customer_product_brand_item']:
                for key1 in dct_data['branch_customer_product_brand_item'][key]:
                    for key2 in dct_data['branch_customer_product_brand_item'][key][key1]:
                        for key3 in dct_data['branch_customer_product_brand_item'][key][key1][key2]:
                            dct_data['branch_customer_product_brand_item'][key][key1][key2][key3]=paginate_data1(dct_data['branch_customer_product_brand_item'][key][key1][key2][key3],10)
            # if request.data['document'].upper() == 'PDF':
            if request.data.get('bln_chart'):
                from pdfGenerate import generate_pdf
                str_report_name = 'New Customer Report'
                lst_details = ['branch_all-bar','customer_all-bar','product_all-bar','brand_all-bar','item_all-bar','status_all-pie']
                dct_label = {'branch_all':'Branch wise','customer_all':'Customer wise','product_all':'Product wise','brand_all':'Brand wise','item_all':'Item wise','status_all':'Status wise'}
                request.data['date_from']=datetime.strftime(datetime.strptime(request.data['date_from'], '%a %b %d %Y' ),"%Y-%m-%d")
                request.data['date_to']=datetime.strftime(datetime.strptime(request.data['date_to'], '%a %b %d %Y' ),"%Y-%m-%d")
                dct_temp={}
                for data in lst_details:
                    if data.split('-')[1]=='bar':
                        dct_temp[data.split('-')[0]]=[]
                        for dat in dct_data[data.split('-')[0]][1]:
                            dct = {}
                            dct[dat]=dct_data[data.split('-')[0]][1][dat]
                            dct_temp[data.split('-')[0]].append(dct)
                    else:
                        dct_temp[data.split('-')[0]]=dct_data[data.split('-')[0]]
                file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_temp)
                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":"success",'file':file_output['file'],'file_name':file_output['file_name']})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":"success"})
            session.close()
            return JsonResponse({'status':'success','data':dct_data})
        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})

def paginate_data1(dct_data, int_page_legth):
    dct_paged = {}
    int_count = 1
    for key in dct_data:
        if int_count not in dct_paged:
            dct_paged[int_count] = OrderedDict()
            dct_paged[int_count][key] = dct_data[key]
        elif len(dct_paged[int_count]) < int_page_legth:
            dct_paged[int_count][key] = dct_data[key]
        else:
            int_count += 1
            dct_paged[int_count] = OrderedDict()
            dct_paged[int_count][key] = dct_data[key]
    return dct_paged

class ServiceReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            session = Session()
            lst_enquiry_data = []
            int_company = request.data['company_id']
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)

            fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
            todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )


            if ins_company[0].fk_company_type.vchr_company_type == 'TRAVEL AND TOURISM':
                rst_data = fun_travels_data(int_company)
            elif ins_company[0].fk_company_type.vchr_company_type == 'SOFTWARE':
                rst_data = fun_software_data(int_company)
            elif ins_company[0].fk_company_type.vchr_company_type == 'AUTOMOBILE':
                session = Session()
                rst_hatchback = session.query(literal("Hatchback").label("vchr_service"),HatchbackEnquirySA.vchr_enquiry_status.label('status'),HatchbackEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_sedan = session.query(literal("Sedan").label("vchr_service"),SedanEnquirySA.vchr_enquiry_status.label('status'),SedanEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_suv = session.query(literal("Suv").label("vchr_service"),SuvEnquirySA.vchr_enquiry_status.label('status'),SuvEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_data = rst_hatchback.union_all(rst_sedan,rst_suv).subquery()
            elif ins_company[0].fk_company_type.vchr_company_type == 'MOBILE':
                rst_data = session = Session()
                rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
                # return rst_data
            # import pdb; pdb.set_trace()
            # if not request.data.get('branch'):
            rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                    rst_data.c.vchr_service, CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),rst_data.c.status,\
                                    CustomerSA.cust_mobile.label('customer_mobile'),BranchSA.vchr_name.label('branch_name'),AuthUserSA.id.label('user_id'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
                                    .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == int_company )\
                                    .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
                                    .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                    .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                    .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
                                    .join(BranchSA, BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)

            if request.data.get('branch'):
                branch = request.data.get('branch')
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == branch)
            if request.data.get('staff'):
                staff = request.data.get('staff')
                rst_enquiry = rst_enquiry.filter(AuthUserSA.id == staff)
            # EDIT
            rst_enquiry_set = rst_enquiry.subquery()
            rst_service_count_all = session.query(rst_enquiry_set.c.vchr_service, func.count(rst_enquiry_set.c.vchr_service).label('count'),func.count(case([((rst_enquiry_set.c.status == 'BOOKED'),rst_enquiry_set.c.vchr_service)],else_=literal_column("NULL"))).label("booked_count")).group_by(rst_enquiry_set.c.vchr_service)

            lst_service_count_all = {}
            lst_enquiry_labels = []
            lst_enquiry_booked = []
            lst_enquiry_all = []
            for serv in rst_service_count_all.all():
                lst_service_count_all[serv.vchr_service] = serv.count
                lst_enquiry_labels.append(serv.vchr_service)
                lst_enquiry_booked.append(serv.booked_count)
                lst_enquiry_all.append(serv.count)

            rst_employee_count_all = session.query(rst_enquiry_set.c.user_id,rst_enquiry_set.c.staff_first_name.label('first_name'), func.count(rst_enquiry_set.c.user_id).label('count'),func.count(case([((rst_enquiry_set.c.status == 'BOOKED'),rst_enquiry_set.c.user_id)],else_=literal_column("NULL"))).label("booked_count")).group_by(rst_enquiry_set.c.user_id,rst_enquiry_set.c.staff_first_name)
            lst_employee_count_all = {}
            lst_employee_labels = []
            lst_employee_booked = []
            lst_employee_all = []
            for emp in rst_employee_count_all.all():
                lst_employee_count_all[emp.first_name] = emp.count
                lst_employee_labels.append(emp.first_name)
                lst_employee_booked.append(emp.booked_count)
                lst_employee_all.append(emp.count)


            lst_status_count_all = {}
            rst_status_count_all = session.query(rst_enquiry_set.c.status.label('status'),func.count(rst_enquiry_set.c.status).label('count')).group_by(rst_enquiry_set.c.status)
            for status in rst_status_count_all.all():
                lst_status_count_all[status.status] = status.count

            # if request.data.get('status'):
            status = request.data.get('status')
            rst_enquiry_booked = rst_enquiry.filter(rst_data.c.status == status)
            rst_user_wise = session.query(func.count(rst_data.c.FK_Enquery).label('count'),rst_data.c.status.label('status'),rst_data.c.vchr_service.label('service'),AuthUserSA.id.label('user_id')).join(EnquiryMasterSA,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N')).join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).group_by(rst_data.c.vchr_service,rst_data.c.status,AuthUserSA.id).filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == int_company ).subquery()
            rst_user_data = session.query(rst_user_wise.c.count.label('count'), rst_user_wise.c.status.label('status'),rst_user_wise.c.service.label('service'),AuthUserSA.first_name.label('first_name'),AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('last_name')).join(AuthUserSA,AuthUserSA.id == rst_user_wise.c.user_id)
            dct_user_wise = {}

            for dct_data in rst_user_data.all():
                str_full_name = dct_data._asdict()['first_name'] + ' ' + dct_data._asdict()['last_name']
                str_full_name = str_full_name.lower()
                if str_full_name in dct_user_wise.keys():
                    if dct_data._asdict()['service'] in dct_user_wise[str_full_name].keys():
                        dct_user_wise[str_full_name][dct_data._asdict()['service']][0].append(dct_data._asdict()['status'])
                        dct_user_wise[str_full_name][dct_data._asdict()['service']][1].append(dct_data._asdict()['count'])
                    else:
                        dct_user_wise[str_full_name][dct_data._asdict()['service']] = [[dct_data._asdict()['status']],[dct_data._asdict()['count']]]
                else:
                    dct_user_wise[str_full_name] = {dct_data._asdict()['service']:[[dct_data._asdict()['status']],[dct_data._asdict()['count']]]}
            lst_enquiry_data = []
            dct_service_wise = {}
            for ins_enquiry in rst_enquiry.all():
                lst_enquiry_data.append(ins_enquiry._asdict())
                dct_temp = ins_enquiry._asdict()
                if dct_temp['vchr_service'] not in dct_service_wise.keys():
                    dct_service_wise[dct_temp['vchr_service']] = {dct_temp['user_id']:{'BOOKED':0,'ALL':0, 'NAME':(dct_temp['staff_first_name']+' '+dct_temp['staff_last_name']).title()}}


                elif dct_temp['user_id'] not in dct_service_wise[dct_temp['vchr_service']].keys():
                    dct_service_wise[dct_temp['vchr_service']][dct_temp['user_id']] = {'BOOKED':0,'ALL':0,'NAME':(dct_temp['staff_first_name']+' '+dct_temp['staff_last_name']).title()}

                if dct_temp['status'] == 'BOOKED':
                    dct_service_wise[dct_temp['vchr_service']][dct_temp['user_id']]['BOOKED'] += 1
                    dct_service_wise[dct_temp['vchr_service']][dct_temp['user_id']]['ALL'] += 1

                else:
                    dct_service_wise[dct_temp['vchr_service']][dct_temp['user_id']]['ALL'] += 1

            lst_enquiry_data_booked = []
            for ins_enquiry_booked in rst_enquiry_booked.all():
                lst_enquiry_data_booked.append(ins_enquiry_booked._asdict())
            # lst_service_count_all = Counter(tok['vchr_service'] for tok in lst_enquiry_data)
            # lst_employee_count_all = Counter((tok['staff_first_name']+' '+tok['staff_last_name']).title() for tok in lst_enquiry_data)
            # lst_status_count_all = Counter(tok['status'] for tok in lst_enquiry_data)

            lst_labels=[]
            lst_all = []
            lst_booked = []
            # lst_employee_labels=[]
            # lst_employee_all = []
            # lst_employee_booked = []

            # lst_service_count_all_booked = Counter(tok['vchr_service'] for tok in lst_enquiry_data_booked)
            # lst_employee_count_all_booked = Counter((tok['staff_first_name']+' '+tok['staff_last_name']).title() for tok in lst_enquiry_data_booked)
            # lst_status_count_all_booked = Counter(tok['status'] for tok in lst_enquiry_data_booked)
            # for key in lst_service_count_all.keys():
            #     lst_labels.append(key)
            #     lst_all.append(lst_service_count_all.get(key))
            #     if lst_service_count_all_booked.get(key):
            #         lst_booked.append(lst_service_count_all_booked.get(key))
            #     else:
            #         lst_booked.append(0)
            # for key in lst_employee_count_all.keys():
            #     lst_employee_labels.append(key)
            #     lst_employee_all.append(lst_employee_count_all.get(key))
            #     if lst_employee_count_all_booked.get(key):
            #         lst_employee_booked.append(lst_employee_count_all_booked.get(key))
            #     else:
            #         lst_employee_booked.append(0)


            lst_service_wise_employee_count = []
            lst_service_wise_status_count = []
            rst_service_wise_employee_count_sub = session.query(rst_enquiry_set.c.vchr_service, func.count(rst_enquiry_set.c.vchr_service).label('count'),rst_enquiry_set.c.user_id).group_by(rst_enquiry_set.c.vchr_service,rst_enquiry_set.c.user_id).subquery()
            rst_service_wise_employee_count = session.query(rst_service_wise_employee_count_sub.c.vchr_service,rst_service_wise_employee_count_sub.c.count,AuthUserSA.first_name.label('first_name'),AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('last_name')).join(AuthUserSA,AuthUserSA.id == rst_service_wise_employee_count_sub.c.user_id)
            dct_service_count_data={}
            for service in rst_service_wise_employee_count.all():
                if service.vchr_service not in dct_service_count_data.keys():
                    dct_service_count_data[service.vchr_service] = {}
                dct_service_count_data[service.vchr_service][service.first_name+' '+service.last_name] = service.count

            for key in dct_service_count_data.keys():
                lst_service_wise_employee_count.append({key:dct_service_count_data[key]})

            rst_service_wise_status_count = session.query(rst_enquiry_set.c.vchr_service,rst_enquiry_set.c.status.label('status'), func.count(rst_enquiry_set.c.status).label('count')).group_by(rst_enquiry_set.c.vchr_service,rst_enquiry_set.c.status)
            dct_status_count_data = {}
            for service in rst_service_wise_status_count.all():
                if service.vchr_service not in dct_status_count_data.keys():
                    dct_status_count_data[service.vchr_service] = {}
                dct_status_count_data[service.vchr_service][service.status] = service.count
            for key in dct_status_count_data.keys():
                lst_service_wise_status_count.append({key:dct_status_count_data[key]})

            # lst_service_wise_employee_count = []
            # lst_service_wise_status_count = []
            # for service in lst_service_count_all.keys():
            #     service_count_data = Counter((tok['staff_first_name']+' '+tok['staff_last_name']).title() for tok in lst_enquiry_data if tok.get('vchr_service') == service)
            #     lst_service_wise_employee_count.append({service:service_count_data})
            #     status_count_data = Counter(tok['status'] for tok in lst_enquiry_data if tok.get('vchr_service') == service)
            #     lst_service_wise_status_count.append({service:status_count_data})
            # lst_service_wise_employee_count_booked = []
            # lst_service_wise_status_count_booked = []
            # for service_booked in lst_service_count_all_booked.keys():
            #     service_count_data_booked = Counter((tok['staff_first_name']+' '+tok['staff_last_name']).title() for tok in lst_enquiry_data_booked if tok.get('vchr_service') == service_booked)
            #     lst_service_wise_employee_count_booked.append({service_booked:service_count_data_booked})
            #
            #     status_count_data_booked = Counter(tok['status'] for tok in lst_enquiry_data_booked if tok.get('vchr_service') == service_booked)
            #     lst_service_wise_status_count_booked.append({service_booked:status_count_data_booked})
            # import pdb; pdb.set_trace()
            session.close()
            return JsonResponse({'status': 'success','dct_service_wise':dct_service_wise,'lst_service_count_all':lst_service_count_all , 'lst_employee_count_all':lst_employee_count_all ,    'lst_service_count_all':lst_service_count_all , 'lst_status_count_all':lst_status_count_all , 'lst_enquiry_data' : lst_enquiry_data,'lst_service_wise_employee_count' : lst_service_wise_employee_count , 'lst_service_wise_status_count' : lst_service_wise_status_count,'lst_enquiry_labels':lst_enquiry_labels,'lst_enquiry_all':lst_enquiry_all,'lst_enquiry_booked':lst_enquiry_booked,'lst_employee_labels':lst_employee_labels,'lst_employee_all':lst_employee_all,'lst_employee_booked':lst_employee_booked, 'user_wise':dct_user_wise })
        except Exception as e:
            session.close()
            print(str(e))
            return JsonResponse({'status': 'failed','error':str(e)})



class ServiceWiseReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            session = Session()
            lst_enquiry_data = []
            int_company = request.data['company_id']
            blnExcel = request.data.get('excel',False)
            fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
            todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
            selected_option = request.data.get('selected_service')
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)

            if ins_company[0].fk_company_type.vchr_company_type == 'TRAVEL AND TOURISM':
                rst_data = fun_travels_data(int_company)
            elif ins_company[0].fk_company_type.vchr_company_type == 'SOFTWARE':
                rst_data = fun_software_data(int_company)
            elif ins_company[0].fk_company_type.vchr_company_type == 'AUTOMOBILE':
                session = Session()
                rst_hatchback = session.query(literal("Hatchback").label("vchr_service"),HatchbackEnquirySA.vchr_enquiry_status.label('status'),HatchbackEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_sedan = session.query(literal("Sedan").label("vchr_service"),SedanEnquirySA.vchr_enquiry_status.label('status'),SedanEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_suv = session.query(literal("Suv").label("vchr_service"),SuvEnquirySA.vchr_enquiry_status.label('status'),SuvEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_data = rst_hatchback.union_all(rst_sedan,rst_suv).subquery()
            elif ins_company[0].fk_company_type.vchr_company_type == 'MOBILE':
                rst_data = session = Session()
                rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
            rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                        rst_data.c.vchr_service, CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),rst_data.c.status,\
                                        CustomerSA.cust_mobile.label('customer_mobile'),BranchSA.vchr_name.label('branch_name'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
                                        .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == int_company )\
                                        .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
                                        .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
                                        .join(BranchSA, BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)

            if request.data.get('branch'):
                branch = request.data.get('branch')
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == branch)
            if request.data.get('staff'):
                staff = request.data.get('staff')
                rst_enquiry = rst_enquiry.filter(AuthUserSA.id == staff)

            if(selected_option):
                rst_enquiry = rst_enquiry.filter(rst_data.c.vchr_service == selected_option )
            rst_enquiry = rst_enquiry.order_by(desc(EnquiryMasterSA.dat_created_at))


            lst_enquiry_data = []
            for ins_enquiry in rst_enquiry.all():
                lst_enquiry_data.append(ins_enquiry._asdict())
            if blnExcel:
                lst_excel_data = []
                for dct_data in lst_enquiry_data:
                    dct_temp = OrderedDict()
                    if not selected_option:
                        dct_temp['Service'] = dct_data.get('vchr_service')
                    dct_temp['Enquiry Date'] = str(datetime.strptime(str(dct_data.get('dat_created_at'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
                    dct_temp['Enquiry Number'] = dct_data.get('vchr_enquiry_num')
                    dct_temp['Customer Name'] = (dct_data.get('customer_first_name') + " " + dct_data.get('customer_last_name')).title()
                    dct_temp['Mobile'] = str(dct_data.get('customer_mobile'))
                    dct_temp['Staff Name'] = (dct_data.get('staff_first_name') + " " + dct_data.get('staff_last_name')).title()
                    dct_temp['Enquiry Status'] = dct_data.get('status')
                    dct_temp['Branch'] = dct_data.get('branch_name').title()
                    lst_excel_data.append(dct_temp)

                fromdate =  request.data['fromdate'][:10].split("-")
                todate =  request.data['todate'][:10].split('-')
                fromdate.reverse()
                todate.reverse()
                from_date = "-".join(fromdate)
                to_date = "-".join(todate)
                str_all = ''
                if selected_option:
                    str_all += lst_enquiry_data[0].get('vchr_service')
                else:
                    str_all += 'all'

                if request.data.get('branch'):
                    str_all += '+branch'
                if request.data.get('staff'):
                    str_all += '+staff'
                if not selected_option:
                    lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Service'])
                    response = export_excel('service',str_all,from_date,to_date,lst_excel_data)
                else:
                    lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Enquiry Number'])
                    response = export_excel('service',str_all,from_date,to_date,lst_excel_data)
                if response != False:
                    session.close()
                    return Response({'status': 'success', 'path':response})
                else:
                    session.close()
                    return Response({'status': 'failure'})
            else:
                session.close()
                return JsonResponse({'status': 'success', 'lst_service_count': lst_user_count , 'lst_service_labels': lst_user_labels , 'lst_status_labels': lst_status_labels  , 'lst_status_count': lst_status_count , 'lst_enquiry_data' : lst_enquiry_data   })
        except Exception as e:
            session.close()
            # print(str(e))
            JsonResponse({'status': 'failed'})


# def get_perm_data_orm(rst_data,user):
#     import pdb; pdb.set_trace()
#     int_branch_id = user.usermodel.fk_branch_id
#     int_group_id = user.usermodel.fk_group_id
#     ins_group_name = user.usermodel.fk_group.vchr_name
#     ins_category = SubCategory.objects.get(vchr_sub_category_name = 'ASSIGN').pk_bint_id
#     ins_permission=GroupPermissions.objects.filter(fk_groups_id = int_group_id,fk_category_items__fk_sub_category_id = ins_category).values('bln_add')
#     if ins_group_name in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
#         rst_data = rst_data.filter(fk_user_id__fk_branch_id = int_branch_id)
#     elif ins_group_name=='Territory Manager':
#         ins_territory=Branch.objects.get(pk_bint_id=int_branch_id).fk_territory_id
#         ins_branch=Branch.objects.filter(fk_territory_id=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(fk_user_id__fk_branch_id__in=ins_branch)
#     elif ins_group_name=='Zone Manager':
#         ins_zone=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id')
#         ins_territory=Territory.objects.filter(fk_zone_id=ins_zone).values_list('pk_bint_id',flat=True)
#         ins_branch=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(fk_user_id__fk_branch_id__in = ins_branch)
#     elif ins_group_name=='Country Manager':
#         ins_country=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id__fk_country_id')
#         ins_zone=Zone.objects.filter(fk_country_id=ins_country).values_list('pk_bint_id',flat=True)
#         ins_territory=Territory.objects.filter(fk_zone_id__in=ins_zone).values_list('pk_bint_id',flat=True)
#         ins_branch=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(fk_user_id__fk_branch_id__in = ins_branch)
#     return rst_data

class StaffRatingReport(APIView):
    permission_classes = [IsAuthenticated]
    # def get(self,request):
    #     try:
    #         session = Session()
    #         lst_branch = []
    #         rst_branch = get_branch_on_permission(request.user)
    #         ins_branch = Branch.objects.filter(Q(vchr_code__icontains=str_search_term)\
    #         | Q(vchr_name__icontains=str_search_term) ,fk_company = user[0].fk_company,pk_bint_id__in = rst_branch).values('pk_bint_id','vchr_name','vchr_code')
    #         if ins_branch:
    #             for itr_item in ins_branch:
    #                 dct_branch = {}
    #                 dct_branch['code'] = itr_item['vchr_code'].upper()
    #                 dct_branch['name'] = itr_item['vchr_name'].title()
    #                 dct_branch['id'] = itr_item['pk_bint_id']
    #                 lst_branch.append(dct_branch)
    #             return Response({'status':'success','data':lst_branch})
    #         return Response({'status':'empty'})
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'line no':str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
    #         return Response({'result':'failed','reason':e})
    #     finally:
    #         session.close()

    def post(self,request):
        try:
            session = Session()
            user_id = request.data.get('user_id',-1)
            blnExcel = request.data.get('excel',True)
            if  user_id == -1:
                return JsonResponse({'status':'failed','data':'this usr not registered'})
            user_id = UserModel.objects.get(id = int(request.data.get('user_id'))).id
            company_id = UserModel.objects.get(id = user_id).fk_company_id

            dat_from = request.data.get('date_from')
            dat_to = request.data.get('date_to')
            staff = request.data.get('staff')
            int_branch_id = request.data.get('branch_id')
            # LG
            rst_branch = get_branch_on_permission(request.user)
            if rst_branch:
                int_branch_id = set([int_branch_id]) & set(rst_branch)
            else:
                int_branch_id = []
                return JsonResponse({'status':'failed','data':"Data Not Available For This User"})
            str_filter = ''


            # select 
            #     em.vchr_enquiry_num,
            #     sr.pk_bint_id,
            #     b.vchr_name,
            #     sr.dat_created,
            #     au.first_name || ' ' ||  au.last_name as user_name,
            #     cust.cust_fname || ' ' || cust.cust_lname,
            #     cust.cust_mobile,
            #     sr.dbl_rating,
            #     (select 
            #         array_agg(distinct(p.vchr_product_name))
            #     from item_enquiry ie
            #         join products p on p.id = ie.fk_product_id
            #     where fk_enquiry_master_id = sr.fk_enquiry_master_id) as products
            # from staff_rating sr
            #     join enquiry_master em on em.pk_bint_id = sr.fk_enquiry_master_id
            #     join branch b on b.pk_bint_id = em.fk_branch_id
            #     join auth_user au on au.id = sr.fk_user_id
            #     join customer_app_customermodel cust on cust.id = sr.fk_customer_id
            # order by sr.dat_created;
            if not staff and not int_branch_id:
                str_filter += """ and b.pk_bint_id in ("""+str(rst_branch)[1:-1]+""")"""

                # insReportData = StaffRating.objects.filter(dat_created__range = (dat_from,dat_to) , fk_user_id__fk_company = company_id).annotate(vchr_staff_impression = F('vchr_staff_attitude'), vchr_cust_satisfied = F('vchr_store_ambience'),vchr_remarks = F('vchr_comments')).values('fk_user_id__first_name','fk_user_id__last_name', 'fk_customer__cust_fname', 'fk_customer__cust_lname', 'fk_customer__cust_mobile', 'dbl_rating' , 'dat_created' , 'vchr_remarks','fk_enquiry_master__fk_branch_id__vchr_name', 'vchr_staff_impression' , 'vchr_cust_satisfied', 'fk_enquiry_master__vchr_enquiry_num','vchr_staff_knowledge','vchr_staff_attitude','vchr_know_about','vchr_recommended')

            elif not staff and int_branch_id:

                str_filter += """ and b.pk_bint_id in ("""+str(int_branch_id)[1:-1]+""")"""

                # insReportData = StaffRating.objects.filter(dat_created__range = (dat_from,dat_to) ,
                #                 fk_user_id__fk_company = company_id, fk_user_id__fk_branch = int(int_branch_id))\
                #                 .annotate(vchr_staff_impression = F('vchr_staff_attitude'), vchr_cust_satisfied = F('vchr_store_ambience'),vchr_remarks = F('vchr_comments')).values('fk_user_id__first_name','fk_user_id__last_name', 'fk_customer__cust_fname',
                #                 'fk_customer__cust_lname', 'fk_customer__cust_mobile', 'dbl_rating' , 'dat_created' , 'vchr_remarks','fk_enquiry_master__fk_branch_id__vchr_name',
                #                  'vchr_staff_impression' , 'vchr_cust_satisfied', 'fk_enquiry_master__vchr_enquiry_num','vchr_staff_knowledge','vchr_staff_attitude','vchr_know_about','vchr_recommended')

            elif staff and int_branch_id:

                str_filter += """ and b.pk_bint_id  in ("""+str(int_branch_id)[1:-1]+""") and au.id = """+str(staff)

                # insReportData = StaffRating.objects.filter(dat_created__range = (dat_from,dat_to) ,
                #                 fk_user_id__fk_company = company_id, fk_user_id__fk_branch = int(int_branch_id),fk_user_id = staff)\
                #                 .annotate(vchr_staff_impression = F('vchr_staff_attitude'), vchr_cust_satisfied = F('vchr_store_ambience'),vchr_remarks = F('vchr_comments')).values('fk_user_id__first_name','fk_user_id__last_name', 'fk_customer__cust_fname',
                #                 'fk_customer__cust_lname', 'fk_customer__cust_mobile', 'dbl_rating' , 'dat_created' , 'vchr_remarks','fk_enquiry_master__fk_branch_id__vchr_name',
                #                  'vchr_staff_impression' , 'vchr_cust_satisfied', 'fk_enquiry_master__vchr_enquiry_num','vchr_staff_knowledge','vchr_staff_attitude','vchr_know_about','vchr_recommended')
            else:
                str_filter += """and au.id = """+str(staff)
                # insReportData = StaffRating.objects.filter(dat_created__range = (dat_from,dat_to) ,
                #                 fk_user_id__fk_company = company_id , fk_user_id = staff )\
                #                 .annotate(vchr_staff_impression = F('vchr_staff_attitude'), vchr_cust_satisfied = F('vchr_store_ambience'),vchr_remarks = F('vchr_comments')).values('fk_user_id__first_name','fk_user_id__last_name', 'fk_customer__cust_fname',
                #                 'fk_customer__cust_lname', 'fk_customer__cust_mobile', 'dbl_rating' , 'dat_created' , 'vchr_remarks','fk_enquiry_master__fk_branch_id__vchr_name',
                #                  'vchr_staff_impression' , 'vchr_cust_satisfied', 'fk_enquiry_master__vchr_enquiry_num','vchr_staff_knowledge','vchr_staff_attitude','vchr_know_about','vchr_recommended')
            insReportData = session.execute("""select 
                            array_agg(distinct(p.vchr_product_name)) as products,
                            em.vchr_enquiry_num as fk_enquiry_master__vchr_enquiry_num,
                            b.vchr_name as fk_enquiry_master__fk_branch_id__vchr_name,
                            sr.dat_created,
                            au.first_name as fk_user_id__first_name,
                            au.last_name as fk_user_id__last_name,
                            cust.cust_fname as fk_customer__cust_fname,
                            cust.cust_lname as fk_customer__cust_lname,
                            cust.cust_mobile as fk_customer__cust_mobile,
                            sr.dbl_rating,
                            sr.vchr_staff_attitude,
                            sr.vchr_comments,
                            sr.vchr_store_ambience,
                            sr.vchr_staff_knowledge,
                            sr.vchr_know_about,
                            sr.vchr_recommended

                        from item_enquiry ie
                            join staff_rating sr on ie.fk_enquiry_master_id = sr.fk_enquiry_master_id
                            join enquiry_master em on em.pk_bint_id = sr.fk_enquiry_master_id
                            join branch b on b.pk_bint_id = em.fk_branch_id
                            join auth_user au on au.id = sr.fk_user_id
                            join customer_app_customermodel cust on cust.id = sr.fk_customer_id
                            join products p on p.id = ie.fk_product_id
                            join user_app_usermodel usr on usr.user_ptr_id = au.id
                        where sr.dat_created::date between '"""+dat_from+"""' and '"""+dat_to+"""' 
                            and usr.fk_company_id = """+str(company_id)+""" """+str_filter+""" 
                            
                        group by em.vchr_enquiry_num,sr.pk_bint_id,b.vchr_name,sr.dat_created,au.first_name,au.last_name,cust.cust_fname,cust.cust_lname,cust.cust_mobile,sr.dbl_rating
                        order by sr.dat_created""").fetchall()
            lst_data = []
            for data in insReportData:
                dct_data = {}
                dct_data['products'] = data['products']
                dct_data['fk_enquiry_master__vchr_enquiry_num'] = data['fk_enquiry_master__vchr_enquiry_num']
                dct_data['fk_enquiry_master__fk_branch_id__vchr_name'] = data['fk_enquiry_master__fk_branch_id__vchr_name']
                dct_data['dat_created'] = data['dat_created']
                dct_data['fk_user_id__first_name'] = data['fk_user_id__first_name']
                dct_data['fk_user_id__last_name'] = data['fk_user_id__last_name']
                dct_data['fk_customer__cust_fname'] = data['fk_customer__cust_fname']
                dct_data['fk_customer__cust_lname'] = data['fk_customer__cust_lname']
                dct_data['fk_customer__cust_mobile'] = data['fk_customer__cust_mobile']
                dct_data['dbl_rating'] = data['dbl_rating']
                dct_data['vchr_remarks'] = data['vchr_comments']
                dct_data['vchr_staff_impression'] = data['vchr_staff_attitude']
                dct_data['vchr_cust_satisfied'] = data['vchr_store_ambience']
                dct_data['vchr_staff_knowledge'] = data['vchr_staff_knowledge']
                dct_data['vchr_staff_attitude'] = data['vchr_staff_attitude']
                dct_data['vchr_know_about'] = data['vchr_know_about']
                dct_data['vchr_recommended'] = data['vchr_recommended']


                lst_data.append(dct_data)

            if request.data.get('branch_id'):
                ins_branchs = Branch.objects.filter(pk_bint_id = request.data.get('branch_id')).values('vchr_name')
                str_branch_name = ins_branchs[0]['vchr_name']
            else:
                str_branch_name = 'All'

            if request.data.get('staff'):
                ins_staff = User.objects.filter(id = request.data.get('staff')).values('first_name','last_name')
                str_staff_name = ins_staff[0]['first_name'] + ins_staff[0]['last_name']
            else:
                str_staff_name = 'All'
            # insReportData = get_perm_data_orm(lst_data,request.user)
            insReportData = lst_data
            if blnExcel:
                lst_excel_data = []
                for dct_data in insReportData:
                    dct_temp = OrderedDict()
                    dct_temp['Branch Name'] = dct_data.get('fk_enquiry_master__fk_branch_id__vchr_name').title()
                    dct_temp['Staff Name'] = (dct_data.get('fk_user_id__first_name') + " " + dct_data.get('fk_user_id__last_name')).title()
                    dct_temp['Date'] = str(datetime.strptime(str(dct_data.get('dat_created'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
                    dct_temp['Rating'] = str(dct_data.get('dbl_rating')).title()
                    dct_temp['Enquiry Number'] = str(dct_data.get('fk_enquiry_master__vchr_enquiry_num')).upper()
                    # import pdb; pdb.set_trace()
                    dct_temp['Products'] = ','.join(dct_data.get('products'))
                    dct_temp['Customer'] = (dct_data.get('fk_customer__cust_fname') + " " + dct_data.get('fk_customer__cust_lname')).title()
                    dct_temp['Customer Mobile'] = str(dct_data.get('fk_customer__cust_mobile'))
                    """ Uncomment this section to create remarks string
                    remark_data = 'Staff behavior is ' + dct_data.get('vchr_staff_attitude')+ ', Customer is '
                    if dct_data.get('vchr_store_ambience') == 'no':
                         remark_data = remark_data + 'not '
                    remark_data = remark_data+'satisfied. '
                    if dct_data.get('vchr_remarks'):
                        remark_data = remark_data + str(dct_data.get('vchr_remarks')[:1]).upper()+str(dct_data.get('vchr_remarks')[1:]).lower() +'.'
                    dct_temp['Remarks'] = remark_data"""
                    dct_temp['HOW DID YOU CAME TO KNOW ABOUT MYG'] = dct_data.get('vchr_know_about')
                    dct_temp['STORE AMBIENCE'] = dct_data.get('vchr_cust_satisfied')
                    dct_temp['STAFF BEHAVIOUR'] = dct_data.get('vchr_staff_impression')
                    dct_temp['STAFF KNOWELDGE ABOUT PRODUCT'] = dct_data.get('vchr_staff_knowledge')
                    dct_temp['WOULD YOU REFER YOUR FRIENDS '] = dct_data.get('vchr_recommended')
                    #import pdb;pdb.set_trace()
                    if len(dct_data.get('vchr_remarks','')) > 0:
                        dct_temp['Remarks'] = dct_data['vchr_remarks']
                    else:
                        dct_temp['Remarks'] = '--'
                    lst_excel_data.append(dct_temp)
                from_date = datetime.strptime(request.data.get('date_from'),'%Y-%m-%d').strftime('%d-%m-%Y')
                to_date = datetime.strptime(request.data.get('date_to'),'%Y-%m-%d').strftime('%d-%m-%Y')
                lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Date'])
                response = export_excel('Customer Feedback',str_branch_name+','+str_staff_name,from_date,to_date,lst_excel_data)

                if response != False:
                    return JsonResponse({'status': 'success', 'path':response })
                else:
                    return JsonResponse({'status': 'failure'})
            else:
                return JsonResponse({'status':'success','data':insReportData})
        except Exception as msg:
            # print(msg)
            return JsonResponse({'status':'failed','data':str(msg)})


# class BranchBasedOnPermission(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             session = Session()
#             lst_branch = []
#             rst_branch = get_branch_on_permission(request.user)
#                 ins_branch = Branch.objects.filter(Q(vchr_code__icontains=str_search_term)\
#                 | Q(vchr_name__icontains=str_search_term) ,fk_company = user[0].fk_company,pk_bint_id__in = rst_branch).values('pk_bint_id','vchr_name','vchr_code')
#                 if ins_branch:
#                     for itr_item in ins_branch:
#                         dct_branch = {}
#                         dct_branch['code'] = itr_item['vchr_code'].upper()
#                         dct_branch['name'] = itr_item['vchr_name'].title()
#                         dct_branch['id'] = itr_item['pk_bint_id']
#                         lst_branch.append(dct_branch)
#                 return Response({'status':'success','data':lst_branch})
#             return Response({'status':'empty'})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'line no':str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'result':'failed','reason':e})
#         finally:
#             session.close()

class ServiceReportMobile(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            session = Session()
            lst_enquiry_data = []
            # import pdb;pdb.set_trace()
            # request.data['date_from'] = "2021-01-12"
            int_company = request.data['company_id']
            if request.data.get('show_type'):
                str_show_type = 'total_amount'
            else:
                str_show_type = 'int_quantity'
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)

            fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
            todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
            # todate = todate + timedelta(days = 1)
            dct_data={}

            # materialized views
            engine = get_engine()
            conn = engine.connect()

            lst_mv_view = []
            lst_mv_view = request.data.get('lst_mv')

            if not lst_mv_view:
                session.close()
                return JsonResponse({'status':'failed', 'reason':'No view list found'})
            query_set = ''
            if len(lst_mv_view) == 1:

                if request.data['type'].upper() == 'ENQUIRY':

                    query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, sum(int_quantity) as qty,sum(total_amount) as value,vchr_product_name as vchr_service, concat(branch_code,'-',staff_first_name, ' ',staff_last_name) as vchr_staff_full_name, user_id as fk_assigned,branch_code, staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id,branch_code, product_id, brand_id"
                else:

                    query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, sum(int_quantity) as qty,sum(total_amount) as value,vchr_product_name as vchr_service, concat(branch_code,'-',staff_first_name, ' ',staff_last_name) as vchr_staff_full_name,user_id as fk_assigned,branch_code,staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id,branch_code, product_id, brand_id"

            else:

                if request.data['type'].upper() == 'ENQUIRY':

                    for data in lst_mv_view:
                        query_set += "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(int_quantity) as qty,sum(total_amount) as value,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned, branch_id, product_id, brand_id,branch_code,staff_first_name, staff_last_name from "+data+" {} group by  vchr_enquiry_status , vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned, branch_id, product_id, brand_id,staff_first_name,branch_code, staff_last_name union "
                else:

                     for data in lst_mv_view:

                        query_set +="select vchr_enquiry_status,vchr_product_name as vchr_service,concat(branch_code,'-',staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(int_quantity) as qty,sum(total_amount) as value,user_id as fk_assigned, vchr_brand_name, vchr_item_name,promoter,is_resigned,branch_id, product_id, brand_id,branch_code,staff_first_name, staff_last_name from "+data+" {} group by vchr_enquiry_status, vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name,branch_code, staff_last_name union "

                query = query_set.rsplit(' ', 2)[0]

            """ data wise filtering """
            str_filter_data = "where dat_enquiry :: date BETWEEN '"+request.data['date_from']+"' AND '"+request.data['date_to']+"' AND int_company_id = "+int_company+""


            """Permission wise filter for data"""
            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.userdetails.fk_branch_id)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            else:
                session.close()
                return Response({'status':'failed','reason':'No data'})

            if request.data.get('branch'):
                branch = request.data.get('branch')

                str_filter_data += " AND branch_id = "+str(branch)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == branch)
            if request.data.get('staff'):
                staff = request.data.get('staff')

                str_filter_data += " AND user_id = "+str(staff)+""
                # rst_enquiry = rst_enquiry.filter(AuthUserSA.id == staff)
            if request.data.get('product'):

                str_filter_data += " AND product_id = "+str(request.data.get('product'))+""
                # rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_product_id == request.data.get('product'))
            if request.data.get('brand'):

                str_filter_data += " AND brand_id = "+str(request.data.get('brand'))+""
                # rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_brand_id == request.data.get('brand'))

            # import pdb; pdb.set_trace()
            #for getting user corresponding products
            lst_user_id =[]
            lst_user_id.append(request.user.id)
            lst_user_products = get_user_products(lst_user_id)
            if lst_user_products:
                str_filter_data += " AND product_id in ("+str(lst_user_products)[1:-1]+")"


            if len(lst_mv_view) == 1:
                query = query.format(str_filter_data)
            else:
                query = query.format(str_filter_data,str_filter_data)
            rst_enquiry = conn.execute(query).fetchall()
            if not rst_enquiry:
                session.close()
                return Response({'status':'failed','reason':'No Data'})

            #structuring data rst enquiry
            if request.data['type'].upper() == 'ENQUIRY':
                dct_data = structure_data_for_report_old(request,rst_enquiry)
            else:
                dct_data = structure_data_for_report_new(request,rst_enquiry)
            # self.structure_data_for_report = rst_enquiry
            session.close()
            return Response({'status':1,'data':dct_data})
        except Exception as msg:
                session.close()
                return JsonResponse({'status':'failed','data':str(msg)})


def key_sort_sale(tup):
    key,data = tup
    return -data['Sale']
def key_sort(tup):
    key,data = tup
    return -data['Enquiry']

def paginate_data(request,dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    if request.data.get('type') == 'Sale':
        sorted_dct_data = sorted(dct_data.items(),key= key_sort_sale)
    else:
        sorted_dct_data = sorted(dct_data.items(),key= key_sort)

    dct_data = OrderedDict(sorted_dct_data)
    for key in dct_data:
        if int_count not in dct_paged:
            dct_paged[int_count]={}
            dct_paged[int_count][key]=dct_data[key]
        elif len(dct_paged[int_count]) < int_page_legth:
            dct_paged[int_count][key]= dct_data[key]
        else:
            int_count += 1
            dct_paged[int_count] ={}
            dct_paged[int_count][key] = dct_data[key]
    return dct_paged

class ServiceReportMobileTable(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            # import pdb; pdb.set_trace()

            session = Session()
            lst_enquiry_data = []
            int_company = request.data['company_id']
            # int_company = 1
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)

            fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
            todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
            # todate = todate + timedelta(days = 1)
            # todate = todate + timedelta(days = 1)
            # fromdate = "2018-10-08"
            # todate = "2018-11-10"

            dct_data={}
            session=Session()

            rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status,
                                ProductSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
                                AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),(CustomerSA.cust_fname+" "+CustomerSA.cust_lname).label('customer_full_name'),
                                AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
                                AuthUserSA.first_name.label('staff_first_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
                                UserSA.fk_brand_id,UserSA.dat_resignation_applied,
                                # case([(UserSA.fk_brand_id > 0,literal_column("'promoter'"))],
                                #     else_=literal_column("'not promoter'")).label('is_promoter'),
                                case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
                                    else_=literal_column("'not resigned'")).label("is_resigned"))\
                                .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
                                        cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
                                        EnquiryMasterSA.fk_company_id == 1 ,
                                        EnquiryMasterSA.chr_doc_status == 'N')\
                                .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
                                .join(ProductSA,ProductSA.id == ItemEnquirySA.fk_product_id)\
                                .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
                                .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)
            # """Permission wise filter for data"""
            # # rst_enquiry = get_perm_data_orm(rst_enquiry,request.user)
            # if request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})

            """Permission wise filter for data"""
            # if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
            #     pass
            # elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.usermodel.int_area_id)
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})


            if request.data.get('branch'):
                branch = request.data.get('branch')
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == branch)
            if request.data.get('staff'):
                staff = request.data.get('staff')
                rst_enquiry = rst_enquiry.filter(AuthUserSA.id == staff)
            if request.data.get('product'):
                rst_enquiry = rst_enquiry.filter(rst_data.c.vchr_service == request.data.get('product'))
            if request.data.get('brand'):
                rst_enquiry = rst_enquiry.filter(rst_data.c.brand_id == request.data.get('brand'))


            if not rst_enquiry.all():
                session.close()
                return Response({'status':'failed','reason':'No data'})
            else:
                session.close()
                return Response({'status':'success','data':list(rst_enquiry.all())})
        except Exception as e:
            session.close()
            # ins_logger.logger.error(str(e))
            return Response({'status':'0','data':str(e)})



# ===================================================================================================================================================================================================================================
# ===================================================================================================================================================================================================================================
# class ServiceReportMobileExportExcel(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             session = Session()
#             lst_enquiry_data = []
#             if request.data.get('company_id'):
#                 int_company = request.data.get('company_id')
#             else:
#                 int_company = str(request.user.usermodel.fk_company_id)
#
#             if request.data.get('show_type'):
#                 str_show_type = 'total_amount'
#             else:
#                 str_show_type = 'int_quantity'
#             ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
#
#             fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#             todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#
#             dct_data={}
#             table_request = request.data['bln_table']
#             chart_request = request.data['bln_chart']
#             export_type = request.data.get('export_type')
#             enquiry_color = '#0d8ec1'
#             sale_color = '#77a7fb'
#             points =[]
#             if AdminSettings.objects.values():
#                 enquiry_color = AdminSettings.objects.filter(vchr_code='ENQUIRY_COLOUR',bln_enabled=True).values('vchr_value')
#                 sale_color = AdminSettings.objects.filter(vchr_code='SALES_COLOUR',bln_enabled=True).values('vchr_value')
#                 pie_color =  AdminSettings.objects.filter(vchr_code='PIE_CHART_COLOURS',bln_enabled=True).values('vchr_value')
#                 if enquiry_color:
#                     enquiry_color = enquiry_color[0]['vchr_value'][0]
#                 else:
#                     enquiry_color = '#0d8ec1'
#                 if sale_color:
#                     sale_color = sale_color[0]['vchr_value'][0]
#                 else:
#                     sale_color = '#77a7fb'
#                 colors = [enquiry_color,sale_color]
#                 points = [{'fill': {'color':i}} for i in pie_color[0]['vchr_value']]
#             # materialized views
#             engine = get_engine()
#             conn = engine.connect()
#
#             lst_mv_view = []
#             lst_mv_view = request.data.get('lst_mv')
#
#             if not lst_mv_view:
#                 return JsonResponse({'status':'failed', 'reason':'No view list found'})
#             query_set = ''
#             if len(lst_mv_view) == 1:
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name, user_id as fk_assigned, staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id"
#                 else:
#                     query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name,user_id as fk_assigned,staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id"
#             else:
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     for data in lst_mv_view:
#                         query_set += "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned, branch_id, product_id, brand_id,staff_first_name, staff_last_name from "+data+" {} group by  vchr_enquiry_status , vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned, branch_id, product_id, brand_id,staff_first_name, staff_last_name union "
#                 else:
#                      for data in lst_mv_view:
#                         query_set +="select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned, vchr_brand_name, vchr_item_name,promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name, staff_last_name from "+data+" {} group by vchr_enquiry_status, vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name, staff_last_name union "
#                 query = query_set.rsplit(' ', 2)[0]
#
#             """ data wise filtering """
#             str_filter_data = "where dat_enquiry :: date BETWEEN '"+request.data['date_from']+"' AND '"+request.data['date_to']+"' AND int_company_id = "+int_company+""
#
#
#             """Permission wise filter for data"""
#             if request.user.usermodel.fk_group.vchr_name.upper()=='ADMIN':
#                 pass
#             elif request.user.usermodel.fk_group.vchr_name.upper()=='BRANCH MANAGER':
#
#                 str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.usermodel.fk_branch_id)+""
#             elif request.user.usermodel.int_area_id:
#                 lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#
#                 str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"
#             else:
#                 return Response({'status':'failed','reason':'No data'})
#
#             if request.data.get('branch'):
#                 branch = request.data.get('branch')
#
#                 str_filter_data += " AND branch_id = "+str(branch)+""
#             if request.data.get('staff'):
#                 staff = request.data.get('staff')
#
#                 str_filter_data += " AND user_id = "+str(staff)+""
#             if request.data.get('product'):
#
#                 str_filter_data += " AND product_id = "+str(request.data.get('product'))+""
#             if request.data.get('brand'):
#
#                 str_filter_data += " AND brand_id = "+str(request.data.get('brand'))+""
#
#             if len(lst_mv_view) == 1:
#                 query = query.format(str_filter_data)
#             else:
#                 query = query.format(str_filter_data,str_filter_data)
#             rst_enquiry = conn.execute(query).fetchall()
#
#             # import pdb; pdb.set_trace()
#
#             dct_data={}
#             dct_data['service_all']={}
#             dct_data['brand_all']={}
#             dct_data['item_all']={}
#             dct_data['staff_all']={}
#             dct_data['status_all']={}
#             dct_data['staffs']={}
#             for ins_data in rst_enquiry:
#                 if ins_data.vchr_service not in dct_data['service_all']:
#                     dct_data['service_all'][ins_data.vchr_service]={}
#                     dct_data['service_all'][ins_data.vchr_service]['Enquiry']=ins_data.counts
#                     dct_data['service_all'][ins_data.vchr_service]['Sale']=0
#
#                     if ins_data.vchr_enquiry_status == 'INVOICED':
#                         dct_data['service_all'][ins_data.vchr_service]['Sale']=ins_data.counts
#                 else:
#                     dct_data['service_all'][ins_data.vchr_service]['Enquiry']+=ins_data.counts
#
#                     if ins_data.vchr_enquiry_status == 'INVOICED':
#                         dct_data['service_all'][ins_data.vchr_service]['Sale'] += ins_data.counts
#
#                 if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
#                     dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
#                     dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
#                     dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
#
#                 else:
#                     dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
#
#                 if ins_data.vchr_item_name.title() not in dct_data['item_all']:
#                     dct_data['item_all'][ins_data.vchr_item_name.title()]={}
#                     dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
#                     dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
#                     if ins_data.vchr_enquiry_status =='BOOKED':
#                         dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
#                 else:
#                     dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
#                 if ins_data.fk_assigned not in dct_data['staff_all']:
#                     dct_data['staffs'][ins_data.fk_assigned]=str(ins_data.staff_first_name+" "+ins_data.staff_last_name).title()
#                     dct_data['staff_all'][ins_data.fk_assigned]={}
#                     dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                     dct_data['staff_all'][ins_data.fk_assigned]['Sale']=0
#                     if ins_data.vchr_enquiry_status =='BOOKED':
#                         dct_data['staff_all'][ins_data.fk_assigned]['Sale']=ins_data.counts
#                 else:
#                     dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['staff_all'][ins_data.fk_assigned]['Sale']+=ins_data.counts
#                 if ins_data.vchr_enquiry_status not in dct_data['status_all']:
#                     dct_data['status_all'][ins_data.vchr_enquiry_status]={}
#                     dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
#                 else:
#                     dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
#
#             # import pdb; pdb.set_trace()
#
#             if request.data['type'] == 'Sale':
#                 dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
#                 dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
#                 dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
#                 dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)
#
#             elif request.data['type'] == 'Enquiry':
#                 dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
#                 dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
#                 dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
#                 dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)
# # ========================================tabledata========================================================================================================================
#             rst_enquiry_table_data = session.query(ItemEnquirySA.vchr_enquiry_status,
#                                 ProductSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
#                                 AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),(CustomerSA.cust_fname+" "+CustomerSA.cust_lname).label('customer_full_name'),
#                                 AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
#                                 AuthUserSA.first_name.label('staff_first_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
#                                 UserSA.fk_brand_id,UserSA.dat_resignation_applied,
#                                 case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
#                                     else_=literal_column("'not resigned'")).label("is_resigned"))\
#                                 .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
#                                         cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
#                                         EnquiryMasterSA.fk_company_id == 1 ,
#                                         EnquiryMasterSA.chr_doc_status == 'N')\
#                                 .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#                                 .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                                 .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#                                 .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
#                                 .join(ProductSA,ProductSA.id == ItemEnquirySA.fk_product_id)\
#                                 .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
#                                 .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)
#
#             """Permission wise filter for data"""
#             if request.user.usermodel.fk_group.vchr_name.upper()=='ADMIN':
#                 pass
#             elif request.user.usermodel.fk_group.vchr_name.upper()=='BRANCH MANAGER':
#                 rst_enquiry_table_data = rst_enquiry_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
#             elif request.user.usermodel.int_area_id:
#                 lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#                 rst_enquiry_table_data = rst_enquiry_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
#             else:
#                 return Response({'status':'failed','reason':'No data'})
#             if request.data.get('branch'):
#                 branch = request.data.get('branch')
#                 rst_enquiry_table_data = rst_enquiry_table_data.filter(EnquiryMasterSA.fk_branch_id == branch)
#             if request.data.get('staff'):
#                 staff = request.data.get('staff')
#                 rst_enquiry_table_data = rst_enquiry_table_data.filter(AuthUserSA.id == staff)
#             # if request.data.get('product'):
#             #     rst_enquiry_table_data = rst_enquiry_table_data.filter(rst_data.c.vchr_service == request.data.get('product'))
#             # if request.data.get('brand'):
#             #     rst_enquiry_table_data = rst_enquiry_table_data.filter(rst_data.c.brand_id == request.data.get('brand'))
#
#             # common header
#             filter_branch = 'Branch : All'
#             filter_staff_name = 'Staff : All'
#             date = 'Date : '+str(datetime.strftime(fromdate,"%d-%m-%Y"))+' To '+str(datetime.strftime(todate,"%d-%m-%Y"))
#             user = 'Name : '+str(request.user.first_name)+' '+str(request.user.last_name)
#             report_date = 'Report Date & Time : '+ str(datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p"))
#
#             if request.data.get('branch'):
#                 branch_name = Branch.objects.filter(pk_bint_id=branch).values('vchr_name').first()
#                 filter_branch = 'Branch : '+str(branch_name['vchr_name']).title()
#             if request.data.get('staff'):
#                 staff_name = UserModel.objects.filter(user_ptr_id=staff).values('first_name','last_name').first()
#                 filter_staff_name = 'Staff : '+str(staff_name['first_name'])+' '+str(staff_name['last_name'])
#
#
#             if table_request and not chart_request :
#                 if not rst_enquiry_table_data.all():
#                     return Response({'status':'failed','reason':'No data'})
#                 else:
#                 # ============================================================= Table Data in Excel=================================================================================================
#                     all_data = {}
#                     lst_title = ['Date','ENQ No','Staff','Product','Customer','Brand','Item','Staff']
#                     dict_all = rst_enquiry_table_data.all()
#                     lst_all = list(zip(*dict_all))
#                     all_data['Date'] = list(map(lambda x:x.strftime('%d-%m-%y'),lst_all[3]))
#                     all_data['ENQ No'] = lst_all[4]
#                     all_data['Staff'] = lst_all[2]
#                     all_data['Customer'] = lst_all[6]
#                     all_data['Product'] = lst_all[1]
#                     all_data['Brand'] = lst_all[10]
#                     all_data['Item'] = lst_all[11]
#                     all_data['Status'] = lst_all[0]
#                     # import pdb; pdb.set_trace()
#
#                     df = pd.DataFrame(all_data ,index = list(range(1,len(all_data['Item'])+1)) )
#
#                     # Create a Pandas Excel writer using XlsxWriter as the engine.
#                     # file_name = str(datetime.now())
#                     # excel_file = settings.MEDIA_ROOT+'/product_table_data'+file_name+'.xlsx'
#                     excel_file = settings.MEDIA_ROOT+'/report.xlsx'
#                     sheet_name1 = 'Sheet1'
#                     writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
#                     df.to_excel(writer, sheet_name=sheet_name1,startrow=6, startcol=0)
#                     workbook = writer.book
#                     worksheet = writer.sheets[sheet_name1]
#                     merge_format1 = workbook.add_format({
#                         'bold': 20,
#                         'border': 1,
#                         'align': 'center',
#                         'valign': 'vcenter',
#                         'font_size':23
#                         })
#                     # filter_branch = 'Branch : All'
#                     # filter_staff_name = 'Staff : All'
#                     # date = 'Date : '+str(datetime.strftime(fromdate,"%d-%m-%Y"))+' To '+str(datetime.strftime(todate,"%d-%m-%Y"))
#                     # user = 'Name : '+str(request.user.first_name)+' '+str(request.user.last_name)
#                     # report_date = 'Report Date & Time : '+ str(datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p"))
#                     #
#                     # if request.data.get('branch'):
#                     #     branch_name = Branch.objects.filter(pk_bint_id=branch).values('vchr_name').first()
#                     #     filter_branch = 'Branch : '+str(branch_name['vchr_name'])
#                     # if request.data.get('staff'):
#                     #     staff_name = UserModel.objects.filter(user_ptr_id=staff).values('first_name','last_name').first()
#                     #     filter_staff_name = 'Staff : '+str(staff_name['first_name'])+' '+str(staff_name['last_name'])
#                     worksheet.merge_range('A1+:I2', ' Product Report ', merge_format1)
#                     worksheet.merge_range('A3+:E3',date)
#                     worksheet.merge_range('A4+:E4',user)
#                     worksheet.merge_range('A5+:E5',report_date)
#                     worksheet.merge_range('G3+:I3',filter_branch)
#                     worksheet.merge_range('G4+:I4',filter_staff_name)
#
#
#                     for i,width in enumerate(get_col_widths(df)):
#                         worksheet.set_column(i, i, width)
#
#                     worksheet.protect()
#                     writer.save()
# # ========================================tabledata========================================================================================================================
#             if chart_request and not table_request:
#                 service_data = {}
#                 brand_data = {}
#                 item_data = {}
#                 staff_data = {}
#                 status_data = {}
#                 all_data = {}
#
#                 dict_service = dct_data['service_all'][1]
#                 dict_brand = dct_data['brand_all'][1]
#                 dict_item = dct_data['item_all'][1]
#                 dict_staff = dct_data['staff_all'][1]
#                 dict_status = dct_data['status_all']
#
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     lst_types = ['Enquiry']
#
#                     service_data['#Name'] = [x.title() for x in dict_service.keys()]
#                     service_data['Enquiry']=[int(i['Enquiry']) for i in dict_service.values()]
#
#                     brand_data['#Name']= [x.title() for x in dict_brand.keys()]
#                     brand_data['Enquiry']=[int(i['Enquiry']) for i in dict_brand.values()]
#
#                     item_data['#Name']= [x.title() for x in dict_item.keys()]
#                     item_data['Enquiry']=[int(i['Enquiry']) for i in dict_item.values()]
#
#                     staff_data['#Name']= [x.title() for x in [dct_data['staffs'][i] for i in dict_staff.keys()]]
#                     staff_data['Enquiry']=[int(i['Enquiry']) for i in dict_staff.values()]
#
#                     status_data['#Name']=[x.title() for x in dict_status.keys()]
#                     status_data['Enquiry']=[int(i['Enquiry']) for i in dict_status.values()]
#                 else:
#
#                     lst_types = ['Enquiry','Sales']
#                     service_data['#Name'] = [x.title() for x in dict_service.keys()]
#                     service_data['Enquiry']=[int(i['Enquiry']) for i in dict_service.values()]
#                     service_data['Sale']=[int(i['Sale']) for i in dict_service.values()]
#
#                     brand_data['#Name']= [x.title() for x in dict_brand.keys()]
#                     brand_data['Enquiry']=[int(i['Enquiry']) for i in dict_brand.values()]
#                     brand_data['Sale']=[int(i['Sale']) for i in dict_brand.values()]
#
#                     item_data['#Name']= [x.title() for x in dict_item.keys()]
#                     item_data['Enquiry']=[int(i['Enquiry']) for i in dict_item.values()]
#                     item_data['Sale']=[int(i['Sale']) for i in dict_item.values()]
#
#                     staff_data['#Name']= [x.title() for x in [dct_data['staffs'][i] for i in dict_staff.keys()]]
#                     staff_data['Enquiry']=[int(i['Enquiry']) for i in dict_staff.values()]
#                     staff_data['Sale']= [int(i['Sale']) for i in dict_staff.values()]
#
#                     status_data['#Name']=[x.title() for x in dict_status.keys()]
#                     status_data['Enquiry']=[int(i['Enquiry']) for i in dict_status.values()]
#                     status_data['Sale']=[int(i['Sale']) for i in dict_status.values()]
#
#                 df1 = pd.DataFrame(service_data, index = [i for i in range(1,len(service_data['Enquiry'])+1)])
#                 df2 = pd.DataFrame(brand_data, index = [i for i in range(1,len(brand_data['Enquiry'])+1)])
#                 df3 = pd.DataFrame(item_data, index = [i for i in range(1,len(item_data['Enquiry'])+1)])
#                 df4 = pd.DataFrame(staff_data, index = [i for i in range(1,len(staff_data['Enquiry'])+1)])
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     df5 = pd.DataFrame(status_data, index = [i for i in range(1,len(status_data['Enquiry'])+1)])
#
#                 # Create a Pandas Excel writer using XlsxWriter as the engine.
#                 excel_file = settings.MEDIA_ROOT+'/report.xlsx'
#                 sheet_name1 = 'Sheet1'
#                 sheet_name2 = 'Sheet2'
#
#                 writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
#                 df1.to_excel(writer,sheet_name=sheet_name1,startrow=7, startcol=9)
#                 df2.to_excel(writer,sheet_name=sheet_name1,startrow=29, startcol=9)
#                 df3.to_excel(writer,sheet_name=sheet_name1,startrow=51, startcol=9)
#                 df4.to_excel(writer,sheet_name=sheet_name1,startrow=73, startcol=9)
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     df5.to_excel(writer,sheet_name=sheet_name1,startrow=95, startcol=9)
#
#                 # Access the XlsxWriter workbook and worksheet objects from the dataframe.
#                 workbook = writer.book
#                 worksheet1 = writer.sheets[sheet_name1]
#                 cell_format = workbook.add_format({'bold':True,'align': 'center'})
#
#
#                 merge_format = workbook.add_format({
#                 'bold': 4,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'font_size':17
#                 })
#
#                 merge_format1 = workbook.add_format({
#                 'bold': 20,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'font_size':23
#                 })
#
#                 worksheet1.write('J8','No.',cell_format)
#                 worksheet1.write('K8','Service',cell_format)
#                 worksheet1.write('J30','No.',cell_format)
#                 worksheet1.write('K30','Brand Name',cell_format)
#                 worksheet1.write('J52','No.',cell_format)
#                 worksheet1.write('K52','Item Name',cell_format)
#                 worksheet1.write('J74','No.',cell_format)
#                 worksheet1.write('K74','Staff Name',cell_format)
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     worksheet1.write('J96','No.',cell_format)
#                     worksheet1.write('K96','Status',cell_format)
#                     worksheet1.merge_range('J95+:M95', 'Status Wise ', merge_format)
#
#
#                 worksheet1.merge_range('A1+:M2', ' Product Report ', merge_format1)
#                 worksheet1.merge_range('A3+:E3',date)
#                 worksheet1.merge_range('A4+:E4',user)
#                 worksheet1.merge_range('K3+:M3',filter_branch)
#                 worksheet1.merge_range('K4+:M4',filter_staff_name)
#                 worksheet1.merge_range('A5+:E5',report_date)
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     worksheet1.merge_range('A6+:I112','')
#                 else:
#                     worksheet1.merge_range('A6+:I90','')
#
#
#                 # =================================chart1===================================
#                 # worksheet1.merge_range('J7+:M7', 'Service Wise ', merge_format)
#                 # Create a chart object.
#                 chart= workbook.add_chart({'type': 'column'})
#                 chart_one = workbook.add_chart({'type': 'column'})
#
#                 # chart chart_one
#                 for col_num in range(1, len(lst_types) + 1):
#                     chart_one.add_series({
#                     'name':       ['Sheet1', 7 ,10+col_num],
#                     'categories': ['Sheet1', 8, 9 ,len(dict_service.keys())+7, 9],
#                     'values':     ['Sheet1', 8,10+col_num, len(dict_service.keys())+7, 10+col_num],
#                     'fill':       {'color':  colors[col_num - 1]},
#                     'gap': 300,
#                     })
#
#                 # Add a chart title and some axis labels.
#                 chart_one.set_size({'width':550, 'height': 360})
#                 chart_one.set_title ({'name': 'Service Wise'})
#
#                 # Set an Excel chart style.
#                 chart_one.set_style(11)
#                 # Configure the chart axes.
#                 chart_one.set_y_axis({
#                 'major_gridlines': {'visible': True}
#                 })
#                 # Insert the chart into the worksheet.
#                 worksheet1.insert_chart('A6', chart_one)
#
#                 # ======================================chart2====================================================
#                 # worksheet1.merge_range('J29+:M29', 'Brand Wise ', merge_format)
#                 chart_two= workbook.add_chart({'type': 'column'})
#
#                 for col_num in range(1, len(lst_types) + 1):
#                     chart_two.add_series({
#                     'name':       ['Sheet1', 29, 10+col_num],
#                     'categories': ['Sheet1', 30, 9,len(dict_brand.keys())+29,9],
#                     'values':     ['Sheet1', 30, 10+col_num,len(dict_brand.keys())+29, 10+col_num],
#                     'fill':       {'color':  colors[col_num - 1]},
#                     'gap': 300,
#                     })
#
#                 chart_two.set_size({'width':550, 'height': 360})
#                 chart_two.set_title ({'name': 'Brand Wise'})
#                 chart_two.set_style(11)
#                 chart_two.set_y_axis({
#                 'major_gridlines': {'visible': True}
#                 })
#                 worksheet1.insert_chart('A28', chart_two)
#                 # ======================================chart3======================================================
#                 # worksheet1.merge_range('J51+:M51', 'Item Wise ', merge_format)
#                 chart3= workbook.add_chart({'type': 'column'})
#                 chart_three= workbook.add_chart({'type': 'column'})
#                 for col_num in range(1, len(lst_types) + 1):
#                     chart_three.add_series({
#                     'name':       ['Sheet1', 51, 10+col_num],
#                     'categories': ['Sheet1', 52, 9,len(dict_item.keys())+51, 9],
#                     'values':     ['Sheet1', 52, 10+col_num,len(dict_item.keys())+51, 10+col_num],
#                     'fill':       {'color':  colors[col_num - 1]},
#                     'gap': 300,
#                     })
#                 chart_three.set_size({'width':550, 'height': 360})
#                 chart_three.set_title ({'name': 'Item Wise'})
#                 chart_three.set_style(11)
#                 chart_three.set_y_axis({
#                 'major_gridlines': {'visible': True}
#                 })
#
#                 worksheet1.insert_chart('A50', chart_three)
#                 # ======================================chart4======================================================
#
#                 if request.data['type'].upper() != 'ENQUIRY':
#                     # worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
#
#                     chart_four= workbook.add_chart({'type': 'column'})
#
#                     for col_num in range(1, len(lst_types) + 1):
#                         chart_four.add_series({
#                         'name':       ['Sheet1', 73, 10+col_num],
#                         'categories': ['Sheet1', 74, 9,len(dict_staff.keys())+73, 9],
#                         'values':     ['Sheet1', 74, 10+col_num,len(dict_staff.keys())+73, 10+col_num],
#                         'fill':       {'color':  colors[col_num - 1]},
#                         'gap': 300,
#                         })
#
#                     chart_four.set_size({'width':550, 'height': 360})
#                     chart_four.set_title ({'name': 'staff Wise'})
#                     chart_four.set_style(11)
#                     chart_four.set_y_axis({
#                     'major_gridlines': {'visible': True}
#                     })
#                     worksheet1.insert_chart('A72', chart_four)
#                 else:
#                     # worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
#
#                     chart_four= workbook.add_chart({'type': 'pie'})
#
#                     chart_four.add_series({
#                     # 'name':       ['Sheet1', 73, 9],
#                     'categories': ['Sheet1', 74, 9,len(dict_staff.keys())+73, 9],
#                     'values':     ['Sheet1', 74, 10+col_num ,len(dict_staff.keys())+73,10+col_num],
#                     'points': points,
#                     # 'points': [
#                     #             {'fill': {'color': '#5ABA10'}},
#                     #             {'fill': {'color': '#FE110E'}},
#                     #             {'fill': {'color': '#CA5C05'}},
#                     #             ],
#                     # 'fill':       {'color':  colors[col_num - 1]},
#                     # 'gap': 300,
#                     })
#
#                     chart_four.set_size({'width':550, 'height': 360})
#                     chart_four.set_title ({'name': 'staff Wise'})
#                     chart_four.set_style(11)
#                     worksheet1.insert_chart('A72', chart_four)
#                     #
#                     # #status pie chart
#                     worksheet1.merge_range('J73+:M73', 'Status Wise ', merge_format)
#                     chart_five= workbook.add_chart({'type': 'pie'})
#
#
#                     chart_five.add_series({
#                     # 'name':       ['Sheet1', 96, 9],
#                     'categories': ['Sheet1', 96, 9,len(dict_status.keys())+95, 9],
#                     'values':     ['Sheet1', 96, 11,len(dict_status.keys())+95, 11],
#                     'points': points,
#                     # 'points': [
#                     #             {'fill': {'color': '#5ABA10'}},
#                     #             {'fill': {'color': '#FE110E'}},
#                     #             {'fill': {'color': '#CA5C05'}},
#                     #             ],
#                     # 'fill':       {'color':  colors[col_num - 1]},
#                     # 'gap': 300,
#                     })
#
#                     chart_five.set_size({'width':550, 'height': 360})
#                     chart_five.set_title ({'name': 'status Wise'})
#                     chart_five.set_style(11)
#                     worksheet1.insert_chart('A94', chart_five)
#
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     worksheet1.merge_range('J7+:L7', 'Service Wise ', merge_format)
#                     worksheet1.merge_range('J29+:L29', 'Brand Wise ', merge_format)
#                     worksheet1.merge_range('J51+:L51', 'Item Wise ', merge_format)
#                     worksheet1.merge_range('J73+:L73', 'Staff Wise ', merge_format)
#                     worksheet1.merge_range('J95+:L95', 'Status Wise ', merge_format)
#                 else:
#                     worksheet1.merge_range('J7+:M7', 'Service Wise ', merge_format)
#                     worksheet1.merge_range('J29+:M29', 'Brand Wise ', merge_format)
#                     worksheet1.merge_range('J51+:M51', 'Item Wise ', merge_format)
#                     worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
#
#                 width = max(get_col_widths(df3))
#                 worksheet1.set_column(10, 10, width)
#                 worksheet1.protect()
#                 writer.save()
#
#
# # To save both chart and table in two sheets of a single file
#             if chart_request and table_request:
#                 service_data = {}
#                 brand_data = {}
#                 item_data = {}
#                 staff_data = {}
#                 status_data = {}
#                 all_data = {}
#
#                 #chart data
#                 dict_service = dct_data['service_all'][1]
#                 dict_brand = dct_data['brand_all'][1]
#                 dict_item = dct_data['item_all'][1]
#                 dict_staff = dct_data['staff_all'][1]
#                 dict_status = dct_data['status_all']
#
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     lst_types = ['Enquiry']
#                     service_data['#Name'] = [x.title() for x in dict_service.keys()]
#                     service_data['Enquiry']=[int(i['Enquiry']) for i in dict_service.values()]
#
#                     brand_data['#Name']= [x.title() for x in dict_brand.keys()]
#                     brand_data['Enquiry']=[int(i['Enquiry']) for i in dict_brand.values()]
#
#                     item_data['#Name']= [x.title() for x in dict_item.keys()]
#                     item_data['Enquiry']=[int(i['Enquiry']) for i in dict_item.values()]
#
#                     staff_data['#Name']= [x.title() for x in [dct_data['staffs'][i] for i in dict_staff.keys()]]
#                     staff_data['Enquiry']=[int(i['Enquiry']) for i in dict_staff.values()]
#
#                     status_data['#Name']=[x.title() for x in dict_status.keys()]
#                     status_data['Enquiry']=[int(i['Enquiry']) for i in dict_status.values()]
#                 else:
#                     lst_types = ['Enquiry','Sales']
#                     service_data['#Name'] = [x.title() for x in dict_service.keys()]
#                     service_data['Enquiry']=[int(i['Enquiry']) for i in dict_service.values()]
#                     service_data['Sale']=[int(i['Sale']) for i in dict_service.values()]
#
#                     brand_data['#Name']= [x.title() for x in dict_brand.keys()]
#                     brand_data['Enquiry']=[int(i['Enquiry']) for i in dict_brand.values()]
#                     brand_data['Sale']=[int(i['Sale']) for i in dict_brand.values()]
#
#                     item_data['#Name']= [x.title() for x in dict_item.keys()]
#                     item_data['Enquiry']=[int(i['Enquiry']) for i in dict_item.values()]
#                     item_data['Sale']=[int(i['Sale']) for i in dict_item.values()]
#
#                     staff_data['#Name']= [x.title() for x in [dct_data['staffs'][i] for i in dict_staff.keys()]]
#                     staff_data['Enquiry']=[int(i['Enquiry']) for i in dict_staff.values()]
#                     staff_data['Sale']= [int(i['Sale']) for i in dict_staff.values()]
#
#                     status_data['#Name']=[x.title() for x in dict_status.keys()]
#                     status_data['Enquiry']=[int(i['Enquiry']) for i in dict_status.values()]
#                     status_data['Sale']=[int(i['Sale']) for i in dict_status.values()]
#                 #table data
#                 lst_title = ['Date','ENQ No','Staff','Product','Customer','Brand','Item','Staff']
#                 dict_all = rst_enquiry_table_data.all()
#                 lst_all = list(zip(*dict_all))
#                 all_data['Date'] = list(map(lambda x:x.strftime('%d-%m-%y'),lst_all[3]))
#                 all_data['ENQ No'] = lst_all[4]
#                 all_data['Staff'] = lst_all[2]
#                 all_data['Customer'] = lst_all[6]
#                 all_data['Product'] = lst_all[1]
#                 all_data['Brand'] = lst_all[10]
#                 all_data['Item'] = lst_all[11]
#                 all_data['Status'] = lst_all[0]
#
#                 #Data Frame of charts
#                 df1 = pd.DataFrame(service_data, index = [i for i in range(1,len(service_data['Enquiry'])+1)])
#                 df2 = pd.DataFrame(brand_data, index = [i for i in range(1,len(brand_data['Enquiry'])+1)])
#                 df3 = pd.DataFrame(item_data, index = [i for i in range(1,len(item_data['Enquiry'])+1)])
#                 df4 = pd.DataFrame(staff_data, index = [i for i in range(1,len(staff_data['Enquiry'])+1)])
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     df5 = pd.DataFrame(status_data, index = [i for i in range(1,len(status_data['Enquiry'])+1)])
#                 #Data Frame of Table
#                 df = pd.DataFrame(all_data ,index = list(range(1,len(all_data['Item'])+1)) )
#
#                 # Create a Pandas Excel writer using XlsxWriter as the engine.
#                 # file_name = str(datetime.now())
#                 # excel_file = settings.MEDIA_ROOT+'/product_chart_table_data'+file_name+'.xlsx'
#                 excel_file = settings.MEDIA_ROOT+'/report.xlsx'
#                 sheet_name1 = 'Sheet1'
#                 sheet_name2 = 'Sheet2'
#                 writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
#
#                 # chart to excel_file sheet1
#                 df1.to_excel(writer,sheet_name=sheet_name1,startrow=7, startcol=9)
#                 df2.to_excel(writer,sheet_name=sheet_name1,startrow=29, startcol=9)
#                 df3.to_excel(writer,sheet_name=sheet_name1,startrow=51, startcol=9)
#                 df4.to_excel(writer,sheet_name=sheet_name1,startrow=73, startcol=9)
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     df5.to_excel(writer,sheet_name=sheet_name1,startrow=95, startcol=9)
#                 #table to excel_file sheet2
#                 df.to_excel(writer, sheet_name=sheet_name2,startrow=6, startcol=0)
#
#                 # Access the XlsxWriter workbook and worksheet objects from the dataframe.
#                 workbook = writer.book
#                 #for chart data
#                 worksheet1 = writer.sheets[sheet_name1]
#                 #for table data
#                 worksheet2 = writer.sheets[sheet_name2]
#                 merge_format = workbook.add_format({
#                 'bold': 4,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'font_size':17
#                 })
#
#                 merge_format1 = workbook.add_format({
#                 'bold': 20,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'font_size':23
#                 })
#                 cell_format = workbook.add_format({'bold':True,'align': 'center'})
#                 worksheet1.write('J30','No.',cell_format)
#                 worksheet1.write('J8','No.',cell_format)
#                 worksheet1.write('K8','Service',cell_format)
#                 worksheet1.write('K30','Brand Name',cell_format)
#                 worksheet1.write('J52','No.',cell_format)
#                 worksheet1.write('K52','Item Name',cell_format)
#                 worksheet1.write('J74','No.',cell_format)
#                 worksheet1.write('K74','Staff Name',cell_format)
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     worksheet1.write('J96','No.',cell_format)
#                     worksheet1.write('K96','Status',cell_format)
#                     worksheet1.merge_range('J95+:M95', 'Status Wise ', merge_format)
#
#                 worksheet1.merge_range('A1+:M2', ' Product Report ', merge_format1)
#                 worksheet1.merge_range('A3+:E3',date)
#                 worksheet1.merge_range('A4+:E4',user)
#                 worksheet1.merge_range('K3+:M3',filter_branch)
#                 worksheet1.merge_range('K4+:M4',filter_staff_name)
#                 worksheet1.merge_range('A5+:E5',report_date)
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     worksheet1.merge_range('A6+:I112','')
#                 else:
#                     worksheet1.merge_range('A6+:I90','')
#                 worksheet2.merge_range('A1+:I2', ' Product Report ', merge_format1)
#                 worksheet2.merge_range('A3+:E3',date)
#                 worksheet2.merge_range('A4+:E4',user)
#                 worksheet2.merge_range('G3+:I3',filter_branch)
#                 worksheet2.merge_range('G4+:I4',filter_staff_name)
#                 worksheet2.merge_range('A5+:E5',report_date)
#
#                 for i,width in enumerate(get_col_widths(df)):
#                     worksheet2.set_column(i, i, width)
#                 # =================================chart1===================================
#                 # worksheet1.merge_range('J7+:M7', 'Service Wise ', merge_format)
#                 # Create a chart object.
#                 # chart= workbook.add_chart({'type': 'column'})
#                 chart_one = workbook.add_chart({'type': 'column'})
#
#                 # chart chart_one
#                 for col_num in range(1, len(lst_types) + 1):
#                     chart_one.add_series({
#                     'name':       ['Sheet1', 7 ,10+col_num],
#                     'categories': ['Sheet1', 8, 9 ,len(dict_service.keys())+7, 9],
#                     'values':     ['Sheet1', 8,10+col_num, len(dict_service.keys())+7, 10+col_num],
#                     'fill':       {'color':  colors[col_num - 1]},
#                     'gap': 300,
#                     })
#
#                 # Add a chart title and some axis labels.
#                 chart_one.set_size({'width':550, 'height': 360})
#                 chart_one.set_title ({'name': 'Service Wise'})
#                 # Set an Excel chart style.
#                 chart_one.set_style(11)
#                 # Configure the chart axes.
#                 chart_one.set_y_axis({
#                 'major_gridlines': {'visible': True}
#                 })
#                 # Insert the chart into the worksheet.
#                 worksheet1.insert_chart('A6', chart_one)
#
#                 # ======================================chart2====================================================
#                 # worksheet1.merge_range('A17+:C17', 'Service Wise ', merge_format)
#                 # worksheet1.merge_range('J29+:M29', 'Brand Wise ', merge_format)
#                 chart_two= workbook.add_chart({'type': 'column'})
#
#                 for col_num in range(1, len(lst_types) + 1):
#                     chart_two.add_series({
#                     'name':       ['Sheet1', 29, 10+col_num],
#                     'categories': ['Sheet1', 30, 9,len(dict_brand.keys())+29,9],
#                     'values':     ['Sheet1', 30, 10+col_num,len(dict_brand.keys())+29, 10+col_num],
#                     'fill':       {'color':  colors[col_num - 1]},
#                     'gap': 300,
#                     })
#
#                 chart_two.set_size({'width':550, 'height': 360})
#                 chart_two.set_title ({'name': 'Brand Wise'})
#                 chart_two.set_style(11)
#                 chart_two.set_y_axis({
#                 'major_gridlines': {'visible': True}
#                 })
#                 # worksheet.insert_chart('H3', chart2)
#                 worksheet1.insert_chart('A28', chart_two)
#                 # worksheet1.insert_chart('I13', chart1)
#                 # ======================================chart3======================================================
#                 # worksheet1.merge_range('J51+:M51', 'Item Wise ', merge_format)
#                 # chart3= workbook.add_chart({'type': 'column'})
#                 chart_three= workbook.add_chart({'type': 'column'})
#
#                 for col_num in range(1, len(lst_types) + 1):
#                     chart_three.add_series({
#                     'name':       ['Sheet1', 51, 10+col_num],
#                     'categories': ['Sheet1', 52, 9,len(dict_item.keys())+51, 9],
#                     'values':     ['Sheet1', 52, 10+col_num,len(dict_item.keys())+51, 10+col_num],
#                     'fill':       {'color':  colors[col_num - 1]},
#                     'gap': 300,
#                     })
#                 chart_three.set_size({'width':550, 'height': 360})
#                 chart_three.set_title ({'name': 'Item Wise'})
#                 chart_three.set_style(11)
#                 chart_three.set_y_axis({
#                 'major_gridlines': {'visible': True}
#                 })
#
#                 worksheet1.insert_chart('A50', chart_three)
#                 # ======================================chart4======================================================
#                 if request.data['type'].upper() != 'ENQUIRY':
#                     # worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
#                     chart_four= workbook.add_chart({'type': 'column'})
#
#                     for col_num in range(1, len(lst_types) + 1):
#                         chart_four.add_series({
#                         'name':       ['Sheet1', 73, 10+col_num],
#                         'categories': ['Sheet1', 74, 9,len(dict_staff.keys())+73, 9],
#                         'values':     ['Sheet1', 74, 10+col_num,len(dict_staff.keys())+73, 10+col_num],
#                         'fill':       {'color':  colors[col_num - 1]},
#                         'gap': 300,
#                         })
#
#                     chart_four.set_size({'width':550, 'height': 360})
#                     chart_four.set_title ({'name': 'Staff Wise'})
#                     chart_four.set_style(11)
#                     chart_four.set_y_axis({
#                     'major_gridlines': {'visible': True}
#                     })
#                     worksheet1.insert_chart('A72', chart_four)
#
#                 else:
#                     # worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
#
#                     chart_four= workbook.add_chart({'type': 'pie'})
#
#
#                     chart_four.add_series({
#                     # 'name':       ['Sheet1', 73, 9],
#                     'categories': ['Sheet1', 74, 9,len(dict_staff.keys())+73, 9],
#                     'values':     ['Sheet1', 74, 10+col_num,len(dict_staff.keys())+73, 10+col_num],
#                     'points': points,
#                     # 'points': [
#                     #             {'fill': {'color': '#5ABA10'}},
#                     #             {'fill': {'color': '#FE110E'}},
#                     #             {'fill': {'color': '#CA5C05'}},
#                     #             ],
#                     # 'fill':       {'color':  colors[col_num - 1]},
#                     # 'gap': 300,
#                     })
#
#                     chart_four.set_size({'width':550, 'height': 360})
#                     chart_four.set_title ({'name': 'staff Wise'})
#                     chart_four.set_style(11)
#                     worksheet1.insert_chart('A72', chart_four)
#
#                     #status pie chart
#                     worksheet1.merge_range('J73+:M73', 'Status Wise ', merge_format)
#                     chart_five= workbook.add_chart({'type': 'pie'})
#
#
#                     chart_five.add_series({
#                     # 'name':       ['Sheet1', 96, 9],
#                     'categories': ['Sheet1', 96, 9,len(dict_status.keys())+95, 9],
#                     'values':     ['Sheet1', 96, 11,len(dict_status.keys())+95, 11],
#                     'points': points,
#                     # 'points': [
#                     #             {'fill': {'color': '#5ABA10'}},
#                     #             {'fill': {'color': '#FE110E'}},
#                     #             {'fill': {'color': '#CA5C05'}},
#                     #             ],
#                     # 'fill':       {'color':  colors[col_num - 1]},
#                     # 'gap': 300,
#                     })
#
#                     chart_five.set_size({'width':550, 'height': 360})
#                     chart_five.set_title ({'name': 'status Wise'})
#                     chart_five.set_style(11)
#                     worksheet1.insert_chart('A94', chart_five)
#
#                 if request.data['type'].upper() == 'ENQUIRY':
#                     worksheet1.merge_range('J7+:L7', 'Service Wise ', merge_format)
#                     worksheet1.merge_range('J29+:L29', 'Brand Wise ', merge_format)
#                     worksheet1.merge_range('J51+:L51', 'Item Wise ', merge_format)
#                     worksheet1.merge_range('J73+:L73', 'Staff Wise ', merge_format)
#                     worksheet1.merge_range('J95+:L95', 'Status Wise ', merge_format)
#                 else:
#                     worksheet1.merge_range('J7+:M7', 'Service Wise ', merge_format)
#                     worksheet1.merge_range('J29+:M29', 'Brand Wise ', merge_format)
#                     worksheet1.merge_range('J51+:M51', 'Item Wise ', merge_format)
#                     worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
#
#                 width = max(get_col_widths(df3))
#                 worksheet1.set_column(10, 10, width)
#                 worksheet1.protect()
#                 worksheet2.protect()
#                 writer.save()
#
#             # import pdb; pdb.set_trace()
#             if export_type.upper() == 'DOWNLOAD':
#                 data = settings.HOSTNAME+'/media/report.xlsx'
#                 return Response({'status':'success','data':data})
#             if export_type.upper() == 'MAIL':
#                 filename = excel_file
#                 to = request.data.get('email')
#                 subject =  'Product Report Print'
#                 from_email = settings.EMAIL_HOST_EMAIL
#                 text_content = 'Travidux'
#                 html_content = '''Dear, '''
#                 email_sent(subject, text_content,from_email,to,html_content,filename)
#                 return Response({'status':'success'})
#         except Exception as msg:
#                 return JsonResponse({'status':'failed','data':str(msg)})

# ===================================================================================================================================================================================================================================
# ===================================================================================================================================================================================================================================

# ===================================================================================================================================================================================================================================
# ===================================================================================================================================================================================================================================
class ServiceReportMobileExportExcel(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            session = Session()
            lst_enquiry_data = []
            if request.data.get('company_id'):
                int_company = request.data.get('company_id')
            else:
                int_company = str(request.user.userdetails.fk_company_id)

            if request.data.get('show_type'):
                str_show_type = 'total_amount'
            else:
                str_show_type = 'int_quantity'
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)

            fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
            todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )

            dct_data={}
            table_request = request.data['bln_table']
            chart_request = request.data['bln_chart']
            export_type = request.data.get('export_type')
            enquiry_color = '#0d8ec1'
            sale_color = '#77a7fb'
            points =[{'fill': {'color': '#01c0c8'}},
                     {'fill': {'color': '#2ecc71'}},
                     {'fill': {'color': '#fb9678'}},
                     {'fill': {'color': '#799fb9'}},
                     {'fill': {'color': '#7e81cb'}},
                     {'fill': {'color': '#cf8595'}},
                     {'fill': {'color': '#9ea720'}},
                     {'fill': {'color': '#bd988b'}},
                     {'fill': {'color': '#008080'}},
                     {'fill': {'color': '#ff99cc'}},
                     {'fill': {'color': '#99ccff'}},
                     {'fill': {'color': '#00ffff'}},
                     {'fill': {'color': '#fba82c'}},
                     {'fill': {'color': '#b0b1a1'}},
                     {'fill': {'color': '#b156b1'}},
                     {'fill': {'color': '#cd3b42'}},
                     {'fill': {'color': '#4188cf'}},
                     {'fill': {'color': '#c18ff4'}},
                     {'fill': {'color': '#866668'}},
                     {'fill': {'color': '#757081'}},
                     {'fill': {'color': '#f4d03f'}}
                     ]

            if AdminSettings.objects.filter(vchr_code='ENQUIRY_COLOUR',bln_enabled=True).values('vchr_value'):
                enquiry_color = AdminSettings.objects.filter(vchr_code='ENQUIRY_COLOUR',bln_enabled=True).values('vchr_value')
                if enquiry_color:
                    enquiry_color = enquiry_color[0]['vchr_value'][0]
                else:
                    enquiry_color = '#0d8ec1'
            if AdminSettings.objects.filter(vchr_code='SALES_COLOUR',bln_enabled=True).values('vchr_value'):
                sale_color = AdminSettings.objects.filter(vchr_code='SALES_COLOUR',bln_enabled=True).values('vchr_value')
                if sale_color:
                    sale_color = sale_color[0]['vchr_value'][0]
                else:
                    sale_color = '#77a7fb'
            # import pdb; pdb.set_trace()
            if AdminSettings.objects.filter(vchr_code='PIE_CHART_COLOURS',bln_enabled=False).values('vchr_value'):
                pie_color =  AdminSettings.objects.filter(vchr_code='PIE_CHART_COLOURS',bln_enabled=False).values('vchr_value')
                if pie_color:
                    points =[]
                    points = [{'fill': {'color':i}} for i in pie_color[0]['vchr_value']]
            colors = [enquiry_color,sale_color]

            # common header
            filter_branch = 'Branch : All'
            filter_staff_name = 'Staff : All'
            date = 'Date : '+str(datetime.strftime(fromdate,"%d-%m-%Y"))+' To '+str(datetime.strftime(todate,"%d-%m-%Y"))
            user = 'Name : '+str(request.user.first_name)+' '+str(request.user.last_name)
            report_date = 'Report Date & Time : '+ str(datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p"))
            # materialized views
            engine = get_engine()
            conn = engine.connect()
            lst_mv_view = []
            lst_mv_view = request.data.get('lst_mv')

            if not lst_mv_view:
                session.close()
                return JsonResponse({'status':'failed', 'reason':'No view list found'})
            query_set = ''

            if chart_request or table_request and chart_request:
                if len(lst_mv_view) == 1:
                    if request.data['type'].upper() == 'ENQUIRY':
                        query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name, user_id as fk_assigned, staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id"
                    else:
                        query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name,user_id as fk_assigned,staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id"
                else:
                    if request.data['type'].upper() == 'ENQUIRY':
                        for data in lst_mv_view:
                            query_set += "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned, branch_id, product_id, brand_id,staff_first_name, staff_last_name from "+data+" {} group by  vchr_enquiry_status , vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned, branch_id, product_id, brand_id,staff_first_name, staff_last_name union "
                    else:
                         for data in lst_mv_view:
                            query_set +="select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned, vchr_brand_name, vchr_item_name,promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name, staff_last_name from "+data+" {} group by vchr_enquiry_status, vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name, staff_last_name union "
                    query = query_set.rsplit(' ', 2)[0]

                """ data wise filtering """
                str_filter_data = "where dat_enquiry :: date BETWEEN '"+request.data['date_from']+"' AND '"+request.data['date_to']+"' AND int_company_id = "+int_company+""


                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','GENERAL MANAGER SALES','COUNTRY HEAD']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                    str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.userdetails.fk_branch_id)+""
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                    str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})

                if request.data.get('branch'):
                    branch = request.data.get('branch')

                    str_filter_data += " AND branch_id = "+str(branch)+""
                if request.data.get('staff'):
                    staff = request.data.get('staff')

                    str_filter_data += " AND user_id = "+str(staff)+""
                if request.data.get('product'):

                    str_filter_data += " AND product_id = "+str(request.data.get('product'))+""
                if request.data.get('brand'):

                    str_filter_data += " AND brand_id = "+str(request.data.get('brand'))+""

                if len(lst_mv_view) == 1:
                    query = query.format(str_filter_data)
                else:
                    query = query.format(str_filter_data,str_filter_data)
                rst_enquiry = conn.execute(query).fetchall()

                if not rst_enquiry:
                    session.close()
                    return Response({'status':'failed','reason':'No Data'})

                dct_data={}
                dct_data['service_all']={}
                dct_data['brand_all']={}
                dct_data['item_all']={}
                dct_data['staff_all']={}
                dct_data['status_all']={}
                dct_data['staffs']={}

                for ins_data in rst_enquiry:
                    if ins_data.vchr_service not in dct_data['service_all']:
                        dct_data['service_all'][ins_data.vchr_service]={}
                        dct_data['service_all'][ins_data.vchr_service]['Enquiry']=ins_data.counts
                        dct_data['service_all'][ins_data.vchr_service]['Sale']=0

                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_all'][ins_data.vchr_service]['Sale']=ins_data.counts
                    else:
                        dct_data['service_all'][ins_data.vchr_service]['Enquiry']+=ins_data.counts

                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_all'][ins_data.vchr_service]['Sale'] += ins_data.counts

                    if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts

                    else:
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts

                    if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                        dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
                        if ins_data.vchr_enquiry_status =='INVOICED':
                            dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    else:
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                    if ins_data.fk_assigned not in dct_data['staff_all']:
                        dct_data['staffs'][ins_data.fk_assigned]=str(ins_data.staff_first_name+" "+ins_data.staff_last_name).title()
                        dct_data['staff_all'][ins_data.fk_assigned]={}
                        dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                        dct_data['staff_all'][ins_data.fk_assigned]['Sale']=0
                        if ins_data.vchr_enquiry_status =='INVOICED':
                            dct_data['staff_all'][ins_data.fk_assigned]['Sale']=ins_data.counts
                    else:
                        dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['staff_all'][ins_data.fk_assigned]['Sale']+=ins_data.counts
                    if ins_data.vchr_enquiry_status not in dct_data['status_all']:
                        dct_data['status_all'][ins_data.vchr_enquiry_status]={}
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
                    else:
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts

                # import pdb; pdb.set_trace()

                if request.data['type'] == 'Sale':
                    dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
                    dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
                    dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
                    dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)

                elif request.data['type'] == 'Enquiry':
                    dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
                    dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
                    dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
                    dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)
# ========================================tabledata========================================================================================================================
            if table_request or table_request and chart_request:
                rst_enquiry_table_data = session.query(ItemEnquirySA.vchr_enquiry_status,
                                    ProductSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
                                    AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),(CustomerSA.cust_fname+" "+CustomerSA.cust_lname).label('customer_full_name'),
                                    AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
                                    AuthUserSA.first_name.label('staff_first_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
                                    UserSA.fk_brand_id,UserSA.dat_resignation_applied,
                                    case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
                                        else_=literal_column("'not resigned'")).label("is_resigned"))\
                                    .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
                                            cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
                                            EnquiryMasterSA.fk_company_id == 1 ,
                                            EnquiryMasterSA.chr_doc_status == 'N')\
                                    .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                    .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                    .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                    .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                    .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
                                    .join(ProductSA,ProductSA.id == ItemEnquirySA.fk_product_id)\
                                    .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
                                    .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)

                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','GENERAL MANAGER SALES','COUNTRY HEAD']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    rst_enquiry_table_data = rst_enquiry_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    rst_enquiry_table_data = rst_enquiry_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})
                if request.data.get('branch'):
                    branch = request.data.get('branch')
                    rst_enquiry_table_data = rst_enquiry_table_data.filter(EnquiryMasterSA.fk_branch_id == branch)
                if request.data.get('staff'):
                    staff = request.data.get('staff')
                    rst_enquiry_table_data = rst_enquiry_table_data.filter(AuthUserSA.id == staff)

            # ============================================================= Table Data in Excel=================================================================================================
            if table_request and not chart_request :
                if not rst_enquiry_table_data.all():
                    session.close()
                    return Response({'status':'failed','reason':'No data'})
                else:
                    all_data = {}
                    # lst_title = ['Date','ENQ No','Staff','Product','Customer','Brand','Item','Staff']
                    dict_all = rst_enquiry_table_data.all()
                    lst_all = list(zip(*dict_all))

                    all_data['1_ENQ No'] = lst_all[4]
                    all_data['2_Date'] = list(map(lambda x:x.strftime('%d-%m-%y'),lst_all[3]))
                    all_data['3_Customer'] = lst_all[6]
                    all_data['4_Staff'] = lst_all[2]
                    all_data['5_Product'] = lst_all[1]
                    all_data['6_Brand'] = lst_all[10]
                    all_data['7_Item'] = lst_all[11]
                    all_data['8_Status'] = lst_all[0]

                    # import pdb; pdb.set_trace()

                    df = pd.DataFrame(all_data)
                    # df = pd.DataFrame(all_data ,index = list(range(1,len(all_data['7_Item'])+1)) )

                    # Create a Pandas Excel writer using XlsxWriter as the engine.
                    excel_file = settings.MEDIA_ROOT+'/report.xlsx'
                    sheet_name1 = 'Sheet1'
                    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                    # df.sort_values('1_ENQ No')
                    df.sort_values('1_ENQ No').to_excel(writer,index=False, sheet_name=sheet_name1,startrow=6, startcol=0)
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name1]
                    merge_format1 = workbook.add_format({
                        'bold': 20,
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_size':23
                        })
                    cell_format = workbook.add_format({'bold':True,'align': 'center'})
                    worksheet.merge_range('A1+:H2', ' Product Report ', merge_format1)
                    worksheet.merge_range('A3+:E3',date)
                    worksheet.merge_range('A4+:E4',user)
                    worksheet.merge_range('A5+:E5',report_date)
                    worksheet.merge_range('G3+:H3',filter_branch)
                    worksheet.merge_range('G4+:H4',filter_staff_name)
                    # worksheet.write('J8','No.',cell_format)

                    for i,width in enumerate(get_col_widths(df)):
                        worksheet.set_column(i-1, i-1, width)
                    worksheet.set_column(0, 0,12)
                    worksheet.set_column(1, 1,10)
                    worksheet.set_column(2, 2,15)
                    worksheet.set_column(3, 3,15)
                    worksheet.set_column(3, 3,15)
                    worksheet.set_column(4, 4,15)
                    worksheet.set_column(5, 5,15)
                    worksheet.write('A7','ENQ No',cell_format)
                    worksheet.write('B7','Date',cell_format)
                    worksheet.write('C7','Customer',cell_format)
                    worksheet.write('D7','Staff',cell_format)
                    worksheet.write('E7','Product',cell_format)
                    worksheet.write('F7','Brand',cell_format)
                    worksheet.write('G7','Item',cell_format)
                    worksheet.write('H7','Status',cell_format)

                    worksheet.protect()
                    writer.save()
# ========================================tabledata========================================================================================================================
            if chart_request :
                service_data = {}
                brand_data = {}
                item_data = {}
                staff_data = {}
                status_data = {}
                all_data = {}

                dict_service = dct_data['service_all'][1]
                dict_brand = dct_data['brand_all'][1]
                dict_item = dct_data['item_all'][1]
                dict_staff = dct_data['staff_all'][1]
                dict_status = dct_data['status_all']

                service_data['#Name'] = [x.title() for x in dict_service.keys()]
                service_data['Enquiry']=[int(i['Enquiry']) for i in dict_service.values()]

                brand_data['#Name']= [x.title() for x in dict_brand.keys()]
                brand_data['Enquiry']=[int(i['Enquiry']) for i in dict_brand.values()]

                item_data['#Name']= [x.title() for x in dict_item.keys()]
                item_data['Enquiry']=[int(i['Enquiry']) for i in dict_item.values()]

                staff_data['#Name']= [x.title() for x in [dct_data['staffs'][i] for i in dict_staff.keys()]]
                staff_data['Enquiry']=[int(i['Enquiry']) for i in dict_staff.values()]

                status_data['#Name']=[x.title() for x in dict_status.keys()]
                status_data['Enquiry']=[int(i['Enquiry']) for i in dict_status.values()]

                if request.data['type'].upper() == 'ENQUIRY':
                    lst_types = ['Enquiry']
                else:
                    lst_types = ['Enquiry','Sales']

                    service_data['Sale']=[int(i['Sale']) for i in dict_service.values()]
                    brand_data['Sale']=[int(i['Sale']) for i in dict_brand.values()]
                    item_data['Sale']=[int(i['Sale']) for i in dict_item.values()]
                    staff_data['Sale']= [int(i['Sale']) for i in dict_staff.values()]
                    status_data['Sale']=[int(i['Sale']) for i in dict_status.values()]

                df1 = pd.DataFrame(service_data, index = [i for i in range(1,len(service_data['Enquiry'])+1)])
                df2 = pd.DataFrame(brand_data, index = [i for i in range(1,len(brand_data['Enquiry'])+1)])
                df3 = pd.DataFrame(item_data, index = [i for i in range(1,len(item_data['Enquiry'])+1)])
                df4 = pd.DataFrame(staff_data, index = [i for i in range(1,len(staff_data['Enquiry'])+1)])
                if request.data['type'].upper() == 'ENQUIRY':
                    df5 = pd.DataFrame(status_data, index = [i for i in range(1,len(status_data['Enquiry'])+1)])

                # Create a Pandas Excel writer using XlsxWriter as the engine.
                excel_file = settings.MEDIA_ROOT+'/report.xlsx'
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                # import pdb; pdb.set_trace()

                sheet_name1 = 'Sheet1'
                if table_request and chart_request:
                    sheet_name2 = 'Sheet2'

                df1.to_excel(writer,sheet_name=sheet_name1,startrow=7, startcol=9)
                df2.to_excel(writer,sheet_name=sheet_name1,startrow=29, startcol=9)
                df3.to_excel(writer,sheet_name=sheet_name1,startrow=51, startcol=9)
                df4.to_excel(writer,sheet_name=sheet_name1,startrow=73, startcol=9)
                if request.data['type'].upper() == 'ENQUIRY':
                    df5.to_excel(writer,sheet_name=sheet_name1,startrow=95, startcol=9)

                # Access the XlsxWriter workbook and worksheet objects from the dataframe.
                workbook = writer.book
                worksheet1 = writer.sheets[sheet_name1]
                cell_format = workbook.add_format({'bold':True,'align': 'center'})


                merge_format = workbook.add_format({
                'bold': 4,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':17
                })

                merge_format1 = workbook.add_format({
                'bold': 20,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':23
                })




                # =================================chart1===================================
                # Create a chart object.
                chart_one = workbook.add_chart({'type': 'column'})

                # chart chart_one
                for col_num in range(1, len(lst_types) + 1):
                    chart_one.add_series({
                    'name':       ['Sheet1', 7 ,10+col_num],
                    'categories': ['Sheet1', 8, 9 ,len(dict_service.keys())+7, 9],
                    'values':     ['Sheet1', 8,10+col_num, len(dict_service.keys())+7, 10+col_num],
                    'fill':       {'color':  colors[col_num - 1]},
                    'gap': 300,
                    })

                # Add a chart title and some axis labels.
                chart_one.set_size({'width':550, 'height': 360})
                chart_one.set_title ({'name': 'Product Wise'})

                # Set an Excel chart style.
                chart_one.set_style(11)
                # Configure the chart axes.
                chart_one.set_y_axis({
                'major_gridlines': {'visible': True}
                })
                # Insert the chart into the worksheet.
                worksheet1.insert_chart('A6', chart_one)

                # ======================================chart2====================================================
                chart_two= workbook.add_chart({'type': 'column'})

                for col_num in range(1, len(lst_types) + 1):
                    chart_two.add_series({
                    'name':       ['Sheet1', 29, 10+col_num],
                    'categories': ['Sheet1', 30, 9,len(dict_brand.keys())+29,9],
                    'values':     ['Sheet1', 30, 10+col_num,len(dict_brand.keys())+29, 10+col_num],
                    'fill':       {'color':  colors[col_num - 1]},
                    'gap': 300,
                    })

                chart_two.set_size({'width':550, 'height': 360})
                chart_two.set_title ({'name': 'Brand Wise'})
                chart_two.set_style(11)
                chart_two.set_y_axis({
                'major_gridlines': {'visible': True}
                })
                worksheet1.insert_chart('A28', chart_two)
                # ======================================chart3======================================================
                chart_three= workbook.add_chart({'type': 'column'})
                for col_num in range(1, len(lst_types) + 1):
                    chart_three.add_series({
                    'name':       ['Sheet1', 51, 10+col_num],
                    'categories': ['Sheet1', 52, 9,len(dict_item.keys())+51, 9],
                    'values':     ['Sheet1', 52, 10+col_num,len(dict_item.keys())+51, 10+col_num],
                    'fill':       {'color':  colors[col_num - 1]},
                    'gap': 300,
                    })
                chart_three.set_size({'width':550, 'height': 360})
                chart_three.set_title ({'name': 'Item Wise'})
                chart_three.set_style(11)
                chart_three.set_y_axis({
                'major_gridlines': {'visible': True}
                })

                worksheet1.insert_chart('A50', chart_three)
                # ======================================chart4======================================================
                if request.data['type'].upper() != 'ENQUIRY':
                    chart_four= workbook.add_chart({'type': 'column'})

                    for col_num in range(1, len(lst_types) + 1):
                        chart_four.add_series({
                        'name':       ['Sheet1', 73, 10+col_num],
                        'categories': ['Sheet1', 74, 9,len(dict_staff.keys())+73, 9],
                        'values':     ['Sheet1', 74, 10+col_num,len(dict_staff.keys())+73, 10+col_num],
                        'fill':       {'color':  colors[col_num - 1]},
                        'gap': 300,
                        })

                    chart_four.set_size({'width':550, 'height': 360})
                    chart_four.set_title ({'name': 'Staff Wise'})
                    chart_four.set_style(11)
                    chart_four.set_y_axis({
                    'major_gridlines': {'visible': True}
                    })
                    worksheet1.insert_chart('A72', chart_four)

                else:
                    #status pie chart
                    chart_four= workbook.add_chart({'type': 'pie'})

                    chart_four.add_series({
                    'categories': ['Sheet1', 74, 9,len(dict_staff.keys())+73, 9],
                    'values':     ['Sheet1', 74, 10+col_num,len(dict_staff.keys())+73, 10+col_num],
                    'points': points,
                    })

                    chart_four.set_size({'width':550, 'height': 360})
                    chart_four.set_title ({'name': 'Staff Wise'})
                    chart_four.set_style(11)
                    worksheet1.insert_chart('A72', chart_four)

                # ======================================chart5======================================================

                    chart_five= workbook.add_chart({'type': 'pie'})

                    chart_five.add_series({
                    'categories': ['Sheet1', 96, 9,len(dict_status.keys())+95, 9],
                    'values':     ['Sheet1', 96, 11,len(dict_status.keys())+95, 11],
                    'points': points,
                    })

                    chart_five.set_size({'width':550, 'height': 360})
                    chart_five.set_title ({'name': 'Status Wise'})
                    chart_five.set_style(11)
                    worksheet1.insert_chart('A94', chart_five)

                if request.data['type'].upper() == 'ENQUIRY':
                    worksheet1.merge_range('J7+:L7', 'Product Wise ', merge_format)
                    worksheet1.merge_range('J29+:L29', 'Brand Wise ', merge_format)
                    worksheet1.merge_range('J51+:L51', 'Item Wise ', merge_format)
                    worksheet1.merge_range('J73+:L73', 'Staff Wise ', merge_format)
                    worksheet1.merge_range('J95+:L95', 'Status Wise ', merge_format)
                    worksheet1.write('J96','No.',cell_format)
                    worksheet1.write('K96','Status',cell_format)
                    worksheet1.merge_range('J95+:M95', 'Status Wise ', merge_format)
                    worksheet1.merge_range('A6+:I112','')
                    worksheet1.merge_range('A1+:L2', ' Product Report ', merge_format1)
                    worksheet1.merge_range('K3+:L3',filter_branch)
                    worksheet1.merge_range('K4+:L4',filter_staff_name)

                else:
                    worksheet1.merge_range('J7+:M7', 'Product Wise ', merge_format)
                    worksheet1.merge_range('J29+:M29', 'Brand Wise ', merge_format)
                    worksheet1.merge_range('J51+:M51', 'Item Wise ', merge_format)
                    worksheet1.merge_range('J73+:M73', 'Staff Wise ', merge_format)
                    worksheet1.merge_range('A6+:I90','')
                    worksheet1.merge_range('A1+:M2', ' Product Report ', merge_format1)
                    worksheet1.merge_range('K3+:M3',filter_branch)
                    worksheet1.merge_range('K4+:M4',filter_staff_name)

                worksheet1.write('J8','No.',cell_format)
                worksheet1.write('K8','Product Name',cell_format)
                worksheet1.write('J30','No.',cell_format)
                worksheet1.write('K30','Brand Name',cell_format)
                worksheet1.write('J52','No.',cell_format)
                worksheet1.write('K52','Item Name',cell_format)
                worksheet1.write('J74','No.',cell_format)
                worksheet1.write('K74','Staff Name',cell_format)
                worksheet1.merge_range('A3+:E3',date)
                worksheet1.merge_range('A4+:E4',user)
                worksheet1.merge_range('A5+:E5',report_date)

                width = max(get_col_widths(df3))
                worksheet1.set_column(10, 10, width)
                worksheet1.protect()

                if table_request:
                    all_data = {}
                    # lst_title = ['Date','ENQ No','Staff','Product','Customer','Brand','Item','Staff']
                    dict_all = rst_enquiry_table_data.all()
                    lst_all = list(zip(*dict_all))

                    all_data['1_ENQ No'] = lst_all[4]
                    all_data['2_Date'] = list(map(lambda x:x.strftime('%d-%m-%y'),lst_all[3]))
                    all_data['3_Customer'] = lst_all[6]
                    all_data['4_Staff'] = lst_all[2]
                    all_data['5_Product'] = lst_all[1]
                    all_data['6_Brand'] = lst_all[10]
                    all_data['7_Item'] = lst_all[11]
                    all_data['8_Status'] = lst_all[0]

                    # import pdb; pdb.set_trace()

                    # df = pd.DataFrame(all_data)
                    df = pd.DataFrame(all_data ,index = list(range(1,len(all_data['7_Item'])+1)) )

                    # Create a Pandas Excel writer using XlsxWriter as the engine.

                    df.sort_values('1_ENQ No').to_excel(writer,index=False, sheet_name=sheet_name2,startrow=6, startcol=0)
                    # workbook = writer.book
                    worksheet2 = writer.sheets[sheet_name2]
                    merge_format1 = workbook.add_format({
                        'bold': 20,
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_size':23
                        })
                    worksheet2.merge_range('A1+:H2', ' Product Report ', merge_format1)
                    worksheet2.merge_range('A3+:E3',date)
                    worksheet2.merge_range('A4+:E4',user)
                    worksheet2.merge_range('A5+:E5',report_date)
                    worksheet2.merge_range('G3+:H3',filter_branch)
                    worksheet2.merge_range('G4+:H4',filter_staff_name)
                    # worksheet2.write('J8','No.',cell_format)

                    for i,width in enumerate(get_col_widths(df)):
                        worksheet2.set_column(i-1, i-1, width)
                    worksheet2.set_column(0, 0,12)
                    worksheet2.set_column(1, 1,10)
                    worksheet2.set_column(2, 2,15)
                    worksheet2.set_column(3, 3,15)
                    worksheet2.set_column(3, 3,15)
                    worksheet2.set_column(4, 4,15)
                    worksheet2.set_column(5, 5,15)
                    worksheet2.write('A7','ENQ No',cell_format)
                    worksheet2.write('B7','Date',cell_format)
                    worksheet2.write('C7','Customer',cell_format)
                    worksheet2.write('D7','Staff',cell_format)
                    worksheet2.write('E7','Product',cell_format)
                    worksheet2.write('F7','Brand',cell_format)
                    worksheet2.write('G7','Item',cell_format)
                    worksheet2.write('H7','Status',cell_format)
                    worksheet2.protect()


                writer.save()


            if export_type.upper() == 'DOWNLOAD':
                data = settings.HOSTNAME+'/media/report.xlsx'
                session.close()
                return Response({'status':'success','data':data})
            if export_type.upper() == 'MAIL':
                filename = excel_file
                to = request.data.get('email')
                subject =  'Product Report Print'
                from_email = settings.EMAIL_HOST_EMAIL
                text_content = 'Travidux'
                html_content = '''Dear, '''
                email_sent(subject, text_content,from_email,to,html_content,filename)
                session.close()
                return Response({'status':'success'})
        except Exception as msg:
                session.close()
                return JsonResponse({'status':'failed','data':str(msg)})

class PriceRangeReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            dat_from =  datetime.strptime(request.data['datFrom'][:10] , '%Y-%m-%d' )
            dat_to = datetime.strptime(request.data['datTo'][:10] , '%Y-%m-%d' )

            engine = get_engine()
            conn = engine.connect()
            session = Session()




            str_query_set = "select sum(int_qty) as int_qty,sum(dbl_net_amount) as dbl_value,dbl_price_range from branch_item_sale INNER JOIN items ON branch_item_sale.fk_item_id = items.id   {} group by dbl_price_range"

            """ date wise filtering """
            str_filter_data = "where dat_sale::date BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"' "

            if request.data.get("intProductId"):
                str_filter_data += "AND items.fk_product_id ="+str(request.data.get("intProductId"))+""
            if request.data.get("intBrandId"):
                str_filter_data += "AND items.fk_brand_id ="+str(request.data.get("intBrandId"))+""
            if request.data.get("intBranchId"):
                str_filter_data += "AND fk_branch_id ="+str(request.data.get("intBranchId"))+""

            # import pdb; pdb.set_trace()
            str_query_set = str_query_set.format(str_filter_data)
            rst_enquiry = conn.execute(str_query_set).fetchall()

            if not rst_enquiry:
                session.close()
                return Response({'status':'failed','reason':'No Data'})


            else:
                dct_data={}
                dct_data['0-2000'] = {}
                dct_data['2001-4000'] = {}
                dct_data['4001-6000'] = {}
                dct_data['6001-10000'] = {}
                dct_data['10001-15000'] = {}
                dct_data['15001-20000'] = {}
                dct_data['20001-25000'] = {}
                dct_data['25001-35000'] = {}
                dct_data['35001-100000'] = {}
                dct_data['100001-200000'] = {}

                dct_data['0-2000']['int_qty'] = 0
                dct_data['0-2000']['dbl_amount'] = 0
                dct_data['2001-4000']['int_qty'] = 0
                dct_data['2001-4000']['dbl_amount'] = 0
                dct_data['4001-6000']['int_qty'] = 0
                dct_data['4001-6000']['dbl_amount'] = 0
                dct_data['6001-10000']['int_qty'] = 0
                dct_data['6001-10000']['dbl_amount'] = 0
                dct_data['10001-15000']['int_qty'] = 0
                dct_data['10001-15000']['dbl_amount'] = 0
                dct_data['15001-20000']['int_qty'] = 0
                dct_data['15001-20000']['dbl_amount'] = 0
                dct_data['20001-25000']['int_qty'] = 0
                dct_data['20001-25000']['dbl_amount'] = 0
                dct_data['25001-35000']['int_qty'] = 0
                dct_data['25001-35000']['dbl_amount'] = 0
                dct_data['35001-100000']['int_qty'] = 0
                dct_data['35001-100000']['dbl_amount'] = 0
                dct_data['100001-200000']['int_qty'] = 0
                dct_data['100001-200000']['dbl_amount'] = 0

                for ins in rst_enquiry:
                    if ins.dbl_price_range>0 and ins.dbl_price_range <=2000:
                        dct_data['0-2000']['int_qty'] += ins.int_qty
                        dct_data['0-2000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>2000 and ins.dbl_price_range <=4000:
                        dct_data['2001-4000']['int_qty'] += ins.int_qty
                        dct_data['2001-4000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>4000 and ins.dbl_price_range <=6000:
                        dct_data['4001-6000']['int_qty'] += ins.int_qty
                        dct_data['4001-6000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>6000 and ins.dbl_price_range <=10000:
                        dct_data['6001-10000']['int_qty'] += ins.int_qty
                        dct_data['6001-10000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>10000 and ins.dbl_price_range <=15000:
                        dct_data['10001-15000']['int_qty'] += ins.int_qty
                        dct_data['10001-15000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>15000 and ins.dbl_price_range <=20000:
                        dct_data['15001-20000']['int_qty'] += ins.int_qty
                        dct_data['15001-20000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>20000 and ins.dbl_price_range <=25000:
                        dct_data['20001-25000']['int_qty'] += ins.int_qty
                        dct_data['20001-25000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>25000 and ins.dbl_price_range <=35000:
                        dct_data['25001-35000']['int_qty'] += ins.int_qty
                        dct_data['25001-35000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>35000 and ins.dbl_price_range <=100000:
                        dct_data['35001-100000']['int_qty'] += ins.int_qty
                        dct_data['35001-100000']['dbl_amount'] += ins.dbl_value
                    if ins.dbl_price_range>100000 and ins.dbl_price_range <=200000:
                        dct_data['100001-200000']['int_qty'] += ins.int_qty
                        dct_data['100001-200000']['dbl_amount'] += ins.dbl_value
                session.close()
                return Response({'status':'success','dct_data':dct_data})


        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})



class BrandComparisonReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_from =  datetime.strptime(request.data['datFrom'][:10] , '%Y-%m-%d' )
            dat_to = datetime.strptime(request.data['datTo'][:10] , '%Y-%m-%d' )
            engine = get_engine()
            conn = engine.connect()
            session = Session()
            lst_brand_id = request.data.get("lstBrandId")
            product_id = request.data.get("intProductId")
            # import pdb; pdb.set_trace()


            # str_query_set = "select brands.vchr_brand_name as vchr_brand_name,sum(int_qty) as int_qty,sum(dbl_net_amount) as dbl_value,dbl_price_range from branch_item_sale INNER JOIN items ON branch_item_sale.fk_item_id = items.id INNER JOIN brands on items.fk_brand_id = brands.id    {} group by dbl_price_range,brands.vchr_brand_name  "

            # import pdb; pdb.set_trace()
            str_query_set = "select brands.vchr_brand_name as vchr_brand_name,sum(int_qty) as int_qty,sum(dbl_net_amount) as dbl_value ,CASE when dbl_price_range between 0 and 2000 then '0-2000' when dbl_price_range between 2001 and 4000 then '2001-4000' when dbl_price_range between 4001 and 6000 then '4001-6000' when dbl_price_range between 6001 and 10000 then '6001-10000' when dbl_price_range between 10001 and 15000 then '10001-15000' when dbl_price_range between 15001 and 20000 then '15001-20000' when dbl_price_range between 20001 and 25000 then '20001-25000' when dbl_price_range between 25001 and 35000 then '25001-35000' when dbl_price_range between 35001 and 100000 then '35001-100000' when dbl_price_range between 100001 and 200000 then '100001-200000' END AS range from branch_item_sale INNER JOIN items ON branch_item_sale.fk_item_id = items.id INNER JOIN brands on items.fk_brand_id = brands.id {} group by brands.vchr_brand_name,range;"
            str_query_set2 = "select DISTINCT vchr_brand_name from brands {};"

            str_filter_brands = ""

            """ date wise filtering """
            str_filter_data = "where dat_sale::date BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"' "


            """branch wise filtering """

            if request.data.get("intBranchId"):
                str_filter_data += "AND fk_branch_id ="+str(request.data.get("intBranchId"))+" "

            if request.data.get("intProductId"):
                str_filter_data += "AND items.fk_product_id ="+str(product_id)+" "


            """brand wise filtering"""
            if request.data.get("lstBrandId"):
                str_filter_data +=  "AND items.fk_brand_id in ("+str(lst_brand_id)[1:-1]+")"
                str_filter_brands = "WHERE id  in  ("+str(lst_brand_id)[1:-1]+")"



            str_query_set = str_query_set.format(str_filter_data)
            str_query_set2 = str_query_set2.format(str_filter_brands)
            rst_enquiry = conn.execute(str_query_set).fetchall()
            rst_brand = conn.execute(str_query_set2).fetchall()

            if not rst_enquiry:
                session.close()
                return Response({'status':'failed','reason':'No Data'})
                #===============================================================================================================================
            dct_data={}

            # import pdb; pdb.set_trace()
            lst_range = ['0-2000','2001-4000','4001-6000','6001-10000','10001-15000','15001-20000','20001-25000','25001-35000','35001-100000','100001-200000']
            lst_brand_name = [item['vchr_brand_name'] for item in rst_brand]
            dct_data={i:{j:{'int_qty':0,'value':0} for j in lst_brand_name} for i in lst_range}
            # dct_data={i:{j:{'int_qty':0,'value':0} for j in lst_brand_name} for i in lst_range}


            # dct_data = {i:{j:{'int_qty':0,'value':0} for j in lst_brand_name} for i in lst_range}

            # dct_data = dct_data.fromkeys(lst_range,{})
            # for strdct in dct_data:
            #     dct_data[strdct]=dct_data[strdct].fromkeys(asd,{'qty':0,'value':0})


            for ins in rst_enquiry:
                dct_data[ins.range][ins.vchr_brand_name]['int_qty'] = ins.int_qty
                dct_data[ins.range][ins.vchr_brand_name]['value'] = ins.dbl_value
            # import pdb; pdb.set_trace()
            session.close()
            return Response({'status':'success','dct_data':dct_data})
        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})


class PeriodComparisonReport(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:

            engine = get_engine()
            conn = engine.connect()
            session = Session()
            dat_from1 = request.data['datFrom1'][:10]
            dat_to1 = request.data['datTo1'][:10]

            # import pdb; pdb.set_trace()

            dat_from2 = request.data['datFrom2'][:10]
            dat_to2 = request.data['datTo2'][:10]
            # dat_from1 = '2018-06-01'
            # dat_to1 = '2018-12-30'
            # dat_from2 = '2018-06-01'
            # dat_to2 = '2018-12-30'
             # where dat_sale::date between '2019-01-01' and '2019-03-30' or dat_sale::date between '2019-03-01' and '2019-06-30' group by range1,range2;
            # import pdb; pdb.set_trace()
            str_query_set = "select sum(int_qty) as int_qty,sum(dbl_net_amount) as dbl_value ,CASE  when {period1} then 'Period1' when {period2} then 'Period2' END as period,CASE   when dbl_price_range between 0 and 2000 then '0-2000'  when dbl_price_range between 2001 and 4000 then '2001-4000'  when dbl_price_range between 4001 and 6000 then '4001-6000' when dbl_price_range between 6001 and 10000 then '6001-10000'  when dbl_price_range between 10001 and 15000 then '10001-15000'  when dbl_price_range between 15001 and 20000 then '15001-20000' when dbl_price_range between 20001 and 25000 then '20001-25000' when dbl_price_range between 25001 and 35000 then '25001-35000' when dbl_price_range between 35001 and 100000 then '35001-100000'  when dbl_price_range between 100001 and 200000 then '100001-200000' END as range from branch_item_sale INNER JOIN items ON branch_item_sale.fk_item_id = items.id INNER JOIN brands on items.fk_brand_id = brands.id {filter_data} group by period,range"

            """ date wise filtering """
            # str_filter_data = "where dat_sale::date BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"' OR where dat_sale::date BETWEEN '"+str(dat_from)+"' AND '"+str(dat_to)+"' "
            str_date_filter1 = "dat_sale::date between '"+dat_from1+"' AND '"+dat_to1+"' "
            str_date_filter2 = "dat_sale::date between '"+dat_from2+"' AND '"+dat_to2+"' "

            str_filter_data = " where ("+str_date_filter1 + "or " + str_date_filter2+")"

            # import pdb; pdb.set_trace()

            if request.data.get("intProductId"):
                str_filter_data += "AND items.fk_product_id ="+str(request.data.get("intProductId"))+""
            if request.data.get("intBrandId"):
                str_filter_data += "AND items.fk_brand_id ="+str(request.data.get("intBrandId"))+""
            if request.data.get("intBranchId"):
                str_filter_data += "AND fk_branch_id ="+str(request.data.get("intBranchId"))+""

            str_query_set = str_query_set.format(period1 = str_date_filter1, period2 = str_date_filter2,filter_data = str_filter_data)

            rst_enquiry = conn.execute(str_query_set).fetchall()
            if not rst_enquiry:
                session.close()
                return Response({'status':'failed','reason':'No Data'})

            lst_range = ['0-2000','2001-4000','4001-6000','6001-10000','10001-15000','15001-20000','20001-25000','25001-35000','35001-100000','100001-200000']
            dct_data = {data:{'Period1':{'qty':0,'value':0},'Period2':{'qty':0,'value':0},'qty_growth':0,'value_growth':0} for data in lst_range }

            # dct_data = dct_data.fromkeys(lst_range,{})
            # lst_period = ['Period1','Period2']
            # for strdct in dct_data:
            #     dct_data[strdct]=dct_data[strdct].fromkeys(lst_period,{'qty':0,'value':0})
            # dct_data['period1'] = dct_data['period1'].fromkeys(lst_range,{'qty':0,'value':0})
            # dct_data['period2'] = dct_data['period2'].fromkeys(lst_range,{'qty':0,'value':0})

            # import pdb; pdb.set_trace()



            for ins in rst_enquiry :
                dct_data[ins.range][ins.period]['qty'] = ins.int_qty
                dct_data[ins.range][ins.period]['value'] = ins.dbl_value
                dct_data[ins.range]['qty_growth'] = dct_data[ins.range]['Period2']['qty']
                if dct_data[ins.range]['Period1']['qty']:
                    dct_data[ins.range]['qty_growth'] = round((((dct_data[ins.range]['Period2']['qty'] - dct_data[ins.range]['Period1']['qty'])/dct_data[ins.range]['Period1']['qty'])*100),2)
                dct_data[ins.range]['value_growth'] = dct_data[ins.range]['Period2']['value']
                if dct_data[ins.range]['Period1']['value']:
                    dct_data[ins.range]['value_growth'] = round((((dct_data[ins.range]['Period2']['value'] - dct_data[ins.range]['Period1']['value'])/dct_data[ins.range]['Period1']['value'])*100),2)

            if str_date_filter1 == str_date_filter2:
                for data in dct_data:
                    dct_data[data]['Period2']['value'] = dct_data[data]['Period1']['value']
                    dct_data[data]['Period2']['qty'] = dct_data[data]['Period1']['qty']
                    dct_data[data]['value_growth'] = 0
                    dct_data[data]['qty_growth'] = 0
                # if ins.period == 'Period1':
                #     dct_data[ins.range]['Period1']['qty'] = ins.int_qty
                #     dct_data[ins.range]['Period1']['value'] = ins.dbl_value
                # else:
                #     dct_data[ins.range]['Period2']['qty'] = ins.int_qty
                #     dct_data[ins.range]['Period2']['value'] = ins.dbl_value
            #     if ins.range1:
            #         dct_data['period1'][ins.range1]['qty'] = ins.int_qty

            #         dct_data['period1'][ins.range1]['value'] = ins.dbl_value
            #
            #     if ins.range2:
            #         dct_data['period2'][ins.range2]['qty'] = ins.int_qty
            #         dct_data['period2'][ins.range2]['value'] = ins.dbl_value
            #
            # else:
            session.close()
            return Response({'status':'success','dct_data':dct_data})


        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})




# ===================================================================================================================================================================================================================================
# ===================================================================================================================================================================================================================================


class PriceRangeReportExport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dct_data = request.data.get('dctData')
            branch = request.data.get('branch')
            product = request.data.get('product')
            brand = request.data.get('brand')
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            lst_price_range = ['0-2000','2001-4000','4001-6000','6001-10000','10001-15000','15001-20000','20001-25000','25001-35000','35001-100000','100001-200000']
            lst_price_range_quantity = []
            lst_price_range_value = []

            for ins_range in lst_price_range:
                for ins_data in dct_data:
                    if ins_data == ins_range:
                        lst_price_range_quantity.append(dct_data[ins_data]['int_qty'])
                        lst_price_range_value.append(dct_data[ins_data]['dbl_amount'])


            # import pdb; pdb.set_trace()


            #creating dataframes
            df_active = pd.DataFrame({
            'SL NO':list(range(1,len(lst_price_range)+1)),
            'PRICE RANGE':lst_price_range,
            'QUANTITY':lst_price_range_quantity,
            'VALUE':lst_price_range_value,
            })
            df_active_order = df_active[['SL NO','PRICE RANGE','QUANTITY','VALUE']]
            df_active_order.index = df_active.index + 1
            #creating and writing to excel
            excel_file = '/pricerangereport.xlsx'
            file_name_export = settings.MEDIA_ROOT + excel_file

            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_active_order.to_excel(writer,sheet_name='Sheet1',index=False, startrow=7,startcol=0)



            workbook = writer.book

            cell_format1=workbook.add_format()
            cell_format1.set_align('center')
            cell_format1.set_align('vcenter')
            cell_format1.set_locked(True)
            cell_format1.set_bold()



            worksheet1 = writer.sheets['Sheet1']
            worksheet1.merge_range( 'A1+:D1','PRICE RANGE REPORT',cell_format1)

            # worksheet1.write_string(1, 0, 'Filters:-',cell_format1)
            worksheet1.write_string(2, 0, 'Branch:-')
            worksheet1.write_string(2, 1, branch)
            worksheet1.write_string(3, 0, 'Product:-')
            worksheet1.write_string(3, 1, product)
            worksheet1.write_string(4, 0, 'Brand:-')
            worksheet1.write_string(4, 1, brand)
            worksheet1.write_string(5, 0, "Date :-")
            worksheet1.write_string(5, 1, dat_from + " to " + dat_to )
            worksheet1.protect()

            worksheet1.set_column(1,4,25)

            writer.save()

            if request.data.get('email'):

                filename = file_name_export
                to = request.data.get('email')
                # to = "freddy.davis@travidux.in"
                subject =  'Price Range Report'
                from_email = settings.EMAIL_HOST_EMAIL
                text_content = 'Travidux'
                html_content = '''Dear, '''
                email_sent(subject, text_content,from_email,to,html_content,filename)

                return Response({'status':'success'})

            return Response({'status':'success','data':request.scheme+'://'+request.get_host()+'/media'+excel_file})
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})


class BrandComparisonReportExport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dct_data = request.data.get('dctData')
            branch = request.data.get('branch')
            product = request.data.get('product')
            brand = request.data.get('brand')
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            lst_price_range = ['0-2000','2001-4000','4001-6000','6001-10000','10001-15000','15001-20000','20001-25000','25001-35000','35001-100000','100001-200000']
            lst_brand = []
            lst_brand_index = []

            # lst_price_range.append(ins_detail)
            dct_new = {}
            for ins_range in lst_price_range:
                for ins_detail in dct_data:
                    if ins_range == ins_detail:
                        for ins_brand in dct_data[ins_detail]:
                            if ins_brand not in dct_new:
                                dct_new[ins_brand] = {}
                                dct_new[ins_brand]['qty'] = []
                                dct_new[ins_brand]['value'] = []
                                dct_new[ins_brand]['qty'].append(dct_data[ins_detail][ins_brand]['int_qty'])
                                dct_new[ins_brand]['value'].append(dct_data[ins_detail][ins_brand]['value'])
                            else:
                                dct_new[ins_brand]['qty'].append(dct_data[ins_detail][ins_brand]['int_qty'])
                                dct_new[ins_brand]['value'].append(dct_data[ins_detail][ins_brand]['value'])



            # import pdb; pdb.set_trace()
            brand_length = len(dct_new)
            dct_latest = {}
            dct_latest['PRICE RANGE'] = lst_price_range
            dct_latest['SL NO'] = list(range(1,len(lst_price_range)+1))
            lst_brand_index.append('SL NO')
            lst_brand_index.append("PRICE RANGE")
            for data in dct_new:
                lst_brand.append(data)
                lst_brand_index.append(data+' QUANTITY')
                lst_brand_index.append(data+' VALUE')
                dct_latest[data+' QUANTITY'] = dct_new[data]['qty']
                dct_latest[data+' VALUE'] = dct_new[data]['value']

            # import pdb; pdb.set_trace()
            #creating dataframes
            df_active = pd.DataFrame(dct_latest)
            df_active_order = df_active[lst_brand_index]

            df_active_order.index = df_active.index + 1

            #creating and writing to excel
            excel_file = '/brandcomparisonreport.xlsx'
            file_name_export = settings.MEDIA_ROOT + excel_file

            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_active_order.to_excel(writer,sheet_name='Sheet1',index=False, startrow=7,startcol=0)

            workbook = writer.book

            cell_format1=workbook.add_format()
            cell_format1.set_align('center')
            cell_format1.set_align('vcenter')
            cell_format1.set_locked(True)
            cell_format1.set_bold()

            cell_format3=workbook.add_format()
            cell_format3.set_align('right')
            cell_format3.set_locked(True)
            cell_format3.set_bold()

            cell_format2=workbook.add_format()
            cell_format2.set_align('center')
            cell_format2.set_align('vcenter')
            cell_format2.set_locked(True)

            worksheet1 = writer.sheets['Sheet1']
            worksheet1.merge_range('A1+:F1', 'BRAND COMPARISON REPORT',cell_format1)
            # worksheet1.write_string(1, 0, 'Filters:-',cell_format1)
            worksheet1.write_string(2, 0, 'Branch:- ')
            worksheet1.write_string(2, 1, branch)
            worksheet1.write_string(3, 0, 'Product:- ')
            worksheet1.write_string(3, 1, product)
            worksheet1.write_string(4, 0, "Date :-")
            worksheet1.write_string(4, 1, dat_from + " to " + dat_to )

            worksheet1.write_string(6, 1, "PRICE RANGE",cell_format1)
            worksheet1.write_string(6, 0, "SL NO",cell_format1)

            # import pdb; pdb.set_trace()

            column=2
            start = "C"
            end = "D"
            for ins_brand in lst_brand:
                worksheet1.merge_range(start+'7+:'+ end +'7', ins_brand ,cell_format1)
                start = chr(ord(start)+2)
                end = chr(ord(end)+2)
                worksheet1.write_string(7, column, "QUANTITY",cell_format2)
                worksheet1.write_string(7, column+1, "VALUE",cell_format2)
                column += 2
            worksheet1.write_string(7, 1, " ",cell_format1)
            worksheet1.write_string(7, 0, " ",cell_format1)
            worksheet1.protect()

            worksheet1.set_column(1,(brand_length*2)+1,16)


            writer.save()

            if request.data.get('email'):

                filename = file_name_export
                to = request.data.get('email')
                # to = "freddy.davis@travidux.in"
                subject =  'Brand Comparison Report'
                from_email = settings.EMAIL_HOST_EMAIL
                text_content = 'Travidux'
                html_content = '''Dear, '''
                email_sent(subject, text_content,from_email,to,html_content,filename)

                return Response({'status':'success'})

            return Response({'status':'success','data':request.scheme+'://'+request.get_host()+'/media'+excel_file})
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})



class PeriodComparisonReportExport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dct_data = request.data.get('dctData')
            branch = request.data.get('branch')
            product = request.data.get('product')
            brand = request.data.get('brand')
            dat_from1 = request.data.get('datFrom1')
            dat_from2 = request.data.get('datFrom2')
            dat_to1 = request.data.get('datTo1')
            dat_to2 = request.data.get('datTo2')

            lst_price_range = ['0-2000','2001-4000','4001-6000','6001-10000','10001-15000','15001-20000','20001-25000','25001-35000','35001-100000','100001-200000']
            lst_qty_growth = []
            lst_value_growth = []
            lst_period1_qty =[]
            lst_period1_value =[]
            lst_period2_qty =[]
            lst_period2_value =[]

            for ins_range in lst_price_range:
                for ins_detail in dct_data:
                    if ins_detail == ins_range:
                        lst_qty_growth.append(dct_data[ins_detail]['qty_growth'])
                        lst_value_growth.append(dct_data[ins_detail]['value_growth'])
                        lst_period1_qty.append(dct_data[ins_detail]['Period1']['qty'])
                        lst_period2_qty.append(dct_data[ins_detail]['Period2']['qty'])
                        lst_period1_value.append(dct_data[ins_detail]['Period1']['value'])
                        lst_period2_value.append(dct_data[ins_detail]['Period2']['value'])

            # import pdb; pdb.set_trace()
            #creating dataframes
            df_active = pd.DataFrame({
            'SL NO':list(range(1,len(lst_price_range)+1)),
            'PRICE RANGE' : lst_price_range,
            'QUANTITY' : lst_period1_qty,
            'VALUE' : lst_period1_value,
            'QUANTITY2' : lst_period2_qty,
            'VALUE2' : lst_period2_value,
            'QUANTITY GROWTH' : lst_qty_growth,
            'VALUE GROWTH' : lst_value_growth
            })
            df_active_order = df_active[['SL NO','PRICE RANGE','QUANTITY','VALUE','QUANTITY2','VALUE2','QUANTITY GROWTH','VALUE GROWTH']]

            df_active_order.index = df_active.index + 1

            #creating and writing to excel
            excel_file = '/periodcomparisonreport.xlsx'
            file_name_export = settings.MEDIA_ROOT + excel_file

            writer = pd.ExcelWriter(file_name_export,engine='xlsxwriter')
            df_active_order.to_excel(writer,sheet_name='Sheet1',index=False, startrow=8,startcol=0)

            workbook = writer.book

            cell_format1=workbook.add_format()
            cell_format1.set_align('center')
            cell_format1.set_align('vcenter')
            cell_format1.set_locked(True)
            cell_format1.set_bold()

            cell_format3=workbook.add_format()
            cell_format3.set_align('right')
            cell_format3.set_locked(True)
            cell_format3.set_bold()

            cell_format2=workbook.add_format()
            cell_format2.set_align('center')
            cell_format2.set_align('vcenter')
            cell_format2.set_locked(True)

            worksheet1 = writer.sheets['Sheet1']
            worksheet1.merge_range('A1+:H1', 'PRICE RANGE COMPARISON REPORT',cell_format1)
            # worksheet1.write_string(1, 0, 'Filters:-',cell_format1)
            worksheet1.write_string(1, 0, 'Branch:- ')
            worksheet1.write_string(1, 1, branch)
            worksheet1.write_string(2, 0, 'Product:- ')
            worksheet1.write_string(2, 1, product)
            worksheet1.write_string(3, 0, 'Brand:- ')
            worksheet1.write_string(3, 1, brand)
            worksheet1.write_string(4, 0, "Period 1:-")
            worksheet1.merge_range('B5+:C5', dat_from1 + " to " + dat_to1 )
            worksheet1.write_string(5, 0, "Period 2:-")
            worksheet1.merge_range('B6+:C6', dat_from2 + " to " + dat_to2 )

            worksheet1.write_string(7, 1, "PRICE RANGE",cell_format1)
            worksheet1.write_string(7, 0, "SL NO",cell_format1)
            worksheet1.write_string(8, 1, " ",cell_format1)
            worksheet1.merge_range('C8+:D8', "PERIOD 1",cell_format1)
            worksheet1.write_string(8, 2, "Qty",cell_format2)
            worksheet1.write_string(8, 3, "value",cell_format2)
            worksheet1.merge_range('E8+:F8', "PERIOD 2",cell_format1)
            worksheet1.write_string(8, 4, "Qty",cell_format2)
            worksheet1.write_string(8, 5, "value",cell_format2)
            worksheet1.write_string(7, 6, "QUANTITY GROWTH",cell_format1)
            worksheet1.write_string(8, 6, " ",cell_format1)
            worksheet1.write_string(7, 7, "VALUE GROWTH",cell_format1)
            worksheet1.write_string(8, 7, " ",cell_format1)
            worksheet1.write_string(8, 0, " ",cell_format1)


            worksheet1.protect()

            worksheet1.set_column(1,1,18)
            worksheet1.set_column(2,5,10)
            worksheet1.set_column(6,7,23)


            writer.save()

            if request.data.get('email'):

                filename = file_name_export
                to = request.data.get('email')
                # to = "freddy.davis@travidux.in"
                subject =  'Price Range Comparison Report'
                from_email = settings.EMAIL_HOST_EMAIL
                text_content = 'Travidux'
                html_content = '''Dear, '''
                email_sent(subject, text_content,from_email,to,html_content,filename)

                return Response({'status':'success'})

            return Response({'status':'success','data':request.scheme+'://'+request.get_host()+'/media'+excel_file})
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})

# class PriceBandItemWise(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_from =  request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            engine = get_engine()
            conn = engine.connect()
            session = Session()
            int_brand_id = request.data.get("brandId")
            int_product_id = request.data.get("productId")
            dict_area =request.data.get("dctArea")

            """date filter"""
            str_filter = "AND dat_enquiry :: DATE BETWEEN '"+dat_from+"' AND '"+dat_to+"'"

            if int_product_id:
                str_filter += " AND product_id = '"+ str(int_product_id)+"'"

            if int_brand_id :
                str_filter += " AND brand_id = '"+ str(int_brand_id)+"'"


            str_query_set = "select (dbl_value/int_qty),vchr_item_name,branch_name,branch_id,territory_name,territory_id,zone_name,zone_id,vchr_product_name,vchr_brand_name,int_qty,dbl_value,CASE when (dbl_value/int_qty) between 0 and 2000 then '0-2000' when (dbl_value/int_qty) between 2001 and 4000 then '2001-4000' when (dbl_value/int_qty) between 4001 and 6000 then '4001-6000' when (dbl_value/int_qty) between 6001 and 10000 then '6001-10000' when (dbl_value/int_qty) between 10001 and 15000 then '10001-15000' when (dbl_value/int_qty) between 15001 and 20000 then '15000-20000' when (dbl_value/int_qty) between 20001 and 25000 then '20001-25000' when (dbl_value/int_qty) between 25001 and 35000 then '25001-35000' when (dbl_value/int_qty) between 35001 and 100000 then '35001-100000' when (dbl_value/int_qty) between 100001 and 200000 then '100001-200000' END as range from (select vchr_item_name,branch_name,branch_id,territory_name,territory_id,zone_name,zone_id,vchr_product_name,vchr_brand_name,sum(int_quantity) as int_qty ,sum(total_amount) as dbl_value from mv_enquiry_data where vchr_enquiry_status = 'INVOICED'  {str_filter}group by vchr_item_name,zone_name,zone_id,vchr_product_name,vchr_brand_name,branch_name,branch_id,territory_name,territory_id) as price_range order by 1,vchr_brand_name"

            str_query_set = str_query_set.format(str_filter = str_filter)
            rst_enquiry = conn.execute(str_query_set).fetchall()

            # import pdb; pdb.set_trace()
            if not rst_enquiry:
                session.close()
                return Response({'status':'failed','reason':'No Data'})

            dct_data = {}
            lst_data = []
            if dict_area["area"] == "ZONE":
                for ins_data in rst_enquiry:

                    if dict_area.get("id") and dict_area.get("id") == ins_data.zone_id:
                        if ins_data.zone_name not in dct_data:
                            dct_data[ins_data.zone_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["zone_id"] = ins_data.zone_id
                        dct_item["zone_name"] = ins_data.zone_name
                        dct_item["territory_name"] = ins_data.territory_name
                        dct_item["territory_id"] = ins_data.territory_id

                        dct_data[ins_data.zone_name].append(dct_item)

                    elif not dict_area.get("id"):
                        if ins_data.zone_name not in dct_data:
                            dct_data[ins_data.zone_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["zone_id"] = ins_data.zone_id
                        dct_item["zone_name"] = ins_data.zone_name
                        dct_data[ins_data.zone_name].append(dct_item)

            if dict_area["area"] == "TERRITORY":
                for ins_data in rst_enquiry:

                    if dict_area.get("id") and dict_area.get("id") == ins_data.territory_id:
                        if ins_data.territory_name not in dct_data:
                            dct_data[ins_data.territory_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_territory_name"] = ins_data.territory_name
                        dct_item["int_territory_id"] = ins_data.territory_id
                        dct_item["vchr_branch_name"] = ins_data.branch_name
                        dct_item["int_branch_id"] = ins_data.branch_id


                        dct_data[ins_data.territory_name].append(dct_item)

                    elif not dict_area.get("id"):
                        if ins_data.territory_name not in dct_data:
                            dct_data[ins_data.territory_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_territory_name"] = ins_data.territory_name
                        dct_item["int_territory_id"] = ins_data.territory_id
                        dct_data[ins_data.territory_name].append(dct_item)

            if dict_area["area"] == "BRANCH":
                for ins_data in rst_enquiry:

                    if dict_area.get("id") and dict_area.get("id") == ins_data.branch_id:
                        if ins_data.branch_name not in dct_data:
                            dct_data[ins_data.branch_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_branch_name"] = ins_data.branch_name
                        dct_item["int_branch_id"] = ins_data.branch_id


                        dct_data[ins_data.branch_name].append(dct_item)

                    elif not dict_area.get("id"):
                        if ins_data.branch_name not in dct_data:
                            dct_data[ins_data.branch_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_territory_name"] = ins_data.territory_name
                        dct_item["int_territory_id"] = ins_data.territory_id
                        dct_item["vchr_branch_name"] = ins_data.branch_name
                        dct_item["int_branch_id"] = ins_data.branch_id

                        dct_data[ins_data.branch_name].append(dct_item)



            session.close()
            return Response({'status':'success','dct_data':dct_data})
        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})




class PriceBandItemWise(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_from =  request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            engine = get_engine()
            conn = engine.connect()
            session = Session()
            int_brand_id = request.data.get("brandId")
            int_product_id = request.data.get("productId")
            dict_area =request.data.get("dctArea")
            # dat_from = '2019-01-01'
            # dat_to = '2019-07-01'
            # dict_area = {"area":"ZONE","id":None}



            """date filter"""
            str_filter = "WHERE dat_sale :: DATE BETWEEN '"+dat_from+"' AND '"+dat_to+"'"

            if int_product_id:
                str_filter += " AND products.id = '"+ str(int_product_id)+"'"

            if int_brand_id :
                str_filter += " AND brands.id = '"+ str(int_brand_id)+"'"

            str_query_set = "select  dat_sale,items.vchr_item_name,brands.vchr_brand_name as vchr_brand_name,branch.pk_bint_id as int_branch_id,branch.vchr_name as vchr_branch_name,territory.pk_bint_id as int_territory_id,territory.vchr_name as vchr_territory_name,zone.pk_bint_id as int_zone_id,zone.vchr_name as vchr_zone_name,products.vchr_product_name as vchr_product_name,sum(int_qty) as int_qty,sum(dbl_net_amount) as dbl_value ,CASE when dbl_price_range between 0 and 2000 then '0-2000' when dbl_price_range between 2001 and 4000 then '2001-4000' when dbl_price_range between 4001 and 6000 then '4001-6000' when dbl_price_range between 6001 and 10000 then '6001-10000' when dbl_price_range between 10001 and 15000 then '10001-15000' when dbl_price_range between 15001 and 20000 then '15001-20000' when dbl_price_range between 20001 and 25000 then '20001-25000' when dbl_price_range between 25001 and 35000 then '25001-35000' when dbl_price_range between 35001 and 100000 then '35001-100000' when dbl_price_range between 100001 and 200000 then '100001-200000' END AS range from branch_item_sale INNER JOIN branch ON branch_item_sale.fk_branch_id = branch.pk_bint_id INNER JOIN territory ON branch.fk_territory_id = territory.pk_bint_id INNER JOIN zone ON  territory.fk_zone_id = zone.pk_bint_id INNER JOIN items ON branch_item_sale.fk_item_id = items.id INNER JOIN brands on items.fk_brand_id = brands.id INNER JOIN products on items.fk_product_id = products.id {str_filter} group by vchr_item_name,vchr_brand_name,vchr_product_name,vchr_branch_name,vchr_territory_name,vchr_zone_name,int_branch_id,int_territory_id,int_zone_id,dat_sale,range order by range,dat_sale,vchr_brand_name ;"

            # import pdb; pdb.set_trace()




            str_query_set = str_query_set.format(str_filter = str_filter)
            rst_enquiry = conn.execute(str_query_set).fetchall()

            if not rst_enquiry:
                session.close()
                return Response({'status':'failed','reason':'No Data'})

            dct_data = {}
            lst_data = []
            if dict_area["area"] == "ZONE":
                for ins_data in rst_enquiry:

                    if dict_area.get("id") and dict_area.get("id") == ins_data.int_zone_id:
                        if ins_data.vchr_zone_name not in dct_data:
                            dct_data[ins_data.vchr_zone_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["zone_id"] = ins_data.int_zone_id
                        dct_item["zone_name"] = ins_data.vchr_zone_name
                        dct_item["vchr_territory_name"] = ins_data.vchr_territory_name
                        dct_item["int_territory_id"] = ins_data.int_territory_id
                        dct_item["dat_sale"] = datetime.strftime(ins_data.dat_sale,"%d-%m-%Y")

                        dct_data[ins_data.vchr_zone_name].append(dct_item)

                    elif not dict_area.get("id"):
                        if ins_data.vchr_zone_name not in dct_data:
                            dct_data[ins_data.vchr_zone_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["zone_id"] = ins_data.int_zone_id
                        dct_item["zone_name"] = ins_data.vchr_zone_name
                        dct_data[ins_data.vchr_zone_name].append(dct_item)
                        dct_item["dat_sale"] = datetime.strftime(ins_data.dat_sale,"%d-%m-%Y")
            if dict_area["area"] == "TERRITORY":
                for ins_data in rst_enquiry:

                    if dict_area.get("id") and dict_area.get("id") == ins_data.int_territory_id:
                        if ins_data.vchr_territory_name not in dct_data:
                            dct_data[ins_data.vchr_territory_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_territory_name"] = ins_data.vchr_territory_name
                        dct_item["int_territory_id"] = ins_data.int_territory_id
                        dct_item["vchr_branch_name"] = ins_data.vchr_branch_name
                        dct_item["int_branch_id"] = ins_data.int_branch_id
                        dct_item["dat_sale"] = datetime.strftime(ins_data.dat_sale,"%d-%m-%Y")

                        dct_data[ins_data.vchr_territory_name].append(dct_item)

                    elif not dict_area.get("id"):
                        if ins_data.vchr_territory_name not in dct_data:
                            dct_data[ins_data.vchr_territory_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_territory_name"] = ins_data.vchr_territory_name
                        dct_item["int_territory_id"] = ins_data.int_territory_id
                        dct_data[ins_data.vchr_territory_name].append(dct_item)
                        dct_item["dat_sale"] = datetime.strftime(ins_data.dat_sale,"%d-%m-%Y")
            if dict_area["area"] == "BRANCH":
                for ins_data in rst_enquiry:

                    if dict_area.get("id") and dict_area.get("id") == ins_data.int_branch_id:
                        if ins_data.vchr_branch_name not in dct_data:
                            dct_data[ins_data.vchr_branch_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_branch_name"] = ins_data.vchr_branch_name
                        dct_item["int_branch_id"] = ins_data.int_branch_id
                        dct_item["dat_sale"] = datetime.strftime(ins_data.dat_sale,"%d-%m-%Y")

                        dct_data[ins_data.vchr_branch_name].append(dct_item)

                    elif not dict_area.get("id"):
                        if ins_data.vchr_branch_name not in dct_data:
                            dct_data[ins_data.vchr_branch_name] = []

                        dct_item = {}
                        dct_item["vchr_brand_name"] = ins_data.vchr_brand_name
                        dct_item["vchr_product_name"] = ins_data.vchr_product_name
                        dct_item["vchr_item_name"] = ins_data.vchr_item_name
                        dct_item["int_qty"] = ins_data.int_qty
                        dct_item["dbl_value"] = ins_data.dbl_value
                        dct_item["range"] = ins_data.range
                        dct_item["vchr_territory_name"] = ins_data.vchr_territory_name
                        dct_item["int_territory_id"] = ins_data.int_territory_id
                        dct_item["vchr_branch_name"] = ins_data.vchr_branch_name
                        dct_item["int_branch_id"] = ins_data.int_branch_id
                        dct_item["dat_sale"] = datetime.strftime(ins_data.dat_sale,"%d-%m-%Y")
                        dct_data[ins_data.vchr_branch_name].append(dct_item)



            session.close()
            return Response({'status':'success','dct_data':dct_data})
        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})

"""structuring for product report"""
def structure_data_for_report_new(request,rst_enquiry):
    try:
        # import pdb; pdb.set_trace()
        dct_data={}
        dct_data['STAFFS']={}
        dct_data['IN_IT'] = {}

        if request.data['type'] == 'Sale':
            dct_data['SERVICE_BRAND_ITEM_STAFF']={}

        elif request.data['type'] == 'Enquiry':
            dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS']={}

        for ins_data in rst_enquiry:
            """sales -> product report """
            if request.data['type'] == 'Sale':
                if ins_data.vchr_service not in dct_data['SERVICE_BRAND_ITEM_STAFF']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS']={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS']={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=ins_data.value


                elif ins_data.vchr_brand_name.title() not in dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryValue'] += ins_data.value


                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value


                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS']={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value


                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=ins_data.value

                elif ins_data.vchr_item_name.title() not in dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS']={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue']=ins_data.value


                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=ins_data.value

                elif ins_data.fk_assigned not in dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]={}
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']=ins_data.value

                else:
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty']+=ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue']+=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']+=ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']+=ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']+=ins_data.value



            elif request.data['type'] == 'Enquiry':
                """enquiry -> product report"""
                if ins_data.vchr_service not in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale']  =  0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale']  =  0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale']  =  0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']  =  0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]  =  {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value



                elif ins_data.vchr_brand_name.title() not in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryValue']+= ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale']  =  0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale']  =  0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_item_name.title() not in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryValue']+= ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue']=0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                elif ins_data.fk_assigned not in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryValue']+= ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty']= 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue'] = ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] = ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_enquiry_status not in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS']:

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryValue']+= ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status] = {}
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = 0
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] = ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] = ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] = ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] = ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] = ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] = ins_data.value

                else:

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['EnquiryValue']+= ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['EnquiryValue'] += ins_data.value

                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Enquiry'] += ins_data.counts
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryQty'] += ins_data.qty
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['EnquiryValue'] += ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['SaleValue'] += ins_data.value

                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['Sale'] += ins_data.counts
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleQty'] += ins_data.qty
                        dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][ins_data.vchr_service]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name.title()]['STAFFS'][ins_data.fk_assigned]['STATUS'][ins_data.vchr_enquiry_status]['SaleValue'] += ins_data.value

            """staff id : staff name"""
            if ins_data.fk_assigned not in dct_data['STAFFS']:
                dct_data['STAFFS'][ins_data.fk_assigned]=str(ins_data.branch_code+"-"+ins_data.staff_first_name+" "+ins_data.staff_last_name).title()

            # import pdb; pdb.set_trace()
        if request.data['type'] == 'Sale':

            """top 5 product->brand->item->staff"""
            dct_data['IN_IT']['PRODUCTS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF'][i]['Sale']),reverse =True)[0]
            top_product = dct_data['IN_IT']['PRODUCTS']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF'][top_product]['BRANDS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF'][top_product]['BRANDS'][i]['Sale']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEMS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF'][top_product]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF'][top_product]['BRANDS'][top_brand]['ITEMS'][i]['Sale']),reverse =True)[0]
            top_item = dct_data['IN_IT']['ITEMS']
            dct_data['IN_IT']['STAFF'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STAFFS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STAFFS'][i]['Sale']),reverse =True)[0]

            """paginating"""
            for key in dct_data['SERVICE_BRAND_ITEM_STAFF']:
                for key1 in dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS']:
                    for key2 in dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'][key1]['ITEMS']:
                        dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS']=paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS'],10)

            for key in dct_data['SERVICE_BRAND_ITEM_STAFF']:
                for key1 in dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS']:
                    dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'][key1]['ITEMS']=paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'][key1]['ITEMS'],10)

            for key in dct_data['SERVICE_BRAND_ITEM_STAFF']:
                dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'] = paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF'][key]['BRANDS'],10)

            dct_data['SERVICE_BRAND_ITEM_STAFF'] = paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF'],10)


        elif request.data['type'] == 'Enquiry':

            """top 5 product->brand->item->staff->status"""
            dct_data['IN_IT']['PRODUCTS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][i]['Enquiry']),reverse =True)[0]
            top_product = dct_data['IN_IT']['PRODUCTS']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][i]['Enquiry']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEMS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][top_brand]['ITEMS'][i]['Enquiry']),reverse =True)[0]
            top_item = dct_data['IN_IT']['ITEMS']
            dct_data['IN_IT']['STAFF'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STAFFS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STAFFS'][i]['Enquiry']),reverse =True)[0]
            top_staff = dct_data['IN_IT']['STAFF']
            dct_data['IN_IT']['STATUS'] = sorted(dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STAFFS'][top_staff]['STATUS'], key = lambda i: (dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STAFFS'][top_staff]['STATUS'][i]['Enquiry']),reverse =True)[0]

            """paginating"""
            # for key in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS']:
            #     for key1 in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS']:
            #         for key2 in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS']:
            #             for key3 in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS']:
            #                 dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS'][key3]['STATUS']=paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS'][key3]['STATUS'],10)
            #
            # for key in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS']:
            #     for key1 in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS']:
            #         for key2 in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS']:
            #             dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS']=paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS'][key2]['STAFFS'],10)

            for key in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS']:
                for key1 in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS']:
                    dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS']=paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'][key1]['ITEMS'],10)

            for key in dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS']:
                dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'] = paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'][key]['BRANDS'],10)

            dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'] = paginate_data(request,dct_data['SERVICE_BRAND_ITEM_STAFF_STATUS'],10)





        return dct_data
    except Exception as msg:
        return str(msg)






def structure_data_for_report_old(request,rst_enquiry):
        try:
            # import pdb; pdb.set_trace()
            # session=Session()

            # rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
            # rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
            # rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
            # rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
            #
            # rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
            # rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service.label('vchr_service'),rst_data.c.brand_id.label('brand_id'), CustomerSA.cust_fname.label('customer_first_name'),\
            #                 CustomerSA.cust_lname.label('customer_last_name'),rst_data.c.vchr_enquiry_status,CustomerSA.cust_mobile.label('customer_mobile'),AuthUserSA.id.label('user_id'),AuthUserSA.first_name.label('staff_first_name'),\
            #                 AuthUserSA.last_name.label('staff_last_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name)\
            #                 .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == request.data['company_id'],EnquiryMasterSA.chr_doc_status == 'N')\
            #                 .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id))\
            #                 .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
            #                 .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
            #                 .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).join(UserSA, AuthUserSA.id == UserSA.user_ptr_id)\
            #                 .join(BrandsSA,BrandsSA.id==rst_data.c.brand_id)\
            #                 .join(ItemsSA,ItemsSA.id==rst_data.c.item_id)

            # rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status,func.count(ProductSA.vchr_product_name).label('counts'),
            #                     ProductSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
            #                     AuthUserSA.last_name).label('vchr_staff_full_name'),
            #                     EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),
            #                     AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
            #                     AuthUserSA.first_name.label('staff_first_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
            #                     UserSA.fk_brand_id,UserSA.dat_resignation_applied,
            #                     # case([(UserSA.fk_brand_id > 0,literal_column("'promoter'"))],
            #                     #     else_=literal_column("'not promoter'")).label('is_promoter'),
            #                     case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
            #                         else_=literal_column("'not resigned'")).label("is_resigned"))\
            #                     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
            #                             cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
            #                             EnquiryMasterSA.fk_company_id == request.user.userdetails.fk_company_id,
            #                             EnquiryMasterSA.chr_doc_status == 'N')\
            #                     .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
            #                     .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
            #                     .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
            #                     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
            #                     .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
            #                     .join(ProductSA,ProductSA.id == ItemEnquirySA.fk_product_id)\
            #                     .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
            #                     .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)\
            #                     .group_by(ProductSA.vchr_product_name,BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
            #                               ItemEnquirySA.vchr_enquiry_status,AuthUserSA.id,EnquiryMasterSA.fk_assigned_id,
            #                               UserSA.fk_brand_id,UserSA.dat_resignation_applied)

            # """Permission wise filter for data"""
            # # rst_enquiry = get_perm_data_orm(rst_enquiry,request.user)
            # if request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})

            # """Permission wise filter for data"""
            # if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
            #     pass
            # elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            # elif request.user.userdetails.int_area_id:
            #     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            # else:
            #     return Response({'status':'failed','reason':'No data'})
            #
            # if request.data.get('branch'):
            #     branch = request.data.get('branch')
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == branch)
            # if request.data.get('staff'):
            #     staff = request.data.get('staff')
            #     rst_enquiry = rst_enquiry.filter(AuthUserSA.id == staff)
            # if request.data.get('product'):
            #     rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_product_id == request.data.get('product'))
            # if request.data.get('brand'):
            #     rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_brand_id == request.data.get('brand'))

            dct_data={}
            dct_data['service_all']={}
            dct_data['brand_all']={}
            dct_data['item_all']={}
            dct_data['staff_all']={}
            dct_data['status_all']={}
            dct_data['service_brand']={}
            dct_data['service_item']={}
            dct_data['service_staff']={}
            dct_data['service_status']={}
            dct_data['service_brand_item']={}
            dct_data['service_brand_staff']={}
            dct_data['service_brand_status']={}
            dct_data['service_brand_item_staff']={}
            dct_data['service_brand_item_status']={}
            dct_data['service_brand_item_staff_status']={}
            dct_data['staffs']={}

            for ins_data in rst_enquiry:
                # ins_data._asdict()['vchr_brand_name'] = ins_data.vchr_brand_name.title()
                # dct_temp = {
                #     'fk_customer__cust_lname': ins_data.fk_customer__cust_lname,'fk_customer__cust_mobile': ins_data.fk_customer__cust_mobile,
                #     'fk_assigned__last_name': ins_data.fk_assigned__last_name,'vchr_created_at': ins_data.dat_created_at.strftime('%d-%m-%Y'),
                #     'vchr_staff_full_name': ins_data.fk_assigned__first_name + ' ' + ins_data.fk_assigned__last_name,
                #     'vchr_enquiry_status': ins_data.vchr_enquiry_status,'vchr_service': ins_data.vchr_service,
                #     'vchr_mobile_num': ins_data.fk_customer__cust_mobile,'vchr_enquiry_num': ins_data.vchr_enquiry_num,
                #     'fk_assigned__first_name': ins_data.fk_assigned__first_name,'dat_created_at': ins_data.dat_created_at,
                #     'fk_customer__cust_fname': ins_data.fk_customer__cust_fname,'vchr_enquiry_source': ins_data.vchr_enquiry_source,
                #     'vchr_enquiry_priority': ins_data.vchr_enquiry_priority,
                #     'vchr_full_name': ins_data.fk_customer__cust_fname + ' ' + ins_data.fk_customer__cust_lname,'pk_bint_id': ins_data.pk_bint_id,
                #     'product':ins_data.vchr_service,
                #     'brand':ins_data.vchr_brand_name,
                #     'item':ins_data.vchr_item_name
                #             }
                # lst_table_data.append( dct_temp.copy())
                # ins_data=ins_data._asdict()
                if ins_data.vchr_service not in dct_data['service_all']:
                    dct_data['service_all'][ins_data.vchr_service]={}
                    dct_data['service_all'][ins_data.vchr_service]['Enquiry']=ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service]['Sale']=0
                    dct_data['service_all'][ins_data.vchr_service]['EnquiryQty']=ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service]['EnquiryValue']=ins_data.value
                    dct_data['service_all'][ins_data.vchr_service]['SaleQty']=0
                    dct_data['service_all'][ins_data.vchr_service]['SaleValue']=0

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['service_all'][ins_data.vchr_service]['Sale']=ins_data.counts
                        dct_data['service_all'][ins_data.vchr_service]['SaleQty']=ins_data.qty
                        dct_data['service_all'][ins_data.vchr_service]['SaleValue']=ins_data.value

                    dct_data['service_brand'][ins_data.vchr_service]={}
                    dct_data['service_item'][ins_data.vchr_service]={}
                    dct_data['service_staff'][ins_data.vchr_service]={}
                    dct_data['service_status'][ins_data.vchr_service]={}
                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]={}
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value

                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue']=0
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']=0
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=0

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleValue']=ins_data.value
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value


                    dct_data['service_brand_item'][ins_data.vchr_service]={}
                    dct_data['service_brand_staff'][ins_data.vchr_service]={}
                    dct_data['service_brand_status'][ins_data.vchr_service]={}
                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}

                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]= {}
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]= {}

                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=0
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0

                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value


                    dct_data['service_brand_item_staff'][ins_data.vchr_service]={}
                    dct_data['service_brand_item_status'][ins_data.vchr_service]={}
                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}

                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned] = {}
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]= {}


                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=0
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0

                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value


                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value

                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service]={}
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status] = {}
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=0

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value

                else:
                    dct_data['service_all'][ins_data.vchr_service]['Enquiry']+=ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service]['EnquiryQty']+=ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service]['EnquiryValue']+=ins_data.value

                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['service_all'][ins_data.vchr_service]['Sale'] += ins_data.counts
                        dct_data['service_all'][ins_data.vchr_service]['SaleQty'] += ins_data.qty
                        dct_data['service_all'][ins_data.vchr_service]['SaleValue'] += ins_data.value


                    if ins_data.vchr_brand_name.title() not in dct_data['service_brand'][ins_data.vchr_service]:
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()] = {}
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']= ins_data.counts
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty']= ins_data.qty
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue']= ins_data.value
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']= 0
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']= 0
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']= 0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']= ins_data.counts
                            dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty']= ins_data.qty
                            dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue']= ins_data.value
                    else:
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                            dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                            dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                    if ins_data.vchr_item_name.title() not in dct_data['service_item'][ins_data.vchr_service]:
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()] = {}
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty'] = ins_data.qty
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue'] = ins_data.value
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 0
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty'] = 0
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue'] = 0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
                            dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty'] = ins_data.qty
                            dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue'] = ins_data.value
                    else:
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryQty'] += ins_data.qty
                        dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['EnquiryValue'] += ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                            dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                            dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value

                    if ins_data.fk_assigned not in dct_data['service_staff'][ins_data.vchr_service]:
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned] = {}
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Enquiry'] = ins_data.counts
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['EnquiryQty'] = ins_data.qty
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['EnquiryValue'] = ins_data.value
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']= 0
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleQty']= 0
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleValue']= 0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']= ins_data.counts
                            dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleQty']= ins_data.qty
                            dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleValue']= ins_data.value
                    else:
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Enquiry'] += ins_data.counts
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['EnquiryQty'] += ins_data.qty
                        dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['EnquiryValue'] += ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']+=ins_data.counts
                            dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleQty']+=ins_data.qty
                            dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['SaleValue']+=ins_data.value

                    if ins_data.vchr_enquiry_status not in dct_data['service_status'][ins_data.vchr_service]:
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                    else:
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                        dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                            dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                            dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value

                    if ins_data.vchr_brand_name.title() not in dct_data['service_brand_item'][ins_data.vchr_service]:
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}

                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]={}
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}

                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value

                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=0
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']=0
                        dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']=0
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                    else:
                        if ins_data.vchr_item_name.title() not in dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                                dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                                dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        else:
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                            dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                                dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                                dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value

                        if ins_data.fk_assigned not in dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]={}
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=0
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']=0
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']=0
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                                dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                                dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                        else:
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryQty']+=ins_data.qty
                            dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['EnquiryValue']+=ins_data.value
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']+=ins_data.counts
                                dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleQty']+=ins_data.qty
                                dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['SaleValue']+=ins_data.value

                        if ins_data.vchr_enquiry_status not in dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                                dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                                dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                        else:
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                            dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                                dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                                dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value
                    if ins_data.vchr_brand_name.title() not in dct_data['service_brand_item_staff'][ins_data.vchr_service]:
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=0
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=0
                        dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value

                    else:
                        if ins_data.vchr_item_name.title() not in dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=0
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                            dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=0
                            dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                            if ins_data.vchr_enquiry_status == 'INVOICED':
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                        else:
                            if ins_data.fk_assigned not in dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=0
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=0
                                if ins_data.vchr_enquiry_status == 'INVOICED':
                                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
                                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']=ins_data.value
                            else:
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryQty']+=ins_data.qty
                                dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['EnquiryValue']+=ins_data.value
                                if ins_data.vchr_enquiry_status == 'INVOICED':
                                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']+=ins_data.counts
                                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleQty']+=ins_data.qty
                                    dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['SaleValue']+=ins_data.value

                            if ins_data.vchr_enquiry_status not in dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=0
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=0
                                if ins_data.vchr_enquiry_status == 'INVOICED':
                                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                            else:
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                                dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                                if ins_data.vchr_enquiry_status == 'INVOICED':
                                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                                    dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value

                    if ins_data.vchr_brand_name.title() not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service]:
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                    elif ins_data.vchr_item_name.title() not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value

                    elif ins_data.fk_assigned not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title().title()][ins_data.fk_assigned]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value

                    elif ins_data.vchr_enquiry_status not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]:
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=0
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value

                    else:
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                        dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                            dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value
                if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value

                else:
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value

                if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                    dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']=0
                    if ins_data.vchr_enquiry_status =='INVOICED':
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                if ins_data.fk_assigned not in dct_data['staff_all']:
                    dct_data['staffs'][ins_data.fk_assigned]=str(ins_data.branch_code+"-"+ins_data.staff_first_name+" "+ins_data.staff_last_name).title()
                    dct_data['staff_all'][ins_data.fk_assigned]={}
                    dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
                    dct_data['staff_all'][ins_data.fk_assigned]['EnquiryQty']=ins_data.qty
                    dct_data['staff_all'][ins_data.fk_assigned]['EnquiryValue']=ins_data.value
                    dct_data['staff_all'][ins_data.fk_assigned]['Sale']=0
                    dct_data['staff_all'][ins_data.fk_assigned]['SaleQty']=0
                    dct_data['staff_all'][ins_data.fk_assigned]['SaleValue']=0
                    if ins_data.vchr_enquiry_status =='INVOICED':
                        dct_data['staff_all'][ins_data.fk_assigned]['Sale']=ins_data.counts
                        dct_data['staff_all'][ins_data.fk_assigned]['SaleQty']=ins_data.qty
                        dct_data['staff_all'][ins_data.fk_assigned]['SaleValue']=ins_data.value
                else:
                    dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
                    dct_data['staff_all'][ins_data.fk_assigned]['EnquiryQty']+=ins_data.qty
                    dct_data['staff_all'][ins_data.fk_assigned]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['staff_all'][ins_data.fk_assigned]['Sale']+=ins_data.counts
                        dct_data['staff_all'][ins_data.fk_assigned]['SaleQty']+=ins_data.qty
                        dct_data['staff_all'][ins_data.fk_assigned]['SaleValue']+=ins_data.value
                if ins_data.vchr_enquiry_status not in dct_data['status_all']:
                    dct_data['status_all'][ins_data.vchr_enquiry_status]={}
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryQty']=ins_data.qty
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryValue']=ins_data.value
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleQty']=0
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleValue']=0
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleQty']=ins_data.qty
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleValue']=ins_data.value
                else:
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryQty']+=ins_data.qty
                    dct_data['status_all'][ins_data.vchr_enquiry_status]['EnquiryValue']+=ins_data.value
                    if ins_data.vchr_enquiry_status == 'INVOICED':
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleQty']+=ins_data.qty
                        dct_data['status_all'][ins_data.vchr_enquiry_status]['SaleValue']+=ins_data.value

            # # ------------------------------------------------------------------
            # if request.data.get('show_table') and request.data.get('type')=='Enquiry':
            #     from table_data import TableData
            #     return Response({'status':'success','table_data':TableData(request,dct_data)})
            #
            # if request.data.get('show_table'):
            #     dct_temp_data=dct_data
            #     table_key = request.data.get('show_table')
            #     str_key = str(*(table_key.keys()))
            #     lst_value = table_key[str_key]
            #     if len(lst_value)==1 and str_key in lst_value:
            #         dct_data=dct_data[str_key]
            #     else:
            #         dct_data=dct_data[str_key]
            #         for key in lst_value:
            #             dct_data=dct_data[key]
            #     lst_table_data = []
            #     enq_total = 0
            #     if request.data.get('type'):
            #         type = request.data.get('type')
            #     else:
            #         type = 'Enquiry'
            #     for data in dct_data:
            #         enq_total += dct_data[data][type]
            #     for data in dct_data:
            #         dct_table_data={}
            #         dct_table_data = dct_data[data]
            #         if str_key == 'staff_all':
            #             dct_table_data['Name'] = dct_temp_data['staffs'][data]
            #         else:
            #             dct_table_data['Name'] = data
            #         dct_table_data['Contrib_per'] = round(dct_data[data][type]/enq_total*100,2)
            #         if type=='Sale' or type=='Sales':
            #             dct_table_data['Conversion_per'] = round(dct_data[data][type]/dct_data[data]['Enquiry']*100,2)
            #         lst_table_data.append(dct_table_data)
            #     return Response({'status':'success','table_data':lst_table_data})
            # # ------------------------------------------------------------------

            # import pdb; pdb.set_trace()
            if request.data['type'] == 'Sale':
                dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
                dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
                dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
                dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)
                for key in dct_data['service_brand']:
                        dct_data['service_brand'][key]=paginate_data(request,dct_data['service_brand'][key],10)
                for key in dct_data['service_item']:
                        dct_data['service_item'][key]=paginate_data(request,dct_data['service_item'][key],10)
                for key in dct_data['service_staff']:
                        dct_data['service_staff'][key]=paginate_data(request,dct_data['service_staff'][key],10)
                for key in dct_data['service_brand_item']:
                    for key1 in dct_data['service_brand_item'][key]:
                        dct_data['service_brand_item'][key][key1]=paginate_data(request,dct_data['service_brand_item'][key][key1],10)
                for key in dct_data['service_brand_staff']:
                    for key1 in dct_data['service_brand_staff'][key]:
                        dct_data['service_brand_staff'][key][key1]=paginate_data(request,dct_data['service_brand_staff'][key][key1],10)
                for key in dct_data['service_brand_item_staff']:
                    for key1 in dct_data['service_brand_item_staff'][key]:
                        for key2 in dct_data['service_brand_item_staff'][key][key1]:
                            dct_data['service_brand_item_staff'][key][key1][key2]=paginate_data(request,dct_data['service_brand_item_staff'][key][key1][key2],10)
            elif request.data['type'] == 'Enquiry':
                dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
                dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
                dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
                for key in dct_data['service_brand']:
                        dct_data['service_brand'][key]=paginate_data(request,dct_data['service_brand'][key],10)
                for key in dct_data['service_item']:
                        dct_data['service_item'][key]=paginate_data(request,dct_data['service_item'][key],10)
                for key in dct_data['service_brand_item']:
                    for key1 in dct_data['service_brand_item'][key]:
                        dct_data['service_brand_item'][key][key1]=paginate_data(request,dct_data['service_brand_item'][key][key1],10)
            # import pdb; pdb.set_trace()
            return dct_data
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})


class ServiceProfitReport(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            # import pdb; pdb.set_trace()
            lst_zones = list(Zone.objects.filter(chr_status = 'N').values('vchr_name','pk_bint_id'))
            lst_territory = list(Territory.objects.filter(chr_status = 'N').values('vchr_name','pk_bint_id'))
            lst_branch = list(Branch.objects.values('vchr_name','pk_bint_id'))

            dct_filter = {}
            dct_filter['lst_zones'] = lst_zones
            dct_filter['lst_territory'] = lst_territory
            dct_filter['lst_branch'] = lst_branch

            return Response({'status':'success' ,'dct_filter' : dct_filter})
        except Exception as e:
            return Response({'status':0,'reason' : str(e)})

    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            session = Session()

            dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d')
            dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d')
            vchr_filter_area = request.data.get('areaChoosen')
            lst_filter = request.data.get('filterIds')

            # rst_profit_report = session.query(JobMasterSA.fk_branch_id.label('branch_id'),\
            #                                 func.sum(func.coalesce(ItemServiceSA.dbl_est_amt,0)- func.coalesce(ItemServiceSA.dbl_tax,0)).label('service_charge'),\
            #                                 func.sum(func.coalesce(JobSpareDetailsSA.dbl_amount,0) - func.coalesce(JobSpareDetailsSA.dbl_tax,0) - func.coalesce(JobSpareDetailsSA.dbl_indirect_discount_amount,0) - func.coalesce(JobSpareDetailsSA.dbl_dealer_price,0)).label('spare_charge'),\
            #                                 BranchSA.vchr_name.label('branch_name'))\
            #                                 .join(ItemServiceSA,ItemServiceSA.fk_job_master_id == JobMasterSA.pk_bint_id)\
            #                                 .outerjoin(JobSpareDetailsSA,JobSpareDetailsSA.fk_details_id == ItemServiceSA.pk_bint_id)\
            #                                 .join(BranchSA,BranchSA.pk_bint_id == JobMasterSA.fk_branch_id)\
            #                                 .join(TerritorySA,TerritorySA.pk_bint_id == BranchSA.fk_territory_id)\
            #                                 .filter(and_(cast(JobMasterSA.dat_created_at,Date) >= dat_from,cast(JobMasterSA.dat_created_at,Date) <= dat_to),(ItemServiceSA.vchr_job_status == 'SERVICED & DELIVERED'))\
            #                                 .group_by('branch_id','branch_name')
            #
            #
            #
            # import pdb; pdb.set_trace()
            # if vchr_filter_area:
            #     lst_filter_ids = []
            #     for ins_filter in lst_filter:
            #         lst_filter_ids.append(ins_filter['pk_bint_id'])
            #     if lst_filter_ids:
            #         if vchr_filter_area.upper() == "ZONE":
            #             rst_profit_report = rst_profit_report.filter(TerritorySA.fk_zone_id.in_(lst_filter_ids))
            #         elif vchr_filter_area.upper() == "TERRITORY":
            #             rst_profit_report = rst_profit_report.filter(TerritorySA.pk_bint_id.in_(lst_filter_ids))
            #         elif vchr_filter_area.upper() == "BRANCH":
            #             rst_profit_report = rst_profit_report.filter(BranchSA.pk_bint_id.in_(lst_filter_ids))
            #
            #
            # dct_branch = {}
            # for ins_profit in rst_profit_report.all():
            #     vchr_branch = ins_profit.branch_name.upper()
            #     if vchr_branch not in dct_branch:
            #         dct_branch[vchr_branch] = 0
            #     dct_branch[vchr_branch] += ins_profit.service_charge + ins_profit.spare_charge

            rst_profit_report = session.query(JobMasterSA.fk_branch_id.label('branch_id'),\
                                            func.sum(func.coalesce(ItemServiceSA.dbl_est_amt,0)- func.coalesce(ItemServiceSA.dbl_tax,0)).label('service_charge'),\
                                            func.sum(func.coalesce(JobSpareDetailsSA.dbl_amount,0) - func.coalesce(JobSpareDetailsSA.dbl_dealer_price,0)).label('spare_charge'),\
                                            BranchSA.vchr_name.label('branch_name'))\
                                            .join(ItemServiceSA,ItemServiceSA.fk_job_master_id == JobMasterSA.pk_bint_id)\
                                            .outerjoin(JobSpareDetailsSA,JobSpareDetailsSA.fk_details_id == ItemServiceSA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == JobMasterSA.fk_branch_id)\
                                            .join(TerritorySA,TerritorySA.pk_bint_id == BranchSA.fk_territory_id)\
                                            .filter(and_(cast(JobMasterSA.dat_created_at,Date) >= dat_from,cast(JobMasterSA.dat_created_at,Date) <= dat_to),(ItemServiceSA.vchr_job_status == 'SERVICED & DELIVERED'))\
                                            .group_by('branch_id','branch_name')



            if vchr_filter_area:
                lst_filter_ids = []
                for ins_filter in lst_filter:
                    lst_filter_ids.append(ins_filter['pk_bint_id'])
                if lst_filter_ids:
                    if vchr_filter_area.upper() == "ZONE":
                        rst_profit_report = rst_profit_report.filter(TerritorySA.fk_zone_id.in_(lst_filter_ids))
                    elif vchr_filter_area.upper() == "TERRITORY":
                        rst_profit_report = rst_profit_report.filter(TerritorySA.pk_bint_id.in_(lst_filter_ids))
                    elif vchr_filter_area.upper() == "BRANCH":
                        rst_profit_report = rst_profit_report.filter(BranchSA.pk_bint_id.in_(lst_filter_ids))


            dct_branch = {}
            for ins_profit in rst_profit_report.all():
                vchr_branch = ins_profit.branch_name.upper()
                if vchr_branch not in dct_branch:
                    dct_branch[vchr_branch] = 0
                dct_branch[vchr_branch] =+ ins_profit.spare_charge

            session.close()
            return Response({'status':'success' ,'data' : dct_branch})
        except Exception as e:
            session.close()
            return Response({'status':0,'reason' : str(e)})

class ServiceProfitReportDownload(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            session = Session()

            dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d')
            dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d')
            vchr_filter_area = request.data.get('areaChoosen')
            lst_filter = request.data.get('filterIds')

            rst_profit_report = session.query(JobMasterSA.fk_branch_id.label('branch_id'),\
                                            func.round(func.sum(func.coalesce(ItemServiceSA.dbl_est_amt,0)- func.coalesce(ItemServiceSA.dbl_tax,0))).label('service_charge'),\
                                            func.round(func.sum(func.coalesce(JobSpareDetailsSA.dbl_amount,0) - func.coalesce(JobSpareDetailsSA.dbl_dealer_price,0))).label('spare_charge'),\
                                            BranchSA.vchr_name.label('branch_name'))\
                                            .join(ItemServiceSA,ItemServiceSA.fk_job_master_id == JobMasterSA.pk_bint_id)\
                                            .outerjoin(JobSpareDetailsSA,JobSpareDetailsSA.fk_details_id == ItemServiceSA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == JobMasterSA.fk_branch_id)\
                                            .join(TerritorySA,TerritorySA.pk_bint_id == BranchSA.fk_territory_id)\
                                            .filter(and_(cast(JobMasterSA.dat_created_at,Date) >= dat_from,cast(JobMasterSA.dat_created_at,Date) <= dat_to))\
                                            .group_by('branch_id','branch_name')



            lst_filter_ids = []
            lst_area =[]
            # import pdb; pdb.set_trace()
            if vchr_filter_area:
                for ins_filter in lst_filter:
                    lst_filter_ids.append(ins_filter['pk_bint_id'])
                if lst_filter_ids:
                    if vchr_filter_area.upper() == "ZONE":
                        rst_profit_report = rst_profit_report.filter(TerritorySA.fk_zone_id.in_(lst_filter_ids))
                        lst_area = list(Zone.objects.filter(pk_bint_id__in = lst_filter_ids).values_list('vchr_name',flat = True))
                    elif vchr_filter_area.upper() == "TERRITORY":
                        rst_profit_report = rst_profit_report.filter(TerritorySA.pk_bint_id.in_(lst_filter_ids))
                        lst_area = list(Territory.objects.filter(pk_bint_id__in = lst_filter_ids).values_list('vchr_name',flat = True))
                    elif vchr_filter_area.upper() == "BRANCH":
                        rst_profit_report = rst_profit_report.filter(BranchSA.pk_bint_id.in_(lst_filter_ids))
                        lst_area = list(Branch.objects.filter(pk_bint_id__in = lst_filter_ids).values_list('vchr_name',flat = True))


            dct_branch = {}
            for ins_profit in rst_profit_report.all():
                vchr_branch = ins_profit.branch_name.upper()
                if vchr_branch not in dct_branch:
                    dct_branch[vchr_branch] = 0
                dct_branch[vchr_branch] += ins_profit.spare_charge

            dct_excel = {}
            dct_excel['Branch'] = []
            dct_excel['Amount'] = []

            for ins_excel in dct_branch:
                dct_excel['Branch'].append(ins_excel)
                dct_excel['Amount'].append(dct_branch[ins_excel])


            dbl_grand_total = sum(dct_excel['Amount'])
            dct_excel['Branch'].append("GRAND TOTAL")
            dct_excel['Amount'].append(dbl_grand_total)

            """Excel creation"""
            df = pd.DataFrame(dct_excel)
            df_order = df[['Branch','Amount']]
            file_name = '/serviceprofitreport.xlsx'
            excel_file = settings.MEDIA_ROOT+file_name
            sheet_name = 'profit'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_order.to_excel(writer, sheet_name=sheet_name,startrow=6, startcol=0 ,index = 0)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(0,5,40)

            merge_format = workbook.add_format({
            'bold': 4,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
            # 'fg_color': 'lighr-blue'
            })

            worksheet.merge_range('A1+:C2', 'Service Profit Report', merge_format)
            worksheet.merge_range('A4+:B4', 'Area : '+','.join(lst_area))
            worksheet.merge_range('A5+:B5', 'Reporting Period : '+datetime.strftime(dat_from,'%d-%m-%Y') +' to '+ datetime.strftime(dat_to,'%d-%m-%Y'))
            worksheet.merge_range('C4+:D4', 'Taken By :           '+request.user.username)
            worksheet.merge_range('C5+:D5', 'Action Date :       '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'))

            writer.save()

            session.close()
            return Response({'status':'success' ,'data' : settings.HOSTNAME+settings.MEDIA_URL+file_name })
        except Exception as e:
            session.close()
            return Response({'status':0,'reason' : str(e)})

class PaymentReport(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            blnZone = False
            blnTert = False
            blnBranch = False

            dct_filter = {}
            if request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                blnBranch = False
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['TERRITORY MANAGER']:
                blnBranch = True
                lst_branch = list(Branch.objects.filter(fk_territory_id = request.user.userdetails.int_area_id).values('vchr_name','pk_bint_id'))
                dct_filter['lst_branch'] = lst_branch
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['ZONE MANAGER']:
                blnTert = True
                lst_territory = list(Territory.objects.filter(fk_zone_id = request.user.userdetails.int_area_id,chr_status = 'N').values('vchr_name','pk_bint_id'))
                dct_filter['lst_territory'] = lst_territory
                blnBranch = True
                lst_branch = list(Branch.objects.filter(fk_territory_id__fk_zone_id = request.user.userdetails.int_area_id).values('vchr_name','pk_bint_id'))
                dct_filter['lst_branch'] = lst_branch
            else:
                blnZone = True
                lst_zones = list(Zone.objects.filter(chr_status = 'N').values('vchr_name','pk_bint_id'))
                dct_filter['lst_zones'] = lst_zones
                blnTert = True
                lst_territory = list(Territory.objects.filter(chr_status = 'N').values('vchr_name','pk_bint_id'))
                dct_filter['lst_territory'] = lst_territory
                blnBranch = True
                lst_branch = list(Branch.objects.values('vchr_name','pk_bint_id'))
                dct_filter['lst_branch'] = lst_branch

            return Response({'status':'success' ,'dct_filter' : dct_filter,'blnBranch':blnBranch,'blnTert':blnTert,'blnZone':blnZone})
        except Exception as e:
            return Response({'status':0,'reason' : str(e)})

    def post(self,request):
        try:

            session = Session()

            dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d')
            dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d')
            vchr_filter_area = request.data.get('areaChoosen')
            lst_filter = request.data.get('filterIds')

            """ data wise filtering """
            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','GENERAL MANAGER SALES','COUNTRY HEAD']:
                lst_branch = Branch.objects.filter(fk_company_id=request.user.userdetails.fk_company_id).values_list('pk_bint_id')
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                lst_branch = [request.user.userdetails.fk_branch_id]
            elif request.user.userdetails.int_area_id:
                lst_branch = show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            else:
                session.close()
                return Response({'status':1 ,'data' : "no data"})

            rst_payment_report = session.query(func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  0 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('finance_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  0 ),PaymentDetailsSA.dbl_amount)])),0).label('finance_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  1 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('cash_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  1 ),PaymentDetailsSA.dbl_amount)])),0).label('cash_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  2 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('debit_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  2 ),PaymentDetailsSA.dbl_amount)])),0).label('debit_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  3 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('credit_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  3 ),PaymentDetailsSA.dbl_amount)])),0).label('credit_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  4 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('receipt_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  4 ),PaymentDetailsSA.dbl_amount)])),0).label('receipt_count'),\
                                            # func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  5 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('paytm_value'),\
                                            # func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  5 ),PaymentDetailsSA.dbl_amount)])),0).label('paytm_count'),\
                                            # func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  6 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('paytmmall_value'),\
                                            # func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  6 ),PaymentDetailsSA.dbl_amount)])),0).label('paytmmall_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  7 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('barath_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  7 ),PaymentDetailsSA.dbl_amount)])),0).label('barath_count'),\
                                            func.coalesce(func.sum(PaymentDetailsSA.dbl_amount),0).label('total_value'),\
                                            func.coalesce(func.count(PaymentDetailsSA.dbl_amount),0).label('total_count'),\
                                            EnquiryMasterSA.fk_branch_id.label('branch_id'),\
                                            ZoneSA.vchr_name.label('zone_name'),\
                                            TerritorySA.vchr_name.label('territory_name'),\
                                            BranchSA.vchr_name.label('branch_name'))\
                                            .join(EnquiryMasterSA,PaymentDetailsSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                            .join(TerritorySA,TerritorySA.pk_bint_id == BranchSA.fk_territory_id)\
                                            .join(ZoneSA,TerritorySA.fk_zone_id == ZoneSA.pk_bint_id)\
                                            .filter(and_(cast(PaymentDetailsSA.dat_created,Date) >= dat_from,cast(PaymentDetailsSA.dat_created,Date) <= dat_to))\
                                            .filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))\
                                            .group_by('branch_id','branch_name','zone_name','territory_name')

            if not rst_payment_report.all():
                session.close()
                return Response({'status':1 ,'data' : "no data"})

            if vchr_filter_area:
                lst_filter_ids = []
                for ins_filter in lst_filter:
                    lst_filter_ids.append(ins_filter['pk_bint_id'])
                if lst_filter_ids:
                    if vchr_filter_area.upper() == "ZONE":
                        rst_payment_report = rst_payment_report.filter(TerritorySA.fk_zone_id.in_(lst_filter_ids))
                    elif vchr_filter_area.upper() == "TERRITORY":
                        rst_payment_report = rst_payment_report.filter(TerritorySA.pk_bint_id.in_(lst_filter_ids))
                    elif vchr_filter_area.upper() == "BRANCH":
                        rst_payment_report = rst_payment_report.filter(BranchSA.pk_bint_id.in_(lst_filter_ids))

            if not rst_payment_report.all():
                session.close()
                return Response({'status':1 ,'data' : "no data"})

            dct_payment = {}
            dct_payment['ALL'] = {}
            dct_payment['ALL']['total_value'] = 0
            dct_payment['ALL']['total_count'] = 0
            dct_payment['lst_payment_methods'] = []
            dct_payment['area_wise_data'] = {}

            dct_payment_methods = {}
            dct_payment_methods['cash'] = {}
            dct_payment_methods['cash']['name'] = "Cash"
            dct_payment_methods['cash']['y'] = 0
            dct_payment_methods['cash']['z'] = 0
            dct_payment_methods['finance'] = {}
            dct_payment_methods['finance']['name'] = "Finance"
            dct_payment_methods['finance']['y'] = 0
            dct_payment_methods['finance']['z'] = 0
            dct_payment_methods['debit'] = {}
            dct_payment_methods['debit']['name'] = "Debit Card"
            dct_payment_methods['debit']['y'] = 0
            dct_payment_methods['debit']['z'] = 0
            dct_payment_methods['credit'] = {}
            dct_payment_methods['credit']['name'] = "Credit Card"
            dct_payment_methods['credit']['y'] = 0
            dct_payment_methods['credit']['z'] = 0
            dct_payment_methods['receipt'] = {}
            dct_payment_methods['receipt']['name'] = "Receipt"
            dct_payment_methods['receipt']['y'] = 0
            dct_payment_methods['receipt']['z'] = 0
            # dct_payment_methods['paytm'] = {}
            # dct_payment_methods['paytm']['name'] = "Paytm"
            # dct_payment_methods['paytm']['y'] = 0
            # dct_payment_methods['paytm']['z'] = 0
            # dct_payment_methods['paytmmall'] = {}
            # dct_payment_methods['paytmmall']['name'] = "Paytm Mall"
            # dct_payment_methods['paytmmall']['y'] = 0
            # dct_payment_methods['paytmmall']['z'] = 0
            dct_payment_methods['barath'] = {}
            dct_payment_methods['barath']['name'] = "Bharath Qr"
            dct_payment_methods['barath']['y'] = 0
            dct_payment_methods['barath']['z'] = 0

            for ins_payment in rst_payment_report.all():
                vchr_branch = ins_payment.branch_name.upper()
                if vchr_branch not in dct_payment['ALL']:
                    dct_payment['ALL'][vchr_branch] = {}
                    dct_payment['ALL'][vchr_branch]['name'] = vchr_branch.title()
                    dct_payment['ALL'][vchr_branch]['finance_value'] = 0
                    dct_payment['ALL'][vchr_branch]['finance_count'] = 0
                    dct_payment['ALL'][vchr_branch]['cash_value'] = 0
                    dct_payment['ALL'][vchr_branch]['cash_count'] = 0
                    dct_payment['ALL'][vchr_branch]['debit_value'] = 0
                    dct_payment['ALL'][vchr_branch]['debit_count'] = 0
                    dct_payment['ALL'][vchr_branch]['credit_value'] = 0
                    dct_payment['ALL'][vchr_branch]['credit_count'] = 0
                    dct_payment['ALL'][vchr_branch]['receipt_value'] = 0
                    dct_payment['ALL'][vchr_branch]['receipt_count'] = 0
                    # dct_payment['ALL'][vchr_branch]['paytm_value'] = 0
                    # dct_payment['ALL'][vchr_branch]['paytm_count'] = 0
                    # dct_payment['ALL'][vchr_branch]['paytmmall_value'] = 0
                    # dct_payment['ALL'][vchr_branch]['paytmmall_count'] = 0
                    dct_payment['ALL'][vchr_branch]['barath_value'] = 0
                    dct_payment['ALL'][vchr_branch]['barath_count'] = 0


                dct_payment['ALL'][vchr_branch]['finance_value'] += ins_payment.finance_value
                dct_payment['ALL'][vchr_branch]['finance_count'] += ins_payment.finance_count
                dct_payment['ALL'][vchr_branch]['cash_value'] += ins_payment.cash_value
                dct_payment['ALL'][vchr_branch]['cash_count'] += ins_payment.cash_count
                dct_payment['ALL'][vchr_branch]['debit_value'] += ins_payment.debit_value
                dct_payment['ALL'][vchr_branch]['debit_count'] += ins_payment.debit_count
                dct_payment['ALL'][vchr_branch]['credit_value'] += ins_payment.credit_value
                dct_payment['ALL'][vchr_branch]['credit_count'] += ins_payment.credit_count
                dct_payment['ALL'][vchr_branch]['receipt_value'] += ins_payment.receipt_value
                dct_payment['ALL'][vchr_branch]['receipt_count'] += ins_payment.receipt_count
                # dct_payment['ALL'][vchr_branch]['paytm_value'] += ins_payment.paytm_value
                # dct_payment['ALL'][vchr_branch]['paytm_count'] += ins_payment.paytm_count
                # dct_payment['ALL'][vchr_branch]['paytmmall_value'] += ins_payment.paytmmall_value
                # dct_payment['ALL'][vchr_branch]['paytmmall_count'] += ins_payment.paytmmall_count
                dct_payment['ALL'][vchr_branch]['barath_value'] += ins_payment.barath_value
                dct_payment['ALL'][vchr_branch]['barath_count'] += ins_payment.barath_count

                dct_payment['ALL']['total_value'] += ins_payment.total_value
                dct_payment['ALL']['total_count'] += ins_payment.total_count

                dct_payment_methods['cash']['y'] += ins_payment.cash_value
                dct_payment_methods['cash']['z'] += ins_payment.cash_count
                dct_payment_methods['finance']['y'] += ins_payment.finance_value
                dct_payment_methods['finance']['z'] += ins_payment.finance_count
                dct_payment_methods['debit']['y'] += ins_payment.debit_value
                dct_payment_methods['debit']['z'] += ins_payment.debit_count
                dct_payment_methods['credit']['y'] += ins_payment.credit_value
                dct_payment_methods['credit']['z'] += ins_payment.credit_count
                dct_payment_methods['receipt']['y'] += ins_payment.receipt_value
                dct_payment_methods['receipt']['z'] += ins_payment.receipt_count
                # dct_payment_methods['paytm']['y'] += ins_payment.paytm_value
                # dct_payment_methods['paytm']['z'] += ins_payment.paytm_count
                # dct_payment_methods['paytmmall']['y'] += ins_payment.paytmmall_value
                # dct_payment_methods['paytmmall']['z'] += ins_payment.paytmmall_count
                dct_payment_methods['barath']['y'] += ins_payment.barath_value
                dct_payment_methods['barath']['z'] += ins_payment.barath_count

                zone_name = ins_payment.zone_name.upper()
                territory_name = ins_payment.territory_name.upper()
                branch_name = ins_payment.branch_name.upper()

                if request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER',"TERRITORY MANAGER"]:
                    if branch_name not in dct_payment['area_wise_data']:
                        dct_payment['area_wise_data'][branch_name] = {}
                        dct_payment['area_wise_data'][branch_name]['total_count'] = 0
                        dct_payment['area_wise_data'][branch_name]['total_value'] = 0

                    dct_payment['area_wise_data'][branch_name]['total_count'] += int(ins_payment.total_count)
                    dct_payment['area_wise_data'][branch_name]['total_value'] += float(ins_payment.total_value)

                elif request.user.userdetails.fk_group.vchr_name.upper() == "ZONE MANAGER":
                    if territory_name not in dct_payment['area_wise_data']:
                        dct_payment['area_wise_data'][territory_name] = {}
                        dct_payment['area_wise_data'][territory_name][branch_name] = {}
                        dct_payment['area_wise_data'][territory_name][branch_name]['total_count'] = 0
                        dct_payment['area_wise_data'][territory_name][branch_name]['total_value'] = 0

                    elif branch_name not in dct_payment['area_wise_data'][territory_name]:
                        dct_payment['area_wise_data'][territory_name][branch_name] = {}
                        dct_payment['area_wise_data'][territory_name][branch_name]['total_count'] = 0
                        dct_payment['area_wise_data'][territory_name][branch_name]['total_value'] = 0

                    dct_payment['area_wise_data'][territory_name][branch_name]['total_count'] += int(ins_payment.total_count)
                    dct_payment['area_wise_data'][territory_name][branch_name]['total_value'] += float(ins_payment.total_value)

                else:
                    if zone_name not in dct_payment['area_wise_data']:
                        dct_payment['area_wise_data'][zone_name] = {}
                        dct_payment['area_wise_data'][zone_name][territory_name] = {}
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name] = {}
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_count'] = 0
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_value'] = 0

                    elif territory_name not in dct_payment['area_wise_data'][zone_name]:
                        dct_payment['area_wise_data'][zone_name][territory_name] = {}
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name] = {}
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_count'] = 0
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_value'] = 0

                    elif branch_name not in dct_payment['area_wise_data'][zone_name][territory_name]:
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name] = {}
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_count'] = 0
                        dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_value'] = 0

                    dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_count'] += int(ins_payment.total_count)
                    dct_payment['area_wise_data'][zone_name][territory_name][branch_name]['total_value'] += float(ins_payment.total_value)

            for ins_method in dct_payment_methods:
                dct_payment['lst_payment_methods'].append(dct_payment_methods[ins_method])

            session.close()
            return Response({'status':'success' ,'data' : dct_payment})
        except Exception as e:
            session.close()
            return Response({'status':0,'reason' : str(e)})

class PaymentReportDownload(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        try:

            session = Session()

            dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d')
            dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d')
            vchr_filter_area = request.data.get('areaChoosen')
            lst_filter = request.data.get('filterIds')
            strType = request.data.get('strType')

            """ data wise filtering """
            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','GENERAL MANAGER SALES','COUNTRY HEAD']:
                lst_branch = Branch.objects.filter(fk_company_id=request.user.userdetails.fk_company_id).values_list('pk_bint_id')
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                lst_branch = [request.user.userdetails.fk_branch_id]
            elif request.user.userdetails.int_area_id:
                lst_branch = show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            else:
                session.close()
                return Response({'status':1 ,'data' : "no data"})

            rst_payment_report = session.query(func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  0 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('finance_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  0 ),PaymentDetailsSA.dbl_amount)])),0).label('finance_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  1 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('cash_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  1 ),PaymentDetailsSA.dbl_amount)])),0).label('cash_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  2 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('debit_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  2 ),PaymentDetailsSA.dbl_amount)])),0).label('debit_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  3 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('credit_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  3 ),PaymentDetailsSA.dbl_amount)])),0).label('credit_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  4 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('receipt_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  4 ),PaymentDetailsSA.dbl_amount)])),0).label('receipt_count'),\
                                            func.coalesce(func.sum(case([(( PaymentDetailsSA.int_fop ==  7 ),func.coalesce(PaymentDetailsSA.dbl_amount,0))])),0).label('barath_value'),\
                                            func.coalesce(func.count(case([(( PaymentDetailsSA.int_fop ==  7 ),PaymentDetailsSA.dbl_amount)])),0).label('barath_count'),\
                                            func.coalesce(func.sum(PaymentDetailsSA.dbl_amount),0).label('total_value'),\
                                            func.coalesce(func.count(PaymentDetailsSA.dbl_amount),0).label('total_count'),\
                                            EnquiryMasterSA.fk_branch_id.label('branch_id'),\
                                            BranchSA.vchr_name.label('branch_name'))\
                                            .join(EnquiryMasterSA,PaymentDetailsSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                            .join(TerritorySA,TerritorySA.pk_bint_id == BranchSA.fk_territory_id)\
                                            .filter(and_(cast(PaymentDetailsSA.dat_created,Date) >= dat_from,cast(PaymentDetailsSA.dat_created,Date) <= dat_to))\
                                            .filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))\
                                            .group_by('branch_id','branch_name')
            lst_area =[]
            if vchr_filter_area:
                lst_filter_ids = []
                for ins_filter in lst_filter:
                    lst_filter_ids.append(ins_filter['pk_bint_id'])
                if lst_filter_ids:
                    if vchr_filter_area.upper() == "ZONE":
                        rst_payment_report = rst_payment_report.filter(TerritorySA.fk_zone_id.in_(lst_filter_ids))
                        lst_area = list(Zone.objects.filter(pk_bint_id__in = lst_filter_ids).values_list('vchr_name',flat = True))
                    elif vchr_filter_area.upper() == "TERRITORY":
                        rst_payment_report = rst_payment_report.filter(TerritorySA.pk_bint_id.in_(lst_filter_ids))
                        lst_area = list(Territory.objects.filter(pk_bint_id__in = lst_filter_ids).values_list('vchr_name',flat = True))
                    elif vchr_filter_area.upper() == "BRANCH":
                        rst_payment_report = rst_payment_report.filter(BranchSA.pk_bint_id.in_(lst_filter_ids))
                        lst_area = list(Branch.objects.filter(pk_bint_id__in = lst_filter_ids).values_list('vchr_name',flat = True))

            dct_payment = {}
            dct_payment['ALL'] = {}
            dct_payment['ALL']['total_value'] = 0
            dct_payment['ALL']['total_count'] = 0

            for ins_payment in rst_payment_report.all():
                vchr_branch = ins_payment.branch_name.upper()
                if vchr_branch not in dct_payment['ALL']:
                    dct_payment['ALL'][vchr_branch] = {}
                    dct_payment['ALL'][vchr_branch]['name'] = vchr_branch.title()
                    dct_payment['ALL'][vchr_branch]['finance_value'] = 0
                    dct_payment['ALL'][vchr_branch]['finance_count'] = 0
                    dct_payment['ALL'][vchr_branch]['cash_value'] = 0
                    dct_payment['ALL'][vchr_branch]['cash_count'] = 0
                    dct_payment['ALL'][vchr_branch]['debit_value'] = 0
                    dct_payment['ALL'][vchr_branch]['debit_count'] = 0
                    dct_payment['ALL'][vchr_branch]['credit_value'] = 0
                    dct_payment['ALL'][vchr_branch]['credit_count'] = 0
                    dct_payment['ALL'][vchr_branch]['receipt_value'] = 0
                    dct_payment['ALL'][vchr_branch]['receipt_count'] = 0
                    dct_payment['ALL'][vchr_branch]['barath_value'] = 0
                    dct_payment['ALL'][vchr_branch]['barath_count'] = 0


                dct_payment['ALL'][vchr_branch]['finance_value'] += ins_payment.finance_value
                dct_payment['ALL'][vchr_branch]['finance_count'] += ins_payment.finance_count
                dct_payment['ALL'][vchr_branch]['cash_value'] += ins_payment.cash_value
                dct_payment['ALL'][vchr_branch]['cash_count'] += ins_payment.cash_count
                dct_payment['ALL'][vchr_branch]['debit_value'] += ins_payment.debit_value
                dct_payment['ALL'][vchr_branch]['debit_count'] += ins_payment.debit_count
                dct_payment['ALL'][vchr_branch]['credit_value'] += ins_payment.credit_value
                dct_payment['ALL'][vchr_branch]['credit_count'] += ins_payment.credit_count
                dct_payment['ALL'][vchr_branch]['receipt_value'] += ins_payment.receipt_value
                dct_payment['ALL'][vchr_branch]['receipt_count'] += ins_payment.receipt_count
                dct_payment['ALL'][vchr_branch]['barath_value'] += ins_payment.barath_value
                dct_payment['ALL'][vchr_branch]['barath_count'] += ins_payment.barath_count

                dct_payment['ALL']['total_value'] += ins_payment.total_value
                dct_payment['ALL']['total_count'] += ins_payment.total_count


            dct_excel = {}
            dct_excel['Branch'] = []
            dct_excel['Cash'] = []
            dct_excel['Finance'] = []
            dct_excel['Credit Card'] = []
            dct_excel['Debit Card'] = []
            dct_excel['Receipt'] = []
            dct_excel['Bharath Qr'] = []
            lst_colum_order = ['Branch','Cash','Finance','Debit Card','Credit Card','Receipt','Bharath Qr']
            for ins_data in dct_payment['ALL']:
                if strType == 'VALUE':
                    if ins_data in ['total_value','total_count']:
                        total_value = dct_payment['ALL']['total_value']
                    else:
                        dct_excel['Branch'].append(dct_payment['ALL'][ins_data]['name'])
                        dct_excel['Cash'].append(dct_payment['ALL'][ins_data]['cash_value'])
                        dct_excel['Finance'].append(dct_payment['ALL'][ins_data]['finance_value'])
                        dct_excel['Credit Card'].append(dct_payment['ALL'][ins_data]['credit_value'])
                        dct_excel['Debit Card'].append(dct_payment['ALL'][ins_data]['debit_value'])
                        dct_excel['Receipt'].append(dct_payment['ALL'][ins_data]['receipt_value'])
                        dct_excel['Bharath Qr'].append(dct_payment['ALL'][ins_data]['barath_value'])
                else:
                    if ins_data in ['total_value','total_count']:
                        total_value = dct_payment['ALL']['total_count']
                    else:
                        dct_excel['Branch'].append(dct_payment['ALL'][ins_data]['name'])
                        dct_excel['Cash'].append(dct_payment['ALL'][ins_data]['cash_count'])
                        dct_excel['Finance'].append(dct_payment['ALL'][ins_data]['finance_count'])
                        dct_excel['Credit Card'].append(dct_payment['ALL'][ins_data]['credit_count'])
                        dct_excel['Debit Card'].append(dct_payment['ALL'][ins_data]['debit_count'])
                        dct_excel['Receipt'].append(dct_payment['ALL'][ins_data]['receipt_count'])
                        dct_excel['Bharath Qr'].append(dct_payment['ALL'][ins_data]['barath_count'])

            """Excel creation"""
            df = pd.DataFrame(dct_excel)
            df_order = df[lst_colum_order]
            file_name = 'paymentreport.xlsx'
            excel_file = settings.MEDIA_ROOT+'/'+file_name
            sheet_name = 'payment'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_order.to_excel(writer, sheet_name=sheet_name,startrow=6, startcol=0 ,index = 0)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(0,0,30)
            worksheet.set_column(1,8,19)

            merge_format = workbook.add_format({
            'bold': 4,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
            })

            footer_format = workbook.add_format({
            'bold': 2,
            'align': 'right',
            'valign': 'vcenter'
            })

            worksheet.merge_range('A1+:G2', 'Payment Report', merge_format)
            worksheet.merge_range('A5+:B5', 'Reporting Period : '+datetime.strftime(dat_from,'%d-%m-%Y') +' to '+ datetime.strftime(dat_to,'%d-%m-%Y'))
            worksheet.merge_range('F4+:G4', 'Taken By :           '+request.user.username)
            worksheet.merge_range('F5+:G5', 'Action Date :       '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'))

            worksheet.write('F'+str(9+len(dct_excel['Branch'])), 'Total :',footer_format)
            worksheet.write('G'+str(9+len(dct_excel['Branch'])), str(total_value),footer_format)

            writer.save()

            session.close()
            return Response({'status':'success' ,'data' : settings.HOSTNAME+settings.MEDIA_URL+file_name })
        except Exception as e:
            session.close()
            return Response({'status':0,'reason' : str(e)})


class GdpReport(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()

            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            int_zone_id = request.data.get("intZoneId")
            int_ter_id = request.data.get("intTerId")
            int_br_id = request.data.get("intBranchId")
            bln_export = request.data.get("blnExport")
            int_type = request.data.get("intType") #0.All,1.Gdp,2.Gdew
            # bln_export = True
            # int_type = 1 #0.All,1.Gdp,2.Gdew
            # dat_to = "2020-05-29"
            # dat_from = "2020-01-01"
            str_querry =  """select
                             TO_CHAR(ie.dat_sale ::DATE,'DD-MM-YYYY') as dat_invoice,
                             (ie.dbl_imei_json->>'imei')::jsonb->0 as imei,ie.int_quantity as int_qty,(ie.dbl_amount-COALESCE(ie.dbl_discount_amount,0)-COALESCE(ie.dbl_indirect_discount_amount,0)-COALESCE(ie.dbl_buy_back_amount,0)) as dbl_amount,
                             (ie2.dbl_amount - COALESCE(ie2.dbl_discount_amount,0)-COALESCE(ie2.dbl_buy_back_amount,0))  as dbl_item_amount,
                             it.vchr_item_name as vchr_item_name_gdp,it.vchr_item_code as vchr_item_code_gdp,
                             it2.id as int_item_id,CONCAT (it2.vchr_item_code,' ',it2.vchr_item_name) as vchr_item_name,it2.vchr_item_code as vchr_exp_item_code ,it2.vchr_item_name as vchr_exp_item_name,
                             bd2.id as int_brand_id,bd2.vchr_brand_name as vchr_brand_name,
                             pd2.id as int_product_id,pd2.vchr_product_name as vchr_product_name,
                             cst.id as int_cust_id,UPPER(CONCAT(cst.cust_fname,' ',cst.cust_lname)) as vchr_cust_name,
                             br.pk_bint_id as int_branch_id ,br.vchr_code as vchr_branch_code,UPPER(br.vchr_name) as vchr_branch_name,
                             tr.pk_bint_id as int_territory_id,tr.vchr_code as vchr_territory_code,tr.vchr_name as vchr_territory_name,
                             zn.pk_bint_id as int_zone_id,zn.vchr_code as vchr_zone_code,zn.vchr_name as vchr_zone_name,
                             CASE WHEN it.vchr_item_code = 'GDC00001' then 'GDP' WHEN it.vchr_item_code = 'GDC00002' then 'GDEW' END AS vchr_type

                             from item_enquiry ie
                             join item_enquiry ie2 on ((ie.dbl_imei_json->>'imei'))::text = (ie2.dbl_imei_json->>'imei')::text  AND ie.fk_item_id != ie2.fk_item_id AND  ie2.fk_enquiry_master_id = ie.fk_enquiry_master_id and  ie2.vchr_enquiry_status IN ('INVOICED','RETURNED')
                             join enquiry_master em on ie.fk_enquiry_master_id = em.pk_bint_id
                             join branch br on br.pk_bint_id = em.fk_branch_id
                             join territory tr on tr.pk_bint_id = br.fk_territory_id
                             join zone zn on zn.pk_bint_id = tr.fk_zone_id
                             join items it on it.id = ie.fk_item_id
                             join items it2 on it2.id =  ie2.fk_item_id AND it2.vchr_item_code not in ('GDC00001','GDC00002')
                             join products pd on pd.id = it.fk_product_id
                             join products pd2 on pd2.id = it2.fk_product_id
                             join brands bd on bd.id =it.fk_brand_id
                             join brands bd2 on bd2.id =it2.fk_brand_id
                             join customer_app_customermodel cst on cst.id = em.fk_customer_id
                             WHERE ie.vchr_enquiry_status IN ('INVOICED','RETURNED') AND em.chr_doc_status = 'N'and it.vchr_item_code in ('GDC00001','GDC00002')
                             and it2.vchr_item_code not in ('GDC00001','GDC00002') {filter}  """



            #hhh
            """DATE WISE FILTER"""
            str_filter = " AND ie.dat_sale:: DATE BETWEEN '"+str(dat_from)+"' and '"+str(dat_to)+"'"
            if int_zone_id:
                str_filter += "AND zn.pk_bint_id = "+str(int_zone_id)+" "
            if int_ter_id:
                str_filter += "AND tr.pk_bint_id = "+str(int_ter_id)+" "
            if int_br_id:
                str_filter += "AND br.pk_bint_id = "+str(int_br_id)+" "
            if int_type ==1:
                str_filter += "AND it.vchr_item_code ='GDC00001' "
            elif int_type ==2:
                str_filter += "AND it.vchr_item_code ='GDC00002' "

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                str_filter +=" AND br.pk_bint_id = "+str(request.user.userdetails.fk_branch_id)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                str_filter += " AND br.pk_bint_id IN ("+str(lst_branch)[1:-1]+")"



            # str_querry = str_querry + "".join(set(lst_join)) + '{filter} group by {groupby} order by  dat_invoice DESC'
            # import pdb; pdb.set_trace()
            str_querry += "group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,ie.dat_sale ORDER BY ie.dat_sale::DATE DESC,br.vchr_name,cst.cust_fname,cst.cust_lname,it.vchr_item_code"
            str_querry = str_querry.format(filter = str_filter)
            # import pdb; pdb.set_trace()
            rst_data = conn.execute(str_querry).fetchall()
            lst_data = []
            if rst_data:
                lst_data = [dict(x) for x in rst_data]
                if bln_export:
                    data = gdp_export_excel(lst_data,request)
                    return Response({'status':1,'lst_data':lst_data,'export_data':data})

                return Response({'status':1,'lst_data' : lst_data} )
            #
            #     for data in rst_data:
            #
            #         dup_data = copy.deepcopy(dict(data))
            #         if data['imei']:
            #             if type(eval(data['imei'])) == list:
            #                 dct_item_data  = ItemEnquiry.objects.filter(
            #                                  dbl_imei_json__imei__has_any_keys = eval(data['imei']),
            #                                  vchr_enquiry_status='INVOICED',
            #                                  fk_enquiry_master__chr_doc_status = 'N').values(
            #                                                                                 'fk_item_id',
            #                                                                                 'fk_product_id',
            #                                                                                 'fk_brand_id',
            #                                                                                 'fk_item__vchr_item_code',
            #                                                                                 'fk_item__vchr_item_name',
            #                                                                                 'fk_brand__vchr_brand_name',
            #                                                                                 'fk_product__vchr_product_name',
            #                                                                                  'dbl_amount',
            #                                                                                  'int_quantity').exclude(fk_item__vchr_item_code__in = ['GDC00001','GDC00002'])
            #
            #
            #                 dct_item_data = dct_item_data.first()
            #                 if dct_item_data:
            #                     dup_data['int_item_id'] = dct_item_data['fk_item_id']
            #                     dup_data['int_product_id'] = dct_item_data['fk_product_id']
            #                     dup_data['int_brand_id'] = dct_item_data['fk_brand_id']
            #                     dup_data['vchr_item_code'] = dct_item_data['fk_item__vchr_item_code']
            #                     dup_data['vchr_item_name'] = dct_item_data['fk_item__vchr_item_code']+ ' '+ dct_item_data['fk_item__vchr_item_name']
            #                     dup_data['vchr_brand_name'] = dct_item_data['fk_brand__vchr_brand_name']
            #                     dup_data['vchr_product_name'] = dct_item_data['fk_product__vchr_product_name']
            #                     # dup_data['vchr_product_code'] = dct_item_data['fk_product__vchr_code']
            #                     dup_data['dbl_item_amount'] = dct_item_data['dbl_amount'] / dct_item_data['int_quantity']
            #                     lst_data.append(dup_data)
            #     import pdb; pdb.set_trace()
            #     if  lst_data:
            #
            #         if bln_export:
            #             asd = gdp_export_excel(lst_data,request)
            #             return Response({'status':1,'lst_data':lst_data,'export_data':data})
            #
            #         return Response({'status':0,'lst_data' : lst_data} )
            #
            else:
                return Response({'status':0,'message' :'No Data' })
        except Exception as e:
            return Response({'status':0,'reason' : str(e)})

def gdp_export_excel(lst_data,request):
    try:
        dat_from = request.data.get("datFrom")
        dat_to = request.data.get("datTo")
        # dat_from = "2020-01-01"
        # dat_to = "2020-05-29"
        int_type = request.data.get("intType") #0.All,1.Gdp,2.Gdew
        str_filter = ''
        if int_type==1:
            str_filter = 'Filter                      : GDP'
        elif int_type==2:
            str_filter = 'Filter                      : GDEW'
        else:
            str_filter = 'Filter                      : ALL'
        sheet_name1 = 'Sheet1'

        # import pdb; pdb.set_trace()
        int_zone_id = request.data.get("intZoneId")
        int_ter_id = request.data.get("intTerId")
        int_br_id = request.data.get("intBranchId")
        # int_br_id = 20

        df = pd.DataFrame(lst_data)
        excel_file = settings.MEDIA_ROOT+'/gdp_report.xlsx'
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df_export = pd.DataFrame()
        df_export['S.No'] = list(range(1,len(df.index)+1))
        # import pdb; pdb.set_trace()
        # df_export.index = pd.RangeIndex(start=1, stop=df.shape[0], step=1)
        df_export['DATE'] = df['dat_invoice']
        str_area = ' '
        if int_zone_id:
            dct_zone = Zone.objects.filter(pk_bint_id = int_zone_id).values('vchr_name').first()
            str_area = 'Area (ZONE)        : '+(dct_zone.get('vchr_name') or '--')
            df_export['TERRITORY'] = df['vchr_territory_name']
            df_export['BRANCH'] = df['vchr_branch_name']
        elif int_ter_id:
            dct_territory = Territory.objects.filter(pk_bint_id = int_ter_id).values('vchr_name').first()
            str_area = 'Area (TERRITORY)        : '+dct_territory.get('vchr_name') or '--'
            df_export['BRANCH'] = df['vchr_branch_name']

        elif  int_zone_id==int_ter_id ==int_br_id == None:
            df_export['BRANCH'] = df['vchr_branch_name']
            str_area = 'Area                       : ALL'

        if int_br_id:
            dct_branch = Branch.objects.filter(pk_bint_id = int_br_id).values('vchr_name').first()
            str_area = 'Area (BRANCH)        : '+dct_branch.get('vchr_name') or '--'

        df_export['CUSTOMER'] = df['vchr_cust_name']
        df_export['TYPE'] = df['vchr_type']
        df_export['PRODUCT'] = df['vchr_product_name']
        # df_export['BRAND'] = df['vchr_brand_name']
        df_export['ITEM CODE'] = df['vchr_exp_item_code']
        df_export['ITEM NAME'] = df['vchr_exp_item_name']
        df_export['IMEI'] = df['imei']
        df_export['GDP AMOUNT'] = df['dbl_amount']
        df_export['ITEM AMOUNT'] = df['dbl_item_amount']


        df_export.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=9, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name1]
        cell_format = workbook.add_format({'bold':True,'align': 'center'})
        str_report = 'Gdp Report'
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

        for i, col in enumerate(df_export.columns):
            if col in ['TYPE', 'ITEM AMOUNT', 'GDP AMOUNT']:
                worksheet.set_column(i, i, len(col)+4)
            else:

                # find length of column i
                column_len = df_export[col].astype(str).str.len().max()
                # Setting the length if the column header is larger
                # than the max column value length
                column_len = max(column_len, len(col)) + 2
                # set the column length
                worksheet.set_column(i, i, column_len)
        # import pdb; pdb.set_trace()
        worksheet.merge_range('A1+:K2', 'GDP ITEM REPORT', merge_format1)
        # worksheet.merge_range('A4+:B4', 'Area : '+','.join(lst_area))
        worksheet.merge_range('A4+:F4', 'Taken By                 : '+request.user.username, merge_format2)
        worksheet.merge_range('A5+:F5', 'Action Date             : '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
        worksheet.merge_range('A6+:F6', 'Reporting Period     : '+datetime.strftime((datetime.strptime(dat_from,'%Y-%m-%d')),'%d-%m-%Y') +' to '+ datetime.strftime((datetime.strptime(dat_to,'%Y-%m-%d')),'%d-%m-%Y'), merge_format2)

        worksheet.merge_range('A7+:F7',str_area, merge_format2)
        worksheet.merge_range('A8+:F8',str_filter, merge_format2)
        writer.save()
        data = settings.HOSTNAME+'/media/gdp_report.xlsx'
        return data


    except Exception as e:
            return Response({'status':0,'reason' : str(e)})
class StaffRewardReport(APIView):
    permission_classes=[AllowAny]


    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()
            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            int_zone_id = request.data.get("intZoneId")
            int_ter_id = request.data.get("intTerId")
            int_br_id = request.data.get("intBranchId")
            bln_export = request.data.get("blnExport")
            int_product_id = request.data.get("intProductId")
            int_brand_id = request.data.get("intBrandId")
            int_group_id = request.data.get("intGroupId")
            bln_export = True
            # dat_to = "2020-06-29"
            # dat_from = "2019-06-14"
            str_querry =  """select UPPER(br.vchr_name) as vchr_branch_name,tr.vchr_name as vchr_territory_name,
                             UPPER(concat(um.first_name,' ',um.last_name)) as vchr_staff_name,
                             UPPER(rm.vchr_reward_name) as vchr_reward_name,sum(sra.reward::float) as dbl_reward_amount,
                             UPPER(pd.vchr_product_name) as vchr_product_name,pd.id as int_product_id ,
                             UPPER(bd.vchr_brand_name) as vchr_brand_name,bd.id as int_brand_id,
                             CONCAT (it.vchr_item_code,' ',it.vchr_item_name) as vchr_item_name,it.id as it_item_id,
                             UPPER(gr.vchr_name) as vchr_group_name,em.vchr_enquiry_num,
                             to_char(em.dat_created_at::DATE,'dd-mm-yyyy') as dat_sale from
                             (SELECT fk_item_enquiry_id as enq_id,fk_rewards_master_id as rm_id,fk_rewards_details_id as rd_id,json_staff->>jsonb_object_keys(json_staff) as reward,jsonb_object_keys(json_staff) as staff_id,
                             dat_reward as reward_date from
                             (SELECT fk_item_enquiry_id,fk_rewards_details_id,fk_rewards_master_id,json_staff,dat_reward FROM rewards_available ) as staff_reward) as sra
                             join auth_user um on um.id = sra.staff_id::int
                             join userdetails us on us.user_ptr_id = um.id
                             join rewards_details rd on rd.pk_bint_id = sra.rd_id
                             join rewards_master rm on rm.pk_bint_id = sra.rm_id
                             join item_enquiry ie on ie.pk_bint_id = sra.enq_id
                             join enquiry_master em on em.pk_bint_id = ie.fk_enquiry_master_id
                             join branch br on br.pk_bint_id = em.fk_branch_id
                             join territory tr on tr.pk_bint_id = br.fk_territory_id
                             join zone zn on zn.pk_bint_id = tr.fk_zone_id
                             join products pd on pd.id= ie.fk_product_id
                             join brands bd on bd.id=ie.fk_brand_id
                             join items it on it.id=ie.fk_item_id
                             join groups gr on gr.pk_bint_id=us.fk_group_id {filter} """



            #hhh
            """DATE WISE FILTER"""
            str_filter = " WHERE em.dat_created_at :: DATE BETWEEN '"+str(dat_from)+"' and '"+str(dat_to)+"'"
            if int_product_id :
                str_filter += "AND pd.id = "+str(int_product_id)+" "
            if int_brand_id :
                str_filter += "AND bd.id = "+str(int_brand_id)+" "
            if int_group_id :
                str_filter += "AND gr.pk_bint_id = "+str(int_group_id)+" "

            if int_zone_id:
                str_filter += "AND zn.pk_bint_id = "+str(int_zone_id)+" "
            if int_ter_id:
                str_filter += "AND tr.pk_bint_id = "+str(int_ter_id)+" "
            if int_br_id:
                str_filter += "AND br.pk_bint_id = "+str(int_br_id)+" "

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                str_filter +=" AND br.pk_bint_id = "+str(request.user.userdetails.fk_branch_id)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                str_filter += " AND br.pk_bint_id IN ("+str(lst_branch)[1:-1]+")"



            # str_querry = str_querry + "".join(set(lst_join)) + '{filter} group by {groupby} order by  dat_invoice DESC'
            # import pdb; pdb.set_trace()
            str_querry += " group by 1,2,3,4,6,7,8,9,10,11,12,13,14 order by 14"
            str_querry = str_querry.format(filter = str_filter)
            # import pdb; pdb.set_trace()
            rst_data = conn.execute(str_querry).fetchall()
            lst_data = []
            if rst_data:
                lst_data = [dict(x) for x in rst_data]
                if bln_export:
                    data = staff_reward_export(lst_data,request)
                    return Response({'status':1,'lst_data':lst_data,'export_data':data})

                return Response({'status':1,'lst_data' : lst_data} )
            else:
                return Response({'status':0,'message' :'No Data' })
        except Exception as e:
            return Response({'status':0,'reason' : str(e)})
def staff_reward_export(lst_data,request):
    try:
        dat_from = request.data.get("datFrom")
        dat_to = request.data.get("datTo")
        # dat_from = "2020-01-01"
        # dat_to = "2020-05-29"
        sheet_name1 = 'Sheet1'
        str_filter = ''
        str_filter_product = 'ALL'
        str_filter_brand ='ALL'
        str_filter_group = 'ALL'
        # import pdb; pdb.set_trace()
        int_zone_id = request.data.get("intZoneId")
        int_ter_id = request.data.get("intTerId")
        int_br_id = request.data.get("intBranchId")


        int_product_id = request.data.get("intProductId")
        int_brand_id = request.data.get("intBrandId")
        int_group_id = request.data.get("intGroupId")
        str_filter_product = 'ALL'
        str_filter_brand ='ALL'
        str_filter_group = 'ALL'
        if int_product_id :
            str_filter_product = Products.objects.filter(id = int_product_id).values('vchr_product_name').first()['vchr_product_name']
        if int_brand_id :
            str_filter_brand =Brands.objects.filter(id = int_brand_id).values('vchr_brand_name').first()['vchr_brand_name']
        if  int_group_id :
            str_filter_group = Groups.objects.filter(pk_bint_id = int_group_id).values('vchr_name').first()['vchr_name']
        # int_br_id = 20

        df = pd.DataFrame(lst_data)
        excel_file = settings.MEDIA_ROOT+'/staff_reward_report.xlsx'
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df_export = pd.DataFrame()
        df_export['S.No'] = list(range(1,len(df.index)+1))
        # import pdb; pdb.set_trace()
        # df_export.index = pd.RangeIndex(start=1, stop=df.shape[0], step=1)
        df_export['DATE'] = df['dat_sale']
        str_area = ' '
        if int_zone_id:
            dct_zone = Zone.objects.filter(pk_bint_id = int_zone_id).values('vchr_name').first()
            str_area = 'Area (ZONE)           : '+(dct_zone.get('vchr_name') or '--')
            df_export['TERRITORY'] = df['vchr_territory_name']
            df_export['BRANCH'] = df['vchr_branch_name']
        elif int_ter_id:
            dct_territory = Territory.objects.filter(pk_bint_id = int_ter_id).values('vchr_name').first()
            str_area = 'Area (TERRITORY)        : '+dct_territory.get('vchr_name') or '--'
            df_export['BRANCH'] = df['vchr_branch_name']

        elif  int_zone_id==int_ter_id ==int_br_id == None:
            df_export['BRANCH'] = df['vchr_branch_name']
            str_area = 'Area                       : ALL'

        if int_br_id:
            dct_branch = Branch.objects.filter(pk_bint_id = int_br_id).values('vchr_name').first()
            str_area = 'Area (BRANCH)        : '+dct_branch.get('vchr_name') or '--'

        df_export['STAFF'] = df['vchr_staff_name']
        df_export['GROUP'] = df['vchr_group_name']
        df_export['ENQUIRY NUMBER'] = df['vchr_enquiry_num']
        df_export['PRODUCT'] = df['vchr_product_name']
        df_export['BRAND'] = df['vchr_brand_name']
        df_export['ITEM'] = df['vchr_item_name']
        df_export['GROUP'] = df['vchr_group_name']
        df_export['REWARD'] = df['vchr_reward_name']
        df_export['REWARD AMOUNT'] = df['dbl_reward_amount']




        df_export.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=12, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name1]
        cell_format = workbook.add_format({'bold':True,'align': 'center'})
        str_report = 'STAFF REWARD REPORT'
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

        for i, col in enumerate(df_export.columns):

                # find length of column i
                column_len = df_export[col].astype(str).str.len().max()
                # Setting the length if the column header is larger
                # than the max column value length
                column_len = max(column_len, len(col)) + 2
                # set the column length
                worksheet.set_column(i, i, column_len)
        # import pdb; pdb.set_trace()
        worksheet.merge_range('A1+:K2', 'STAFF REWARD REPORT', merge_format1)
        # worksheet.merge_range('A4+:B4', 'Area : '+','.join(lst_area))
        worksheet.merge_range('A4+:F4', 'Taken By                 : '+request.user.username, merge_format2)
        worksheet.merge_range('A5+:F5', 'Action Date             : '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
        worksheet.merge_range('A6+:F6', 'Reporting Period     : '+datetime.strftime((datetime.strptime(dat_from,'%Y-%m-%d')),'%d-%m-%Y') +' to '+ datetime.strftime((datetime.strptime(dat_to,'%Y-%m-%d')),'%d-%m-%Y'), merge_format2)

        worksheet.merge_range('A7+:F7',str_area, merge_format2)
        worksheet.merge_range('A8+:F8','Group                     : '+str_filter_group, merge_format2)
        worksheet.merge_range('A9+:F9','Product                  : '+str_filter_product, merge_format2)
        worksheet.merge_range('A10+:F10','Brand                     : '+str_filter_brand, merge_format2)
        writer.save()
        data = settings.HOSTNAME+'/media/staff_reward_report.xlsx'
        return data




    except Exception as e:
            return Response({'status':0,'reason' : str(e)})


class BankDetailRewardReport(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()

            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            int_zone_id = request.data.get("intZoneId")
            int_ter_id = request.data.get("intTerId")
            int_br_id = request.data.get("intBranchId")
            bln_export = request.data.get("blnExport")
            int_product_id = request.data.get("intProductId")
            int_brand_id = request.data.get("intBrandId")
            int_group_id = request.data.get("intGroupId")
            bln_export = True
            # dat_to = "2020-06-29"
            # dat_from = "2019-01-01"
            str_querry =  """select upper(br.vchr_name) as vchr_branch_name,
                             upper(concat(um.first_name,' ',um.last_name)) as vchr_staff_name,
                             sum(sra.reward::float) as dbl_reward_amount,
                             upper(gr.vchr_name) as vchr_group_name,
                             '"'||account_number as vchr_account_num,'"'||bank_ifsc as vchr_ifsc_num,
                             bn.vchr_name as vchr_bank_name ,upper(tr.vchr_name) as vchr_territory_name
                             from (select fk_item_enquiry_id as enq_id,fk_rewards_master_id as rm_id,fk_rewards_details_id as rd_id,json_staff->>jsonb_object_keys(json_staff) as reward,jsonb_object_keys(json_staff) as staff_id,dat_reward as reward_date
                             from  (SELECT fk_item_enquiry_id,fk_rewards_details_id,fk_rewards_master_id,json_staff,dat_reward FROM rewards_available ) as staff_reward) as sra
                             join auth_user um on um.id = sra.staff_id::int
                             join userdetails us on us.user_ptr_id = um.id
                             join rewards_details rd on rd.pk_bint_id = sra.rd_id
                             join rewards_master rm on rm.pk_bint_id = sra.rm_id
                             join item_enquiry ie on ie.pk_bint_id = sra.enq_id
                             join enquiry_master em on em.pk_bint_id = ie.fk_enquiry_master_id
                             left join branch br on br.pk_bint_id=em.fk_branch_id
                             join territory tr on tr.pk_bint_id = br.fk_territory_id
                             join zone zn on zn.pk_bint_id = tr.fk_zone_id
                             join products pd on pd.id= ie.fk_product_id
                             join brands bd on bd.id=ie.fk_brand_id
                             join items it on it.id=ie.fk_item_id
                             join groups gr on gr.pk_bint_id=us.fk_group_id
                             left join bankdetails bn on bn.pk_bint_id=us.fk_bank_details_id {filter}"""

            #"""
            """DATE WISE FILTER"""
            str_filter = " WHERE em.dat_created_at :: DATE BETWEEN '"+str(dat_from)+"' and '"+str(dat_to)+"'"
            if int_product_id :
                str_filter += "AND pd.id = "+str(int_product_id)+" "
            if int_brand_id :
                str_filter += "AND bd.id = "+str(int_brand_id)+" "
            if int_group_id :
                str_filter += "AND gr.pk_bint_id = "+str(int_group_id)+" "

            if int_zone_id:
                str_filter += "AND zn.pk_bint_id = "+str(int_zone_id)+" "
            if int_ter_id:
                str_filter += "AND tr.pk_bint_id = "+str(int_ter_id)+" "
            if int_br_id:
                str_filter += "AND br.pk_bint_id = "+str(int_br_id)+" "

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                str_filter +=" AND br.pk_bint_id = "+str(request.user.userdetails.fk_branch_id)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                str_filter += " AND br.pk_bint_id IN ("+str(lst_branch)[1:-1]+")"



            # import pdb; pdb.set_trace()
            str_querry += " group by 1,2,4,5,6,7,8 order by 3 desc"
            str_querry = str_querry.format(filter = str_filter)
            # import pdb; pdb.set_trace()
            rst_data = conn.execute(str_querry).fetchall()
            lst_data = []
            if rst_data:
                lst_data = [dict(x) for x in rst_data]
                if bln_export:
                    data = bank_detail_reward_export(lst_data,request)
                    return Response({'status':1,'lst_data':lst_data,'export_data':data})

                return Response({'status':1,'lst_data' : lst_data} )
            else:
                return Response({'status':0,'message' :'No Data' })
        except Exception as e:
            return Response({'status':0,'reason' : str(e)})

def bank_detail_reward_export(lst_data,request):
    try:
        dat_from = request.data.get("datFrom")
        dat_to = request.data.get("datTo")
        # dat_to = "2020-06-29"
        # dat_from = "2019-01-01"
        sheet_name1 = 'Sheet1'
        str_filter = ''
        # import pdb; pdb.set_trace()
        int_zone_id = request.data.get("intZoneId")
        int_ter_id = request.data.get("intTerId")
        int_br_id = request.data.get("intBranchId")

        int_group_id = request.data.get("intGroupId")

        str_filter_group = 'ALL'
        if  int_group_id :
            str_filter_group = Groups.objects.filter(pk_bint_id = int_group_id).values('vchr_name').first()['vchr_name']
        # int_br_id = 20

        df = pd.DataFrame(lst_data)
        excel_file = settings.MEDIA_ROOT+'/bank_detail_reward_export.xlsx'
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df_export = pd.DataFrame()
        df_export['S.No'] = list(range(1,len(df.index)+1))
        # import pdb; pdb.set_trace()
        # df_export.index = pd.RangeIndex(start=1, stop=df.shape[0], step=1)
        # df_export['DATE'] = df['dat_sale']
        str_area = ' '
        if int_zone_id:
            dct_zone = Zone.objects.filter(pk_bint_id = int_zone_id).values('vchr_name').first()
            str_area = 'Area (ZONE)           : '+(dct_zone.get('vchr_name') or '--')
            df_export['TERRITORY'] = df['vchr_territory_name']
            df_export['BRANCH'] = df['vchr_branch_name']
        elif int_ter_id:
            dct_territory = Territory.objects.filter(pk_bint_id = int_ter_id).values('vchr_name').first()
            str_area = 'Area (TERRITORY)        : '+dct_territory.get('vchr_name') or '--'
            df_export['BRANCH'] = df['vchr_branch_name']

        elif  int_zone_id==int_ter_id ==int_br_id == None:
            df_export['BRANCH'] = df['vchr_branch_name']
            str_area = 'Area                       : ALL'

        if int_br_id:
            dct_branch = Branch.objects.filter(pk_bint_id = int_br_id).values('vchr_name').first()
            str_area = 'Area (BRANCH)        : '+dct_branch.get('vchr_name') or '--'

        df_export['STAFF'] = df['vchr_staff_name']
        df_export['GROUP'] = df['vchr_group_name']
        df_export['BANK'] = df['vchr_bank_name']
        df_export['ACCOUNT NUMBER'] = df['vchr_account_num']
        df_export['IFSC NUMBER'] = df['vchr_ifsc_num']
        df_export['REWARD AMOUNT'] = df['dbl_reward_amount']




        df_export.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=12, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name1]
        cell_format = workbook.add_format({'bold':True,'align': 'center'})
        str_report = 'BANK DETAIL STAF REWARD'
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

        for i, col in enumerate(df_export.columns):

                # find length of column i
                column_len = df_export[col].astype(str).str.len().max()
                # Setting the length if the column header is larger
                # than the max column value length
                column_len = max(column_len, len(col)) + 2
                # set the column length
                worksheet.set_column(i, i, column_len)
        # import pdb; pdb.set_trace()
        worksheet.merge_range('A1+:H2', 'BANK WISE REWARD REPORT', merge_format1)
        # worksheet.merge_range('A4+:B4', 'Area : '+','.join(lst_area))
        worksheet.merge_range('A4+:F4', 'Taken By                 : '+request.user.username, merge_format2)
        worksheet.merge_range('A5+:F5', 'Action Date             : '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
        worksheet.merge_range('A6+:F6', 'Reporting Period     : '+datetime.strftime((datetime.strptime(dat_from,'%Y-%m-%d')),'%d-%m-%Y') +' to '+ datetime.strftime((datetime.strptime(dat_to,'%Y-%m-%d')),'%d-%m-%Y'), merge_format2)

        worksheet.merge_range('A7+:F7',str_area, merge_format2)
        worksheet.merge_range('A8+:F8','Group                     : '+str_filter_group, merge_format2)

        writer.save()
        data = settings.HOSTNAME+'/media/bank_detail_reward_export.xlsx'
        return data
    except Exception as e:
        return Response({'status':0,'reason' : str(e)})
class SlabWiseRewardReport(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        try:
            engine = get_engine()
            conn = engine.connect()

            dat_from = request.data.get("datFrom")
            dat_to = request.data.get("datTo")
            int_zone_id = request.data.get("intZoneId")
            int_ter_id = request.data.get("intTerId")
            int_br_id = request.data.get("intBranchId")
            bln_export = request.data.get("blnExport")
            int_product_id = request.data.get("intProductId")
            int_brand_id = request.data.get("intBrandId")
            bln_export = True
            str_querry =               """ select
                                          vchr_product_name,
                                          vchr_brand_name,
                                          vchr_item_name,
                                          count(vchr_item_name) as int_quantity,
                                          sum(reward_sum.reward_amount) as dbl_reward_amount,
                                          selling_price as dbl_selling_price,
                                          dbl_mop_amount,

                                          case when rewards.mop_percent >= ra.dbl_slab1_percentage then concat(ra.dbl_slab1_percentage :: TEXT, 'perc mop')
                                          when rewards.mop_percent < ra.dbl_slab1_percentage and rewards.mop_percent >= ra.dbl_slab2_percentage then concat(ra.dbl_slab2_percentage :: TEXT,'perc mop')
                                          when rewards.mop_percent < ra.dbl_slab2_percentage and rewards.mop_percent >= ra.dbl_slab3_percentage then concat(ra.dbl_slab3_percentage :: TEXT,'perc mop'  )
                                          else concat(rad.dbl_value_from :: TEXT, '-', rad.dbl_value_to :: TEXT,' ', 'price band')
                                          end as vchr_slab,

                                          reward_sum.branch_name as vchr_branch_name,
                                          reward_sum.int_branch_id,
                                          int_product_id,
                                          int_brand_id,
                                          int_item_id,
                                          reward_sum.int_territory_id,
                                          reward_sum.vchr_territory_name,
                                          reward_sum.int_zone_id,
                                          reward_sum.vchr_zone_name
                                        from
                                          (
                                            select
                                              rd.pk_bint_id as int_reward_id,
                                              rd.fk_rewards_master_id,
                                              rd.fk_rewards_details_id,
                                              em.vchr_enquiry_num,
                                              em.dat_created_at :: DATE,
                                              ie.dbl_amount - ie.dbl_discount_amount as selling_price,
                                              rd.dbl_mop_amount,
                                              ( ( ( ie.dbl_amount - ie.dbl_discount_amount )/ rd.dbl_mop_amount )* 100 ) as mop_percent,
                                              pd.vchr_product_name as vchr_product_name,
                                              bd.vchr_brand_name as vchr_brand_name,
                                              CONCAT(it.vchr_item_code,'-',it.vchr_item_name) as vchr_item_name,
                                              pd.id as int_product_id,
                                              bd.id as int_brand_id,
                                              it.id as int_item_id
                                            from
                                              rewards_available rd
                                              JOIN item_enquiry ie on ie.pk_bint_id = rd.fk_item_enquiry_id
                                              JOIN enquiry_master em on em.pk_bint_id = ie.fk_enquiry_master_id
                                              JOIN products pd on pd.id = ie.fk_product_id
                                              JOIN brands bd on bd.id = ie.fk_brand_id
                                              JOIN items it on it.id = ie.fk_item_id
                                            {date_filter}
                                            order by
                                              em.vchr_enquiry_num
                                          ) as rewards
                                          JOIN rewards_master ra on ra.pk_bint_id = rewards.fk_rewards_master_id
                                          JOIN rewards_details rad on rad.pk_bint_id = rewards.fk_rewards_details_id
                                          JOIN (
                                            select
                                              sum(sra.reward :: float) as reward_amount,
                                              sra.ra_id,
                                              sra.branch_name ,
                                              sra.int_branch_id,
                                              sra.int_territory_id,
                                              sra.vchr_territory_name,
                                              sra.int_zone_id,
                                              sra.vchr_zone_name
                                            from
                                              (
                                                select
                                                  json_staff ->> jsonb_object_keys(json_staff) as reward,
                                                  ra_id,
                                                  branch_name ,int_branch_id,int_territory_id,vchr_territory_name,int_zone_id,vchr_zone_name
                                                from
                                                  (
                                                    SELECT
                                                      json_staff,
                                                      sura.pk_bint_id as ra_id,
                                                      upper(br.vchr_name) as branch_name ,
                                                      br.pk_bint_id as int_branch_id,
                                                      tr.pk_bint_id as int_territory_id,
                                                      tr.vchr_name as vchr_territory_name,
                                                      zn.pk_bint_id as int_zone_id,
                                                      zn.vchr_name as vchr_zone_name

                                                    FROM
                                                      rewards_available sura
                                                      JOIN item_enquiry ies on ies.pk_bint_id = sura.fk_item_enquiry_id
                                                      JOIN enquiry_master em on em.pk_bint_id = ies.fk_enquiry_master_id
                                                      JOIN branch br on em.fk_branch_id = br.pk_bint_id
                                                      join territory tr on tr.pk_bint_id = br.fk_territory_id
                                                      join zone zn on zn.pk_bint_id = tr.fk_zone_id

                                                    {date_filter}
                                                  ) as staff_reward
                                              ) as sra
                                            group by
                                              2, 3,4,5,6,7,8
                                          ) as reward_sum on reward_sum.ra_id = rewards.int_reward_id
                                        where
                                          reward_sum.reward_amount > 0 {filter}"""


            #where em.dat_created_at::DATE between '2020-03-16' and '2020-03-31' group by 1,2,4,5,6,7 order by 3 desc"""
            """DATE WISE FILTER"""
            str_date_filter = " WHERE em.dat_created_at :: DATE BETWEEN '"+str(dat_from)+"' and '"+str(dat_to)+"'"
            str_filter = ''
            if int_product_id :
                str_filter += "AND rewards.int_product_id = "+str(int_product_id)+" "
            if int_brand_id :
                str_filter += "AND rewards.int_brand_id = "+str(int_brand_id)+" "

            if int_zone_id:
                str_filter += "AND reward_sum.int_zone_id = "+str(int_zone_id)+" "
            if int_ter_id:
                str_filter += "AND reward_sum.int_territory_id = "+str(int_ter_id)+" "
            if int_br_id:
                str_filter += "AND reward_sum.int_branch_id = "+str(int_br_id)+" "

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER BUSINESS OPERATIONS','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                str_filter_data +=" AND br.pk_bint_id = "+str(request.user.userdetails.fk_branch_id)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                str_filter += " AND reward_sum.int_branch_id IN ("+str(lst_branch)[1:-1]+")"


            # import pdb; pdb.set_trace()
            str_querry += "group by 1, 2, 3, 6, 7,8, 9 , 10, 11, 12, 13,14,15,16,17 order by 9 desc"
            str_querry = str_querry.format(date_filter = str_date_filter,filter = str_filter)
            # import pdb; pdb.set_trace()
            rst_data = conn.execute(str_querry).fetchall()
            lst_data = []
            if rst_data:
                lst_data = [dict(x) for x in rst_data]
                if bln_export:
                    data = slab_wise_reward_export(lst_data,request)
                    return Response({'status':1,'lst_data':lst_data,'export_data':data})

                return Response({'status':1,'lst_data' : lst_data} )
            else:
                return Response({'status':0,'message' :'No Data' })
        except Exception as e:
            return Response({'status':0,'reason' : str(e)})
def slab_wise_reward_export(lst_data,request):
    try:
        dat_from = request.data.get("datFrom")
        dat_to = request.data.get("datTo")
        dat_from = "2020-01-01"
        dat_to = "2020-05-29"
        str_filter = ''
        sheet_name1 = 'Sheet1'
        int_zone_id = request.data.get("intZoneId")
        int_ter_id = request.data.get("intTerId")
        int_br_id = request.data.get("intBranchId")

        int_product_id = request.data.get("intProductId")
        int_brand_id = request.data.get("intBrandId")

        str_filter_product =  'ALL'
        str_filter_brand ='ALL'
        if int_product_id :

            str_filter_product = Products.objects.filter(id = int_product_id).values('vchr_product_name').first()['vchr_product_name']

        if int_brand_id :

            str_filter_brand =Brands.objects.filter(id = int_brand_id).values('vchr_brand_name').first()['vchr_brand_name']

        # int_br_id = 20

        df = pd.DataFrame(lst_data)
        excel_file = settings.MEDIA_ROOT+'/slab_wise_reward_report.xlsx'
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df_export = pd.DataFrame()
        df_export['S.No'] = list(range(1,len(df.index)+1))
        # import pdb; pdb.set_trace()
        # df_export.index = pd.RangeIndex(start=1, stop=df.shape[0], step=1)
        str_area = ' '
        if int_zone_id:
            dct_zone = Zone.objects.filter(pk_bint_id = int_zone_id).values('vchr_name').first()
            str_area = 'Area (ZONE)           : '+(dct_zone.get('vchr_name') or '--')
            df_export['TERRITORY'] = df['vchr_territory_name']
            df_export['BRANCH'] = df['vchr_branch_name']
        elif int_ter_id:
            dct_territory = Territory.objects.filter(pk_bint_id = int_ter_id).values('vchr_name').first()
            str_area = 'Area (TERRITORY)   : '+dct_territory.get('vchr_name') or '--'
            df_export['BRANCH'] = df['vchr_branch_name']

        elif  int_zone_id==int_ter_id ==int_br_id == None:
            df_export['BRANCH'] = df['vchr_branch_name']
            str_area = 'Area                       : ALL'

        if int_br_id:
            dct_branch = Branch.objects.filter(pk_bint_id = int_br_id).values('vchr_name').first()
            str_area = 'Area (BRANCH)        : '+dct_branch.get('vchr_name') or '--'

        df_export['PRODUCT'] = df['vchr_product_name']
        df_export['BRAND'] = df['vchr_brand_name']
        df_export['ITEM'] = df['vchr_item_name']
        df_export['QUANTITY'] = df['int_quantity']
        df_export['REWARD AMOUNT'] = df['dbl_reward_amount']
        df_export['SELLING PRICE'] = df['dbl_selling_price']
        df_export['MOP AMOUNT'] = df['dbl_mop_amount']
        df_export['SLAB'] = df['vchr_slab'].str.replace('perc','%')
        df_export['BRANCH'] = df['vchr_branch_name']



        df_export.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=12, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name1]
        cell_format = workbook.add_format({'bold':True,'align': 'center'})
        str_report = 'Slab Wise Report'
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

        for i, col in enumerate(df_export.columns):

                # find length of column i
                column_len = df_export[col].astype(str).str.len().max()
                # Setting the length if the column header is larger
                # than the max column value length
                column_len = max(column_len, len(col)) + 2
                # set the column length
                worksheet.set_column(i, i, column_len)
        # import pdb; pdb.set_trace()
        worksheet.merge_range('A1+:K2', 'SLAB WISE REWARD REPORT', merge_format1)
        # worksheet.merge_range('A4+:B4', 'Area : '+','.join(lst_area))
        worksheet.merge_range('A4+:F4', 'Taken By                 : '+request.user.username, merge_format2)
        worksheet.merge_range('A5+:F5', 'Action Date             : '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
        worksheet.merge_range('A6+:F6', 'Reporting Period     : '+datetime.strftime((datetime.strptime(dat_from,'%Y-%m-%d')),'%d-%m-%Y') +' to '+ datetime.strftime((datetime.strptime(dat_to,'%Y-%m-%d')),'%d-%m-%Y'), merge_format2)

        worksheet.merge_range('A7+:F7',str_area, merge_format2)
        worksheet.merge_range('A8+:F8','Product                  : '+str_filter_product, merge_format2)
        worksheet.merge_range('A9+:F9','Brand                     : '+str_filter_brand, merge_format2)
        writer.save()
        data = settings.HOSTNAME+'/media/slab_wise_reward_report.xlsx'
        return data
    except Exception as e:
        return Response({'status':0,'reason' : str(e)})

class GroupTypeahead(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lstGroup = []
            if str_search_term != -1:
                lstGroup = list(Groups.objects.filter(fk_company = request.user.userdetails.fk_company_id,bln_status=True,vchr_name__icontains=str_search_term).values('pk_bint_id','vchr_name'))

            return Response({'status':'success','data':lstGroup})
        except Exception as e:
            return Response({'status':'failed','data':str(e)})
class PromoterSalesReport(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            date_from = request.data.get('dateFrom')
            date_to = request.data.get('dateTo')
            lst_brand = request.data.get('lstCsaBrand')
            lst_branch = request.data.get('lstBranch')
            lst_tm = request.data.get('lstTm')
            lst_zm = request.data.get('lstZm')
            bln_date = request.data.get('blnDate')
            dct_data = {}
            dct_prdct = {}
            dct_brand = {}
            dct_item = {}
            conn = engine.connect()
            if bln_date:
                 str_query = """select
                 sum(CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) as int_total_qnty,
                 sum(it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) as int_total_values,
                 sum(CASE WHEN itm.fk_product_id = (select id from products WHERE vchr_product_name = 'MOBILE') THEN (CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) ELSE 0 END) AS int_mob_qty,
                 sum(CASE WHEN itm.fk_product_id = (select id from products WHERE vchr_product_name = 'MOBILE') THEN (it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) ELSE 0 END) AS int_mob_values,
                 sum(CASE WHEN it_eq.fk_brand_id = brnd.id THEN (CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) ELSE 0 END) AS int_own_qty,
                 sum(CASE WHEN it_eq.fk_brand_id = brnd.id THEN (it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) ELSE 0 END) AS int_own_values,
                 sum(CASE WHEN it_eq.fk_brand_id != brnd.id OR usr_mdl.fk_brand_id IS NULL THEN (CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) ELSE 0 END) AS int_otr_qty,
                 sum(CASE WHEN it_eq.fk_brand_id != brnd.id OR usr_mdl.fk_brand_id IS NULL THEN (it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) ELSE 0 END) AS int_otr_values,
                 CONCAT(TRIM(au.first_name), ' ',TRIM(au.last_name)) AS str_emp_name,
                 au.username,tr.vchr_name as str_territory,
                 zn.vchr_name as str_zone,br.vchr_name as str_branch,

                 itm.id as item_id, bds.id as brand_id , prdcts.id as prct_id, itm.vchr_item_name, bds.vchr_brand_name,
                 prdcts.vchr_product_name,brnd.vchr_brand_name as str_staff_brand

                 from item_enquiry as it_eq
                 JOIN enquiry_master eq_mtr ON eq_mtr.pk_bint_id = it_eq.fk_enquiry_master_id
                 JOIN auth_user as au ON au.id = eq_mtr.fk_assigned_id
                 JOIN branch AS br ON br.pk_bint_id = eq_mtr.fk_branch_id
                 JOIN territory AS tr ON tr.pk_bint_id = br.fk_territory_id
                 JOIN zone AS zn ON zn.pk_bint_id = tr.fk_zone_id
                 JOIN items AS itm ON itm.id = it_eq.fk_item_id
                 JOIN products AS prdcts ON itm.fk_product_id = prdcts.id and prdcts.vchr_product_name != 'SMART CHOICE'
                 JOIN brands as bds ON itm.fk_brand_id = bds.id JOIN userdetails as usr_mdl ON usr_mdl.user_ptr_id = au.id
                 JOIN brands AS brnd ON usr_mdl.fk_brand_id = brnd.id where it_eq.vchr_enquiry_status in ('INVOICED','RETURNED','IMAGE PENDING') and it_eq.dat_sale ::DATE BETWEEN '"""+str(date_from)+"""' and '"""+str(date_to)+"""'"""

            else:
                 str_query = """select
                 sum(CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) as int_total_qnty,
                 sum(it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) as int_total_values,
                 sum(CASE WHEN itm.fk_product_id = (select id from products WHERE vchr_product_name = 'MOBILE') THEN (CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) ELSE 0 END) AS int_mob_qty,
                 sum(CASE WHEN itm.fk_product_id = (select id from products WHERE vchr_product_name = 'MOBILE') THEN (it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) ELSE 0 END) AS int_mob_values,
                 sum(CASE WHEN it_eq.fk_brand_id = brnd.id THEN (CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) ELSE 0 END) AS int_own_qty,
                 sum(CASE WHEN it_eq.fk_brand_id = brnd.id THEN (it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) ELSE 0 END) AS int_own_values,
                 sum(CASE WHEN it_eq.fk_brand_id != brnd.id OR usr_mdl.fk_brand_id IS NULL THEN (CASE WHEN it_eq.vchr_enquiry_status='RETURNED' THEN it_eq.int_sold * -1 ELSE it_eq.int_sold END) ELSE 0 END) AS int_otr_qty,
                 sum(CASE WHEN it_eq.fk_brand_id != brnd.id OR usr_mdl.fk_brand_id IS NULL THEN (it_eq.dbl_amount - dbl_buy_back_amount-dbl_discount_amount) ELSE 0 END) AS int_otr_values,
                 CONCAT(TRIM(au.first_name), ' ',TRIM(au.last_name)) AS str_emp_name,
                 au.username,it_eq.dat_sale::date,tr.vchr_name as str_territory,
                 zn.vchr_name as str_zone,br.vchr_name as str_branch,

                 itm.id as item_id, bds.id as brand_id , prdcts.id as prct_id, itm.vchr_item_name, bds.vchr_brand_name,
                 prdcts.vchr_product_name,brnd.vchr_brand_name as str_staff_brand

                 from item_enquiry as it_eq
                 JOIN enquiry_master eq_mtr ON eq_mtr.pk_bint_id = it_eq.fk_enquiry_master_id
                 JOIN auth_user as au ON au.id = eq_mtr.fk_assigned_id
                 JOIN branch AS br ON br.pk_bint_id = eq_mtr.fk_branch_id
                 JOIN territory AS tr ON tr.pk_bint_id = br.fk_territory_id
                 JOIN zone AS zn ON zn.pk_bint_id = tr.fk_zone_id
                 JOIN items AS itm ON itm.id = it_eq.fk_item_id
                 JOIN products AS prdcts ON itm.fk_product_id = prdcts.id and prdcts.vchr_product_name != 'SMART CHOICE'
                 JOIN brands as bds ON itm.fk_brand_id = bds.id JOIN userdetails as usr_mdl ON usr_mdl.user_ptr_id = au.id
                 JOIN brands AS brnd ON usr_mdl.fk_brand_id = brnd.id where it_eq.vchr_enquiry_status in ('INVOICED','RETURNED','IMAGE PENDING') and it_eq.dat_sale ::DATE BETWEEN '"""+str(date_from)+"""' and '"""+str(date_to)+"""'"""

            if request.data.get('lstBranch'):
                str_query += " AND br.pk_bint_id in ("+ str(lst_branch)[1:-1] +")"
            if request.data.get('lstTm'):
                str_query += " AND tr.pk_bint_id in ("+ str(lst_tm)[1:-1] +")"
            if request.data.get('lstZm'):
                str_query += " AND zn.pk_bint_id in ("+ str(lst_zm)[1:-1] +")"
            if request.data.get('lstCsaBrand'):
                str_query += " AND brnd.id in ("+ str(lst_brand)[1:-1] +")"
            if bln_date:
                str_query +=" group by au.first_name,au.last_name,au.username,tr.vchr_name,zn.vchr_name,br.vchr_name,au.first_name,au.last_name,itm.id,bds.id, prdcts.id,brnd.vchr_brand_name order by au.username"
            else:
                str_query +=" group by it_eq.dat_sale :: date,au.first_name,au.last_name,au.username,tr.vchr_name,zn.vchr_name,br.vchr_name,itm.id,bds.id, prdcts.id,brnd.vchr_brand_name order by it_eq.dat_sale :: date,au.first_name"

            rst_data = conn.execute(str_query).fetchall()
            dct_data = {}
            dct_data = OrderedDict()

            for ins_data in rst_data:

                if bln_date:
                    dct_temp = ins_data.username
                else:
                    dct_temp = ins_data.username +'_'+str(ins_data.dat_sale)
                if dct_temp not in dct_data:
                    dct_data[dct_temp] = {}
                    dct_data[dct_temp]['intTotalQnty'] = 0
                    dct_data[dct_temp]['intTotalValues'] = 0
                    dct_data[dct_temp]['intMobQty'] = 0
                    dct_data[dct_temp]['intMobValues'] = 0
                    dct_data[dct_temp]['intOwnQty'] = 0
                    dct_data[dct_temp]['intOwnValues'] = 0
                    dct_data[dct_temp]['intOtrQty'] = 0
                    dct_data[dct_temp]['intOtrValues'] = 0
                if bln_date:
                    dct_data[dct_temp]['dateSale'] = None
                else:
                    dct_data[dct_temp]['dateSale'] = ins_data.dat_sale
                dct_data[dct_temp]['strStaffName'] = ins_data.str_emp_name
                dct_data[dct_temp]['strBranch'] = ins_data.str_branch
                dct_data[dct_temp]['strTerritory'] = ins_data.str_territory
                dct_data[dct_temp]['strZone'] = ins_data.str_zone
                dct_data[dct_temp]['strStaffBrand'] = ins_data.str_staff_brand
                dct_data[dct_temp]['intTotalQnty'] += ins_data.int_total_qnty  if ins_data.int_total_qnty else 0
                dct_data[dct_temp]['intTotalValues'] += ins_data.int_total_values if ins_data.int_total_values else 0
                dct_data[dct_temp]['intMobQty'] += ins_data.int_mob_qty if ins_data.int_mob_qty else 0
                dct_data[dct_temp]['intMobValues'] += ins_data.int_mob_values if ins_data.int_mob_values else 0
                dct_data[dct_temp]['intOwnQty'] += ins_data.int_own_qty if ins_data.int_own_qty else 0
                dct_data[dct_temp]['intOwnValues'] += ins_data.int_own_values if ins_data.int_own_values else 0
                dct_data[dct_temp]['intOtrQty'] += ins_data.int_otr_qty if ins_data.int_otr_qty else 0
                dct_data[dct_temp]['intOtrValues'] += ins_data.int_otr_values if ins_data.int_otr_values else 0
                if ins_data.prct_id not in dct_data[dct_temp]:
                    dct_data[dct_temp][ins_data.prct_id] = {}
                    dct_data[dct_temp][ins_data.prct_id]['intTotalQnty'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intTotalValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intMobQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intMobValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intOwnQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intOwnValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intOtrQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id]['intOtrValues'] = 0
                dct_data[dct_temp][ins_data.prct_id]['strProductName'] = ins_data.vchr_product_name
                dct_data[dct_temp][ins_data.prct_id]['intTotalQnty'] += ins_data.int_total_qnty if ins_data.int_total_qnty else 0
                dct_data[dct_temp][ins_data.prct_id]['intTotalValues'] += ins_data.int_total_values if ins_data.int_total_values else 0
                dct_data[dct_temp][ins_data.prct_id]['intMobQty'] += ins_data.int_mob_qty if ins_data.int_mob_qty else 0
                dct_data[dct_temp][ins_data.prct_id]['intMobValues'] += ins_data.int_mob_values if ins_data.int_mob_values else 0
                dct_data[dct_temp][ins_data.prct_id]['intOwnQty'] += ins_data.int_own_qty if ins_data.int_own_qty else 0
                dct_data[dct_temp][ins_data.prct_id]['intOwnValues'] += ins_data.int_own_values if ins_data.int_own_values else 0
                dct_data[dct_temp][ins_data.prct_id]['intOtrQty'] += ins_data.int_otr_qty if ins_data.int_otr_qty else 0
                dct_data[dct_temp][ins_data.prct_id]['intOtrValues'] += ins_data.int_otr_values if ins_data.int_otr_values else 0
                if ins_data.brand_id not in dct_data[dct_temp][ins_data.prct_id]:
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id] = {}
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intTotalQnty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intTotalValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intMobQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intMobValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOwnQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOwnValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOtrQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOtrValues'] = 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['strBrandName'] = ins_data.vchr_brand_name
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intTotalQnty'] += ins_data.int_total_qnty if ins_data.int_total_qnty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intTotalValues'] += ins_data.int_total_values if ins_data.int_total_values else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intMobQty'] += ins_data.int_mob_qty if ins_data.int_mob_qty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intMobValues'] += ins_data.int_mob_values if ins_data.int_mob_values else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOwnQty'] += ins_data.int_own_qty if ins_data.int_own_qty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOwnValues'] += ins_data.int_own_values if ins_data.int_own_values else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOtrQty'] += ins_data.int_otr_qty if ins_data.int_otr_qty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]['intOtrValues'] += ins_data.int_otr_values if ins_data.int_otr_values else 0
                if ins_data.item_id not in dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id]:
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id] = {}
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intTotalQnty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intTotalValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intMobQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intMobValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOwnQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOwnValues'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOtrQty'] = 0
                    dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOtrValues'] = 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['strItemName'] = ins_data.vchr_item_name
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intTotalQnty'] += ins_data.int_total_qnty if ins_data.int_total_qnty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intTotalValues'] += ins_data.int_total_values if ins_data.int_total_values else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intMobQty'] += ins_data.int_mob_qty if ins_data.int_mob_qty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intMobValues'] += ins_data.int_mob_values if ins_data.int_mob_values else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOwnQty'] += ins_data.int_own_qty if ins_data.int_own_qty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOwnValues'] += ins_data.int_own_values if ins_data.int_own_values else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOtrQty'] += ins_data.int_otr_qty if ins_data.int_otr_qty else 0
                dct_data[dct_temp][ins_data.prct_id][ins_data.brand_id][ins_data.item_id]['intOtrValues'] += ins_data.int_otr_values if ins_data.int_otr_values else 0


            lst_data = []
            for data in dct_data.values():
                dct_sale = {}
                if not bln_date:
                    dct_sale['dateSale'] = datetime.strftime(data['dateSale'],'%d-%m-%Y')
                dct_sale['strTerritory'] = data['strTerritory']
                dct_sale['strZone'] = data['strZone']
                dct_sale['strBranch'] = data['strBranch']
                dct_sale['strStaffName'] = data['strStaffName']
                dct_sale['intTotalQnty'] = data['intTotalQnty']
                dct_sale['intTotalValues'] = round(data['intTotalValues'], 2)
                dct_sale['intMobQty'] = data['intMobQty']
                dct_sale['intMobValues'] = round(data['intMobValues'], 2)
                dct_sale['intOwnQty'] = data['intOwnQty']
                dct_sale['intOwnValues'] = round(data['intOwnValues'], 2)
                dct_sale['intOtrQty'] = data['intOtrQty']
                dct_sale['intOtrValues'] = round(data['intOtrValues'], 2)
                dct_sale['strStaffBrand'] = data['strStaffBrand']
                tp1 = ('dateSale','strTerritory','strZone','strBranch','strStaffName','intTotalQnty','intTotalValues','intMobQty','intMobValues','intOwnQty','intOwnValues','intOtrQty','intOtrValues','strStaffBrand')
                tp2 = tuple(data.keys())
                lst_pdct_id = list(set(tp2)-set(tp1))
                lst_product = []
                for pr_item in lst_pdct_id:
                    dct_prdt = {}
                    dct_prdt['strProductName'] = data[pr_item]['strProductName']
                    dct_prdt['intTotalQnty'] = data[pr_item]['intTotalQnty']
                    dct_prdt['intTotalValues'] = round(data[pr_item]['intTotalValues'], 2)
                    dct_prdt['intMobQty'] = data[pr_item]['intMobQty']
                    dct_prdt['intMobValues'] = round(data[pr_item]['intMobValues'], 2)
                    dct_prdt['intOwnQty'] = data[pr_item]['intOwnQty']
                    dct_prdt['intOwnValues'] = round(data[pr_item]['intOwnValues'], 2)
                    dct_prdt['intOtrQty'] = data[pr_item]['intOtrQty']
                    dct_prdt['intOtrValues'] = round(data[pr_item]['intOtrValues'], 2)
                    tp3 = {'intTotalQnty','intTotalValues','intMobQty','intMobValues','intOwnQty','intOwnValues','intOtrQty','intOtrValues','strProductName'}
                    tp4 = tuple(data[pr_item].keys())
                    lst_brand_id = list(set(tp4)-set(tp3))
                    lst_brand = []
                    for brd_item in lst_brand_id:
                        dct_brd = {}
                        dct_brd['strBrandName'] = data[pr_item][brd_item]['strBrandName']
                        dct_brd['intTotalQnty'] = data[pr_item][brd_item]['intTotalQnty']
                        dct_brd['intTotalValues'] = round(data[pr_item][brd_item]['intTotalValues'], 2)
                        dct_brd['intMobQty'] = data[pr_item][brd_item]['intMobQty']
                        dct_brd['intMobValues'] = round(data[pr_item][brd_item]['intMobValues'], 2)
                        dct_brd['intOwnQty'] = data[pr_item][brd_item]['intOwnQty']
                        dct_brd['intOwnValues'] = round(data[pr_item][brd_item]['intOwnValues'], 2)
                        dct_brd['intOtrQty'] = data[pr_item][brd_item]['intOtrQty']
                        dct_brd['intOtrValues'] = round(data[pr_item][brd_item]['intOtrValues'], 2)
                        tp5 = {'intTotalQnty','intTotalValues','intMobQty','intMobValues','intOwnQty','intOwnValues','intOtrQty','intOtrValues','strBrandName'}
                        tp6 = tuple(data[pr_item][brd_item].keys())
                        lst_item_id = list(set(tp6)-set(tp5))
                        lst_item = []
                        for item_item in lst_item_id:
                            dct_item = {}
                            dct_item['strItemName'] = data[pr_item][brd_item][item_item]['strItemName']
                            dct_item['intTotalQnty'] = data[pr_item][brd_item][item_item]['intTotalQnty']
                            dct_item['intTotalValues'] = round(data[pr_item][brd_item][item_item]['intTotalValues'], 2)
                            dct_item['intMobQty'] = data[pr_item][brd_item][item_item]['intMobQty']
                            dct_item['intMobValues'] = round(data[pr_item][brd_item][item_item]['intMobValues'], 2)
                            dct_item['intOwnQty'] = data[pr_item][brd_item][item_item]['intOwnQty']
                            dct_item['intOwnValues'] = round(data[pr_item][brd_item][item_item]['intOwnValues'], 2)
                            dct_item['intOtrQty'] = data[pr_item][brd_item][item_item]['intOtrQty']
                            dct_item['intOtrValues'] = round(data[pr_item][brd_item][item_item]['intOtrValues'], 2)
                            lst_item.append(dct_item)
                        dct_brd['lstItem'] = lst_item
                        lst_brand.append(dct_brd)
                    dct_prdt['lstBrand'] = lst_brand
                    lst_product.append(dct_prdt)
                dct_sale['lstProduct'] = lst_product
                lst_data.append(dct_sale)
            return Response({'status':1,'data':lst_data})
        except Exception as e:
            return Response({'status':'failed','reason':str(e)})

    def get(self,request):
        try:
            dct_details = {}
            ins_branch = list(Branch.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            ins_brands = list(Brands.objects.annotate(name=Upper('vchr_brand_name')).values('id','name'))
            ins_territory = list(Territory.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            ins_zone = list(Zone.objects.annotate(id=F('pk_bint_id'),name=Upper('vchr_name')).values('id','name'))
            dct_details['branch']=ins_branch
            dct_details['brand']=ins_brands
            dct_details['territory']=ins_territory
            dct_details['zone']=ins_zone
            return Response({'status':1,'data':dct_details})
        except Exception as e:
            return Response({'status':'failed','data':str(e)})



""" COMPARISON REPORT FOR SHOWING SALES OCCURED FOR THE GIVEN TARGET GROUP IN TWO DATE RANGES"""
class TargetAchieveComparisonReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            cur = Session()
            # import pdb; pdb.set_trace()
            str_query = """
                        SELECT ms.int_type as qty_amount_status, ms.vchr_name as target_name, ms.pk_bint_id as target_id,
                        SUM(CASE WHEN ms.int_type = 1 {date_1} THEN COALESCE(mv.sold_quantity,0) ELSE 0 END) as date_range_one_qty, SUM(CASE WHEN ms.int_type = 2 {date_1} THEN COALESCE(mv.sold_amount,0) ELSE 0 END) as date_range_one_amount,
                        SUM(CASE WHEN ms.int_type = 1 {date_2} THEN COALESCE(mv.sold_quantity,0) ELSE 0 END) as date_range_two_qty, SUM(CASE WHEN ms.int_type = 2 {date_2} THEN COALESCE(mv.sold_amount,0) ELSE 0 END) as date_range_two_amount
                        FROM target_group_master as ms
                        JOIN target_group_details as dt_inc on ms.pk_bint_id = dt_inc.fk_target_group_master_id and dt_inc.int_type = 1 and ms.int_status = 1
                        JOIN target_group_details as dt_exc on ms.pk_bint_id = dt_exc.fk_target_group_master_id and dt_exc.int_type = 2 and ms.int_status = 1
                        LEFT JOIN
                        (SELECT (CASE WHEN eq.vchr_enquiry_status = 'RETURNED' THEN -1*(eq.int_sold) ELSE eq.int_sold END) as sold_quantity, eq.total_amount as sold_amount, eq.dat_enquiry as dat_enquiry,
                        eq.product_id as product_id, eq.brand_id as brand_id, eq.id as id, it.fk_category_id as fk_category_id, it.fk_item_group_id as fk_item_group_id
                        FROM mv_enquiry_data as eq JOIN items as it on it.id = eq.id
                        WHERE eq.vchr_enquiry_status in ('INVOICED','IMAGE PENDING','RETURNED') and eq.product_id not in (SELECT id from products WHERE vchr_product_name = 'SMART CHOICE') {branch_filter} {zone_filter} {territory_filter}) as mv on
                        ((jsonb_array_length(dt_inc.lst_product) > 0  and dt_inc.lst_product @> mv.product_id::text::jsonb) or (jsonb_array_length(dt_inc.lst_product) = 0  and NOT dt_inc.lst_product @> mv.product_id::text::jsonb))
                        and
                        ((jsonb_array_length(dt_inc.lst_item) > 0 and dt_inc.lst_item @> mv.id::text::jsonb) or (jsonb_array_length(dt_inc.lst_item) = 0 and NOT dt_inc.lst_item @> mv.id::text::jsonb))
                        and
                        ((jsonb_array_length(dt_inc.lst_brand) >0 and dt_inc.lst_brand @> mv.brand_id::text::jsonb) or (jsonb_array_length(dt_inc.lst_brand) =0 and NOT dt_inc.lst_brand @> mv.brand_id::text::jsonb))
                        and
                        ((jsonb_array_length(dt_inc.lst_item_category) >0 and dt_inc.lst_item_category @> mv.fk_category_id::text::jsonb) or (jsonb_array_length(dt_inc.lst_item_category) = 0 and NOT dt_inc.lst_item_category @> mv.fk_category_id::text::jsonb))
                        and
                        ((jsonb_array_length(dt_inc.lst_item_group) >0 and dt_inc.lst_item_group @> mv.fk_item_group_id::text::jsonb) or (jsonb_array_length(dt_inc.lst_item_group) = 0 and NOT dt_inc.lst_item_group @> mv.fk_item_group_id::text::jsonb))
                        and NOT dt_exc.lst_product @> mv.product_id::text::jsonb
                        and NOT dt_exc.lst_item @> mv.id::text::jsonb
                        and NOT dt_exc.lst_brand @> mv.brand_id::text::jsonb
                        and NOT dt_exc.lst_item_category @> mv.fk_category_id::text::jsonb
                        and NOT dt_exc.lst_item_group @> mv.fk_item_group_id::text::jsonb
                        GROUP BY ms.pk_bint_id,ms.int_type,ms.vchr_name
                        ORDER BY ms.pk_bint_id
                        """


            date_1 = " AND mv.dat_enquiry :: DATE >= '"+request.data.get('date_from1') + "' AND mv.dat_enquiry :: DATE <= '" + request.data.get('date_to1')+" '"
            date_2 = " AND mv.dat_enquiry :: DATE >= '"+request.data.get('date_from2') + "' AND mv.dat_enquiry :: DATE <= '" + request.data.get('date_to2')+" '"
            branch_filter = ''
            territory_filter = ''
            zone_filter = ''
            if len(request.data.get("lst_branch"))>0:
                branch_filter = " AND eq.branch_id in (" + str(request.data.get("lst_branch")).split('[')[1].split(']')[0] +") "
            if len(request.data.get("lst_territory"))>0:
                territory_filter = "AND eq.territory_id in (" + str(request.data.get("lst_territory")).split('[')[1].split(']')[0] +") "
            if len(request.data.get("lst_zone"))>0:
                zone_filter = "AND eq.zone_id in (" + str(request.data.get("lst_zone")).split('[')[1].split(']')[0] +") "

            str_query = str_query.format(date_1 = date_1,date_2=date_2,branch_filter=branch_filter,territory_filter=territory_filter,zone_filter=zone_filter)
            target_comparison = cur.execute(str_query).fetchall()
            # target_comparison = cur.fetchall()
            date_range1 = datetime.strftime((datetime.strptime(request.data.get('date_from1'),'%Y-%m-%d')),'%d-%m-%Y') + " to " +datetime.strftime((datetime.strptime(request.data.get('date_to1'),'%Y-%m-%d')),'%d-%m-%Y')
            date_range2 = datetime.strftime((datetime.strptime(request.data.get('date_from2'),'%Y-%m-%d')),'%d-%m-%Y') + " to " +datetime.strftime((datetime.strptime(request.data.get('date_to2'),'%Y-%m-%d')),'%d-%m-%Y')
            # dct = [{'qty_amount_status':1,'target_name':'smart phone','date_range_one_amount':35000,'date_range_two_amount':45000,'date_range_one_qty':250,'date_range_two_qty':350},{'qty_amount_status':2,'target_name':'smart phone','date_range_one_amount':55000,'date_range_two_amount':50000,'date_range_one_qty':150,'date_range_two_qty':100}]
            cur.close()
            return Response({'status':1,'data':target_comparison,'date_range1': date_range1,'date_range2': date_range2})

        except Exception as e:
            cur.close()
            return Response({'status':'failed','data':str(e)})

    def put(self,request):
        try:
            ##view for showing zones ,territory and branches on the basis of each ones selection from  the front end
            zone = request.data.get('zone')
            territory = request.data.get('territory')

            if len(zone) == 0 and len(territory) == 0:
                lst_zone = Zone.objects.all().values('vchr_name','pk_bint_id')
                lst_territory = Territory.objects.all().values('vchr_name','pk_bint_id')
                lst_branch = Branch.objects.all().values('vchr_name','pk_bint_id')
                return Response({'status':1, 'lst_branch': lst_branch, 'lst_territory': lst_territory, 'lst_zone': lst_zone,'int_status':0})

            elif len(zone) > 0 :
                if len(territory) >0:
                    lst_branch = Branch.objects.filter(fk_territory_id__in = territory).values('vchr_name','pk_bint_id')
                    return Response({'status':1, 'lst_branch': lst_branch,'int_status':2})

                else:
                    lst_territory = Territory.objects.filter(fk_zone_id__in = zone).values('vchr_name','pk_bint_id')
                    territory_ids = list(lst_territory.values_list('pk_bint_id',flat=True))
                    lst_branch = Branch.objects.filter(fk_territory_id__in = territory_ids).values('vchr_name','pk_bint_id')
                    return Response({'status':1, 'lst_branch': lst_branch, 'lst_territory': lst_territory,'int_status':1})

            elif len(territory) > 0:
                lst_branch = Branch.objects.filter(fk_territory_id__in = territory).values('vchr_name','pk_bint_id')
                return Response({'status':1, 'lst_branch': lst_branch,'int_status':2})

        except Exception as e:
            return Response({'status':'failed','data':str(e)})
