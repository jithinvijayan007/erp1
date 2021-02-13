from aldjemy.core import get_engine
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from POS import ins_logger
from enquiry.models import EnquiryMaster,AddAttachments,Document
# from inventory.models import Brands,Items,Products
from products.models import Products
from brands.models import Brands
from item_category.models import Item as Items
from userdetails.models import UserDetails as UserModel
from customer.models import CustomerDetails as  CustomerModel
from branch.models import Branch
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.http import JsonResponse
import random
from adminsettings.models import AdminSettings
from django.core.files.storage import FileSystemStorage
from os import remove
from django.core.mail import EmailMultiAlternatives
from export_excel.views import export_excel
from collections import OrderedDict
from sqlalchemy import case, literal_column, desc, tuple_, select, table, column
from sqlalchemy.orm.session import sessionmaker
import aldjemy
from sqlalchemy.orm import mapper,aliased
from sqlalchemy import and_,func,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy.types import TypeDecorator,BigInteger
from enquiry_mobile.models import MobileEnquiry, TabletEnquiry, ComputersEnquiry, AccessoriesEnquiry,ItemEnquiry
import pdfkit
import base64
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
# from enquiry_mobile.tasks import print_fun
from django.conf import settings
# from enquiry_mobile.tasks import email_sent
from pdfGenerate import generate_pdf
from generateExcel import generate_excel

import numpy as np
import time
# from POS.graph import *
from django.db.models import Q
from globalMethods import show_data_based_on_role,chart_data_sort,get_user_products

EnquiryMasterSA = EnquiryMaster.sa
BranchSA = Branch.sa
CustomerModelSA = CustomerModel.sa
AuthUserSA = User.sa
UserModelSA = UserModel.sa
AddAttachmentsSA = AddAttachments.sa
DocumentSA = Document.sa
BrandsSA = Brands.sa
ItemsSA = Items.sa
ProductsSA = Products.sa
ItemEnquirySA = ItemEnquiry.sa

MobileEnquirySA = MobileEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
ComputersEnquirySA = ComputersEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
# BrandsSA=Brands.sa
# ItemsSA=Items.sa
def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind = engine)
    return _Session()
# Create your views here.
def key_sort_sale(tup):
    key,data = tup
    return data['Sale']
def key_sort(tup):
    key,data = tup
    return data['Enquiry']
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


class ProductivityReportDownload(APIView):
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            staffs = []
            start = datetime.now()
            session = Session()

            str_username = request.user.username
            if str_username:
                ins_user = UserModel.objects.get(username = str_username)
            lst_table_data = []
            dat_from_date = datetime.strptime(request.data.get('date_from'), "%Y-%m-%d").date()
            dat_to_date = datetime.strptime(request.data.get('date_to'), "%Y-%m-%d").date()
            if request.data['bln_chart']:
                str_sort = request.data.get('strGoodPoorClicked','NORMAL')
                int_page = int(request.data.get('intCurrentPage',1))
                if request.data.get('show_type'):
                    str_show_type = 'total_amount'
                else:
                    str_show_type = 'int_quantity'

                if request.data.get('staffs'):
                    for staffs_id in request.data.get('staffs'):
                        staffs.append(staffs_id['id'])
                lst_mviews = request.data['lst_mv']
                # nisam_materilized views
                engine = get_engine()
                conn = engine.connect()
                lst_branch_id = []
                str_filter = ''

                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    str_filter += " branch_id ="+str(request.user.userdetails.fk_branch_id)
                elif request.user.userdetails.int_area_id:
                    lst_branch_id=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    str_filter += " branch_id in ("+str(lst_branch_id)[1:-1]+")"
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})

                 # '''Get with Branch'''
                if request.data.get('branch'):
                    if len(str_filter):
                        str_filter += " AND branch_id = "+str(request.data.get('branch'))
                    else:
                        str_filter += " branch_id = "+str(request.data.get('branch'))

                # staff filter
                if request.data.get('staffs'):
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
                        query = "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+lst_mviews[0]+" where"+str_filter+"'AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned"
                    else:
                        query = "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+lst_mviews[0]+" where"+str_filter+"' AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned"
                else:
                    if request.data['type'].upper() == 'ENQUIRY':
                        for data in lst_mviews:
                            query_set += "select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+data+" where"+str_filter+"' AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned union "
                    else:
                        for data in lst_mviews:
                            query_set +="select vchr_enquiry_status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned from "+data+" where"+str_filter+"' AND int_company_id = "+str(ins_user.fk_company_id)+" group by vchr_enquiry_status,vchr_service,vchr_staff_full_name,fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned union "
                    query = query_set.rsplit(' ', 2)[0]
                rst_table_data = conn.execute(query).fetchall()

                if not rst_table_data:
                    session.close()
                    return Response({'status':'0','reason':'No data'})

                dct_data={}
                lst_table_data = []
                dct_data['assigne_all']={}
                dct_data['service_all']={}
                dct_data['brand_all']={}
                dct_data['item_all']={}
                dct_data['status_all']={}

                for ins_data in rst_table_data:

                    if ins_data.vchr_staff_full_name not in dct_data['assigne_all']:
                        dct_data['assigne_all'][ins_data.vchr_staff_full_name]={}
                        dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Enquiry'] = int(ins_data.counts)
                        dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] = int(ins_data.counts)
                    else:
                        dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Enquiry'] += int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['assigne_all'][ins_data.vchr_staff_full_name]['Sale'] += int(ins_data.counts)


                    if ins_data.vchr_service not in dct_data['service_all']:
                        dct_data['service_all'][ins_data.vchr_service]={}
                        dct_data['service_all'][ins_data.vchr_service]['Enquiry']=int(ins_data.counts)
                        dct_data['service_all'][ins_data.vchr_service]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_all'][ins_data.vchr_service]['Sale'] = int(ins_data.counts)
                    else:
                        dct_data['service_all'][ins_data.vchr_service]['Enquiry']+= int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['service_all'][ins_data.vchr_service]['Sale']+= int(ins_data.counts)


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
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = 0
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale'] = int(ins_data.counts)
                    else:
                        dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=int(ins_data.counts)
                        if ins_data.vchr_enquiry_status == 'INVOICED':
                            dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=int(ins_data.counts)

                    if ins_data.vchr_enquiry_status not in dct_data['status_all']:
                        dct_data['status_all'][ins_data.vchr_enquiry_status]=int(ins_data.counts)
                    else:
                        dct_data['status_all'][ins_data.vchr_enquiry_status]+=int(ins_data.counts)

                dct_data['assigne_all']=paginate_data(request,dct_data['assigne_all'],10)
                dct_data['assigne_all']=chart_data_sort(request,dct_data['assigne_all'],str_sort,int_page)

                dct_data['brand_all']=paginate_data(request,dct_data['brand_all'],10)
                dct_data['brand_all']=chart_data_sort(request,dct_data['brand_all'],'NORMAL',1)
                dct_data['item_all']=paginate_data(request,dct_data['item_all'],10)
                dct_data['item_all']=chart_data_sort(request,dct_data['item_all'],'NORMAL',1)
                dct_data['service_all']=paginate_data(request,dct_data['service_all'],10)
                dct_data['service_all']=chart_data_sort(request,dct_data['service_all'],'NORMAL',1)

                if request.data['type'].upper() == 'ENQUIRY':
                    str_report_name = 'Productivity Enquiry Report'
                    lst_details = ['assigne_all-bar','service_all-bar','brand_all-bar','item_all-bar','status_all-pie']
                    dct_label = {'assigne_all':'Staff wise','service_all':'Product wise','brand_all':'Brand wise','item_all':'Item wise','status_all':'Status wise'}
                else:
                    str_report_name = 'Productivity Sales Report'
                    lst_details = ['assigne_all-bar','service_all-bar','brand_all-bar','item_all-bar']
                    dct_label = {'assigne_all':'Staff wise','service_all':'Product wise','brand_all':'Brand wise','item_all':'Item wise'}


            if request.data['bln_table']:
                 if request.data['type'].upper() == 'ENQUIRY':
                     str_report_name = 'Productivity Enquiry Report'
                 else:
                     str_report_name = 'Productivity Sales Report'
                 str_username = request.data.get('username',False)
                 if str_username:
                     ins_user = UserModel.objects.get(username = str_username)

                 dat_from_date = datetime.strptime(request.data['date_from'], "%Y-%m-%d").date()
                 dat_to_date = datetime.strptime(request.data['date_to'], "%Y-%m-%d").date()
                 if request.data.get('staffs'):
                     for staffs_id in request.data.get('staffs'):
                         staffs.append(staffs_id['id'])

                 rst_table_data = session.query(ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_name.label('vchr_service')\
                                         ,func.concat(AuthUserSA.first_name,'',AuthUserSA.last_name).label('vchr_staff_full_name'),EnquiryMasterSA.vchr_enquiry_num\
                                         ,func.DATE(EnquiryMasterSA.dat_created_at).label('dat_created_at'),EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),BranchSA.vchr_name\
                                         ,AuthUserSA.id.label('user_id'),BrandsSA.vchr_name,ItemsSA.vchr_name,UserModelSA.fk_brand_id\
                                         ,UserModelSA.dat_resignation,case([(UserModelSA.fk_brand_id > 0,literal_column("'promoter'"))]\
                                         ,else_=literal_column("'not promoter'")).label('is_promoter'),case([(UserModelSA.dat_resignation<datetime.now()\
                                         ,literal_column("'resigned'"))],else_=literal_column("'not resigned'")).label("is_resigned")\
                                         ,(CustomerModelSA.vchr_name).label('customer_full_name'))\
                                         .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_from_date,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_to_date, EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N')\
                                         .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                         .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                         .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.pk_bint_id)\
                                         .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                         .join(UserModelSA, AuthUserSA.id == UserModelSA.user_ptr_id )\
                                         .join(ProductsSA,ProductsSA.pk_bint_id == ItemEnquirySA.fk_product_id)\
                                         .join(BrandsSA,BrandsSA.pk_bint_id == ItemEnquirySA.fk_brand_id)\
                                         .join(ItemsSA,ItemsSA.pk_bint_id == ItemEnquirySA.fk_item_id)


                 """Permission wise filter for data"""
                 if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                     pass
                 elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                 elif request.user.userdetails.int_area_id:
                     lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
                 else:
                     session.close()
                     return Response({'status':'0','reason':'No data'})

                 # staff filter
                 if request.data.get('staffs'):
                     rst_table_data=rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(tuple([i['id'] for i in request.data.get('staffs',[])])))
                 if request.data.get('promoters'):
                     lst_promoters = UserModel.objects.filter(fk_brand_id__in = promoters).values_list('user_ptr_id',flat = True)
                     rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_assigned_id.in_(lst_promoters))

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

                 if request.data.get('brand'):
                     rst_table_data = rst_table_data.filter(rst_data.c.brand_id == request.data.get('brand'))

                 # import pdb; pdb.set_trace()
                 #for getting user corresponding products
                 lst_user_id =[]
                 lst_user_id.append(request.user.id)
                 lst_user_products = get_user_products(lst_user_id)

                 if lst_user_products:
                      rst_table_data = rst_table_data.filter(ProductsSA.id.in_(lst_user_products))


                 if not rst_table_data.all():
                     session.close()
                     return Response({'status':'0','reason':'No data'})

                 lst_tbl_head = ['Enquiry No','Staff','Product','Brand','Item','Status']
                 lst_tbl_index = [3,2,1,8,9,0]

            if request.data['document'].upper() == 'PDF':

                if request.data['bln_table'] and request.data['bln_chart']:
                    file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_table_data.all()))
                elif request.data['bln_chart']:
                    file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data)
                elif request.data['bln_table']:
                    file_output = generate_pdf(request,str_report_name,lst_tbl_head,lst_tbl_index,list(rst_table_data.all()))
                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":"1",'file':file_output['file'],'file_name':file_output['file_name']})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":"1"})

            elif request.data['document'].upper() == 'EXCEL':
                if request.data['bln_table'] and request.data['bln_chart']:
                    data=generate_excel(request,str_report_name,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_table_data.all()))
                elif request.data['bln_chart']:
                    data=generate_excel(request,str_report_name,lst_details,dct_label,dct_data)
                elif request.data['bln_table']:
                    data=generate_excel(request,str_report_name,lst_tbl_head,lst_tbl_index,list(rst_table_data.all()))

                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":"1","file":data})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":"1"})

        except Exception as e:
            session.close()
            ins_logger.logger.error(str(e))
            return Response({'status':'0','data':str(e)})
