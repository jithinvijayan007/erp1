
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import and_,func ,cast,Date
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
from userdetails.models import UserDetails as UserModel
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
from enquiry_mobile.models import Notification

# from django.conf import settings
from enquiry_mobile.models import MobileEnquiry, MobileFollowup, TabletEnquiry, TabletFollowup, ComputersEnquiry,ItemEnquiry,ItemFollowup, ComputersFollowup, AccessoriesEnquiry, AccessoriesFollowup,Notification
from userdetails.models import Financiers
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

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()


class getProductPrice(APIView):
    permission_classes=[IsAuthenticated]
    """Estimated amount of purticular item"""
    def post(self,request):
        try:
            int_id = request.data.get('itemId')
            flt_amount = 0
            if int_id:
                str_item_code = Items.objects.filter(id = int_id).values('vchr_item_code')[0]['vchr_item_code']
                dbl_apx_amount = Items.objects.filter(id = int_id).values('dbl_apx_amount')[0]['dbl_apx_amount']
                if dbl_apx_amount:
                    return JsonResponse({'status':'success', 'item_amount_per_qty':dbl_apx_amount})
                # url and passing parameter for getting the item price
                url = 'http://devserv1.gdpplus.in/Item_Model_Selling_Price.aspx'
                params = {'model':str_item_code}
                r = requests.get(url, params=params)

                if r.status_code == 200:
                    data = json.dumps(r.text)
                    if data.split('\\')[0] != '"[]':
                        # splitting the response string to get the amount
                        flt_amount = float(data.split('\\')[6].split(':')[1].split('}')[0])
                        Items.objects.filter(id = int_id).update(dbl_apx_amount = flt_amount)

            return JsonResponse({'status':'success', 'item_amount_per_qty':flt_amount})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':str(e)})

class ProductList(APIView):
    """docstring for Typeahead."""
    permission_classes = [IsAuthenticated]
    def get(self,request,):
        try:
            lst_product_visible = []
            lst_product = []
            ins_product = Products.objects.filter(fk_company = request.user.usermodel.fk_company).exclude(vchr_product_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY'] ).values('id','vchr_product_name','bln_visible','dct_product_spec').order_by('id')
            lst_other_prodcuts = []
            dct_na_stock_product = {}
            if ins_product:
                for itr_item in ins_product:
                    dct_product = {}
                    if not itr_item['bln_visible']:
                        if itr_item['vchr_product_name'] not in lst_other_prodcuts:
                            lst_other_prodcuts.append(itr_item['vchr_product_name'])
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
                return Response({'status':'success','data':lst_product_visible,'others':lst_other_prodcuts,'dct_na_stock':dct_na_stock_product})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            return Response({'result':'failed','reason':e})


class AddEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                dct_data = request.data.get('product')
                ins_user = UserModel.objects.get(id = request.user.id)
                if request.data.get('fk_branch'):
                    ins_user_branch = Branch.objects.get(pk_bint_id = request.data.get('fk_branch'))
                else:
                    ins_branch = UserModel.objects.filter(id = request.user.id).values('fk_branch')
                    ins_user_branch = Branch.objects.get(pk_bint_id = ins_branch[0]['fk_branch'])
                dat_created_at = datetime.now()
                dct_enquirystatus = request.data.get('enquirystatus')
                if request.data.get('fk_assigned_id'):
                    int_assigned_id = request.data.get('fk_assigned_id')
                else:
                    int_assigned_id = ins_user.id
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

                                ins_item_enq = ItemEnquiry(fk_enquiry_master = ins_master,
                                                            fk_product_id=int_product_id,
                                                            fk_brand = Brands.objects.get(id = dct_enquiry['fk_brand']['id']),
                                                            fk_item = Items.objects.get(id = dct_enquiry['fk_item']['id']),
                                                            int_quantity = dct_enquiry['int_quantity'],
                                                            dbl_amount = dct_enquiry['dbl_estimated_amount'],
                                                            vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                            vchr_remarks = dct_enquiry['vchr_remarks'])
                                                            # fk_stockdetails = ins_stock_details)----un comment only when stock details consider

                                if dct_enquiry['vchr_enquiry_status'] == 'BOOKED':
                                    # ins_item_enq.int_sold = int(dct_enquiry['int_quantity'])
                                    # ins_item_enq.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                                    ins_item_enq.dbl_imei_json = {"imei" : dct_enquiry['lst_imei']}
                                    ins_item_enq.int_sold = dct_enquiry['int_quantity']
                                ins_item_enq.save()
                                if ins_item_enq and dct_enquiry.get('vchr_enquiry_status','') == 'BOOKED':
                                    '''Following code commented in order to prevent lost case if same product booked multiple times'''
                                    '''ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company,fk_product_id=int_product_id).exclude(vchr_enquiry_status = 'BOOKED')
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
                                    # ins_manager=UserModel.objects.filter(fk_branch_id=request.user.usermodel.fk_branch_id,fk_group__vchr_name='BRANCH MANAGER').values_list('username',flat=True)

                                    ins_manager=UserModel.objects.filter(fk_branch_id=request.user.usermodel.fk_branch_id,fk_group__vchr_name='BRANCH MANAGER').values_list('username',flat=True)
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

                                ################

                                ins_item_foll = ItemFollowup(  fk_item_enquiry = ins_item_enq,
                                                                dat_followup = datetime.now(),
                                                                fk_user = ins_user,
                                                                vchr_notes = dct_enquiry['vchr_remarks'],
                                                                vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                dbl_amount = dct_enquiry['dbl_estimated_amount'],
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
                            ,fk_assigned = ins_assigned_user
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
class AddFollowup(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            dat_created = datetime.now()
            dct_data = request.data
            with transaction.atomic():
                ins_customer_id=ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).values('fk_enquiry_master__fk_customer_id')
                # Save customer email
                if request.data.get('cust_email'):
                    ins_cust_email = CustomerModel.objects.filter(~Q(id = ins_customer_id[0]['fk_enquiry_master__fk_customer_id']) & Q(cust_email = request.data.get('cust_email')))
                    if ins_cust_email:
                        return Response({'status':'1', 'data':'Customer email already exist'})
                    else:
                        CustomerModel.objects.filter(id = ins_customer_id[0]['fk_enquiry_master__fk_customer_id']).update(cust_email = request.data.get('cust_email'))
                #
                str_enquiry_no = ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                if ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.user.username:
                    dat_updated_time = dat_created
                    fk_updated_by = request.user.id
                    int_status = 1
                else :
                    dat_updated_time = None
                    fk_updated_by = None
                    int_status = 0

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
                    int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = request.user.usermodel,\
                    fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                ins_item_follow_up.save()

                if request.data.get('vchr_followup_status')== 'BOOKED':
                    ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status='BOOKED',dbl_imei_json={"imei" : request.data.get('lst_imei',[])})
                if int_status:
                    ins_obj = ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                    ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                    dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
                if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                    ins_obj.update(dbl_imei_json = {"imei" : request.data.get('lst_imei',[])},int_sold = request.data.get('int_followup_quantity'))
                    '''Following code commented in order to prevent lost case if same product booked multiple times'''

                    '''ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id = ins_customer_id,fk_enquiry_master__fk_company = request.user.usermodel.fk_company,fk_product_id=ins_obj.first().fk_product_id).exclude(vchr_enquiry_status = 'BOOKED')
                    if ins_item_enq_exist:
                        ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                        lst_query_set = []
                        for ins_data in ins_item_enq_exist:
                            ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                                              vchr_notes = 'Same product '+ ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                              vchr_enquiry_status = 'LOST',
                                                              int_status = 1,
                                                              dbl_amount = 0.0,
                                                              fk_user = request.user.usermodel,
                                                              fk_updated = request.user.usermodel,
                                                              dat_followup = datetime.now(),
                                                              dat_updated = datetime.now())
                            lst_query_set.append(ins_follow_up)
                        if lst_query_set:
                            ItemFollowup.objects.bulk_create(lst_query_set);
                            '''
                int_enquiry_id = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_enquiry_num = str_enquiry_no, fk_company_id = request.user.usermodel.fk_company_id).pk_bint_id
                # enquiry_print(str_enquiry_no,request,ins_user)
                return JsonResponse({'status':'success','value':'Follow-up completed successfully!','remarks':request.data['vchr_followup_remarks'],'followup':request.data['vchr_followup_status'],'amount':request.data['int_followup_amount'],'change':int_status,'enqId':int_enquiry_id,'int_quantity':request.data.get('int_followup_quantity')})


        except Exception as e:
            return Response({'status':'1', 'error':str(e)})
            # if int_status:
            #     ins_user = request.user

        # except Exception as e:
        #     return JsonResponse({'status':'0','data':str(e)})
class EnquiryList(APIView):
    permission_classes=[IsAuthenticated]


    def post(self,request):
        try:
            # import pdb;pdb.set_trace()
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
            lst_statuses= ["LOST","BOOKED","UNQUALIFIED","INVOICED"]
            rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                        CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                        AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name'),\
                                        ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_product_name.label('service'))\
                                        .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                        .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end,\
                                         EnquiryMasterSA.fk_company_id ==  ins_user.fk_company_id)\
                                        .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                        .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.id)\
                                        .order_by(desc(EnquiryMasterSA.dat_created_at))
            if request.user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                pass
            elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
            elif request.user.usermodel.int_area_id:
                # lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
                rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            else:
                rst_enquiry =rst_enquiry.filter(EnquiryMasterSA.fk_branch_id== request.user.usermodel.fk_branch_id,EnquiryMasterSA.fk_assigned_id==request.user.id)

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
                    if dct_data['vchr_enquiry_status'].upper() not in ['BOOKED','LOST','INVOICED']:
                        dct_enquiries['status_display'] = 'pending'
                    elif dct_data['vchr_enquiry_status'].upper() == 'BOOKED' and dct_enquiries['status_display'] != 'pending':
                        dct_enquiries['status_display'] = 'booked'
                    elif dct_data['vchr_enquiry_status'].upper() in ['LOST'] and dct_enquiries['status_display'] not in ['pending','booked']:
                        dct_enquiries['status_display'] = 'lost'
                else:
                    if dct_enquiries == {}:
                        dct_enquiries = {'enquiry_id':dct_data['pk_bint_id'],'enquiry':dct_data['vchr_enquiry_num'],'date':dct_data['dat_created_at'],\
                                        'customer_name':dct_data['customer_first_name']+' '+dct_data['customer_last_name'],'staff_name':dct_data['staff_first_name']+' '+dct_data['staff_last_name'],\
                                        'status':[dct_data['vchr_enquiry_status'].title()],'services':[dct_data['service'].title()]
                                        }
                    else:
                        lst_enquiry_data.append(dct_enquiries)
                        dct_enquiries = {'enquiry_id':dct_data['pk_bint_id'],'enquiry':dct_data['vchr_enquiry_num'],'date':dct_data['dat_created_at'],\
                                         'customer_name':dct_data['customer_first_name']+' '+dct_data['customer_last_name'],'staff_name':dct_data['staff_first_name']+' '+dct_data['staff_last_name'],\
                                         'status':[dct_data['vchr_enquiry_status'].title()],'services':[dct_data['service'].title()]
                                         }
                    if dct_data['vchr_enquiry_status'].upper() not in ['BOOKED','LOST','INVOICED']:
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
            session.close()
            return Response({'status':'1','data':[str(e)]})

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
                                            ItemEnquirySA.c.pk_bint_id,ItemEnquirySA.c.dbl_min_price,ItemEnquirySA.c.dbl_max_price,\
                                            ItemEnquirySA.c.vchr_enquiry_status,ItemEnquirySA.c.int_quantity,ItemEnquirySA.c.dbl_amount,ItemEnquirySA.c.dbl_imei_json,ItemEnquirySA.c.vchr_remarks,ProductsSA.vchr_product_name.label('product'),\
                                            BrandSA.vchr_brand_name,ItemSA.vchr_item_name,\
                                            SourceSA.vchr_source_name,PrioritySA.vchr_priority_name,BranchSA.vchr_name)\
                                            .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                            .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                            .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.c.fk_enquiry_master_id)\
                                            .join(ProductsSA,ItemEnquirySA.c.fk_product_id == ProductsSA.id)\
                                            .join(BrandSA,ItemEnquirySA.c.fk_brand_id == BrandSA.id)\
                                            .join(ItemSA,ItemEnquirySA.c.fk_item_id == ItemSA.id)\
                                            .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                                            .join(PrioritySA, EnquiryMasterSA.fk_priority_id == PrioritySA.pk_bint_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                            .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N' )

            dct_enquiries = {}
            # dct_enquiry_data = {}
            for dct_data in rst_enquiry.all():
                dct_data = dct_data._asdict()
                if dct_data['product'] not in dct_enquiries:
                    dct_enquiries[dct_data['product']] = []
                # dct_enquiries[dct_data['product']].append(dct_data)
                dct_enquiries[dct_data['product']].append({'pk_bint_id':dct_data['pk_bint_id'],'vchr_brand_name':dct_data['vchr_brand_name'], 'vchr_item_name':dct_data['vchr_item_name'],'int_quantity':dct_data['int_quantity'],'vchr_enquiry_status':dct_data['vchr_enquiry_status'],'dbl_imei_json':dct_data['dbl_imei_json'],'dbl_amount':dct_data['dbl_amount'],'vchr_remarks':dct_data['vchr_remarks'],'dbl_min_price':dct_data['dbl_min_price'],'dbl_max_price':dct_data['dbl_max_price'],'status':False})

            if rst_enquiry.all():
                dct_customer_data = {'vchr_enquiry_num':dct_data['vchr_enquiry_num'],'cust_fname':dct_data['cust_fname'],'cust_lname':dct_data['cust_lname'],'cust_mobile':dct_data['cust_mobile'],'dat_created_at':dct_data['dat_created_at'],'cust_email':dct_data['cust_email'],'cust_alternatemobile':dct_data['cust_alternatemobile'],'cust_alternatemail':dct_data['cust_alternatemail'],'vchr_source_name':dct_data['vchr_source_name'],'vchr_priority_name':dct_data['vchr_priority_name'],'cust_contactsrc':dct_data['cust_contactsrc'],'bln_sms':dct_data['bln_sms'],'vchr_name':dct_data['vchr_name']}
            session.close()
            return Response({'status' : '0','dct_enquiry_details':dct_enquiries,'dct_customer_data':dct_customer_data})

        except Exception as e:
            session.close()
            return Response({'status':'1','data':[str(e)]})

class PendingEnquiryListSide(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            int_company_id = request.user.usermodel.fk_company_id
            if not int_company_id:
                return Response({'status':'1','data':["No company found"]})
            else:
                # dat_start = ""
                # dat_end = ""
                # if not request.data['_status']:
                #     if request.data['start_date']:
                #         dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y').replace(day=1)
                #     if request.data['end_date']:
                #         dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')
                # else:
                #     if request.data['start_date']:
                #         dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y')
                #     if request.data['end_date']:
                #         dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')

                int_cust_id=request.data.get('fk_customer_id')
                # int_branch_id=request.data.get('branchId')
                session = Session()
                lst_enquiry_data = []
                # rst_mobile = session.query(MobileEnquirySA.dbl_amount.label('amount'),MobileEnquirySA.vchr_enquiry_status.label('status'),literal("Mobile").label("vchr_service"),MobileEnquirySA.int_quantity.label('int_quantity'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'),MobileEnquirySA.vchr_remarks.label('remarks'))
                # # .filter(MobileEnquirySA.vchr_enquiry_status != 'LOST' ,MobileEnquirySA.vchr_enquiry_status != 'BOOKED' , MobileEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
                #
                # rst_tablet =session.query(TabletEnquirySA.dbl_amount.label('amount'),TabletEnquirySA.vchr_enquiry_status.label('status'),literal("Tablet").label("vchr_service"),TabletEnquirySA.int_quantity.label('int_quantity'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'),TabletEnquirySA.vchr_remarks.label('remarks'))
                # # .filter(TabletEnquirySA.vchr_enquiry_status != 'LOST' ,TabletEnquirySA.vchr_enquiry_status != 'BOOKED' , TabletEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
                #
                # rst_computer =session.query(ComputersEnquirySA.dbl_amount.label('amount'),ComputersEnquirySA.vchr_enquiry_status.label('status'),literal("Computer").label("vchr_service"),ComputersEnquirySA.int_quantity.label('int_quantity'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'),ComputersEnquirySA.vchr_remarks.label('remarks'))
                # # .filter(ComputersEnquirySA.vchr_enquiry_status != 'LOST' ,ComputersEnquirySA.vchr_enquiry_status != 'BOOKED' , ComputersEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
                #
                # rst_accessories =session.query(AccessoriesEnquirySA.dbl_amount.label('amount'),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.int_quantity.label('int_quantity'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FKrequest,_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'),AccessoriesEnquirySA.vchr_remarks.label('remarks'))
                # # .filter(AccessoriesEnquirySA.vchr_enquiry_status != 'LOST' ,AccessoriesEnquirySA.vchr_enquiry_status != 'BOOKED' , AccessoriesEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
                # rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
                #
                # rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service,rst_data.c.int_quantity,rst_data.c.amount,rst_data.c.vchr_service,rst_data.c.status,BranchSA.vchr_name,ItemSA.vchr_item_name,rst_data.c.remarks)\
                #                         .filter( EnquiryMasterSA.fk_company_id == int_company_id,EnquiryMasterSA.fk_customer_id == int_cust_id)\
                #                         .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
                #                         .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                #                         .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                #                         .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                #                         .join(BrandSA,BrandSA.id==rst_data.c.brand_id)\
                #                         .join(ItemSA,ItemSA.id==rst_data.c.item_id)
                rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                            CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                            AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name'),\
                                            ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_product_name.label('service'),BranchSA.vchr_name,ItemEnquirySA.vchr_remarks,ItemEnquirySA.int_quantity,ItemEnquirySA.dbl_amount,ItemSA.vchr_item_name,BrandSA.vchr_brand_name)\
                                            .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                            .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                            .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                            .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.id)\
                                            .join(BrandSA,ItemEnquirySA.fk_brand_id==BrandSA.id).filter(EnquiryMasterSA.fk_company_id == int_company_id,EnquiryMasterSA.fk_customer_id == int_cust_id).join(ItemSA,ItemSA.id==ItemEnquirySA.fk_item_id)
                                        # .group_by(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service, CustomerSA.cust_fname,BranchSA.vchr_name,ItemsSA.vchr_item_name,\
                                        # rst_data.c.vchr_service,rst_data.c.remarks,CustomerSA.cust_fname,CustomerSA.cust_lname,)

                                                    # , EnquiryMasterSA.int_company_id == int_company_id )\
                                        # .filter(EnquiryMasterSA.dat_created_at >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end, EnquiryMasterSA.fk_company_id == int_company_id )\

                # if dat_start:
                #         rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.dat_created_at >= dat_start)
                # if dat_end:
                #     rst_enquiry = rst_enquiry.filter(cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end)
                # if int_cust_id:
                #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_customer_id == int_cust_id)
                # if int_branch_id:
                #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == int_branch_id)

                rst_enquiry = rst_enquiry.order_by(desc(EnquiryMasterSA.dat_created_at))
                if not rst_enquiry.all():
                    session.close()
                    return Response({'status':'failed','data':'No data'})
                # for a in rst_enquiry.order_by(EnquiryMasterSA.dat_created_at.desc()).all() : a.dat_created_at
                dct_enquiries = {}
                for dct_data in rst_enquiry.all():
                    if dct_data.vchr_enquiry_num == dct_enquiries.get('enquiry'):
                        dct_enquiries['services'].append(dct_data._asdict()['service'])
                        dct_enquiries['brands'].append(dct_data._asdict()['vchr_brand_name'])
                        dct_enquiries['items'].append(dct_data._asdict()['vchr_item_name'])
                        dct_enquiries['status'].append(dct_data._asdict()['vchr_enquiry_status'])
                        dct_enquiries['remarks'].append(dct_data._asdict()['vchr_remarks'])
                        dct_enquiries['amount'].append(dct_data._asdict()['dbl_amount'])
                        dct_enquiries['quantity'].append(dct_data._asdict()['int_quantity'])
                    else:
                        if dct_enquiries == {}:
                            dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'].strftime('%d-%m-%Y'),'services':[dct_data._asdict()['service']],'status':[dct_data._asdict()['vchr_enquiry_status']],'branch':dct_data._asdict()['vchr_name'],'amount':[dct_data._asdict()['dbl_amount']],'quantity':[dct_data._asdict()['int_quantity']],'items':[dct_data._asdict()['vchr_item_name']],'brands':[dct_data._asdict()['vchr_brand_name']],'remarks':[dct_data._asdict()['vchr_remarks']]}
                        else:
                            lst_enquiry_data.append(dct_enquiries)
                            dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'].strftime('%d-%m-%Y'),'services':[dct_data._asdict()['service']],'status':[dct_data._asdict()['vchr_enquiry_status']],'branch':dct_data._asdict()['vchr_name'],'amount':[dct_data._asdict()['dbl_amount']],'quantity':[dct_data._asdict()['int_quantity']],'items':[dct_data._asdict()['vchr_item_name']],'brands':[dct_data._asdict()['vchr_brand_name']],'remarks':[dct_data._asdict()['vchr_remarks']]}
                lst_enquiry_data.append(dct_enquiries)
                # lst_enquiry_data=paginate_data(lst_enquiry_data,5)
                #             dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'services':[dct_data._asdict()['vchr_service']],'branch':dct_data._asdict()['vchr_name'],'amount':dct_data._asdict()['amount'],'item':dct_data._asdict()['vchr_item_name'],'remarks':dct_data._asdict()['remarks']}
                # lst_enquiry_data.append(dct_enquiries)
                #             dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
                session.close()
                return Response({'status':'success','data':lst_enquiry_data})
        except Exception as e:
            session.close()
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':[str(e)]})

class Source_PriorityAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            lst_source = list(Source.objects.filter(bln_status=True,fk_company_id = request.user.usermodel.fk_company_id).values('vchr_source_name','pk_bint_id').order_by('pk_bint_id'))
            lst_priority = list(Priority.objects.filter(bln_status=True,fk_company_id = request.user.usermodel.fk_company_id).values('vchr_priority_name','pk_bint_id').order_by('pk_bint_id'))
            return Response({'source':lst_source,'priority':lst_priority})

        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})


def paginate_data(dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    # sorted_dct_data = reversed(sorted(dct_data.items())
    # dct_data = OrderedDict(sorted_dct_data)
    for key in dct_data:
        if int_count not in dct_paged:
            dct_paged[int_count]=[]
            dct_paged[int_count].append(key)
        elif len(dct_paged[int_count]) < int_page_legth:
            dct_paged[int_count].append(key)
        else:
            int_count += 1
            dct_paged[int_count] =[]
            dct_paged[int_count].append(key)
    return dct_paged



class GetDataForMobileEnquiry(APIView):
    """Onload details for mobile enquiry"""
    permission_classes = [IsAuthenticated]
    def get(self,request,):
        try:
            lst_product_visible = []
            lst_product = []
            ins_product = Products.objects.filter(fk_company = request.user.usermodel.fk_company).exclude(vchr_product_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY'] ).values('id','vchr_product_name','bln_visible','dct_product_spec').order_by('id')
            lst_other_prodcuts = []
            dct_na_stock_product = {}
            if ins_product:
                for itr_item in ins_product:
                    dct_product = {}
                    if not itr_item['bln_visible']:
                        if itr_item['vchr_product_name'] not in lst_other_prodcuts:
                            lst_other_prodcuts.append(itr_item['vchr_product_name'])
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


                lst_source = list(Source.objects.filter(bln_status=True,fk_company_id = request.user.usermodel.fk_company_id).values('vchr_source_name','pk_bint_id').order_by('pk_bint_id'))
                lst_priority = list(Priority.objects.filter(bln_status=True,fk_company_id = request.user.usermodel.fk_company_id).values('vchr_priority_name','pk_bint_id').order_by('pk_bint_id'))


                int_companyId = request.GET.get('id',request.user.usermodel.fk_company_id)

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
                    'lstNaStockProduct':dct_na_stock_product,
                    'lst_source':lst_source,
                    'lst_priority':lst_priority,'userListData':userListData})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            return Response({'result':'failed','reason':e})
