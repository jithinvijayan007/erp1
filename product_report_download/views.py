from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from branch.models import Branch
from aldjemy.core import get_engine
from collections import OrderedDict
from POS import ins_logger
import base64
from sqlalchemy.orm.session import sessionmaker
from enquiry_mobile.models import ItemEnquiry
# from inventory.models import Products,Brands,Items

from item_category.models import Item as Items
from brands.models import Brands
from products.models import Products
from globalMethods import show_data_based_on_role,chart_data_sort,get_user_products
from sqlalchemy import func,case,literal_column,cast,Date,and_
from django.contrib.auth.models import User
from enquiry.models import EnquiryMaster
from adminsettings.models import AdminSettings
from customer.models import CustomerDetails as CustomerModel
from userdetails.models import UserDetails as UserModel
from branch.models import Branch
from django.core.mail import EmailMultiAlternatives
from os import remove
from pdfGenerate import generate_pdf
from generateExcel import generate_excel

ItemEnquirySA =ItemEnquiry.sa
ProductSA = Products.sa
AuthUserSA = User.sa
EnquiryMasterSA = EnquiryMaster.sa
CustomerSA = CustomerModel.sa
ItemsSA=Items.sa
BrandsSA=Brands.sa
UserSA=UserModel.sa
BranchSA = Branch.sa

from datetime import datetime
from datetime import timedelta
import pdfkit

def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()
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

# def ReportData(request):
#     try:
#         lst_enquiry_data = []
#         if request.data.get('show_type'):
#             str_show_type = 'total_amount'
#         else:
#             str_show_type = 'int_quantity'
#         int_company = request.user.usermodel.fk_company_id
#
#         fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#         todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#         dct_data={}
#
#         engine = get_engine()
#         conn = engine.connect()
#
#         lst_mv_view = []
#         lst_mv_view = request.data.get('lst_mv')
#
#         if not lst_mv_view:
#             return JsonResponse({'status':'failed', 'reason':'No view list found'})
#         query_set = ''
#         if len(lst_mv_view) == 1:
#
#             if request.data['type'].upper() == 'ENQUIRY':
#
#                 query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name, user_id as fk_assigned, staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id"
#             else:
#
#                 query = "select vchr_enquiry_status, sum("+str_show_type+") as counts, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name,user_id as fk_assigned,staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id"
#
#         else:
#
#             if request.data['type'].upper() == 'ENQUIRY':
#
#                 for data in lst_mv_view:
#                     query_set += "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned, branch_id, product_id, brand_id,staff_first_name, staff_last_name from "+data+" {} group by  vchr_enquiry_status , vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned, branch_id, product_id, brand_id,staff_first_name, staff_last_name union "
#             else:
#
#                  for data in lst_mv_view:
#
#                     query_set +="select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned, vchr_brand_name, vchr_item_name,promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name, staff_last_name from "+data+" {} group by vchr_enquiry_status, vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter,is_resigned,branch_id, product_id, brand_id,staff_first_name, staff_last_name union "
#
#             query = query_set.rsplit(' ', 2)[0]
#
#         """ data wise filtering """
#         str_filter_data = "where dat_enquiry :: date BETWEEN '"+request.data['date_from']+"' AND '"+request.data['date_to']+"' AND int_company_id = "+str(int_company)+""
#
#
#         """Permission wise filter for data"""
#         if request.user.usermodel.fk_group.vchr_name.upper()=='ADMIN':
#             pass
#         elif request.user.usermodel.fk_group.vchr_name.upper()=='BRANCH MANAGER':
#
#             str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.usermodel.fk_branch_id)+""
#         elif request.user.usermodel.int_area_id:
#             lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#
#             str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"
#         else:
#             return Response({'status':'failed','reason':'No data'})
#
#         if request.data.get('branch'):
#             branch = request.data.get('branch')
#
#             str_filter_data += " AND branch_id = "+str(branch)+""
#         if request.data.get('staff'):
#             staff = request.data.get('staff')
#
#             str_filter_data += " AND user_id = "+str(staff)+""
#         if request.data.get('product'):
#
#             str_filter_data += " AND product_id = "+str(request.data.get('product'))+""
#         if request.data.get('brand'):
#
#             str_filter_data += " AND brand_id = "+str(request.data.get('brand'))+""
#
#         if len(lst_mv_view) == 1:
#             query = query.format(str_filter_data)
#         else:
#             query = query.format(str_filter_data,str_filter_data)
#         rst_enquiry = conn.execute(query).fetchall()
#         dct_data={}
#         dct_data['service_all']={}
#         dct_data['brand_all']={}
#         dct_data['item_all']={}
#         dct_data['staff_all']={}
#         dct_data['status_all']={}
#         dct_data['service_brand']={}
#         dct_data['service_item']={}
#         dct_data['service_staff']={}
#         dct_data['service_status']={}
#         dct_data['service_brand_item']={}
#         dct_data['service_brand_staff']={}
#         dct_data['service_brand_status']={}
#         dct_data['service_brand_item_staff']={}
#         dct_data['service_brand_item_status']={}
#         dct_data['service_brand_item_staff_status']={}
#         dct_data['staffs']={}
#
#         for ins_data in rst_enquiry:
#             if ins_data.vchr_service not in dct_data['service_all']:
#                 dct_data['service_all'][ins_data.vchr_service]={}
#                 dct_data['service_all'][ins_data.vchr_service]['Enquiry']=ins_data.counts
#                 dct_data['service_all'][ins_data.vchr_service]['Sale']=0
#
#                 if ins_data.vchr_enquiry_status == 'INVOICED':
#                     dct_data['service_all'][ins_data.vchr_service]['Sale']=ins_data.counts
#
#                 dct_data['service_brand'][ins_data.vchr_service]={}
#                 dct_data['service_item'][ins_data.vchr_service]={}
#                 dct_data['service_staff'][ins_data.vchr_service]={}
#                 dct_data['service_status'][ins_data.vchr_service]={}
#                 dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                 dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]={}
#                 dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]={}
#                 dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
#                 dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
#                 dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
#                 dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                 dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#
#                 dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=0
#                 dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=0
#                 dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']=0
#                 dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
#
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
#                     dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
#                     dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']=1
#                     dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#
#                 dct_data['service_brand_item'][ins_data.vchr_service]={}
#                 dct_data['service_brand_staff'][ins_data.vchr_service]={}
#                 dct_data['service_brand_status'][ins_data.vchr_service]={}
#                 dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                 dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                 dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#
#                 dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
#                 dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]= {}
#                 dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]= {}
#
#                 dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
#                 dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=0
#                 dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#
#                 dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
#                 dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                 dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
#                     dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                     dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#
#                 dct_data['service_brand_item_staff'][ins_data.vchr_service]={}
#                 dct_data['service_brand_item_status'][ins_data.vchr_service]={}
#                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#
#                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned] = {}
#                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]= {}
#
#
#                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
#                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#
#                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#
#
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                     dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service]={}
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status] = {}
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                 dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
#
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#             else:
#                 dct_data['service_all'][ins_data.vchr_service]['Enquiry']+=ins_data.counts
#
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['service_all'][ins_data.vchr_service]['Sale'] += ins_data.counts
#
#
#                 if ins_data.vchr_brand_name.title() not in dct_data['service_brand'][ins_data.vchr_service]:
#                     dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()] = {}
#                     dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry']= ins_data.counts
#                     dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']= 0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale']= ins_data.counts
#                 else:
#                     dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
#
#                 if ins_data.vchr_item_name.title() not in dct_data['service_item'][ins_data.vchr_service]:
#                     dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()] = {}
#                     dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry'] = ins_data.counts
#                     dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = 0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale'] = ins_data.counts
#                 else:
#                     dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Enquiry'] += ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_item'][ins_data.vchr_service][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
#
#                 if ins_data.fk_assigned not in dct_data['service_staff'][ins_data.vchr_service]:
#                     dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned] = {}
#                     dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Enquiry'] = ins_data.counts
#                     dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']= 0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']= ins_data.counts
#                 else:
#                     dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Enquiry'] += ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_staff'][ins_data.vchr_service][ins_data.fk_assigned]['Sale']+=ins_data.counts
#
#                 if ins_data.vchr_enquiry_status not in dct_data['service_status'][ins_data.vchr_service]:
#                     dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]={}
#                     dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#                 else:
#                     dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_status'][ins_data.vchr_service][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
#
#                 if ins_data.vchr_brand_name.title() not in dct_data['service_brand_item'][ins_data.vchr_service]:
#                     dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                     dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                     dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#
#                     dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                     dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]={}
#                     dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
#
#                     dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#
#                     dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
#                     dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=0
#                     dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
#                         dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                         dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#                 else:
#                     if ins_data.vchr_item_name.title() not in dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
#                         dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()] = {}
#                         dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
#                         dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
#                     else:
#                         dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_item'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
#
#                     if ins_data.fk_assigned not in dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
#                         dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]={}
#                         dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                         dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=0
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                     else:
#                         dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.fk_assigned]['Sale']+=ins_data.counts
#
#                     if ins_data.vchr_enquiry_status not in dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
#                         dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]={}
#                         dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                         dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#                     else:
#                         dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
#                 if ins_data.vchr_brand_name.title() not in dct_data['service_brand_item_staff'][ins_data.vchr_service]:
#                     dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                     dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                     dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                     dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                     dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
#                     dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
#                     dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
#                     dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                         dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#                 else:
#                     if ins_data.vchr_item_name.title() not in dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
#                         dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                         dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                         dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
#                         dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
#                         dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                         dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                         dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
#                         dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#                         if ins_data.vchr_enquiry_status == 'BOOKED':
#                             dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                             dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#                     else:
#                         if ins_data.fk_assigned not in dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
#                             dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
#                             dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                             dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=0
#                             if ins_data.vchr_enquiry_status == 'BOOKED':
#                                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']=ins_data.counts
#                         else:
#                             dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
#                             if ins_data.vchr_enquiry_status == 'BOOKED':
#                                 dct_data['service_brand_item_staff'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]['Sale']+=ins_data.counts
#
#                         if ins_data.vchr_enquiry_status not in dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
#                             dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]={}
#                             dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                             dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=0
#                             if ins_data.vchr_enquiry_status == 'BOOKED':
#                                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#                         else:
#                             dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
#                             if ins_data.vchr_enquiry_status == 'BOOKED':
#                                 dct_data['service_brand_item_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
#
#                 if ins_data.vchr_brand_name.title() not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service]:
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#                 elif ins_data.vchr_item_name.title() not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()]:
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#                 elif ins_data.fk_assigned not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title().title()][ins_data.fk_assigned]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#                 elif ins_data.vchr_enquiry_status not in dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned]:
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]={}
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=0
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']=ins_data.counts
#
#                 else:
#                     dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
#                     if ins_data.vchr_enquiry_status == 'BOOKED':
#                         dct_data['service_brand_item_staff_status'][ins_data.vchr_service][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.fk_assigned][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
#             if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
#                 dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
#                 dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
#                 dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
#
#             else:
#                 dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
#
#             if ins_data.vchr_item_name.title() not in dct_data['item_all']:
#                 dct_data['item_all'][ins_data.vchr_item_name.title()]={}
#                 dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
#                 dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
#                 if ins_data.vchr_enquiry_status =='BOOKED':
#                     dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
#             else:
#                 dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
#             if ins_data.fk_assigned not in dct_data['staff_all']:
#                 dct_data['staffs'][ins_data.fk_assigned]=str(ins_data.staff_first_name+" "+ins_data.staff_last_name).title()
#                 dct_data['staff_all'][ins_data.fk_assigned]={}
#                 dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']=ins_data.counts
#                 dct_data['staff_all'][ins_data.fk_assigned]['Sale']=0
#                 if ins_data.vchr_enquiry_status =='BOOKED':
#                     dct_data['staff_all'][ins_data.fk_assigned]['Sale']=ins_data.counts
#             else:
#                 dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']+=ins_data.counts
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['staff_all'][ins_data.fk_assigned]['Sale']+=ins_data.counts
#             if ins_data.vchr_enquiry_status not in dct_data['status_all']:
#                 dct_data['status_all'][ins_data.vchr_enquiry_status]={}
#                 dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']=ins_data.counts
#                 dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']=0
#             else:
#                 dct_data['status_all'][ins_data.vchr_enquiry_status]['Enquiry']+=ins_data.counts
#                 if ins_data.vchr_enquiry_status == 'BOOKED':
#                     dct_data['status_all'][ins_data.vchr_enquiry_status]['Sale']+=ins_data.counts
#         if request.data['type'] == 'Sale':
#             dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
#             dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
#             dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
#             dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)
#             for key in dct_data['service_brand']:
#                     dct_data['service_brand'][key]=paginate_data(request,dct_data['service_brand'][key],10)
#             for key in dct_data['service_item']:
#                     dct_data['service_item'][key]=paginate_data(request,dct_data['service_item'][key],10)
#             for key in dct_data['service_staff']:
#                     dct_data['service_staff'][key]=paginate_data(request,dct_data['service_staff'][key],10)
#             for key in dct_data['service_brand_item']:
#                 for key1 in dct_data['service_brand_item'][key]:
#                     dct_data['service_brand_item'][key][key1]=paginate_data(request,dct_data['service_brand_item'][key][key1],10)
#             for key in dct_data['service_brand_staff']:
#                 for key1 in dct_data['service_brand_staff'][key]:
#                     dct_data['service_brand_staff'][key][key1]=paginate_data(request,dct_data['service_brand_staff'][key][key1],10)
#             for key in dct_data['service_brand_item_staff']:
#                 for key1 in dct_data['service_brand_item_staff'][key]:
#                     for key2 in dct_data['service_brand_item_staff'][key][key1]:
#                         dct_data['service_brand_item_staff'][key][key1][key2]=paginate_data(request,dct_data['service_brand_item_staff'][key][key1][key2],10)
#         elif request.data['type'] == 'Enquiry':
#             dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
#             dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
#             dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
#             for key in dct_data['service_brand']:
#                     dct_data['service_brand'][key]=paginate_data(request,dct_data['service_brand'][key],10)
#             for key in dct_data['service_item']:
#                     dct_data['service_item'][key]=paginate_data(request,dct_data['service_item'][key],10)
#             for key in dct_data['service_brand_item']:
#                 for key1 in dct_data['service_brand_item'][key]:
#                     dct_data['service_brand_item'][key][key1]=paginate_data(request,dct_data['service_brand_item'][key][key1],10)
#         return (dct_data)
#     except Exception as msg:
#             return Response({'status':'failed','data':str(msg)})
#
# def TableData(request):
#     try:
#         session = Session()
#         lst_enquiry_data = []
#         ins_company = request.user.usermodel.fk_company_id
#
#         fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#         todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#         dct_data={}
#         session=Session()
#         rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status,
#                             ProductSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
#                             AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),(CustomerSA.cust_fname+" "+CustomerSA.cust_lname).label('customer_full_name'),
#                             AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
#                             AuthUserSA.first_name.label('staff_first_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
#                             UserSA.fk_brand_id,UserSA.dat_resignation_applied,
#                             case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
#                                 else_=literal_column("'not resigned'")).label("is_resigned"))\
#                             .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
#                                     cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
#                                     EnquiryMasterSA.fk_company_id == request.user.usermodel.fk_company_id,
#                                     EnquiryMasterSA.chr_doc_status == 'N')\
#                             .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                             .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#                             .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                             .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#                             .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
#                             .join(ProductSA,ProductSA.id == ItemEnquirySA.fk_product_id)\
#                             .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
#                             .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)
#         """Permission wise filter for data"""
#         if request.user.usermodel.fk_group.vchr_name.upper()=='ADMIN':
#             pass
#         elif request.user.usermodel.fk_group.vchr_name.upper()=='BRANCH MANAGER':
#             rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
#         elif request.user.usermodel.int_area_id:
#             lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#             rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
#         else:
#             return Response({'status':'failed','reason':'No data'})
#
#
#         if request.data.get('branch'):
#             branch = request.data.get('branch')
#             rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == branch)
#         if request.data.get('staff'):
#             staff = request.data.get('staff')
#             rst_enquiry = rst_enquiry.filter(AuthUserSA.id == staff)
#         if request.data.get('product'):
#             rst_enquiry = rst_enquiry.filter(rst_data.c.vchr_service == request.data.get('product'))
#         if request.data.get('brand'):
#             rst_enquiry = rst_enquiry.filter(rst_data.c.brand_id == request.data.get('brand'))
#
#         return(list(rst_enquiry.all()))
#     except Exception as e:
#         ins_logger.logger.error(str(e))
#         return Response({'status':'0','data':str(e)})
#
#
# class ProductReportPDF(APIView):
#     def post(self,request):
#         try:
#             lst_file=[]
#             sale_color = AdminSettings.objects.filter(fk_company=request.user.usermodel.fk_company_id,vchr_code='SALES_COLOUR',bln_enabled=True).values('vchr_value')
#             if sale_color:
#                 sale_color = sale_color[0]['vchr_value'][0]
#             else:
#                 sale_color = '#aec7e8'
#             enquiry_color = AdminSettings.objects.filter(fk_company=request.user.userdetails.fk_company_id,vchr_code='ENQUIRY_COLOUR',bln_enabled=True).values('vchr_value')
#             if enquiry_color:
#                 enquiry_color=enquiry_color[0]['vchr_value'][0]
#             else:
#                 enquiry_color = '#1f77b4'
#             lst_color=[enquiry_color,sale_color]
#             pdf_path = settings.MEDIA_ROOT+'/'
#             if request.data['bln_chart']:
#                 dct_data=ReportData(request)
#                 if 'status' in dct_data and dct_data['status']=='failed':
#                     JsonResponse({'status':'failed','data':dct_data['data']})
#                 if request.data['type']=='Sale':
#
#                     lst_details = ['service_all','brand_all','item_all','staff_all']
#                     dct_label = {'service_all':'Product wise','brand_all':'Brand wise','item_all':'Item wise','staff_all':'Staff wise'}
#                     dct_details={}
#                     for details in lst_details:
#                         lst_item = ['x']
#                         lst_enquiry = ['Enquiry']
#                         lst_sale = ['Sale']
#                         tbl_data =''
#                         i=1
#                         for item in dct_data[details][1]:
#                             name=''
#                             if details=='staff_all':
#                                 name=dct_data['staffs'][item]
#                             else:
#                                 name=item
#                             if len(name)>31:
#                                 name=name[:29]+"..."
#                             lst_item.append(i)
#                             lst_enquiry.append(int(dct_data[details][1][item]['Enquiry']))
#                             lst_sale.append(int(dct_data[details][1][item]['Sale']))
#                             tbl_data+='<tr><td>'+str(i)+'</td><td>'+str(name)+'</td><td align="right">'+str(dct_data[details][1][item]['Enquiry'])+'</td><td align="right">'+str(dct_data[details][1][item]['Sale'])+'</td></tr>'
#                             i+=1
#                         dct_details[details]=[dct_label[details],lst_item,lst_enquiry,lst_sale,tbl_data]
#
#
#                     html_data = """<!DOCTYPE HTML>
#                                     <html>
#                                     <head>
#                                         <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
#                                         <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
#                                         <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>
#                                         <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
#                                     </head>
#                                     <body style="font-family: sans-serif; font-size: 14px;">
#                                       <div style="width:1000px; height:100%; margin:0 auto; padding:0px 30px; float:center; border:1px solid #000;">
#
#                                           <h3 class="text-center"><b>Product Report</b></h3>
#
#                                             <div class="row" style="padding:15px;">
#                                               <div class="col-sm-7 col-xs-7">
#                                                 <div class="row"><div class="col-sm-3 col-xs-3"><b>From</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
#                                                 <div class="row"><div class="col-sm-3 col-xs-3"><b>To</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
#                                                 <div class="row"><div class="col-sm-3 col-xs-3"><b>Taken By</b></div><div class="col-sm-9 col-xs-9">"""+request.user.first_name+" "+request.user.last_name+"""</div></div>
#                                               </div>
#                                               <div class="col-sm-5 col-xs-5">"""
#                     if request.data.get('branch'):
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b> </div><div class="col-sm-7 col-xs-7">"""+Branch.objects.get(pk_bint_id=int(request.data['branch'])).vchr_name.capitalize()+"""</div></div>"""
#                     else:
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b></div><div class="col-sm-7 col-xs-7">All</div></div>"""
#                     if request.data.get('staff'):
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">"""+str(dct_data['staffs'][request.data['staff']])+"""</div></div>"""
#                     else:
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">All</div></div>"""
#                     html_data+="""<div class="row"><div class="col-sm-5 col-xs-5"><b>Action Date</b></div><div class="col-sm-7 col-xs-7"><span>"""+datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p")+"""</span></div></div></div></div>"""
#                     for details in lst_details:
#                         html_data+="""<div>
#                                             <div class="text-center"style="padding:15px;"><b>"""+dct_details[details][0].upper()+"""</b></div>
#                                             <div class="row">
#                                                 <div class="col-sm-6 col-xs-6" >
#                                                     <div id='"""+details+"""'></div>
#                                                 </div>
#                                                 <div class="col-sm-6 col-xs-6"><div>
#                                                   <table class="table" style="padding-top:25px;">
#                                                     <thead>
#                                                       <tr>
#                                                         <td><b>#</b></td>
#                                                         <td><b>"""+dct_details[details][0].rstrip("wise")+"""</b></td>
#                                                         <td align="right"><b>Enquiry</b></td>
#                                                         <td align="right"><b>Sale</b></td>
#                                                       </tr>
#                                                     </thead>
#                                                     <tbody>
#                                                       """+dct_details[details][4]+"""
#                                                     </tbody>
#                                                   </table></div>
#                                                 </div>
#                                             </div>
#                                           </div>"""
#                     html_data+="""</div></body>
#                                      <script>"""
#                     for details in lst_details:
#                         html_data+="""
#                                        var """+details+""" = c3.generate({
#                                          bindto:'#"""+details+"""',
#                                          data: {
#                                            x : 'x',
#                                            columns: ["""+str(dct_details[details][1])+""","""+str(dct_details[details][2])+""","""+str(dct_details[details][3])+"""
#                                            ],
#                                            type: 'bar'
#                                          },
#                                          axis: {
#                                            x: {
#                                              type: 'category'
#                                            }
#                                          },
#                                          color: {
#                                              pattern: """+str(lst_color)+"""
#                                          },
#                                          bar: {
#                                              width: 15
#                                          }
#                                         });"""
#
#                     html_data+=""" </script>
#                                     </html>"""
#                     filename =  'Report.pdf'
#                     options = {
#                                 'page-size': 'A4',
#                                 'margin-top': '10.00mm',
#                                 'margin-right': '10.00mm',
#                                 'margin-bottom': '10.00mm',
#                                 'margin-left': '10.00mm',
#                                 'dpi':400,
#                             }
#                     pdfkit.from_string(html_data,pdf_path+filename, options=options)
#                     lst_file.append(filename)
#
#             if request.data['bln_table']:
#                 dct_data=TableData(request)
#                 if 'status' in dct_data and dct_data['status']=='0':
#                     return Response({'status':'0','data':dct_data['data']})
#                 if request.data['type']:
#                     html_data = """<!DOCTYPE HTML>
#                                     <html>
#                                     <head>
#                                         <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css" rel="stylesheet" />
#                                         <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
#                                         <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>
#                                         <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
#                                     </head>
#                                     <body style="font-family: sans-serif; font-size: 14px;">
#                                       <div style="width:1000px; height:100%; margin:0 auto; padding:0px 30px; float:center; border:1px solid #000;">
#
#                                           <h3 class="text-center"><b>Product Report</b></h4>
#
#                                             <div class="row" style="padding:15px;">
#                                               <div class="col-sm-7 col-xs-7">
#                                                 <div class="row"><div class="col-sm-3 col-xs-3"><b>From</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
#                                                 <div class="row"><div class="col-sm-3 col-xs-3"><b>To</b></div><div class="col-sm-9 col-xs-9">"""+datetime.strftime(datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ),"%d-%m-%Y")+"""</div></div>
#                                                 <div class="row"><div class="col-sm-3 col-xs-3"><b>Taken By</b></div><div class="col-sm-9 col-xs-9">"""+request.user.first_name+" "+request.user.last_name+"""</div></div>
#                                               </div>
#                                               <div class="col-sm-5 col-xs-5">"""
#                     if request.data.get('branch'):
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b> </div><div class="col-sm-7 col-xs-7">"""+Branch.objects.get(pk_bint_id=int(request.data['branch'])).vchr_name.capitalize()+"""</div></div>"""
#                     else:
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Branch</b></div><div class="col-sm-7 col-xs-7">All</div></div>"""
#                     if request.data.get('staff'):
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">"""+dct_data[0][2]+"""</div></div>"""
#                     else:
#                         html_data += """<div class="row"><div class="col-sm-5 col-xs-5"><b>Staff</b> </div><div class="col-sm-7 col-xs-7">All</div></div>"""
#                     html_data+="""<div class="row"><div class="col-sm-5 col-xs-5"><b>Action Date</b></div><div class="col-sm-7 col-xs-7"><span>"""+datetime.strftime(datetime.now(),"%d-%m-%Y , %I:%M %p")+"""</span></div></div></div></div>
#                     <div style="padding-top:20px">
#                         <table class="table">
#                             Date<thead>
#                                 <tr>
#                                     <th scope="">Enquiry</th>
#                                     <th scope="col">Staff</th>
#                                     <th scope="col">Product</th>
#                                     <th scope="col">Brand</th>
#                                     <th scope="col">Item</th>
#                                     <th scope="col">Status</th>
#                                 </tr>
#                             </thead>
#                             <tbody>"""
#                     for table in dct_data:
#                         html_data += '''<tr>
#                                             <td>'''+table[4]+'''</td>
#                                             <td>'''+table[2]+'''</td>
#                                             <td>'''+table[1]+'''</td>
#                                             <td>'''+table[10]+'''</td>
#                                             <td>'''+table[11]+'''</td>
#                                             <td>'''+table[0]+'''</td>
#
#                                         </tr>'''
#                                         # if len(table[11])>35:
#                                         #     # import pdb; pdb.set_trace()
#                                         #     html_data += "<td>"+table[11][:35]++"</td>"
#                                         # else:
#                                         #     html_data += "<td>"+table[11]+"</td>"
#                                         #
#                                         # html_data +=        '''<td>'''+table[0]+'''</td>
#                     html_data+='''</tbody>
#                         </div>
#                         </main>
#                       </div>
#                      </body>
#                      <script>
#                      </script>
#                     </html>
#                     '''
#                     filename = 'TableData.pdf'
#                     options = {
#                                 'page-size': 'A4',
#                                 'margin-top': '10.00mm',
#                                 'margin-right': '10.00mm',
#                                 'margin-bottom': '10.00mm',
#                                 'margin-left': '10.00mm',
#                                 'dpi':400,
#                             }
#                     pdfkit.from_string(html_data,pdf_path+filename, options=options)
#                     lst_file.append(filename)
#             if request.data.get('export_type') == 'DOWNLOAD':
#                 # filename = lst_file[0]
#                 fs = FileSystemStorage()
#                 lst_encoded_string=[]
#                 for filename in lst_file:
#                     if fs.exists(pdf_path+filename):
#                         with fs.open(pdf_path+filename) as pdf:
#                             lst_encoded_string.append(str(base64.b64encode(pdf.read())))
#                 return Response({'status':'success','file':lst_encoded_string,'file_name':lst_file})
#             elif request.data.get('export_type') == 'MAIL':
#                 to = request.data.get('email').split(",")
#                 subject =  'Report Print'
#                 from_email = settings.EMAIL_HOST_EMAIL
#                 text_content = 'Travidux'
#                 html_content = '''Dear '''
#                 mail = EmailMultiAlternatives(subject, text_content, from_email, to)
#                 mail.attach_alternative(html_content, "text/html")
#                 for file in lst_file:
#                     mail.attach_file(pdf_path+file)
#                     remove(pdf_path+file)
#                 mail.send()
#                 return Response({'status':'success'})
#         except Exception as e:
#             ins_logger.logger.error(str(e))
#             return Response({'status':'0','data':str(e)})


class ProductReportDOwnload(APIView):
    def post(self,request):
        try:
            # import pdb;pdb.set_trace()
            lst_enquiry_data = []
            int_company = request.user.userdetails.fk_company_id

            fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
            todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
            dct_data={}

            engine = get_engine()
            conn = engine.connect()

            if request.data['bln_chart']:
                str_sort = request.data.get('strGoodPoorClicked','NORMAL')
                int_page = int(request.data.get('intCurrentPage',1))
                if request.data.get('show_type'):
                    str_show_type = 'total_amount'
                else:
                    str_show_type = 'int_quantity'
                lst_mv_view = []
                lst_mv_view = request.data.get('lst_mv')

                if not lst_mv_view:
                    return JsonResponse({'status':'failed', 'reason':'No view list found'})
                query_set = ''
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
                str_filter_data = "where dat_enquiry :: date BETWEEN '"+request.data['date_from']+"' AND '"+request.data['date_to']+"' AND int_company_id = "+str(int_company)+""


                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:

                    str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.userdetails.fk_branch_id)+""
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                    str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"
                else:
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
                    return Response({'status':'failed','message':'No data'})
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
                        dct_data['service_all'][ins_data.vchr_service]['Enquiry']=int(ins_data.counts)
                        dct_data['service_all'][ins_data.vchr_service]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_all'][ins_data.vchr_service]['Sale']=int(ins_data.counts)
                    else:
                        dct_data['service_all'][ins_data.vchr_service]['Enquiry']+=int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_all'][ins_data.vchr_service]['Sale'] += int(ins_data.counts)

                    if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=int(ins_data.counts)
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=int(ins_data.counts)
                    else:
                        dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=int(ins_data.counts)

                    if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                        dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=int(ins_data.counts)
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
                        if ins_data.vchr_enquiry_status =='INVOICED':
                            dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=int(ins_data.counts)
                    else:
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=int(ins_data.counts)

                    if ins_data.fk_assigned not in dct_data['staff_all']:
                        dct_data['staffs'][ins_data.fk_assigned]=str(ins_data.staff_first_name+" "+ins_data.staff_last_name).title()
                        dct_data['staff_all'][ins_data.fk_assigned]={}
                        dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']=int(ins_data.counts)
                        dct_data['staff_all'][ins_data.fk_assigned]['Sale']=0
                        if ins_data.vchr_enquiry_status =='INVOICED':
                            dct_data['staff_all'][ins_data.fk_assigned]['Sale']=int(ins_data.counts)
                    else:
                        dct_data['staff_all'][ins_data.fk_assigned]['Enquiry']+=int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['staff_all'][ins_data.fk_assigned]['Sale']+=int(ins_data.counts)

                    if ins_data.vchr_enquiry_status not in dct_data['status_all']:
                        dct_data['status_all'][ins_data.vchr_enquiry_status]=int(ins_data.counts)
                    else:
                        dct_data['status_all'][ins_data.vchr_enquiry_status]+=int(ins_data.counts)

                if request.data['type'] == 'Sale':
                    dct_data['staff_all']=paginate_data(request,dct_data['staff_all'],10)
                    dct_data['staff_all'] = chart_data_sort(request,dct_data['staff_all'],'NORMAL',1)

                dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
                dct_data['service_all'] = chart_data_sort(request,dct_data['service_all'],str_sort,int_page)
                dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
                dct_data['brand_all']=chart_data_sort(request,dct_data['brand_all'],'NORMAL',1)

                dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
                dct_data['item_all']=chart_data_sort(request,dct_data['item_all'],'NORMAL',1)

                if request.data['type'].upper() == 'ENQUIRY':
                    str_report_name = 'Product Enquiry Report'
                    lst_details = ['service_all-bar','brand_all-bar','item_all-bar','staff_all-pie','status_all-pie']
                    dct_label = {'service_all':'Product wise','brand_all':'Brand wise','item_all':'Item wise','status_all':'Status wise','staff_all':'Staff wise'}
                else:
                    str_report_name = 'Product Sales Report'
                    lst_details = ['service_all-bar','brand_all-bar','item_all-bar','staff_all-bar']
                    dct_label = {'service_all':'Product wise','brand_all':'Brand wise','item_all':'Item wise','staff_all':'Staff wise'}

            if request.data['bln_table']:
                if request.data['type'].upper() == 'ENQUIRY':
                    str_report_name = 'Product Enquiry Report'
                else:
                    str_report_name = 'Product Sales Report'

                session = Session()
                lst_enquiry_data = []
                ins_company = request.user.userdetails.fk_company_id

                # import pdb; pdb.set_trace()
                #for getting user corresponding products
                lst_user_id =[]
                lst_user_id.append(request.user.id)
                lst_user_products = get_user_products(lst_user_id)



                fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
                todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
                # import pdb;pdb.set_trace()
                rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status,
                                    ProductSA.vchr_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
                                    AuthUserSA.last_name).label('vchr_staff_full_name'),func.DATE(EnquiryMasterSA.dat_created_at).label('dat_created_at'),EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),(CustomerSA.vchr_name).label('customer_full_name'),
                                    AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
                                    AuthUserSA.first_name.label('staff_first_name'),BrandsSA.vchr_name.label('vchr_brand_name'),ItemsSA.vchr_name.label('vchr_item_name'),
                                    UserSA.fk_brand_id,UserSA.dat_resignation_applied,
                                    case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
                                        else_=literal_column("'not resigned'")).label("is_resigned"))\
                                    .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
                                            cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
                                            EnquiryMasterSA.fk_company_id == request.user.userdetails.fk_company_id,
                                            EnquiryMasterSA.chr_doc_status == 'N')\
                                    .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                    .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                    .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.pk_bint_id)\
                                    .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                    .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
                                    .join(ProductSA,ProductSA.pk_bint_id == ItemEnquirySA.fk_product_id)\
                                    .join(BrandsSA,BrandsSA.pk_bint_id==ItemEnquirySA.fk_brand_id)\
                                    .join(ItemsSA,ItemsSA.pk_bint_id==ItemEnquirySA.fk_item_id)\
                                    .group_by(ItemEnquirySA.vchr_enquiry_status,ProductSA.vchr_name,AuthUserSA.first_name,AuthUserSA.last_name,\
                                    EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_assigned_id,CustomerSA.vchr_name,\
                                    AuthUserSA.id,AuthUserSA.last_name,AuthUserSA.first_name,BrandsSA.vchr_name,ItemsSA.vchr_name,UserSA.fk_brand_id,UserSA.dat_resignation_applied,'is_resigned')
                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})


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
                if lst_user_products:
                    rst_enquiry = rst_enquiry.filter(ProductSA.id.in_(lst_user_products))

                if not rst_enquiry.all():
                    session.close()
                    return Response({'status':'failed','reason':'No data'})


                lst_tbl_head = ['Enquiry No','Staff','Product','Brand','Item','Status']
                lst_tbl_index = [4,2,1,10,11,0]

            if request.data['document'].upper() == 'PDF':
                if request.data['bln_table'] and request.data['bln_chart']:
                    file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))
                elif request.data['bln_chart']:
                    file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data)
                elif request.data['bln_table']:
                    file_output = generate_pdf(request,str_report_name,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))

                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":1,'file':file_output['file'],'file_name':file_output['file_name']})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":1})
            elif request.data['document'].upper() == 'EXCEL':
                if request.data['bln_table'] and request.data['bln_chart']:
                    data=generate_excel(request,str_report_name,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))
                elif request.data['bln_chart']:
                    data=generate_excel(request,str_report_name,lst_details,dct_label,dct_data)
                elif request.data['bln_table']:
                    data=generate_excel(request,str_report_name,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))

                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":1,"file":data})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":1})

        except Exception as e:
            ins_logger.logger.error(str(e))
            #session.close()
            return Response({'status':'0','data':str(e)})
