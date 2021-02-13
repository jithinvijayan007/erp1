from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_404_NOT_FOUND
from datetime import datetime
from django.contrib.auth.models import User
from userdetails.models import UserDetails as UserModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import and_,func ,cast,Date
from company_permissions.models import MainCategory,GroupPermissions,SubCategory

from enquiry.models import EnquiryMaster
from customer.models import CustomerDetails as CustomerModel
from enquiry_print.views import enquiry_print
from enquiry_mobile.models import ComputersEnquiry,ComputersFollowup,TabletEnquiry,TabletFollowup,AccessoriesEnquiry,AccessoriesFollowup,MobileEnquiry,MobileFollowup, ItemEnquiry, ItemFollowup,GDPRange
from django.db import transaction
from stock_app.models import Stockmaster,Stockdetails
from django.db.models import Case,  Value, When,F
from django.db.models import Q
# from inventory.models import Products,Items
from products.models import Products
from item_category.models import Item as Items
from django.conf import settings
import requests

EnquiryMasterSA = EnquiryMaster.sa
CustomerSA = CustomerModel.sa
AuthUserSA = User.sa
ProductsSA = Products.sa

ComputersEnquirySA = ComputersEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
MobileEnquirySA = MobileEnquiry.sa

ComputersFollowupSA = ComputersFollowup.sa
TabletFollowupSA = TabletFollowup.sa
AccessoriesFollowupSA = AccessoriesFollowup.sa
MobileFollowupSA = MobileFollowup.sa
ItemFollowupSA = ItemFollowup.sa
ItemEnquirySA = ItemEnquiry.sa

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

# class AddFollowup(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             dat_created = datetime.now()
#             if request.data['vchr_servicetype'] == 'computers':
#                 try:
#                     with transaction.atomic():
#                         str_enquiry_no = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
#                         if ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.data['vchr_current_user_name'] :
#                             dat_updated_time = dat_created
#                             fk_updated_by = UserModel.objects.get(username = request.data['vchr_current_user_name']).id
#                             int_status = 1
#                         else :
#                             dat_updated_time = None
#                             fk_updated_by = None
#                             int_status = 0
#
#                         if request.data.get('vchr_followup_status') == 'BOOKED':
#                             int_status = 1
#                             rst_enq = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
#                             ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
#                             if ins_stock:
#                                 Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
#                             else:
#                                 ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
#                                 int_available = ins_stock.int_available
#                                 return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
#                         ins_computers_follow_up = ComputersFollowup(fk_computers = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                             vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                             int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(username = request.data['vchr_current_user_name']),\
#                             fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
#                         ins_computers_follow_up.save()
#                         if request.data.get('vchr_followup_status')== 'BOOKED':
#                             ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
#                         if int_status:
#                             ins_obj = ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
#                             ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
#                             dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
#                         if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
#                             ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
#                             dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
#                             ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})
#
#                 except Exception as e:
#                     return Response({'status':'1', 'error':str(e)})
#
#             elif request.data['vchr_servicetype'] == 'tablet':
#                 try:
#                     with transaction.atomic():
#                         str_enquiry_no = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
#                         if TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.data['vchr_current_user_name'] :
#                             dat_updated_time = dat_created
#                             fk_updated_by = UserModel.objects.get(username = request.data['vchr_current_user_name']).id
#                             int_status = 1
#                         else :
#                             dat_updated_time = None
#                             fk_updated_by = None
#                             int_status = 0
#                         if  request.data.get('vchr_followup_status') == 'BOOKED':
#                             int_status = 1
#                             rst_enq = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
#                             ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
#                             if ins_stock:
#                                 Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
#                             else:
#                                 ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
#                                 int_available = ins_stock.int_available
#                                 return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
#                         ins_tablet_followup = TabletFollowup(fk_tablet = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                             vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                             int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(username = request.data['vchr_current_user_name']),\
#                             fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
#                         ins_tablet_followup.save()
#                         if request.data.get('vchr_followup_status')== 'BOOKED':
#                             TabletEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
#                         if int_status:
#                             ins_obj = TabletEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
#                             ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],dbl_amount = request.data['int_followup_amount'],int_quantity=request.data.get('int_followup_quantity'),
#                             vchr_remarks= request.data['vchr_followup_remarks'])
#                         if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
#                             ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
#                             dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
#                             ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})
#
#                 except Exception as e:
#                     return Response({'status':'1', 'error':str(e)})
#
#
#             elif request.data['vchr_servicetype'] == 'accessories':
#                 try:
#                     with transaction.atomic():
#                         str_enquiry_no = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
#                         if AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.data['vchr_current_user_name'] :
#                             dat_updated_time = dat_created
#                             fk_updated_by = UserModel.objects.get(username = request.data['vchr_current_user_name']).id
#                             int_status = 1
#                         else :
#                             dat_updated_time = None
#                             fk_updated_by = None
#                             int_status = 0
#                         if request.data.get('vchr_followup_status') == 'BOOKED':
#                             int_status =1
#                             rst_enq = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
#                             ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
#                             if ins_stock:
#                                 Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
#                             else:
#                                 ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
#                                 int_available = ins_stock.int_available
#                                 return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
#                         ins_accessories_follow_up = AccessoriesFollowup(fk_accessories = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                             vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                             int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(username = request.data['vchr_current_user_name']),\
#                             fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
#                         ins_accessories_follow_up.save()
#                         if request.data.get('vchr_followup_status')== 'BOOKED':
#                             AccessoriesEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
#                         if int_status:
#                             ins_obj = AccessoriesEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
#                             ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
#                             dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
#                         if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
#                             ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
#                             dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
#                             ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})
#
#                 except Exception as e:
#                     return Response({'status':'1', 'error':str(e)})
#
#             elif request.data['vchr_servicetype'] == 'mobile':
#                 try:
#                     with transaction.atomic():
#                         str_enquiry_no = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
#                         if MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.data['vchr_current_user_name'] :
#                             dat_updated_time = dat_created
#                             fk_updated_by = UserModel.objects.get(username = request.data['vchr_current_user_name']).id
#                             int_status = 1
#                         else :
#                             dat_updated_time = None
#                             fk_updated_by = None
#                             int_status = 0
#                         if request.data.get('vchr_followup_status') == 'BOOKED':
#                             int_status =1
#                             rst_enq = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
#                             ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
#                             if ins_stock:
#                                 Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
#                             else:
#                                 ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
#                                 int_available = ins_stock.int_available
#                                 return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
#                         ins_mobile_follow_up = MobileFollowup(fk_mobile = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                             vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                             int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(username = request.data['vchr_current_user_name']),\
#                             fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
#                         ins_mobile_follow_up.save()
#                         if request.data.get('vchr_followup_status')== 'BOOKED':
#                             MobileEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
#                         if int_status:
#                             ins_obj = MobileEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
#                             ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
#                             dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
#                         if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
#                             ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
#                             dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
#                             ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})
#
#                 except Exception as e:
#                     return Response({'status':'1', 'error':str(e)})
#             if int_status:
#                 ins_user = UserModel.objects.get(username = request.data['vchr_current_user_name'])
#                 enquiry_print(str_enquiry_no,request,ins_user)
#             int_enquiry_id = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_enquiry_num = str_enquiry_no, fk_company_id = request.user.userdetails.fk_company_id).pk_bint_id
#             return JsonResponse({'status':'success','value':'Follow-up completed successfully!','remarks':request.data['vchr_followup_remarks'],'followup':request.data['vchr_followup_status'],'amount':request.data['int_followup_amount'],'change':int_status,'enqId':int_enquiry_id,'int_quantity':request.data.get('int_followup_quantity')})
#
#         except Exception as e:
#             return JsonResponse({'status':'0','data':str(e)})
class AddFollowup(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            dat_created = datetime.now()
            dct_data = request.data
            with transaction.atomic():
                lst_item_pos = []

                ins_customer_id=ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).values('fk_enquiry_master__fk_customer_id')
                str_enquiry_no = ItemEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                enq_mastr_id=ItemEnquiry.objects.filter(pk_bint_id = request.data['int_service_id']).values('fk_enquiry_master__pk_bint_id').first()['fk_enquiry_master__pk_bint_id']
                if request.data.get('vchr_followup_status') == 'BOOKED':
                    ins_customer = CustomerModel.objects.filter(id = ins_customer_id).first()
                    ins_enq_master = EnquiryMaster.objects.filter(pk_bint_id=enq_mastr_id).first()
                    dct_pos_data = {}
                    dct_pos_data['vchr_cust_name'] = ins_customer.cust_fname+' '+ins_customer.cust_lname
                    dct_pos_data['vchr_cust_email'] = ins_customer.cust_email
                    dct_pos_data['int_cust_mob'] = ins_customer.cust_mobile
                    dct_pos_data['vchr_gst_no'] = ins_customer.vchr_gst_no
                    dct_pos_data['int_enq_master_id'] = ins_enq_master.pk_bint_id
                    dct_pos_data['vchr_enquiry_num'] = ins_enq_master.vchr_enquiry_num
                    dct_pos_data['vchr_location'] = ''
                    dct_pos_data['int_pin_code'] = ''
                    dct_pos_data['txt_address'] = ''
                    if ins_customer.fk_location:
                        dct_pos_data['vchr_location'] = ins_customer.fk_location.vchr_name
                        dct_pos_data['vchr_district'] = ins_customer.fk_location.vchr_district
                        dct_pos_data['vchr_pin_code'] = ins_customer.fk_location.vchr_pin_code
                    if ins_customer.fk_state:
                        dct_pos_data['vchr_state_code'] = ins_customer.fk_state.vchr_code
                    dct_pos_data['vchr_staff_code'] = ins_enq_master.fk_assigned.username
                    dct_pos_data['vchr_branch_code'] = ins_enq_master.fk_branch.vchr_code
                    if not ins_enq_master.vchr_remarks and request.data.get('vchr_followup_remarks'):
                        dct_pos_data['str_remarks'] = request.data.get('vchr_followup_remarks')
                    elif request.data.get('vchr_followup_remarks'):
                        dct_pos_data['str_remarks'] = ins_enq_master.vchr_remarks+', '+request.data.get('vchr_followup_remarks')
                    else:
                        dct_pos_data['str_remarks'] = ins_enq_master.vchr_remarks
                    dct_pos_data['dat_enquiry'] = ins_enq_master.dat_created_at.strftime('%Y-%m-%d')
                    dct_pos_data['dct_products'] = {}
                    dct_pos_data['lst_item'] = []
                    dct_pos_data['dbl_total_amt'] = float(request.data.get('int_followup_amount'))
                    dct_pos_data['dbl_discount'] = float(request.data.get('int_followup_discount_amount'))
                    dct_item = {}
                    if request.data.get('fk_item_id'):
                        ins_item = Items.objects.filter(id=request.data.get('fk_item_id')['id']).first()
                        dct_item['vchr_item_name'] = ins_item.vchr_item_name
                        dct_item['vchr_item_code'] = ins_item.vchr_item_code

                    else:
                        ins_item_enq = ItemEnquiry.objects.filter(pk_bint_id=request.data.get('int_service_id')).first()
                        dct_item['vchr_item_name'] = ins_item_enq.fk_item.vchr_item_name
                        dct_item['vchr_item_code'] = ins_item_enq.fk_item.vchr_item_code

                    dct_item['item_enquiry_id'] = request.data['int_service_id']
                    dct_item['json_imei'] = {"imei" : request.data.get('lst_imei')}
                    dct_item['int_quantity'] = int(request.data.get('int_followup_quantity'))
                    dct_item['dbl_amount'] = float(request.data.get('int_followup_amount'))
                    dct_item['dbl_discount'] = float(request.data.get('int_followup_discount_amount'))
                    dct_item['dbl_buyback'] = float(request.data.get('int_followup_buyback_amount'))
                    dct_item['int_status'] = 1
                    dct_item['vchr_remarks'] = request.data.get('vchr_followup_remarks')
                    dct_pos_data['lst_item'].append(dct_item)
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
                dbl_discount = 0
                dbl_buyback = 0
                dbl_gdw = 0
                dbl_gdew = 0
                # import pdb; pdb.set_trace()
                if request.data.get('int_followup_discount_amount'):
                    dbl_discount = request.data.get('int_followup_discount_amount')
                if request.data.get('int_followup_buyback_amount'):
                    dbl_buyback = request.data.get('int_followup_buyback_amount')
                if request.data.get('dbl_gdp'):
                    dbl_gdw=request.data.get('dbl_gdp')
                if request.data.get('dbl_gdew'):
                    dbl_gdew=request.data.get('dbl_gdew')
                if request.data.get('vchr_followup_status')== 'BOOKED':
                    ins_gp_item=Items.objects.filter(vchr_item_name__in=['GDP','GDEW (EXTENDED WARRANTY)']).values()
                    dct_gdp_data={data_gdp['vchr_item_name']:{'product_id':data_gdp['fk_product_id'],'brand_id':data_gdp['fk_brand_id'],
                                                                                'pk_bint_id':data_gdp['id'],'item_code':data_gdp['vchr_item_code']} for data_gdp in ins_gp_item}
                    if request.data.get('int_type') in [1,3] and dct_gdp_data.get('GDP'):
                        ins_range=GDPRange.objects.filter(dbl_from__lte=dbl_gdw,dbl_to__gte=dbl_gdw,int_type=1).values('dbl_amt','int_type')
                        dct_actual_gdp={data_range['int_type']:data_range['dbl_amt'] for data_range in ins_range}
                        ins_item_gdp_enq = ItemEnquiry(fk_enquiry_master_id = enq_mastr_id,
                                            fk_product_id=dct_gdp_data['GDP'].get('product_id'),
                                            fk_brand_id = dct_gdp_data['GDP'].get('brand_id'),
                                            fk_item_id = dct_gdp_data['GDP'].get('pk_bint_id'),
                                            int_quantity = int(request.data.get('int_followup_quantity')),
                                            dbl_amount = dbl_gdw,
                                            vchr_enquiry_status = 'BOOKED',
                                            # vchr_remarks = dct_enquiry['vchr_remarks'],
                                            dbl_discount_amount = 0,
                                            dbl_buy_back_amount = 0,
                                            int_sold = int(request.data.get('int_followup_quantity')),
                                            dbl_imei_json = {"imei" : request.data.get('lst_imei',[])},
                                            dbl_actual_est_amt = dct_actual_gdp[1],
                                            dat_sale = datetime.now()
                                            )
                        ins_item_gdp_enq.save()
                        dct_item={}
                        dct_pos_data['dbl_total_amt'] += float(dbl_gdw)
                        dct_item['item_enquiry_id'] = ins_item_gdp_enq.pk_bint_id
                        dct_item['vchr_item_name'] = 'GDP'
                        dct_item['vchr_item_code'] = dct_gdp_data['GDP'].get('item_code')
                        dct_item['json_imei'] = {"imei" : request.data.get('lst_imei')}
                        dct_item['int_quantity'] = int(request.data.get('int_followup_quantity'))
                        dct_item['dbl_amount'] = float(dbl_gdw)
                        dct_item['int_status'] = 1
                        dct_item['dbl_discount'] = 0.0
                        dct_item['dbl_buyback'] = 0.0
                        dct_item['vchr_remarks'] = request.data.get('vchr_followup_remarks')
                        lst_item_pos.append(dct_item)
                    if request.data.get('int_type') in [2,3] and dct_gdp_data.get('GDEW (EXTENDED WARRANTY)'):
                        ins_range=GDPRange.objects.filter(dbl_from__lte=dbl_gdew,dbl_to__gte=dbl_gdew,int_type=2).values('dbl_amt','int_type')
                        dct_actual_gdp={data_range['int_type']:data_range['dbl_amt'] for data_range in ins_range}
                        ins_item_gdp_enq = ItemEnquiry(fk_enquiry_master_id = enq_mastr_id,
                                            fk_product_id=dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('product_id'),
                                            fk_brand_id = dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('brand_id'),
                                            fk_item_id = dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('pk_bint_id'),
                                            int_quantity = int(request.data.get('int_followup_quantity')),
                                            dbl_amount = dbl_gdew,
                                            vchr_enquiry_status = 'BOOKED',
                                            # vchr_remarks = dct_enquiry['vchr_remarks'],
                                            dbl_discount_amount = 0,
                                            dbl_buy_back_amount = 0,
                                            int_sold = int(request.data.get('int_followup_quantity')),
                                            dbl_imei_json = {"imei" : request.data.get('lst_imei',[])},
                                            dbl_actual_est_amt = dct_actual_gdp[2],
                                            dat_sale = datetime.now()
                                            )
                        ins_item_gdp_enq.save()
                        dct_item={}
                        dct_pos_data['dbl_total_amt'] += float(dbl_gdew)
                        dct_item['item_enquiry_id'] = ins_item_gdp_enq.pk_bint_id
                        dct_item['vchr_item_name'] = 'GDEW (EXTENDED WARRANTY)'
                        dct_item['vchr_item_code'] = dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('item_code')
                        dct_item['json_imei'] = {"imei" : request.data.get('lst_imei')}
                        dct_item['int_quantity'] = int(request.data.get('int_followup_quantity'))
                        dct_item['dbl_amount'] = float(dbl_gdew)
                        dct_item['int_status'] = 1
                        dct_item['dbl_discount'] = 0.0
                        dct_item['dbl_buyback'] = 0.0
                        dct_item['vchr_remarks'] = request.data.get('vchr_followup_remarks')
                        lst_item_pos.append(dct_item)
                    ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(int_sold=request.data.get('int_followup_quantity'),dbl_amount = request.data['int_followup_amount'],vchr_enquiry_status='BOOKED',dbl_imei_json={"imei" : request.data.get('lst_imei',[])},dbl_buy_back_amount = dbl_buyback,dbl_discount_amount =dbl_discount,dbl_gdp_amount=0,dbl_gdew_amount=0,int_type=int(request.data.get('int_type')))
                if int_status and request.data.get('vchr_followup_status')!= 'BOOKED':

                    ins_obj = ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                    ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                    dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'],dbl_buy_back_amount = dbl_buyback,dbl_discount_amount =dbl_discount,dbl_gdp_amount=dbl_gdw,dbl_gdew_amount=dbl_gdew)
                if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                    ins_obj = ItemEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                    ins_obj.update(dbl_amount = request.data['int_followup_amount'],dbl_imei_json = {"imei" : request.data.get('lst_imei',[])},int_sold = request.data.get('int_followup_quantity'),dbl_buy_back_amount = dbl_buyback,dbl_discount_amount =dbl_discount,dbl_gdp_amount=dbl_gdw,dbl_gdew_amount=dbl_gdew)
                    '''Following code commented in order to prevent lost case if same product booked multiple times'''

                    '''
                    ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id = ins_customer_id,fk_enquiry_master__fk_company = request.user.userdetails.fk_company,fk_product_id=ins_obj.first().fk_product_id).exclude(vchr_enquiry_status__in =['BOOKED','INVOICED'])
                    if ins_item_enq_exist:
                        ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                        lst_query_set = []
                        for ins_data in ins_item_enq_exist:
                            ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                                              vchr_notes = ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                              vchr_enquiry_status = 'LOST',
                                                              int_status = 1,
                                                              dbl_amount = 0.0,
                                                              int_quantity = 0,
                                                              fk_user = request.user.userdetails,
                                                              fk_updated = request.user.userdetails,
                                                              dat_followup = datetime.now(),
                                                              dat_updated = datetime.now())
                            lst_query_set.append(ins_follow_up)
                        if lst_query_set:
                            ItemFollowup.objects.bulk_create(lst_query_set);'''

                vchr_enquiry_remarks = EnquiryMaster.objects.get(pk_bint_id = enq_mastr_id).vchr_remarks
                if len(vchr_enquiry_remarks) > 0:
                    EnquiryMaster.objects.filter(pk_bint_id = enq_mastr_id).update(vchr_remarks = vchr_enquiry_remarks+' , '+'\n'+request.data.get('vchr_followup_remarks'))
                else:
                    EnquiryMaster.objects.filter(pk_bint_id = enq_mastr_id).update(vchr_remarks = request.data.get('vchr_followup_remarks'))

                int_enquiry_id = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_enquiry_num = str_enquiry_no, fk_company_id = request.user.userdetails.fk_company_id).pk_bint_id

                # ----------- POS ------------
                # import pdb; pdb.set_trace()
                if request.data.get('vchr_followup_status')== 'BOOKED':
                    dct_pos_data['lst_item'].extend(lst_item_pos)

                    url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
                    try:
                        # import pdb; pdb.set_trace()
                        res_data = requests.post(url,json=dct_pos_data)
                        if res_data.json().get('status')=='1':
                            pass
                        else:
                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                    except Exception as e:
                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
                # ----------------------------

                # if int_status:
                #     enquiry_print(str_enquiry_no,request,request.user.userdetails)
                return JsonResponse({'status':'success','value':'Follow-up completed successfully!','remarks':request.data['vchr_followup_remarks'],'followup':request.data['vchr_followup_status'],'amount':request.data['int_followup_amount'],'change':int_status,'enqId':int_enquiry_id,'int_quantity':request.data.get('int_followup_quantity')})


        except Exception as e:
            return Response({'status':'1', 'error':str(e)})
            # if int_status:
            #     ins_user = request.user

        # except Exception as e:
        #     return JsonResponse({'status':'0','data':str(e)})

class FollowupHistory(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # print(td)
            session = Session()
            rst_data = []
            lst_data = []
            dct_status = {}
            int_enquiry_id = int(request.data.get('id'))
            str_status = request.data.get('status')
            int_user = request.data.get('user')
            ins_user = UserModel.objects.get(id = int_user)
            int_company = ins_user.fk_company.pk_bint_id
            # rst_computers = session.query(EnquiryMasterSA.pk_bint_id.label("fk_enquiry_id"),ItemEnquirySA.pk_bint_id.label('service_id'),ItemFollowupSA.dat_followup,ItemFollowupSA.vchr_enquiry_status,ItemFollowupSA.dbl_amount,ItemFollowupSA.fk_item_enquiry,ItemFollowupSA.vchr_notes,ItemFollowupSA.int_status,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.dat_created_at,\
            # ProductsSA.vchr_product_name.label("vchr_service"),CustomerSA.cust_fname,CustomerSA.cust_lname,\
            # CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name)\
            # .join(ItemEnquirySA,and_(ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.fk_company_id == int_company,EnquiryMasterSA.chr_doc_status == 'N'))\
            # .join(ItemFollowupSA,ItemEnquirySA.pk_bint_id==ItemFollowupSA.fk_item_enquiry_id)\
			# .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
            # .join(AuthUserSA,ItemFollowupSA.fk_user_id == AuthUserSA.id)\
            # .join(ProductsSA,ProductsSA.id==ItemEnquirySA.fk_product_id )
            # rst_data += rst_computers.all()

            rst_data = session.query(EnquiryMasterSA.pk_bint_id.label("fk_enquiry_id"),ItemEnquirySA.pk_bint_id.label('service_id'),ItemFollowupSA.dat_followup,ItemFollowupSA.vchr_enquiry_status,ItemFollowupSA.dbl_amount,ItemFollowupSA.fk_item_enquiry,ItemFollowupSA.vchr_notes,ItemFollowupSA.int_status,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.dat_created_at,\
            ProductsSA.vchr_product_name.label("vchr_service"),CustomerSA.cust_fname,CustomerSA.cust_lname,\
            CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name)\
            .join(ItemEnquirySA,and_(ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.fk_company_id == int_company,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.pk_bint_id == int_enquiry_id))\
            .join(ItemFollowupSA,ItemEnquirySA.pk_bint_id==ItemFollowupSA.fk_item_enquiry_id)\
			.join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
            .join(AuthUserSA,ItemFollowupSA.fk_user_id == AuthUserSA.id)\
            .join(ProductsSA,ProductsSA.id==ItemEnquirySA.fk_product_id )
            # rst_data += rst_computers.all()

            # # rst_data = sorted(rst_data, key=lambda k: (k.vchr_service , k.service_id))
            # rst_data = reversed(sorted(rst_data, key=lambda k: (k.dat_followup)))

            for dct_temp in rst_data.all():
                # if int(int_enquiry_id) and dct_temp._asdict()['fk_enquiry_id'] == int_enquiry_id:
                lst_data.append(dct_temp._asdict())
            str_prev = ''
            str_prev_service_id = 0
            int_count = 0
            for dct_data in lst_data:
                if str_prev == dct_data['vchr_service'] and str_prev_service_id == dct_data['service_id']:
                    str_prev = dct_data['vchr_service']
                    str_prev_service_id= dct_data['service_id']
                    dct_data['vchr_service'] = dct_data['vchr_service'] +" - "+str(int_count)
                elif str_prev == dct_data['vchr_service'] and str_prev_service_id != dct_data['service_id']:
                    int_count += 1
                    str_prev = dct_data['vchr_service']
                    str_prev_service_id= dct_data['service_id']
                    dct_data['vchr_service'] = dct_data['vchr_service'] +" - "+str(int_count)
                else:
                    str_prev_service_id= dct_data['service_id']
                    str_prev = dct_data['vchr_service']
                    int_count = 1
                    dct_data['vchr_service'] = dct_data['vchr_service'] +" - "+str(int_count)
            session.close()
            return JsonResponse({'status':'0','data': lst_data})
        except Exception as msg:
            session.close()
            return Response({'status':'1','data':[str(msg)]})


class FollowupApproveList(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # return JsonResponse({'status':'1','data': 'lst_data'})
            lst_data = []
            rst_data = []
            int_staff_id = int(request.data.get('int_staff_id'))
            int_company= UserModel.objects.get(id = int_staff_id).fk_company.pk_bint_id
            int_group = UserModel.objects.get(id = int_staff_id).fk_group.pk_bint_id
            ins_category = SubCategory.objects.get(vchr_sub_category_name = 'ASSIGN').pk_bint_id
            ins_permission = GroupPermissions.objects.filter(fk_groups_id = int_group,fk_category_items__fk_sub_category_id = ins_category).values('bln_add')
            int_status = 0
            if not int_staff_id:
                return Response({'status':'success','data':['Please provide concerned staff details']})
            else:
                session = Session()
                rst_computers = session.query(ComputersFollowupSA.pk_bint_id.label("service_id"),ComputersFollowupSA.dat_followup,ComputersFollowupSA.vchr_enquiry_status,ComputersFollowupSA.dbl_amount,ComputersFollowupSA.vchr_notes,\
                                                                ComputersFollowupSA.int_quantity,ComputersFollowupSA.int_status,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.dat_created_at,\
                                                                literal("Computers").label("vchr_service"),AuthUserSA.first_name,AuthUserSA.last_name)\
                                                                .filter(ComputersFollowupSA.int_status == int_status)\
                                                                .join(ComputersEnquirySA,ComputersEnquirySA.pk_bint_id == ComputersFollowupSA.fk_computers_id)\
                                                                .join(EnquiryMasterSA,and_(ComputersEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.fk_company_id == int_company,\
                                                                EnquiryMasterSA.chr_doc_status == 'N')).join(AuthUserSA, ComputersFollowupSA.fk_user_id == AuthUserSA.id)
                if ins_permission and not ins_permission[0]['bln_add']:
                    rst_computers = rst_computers.filter(EnquiryMasterSA.fk_assigned_id==int_staff_id)




                rst_tablet = session.query(TabletFollowupSA.pk_bint_id.label("service_id"),TabletFollowupSA.dat_followup,TabletFollowupSA.vchr_enquiry_status,TabletFollowupSA.dbl_amount,TabletFollowupSA.vchr_notes,\
                                                                TabletFollowupSA.int_quantity,TabletFollowupSA.int_status,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.dat_created_at,\
                                                                literal("Tablet").label("vchr_service"),AuthUserSA.first_name,AuthUserSA.last_name)\
                                                                .filter(TabletFollowupSA.int_status == int_status)\
                                                                .join(TabletEnquirySA,TabletEnquirySA.pk_bint_id == TabletFollowupSA.fk_tablet_id)\
                                                                .join(EnquiryMasterSA,and_(TabletEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.fk_company_id == int_company,\
                                                                EnquiryMasterSA.chr_doc_status == 'N')).join(AuthUserSA, TabletFollowupSA.fk_user_id == AuthUserSA.id)

                if ins_permission and not ins_permission[0]['bln_add']:
                    rst_tablet = rst_tablet.filter(EnquiryMasterSA.fk_assigned_id==int_staff_id)




                rst_accessories = session.query(AccessoriesFollowupSA.pk_bint_id.label("service_id"),AccessoriesFollowupSA.dat_followup,AccessoriesFollowupSA.vchr_enquiry_status,AccessoriesFollowupSA.dbl_amount,AccessoriesFollowupSA.vchr_notes,\
                                                                AccessoriesFollowupSA.int_quantity,AccessoriesFollowupSA.int_status,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.dat_created_at,\
                                                                literal("Accessories").label("vchr_service"),AuthUserSA.first_name,AuthUserSA.last_name)\
                                                                .filter(AccessoriesFollowupSA.int_status == int_status)\
                                                                .join(AccessoriesEnquirySA,AccessoriesEnquirySA.pk_bint_id == AccessoriesFollowupSA.fk_accessories_id)\
                                                                .join(EnquiryMasterSA,and_(AccessoriesEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id,  EnquiryMasterSA.fk_company_id == int_company,\
                                                                EnquiryMasterSA.chr_doc_status == 'N')).join(AuthUserSA, AccessoriesFollowupSA.fk_user_id == AuthUserSA.id)

                if ins_permission and not ins_permission[0]['bln_add']:
                    rst_accessories = rst_accessories.filter(EnquiryMasterSA.fk_assigned_id==int_staff_id)

                rst_mobile = session.query(MobileFollowupSA.pk_bint_id.label("service_id"),MobileFollowupSA.dat_followup,MobileFollowupSA.vchr_enquiry_status,MobileFollowupSA.dbl_amount,MobileFollowupSA.vchr_notes,\
                                                                MobileFollowupSA.int_quantity,MobileFollowupSA.int_status,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.dat_created_at,\
                                                                literal("Mobile").label("vchr_service"),AuthUserSA.first_name,AuthUserSA.last_name)\
                                                                .filter(MobileFollowupSA.int_status == int_status)\
                                                                .join(MobileEnquirySA,MobileEnquirySA.pk_bint_id == MobileFollowupSA.fk_mobile_id)\
                                                                .join(EnquiryMasterSA,and_(MobileEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int_company,\
                                                                EnquiryMasterSA.chr_doc_status == 'N')).join(AuthUserSA, MobileFollowupSA.fk_user_id == AuthUserSA.id)


                if ins_permission and not ins_permission[0]['bln_add']:
                    rst_mobile = rst_mobile.filter(EnquiryMasterSA.fk_assigned_id==int_staff_id)



                rst_computers = rst_computers.all()
                rst_tablet = rst_tablet.all()
                rst_accessories = rst_accessories.all()
                rst_mobile = rst_mobile.all()

                rst_data += rst_computers
                rst_data += rst_tablet
                rst_data += rst_accessories
                rst_data += rst_mobile
                for dct_temp in rst_data:
                    lst_data.append(dct_temp._asdict())
                lst_newlist = sorted(lst_data, key=lambda k: k['dat_followup'], reverse=True)
                session.close()
                return Response({'status':'success','data':lst_newlist})
        except Exception as msg:
            session.close()
            return Response({'status':'failed','data':[str(msg)]})

class FollowupUpdate(APIView):
    def post(self,request):
        try:
            int_service_id = request.data.get('int_service_id')
            vchr_service = request.data.get('vchr_service')
            int_service_status = request.data.get('int_service_status')
            vchr_service_status = request.data.get('vchr_service_status')
            int_user_id = request.data.get('int_staff_id')
            int_amount = request.data.get('int_estimated_amount')
            int_quantity = request.data.get('int_quantity',0)
            str_enquiry_no = ''
            with transaction.atomic():
                if int_service_status == 1:
                    dat_updated_time = datetime.now()
                    fk_updated_by = int_user_id
                elif int_service_status == -1:
                    dat_updated_time = None
                    fk_updated_by = None
                if vchr_service == 'Computers':
                    computers_id = ComputersFollowup.objects.filter(pk_bint_id = int_service_id).values('fk_computers_id').first()['fk_computers_id']
                    if vchr_service_status == 'BOOKED' and not int_service_status==-1:
                        rst_enq = ComputersEnquiry.objects.get(pk_bint_id = computers_id)
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(int_quantity)).order_by('fk_stock_master__dat_added').first()
                        if ins_stock:
                            Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(int_quantity))
                        else:
                            return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(int_quantity)+' exceeds available stock quantity'})
                    ComputersFollowup.objects.filter(pk_bint_id = int_service_id).update(int_status = int_service_status,fk_updated_id = fk_updated_by,dat_updated = dat_updated_time,int_quantity = int_quantity)
                    if int_service_status==1:
                        ins_obj = ComputersEnquiry.objects.filter(pk_bint_id=computers_id)
                        ins_obj.update(vchr_enquiry_status=vchr_service_status,dbl_amount = int_amount,  vchr_remarks= request.data['vchr_remarks'],int_quantity=int_quantity)
                        str_enquiry_no = ComputersEnquiry.objects.get(pk_bint_id=computers_id).fk_enquiry_master.vchr_enquiry_num
                    if int_service_status==1 and vchr_service_status=='BOOKED':
                        ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                                dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = int_quantity)
                    if int_service_status==-1 and vchr_service_status=='BOOKED':
                        ComputersEnquiry.objects.filter(pk_bint_id=computers_id).update(dbl_imei_json = {'imei' : []})
                elif vchr_service == 'Tablet':
                    tablet_id = TabletFollowup.objects.filter(pk_bint_id = int_service_id).values('fk_tablet_id').first()['fk_tablet_id']
                    if vchr_service_status == 'BOOKED' and not int_service_status==-1:
                        rst_enq = TabletEnquiry.objects.get(pk_bint_id = tablet_id)
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(int_quantity)).order_by('fk_stock_master__dat_added').first()
                        if ins_stock:
                            Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(int_quantity))
                        else:
                            return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(int_quantity)+' exceeds available stock quantity'})
                    TabletFollowup.objects.filter(pk_bint_id = int_service_id).update(int_status = int_service_status,fk_updated_id = fk_updated_by,dat_updated = dat_updated_time,int_quantity = int_quantity)
                    if int_service_status==1:
                        ins_obj = TabletEnquiry.objects.filter(pk_bint_id=tablet_id)
                        ins_obj.update(vchr_enquiry_status=vchr_service_status,dbl_amount = int_amount,  vchr_remarks= request.data['vchr_remarks'],int_quantity=int_quantity)
                        str_enquiry_no = TabletEnquiry.objects.get(pk_bint_id=tablet_id).fk_enquiry_master.vchr_enquiry_num
                    if int_service_status==1 and vchr_service_status=='BOOKED':
                        ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                                dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = int_quantity)
                    if int_service_status==-1 and vchr_service_status=='BOOKED':
                        TabletEnquiry.objects.filter(pk_bint_id=computers_id).update(dbl_imei_json = {'imei' : []})
                elif vchr_service == 'Accessories':
                    accessories_id = AccessoriesFollowup.objects.filter(pk_bint_id = int_service_id).values('fk_accessories_id').first()['fk_accessories_id']
                    if vchr_service_status == 'BOOKED' and not int_service_status==-1:
                        rst_enq = AccessoriesEnquiry.objects.get(pk_bint_id = accessories_id)
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(int_quantity)).order_by('fk_stock_master__dat_added').first()
                        if ins_stock:
                            Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(int_quantity))
                        else:
                            return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(int_quantity)+' exceeds available stock quantity'})
                    AccessoriesFollowup.objects.filter(pk_bint_id = int_service_id).update(int_status = int_service_status,fk_updated_id = fk_updated_by,dat_updated = dat_updated_time,int_quantity = int_quantity)
                    if int_service_status==1:
                        ins_obj = AccessoriesEnquiry.objects.filter(pk_bint_id=accessories_id)
                        ins_obj.update(vchr_enquiry_status=vchr_service_status,dbl_amount = int_amount, vchr_remarks= request.data['vchr_remarks'],int_quantity=int_quantity)
                        str_enquiry_no = AccessoriesEnquiry.objects.get(pk_bint_id=accessories_id).fk_enquiry_master.vchr_enquiry_num
                    if int_service_status==1 and vchr_service_status=='BOOKED':
                        ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                                dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = int_quantity)
                    if int_service_status==-1 and vchr_service_status=='BOOKED':
                        AccessoriesEnquiry.objects.filter(pk_bint_id=computers_id).update(dbl_imei_json = {'imei' : []})
                elif vchr_service == 'Mobile':
                    mobile_id = MobileFollowup.objects.filter(pk_bint_id = int_service_id).values('fk_mobile_id').first()['fk_mobile_id']
                    if vchr_service_status == 'BOOKED' and not int_service_status==-1:
                        rst_enq = MobileEnquiry.objects.get(pk_bint_id = mobile_id)
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(int_quantity)).order_by('fk_stock_master__dat_added').first()
                        if ins_stock:
                            Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(int_quantity))
                        else:
                            return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(int_quantity)+' exceeds available stock quantity'})
                    MobileFollowup.objects.filter(pk_bint_id = int_service_id).update(int_status = int_service_status,fk_updated_id = fk_updated_by,dat_updated = dat_updated_time,int_quantity=int_quantity)
                    if int_service_status==1:
                        ins_obj=MobileEnquiry.objects.filter(pk_bint_id=mobile_id)
                        ins_obj.update(vchr_enquiry_status=vchr_service_status,dbl_amount = int_amount,vchr_remarks= request.data['vchr_remarks'],int_quantity=int_quantity)
                        str_enquiry_no = MobileEnquiry.objects.get(pk_bint_id=mobile_id).fk_enquiry_master.vchr_enquiry_num
                    if int_service_status==1 and vchr_service_status=='BOOKED':
                        ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                                dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = int_quantity)
                    if int_service_status==-1 and vchr_service_status=='BOOKED':
                        MobileEnquiry.objects.filter(pk_bint_id=computers_id).update(dbl_imei_json = {'imei' : []})
            if int_service_status == 1:
                ins_user = UserModel.objects.get(user_ptr_id = int_user_id)
                enquiry_print(str_enquiry_no,request,ins_user)
                return Response({'status':'success','operation':'Approve'})
            if int_service_status == -1:
                return Response({'status':'success','operation':'Reject'})
        except Exception as msg:
            return Response({'status':'1','data':[str(msg)]})
