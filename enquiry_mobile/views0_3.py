
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import and_,func ,cast,Date,or_
from sqlalchemy import desc
import json

from source.models import Source
from branch.models import Branch
from priority.models import Priority
from sqlalchemy import between

# from hasher.views import hash_enquiry
from enquiry_print.views import enquiry_print

from django.http import JsonResponse
from django.contrib.auth.models import User
from userdetails.models import UserDetails as UserModel,Financiers
from enquiry.models import EnquiryMaster,Document
from stock_app.models import Stockmaster,Stockdetails
from source.models import Source
from priority.models import Priority
from customer.models import CustomerDetails as CustomerModel
from customer_rating.models import CustomerRating
from company.models import Company as CompanyDetails
from datetime import datetime,timedelta
from django.db import transaction
from sqlalchemy import desc
# from globalMethods import show_data_based_on_role

from location.models import Country as Countries
from zone.models import Zone
from territory.models import Territory
from location.models import State
from na_enquiry.models import NaEnquiryMaster,NaEnquiryDetails
from enquiry_mobile.models import Notification,GDPRange

# from django.conf import settings

from enquiry_mobile.models import MobileEnquiry, MobileFollowup, TabletEnquiry, TabletFollowup, ComputersEnquiry,ItemEnquiry,ItemFollowup, ComputersFollowup, AccessoriesEnquiry, AccessoriesFollowup,Notification,ItemExchange

# from inventory.models import Brands, Products, Items
from brands.models import Brands
from products.models import  Products
from item_category.models import Item as Items
from django.db.models import Case,  Value, When,F
from django.db.models import Q

from POS.dftosql import Savedftosql
from sqlalchemy import create_engine,inspect,MetaData,Table,Column,select,func
from sqlalchemy.orm import sessionmaker

# from globalMethods import notifications_data

import requests
import json

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)

EnquiryMasterSA = EnquiryMaster.sa
CustomerSA = CustomerModel.sa
UserSA=UserModel.sa
AuthUserSA = User.sa
ItemEnquirySA = ItemEnquiry.sa
ProductsSA = Products.sa
BranchSA = Branch.sa
BrandSA = Brands.sa
ItemSA = Items.sa
SourceSA = Source.sa
PrioritySA = Priority.sa
# EnquiryFinanceSA = EnquiryFinance.sa
FinanciersSa = Financiers.sa
GDPRangeSA = GDPRange.sa

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()





class GetDataForMobileEnquiry(APIView):
    """Onload details for mobile enquiry"""
    permission_classes = [IsAuthenticated]
    def get(self,request,):
        try:
            lst_product_visible = []
            lst_product = []
            ins_product = Products.objects.filter(fk_company = request.user.userdetails.fk_company).exclude(vchr_product_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY'] ).values('id','vchr_product_name','bln_visible','dct_product_spec').order_by('id')
            lst_other_prodcuts = []
            lst_product_smart_choice = []
            dct_na_stock_product = {}
            if ins_product:
                for itr_item in ins_product:
                    dct_product = {}
                    if not itr_item['bln_visible']:
                        if itr_item['vchr_product_name'] not in lst_other_prodcuts:
                            lst_other_prodcuts.append(itr_item['vchr_product_name'])
                            lst_product_smart_choice.append(itr_item['vchr_product_name'])
                            if itr_item['dct_product_spec']:
                                dct_na_stock_product[itr_item['vchr_product_name']] = []
                                for str_spec in itr_item['dct_product_spec']:
                                    if itr_item['dct_product_spec'][str_spec]:
                                        dct_na_stock_product[itr_item['vchr_product_name']].append(str_spec)
                                # dct_na_stock_product[itr_item['vchr_product_name']] = itr_item['dct_product_spec'].keys()
                            else:
                                dct_na_stock_product[itr_item['vchr_product_name']] = []
                        # if 'Others' not in dct_product['name']:
                        #     dct_product['name'] = 'Others'
                    else:
                        # dct_product['name'] = itr_item['vchr_product_name']
                        # dct_product['id'] = itr_item['id']
                        # dct_product['checked'] = False
                        dct_product['name'] = itr_item['vchr_product_name']
                        dct_product['id'] = itr_item['id']
                        dct_product['checked'] = False
                        lst_product_smart_choice.append(dct_product['name'])
                        lst_product_visible.append(dct_product)
                        # dct_na_stock_product[itr_item['vchr_product_name']] = itr_item['vchr_order']
                        if itr_item['dct_product_spec']:
                            dct_na_stock_product[itr_item['vchr_product_name']] = []
                            for str_spec in itr_item['dct_product_spec']:
                                if itr_item['dct_product_spec'][str_spec]:
                                    dct_na_stock_product[itr_item['vchr_product_name']].append(str_spec)
                            # dct_na_stock_product[itr_item['vchr_product_name']] = itr_item['dct_product_spec'].keys()
                        else:
                            dct_na_stock_product[itr_item['vchr_product_name']] = []
                        # if itr_item['dct_product_spec']:
                        #         dct_na_stock_product[itr_item['vchr_product_name']] = itr_item['dct_product_spec'].keys()

                    # if itr_item['bln_visible']:
                    #     dct_product['name'] = itr_item['vchr_product_name']
                    #     dct_product['id'] = itr_item['id']
                    #     dct_product['checked'] = False
                    #     lst_product_visible.append(dct_product)
                    # else:
                    #     dct_product['id'] = itr_item['id']
                    #     dct_product['name'] = itr_item['vchr_product_name']
                    #     lst_product.append(dct_product)


                lst_source = list(Source.objects.filter(bln_status=True,fk_company_id = request.user.userdetails.fk_company_id).values('vchr_source_name','pk_bint_id').order_by('pk_bint_id'))
                lst_priority = list(Priority.objects.filter(bln_status=True,fk_company_id = request.user.userdetails.fk_company_id).values('vchr_priority_name','pk_bint_id').order_by('pk_bint_id'))
                # lst_financier = list(Financiers.objects.filter(bln_active=True,fk_company_id = request.user.userdetails.fk_company_id).values('vchr_name','pk_bint_id').order_by('pk_bint_id'))
                lst_financier = list(UserModel.objects.filter(fk_financier__bln_active=True,fk_company_id = request.user.userdetails.fk_company_id,fk_branch_id = request.user.userdetails.fk_branch_id).annotate(vchr_name=F('fk_financier__vchr_name'),pk_bint_id=F('fk_financier__pk_bint_id')).values('vchr_name','pk_bint_id').order_by('fk_financier__pk_bint_id'))

                int_companyId = request.GET.get('id',request.user.userdetails.fk_company_id)

                if UserModel.objects.filter(is_active=True,id=request.user.id).values('fk_branch'):
                    int_branch_id = UserModel.objects.filter(is_active=True,id=request.user.id).values('fk_branch')[0]['fk_branch']

                if int_companyId == '0':
                    userListData=list(UserModel.objects.filter(is_active=True).values('id','first_name','last_name','fk_branch','fk_branch__vchr_name','bint_phone','username','fk_group__vchr_name','fk_company__vchr_name','username').order_by('-id'))
                else:
                    # branch = UserModel.objects.get(id = request.user.id).fk_branch
                    userListData=UserModel.objects.filter(is_active=True,fk_company=int(int_companyId),fk_branch=int_branch_id).values('id', 'first_name','last_name','fk_branch','fk_branch__vchr_name','bint_phone','username','fk_group__vchr_name','username').exclude(fk_group__vchr_name__in = ['BRANCH MANAGER','TERRITORY MANAGER','ZONE MANAGER','STATE HEAD','COUNTRY HEAD']).order_by('id')
                for dct_data in userListData:
                    dct_data['full_name'] = dct_data['first_name'] + ' ' + dct_data['last_name']
                return Response({'status':'success',
                    'lstProducts':lst_product_visible,
                    'lstProductsOthers':lst_other_prodcuts,
                    'lstProductsExc':lst_product_smart_choice,
                    'lstNaStockProduct':dct_na_stock_product,
                    'lst_source':lst_source,
                    'lst_priority':lst_priority,'userListData':userListData,'lst_financier':lst_financier})

            else:
                return Response({'status':'empty'})
        except Exception as e:
            return Response({'result':'failed','reason':e})
class EnquiryList(APIView):
    permission_classes=[IsAuthenticated]


    def post(self,request):
        try:
            # int_company_id = int(request.data.get('company_id'))
            ins_user = UserModel.objects.get(id = request.user.id)
            int_pending = int(request.data.get('int_pending'))
            if not request.data['start_date'] and not request.data['end_date'] and int_pending:
                dat_start=datetime.strptime('2017-01-01','%Y-%m-%d')
                dat_end=datetime.now()
            else:
                dat_start = datetime.strptime(request.data['start_date'],'%Y-%m-%d')
                dat_end = datetime.strptime(request.data['end_date'],'%Y-%m-%d')
            # if datetime.now().date()==dat_end.date():
                # dat_end=dat_end + timedelta(days = 1)
            int_branch_id = request.data.get('branchId')
            session = Session()
            lst_enquiry_data = []
            lst_enquiry_data_status = []
            lst_branch=[]
            int_cust_id=request.data.get('custId')
            int_branch_id = request.data.get('branchId')
            dat_start=dat_start.date()
            dat_end=dat_end.date()
            #These are the statuses which are excluded in pending enquiries
            lst_statuses= ["LOST","BOOKED","UNQUALIFIED"]
            rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                        CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                        AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name'),\
                                        ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_product_name.label('service'),\
                                        EnquiryFinanceSA.vchr_finance_status,)\
                                        .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                        .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end,\
                                         EnquiryMasterSA.fk_company_id ==  ins_user.fk_company_id)\
                                        .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                        .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.id)\
                                        .outerjoin(EnquiryFinanceSA,EnquiryMasterSA.pk_bint_id == EnquiryFinanceSA.fk_enquiry_master_id)\
                                        .order_by(desc(EnquiryMasterSA.dat_created_at))
            if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                # lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            else:
                rst_enquiry =rst_enquiry.filter(EnquiryMasterSA.fk_branch_id== request.user.userdetails.fk_branch_id,EnquiryMasterSA.fk_assigned_id==request.user.id)

            if int_pending:
                rst_enquiry = rst_enquiry.filter(ItemEnquirySA.vchr_enquiry_status.notin_(lst_statuses))
            if int_cust_id:
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_customer_id == int_cust_id)
            # if int_branch_id:
            #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == int_branch_id)

            dct_enquiries = {}
            for dct_data in rst_enquiry.all():
                dct_data = dct_data._asdict()

                if dct_data['vchr_enquiry_num'] == dct_enquiries.get('enquiry'):
                    if dct_data['service'].title() not in dct_enquiries['services']:
                        dct_enquiries['services'].append(dct_data['service'].title())
                    dct_enquiries['status'].append(dct_data['vchr_enquiry_status'].title())
                    if dct_data['vchr_enquiry_status'].upper() not in ['BOOKED','LOST']:
                        dct_enquiries['status_display'] = 'pending'
                    elif dct_data['vchr_enquiry_status'].upper() == 'BOOKED' and dct_enquiries['status_display'] != 'pending':
                        dct_enquiries['status_display'] = 'booked'
                    elif dct_data['vchr_enquiry_status'].upper() in ['LOST'] and dct_enquiries['status_display'] not in ['pending','booked']:
                        dct_enquiries['status_display'] = 'lost'
                else:
                    if dct_enquiries == {}:
                        dct_enquiries = {'enquiry_id':dct_data['pk_bint_id'],'enquiry':dct_data['vchr_enquiry_num'],'date':dct_data['dat_created_at'],\
                                        'customer_name':dct_data['customer_first_name']+' '+dct_data['customer_last_name'],'staff_name':dct_data['staff_first_name']+' '+dct_data['staff_last_name'],\
                                        'status':[dct_data['vchr_enquiry_status'].title()],'services':[dct_data['service'].title()],
                                        'finance_status':dct_data['vchr_finance_status'] if dct_data['vchr_finance_status'] else 'null'
                                        }
                    else:
                        lst_enquiry_data.append(dct_enquiries)
                        dct_enquiries = {'enquiry_id':dct_data['pk_bint_id'],'enquiry':dct_data['vchr_enquiry_num'],'date':dct_data['dat_created_at'],\
                                         'customer_name':dct_data['customer_first_name']+' '+dct_data['customer_last_name'],'staff_name':dct_data['staff_first_name']+' '+dct_data['staff_last_name'],\
                                         'status':[dct_data['vchr_enquiry_status'].title()],'services':[dct_data['service'].title()],
                                         'finance_status':dct_data['vchr_finance_status'] if dct_data['vchr_finance_status'] else 'null'
                                         }
                    if dct_data['vchr_enquiry_status'].upper() not in ['BOOKED','LOST']:
                        dct_enquiries['status_display'] = 'pending'
                    elif dct_data['vchr_enquiry_status'].upper() == 'BOOKED':
                        dct_enquiries['status_display'] = 'booked'
                    else:
                        dct_enquiries['status_display'] = 'lost'
            lst_enquiry_data.append(dct_enquiries)
            if request.data.get('enquiry_status'):
                for dct_data in lst_enquiry_data:
                    if dct_data:
                        if request.data.get('enquiry_status')  in dct_data['status']:
                            lst_enquiry_data_status.append(dct_data)
                session.close()
                return Response({'status':'0','data':lst_enquiry_data_status,})
            session.close()
            return Response({'status':'0','data':lst_enquiry_data,})


        except Exception as e:
            return Response({'status':'1','data':[str(e)]})

class AddEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                dct_data = request.data.get('product')
                ins_user = UserModel.objects.get(id = request.user.id)
                if request.data.get('fk_branch'):
                    ins_user_branch = Branch.objects.get(pk_bint_id = request.data.get('fk_branch'))
                    int_assigned_id=UserModel.objects.filter(fk_branch=ins_user_branch,fk_group__vchr_name='BRANCH MANAGER').values('id').first()['id']
                else:
                    ins_branch = UserModel.objects.filter(id = request.user.id).values('fk_branch')
                    ins_user_branch = Branch.objects.get(pk_bint_id = ins_branch[0]['fk_branch'])
                    if request.data.get('fk_assigned_id'):
                        int_assigned_id = request.data.get('fk_assigned_id')
                    else:
                        int_assigned_id = ins_user.id
                dat_created_at = datetime.now()
                dct_enquirystatus = request.data.get('enquirystatus')

                ins_assigned_user = ins_user
                ins_customer = CustomerModel.objects.get(id = request.data.get('fk_customer_id'))
                # Save customer email
                if request.data.get('cust_email'):
                    customer_mail_check = CustomerModel.objects.filter(id = request.data.get('fk_customer_id')).values_list('cust_email',flat=True)
                    ins_cust_email = CustomerModel.objects.filter(~Q(id = request.data.get('fk_customer_id')) & Q(cust_email = request.data.get('cust_email')))
                    if ins_cust_email:
                        return Response({'status':'1', 'data':'Customer email already exist'})
                    else:
                        if customer_mail_check[0]:
                            customer_mail=customer_mail_check[0]
                            if customer_mail != request.data.get('cust_email'):
                                CustomerModel.objects.filter(id = request.data.get('fk_customer_id')).update(cust_email = request.data.get('cust_email'),cust_alternatemail=customer_mail)
                        else:
                            CustomerModel.objects.filter(id = request.data.get('fk_customer_id')).update(cust_email = request.data.get('cust_email'))

                        # CustomerModel.objects.filter(id = request.data.get('fk_customer_id')).update(cust_email = request.data.get('cust_email'))
                #
                if dct_enquirystatus['enquiry']:
                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
                    str_code = ins_document[0].vchr_short_code
                    int_doc_num = ins_document[0].int_number + 1
                    ins_document.update(int_number = int_doc_num)
                    str_number = str(int_doc_num).zfill(4)
                    str_enquiry_no = str_code + '-' + str_number
                    ins_master = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
                    EnquiryMaster.objects.filter(pk_bint_id = ins_master.pk_bint_id).update(
                            # vchr_enquiry_num = str_enquiry_no
                            fk_customer = ins_customer
                            ,fk_source = Source.objects.get(pk_bint_id=request.data.get('fk_enquiry_source'))
                            ,fk_priority = Priority.objects.get(pk_bint_id=request.data.get('fk_enquiry_priority'))
                            ,fk_assigned_id = int_assigned_id
                            ,fk_branch = ins_user_branch
                            # ,bln_sms = dct_customer_data['bln_sms']
                            ,chr_doc_status = 'N'
                            ,fk_created_by = ins_user
                            ,dat_created_at = datetime.now(),
                            fk_company = ins_user.fk_company
                        )
                    ins_master.save()
                    if request.data.get('fk_financier'):
                        ins_enquiry_finance=EnquiryFinance(
                        fk_financiers_id=request.data.get('fk_financier'),
                        vchr_finance_status='PENDING',
                        fk_enquiry_master=ins_master
                        )
                        ins_enquiry_finance.save()

                    for dct_sub in dct_data:
                        for dct_enquiry in dct_data[dct_sub]:
                            if not dct_enquiry['mobileNa']:
                                int_product_id=Products.objects.filter(vchr_product_name__iexact = dct_enquiry['str_product'],fk_company=ins_user.fk_company).values_list('id',flat=True).first()
                                ins_brand = Brands.objects.get(id = int(dct_enquiry['fk_brand']['id']))
                                ins_item = Items.objects.get(id = int(dct_enquiry['fk_item']['id']))

                                if not dct_enquiry['dbl_estimated_amount']:
                                        dct_enquiry['dbl_estimated_amount'] = '0.0'

                                if not dct_enquiry['int_quantity']:
                                    dct_enquiry['int_quantity'] = '0'

        # //////----un comment only when stock details consider
                                # ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_enquiry['fk_item']['id']), int_available__gte = int(dct_enquiry['int_quantity'])).order_by('fk_stock_master__dat_added').values()
                                # ins_stock_details = ''
                                # if ins_stock:
                                #     int_stock_id = int(ins_stock[0]['pk_bint_id'])
                                #     ins_stock_details = Stockdetails.objects.get(pk_bint_id = int_stock_id)
                                #     if dct_enquiry.get('vchr_enquiry_status') == 'BOOKED':
                                #         int_curr = int(ins_stock[0]['int_available']) - int(dct_enquiry['int_quantity'])
                                #         ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                                #     else:
                                #         ins_stock_details = None
                                #
                                # else:
                                #     return Response({'status':'1', 'data':'Selected Mobile exceeds available stock amount'})
                                #
                                if not dct_enquiry['dbl_buyback']:
                                    dct_enquiry['dbl_buyback']=0
                                if not dct_enquiry['dbl_discount']:
                                    dct_enquiry['dbl_discount']=0
                                ins_item_enq = ItemEnquiry(fk_enquiry_master = ins_master,
                                                            fk_product_id=int_product_id,
                                                            fk_brand = Brands.objects.get(id = dct_enquiry['fk_brand']['id']),
                                                            fk_item = Items.objects.get(id = dct_enquiry['fk_item']['id']),
                                                            int_quantity = dct_enquiry['int_quantity'],
                                                            dbl_amount = float(dct_enquiry['dbl_estimated_amount']),
                                                            vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                            vchr_remarks = dct_enquiry['vchr_remarks'],
                                                            dbl_buy_back_amount=float(dct_enquiry['dbl_buyback']),
                                                            dbl_discount_amount=float(dct_enquiry['dbl_discount']),
                                                            dbl_imei_json = {"imei" : []},
                                                            dbl_exchange_amt = None,
                                                            fk_item_exchange = None)

                                                            # fk_stockdetails = ins_stock_details)----un comment only when stock details consider
                                if dct_sub == 'SMART CHOICE':
                                    ins_item_ex = ItemExchange(
                                                fk_item = Items.objects.get(id = dct_enquiry['fk_item_exchange']['id']),
                                                vchr_filename_json = {"image": dct_enquiry['lst_image']})
                                    ins_item_ex.save()
                                    ins_item_enq.dbl_exchange_amt = float(dct_enquiry['dbl_exchange_amt'])
                                    ins_item_enq.fk_item_exchange = ins_item_ex
                                if dct_enquiry['dbl_gdp_amount']=='':
                                    dct_enquiry['dbl_gdp_amount']=0

                                if dct_enquiry['dbl_gdew_amount']=='':
                                    dct_enquiry['dbl_gdew_amount']=0

                                if dct_enquiry['vchr_enquiry_status'] == 'BOOKED':
                                    # ins_item_enq.int_sold = int(dct_enquiry['int_quantity'])
                                    # ins_item_enq.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                                    ins_item_enq.dbl_imei_json = {"imei" : dct_enquiry['lst_imei']}
                                    ins_item_enq.int_sold = dct_enquiry['int_quantity']
                                    ins_item_enq.dbl_gdp_amount = float(dct_enquiry['dbl_gdp_amount'])
                                    ins_item_enq.dbl_gdew_amount = float(dct_enquiry['dbl_gdew_amount'])
                                    ins_item_enq.int_type = dct_enquiry['int_type']
                                ins_item_enq.save()
                                if ins_item_enq and dct_enquiry.get('vchr_enquiry_status','') == 'BOOKED':
                                    '''Following code commented in order to prevent lost case if same product booked multiple times'''

                                    '''
                                    ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company,fk_product_id=int_product_id).exclude(vchr_enquiry_status = 'BOOKED')
                                    if ins_item_enq_exist:
                                        ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                                        lst_query_set = []
                                        for ins_data in ins_item_enq_exist:
                                            ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                                                              vchr_notes = dct_sub+' '+ ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                                              vchr_enquiry_status = 'LOST',
                                                                              int_status = 1,
                                                                              dbl_amount = 0.0,
                                                                              fk_user = ins_user,
                                                                              fk_updated = ins_user,
                                                                              dat_followup = dat_created_at,
                                                                              dat_updated = dat_created_at)
                                            lst_query_set.append(ins_follow_up)
                                        if lst_query_set:
                                            ItemFollowup.objects.bulk_create(lst_query_set);
                                            '''
                                    # for notifications
                                    # ins_manager=UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group__vchr_name='BRANCH MANAGER').values_list('username',flat=True)

                                    ins_manager=UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group__vchr_name='BRANCH MANAGER').values_list('username',flat=True)
                                    if ins_manager:
                                        str_url='/crm/viewmobilelead'
                                        str_msg= ins_master.vchr_enquiry_num+' is booked'
                                        str_notification_type = 'ENQUIRY'
                                        str_enquiry_id = ins_master.pk_bint_id
                                        lst_notification_query = []
                                        for data in ins_manager:
                                            ins_notification = Notification(vchr_module = str_notification_type,
                                                                            vchr_message = str_msg,
                                                                            vchr_url = str_url,
                                                                            username = data,
                                                                            int_doc_id = str_enquiry_id,
                                                                            bln_active_status = True,
                                                                            )
                                            lst_notification_query.append(ins_notification)
                                        ins_notify = Notification.objects.bulk_create(lst_notification_query);
                                        lst_notify_data = []
                                        for data in ins_notify:
                                            dct_notfiy = {
                                            'username':data.username,
                                            'url': data.vchr_url,
                                            'msg':data.vchr_message,
                                            'str_notification_type':data.vchr_module,
                                            'str_enquiry_id':data.int_doc_id,
                                            'int_notification_id': data.pk_bint_id
                                            }
                                            lst_notify_data.append(dct_notfiy)
                                        # notifications_data(lst_notify_data)


                                ins_item_foll = ItemFollowup(  fk_item_enquiry = ins_item_enq,
                                                                dat_followup = datetime.now(),
                                                                fk_user = ins_user,
                                                                vchr_notes = dct_enquiry['vchr_remarks'],
                                                                vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                dbl_amount = float(dct_enquiry['dbl_estimated_amount']),
                                                                fk_updated = ins_user,
                                                                dat_updated = datetime.now())
                                ins_item_foll.save()

                if dct_enquirystatus['naEnquiry']:

                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'NAENQUIRY',fk_company = ins_user.fk_company)
                    str_code = ins_document[0].vchr_short_code
                    int_doc_num = ins_document[0].int_number + 1
                    ins_document.update(int_number = int_doc_num)
                    str_number = str(int_doc_num).zfill(4)
                    str_naenquiry_no = str_code + '-' + str_number
                    dct_na_details=request.data.get('naProduct')

                    if dct_na_details:
                        ins_enquiry = NaEnquiryMaster.objects.create_enquiry_num(str_naenquiry_no)
                        NaEnquiryMaster.objects.filter(pk_bint_id = ins_enquiry.pk_bint_id).update(
                            # vchr_enquiry_num = str_naenquiry_no
                            fk_customer = ins_customer
                            ,fk_source = Source.objects.get(pk_bint_id=request.data.get('fk_enquiry_source'))
                            ,fk_priority = Priority.objects.get(pk_bint_id=request.data.get('fk_enquiry_priority'))
                            # ,vchr_customer_type = dct_customer['vchr_customer_type']
                            ,fk_assigned_id = int_assigned_id
                            ,fk_branch = ins_user_branch
                            ,fk_created_by = ins_user
                            ,dat_created_at = datetime.now()
                            ,fk_company = ins_user.fk_company
                        )


                        for dct_na_data in dct_na_details:
                            for dct_data in dct_na_details[dct_na_data]:
                                # dct_data['specification'] = {"os":"android","color":"black","width":"5.5"}
                                if not dct_data['dbl_estimated_amount']:
                                    dct_data['dbl_estimated_amount'] = '0.0'

                                if not dct_data['int_quantity']:
                                    dct_data['int_quantity'] = '0'

                                ins_details = NaEnquiryDetails(
                                    fk_na_enquiry_master = ins_enquiry
                                    ,vchr_product = dct_data['str_product'].upper()
                                    ,vchr_brand = dct_data['strStockBrand'].strip().upper()
                                    ,vchr_item = dct_data['strStockItem'].strip().upper()
                                    # ,vchr_color = dct_computer['vchr_color']
                                    ,int_quantity = int(dct_data['int_quantity'])
                                    ,vchr_remarks = dct_data['vchr_remarks'].strip()
                                    ,json_product_spec = json.dumps(dct_data['specification'])
                                )
                                ins_details.save()
                if dct_enquirystatus['enquiry']:
                    # str_hash = hash_enquiry(ins_master)
                    EnquiryMaster.objects.filter(chr_doc_status='N',pk_bint_id = ins_master.pk_bint_id).update(vchr_hash = str_hash)
                    # enquiry_print(str_enquiry_no,request,ins_user)
                    return JsonResponse({'status': 'Success','data':str_enquiry_no})
                elif dct_enquirystatus['naEnquiry']:
                    return JsonResponse({'status': 'Success','data':str_naenquiry_no})
        except Exception as e:
            return JsonResponse({'status': 'Failed','data':str(e)})
            # if 'ins_master' in locals():
            #     ItemFollowup.objects.filter(fk_item_enquiry__fk_enquiry_master = ins_master.pk_bint_id).delete()
            #     ItemEnquiry.objects.filter(fk_enquiry_master = ins_master.pk_bint_id).delete()
            #     EnquiryMaster.objects.filter(pk_bint_id = ins_master.pk_bint_id).delete()

class EnquiryView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # sqlalobj = Savedftosql('','')
            # engine = sqlalobj.engine
            # metadata = MetaData()
            # metadata.reflect(bind=engine)
            # Session = sessionmaker()
            # Session.configure(bind=engine)
            session = Connection()
            ItemEnquirySA = metadata.tables['item_enquiry']
            int_enquiry_id=request.data["enquiry_id"]
            int_financier = 0
            rst_financier = EnquiryFinance.objects.filter(fk_enquiry_master_id = int_enquiry_id).values('fk_financiers_id')
            if rst_financier:
                int_financier = rst_financier[0]['fk_financiers_id']
                lst_financier = Financiers.objects.filter(pk_bint_id=int_financier).values('vchr_name','pk_bint_id')
            # import pdb; pdb.set_trace()
            else:
                int_branch_id = EnquiryMaster.objects.filter(pk_bint_id =int_enquiry_id).values('fk_branch_id').first()['fk_branch_id']
                lst_financier = list(UserModel.objects.filter(fk_financier__bln_active=True,fk_company_id = request.user.userdetails.fk_company_id,fk_branch_id = int_branch_id).annotate(vchr_name=F('fk_financier__vchr_name'),pk_bint_id=F('fk_financier__pk_bint_id')).values('vchr_name','pk_bint_id').order_by('fk_financier__pk_bint_id'))
            # lst_financier = list(Financiers.objects.filter(bln_active=True,fk_company_id = request.user.userdetails.fk_company_id).values('vchr_name','pk_bint_id').order_by('pk_bint_id'))
            if not int_enquiry_id or int_enquiry_id == 'undefined' :
                session.close()
                return Response({'status': '1','data':'Enquiry id must be provided'})
            else:
                # session = Session()
                rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                            CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,CustomerSA.cust_email,\
                                            CustomerSA.cust_alternatemobile,CustomerSA.cust_alternatemail,CustomerSA.cust_contactsrc,\
                                            EnquiryMasterSA.fk_source_id,EnquiryMasterSA.vchr_customer_type,EnquiryMasterSA.bln_sms,\
                                            EnquiryMasterSA.fk_priority_id,\
                                            ItemEnquirySA.c.pk_bint_id,ItemEnquirySA.c.dbl_gdp_amount,ItemEnquirySA.c.dbl_gdew_amount,ItemEnquirySA.c.dbl_min_price,ItemEnquirySA.c.dbl_max_price,ItemEnquirySA.c.dbl_buy_back_amount,ItemEnquirySA.c.dbl_discount_amount,\
                                            ItemEnquirySA.c.vchr_enquiry_status,ItemEnquirySA.c.int_quantity,ItemEnquirySA.c.dbl_amount,ItemEnquirySA.c.dbl_imei_json,ItemEnquirySA.c.vchr_remarks,ProductsSA.vchr_product_name.label('product'),\
                                            BrandSA.vchr_brand_name,ItemSA.vchr_item_name,\
                                            SourceSA.vchr_source_name,PrioritySA.vchr_priority_name,BranchSA.vchr_name,\
                                            EnquiryFinanceSA.fk_financiers_id,EnquiryFinanceSA.vchr_finance_status,EnquiryFinanceSA.vchr_remarks.label('finance_remarks'),\
                                            EnquiryFinanceSA.dbl_max_amt,FinanciersSa.vchr_name.label('financier_name'))\
                                            .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                            .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                            .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.c.fk_enquiry_master_id)\
                                            .join(ProductsSA,ItemEnquirySA.c.fk_product_id == ProductsSA.id)\
                                            .join(BrandSA,ItemEnquirySA.c.fk_brand_id == BrandSA.id)\
                                            .join(ItemSA,ItemEnquirySA.c.fk_item_id == ItemSA.id)\
                                            .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                                            .join(PrioritySA, EnquiryMasterSA.fk_priority_id == PrioritySA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                            .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N' )\
                                            .outerjoin(EnquiryFinanceSA,EnquiryMasterSA.pk_bint_id == EnquiryFinanceSA.fk_enquiry_master_id)\
                                            .outerjoin(FinanciersSa,EnquiryFinanceSA.fk_financiers_id == FinanciersSa.pk_bint_id)\
                                            # .filter(EnquiryFinanceSA.fk_financiers_id == FinanciersSa.pk_bint_id)



            dct_enquiries = {}
            dct_customer_data ={}
            # dct_enquiry_data = {}
            for dct_data in rst_enquiry.all():
                dct_data = dct_data._asdict()
                if dct_data['product'] not in dct_enquiries:
                    dct_enquiries[dct_data['product']] = []
                # dct_enquiries[dct_data['product']].append(dct_data)
                dct_enquiries[dct_data['product']].append({'pk_bint_id':dct_data['pk_bint_id'],'vchr_brand_name':dct_data['vchr_brand_name'],
                                                           'vchr_item_name':dct_data['vchr_item_name'],'int_quantity':dct_data['int_quantity'],
                                                           'vchr_enquiry_status':dct_data['vchr_enquiry_status'],'dbl_imei_json':dct_data['dbl_imei_json'],
                                                           'dbl_amount':dct_data['dbl_amount'],'dbl_gdp_amount':dct_data['dbl_gdp_amount'],
                                                           'dbl_gdew_amount':dct_data['dbl_gdew_amount'],'vchr_remarks':dct_data['vchr_remarks'],
                                                           'dbl_min_price':dct_data['dbl_min_price'],'dbl_max_price':dct_data['dbl_max_price'],
                                                           'dbl_buyback':dct_data['dbl_buy_back_amount'], 'dbl_discount':dct_data['dbl_discount_amount'],'dbl_total_amount':((dct_data['dbl_amount']-dct_data['dbl_buy_back_amount']-dct_data['dbl_discount_amount'])+(dct_data['dbl_gdp_amount']+dct_data['dbl_gdew_amount'])),
                                                           'status':False})

            if rst_enquiry.all():
                dct_customer_data = {'vchr_enquiry_num':dct_data['vchr_enquiry_num'],'cust_fname':dct_data['cust_fname'],
                                     'cust_lname':dct_data['cust_lname'],'cust_mobile':dct_data['cust_mobile'],
                                     'dat_created_at':dct_data['dat_created_at'],'cust_email':dct_data['cust_email'],
                                     'cust_alternatemobile':dct_data['cust_alternatemobile'],'cust_alternatemail':dct_data['cust_alternatemail'],
                                     'vchr_source_name':dct_data['vchr_source_name'],'vchr_priority_name':dct_data['vchr_priority_name'],
                                     'cust_contactsrc':dct_data['cust_contactsrc'],'bln_sms':dct_data['bln_sms'],'vchr_name':dct_data['vchr_name'],
                                     'fk_financiers':dct_data['financier_name'],'vchr_finance_status':dct_data['vchr_finance_status'],
                                     'vchr_remarks_finance':dct_data['finance_remarks'],'dbl_max_amt':dct_data['dbl_max_amt']}

            session.close()
            return Response({'status' : '0','dct_enquiry_details':dct_enquiries,'dct_customer_data':dct_customer_data,'lst_financier':lst_financier})

        except Exception as e:
            session.close()
            return Response({'status':'1','data':[str(e)]})

class AddFollowup(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_created = datetime.now()
            dct_data = request.data
            with transaction.atomic():
                ins_customer_id=ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).values('fk_enquiry_master__fk_customer_id')
                ins_enquiry_master_id =ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).values_list('fk_enquiry_master_id',flat=True)[0]
                # Save customer email
                if request.data.get('cust_email'):
                    customer_mail_check = CustomerModel.objects.filter(id = ins_customer_id[0]['fk_enquiry_master__fk_customer_id']).values_list('cust_email',flat=True)
                    ins_cust_email = CustomerModel.objects.filter(~Q(id = ins_customer_id[0]['fk_enquiry_master__fk_customer_id']) & Q(cust_email = request.data.get('cust_email')))
                    if ins_cust_email:
                        return Response({'status':'1', 'data':'Customer email already exist'})
                    else:
                        if customer_mail_check:
                            customer_mail=customer_mail_check[0]
                            if customer_mail != request.data.get('cust_email'):
                                CustomerModel.objects.filter(id = ins_customer_id[0]['fk_enquiry_master__fk_customer_id']).update(cust_email = request.data.get('cust_email'),cust_alternatemail=customer_mail)
                        else:
                            CustomerModel.objects.filter(id = ins_customer_id[0]['fk_enquiry_master__fk_customer_id']).update(cust_email = request.data.get('cust_email'))

                str_enquiry_no = ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                # if ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.user.username:
                dat_updated_time = dat_created
                fk_updated_by = request.user.id
                int_status = 1
                # else :
                    # dat_updated_time = None
                    # fk_updated_by = None
                    # int_status = 0

                # if request.data.get('vchr_followup_status') == 'BOOKED':
                #     int_status = 1
                #     rst_enq = ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
                    # ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
                    # if ins_stock:
                    #     Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
                    # else:
                    #     ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
                    #     int_available = ins_stock.int_available
                    #     return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
                ins_item_follow_up = ItemFollowup(fk_item_enquiry = ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
                    vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
                    int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = request.user.userdetails,\
                    fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                ins_item_follow_up.save()

                if request.data.get('int_financier'):
                    rst_financier = EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_enquiry_master_id).values('fk_financiers_id')
                    if not rst_financier:
                        ins_enquiry_finance=EnquiryFinance(
                        fk_financiers_id=request.data.get('int_financier'),
                        vchr_finance_status='PENDING',
                        fk_enquiry_master_id=ins_enquiry_master_id
                        )
                        ins_enquiry_finance.save()

                if request.data.get('dbl_gdp_amount')=='':
                    request.data['dbl_gdp_amount']=0

                if request.data.get('dbl_gdew_amount')=='':
                    request.data['dbl_gdew_amount']=0


                if request.data.get('vchr_followup_status')== 'BOOKED'  :
                    ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status='BOOKED',dbl_gdp_amount=float(request.data['dbl_gdp_amount']),dbl_gdew_amount=float(request.data['dbl_gdew_amount']),int_type=request.data['int_type'],dbl_imei_json={"imei" : request.data.get('lst_imei',[])})
                if request.data.get('vchr_followup_status')=='TO PROCESS':
                    EnquiryFinance.objects.filter(fk_enquiry_master_id=ins_enquiry_master_id).update(vchr_finance_status = 'TO PROCESS')
                    ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status='TO PROCESS',dbl_gdp_amount=float(request.data['dbl_gdp_amount']),dbl_gdew_amount=float(request.data['dbl_gdew_amount']),int_type=request.data['int_type'],dbl_imei_json={"imei" : request.data.get('lst_imei',[])})
                if int_status:
                    ins_obj = ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                    ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                    dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
                    if request.data.get('dbl_buyback') or request.data.get('dbl_buyback')==0:
                        ins_obj.update(dbl_buy_back_amount=request.data.get('dbl_buyback'))
                    if request.data.get('dbl_discount') or request.data.get('dbl_discount') ==0:
                        ins_obj.update(dbl_discount_amount=request.data.get('dbl_discount'))
                if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                    ins_obj.update(dbl_imei_json = {"imei" : request.data.get('lst_imei',[])},int_sold = request.data.get('int_followup_quantity'))
                    '''Following code commented in order to prevent lost case if same product booked multiple times'''

                    '''ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id = ins_customer_id,fk_enquiry_master__fk_company = request.user.userdetails.fk_company,fk_product_id=ins_obj.first().fk_product_id).exclude(vchr_enquiry_status = 'BOOKED')
                    if ins_item_enq_exist:
                        ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                        lst_query_set = []
                        for ins_data in ins_item_enq_exist:
                            ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                                              vchr_notes = 'Same product '+ ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                              vchr_enquiry_status = 'LOST',
                                                              int_status = 1,
                                                              dbl_amount = 0.0,
                                                              fk_user = request.user.userdetails,
                                                              fk_updated = request.user.userdetails,
                                                              dat_followup = datetime.now(),
                                                              dat_updated = datetime.now())
                            lst_query_set.append(ins_follow_up)
                        if lst_query_set:
                            ItemFollowup.objects.bulk_create(lst_query_set);
                        '''
                int_enquiry_id = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_enquiry_num = str_enquiry_no, fk_company_id = request.user.userdetails.fk_company_id).pk_bint_id
                # enquiry_print(str_enquiry_no,request,ins_user)
                return JsonResponse({'status':'success','value':'Follow-up completed successfully!','remarks':request.data['vchr_followup_remarks'],'followup':request.data['vchr_followup_status'],'amount':request.data['int_followup_amount'],'change':int_status,'enqId':int_enquiry_id,'int_quantity':request.data.get('int_followup_quantity')})


        except Exception as e:
            return Response({'status':'1', 'error':str(e)})
            # if int_status:
            #     ins_user = request.user

        # except Exception as e:
        #     return JsonResponse({'status':'0','data':str(e)})


class BranchTypeahed(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            q = request.GET.get('query')
            ins_data = UserModel.objects.filter(id=request.user.id).values('int_area_id','fk_group__vchr_name')
            rst_branches = []
            if ins_data:
                # rst_branches = show_data_based_on_role(ins_data[0]['fk_group__vchr_name'],ins_data[0]['int_area_id'])
                lst_branches = list(Branch.objects.filter(Q(vchr_name__icontains = q) & Q(pk_bint_id__in = rst_branches)).values('vchr_name','vchr_code','pk_bint_id'))
            # lst_customerlist = list(CustomerModel.objects.filter(Q(cust_mobile__icontains = q) & Q(cust_activestate = True) & Q(fk_company = int_company)).values('id','cust_mobile','cust_fname','cust_lname','cust_email').order_by('-id') )

            # for d in lst_customerlist:
                # d['name']=d['cust_fname']+' '+d['cust_lname']+' - '+str(d['cust_mobile'])
            return Response(lst_branches)
        except Exception as e:
            print(e)
            return Response({'status':'1'})
    def post(self,request):
        try:
            int_branch_id = request.data.get('id')
            lst_financier = list(UserModel.objects.filter(fk_financier__bln_active=True,fk_company_id = request.user.userdetails.fk_company_id,fk_branch_id = int_branch_id).annotate(vchr_name=F('fk_financier__vchr_name'),pk_bint_id=F('fk_financier__pk_bint_id')).values('vchr_name','pk_bint_id').order_by('fk_financier__pk_bint_id'))
            return JsonResponse({'status':'success','data':lst_financier})
        except Exception as e:
            print(e)
            return Response({'status':'failed'})

class GDPRangeGET(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,):
        try:
            obj_gdp_range = GDPRange.objects.values('dbl_from','dbl_to','dbl_amt','int_type');
            dct_gdprange={}
            lst_gdprange = []
            for dct_data in obj_gdp_range:
                lst_gdprange.append(dct_data)
            return JsonResponse({'status':'success','data':lst_gdprange})
        except Exception as e:
            return Response({'status':'1', 'error':str(e)})

class SaveImages(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            import pdb; pdb.set_trace()
            print(request.data)
            return Response({'status':'0'})
        except Exception as e:
            return Response({'status':'1', 'error':str(e)})
