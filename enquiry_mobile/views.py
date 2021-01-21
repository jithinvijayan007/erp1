
from invoice.models import PaymentDetails
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# Create your views here.
from django.shortcuts import render
from django.db.models import Q
import traceback
from django.contrib.auth.models import User
from POS import ins_logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from reminder.models import Reminder
# from sticky_notes.models import StickyNotes
from userdetails.models import UserDetails as UserModel
from enquiry.models import EnquiryMaster,Document,Offers
from customer.models import CustomerDetails as CustomerModel
from datetime import datetime,timedelta
from source.models import Source
from priority.models import Priority
from enquiry_mobile.models import ComputersFollowup,TabletFollowup,AccessoriesFollowup,MobileFollowup,EnquiryFinanceImages
from item_category.models import Item as Items
from brands.models import Brands
from products.models import Products
# from customer_rating.models import CustomerRating
# from hasher.views import hash_enquiry
from enquiry_print.views import enquiry_print
from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry
from branch.models import Branch
from stock_app.models import Stockmaster,Stockdetails
'''for alchemy'''
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import desc
from os.path import splitext
from os import path,makedirs
from django.db import transaction
from enquiry_mobile.models import Notification
from enquiry_mobile.models import GDPRange,MobileEnquiry, MobileFollowup, TabletEnquiry, TabletFollowup, ComputersEnquiry,ItemEnquiry,ItemFollowup, ComputersFollowup, AccessoriesEnquiry, AccessoriesFollowup
from django.db.models import Case,  Value, When,F
from django.db.models import Q
# from globalMethods import notifications_data

from django.db.models import IntegerField
from staff_rewards.models import RewardsDetails,RewardsAvailable ,RewardAssigned
from staff_rewards2.models import RewardsDetails2,RewardsAvailable2



from django.db.models import Count, Case, When, CharField, F

from groups.models import Groups
from buy_back.models import BuyBack

import requests
import json
# from django.conf import settings
from na_enquiry.models import NaEnquiryMaster,NaEnquiryDetails
from finance_enquiry.models import EnquiryFinance,FinanceCustomerDetails,FinanceSchema

from adminsettings.models import AdminSettings

from company.models import Company as CompanyDetails
# from .tasks import send_feedback_sms


def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

EnquiryMasterSA = EnquiryMaster.sa
CustomerSA = CustomerModel.sa
UserSA=UserModel.sa
AuthUserSA = User.sa
MobileEnquirySA = MobileEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
ComputersEnquirySA = ComputersEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
BranchSA = Branch.sa
BrandSA = Brands.sa
ProductsSA = Products.sa
ItemSA = Items.sa
ItemEnquirySA = ItemEnquiry.sa


class EnquiryInvoicedSave(APIView):
    permission_classes=[IsAuthenticated]
    """Estimated amount of purticular item"""
    def post(self,request):
        try:
            #CHECKS ADMIN SETTINGS TO KNOW WHETHER CURRENT USER GRANTS REWARDS TO COMPANY1 STAFF or COMPANY 2 staff.

                    dct_details = request.data.get('details')
                    ins_user = UserModel.objects.get(id = request.user.id)
                    lst_item_enquiry_new = []
                    # 
                    # ins_follow_up = ItemFollowup.objects.filter(vchr_enquiry_status = 'IMEI PENDING',fk_item_enquiry__vchr_enquiry_status='BOOKED',fk_item_enquiry__fk_enquiry_master_id=request.data['enquiry_id'])
                    # ins_follow_up.update(fk_item_enquiry__vchr_enquiry_status='IMG PENDING')
                    #
                    # ItemFollowup.objects.create(fk_item_enquiry = ins_follow_up,
                    #                             dat_followup = datetime.now(),
                    #                             fk_user = ins_user,
                    #                             vchr_notes = request.data.get('remark'),
                    #                             int_quantity = dct_details['int_quantity'],
                    #                             vchr_enquiry_status = 'IMG PENDING',
                    #                             dbl_amount = (dct_details['dbl_amount'] * dct_details['int_quantity']),
                    #                             fk_updated = ins_user,
                    #                             dat_updated = datetime.now())



                    lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master_id = request.data['enquiry_id'],vchr_enquiry_status='BOOKED').values_list('pk_bint_id',flat=True)
                    for key in dct_details.keys():
                        for dct_data in dct_details[key]:
                            if dct_data['lst_imei']['imei'] == {0:""}:
                                dct_data['lst_imei']['imei'] = []
                            elif  dct_data['lst_imei']['imei'] == {}:
                                dct_data['lst_imei']['imei'] = []
                            if not dct_data['dbl_gdp_amount'] and not dct_data['dbl_gdew_amount']:
                                int_type = 0
                            elif dct_data['dbl_gdp_amount'] and not dct_data['dbl_gdew_amount']:
                                int_type = 1
                            elif not dct_data['dbl_gdp_amount'] and dct_data['dbl_gdew_amount']:
                                int_type = 2
                            elif dct_data['dbl_gdp_amount'] and dct_data['dbl_gdew_amount']:
                                int_type = 3
                            dct_gdp_gdew={}
                            dbl_actual_est_amt = Items.objects.filter(id = dct_data['fk_item_id']).values('dbl_apx_amount').first()['dbl_apx_amount'] or 0
                            ins_gdp_gdew=GDPRange.objects.filter(dbl_from__lte=(dct_data['dbl_amount'] * dct_data['int_quantity']),dbl_to__gte=(dct_data['dbl_amount'] * dct_data['int_quantity'])).values_list('int_type','dbl_amt')
                            if ins_gdp_gdew:
                                dct_gdp_gdew={data[0]:data[1] for data in ins_gdp_gdew}

                            if 'item_id' in dct_data:
                                ins_item_enq = ItemEnquiry.objects.filter(pk_bint_id = dct_data['item_id'])
                                ins_item_enq.update(vchr_enquiry_status = 'INVOICED',dbl_buy_back_amount = dct_data['dbl_buy_back_amount'],dbl_discount_amount = dct_data['discount'],dbl_actual_est_amt = dbl_actual_est_amt,dbl_actual_gdp=dct_gdp_gdew.get(1),dbl_actual_gdew=dct_gdp_gdew.get(2))
                                ins_item_foll = ItemFollowup(fk_item_enquiry = ins_item_enq.first(),
                                                            dat_followup = datetime.now(),
                                                            fk_user = ins_user,
                                                            vchr_notes = request.data.get('remark'),
                                                            int_quantity = dct_data['int_quantity'],
                                                            vchr_enquiry_status = 'INVOICED',
                                                            dbl_amount = (dct_data['dbl_amount'] * dct_data['int_quantity']),
                                                            fk_updated = ins_user,
                                                            dat_updated = datetime.now())
                                ins_item_foll.save()
                                item_enquiry_id = ins_item_enq.values('pk_bint_id').first()['pk_bint_id']
                                lst_item_enquiry_new.append(item_enquiry_id)
                            else:
                                ins_item_enq = ItemEnquiry(
                                                            fk_enquiry_master_id = request.data.get('enquiry_id'),
                                                            fk_product_id = dct_data['fk_product_id'],
                                                            fk_brand_id = dct_data['fk_brand_id'],
                                                            fk_item_id = dct_data['fk_item_id'],
                                                            int_quantity = dct_data['int_quantity'],
                                                            dbl_amount = (dct_data['dbl_amount'] * dct_data['int_quantity']),
                                                            vchr_enquiry_status = 'INVOICED',
                                                            int_sold = dct_data['int_quantity'],
                                                            dbl_imei_json = dct_data['lst_imei'],
                                                            dbl_buy_back_amount = dct_data['dbl_buy_back_amount'],
                                                            dbl_discount_amount = dct_data['discount'],
                                                            dbl_gdp_amount = dct_data['dbl_gdp_amount'],
                                                            dbl_gdew_amount = dct_data['dbl_gdew_amount'],
                                                            int_type = int_type,
                                                            dbl_actual_est_amt = dbl_actual_est_amt,
                                                            dbl_actual_gdp=dct_gdp_gdew.get(1),
                                                            dbl_actual_gdew=dct_gdp_gdew.get(2)
                                                           )
                                ins_item_enq.save()
                                item_enquiry_id = ins_item_enq.pk_bint_id
                                lst_item_enquiry_new.append(item_enquiry_id)
                                ins_item_foll = ItemFollowup(fk_item_enquiry = ins_item_enq,
                                                            dat_followup = datetime.now(),
                                                            fk_user = ins_user,
                                                            vchr_notes = request.data.get('remark'),
                                                            int_quantity = dct_data['int_quantity'],
                                                            vchr_enquiry_status = 'INVOICED',
                                                            dbl_amount = (dct_data['dbl_amount'] * dct_data['int_quantity']),
                                                            fk_updated = ins_user,
                                                            dat_updated = datetime.now())
                                ins_item_foll.save()
                    EnquiryMaster.objects.filter(pk_bint_id=int(request.data.get('enquiry_id'))).update(dat_created_at=datetime.now(),vchr_remarks = request.data.get('remark'))

                    lost_item_enquiry = list(set(lst_item_enquiry_all)-set(lst_item_enquiry_new))
                    if len(lost_item_enquiry):
                        ItemEnquiry.objects.filter(pk_bint_id__in = lost_item_enquiry).update(vchr_enquiry_status='CONVERTED')

                    # ====================================================================================================================
                    # 
                    # lst_item_enq_id = ItemFollowup.objects.filter(vchr_enquiry_status = 'IMEI PENDING',fk_item_enquiry__vchr_enquiry_status='INVOICED',fk_item_enquiry__fk_enquiry_master_id=request.data['enquiry_id']).values_list('fk_item_enquiry_id',flat=True)
                    # ItemEnquiry.objects.filter(pk_bint_id__in=lst_item_enq_id).update(vchr_enquiry_status='IMAGE PENDING')
                    # ItemFollowup.objects.filter(fk_item_enquiry_id__in=lst_item_enq_id,vchr_enquiry_status='INVOICED').update(vchr_enquiry_status='IMAGE PENDING')

                    # ----------------------------------------------
                    ins_data  = ItemFollowup.objects.filter(vchr_enquiry_status = 'IMEI PENDING',fk_item_enquiry__fk_enquiry_master_id = request.data['enquiry_id'])
                    # 
                    if ins_data:
                        ItemEnquiry.objects.filter(fk_enquiry_master=request.data['enquiry_id'],vchr_enquiry_status='INVOICED').update(vchr_enquiry_status='IMAGE PENDING')
                        ItemFollowup.objects.filter(fk_item_enquiry_id__fk_enquiry_master=request.data['enquiry_id'],fk_item_enquiry_id__vchr_enquiry_status='IMAGE PENDING',vchr_enquiry_status='INVOICED').update(vchr_enquiry_status='IMAGE PENDING')

                        # NOTIFICATION IMAGE PENDING
                        ins_assigned = ItemEnquiry.objects.filter(fk_enquiry_master=request.data['enquiry_id']).values('fk_enquiry_master_id__fk_assigned_id').first()
                        int_assigned = ins_assigned['fk_enquiry_master_id__fk_assigned_id']
                        count_image_pending = ItemEnquiry.objects.filter(fk_enquiry_master=request.data['enquiry_id'],vchr_enquiry_status='INVOICED').count()
                        ins_rem = Reminder.objects.filter(fk_user = int_assigned, vchr_description__icontains = '(IMAGE PENDING)')
                        count_old = ItemEnquiry.objects.filter(fk_enquiry_master_id__fk_assigned_id = int_assigned,vchr_enquiry_status = 'IMAGE PENDING').values('fk_enquiry_master_id__fk_assigned_id').count()
                        actual_count = count_old
                        if actual_count > 1:
                            str_notification = str(actual_count) + ' enquiries need to be updated with proper images(IMAGE PENDING)'

                        elif actual_count == 1:
                            str_notification = str(actual_count) + ' enquiry needs to be updated with proper images(IMAGE PENDING)'

                        if actual_count != 0:
                            ins_reminder = Reminder.objects.create(fk_user_id        = int_assigned,
                                                                    dat_created_at   = datetime.now(),
                                                                    dat_updated_at   = datetime.now(),
                                                                    vchr_title       = 'IMAGE PENDING ENQUIRY',
                                                                    vchr_description = str_notification,
                                                                    dat_reminder     = datetime.now()
                                                                    )
                        # NOTIFICATION END
                    # ins_item_foll = ItemFollowup(fk_item_enquiry = ins_follow_up,
                    #                             dat_followup = datetime.now(),
                    #                             fk_user = ins_user,
                    #                             vchr_notes = request.data.get('remark'),
                    #                             int_quantity = dct_data['int_quantity'],
                    #                             vchr_enquiry_status = 'IMAGE PENDING',
                    #                             dbl_amount = (dct_data['dbl_amount'] * dct_data['int_quantity']),
                    #                             fk_updated = ins_user,
                    #                             dat_updated = datetime.now())
                    # ins_item_foll.save()


                    # ====================================================================================================================


                    lst_company=list(AdminSettings.objects.filter(fk_company_id=request.user.userdetails.fk_company_id,bln_enabled=True,vchr_name__icontains="REWARDS").values_list('vchr_name',flat=True))
                    if lst_company:
                            if lst_company[0]=="REWARDS2":
                                        json_staff={}

                            ############################## incentives handling #################
                                        # 
                                        lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master_id = request.data['enquiry_id'],vchr_enquiry_status='INVOICED').values('pk_bint_id','fk_item_id','fk_item__fk_product_id','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_discount_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew')
                                        int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],is_active=True).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()
                                        lst_available=[int_promoter['promo'],1]
                                        if not UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF',is_active=True).values():
                                            lst_available.pop(0)
                                        product_total_qty={}
                                        item_amount={}


                                        # int_total_gdp_count=0
                                        # gdp_details={}
                                        # int_total_gdew_count=0
                                        # gdew_details={}
                                        for data in lst_item_enquiry_all:
                                            lst_available=[]
                                            if not int_promoter['fk_brand_id']:
                                                lst_available=[3,1]
                                            elif data['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                                                lst_available=[3,1]
                                            elif int_promoter['fk_brand_id']==data['fk_item__fk_brand_id']:
                                                lst_available=[2,1]
                                        #     if data['int_type']=1:
                                        #         int_total_gdp_count+=1
                                        #         gdp_details[data['pk_bint_id']]=data['dbl_gdp_amount']
                                        #     if data['int_type']=2:
                                        #         int_total_gdew_count+=1
                                        #         gdew_details[data['pk_bint_id']]=data['dbl_gdew_amount']
                                        #     if data['int_type']=3:
                                        #         int_total_gdp_count+=1
                                        #         int_total_gdew_count+=1
                                        #         gdp_details[data['pk_bint_id']]=data['dbl_gdp_amount']
                                        #         gdew_details[data['pk_bint_id']]=data['dbl_gdew_amount']

                                            total_reward=0
                                            item_amount['dbl_apx_amount']=0
                                            item_data=RewardsDetails2.objects.filter(int_to__in=lst_available,int_quantity_from__lte=data['int_sold'],int_quantity_to__gte=data['int_sold'],fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,int_map_type=0,int_map_id=data['fk_item__fk_product_id'],fk_rewards_master__dat_from__lte=datetime.now().date(),fk_rewards_master__dat_to__gte=datetime.now().date(),fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_rewards_master_id','int_quantity_from','int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','int_mop_sale').order_by('int_quantity_to').first()
                                            if item_data:
                                                if item_data and item_data['int_mop_sale']==1:
                                                    item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                    if not item_amount['dbl_apx_amount']:
                                                        pass
                                                    elif item_amount['dbl_apx_amount']>(data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold']:
                                                        pass
                                                    else:
                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_percentage']:
                                                            reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount']
                                                        total_reward+=reward*data['int_sold']
                                                elif item_data:
                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                        reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                    elif item_data['dbl_slab1_percentage']:
                                                        reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                    elif item_data['dbl_slab1_amount']:
                                                        reward=item_data['dbl_slab1_amount']
                                                    total_reward+=reward*data['int_sold']
                                                # else:
                                                #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                #         product_total_qty[data['fk_item__fk_product_id']]+=data['int_sold']
                                                #     else:
                                                #         product_total_qty[data['fk_item__fk_product_id']]=data['int_sold']

                                                #EXPLANATION : JSON HAS KEY SHOWED AN ERROR THEREFORE THE FOLLOWING CODE IS USED,
                                                # FIRST RewardsAvailable2 IS CALLED AND THEN CHECKED IF EXIST IT DOESNT EXIST NEW FIELD IS CREATED, IF IT DOES BUT JSON staff
                                                # DOESNT HAVE THE SAME KEY THEN ALSO AN OBJECT IS CREATED
                                                if total_reward:
                                                    lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id']).values('json_staff')
                                                    if not lst_json1:
                                                                json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                    elif data['fk_enquiry_master__fk_assigned_id'] not in lst_json1.first()['json_staff']:
                                                                json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}

                                                    if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()):
                                                            fk_user=UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']

                                                            if not lst_json1:
                                                                if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                            elif UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                    ins_user=UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first())
                                                    if ins_user:
                                                        if not lst_json1:
                                                            json_staff.update({str(UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                        elif UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                            json_staff.update({str(UserModel.objects.filter(fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})

                                                    if json_staff:
                                                            ins_item_reward=RewardsAvailable2(json_staff=json_staff,fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                                                            ins_item_reward.save()

                                            # 
                                            item_data=RewardsDetails2.objects.filter(int_to__in=lst_available,int_quantity_from__lte=data['int_sold'],int_quantity_to__gte=data['int_sold'],fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,int_map_type=2,int_map_id=data['fk_item_id'],fk_rewards_master__dat_from__lte=datetime.now().date(),fk_rewards_master__dat_to__gte=datetime.now().date(),fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_rewards_master_id','int_quantity_from','int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','int_mop_sale').order_by('int_quantity_to').first()
                                            total_reward=0
                                            if item_data:
                                                if item_data and item_data['int_mop_sale']==1:
                                                    item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                    if not item_amount['dbl_apx_amount']:
                                                        pass
                                                    elif item_amount['dbl_apx_amount']>(data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold']:
                                                        pass
                                                    else:
                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_percentage']:
                                                            reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount']
                                                        total_reward+=reward*data['int_sold']
                                                elif item_data:
                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                        reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                    elif item_data['dbl_slab1_percentage']:
                                                        reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                    elif item_data['dbl_slab1_amount']:
                                                        reward=item_data['dbl_slab1_amount']
                                                    total_reward+=reward*data['int_sold']
                                                # else:
                                                #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                #     else:
                                                #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                if total_reward:
                                                    lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id']).values('json_staff')
                                                    if not lst_json1:
                                                        json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                    elif data['fk_enquiry_master__fk_assigned_id'] not in lst_json1.first()['json_staff']:
                                                        json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                    if UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first(),is_active=True):
                                                        fk_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']
                                                        if not lst_json1:
                                                            if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                            else:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                        elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                            if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                            else:

                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                    ins_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first())
                                                    if ins_user:
                                                        if not lst_json1:
                                                            json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                        elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                            json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                    if json_staff:
                                                            ins_item_reward=RewardsAvailable2(json_staff=json_staff,fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'] if item_amount['dbl_apx_amount'] else 0,dat_reward=datetime.now())
                                                            ins_item_reward.save()
                                            ############GDP
                                            if data['int_type'] in [1,3]:
                                                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']
                                                item_data=RewardsDetails2.objects.filter(int_to__in=lst_available,fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,int_map_type=0,int_map_id=int_gdp,fk_rewards_master__dat_from__lte=datetime.now().date(),fk_rewards_master__dat_to__gte=datetime.now().date(),fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_rewards_master_id','int_quantity_from','int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','int_mop_sale').order_by('int_quantity_to').first()
                                                total_reward=0
                                                if item_data:
                                                    if item_data and item_data['int_mop_sale']==1:
                                                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                        if not data['dbl_actual_gdp'] :
                                                            pass
                                                        elif data['dbl_actual_gdp']>data['dbl_gdp_amount']:
                                                            pass
                                                        else:
                                                            if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount'] if data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_percentage']:
                                                                reward=data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount']
                                                            total_reward+=reward
                                                    elif item_data:
                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount'] if data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_percentage']:
                                                            reward=data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount']
                                                        total_reward+=reward
                                                    # else:
                                                    #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                    #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                    #     else:
                                                    #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                    if total_reward:
                                                        lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id']).values('json_staff')
                                                        if not lst_json1:
                                                            json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                        elif data['fk_enquiry_master__fk_assigned_id'] not in lst_json1.first()['json_staff']:
                                                            json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}

                                                        if UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()):
                                                            fk_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']
                                                            if not lst_json1:
                                                                if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                        json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                        json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:

                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})

                                                        ins_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first())
                                                        if ins_user:
                                                            if not lst_json1:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})

                                                        if json_staff:
                                                            ins_item_reward=RewardsAvailable2(json_staff=json_staff,fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=datetime.now())
                                                            ins_item_reward.save()
                                            ############ GDEW
                                            if data['int_type'] in [2,3]:
                                                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                                                item_data=RewardsDetails2.objects.filter(int_to__in=lst_available,fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,int_map_type=0,int_map_id=int_gdew,fk_rewards_master__dat_from__lte=datetime.now().date(),fk_rewards_master__dat_to__gte=datetime.now().date(),fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_rewards_master_id','int_quantity_from','int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','int_mop_sale').order_by('int_quantity_to').first()
                                                total_reward=0
                                                if item_data:
                                                    if item_data and item_data['int_mop_sale']==1:
                                                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                        if not data['dbl_actual_gdew'] :
                                                            pass
                                                        elif data['dbl_actual_gdew']>data['dbl_gdew_amount']:
                                                            pass
                                                        else:
                                                            if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount'] if data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_percentage']:
                                                                reward=data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount']
                                                            total_reward+=reward
                                                    elif item_data:
                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount'] if data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_percentage']:
                                                            reward=data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount']
                                                        total_reward+=reward
                                                    # else:
                                                    #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                    #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                    #     else:
                                                    #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                    if total_reward:
                                                        lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id']).values('json_staff')
                                                        if not lst_json1:
                                                            json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                        elif data['fk_enquiry_master__fk_assigned_id'] not in lst_json1.first()['json_staff']:
                                                            json_staff={str(data['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}

                                                        if UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()):
                                                            fk_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']
                                                            if not lst_json1:
                                                                if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                if fk_user==data['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                        ins_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first())
                                                        if ins_user:
                                                            lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id']).values('json_staff')
                                                            if not lst_json1:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']  not in lst_json1.first()['json_staff']:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']['user_ptr_id']):((total_reward/100)*20)/100*40})



                                                        if json_staff:
                                                            ins_item_reward=RewardsAvailable2(json_staff=json_staff,fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=datetime.now())

                                                            ins_item_reward.save()



                                        return Response({'status':'success'})
                            if lst_company[0]=="REWARDS1":

                                                    ############################## incentives handling #################
                                                    # 
                                                    lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master_id = request.data['enquiry_id'],vchr_enquiry_status='INVOICED').values('pk_bint_id','fk_item_id','fk_item__fk_product_id','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_discount_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew')
                                                    if not lst_item_enquiry_all:
                                                        return JsonResponse({'status':'success'})
                                                    int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],is_active=True).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()
                                                    lst_available=[int_promoter['promo'],1]
                                                    if not UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF',is_active=True).values():
                                                        lst_available.pop(0)
                                                    product_total_qty={}
                                                    item_amount={}


                                                    # int_total_gdp_count=0
                                                    # gdp_details={}
                                                    # int_total_gdew_count=0
                                                    # gdew_details={}
                                                    for data in lst_item_enquiry_all:
                                                        lst_available=[]
                                                        if not int_promoter['fk_brand_id']:
                                                            lst_available=[3,1]
                                                        elif data['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                                                            lst_available=[3,1]
                                                        elif int_promoter['fk_brand_id']==data['fk_item__fk_brand_id']:
                                                            lst_available=[2,1]
                                                    #     if data['int_type']=1:
                                                    #         int_total_gdp_count+=1
                                                    #         gdp_details[data['pk_bint_id']]=data['dbl_gdp_amount']
                                                    #     if data['int_type']=2:
                                                    #         int_total_gdew_count+=1
                                                    #         gdew_details[data['pk_bint_id']]=data['dbl_gdew_amount']
                                                    #     if data['int_type']=3:
                                                    #         int_total_gdp_count+=1
                                                    #         int_total_gdew_count+=1
                                                    #         gdp_details[data['pk_bint_id']]=data['dbl_gdp_amount']
                                                    #         gdew_details[data['pk_bint_id']]=data['dbl_gdew_amount']

                                                        total_reward=0
                                                        item_data=RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__int_quantity_from__lte=data['int_sold'],fk_reward_details__int_quantity_to__gte=data['int_sold'],fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to',"-pk_bint_id").first()
                                                        if item_data:
                                                            if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                                                item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                                if not item_amount['dbl_apx_amount'] :
                                                                    pass
                                                                elif item_amount['dbl_apx_amount']>(data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold']:
                                                                    pass
                                                                else:
                                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_percentage']:
                                                                        reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount']
                                                                    total_reward+=reward*data['int_sold']
                                                            elif item_data:
                                                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                    reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                elif item_data['dbl_slab1_percentage']:
                                                                    reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                elif item_data['dbl_slab1_amount']:
                                                                    reward=item_data['dbl_slab1_amount']
                                                                total_reward+=reward*data['int_sold']
                                                            # else:
                                                            #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                            #         product_total_qty[data['fk_item__fk_product_id']]+=data['int_sold']
                                                            #     else:
                                                            #         product_total_qty[data['fk_item__fk_product_id']]=data['int_sold']
                                                            if total_reward:
                                                                if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                                                    lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))
                                                                    json_staffs = {}
                                                                    for dct_assign in lst_reawards_assigned:
                                                                        int_assign_id = EnquiryMaster.objects.filter(pk_bint_id=request.data['enquiry_id']).values('fk_assigned_id').first()['fk_assigned_id']
                                                                        str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                                                        if dct_assign['dbl_slab1_amount'] and dct_assign['dbl_slab1_percentage']:
                                                                            int_reward = dct_assign['dbl_slab1_amount'] if dct_assign['dbl_slab1_amount']<data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage'] else data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        elif dct_assign['dbl_slab1_amount']:
                                                                            int_reward=dct_assign['dbl_slab1_amount']

                                                                        elif dct_assign['dbl_slab1_percentage']:
                                                                            int_reward=data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        int_reward= int_reward*data['int_sold']
                                                                        if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':


                                                                            if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                                                json_staffs[int_assign_id]= int_reward
                                                                            elif dct_assign['int_to'] == 1:

                                                                                json_staffs[int_assign_id] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                    if json_staffs:
                                                                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                                                                        ins_item_reward.save()
                                                        # 
                                                        item_data = RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0,fk_reward_details__int_quantity_from__lte=data['int_sold'],fk_reward_details__int_quantity_to__gte=data['int_sold'],fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=1,fk_reward_details__int_map_id=data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(request.user.userdetails.fk_branch_id)]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to',"-pk_bint_id").first()


                                                        total_reward=0
                                                        if item_data:
                                                            if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                                                item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                                if not item_amount['dbl_apx_amount'] :
                                                                    pass
                                                                elif item_amount['dbl_apx_amount']>(data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold']:
                                                                    pass
                                                                else:
                                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_percentage']:
                                                                        reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount']
                                                                    total_reward+=reward*data['int_sold']
                                                            elif item_data:
                                                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                    reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                elif item_data['dbl_slab1_percentage']:
                                                                    reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                elif item_data['dbl_slab1_amount']:
                                                                    reward=item_data['dbl_slab1_amount']
                                                                total_reward+=reward*data['int_sold']
                                                            # else:
                                                            #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                            #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                            #     else:
                                                            #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                            if total_reward:
                                                                if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                                                    lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))

                                                                    json_staffs = {}
                                                                    for dct_assign in lst_reawards_assigned:
                                                                        int_assign_id = EnquiryMaster.objects.filter(pk_bint_id=request.data['enquiry_id']).values('fk_assigned_id').first()['fk_assigned_id']
                                                                        str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                                                        if dct_assign['dbl_slab1_amount'] and dct_assign['dbl_slab1_percentage']:
                                                                            int_reward = dct_assign['dbl_slab1_amount'] if dct_assign['dbl_slab1_amount']<data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage'] else data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        elif dct_assign['dbl_slab1_amount']:
                                                                            int_reward=dct_assign['dbl_slab1_amount']

                                                                        elif dct_assign['dbl_slab1_percentage']:
                                                                            int_reward=data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        int_reward= int_reward*data['int_sold']

                                                                        if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':

                                                                            if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                                                json_staffs[int_assign_id]= int_reward
                                                                            elif dct_assign['int_to'] == 1:

                                                                                json_staffs[int_assign_id] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                    if json_staffs:
                                                                        ins_item_reward=RewardsAvailable(json_staff = json_staffs, fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'], fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                                                                        ins_item_reward.save()
                                                        # import pdb;
                                                        # pdb.set_trace()
                                                        item_data = RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__int_quantity_from__lte=data['int_sold'], fk_reward_details__int_quantity_to__gte= data['int_sold'],fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=2,fk_reward_details__int_map_id=data['fk_item_id'],fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(request.user.userdetails.fk_branch_id)]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to',"-pk_bint_id").first()

                                                        total_reward=0
                                                        if item_data:
                                                            if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                                                item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                                if not item_amount['dbl_apx_amount'] :
                                                                    pass
                                                                elif item_amount['dbl_apx_amount']>(data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold']:
                                                                    pass
                                                                else:
                                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_percentage']:
                                                                        reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount']
                                                                    total_reward+=reward*data['int_sold']
                                                            elif item_data:
                                                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                    reward=item_data['dbl_slab1_amount'] if ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else ((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                elif item_data['dbl_slab1_percentage']:
                                                                    reward=((data['dbl_amount']-data['dbl_discount_amount'])/data['int_sold'])/100*item_data['dbl_slab1_percentage']
                                                                elif item_data['dbl_slab1_amount']:
                                                                    reward=item_data['dbl_slab1_amount']
                                                                total_reward+=reward*data['int_sold']

                                                            if total_reward:
                                                                if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                                                    lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))

                                                                    json_staffs = {}
                                                                    for dct_assign in lst_reawards_assigned:

                                                                        int_assign_id = EnquiryMaster.objects.filter(pk_bint_id=request.data['enquiry_id']).values('fk_assigned_id').first()['fk_assigned_id']
                                                                        str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                                                        if dct_assign['dbl_slab1_amount'] and dct_assign['dbl_slab1_percentage']:
                                                                            int_reward = dct_assign['dbl_slab1_amount'] if dct_assign['dbl_slab1_amount']<data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage'] else data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        elif dct_assign['dbl_slab1_amount']:
                                                                            int_reward=dct_assign['dbl_slab1_amount']

                                                                        elif dct_assign['dbl_slab1_percentage']:
                                                                            int_reward=data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        int_reward= int_reward*data['int_sold']

                                                                        if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':

                                                                            if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                                                json_staffs[int_assign_id]= int_reward
                                                                            elif dct_assign['int_to'] == 1:

                                                                                json_staffs[int_assign_id] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward

                                                                    ins_item_reward=RewardsAvailable(json_staff = json_staffs, fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'], fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                                                                    ins_item_reward.save()

                                                        ############GDP
                                                        # import pdb;
                                                        # pdb.set_trace()
                                                        if data['int_type'] in [1,3]:
                                                            int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']

                                                            item_data=RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0,  fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id =request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=int_gdp,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                                                            'fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to','fk_reward_details',"-pk_bint_id").first()

                                                            total_reward=0
                                                            if item_data:
                                                                if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                                                    # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                                    if not data['dbl_actual_gdp'] :
                                                                        pass
                                                                    elif data['dbl_actual_gdp']>data['dbl_gdp_amount']:
                                                                        pass
                                                                    else:
                                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                            reward=item_data['dbl_slab1_amount'] if data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                                        elif item_data['dbl_slab1_percentage']:
                                                                            reward=data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                                        elif item_data['dbl_slab1_amount']:
                                                                            reward=item_data['dbl_slab1_amount']
                                                                        total_reward+=reward
                                                                elif item_data:
                                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount'] if data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_percentage']:
                                                                        reward=data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount']
                                                                    total_reward+=reward
                                                                # else:
                                                                #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                                #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                                #     else:
                                                                #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                                if total_reward:
                                                                    if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                                                        lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))

                                                                        json_staffs = {}
                                                                        for dct_assign in lst_reawards_assigned:

                                                                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id=request.data['enquiry_id']).values('fk_assigned_id').first()['fk_assigned_id']
                                                                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                                                        if dct_assign['dbl_slab1_amount'] and dct_assign['dbl_slab1_percentage']:
                                                                            int_reward = dct_assign['dbl_slab1_amount'] if dct_assign['dbl_slab1_amount']<data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage'] else data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        elif dct_assign['dbl_slab1_amount']:
                                                                            int_reward=dct_assign['dbl_slab1_amount']

                                                                        elif dct_assign['dbl_slab1_percentage']:
                                                                            int_reward=data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                        int_reward= int_reward*data['int_sold']

                                                                        if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                                                            int_reward = dct_assign['dbl_slab1_amount'] if dct_assign['dbl_slab1_amount']<data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage'] else data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                            int_reward= int_reward*data['int_sold']

                                                                            if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                                                json_staffs[int_assign_id]= int_reward
                                                                            elif dct_assign['int_to'] == 1:

                                                                                json_staffs[int_assign_id] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                                                                json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                        elif dct_assign['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                                                            if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward

                                                                        ins_item_reward=RewardsAvailable(json_staff=json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                                                                        ins_item_reward.save()

                                                        ############ GDEW
                                                        if data['int_type'] in [2,3]:
                                                            int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                                                            item_data=RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=int_gdew,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(request.user.userdetails.fk_branch_id)]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to',"-pk_bint_id").first()

                                                            total_reward=0
                                                            if item_data:
                                                                if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                                                    # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                                    if not data['dbl_actual_gdew'] :
                                                                        pass
                                                                    elif data['dbl_actual_gdew']>data['dbl_gdew_amount']:
                                                                        pass
                                                                    else:
                                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                            reward=item_data['dbl_slab1_amount'] if data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                                        elif item_data['dbl_slab1_percentage']:
                                                                            reward=data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                                        elif item_data['dbl_slab1_amount']:
                                                                            reward=item_data['dbl_slab1_amount']
                                                                        total_reward+=reward
                                                                elif item_data:
                                                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount'] if data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_percentage']:
                                                                        reward=data['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                                    elif item_data['dbl_slab1_amount']:
                                                                        reward=item_data['dbl_slab1_amount']
                                                                    total_reward+=reward
                                                                # else:
                                                                #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                                #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                                #     else:
                                                                #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                                if total_reward:
                                                                    if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():
                                                                        lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))

                                                                        json_staffs = {}
                                                                        for dct_assign in lst_reawards_assigned:

                                                                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id=request.data['enquiry_id']).values('fk_assigned_id').first()['fk_assigned_id']
                                                                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                                                            if dct_assign['dbl_slab1_amount'] and dct_assign['dbl_slab1_percentage']:
                                                                                int_reward = dct_assign['dbl_slab1_amount'] if dct_assign['dbl_slab1_amount']<data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage'] else data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                            elif dct_assign['dbl_slab1_amount']:
                                                                                int_reward=dct_assign['dbl_slab1_amount']

                                                                            elif dct_assign['dbl_slab1_percentage']:
                                                                                int_reward=data['dbl_amount']/(data['int_sold']*100)*dct_assign['dbl_slab1_percentage']
                                                                            int_reward= int_reward*data['int_sold']

                                                                            if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':

                                                                                if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                                                    json_staffs[int_assign_id]= int_reward
                                                                                elif dct_assign['int_to'] == 1:

                                                                                    json_staffs[int_assign_id] = int_reward
                                                                            elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                            elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward
                                                                            elif dct_assign['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                                                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):

                                                                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = int_reward

                                                                            ins_item_reward=RewardsAvailable(json_staff=json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                                                                            ins_item_reward.save()
                            # add_reward = value_based_staff_rewards(request)
                            add_reward = special_rewards(request.data['enquiry_id'])

                            return Response({'status':'success'})

                    else:
                        return Response({'status':'success'})

        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return JsonResponse({'status':'failed'})


def value_based_staff_rewards(request):
    try:
        enquiry_num = EnquiryMaster.objects.get(pk_bint_id=request.data['enquiry_id']).vchr_enquiry_num
        lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master__vchr_enquiry_num = enquiry_num,vchr_enquiry_status='INVOICED').\
        values('pk_bint_id','fk_item_id','fk_item__fk_product_id','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_discount_amount',\
        'dbl_buy_back_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew')

        if not lst_item_enquiry_all:
            return JsonResponse({'status':'success'})

        int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],is_active=True).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()

        lst_available=[int_promoter['promo'],1]
        if not UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF',is_active=True).values():
            lst_available.pop(0)


        product_total_qty={}
        item_amount={}


        for data in lst_item_enquiry_all:

            lst_available=[]
            if not int_promoter['fk_brand_id']:
                lst_available=[3,1]
            elif data['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                lst_available=[3,1]
            elif int_promoter['fk_brand_id']==data['fk_item__fk_brand_id']:
                lst_available=[2,1]

            """map type product"""
            total_reward=0
            item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not item_amount['dbl_apx_amount'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(vchr_enquiry_num = enquiry_num).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                            if item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward


                if json_staffs:
                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """map type brand"""
            total_reward=0
            item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 6,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not item_amount['dbl_apx_amount'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(vchr_enquiry_num = enquiry_num).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                            if item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward



                if json_staffs:
                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """map type item"""
            total_reward=0
            item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 7,fk_reward_details__int_map_id = data['fk_item_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not item_amount['dbl_apx_amount'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100 * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = ((data['dbl_amount'] - data['dbl_buy_back_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100 * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(vchr_enquiry_num = enquiry_num).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                            if item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward




                if json_staffs:
                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """GDP"""

            if data['int_type'] in [1,3]:
                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']


                total_reward=0
                item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdp'] :
                                pass
                            elif data['dbl_actual_gdp']>data['dbl_gdp_amount']:
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= ((data['dbl_gdp_amount']) / data['int_sold']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if ((data['dbl_gdp_amount'])/data['int_sold']) / 100 * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else ((data['dbl_gdp_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = ((data['dbl_gdp_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= ((data['dbl_gdp_amount']) / data['int_sold']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if ((data['dbl_gdp_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else ((data['dbl_gdp_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = ((data['dbl_gdp_amount']) / data['int_sold']) / 100 * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= ((data['dbl_gdp_amount']) / data['int_sold']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if ((data['dbl_gdp_amount'])/data['int_sold']) / 100 * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else ((data['dbl_gdp_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = ((data['dbl_gdp_amount']) / data['int_sold']) / 100 * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(vchr_enquiry_num = enquiry_num).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                                if item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward



                    if json_staffs:
                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                        ins_item_reward.save()


            """GDEW"""
            if data['int_type'] in [2,3]:
                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']

                total_reward=0
                item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdew'] :
                                pass
                            elif data['dbl_actual_gdew']>data['dbl_gdew_amount']:
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= ((data['dbl_gdew_amount']) / data['int_sold']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if ((data['dbl_gdew_amount'])/data['int_sold']) / 100 * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else ((data['dbl_gdew_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = ((data['dbl_gdew_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= ((data['dbl_gdew_amount']) / data['int_sold']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if ((data['dbl_gdew_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else ((data['dbl_gdew_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = ((data['dbl_gdew_amount']) / data['int_sold']) / 100 * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= ((data['dbl_gdew_amount']) / data['int_sold']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if ((data['dbl_gdew_amount'])/data['int_sold']) / 100 * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else ((data['dbl_gdew_amount']) / data['int_sold'] ) / 100 * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = ((data['dbl_gdew_amount']) / data['int_sold']) / 100 * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(vchr_enquiry_num = enquiry_num).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                                if item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward



                    if json_staffs:
                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=item_amount['dbl_apx_amount'],dat_reward=datetime.now())
                        ins_item_reward.save()


        return "Success"
    except Exception as e:
        data = str(e)
        return data



class getProductPrice(APIView):
    permission_classes=[IsAuthenticated]
    """Estimated amount and mrp of a purticular item"""
    def post(self,request):
        try:
            # 
            int_id = request.data.get('itemId')
            flt_amount = 0
            if int_id:
                rst_data = Items.objects.filter(pk_bint_id = int_id).annotate(dbl_mrp_price = F('dbl_mrp'),dbl_apx_amount = F('dbl_mop')).values('dbl_apx_amount','dbl_mrp_price').first()
                str_item_code = Items.objects.filter(pk_bint_id = int_id).values('vchr_item_code')[0]['vchr_item_code']


                dat_today = datetime.strftime(datetime.now(),'%Y-%m-%d')
                int_buyback_amount = BuyBack.objects.filter(fk_item_id = int_id,int_status=1,dat_end__gte = dat_today, dat_start__lte = dat_today).values('dbl_amount')
                if int_buyback_amount:
                    int_buyback_amount = int_buyback_amount[0]['dbl_amount']
                else:
                    int_buyback_amount = 0
                if rst_data:
                    return JsonResponse({'status':'success', 'item_amount_per_qty':rst_data['dbl_apx_amount'], 'int_buyback_amount' :int_buyback_amount, 'mrp':rst_data['dbl_mrp_price'] })
                # url and passing parameter for getting the item price
                # url = 'http://devserv1.gdpplus.in/Item_Model_Selling_Price.aspx'
                # params = {'model':str_item_code}
                # r = requests.get(url, params=params)

                # if r.status_code == 200:
                #     data = json.dumps(r.text)
                #     if data.split('\\')[0] != '"[]':
                #         # splitting the response string to get the amount
                #         flt_amount = float(data.split('\\')[6].split(':')[1].split('}')[0])
                #         Items.objects.filter(id = int_id).update(dbl_apx_amount = flt_amount)


            # return JsonResponse({'status':'success', 'item_amount_per_qty':flt_amount , 'int_buyback_amount' :int_buyback_amount, 'mrp':rst_data['dbl_mrp_price']})
            return JsonResponse({'status':'success', 'item_amount_per_qty':flt_amount,  'mrp':0})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':str(e)})


class getItemStock(APIView):
    permission_classes=[IsAuthenticated]
    """Available stock of purticular item"""
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_id = request.data.get('itemId')     #item id
            flt_amount = 0
            lst_branches = []
            dct_branches = {}
            if int_id:
                str_item_code = Items.objects.filter(pk_bint_id = int_id).values('vchr_item_code')[0]['vchr_item_code']     #item code of item id
                # str_item_code = 2232366
                branch_name = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('vchr_name').first()['vchr_name']      #branch name of current user
                int_territory = Branch.objects.filter(pk_bint_id = request.user.userdetails.fk_branch_id).values('fk_territory').first()['fk_territory']      #territory or current user
                lst_branches_in_terrritory = list(Branch.objects.filter(fk_territory = int_territory).exclude(vchr_name = branch_name).values_list('vchr_name',flat=True))    #branches in the territory
                # lst_branches_in_terrritory.append('LANDSHIP MALL')

                # url and passing parameter for getting the item stock
                url = 'http://138.128.171.250/Branch_wise_cstock.aspx'
                params = {'brwcs':str_item_code}
                req_data = requests.get(url, params=params)
                if req_data.status_code == 200:
                    data = req_data.text
                    if json.loads(data.split('\r\n')[0]) != []:
                        # splitting the response string to get the stock
                        for item in json.loads(data.split('\r\n')[0]):
                            if item['BRANCH_NAME'] == branch_name:      #if stock available in current branch
                                int_stock = item['CS_STOCK']
                                return Response({'status':'success','data':'available','item_stock':int_stock})
                            elif item['BRANCH_NAME'] in lst_branches_in_terrritory:     #if stock available in other branch of same territory
                                dct_branches[item['BRANCH_NAME']] = item['CS_STOCK']
                        lst_branches.append(dct_branches)
            # lst_branches.append({'a':1})
            # lst_branches.append({'b':2})
            return Response({'status':'success','data':'unavailable','item_stock':lst_branches})
        except Exception as e:
            return Response({'status':'failed','reason':str(e)})

class SaveEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            dct_customer = request.data.get('customer_data',0)
            lst_mobile= request.data.get('mobile_data',0)
            lst_tablet= request.data.get('tablet_data',0)
            lst_computer= request.data.get('computer_data',0)
            lst_accessories= request.data.get('accessories_data',0)
            dct_cust_rating = request.data.get('customer_rating')
            bln_status = request.data.get('status')
            ins_user = UserModel.objects.get(id = request.user.id)
            int_stock_id = 0
            # Customer Save Section
            if bln_status.get('MOBILESTATUS'):
                ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
                str_code = ins_document[0].vchr_short_code
                int_doc_num = ins_document[0].int_number + 1
                ins_document.update(int_number = int_doc_num)
                str_number = str(int_doc_num).zfill(4)
                str_enquiry_no = str_code + '-' + str_number
                int_status = 1
                if not dct_customer['fk_assigned_id'] :
                    dct_customer['fk_assigned_id']  = ins_user
                else:
                    dct_customer['fk_assigned_id'] = UserModel.objects.get(id = dct_customer['fk_assigned_id'])
                if dct_customer['fk_branch']:
                    ins_assigneee = UserModel.objects.get(fk_company_id=request.user.userdetails.fk_company_id,fk_group_id__vchr_name='BRANCH MANAGER',fk_branch=ins_user.fk_branch)
                    if not ins_assigneee:
                        return Response({'status':'1', 'data':'branch manager does not exist for select branch'})
                    else:
                        dct_customer['fk_assigned_id']=ins_assigneee
                if dct_customer['fk_assigned_id'].id != ins_user.id:
                    int_status = 0
                dat_created = datetime.now()
                #ins_enquiry = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
                ins_enquiry=EnquiryMaster.objects.create(
                    vchr_enquiry_num = str_enquiry_no,
                    fk_customer = CustomerModel.objects.get(id = dct_customer['fk_customer_id'])
                    ,fk_source = Source.objects.get(pk_bint_id=dct_customer['fk_enquiry_source'])
                    # ,fk_priority = Priority.objects.get(pk_bint_id=dct_customer['fk_enquiry_priority'])
                    ,vchr_customer_type = dct_customer['vchr_customer_type']
                    ,fk_assigned = dct_customer['fk_assigned_id']
                    ,fk_branch = ins_user.fk_branch
                    ,bln_sms = dct_customer['bln_sms']
                    ,chr_doc_status = 'N'
                    ,fk_created_by = ins_user
                    ,dat_created_at = dat_created
                    ,fk_company = ins_user.fk_company
                )
                # Computer Save Section
                if bln_status.get('COMPUTER'):
                    for dct_computer in lst_computer:
                        ins_brand = Brands.objects.get(id = int(dct_computer['fk_brand_id']))
                        ins_item = Items.objects.get(id = int(dct_computer['fk_item_id']))
                        if not dct_computer['dbl_estimated_amount']:
                            dct_computer['dbl_estimated_amount'] = '0.0'

                        if not dct_computer['intQty']:
                            dct_computer['intQty'] = '0'

                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_computer['fk_item_id']), int_available__gte = int(dct_computer['intQty'])).order_by('fk_stock_master__dat_added').values()
                        if ins_stock:
                            int_stock_id = int(ins_stock[0]['pk_bint_id'])
                            if dct_computer.get('vchr_enquiry_status','NEW') == 'BOOKED':
                                int_curr = int(ins_stock[0]['int_available']) - int(dct_computer['intQty'])
                                ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                            else:
                                ins_stock_details = None
                        else:
                            return Response({'status':'1', 'data':'Selected Computer '+ins_brand.vchr_brand_name+'-'+ins_item.vchr_item_name+' quantity '+int(dct_computer['intQty'])+' exceeds available stock amount'})
                        ins_computer = ComputersEnquiry(
                            fk_enquiry_master = ins_enquiry
                            ,fk_brand = ins_brand
                            ,fk_item = ins_item
                            ,int_quantity = int(dct_computer['intQty'])
                            ,dbl_amount = float(dct_computer.get('dbl_estimated_amount','0.0'))
                            ,vchr_enquiry_status = dct_computer.get('vchr_enquiry_status','NEW')
                            ,vchr_remarks = dct_computer['vchr_remarks']
                            ,fk_stockdetails = Stockdetails.objects.get(pk_bint_id = int_stock_id)
                            ,dbl_imei_json = {'imei' : dct_computer.get('lst_imei',[])}
                        )
                        if dct_computer.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            ins_computer.int_sold = int(dct_computer.get('intQty',0))
                            ins_computer.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                        ins_computer.save()
                        ins_computer_follow_up = ComputersFollowup.objects.create(
                            fk_computers = ins_computer
                            ,vchr_notes = dct_computer['vchr_remarks']
                            ,vchr_enquiry_status = dct_computer.get('vchr_enquiry_status','NEW')
                            ,int_status = int_status
                            ,dbl_amount = float(dct_computer.get('dbl_estimated_amount','0.0'))
                            ,fk_user = ins_user
                            ,fk_updated = ins_user
                            ,dat_followup = dat_created
                            ,dat_updated = dat_created
                            ,int_quantity = int(dct_computer['intQty'])

                        )

                # Tablet Save Section
                if bln_status.get('TABLET'):
                    for dct_tablet in lst_tablet:
                        ins_brand = Brands.objects.get(id = int(dct_tablet['fk_brand_id']))
                        ins_item = Items.objects.get(id = int(dct_tablet['fk_item_id']))
                        if not dct_tablet['dbl_estimated_amount']:
                            dct_tablet['dbl_estimated_amount'] = '0.0'

                        if not dct_tablet['intQty']:
                            dct_tablet['intQty'] = '0'
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_tablet['fk_item_id']), int_available__gte = int(dct_tablet['intQty'])).order_by('fk_stock_master__dat_added').values()
                        if ins_stock:
                            int_stock_id = int(ins_stock[0]['pk_bint_id'])
                            if dct_tablet.get('vchr_enquiry_status','NEW') == 'BOOKED':
                                int_curr = int(ins_stock[0]['int_available']) - int(dct_tablet['intQty'])
                                ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                            else:
                                ins_stock_details = None
                        else:
                            return Response({'status':'1', 'data':'Selected Tablet '+ins_brand.vchr_brand_name+'-'+ins_item.vchr_item_name+' quantity '+int(dct_tablet['intQty'])+' exceeds available stock amount'})
                        ins_tablet = TabletEnquiry(
                            fk_enquiry_master = ins_enquiry
                            ,fk_brand = ins_brand
                            ,fk_item = ins_item
                            ,int_quantity = int(dct_tablet['intQty'])
                            ,dbl_amount = float(dct_tablet.get('dbl_estimated_amount','0.0'))
                            ,vchr_enquiry_status = dct_tablet.get('vchr_enquiry_status','NEW')
                            ,vchr_remarks = dct_tablet['vchr_remarks']
                            ,fk_stockdetails = Stockdetails.objects.get(pk_bint_id = int_stock_id)
                            ,dbl_imei_json = {'imei' : dct_tablet.get('lst_imei',[])}
                        )
                        if dct_tablet.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            ins_tablet.int_sold = int(dct_tablet.get('intQty',0))
                            ins_tablet.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                        ins_tablet.save()
                        ins_tablet_follow_up = TabletFollowup.objects.create(
                            fk_tablet = ins_tablet
                            ,vchr_notes = dct_tablet['vchr_remarks']
                            ,vchr_enquiry_status = dct_tablet.get('vchr_enquiry_status','NEW')
                            ,int_status = int_status
                            ,dbl_amount = float(dct_tablet.get('dbl_estimated_amount','0.0'))
                            ,fk_user = ins_user
                            ,fk_updated = ins_user
                            ,dat_followup = dat_created
                            ,dat_updated = dat_created
                            ,int_quantity = int(dct_tablet['intQty'])

                        )
                # Mobile Save Section
                if bln_status.get('MOBILE'):
                    for dct_mobile in lst_mobile:
                        ins_brand = Brands.objects.get(id = int(dct_mobile['fk_brand_id']))
                        ins_item = Items.objects.get(id = int(dct_mobile['fk_item_id']))
                        if not dct_mobile['dbl_estimated_amount']:
                            dct_mobile['dbl_estimated_amount'] = '0.0'

                        if not dct_mobile['intQty']:
                            dct_mobile['intQty'] = '0'
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_mobile['fk_item_id']), int_available__gte = int(dct_mobile['intQty'])).order_by('fk_stock_master__dat_added').values()
                        if ins_stock:
                            int_stock_id = int(ins_stock[0]['pk_bint_id'])
                            if dct_mobile.get('vchr_enquiry_status','NEW') == 'BOOKED':
                                int_curr = int(ins_stock[0]['int_available']) - int(dct_mobile['intQty'])
                                ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                            else:
                                ins_stock_details = None
                        else:
                            return Response({'status':'1', 'data':'Selected Mobile '+ins_brand.vchr_brand_name+'-'+ins_item.vchr_item_name+' quantity '+str(dct_mobile['intQty'])+' exceeds available stock amount'})
                        ins_mobile = MobileEnquiry(
                            fk_enquiry_master = ins_enquiry
                            ,fk_brand = ins_brand
                            ,fk_item = ins_item
                            ,int_quantity = int(dct_mobile['intQty'])
                            ,dbl_amount = float(dct_mobile.get('dbl_estimated_amount','0.0'))
                            ,vchr_enquiry_status = dct_mobile.get('vchr_enquiry_status','NEW')
                            ,vchr_colour = dct_mobile.get('vchr_colour')
                            ,vchr_spec = dct_mobile.get('vchr_spec')
                            ,vchr_remarks = dct_mobile['vchr_remarks']
                            ,fk_stockdetails = Stockdetails.objects.get(pk_bint_id = int_stock_id)
                            ,dbl_imei_json = {'imei' : dct_mobile.get('lst_imei',[])}
                        )
                        if dct_mobile.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            ins_mobile.int_sold = int(dct_mobile.get('intQty',0))
                            ins_mobile.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                        ins_mobile.save()
                        ins_mobile_follow_up = MobileFollowup.objects.create(
                            fk_mobile = ins_mobile
                            ,vchr_notes = dct_mobile['vchr_remarks']
                            ,vchr_enquiry_status = dct_mobile.get('vchr_enquiry_status','NEW')
                            ,int_status = int_status
                            ,dbl_amount = float(dct_mobile.get('dbl_estimated_amount','0.0'))
                            ,fk_user = ins_user
                            ,fk_updated = ins_user
                            ,dat_followup = dat_created
                            ,dat_updated = dat_created
                            ,int_quantity = int(dct_mobile['intQty'])
                        )
                # Accessories Save Section
                if bln_status.get('ACCESSORIES'):
                    for dct_accessories in lst_accessories:
                        ins_brand = Brands.objects.get(id = int(dct_accessories['fk_brand_id']))
                        ins_item = Items.objects.get(id = int(dct_accessories['fk_item_id']))
                        if not dct_accessories['dbl_estimated_amount']:
                            dct_accessories['dbl_estimated_amount'] = '0.0'

                        if not dct_accessories['intQty']:
                            dct_accessories['intQty'] = '0'
                        ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_accessories['fk_item_id']), int_available__gte = int(dct_accessories['intQty'])).order_by('fk_stock_master__dat_added').values()
                        if ins_stock:
                            int_stock_id = int(ins_stock[0]['pk_bint_id'])
                            if dct_accessories.get('vchr_enquiry_status','NEW') == 'BOOKED':
                                int_curr = int(ins_stock[0]['int_available']) - int(dct_accessories['intQty'])
                                ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                            else:
                                ins_stock_details = None
                        else:
                            return Response({'status':'1', 'data':'Selected Accessory '+ins_brand.vchr_brand_name+'-'+ins_item.vchr_item_name+' quantity '+int(dct_accessories['intQty'])+' exceeds available stock amount'})
                        ins_accessories = AccessoriesEnquiry(
                            fk_enquiry_master = ins_enquiry
                            ,fk_brand = ins_brand
                            ,fk_item = ins_item
                            ,int_quantity = int(dct_accessories['intQty'])
                            ,dbl_amount = float(dct_accessories.get('dbl_estimated_amount','0.0'))
                            ,vchr_enquiry_status = dct_accessories.get('vchr_enquiry_status','NEW')
                            ,vchr_remarks = dct_accessories['vchr_remarks']
                            ,fk_stockdetails = Stockdetails.objects.get(pk_bint_id = int_stock_id)
                            ,dbl_imei_json = {'imei' : dct_accessories.get('lst_imei',[])}
                        )
                        if dct_accessories.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            ins_accessories.int_sold = int(dct_accessories.get('intQty',0))
                            ins_accessories.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                        ins_accessories.save()
                        ins_accessories_follow_up = AccessoriesFollowup.objects.create(
                            fk_accessories = ins_accessories
                            ,vchr_notes = dct_accessories['vchr_remarks']
                            ,vchr_enquiry_status = dct_accessories.get('vchr_enquiry_status','NEW')
                            ,int_status = int_status
                            ,dbl_amount = float(dct_accessories.get('dbl_estimated_amount','0.0'))
                            ,fk_user = ins_user
                            ,fk_updated = ins_user
                            ,dat_followup = dat_created
                            ,dat_updated = dat_created
                            ,int_quantity = int(dct_accessories['intQty'])
                        )
                # dct_cust_rating = dct_rating.get('customerRating')
                vchr_feedback = dct_cust_rating['vchr_feedback']
                dbl_rating = dct_cust_rating['dbl_rating']
                fk_customer = dct_cust_rating['fk_customer_id']
                fk_user = dct_cust_rating['fk_user_id']
                # ins_rating =  CustomerRating(
                #     vchr_feedback = vchr_feedback
                #     ,dbl_rating = dbl_rating
                #     ,fk_customer = CustomerModel.objects.get(id= fk_customer)
                #     , fk_user = UserModel.objects.get(user_ptr_id = fk_user)
                # )
                ins_rating.save()
                # str_hash = hash_enquiry(ins_enquiry)
                EnquiryMaster.objects.filter(chr_doc_status='N',pk_bint_id = ins_enquiry.pk_bint_id).update(vchr_hash = str_hash)
                enquiry_print(str_enquiry_no,request,ins_user)
                return Response({'status':'0','result':str_enquiry_no,'enqId':ins_enquiry.pk_bint_id})
            else:
                return Response({'status':'1'})
        except Exception as e:
            ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
            str_code = ins_document[0].vchr_short_code
            int_doc_num = ins_document[0].int_number
            int_update_num = int_doc_num - 1
            str_number = str(int_doc_num).zfill(4)
            str_enquiry_no = str_code + '-' + str_number
            ins_document.update(int_number = int_update_num)
            EnquiryMaster.objects.filter(chr_doc_status='N',vchr_enquiry_num = str_enquiry_no).update(chr_doc_status='D')
            return Response({'status':'1','data':str(e)})
class PendingEnquiryList(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):

        try:

            int_company_id = int(request.data.get('company_id'))
            if not int_company_id:
                return Response({'status':'1','data':["No company found"]})
            else:
                dat_start = ""
                dat_end = ""
                if not request.data['_status']:
                    if request.data['start_date']:
                        dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y').replace(day=1)
                    if request.data['end_date']:
                        dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')
                else:
                    if request.data['start_date']:
                        dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y')
                    if request.data['end_date']:
                        dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')

                # if datetime.now().date() == dat_end.date():
                    # dat_end = dat_end + timedelta(days = 1)

                int_cust_id=request.data.get('custId')
                int_branch_id=request.data.get('branchId')
                session = Session()
                lst_enquiry_data = []

                rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.vchr_enquiry_status.label("Status"))\
                .filter(MobileEnquirySA.vchr_enquiry_status != 'LOST' ,MobileEnquirySA.vchr_enquiry_status != 'BOOKED' , MobileEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )

                rst_tablet =session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.vchr_enquiry_status.label("Status"))\
                .filter(TabletEnquirySA.vchr_enquiry_status != 'LOST' ,TabletEnquirySA.vchr_enquiry_status != 'BOOKED' , TabletEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )

                rst_computer =session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.vchr_enquiry_status.label("Status"))\
                .filter(ComputersEnquirySA.vchr_enquiry_status != 'LOST' ,ComputersEnquirySA.vchr_enquiry_status != 'BOOKED' , ComputersEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )

                rst_accessories =session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.vchr_enquiry_status.label("Status"))\
                .filter(AccessoriesEnquirySA.vchr_enquiry_status != 'LOST' ,AccessoriesEnquirySA.vchr_enquiry_status != 'BOOKED' , AccessoriesEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
                rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()

                rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.Status,\
                                        rst_data.c.vchr_service, CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                        CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
                                        .filter( EnquiryMasterSA.fk_company_id == int_company_id )\
                                        .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
                                        .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                        .group_by(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service, CustomerSA.cust_fname,\
                                        rst_data.c.vchr_service,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name,rst_data.c.Status)

                                                    # , EnquiryMasterSA.int_company_id == int_company_id )\
                                        # .filter(EnquiryMasterSA.dat_created_at >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end, EnquiryMasterSA.fk_company_id == int_company_id )\


                if dat_start:
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.dat_created_at >= dat_start)
                if dat_end:
                    rst_enquiry = rst_enquiry.filter(cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end)
                if request.data.get('custId'):
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_customer_id == request.data.get('custId'))

                if int_branch_id:
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == int_branch_id)

                rst_enquiry = rst_enquiry.order_by(desc(EnquiryMasterSA.dat_created_at))
                # for a in rst_enquiry.order_by(EnquiryMasterSA.dat_created_at.desc()).all() : a.dat_created_at
                dct_enquiries = {}


                for dct_data in rst_enquiry.all():
                    if dct_data.vchr_enquiry_num == dct_enquiries.get('enquiry'):
                        if dct_data._asdict()['vchr_service'] not in dct_enquiries['services']:
                            dct_enquiries['services'].append(dct_data._asdict()['vchr_service'])
                        dct_enquiries['enquiry_status'].append(dct_data._asdict()['Status'].title())

                    else:
                        if dct_enquiries == {}:
                            dct_enquiries = {'enquiry_status':[dct_data._asdict()['Status'].title()],'enquiry_id':dct_data._asdict()['pk_bint_id'],'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
                        else:
                            lst_enquiry_data.append(dct_enquiries)
                            dct_enquiries = {'enquiry_status':[dct_data._asdict()['Status'].title()],'enquiry_id':dct_data._asdict()['pk_bint_id'],'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
                lst_enquiry_data.append(dct_enquiries)
                #            dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
                session.close()
                return Response({'status':'0','data':lst_enquiry_data,})
        except Exception as e:
            session.close()
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'1','data':[str(e)]})


class PendingEnquiryListSide(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):

        try:
            int_company_id = int(request.data.get('intCompanyId'))
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

                int_cust_id=request.data.get('intCustomerId')
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
                # rst_accessories =session.query(AccessoriesEnquirySA.dbl_amount.label('amount'),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.int_quantity.label('int_quantity'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'),AccessoriesEnquirySA.vchr_remarks.label('remarks'))
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
                                            .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.id).join(BrandSA,ItemEnquirySA.fk_brand_id==BrandSA.id)\
                                            .filter(EnquiryMasterSA.fk_company_id ==  int_company_id,EnquiryMasterSA.fk_customer_id == int_cust_id).join(ItemSA,ItemSA.id==ItemEnquirySA.fk_item_id)
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
                lst_enquiry_data=paginate_data(lst_enquiry_data,5)
                #             dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'services':[dct_data._asdict()['vchr_service']],'branch':dct_data._asdict()['vchr_name'],'amount':dct_data._asdict()['amount'],'item':dct_data._asdict()['vchr_item_name'],'remarks':dct_data._asdict()['remarks']}
                # lst_enquiry_data.append(dct_enquiries)
                #             dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
                session.close()
                return Response({'status':'success','data':lst_enquiry_data})
        except Exception as e:
            session.close()
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'failed','data':[str(e)]})

class PendingEnquiryListUser(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):

        try:
            if request.data['start_date']:
                dat_start = datetime.strptime(request.data['start_date'],'%d/%m/%Y')
            if request.data['end_date']:
                dat_end = datetime.strptime(request.data['end_date'],'%d/%m/%Y')

            session = Session()
            lst_enquiry_data = []

            rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id.label("FK_Enquery"), EnquiryMasterSA.dat_created_at, EnquiryMasterSA.vchr_enquiry_num, CustomerSA.cust_fname.label('customer_first_name'), CustomerSA.cust_lname.label('customer_last_name'), CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'), AuthUserSA.last_name.label('staff_last_name'), ItemEnquirySA.fk_product_id,ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_product_name.label("vchr_service")).join(ItemEnquirySA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id).join(ProductsSA,ProductsSA.id == ItemEnquirySA.fk_product_id).join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id).join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id).filter(EnquiryMasterSA.fk_assigned_id == request.data.get('userid'),ItemEnquirySA.vchr_enquiry_status != 'CONVERTED',ItemEnquirySA.vchr_enquiry_status != 'LOST' ,ItemEnquirySA.vchr_enquiry_status != 'BOOKED' ,ItemEnquirySA.vchr_enquiry_status != 'INVOICED').group_by(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.vchr_enquiry_num, CustomerSA.cust_fname,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name,ItemEnquirySA.fk_product_id,ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_product_name)


            if dat_start:
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.dat_created_at >= dat_start)
            if dat_end:
                rst_enquiry = rst_enquiry.filter(cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end)

            rst_enquiry = rst_enquiry.order_by(desc(EnquiryMasterSA.dat_created_at))
            dct_enquiries = {}
            for dct_data in rst_enquiry.all():
                if dct_data.vchr_enquiry_num == dct_enquiries.get('enquiry'):
                    dct_enquiries['services'].append(dct_data._asdict()['vchr_service'])
                else:
                    if dct_enquiries == {}:
                        dct_enquiries = {'enquiry_id':dct_data._asdict()['FK_Enquery'],'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
                    else:
                        lst_enquiry_data.append(dct_enquiries)
                        dct_enquiries = {'enquiry_id':dct_data._asdict()['FK_Enquery'],'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
            lst_enquiry_data.append(dct_enquiries)
            session.close()
            return Response({'status':'0','data':lst_enquiry_data,})
        except Exception as e:
            session.close()
            return Response({'status':'1','data':[str(e)]})

class AssignEnquiry(APIView):
    def post(self,request):
        try:
            for dct_data in request.data['status']:
                if dct_data['status'] == True:
                    ins_enquiry = EnquiryMaster.objects.filter(pk_bint_id = dct_data['id'])
                    ins_enquiry.update(fk_assigned_id = request.data.get('assigneeid'))
            return Response({'status':'success'})
        except Exception as e:
            return Response({'status':'failled','data':str(e)})

def paginate_data(lst_enquiry_data,int_page_legth):
    lst_paged_data = []
    if len(lst_enquiry_data)<=5:
        lst_paged_data.append(lst_enquiry_data)
        return lst_paged_data
    # int_count = 1
    # sorted_dct_data = reversed(sorted(dct_data.items(), key=operator.itemgetter(1)))
    # dct_data = OrderedDict(sorted_dct_data)
    n=1
    lst_sub=[]
    for i in lst_enquiry_data:
        if n==5:
            lst_sub.append(i)
            lst_paged_data.append(lst_sub)
            n=1
            lst_sub=[]
        else:
            lst_sub.append(i)
            n+=1
    if lst_sub:
        lst_paged_data.append(lst_sub)
    return lst_paged_data


class AddEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            with transaction.atomic():
                dct_data = request.data.get('product')
                dct_customer_data = request.data.get('customer_data')
                ins_user = UserModel.objects.get(id = request.user.id)
                ins_branch = UserModel.objects.filter(id = request.user.id).values('fk_branch')
                ins_user_branch = Branch.objects.get(pk_bint_id = ins_branch[0]['fk_branch'])

                dat_created_at = datetime.now()
                # dct_customer_rating = request.data.get('customer_rating')
                # dct_status = request.data.get('status')
                dct_enquirystatus = request.data.get('enquirystatus')

                if dct_customer_data['fk_assigned_id']:
                    ins_assigned_user = UserModel.objects.get(id = int(dct_customer_data['fk_assigned_id']))
                elif ins_user.fk_group.vchr_name=='CALL CENTER':
                    ins_assigned_user= UserModel.objects.filter(fk_branch=dct_customer_data['fk_branch'],fk_group__vchr_name='BRANCH MANAGER',is_active=True).first()
                    ins_user_branch = ins_assigned_user.fk_branch
                else:
                    ins_assigned_user = ins_user
                ins_customer = CustomerModel.objects.get(pk_bint_id = dct_customer_data.get('fk_customer_id'))
                if dct_enquirystatus['enquiry']:
                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
                    str_code = ins_document[0].vchr_short_code
                    int_doc_num = ins_document[0].int_number + 1
                    ins_document.update(int_number = int_doc_num)
                    str_number = str(int_doc_num).zfill(4)
                    str_enquiry_no = str_code + '-' + str_number
                    # ins_master = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
                    ins_master =EnquiryMaster(
                            vchr_enquiry_num = str_enquiry_no,
                            fk_customer = ins_customer
                            ,fk_source = Source.objects.get(pk_bint_id=dct_customer_data.get('fk_enquiry_source'))
                            # ,fk_priority = Priority.objects.get(pk_bint_id=dct_customer_data.get('fk_enquiry_priority'))
                            ,fk_assigned = ins_assigned_user
                            ,fk_branch = ins_user_branch
                            # ,bln_sms = dct_customer_data['bln_sms']
                            ,chr_doc_status = 'N'
                            ,fk_created_by = ins_user
                            ,dat_created_at = datetime.now()
                            ,fk_company = ins_user.fk_company
                            ,vchr_remarks=request.data.get('remarks','')
                        )
                    ins_master.save()
                    

                    ins_gp_item=Items.objects.filter(vchr_name__in=['GDP','GDEW (EXTENDED WARRANTY)']).values()
                    dct_gdp_data={data_gdp['vchr_item_name']:{'product_id':data_gdp['fk_product_id'],'brand_id':data_gdp['fk_brand_id'],'pk_bint_id':data_gdp['id'],'item_code':data_gdp['vchr_item_code']} for data_gdp in ins_gp_item}

                    # ---------------POS API--------------
                    # 
                    

                    dct_pos_data = {}
                    dct_pos_data['vchr_cust_name'] = ins_customer.vchr_name
                    dct_pos_data['vchr_cust_email'] = ins_customer.vchr_email
                    dct_pos_data['int_cust_mob'] = ins_customer.int_mobile
                    dct_pos_data['vchr_gst_no'] = ins_customer.vchr_gst_no
                    dct_pos_data['int_enq_master_id'] = ins_master.pk_bint_id
                    dct_pos_data['vchr_enquiry_num'] = ins_master.vchr_enquiry_num
                    dct_pos_data['vchr_location'] = ''
                    dct_pos_data['int_pin_code'] = ''
                    dct_pos_data['txt_address'] = ''
                    if ins_customer.fk_location:
                        dct_pos_data['vchr_location'] = ins_customer.fk_location.vchr_name
                        dct_pos_data['vchr_district'] = ins_customer.fk_location.vchr_district
                        dct_pos_data['vchr_pin_code'] = ins_customer.fk_location.vchr_pin_code
                    if ins_customer.fk_state:
                        dct_pos_data['vchr_state_code'] = ins_customer.fk_state.vchr_code
                    dct_pos_data['vchr_staff_code'] = ins_master.fk_assigned.username
                    dct_pos_data['vchr_branch_code'] = ins_master.fk_branch.vchr_code
                    dct_pos_data['str_remarks'] = ins_master.vchr_remarks
                    dct_pos_data['dat_enquiry'] = datetime.now().strftime('%Y-%m-%d')
                    dct_pos_data['dct_products'] = {}
                    dct_pos_data['dbl_total_amt'] = 0
                    dct_pos_data['dbl_total_tax'] = 0
                    dct_pos_data['dbl_discount'] = 0
                    dct_pos_data['lst_item'] = []
                    bln_post_rqst = False
                    lst_item_pos = []
                    # -----------------------------

                    for dct_sub in dct_data:

                        for dct_enquiry in dct_data[dct_sub]:
                            if not dct_enquiry['mobileNa']:
                                # 
                                int_product_id=Products.objects.filter(vchr_name__iexact = dct_enquiry['str_product'],fk_company=ins_user.fk_company).values_list('pk_bint_id',flat=True).first()
                                ins_brand = Brands.objects.get(pk_bint_id = int(dct_enquiry['fk_brand_id']))
                                ins_item = Items.objects.get(pk_bint_id = int(dct_enquiry['fk_item_id']))

                                if not dct_enquiry['dbl_estimated_amount']:
                                    dct_enquiry['dbl_estimated_amount'] = '0.0'
                                if not dct_enquiry['intQty']:
                                    dct_enquiry['intQty'] = '0'
                                if not dct_enquiry['dbl_buyback_amount']:
                                    dct_enquiry['dbl_buyback_amount'] = '0'
                                if not dct_enquiry['dbl_discount_amount']:
                                    dct_enquiry['dbl_discount_amount'] = '0'
                                if not dct_enquiry['dbl_gdp']:
                                    dct_enquiry['dbl_gdp'] = '0'
                                if not dct_enquiry['dbl_gdew']:
                                    dct_enquiry['dbl_gdew'] = '0'
                                if not dct_enquiry['dbl_gdew']:
                                    dct_enquiry['dbl_gdew'] = '0'
                                if not dct_enquiry['dbl_actual_amount']:
                                    dct_enquiry['dbl_actual_amount'] = 0.0
                                if not dct_enquiry['dbl_actual_gdp']:
                                    dct_enquiry['dbl_actual_gdp'] = 0.0
                                if not dct_enquiry['dbl_actual_gdew']:
                                    dct_enquiry['dbl_actual_gdew'] = 0.0
                                if dct_enquiry['lst_imei'] == {}:
                                    imei_list = []
                                else:
                                    imei_list = dct_enquiry['lst_imei']
                                # 
                                if dct_enquiry.get('vchr_enquiry_status','') == 'BOOKED':
                                    ins_item_enq = ItemEnquiry(fk_enquiry_master = ins_master,
                                                                fk_product_id=int_product_id,
                                                                fk_brand = Brands.objects.get(id = dct_enquiry['fk_brand_id']),
                                                                fk_item = Items.objects.get(id = dct_enquiry['fk_item_id']),
                                                                int_quantity = dct_enquiry['intQty'],
                                                                dbl_amount = dct_enquiry['dbl_estimated_amount'],
                                                                vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                int_sold = dct_enquiry['intQty'],
                                                                dbl_imei_json = {'imei' : imei_list},
                                                                dbl_buy_back_amount = dct_enquiry['dbl_buyback_amount'],
                                                                dbl_discount_amount =dct_enquiry['dbl_discount_amount'],
                                                                dbl_gdp_amount = 0,
                                                                dbl_gdew_amount = 0,
                                                                int_type = dct_enquiry['int_type'],
                                                                dbl_actual_gdp = dct_enquiry['dbl_actual_gdp'] ,
                                                                dbl_actual_gdew = dct_enquiry['dbl_actual_gdew'],
                                                                dbl_actual_est_amt = dct_enquiry['dbl_actual_amount'],
                                                                dat_sale = datetime.now()
                                                                )
                                    if dct_enquiry['int_type'] in [1,3] and dct_gdp_data.get('GDP'):
                                        ins_item_gdp_enq = ItemEnquiry(fk_enquiry_master = ins_master,
                                                                    fk_product_id=dct_gdp_data['GDP'].get('product_id'),
                                                                    fk_brand_id = dct_gdp_data['GDP'].get('brand_id'),
                                                                    fk_item_id = dct_gdp_data['GDP'].get('pk_bint_id'),
                                                                    int_quantity = dct_enquiry['intQty'],
                                                                    dbl_amount = dct_enquiry['dbl_gdp'],
                                                                    vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                    # vchr_remarks = dct_enquiry['vchr_remarks'],
                                                                    dbl_discount_amount = 0,
                                                                    dbl_buy_back_amount = 0,
                                                                    int_sold = dct_enquiry['intQty'],
                                                                    dbl_imei_json = {'imei' : imei_list},
                                                                    dbl_actual_est_amt = dct_enquiry['dbl_actual_gdp'],
                                                                    dat_sale = datetime.now()
                                                                    )
                                        ins_item_gdp_enq.save()
                                        dct_pos_data['dbl_total_amt'] += float(dct_enquiry['dbl_gdp'])
                                        dct_item = {}
                                        dct_item['item_enquiry_id'] = ins_item_gdp_enq.pk_bint_id
                                        dct_item['vchr_item_name'] = 'GDP'
                                        dct_item['vchr_item_code'] = dct_gdp_data['GDP'].get('item_code')
                                        dct_item['json_imei'] = {"imei" : imei_list}
                                        dct_item['int_quantity'] = dct_enquiry['intQty']
                                        dct_item['dbl_amount'] = float(dct_enquiry['dbl_gdp'])
                                        dct_item['int_status'] = 1
                                        dct_item['dbl_discount'] = 0.0
                                        dct_item['dbl_buyback'] = 0.0
                                        lst_item_pos.append(dct_item)
                                    if dct_enquiry['int_type'] in [2,3] and dct_gdp_data.get('GDEW (EXTENDED WARRANTY)'):
                                        ins_item_gdp_enq = ItemEnquiry(fk_enquiry_master = ins_master,
                                                                    fk_product_id=dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('product_id'),
                                                                    fk_brand_id = dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('brand_id'),
                                                                    fk_item_id = dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('pk_bint_id'),
                                                                    int_quantity = dct_enquiry['intQty'],
                                                                    dbl_amount = dct_enquiry['dbl_gdew'],
                                                                    vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                    # vchr_remarks = dct_enquiry['vchr_remarks'],
                                                                    dbl_discount_amount = 0,
                                                                    dbl_buy_back_amount = 0,
                                                                    int_sold = dct_enquiry['intQty'],
                                                                    dbl_imei_json = {'imei' : imei_list},
                                                                    dbl_actual_est_amt = dct_enquiry['dbl_actual_gdew'],
                                                                    dat_sale = datetime.now()
                                                                    )
                                        ins_item_gdp_enq.save()
                                        dct_pos_data['dbl_total_amt'] += float(dct_enquiry['dbl_gdp'])
                                        dct_item = {}
                                        dct_item['item_enquiry_id'] = ins_item_gdp_enq.pk_bint_id
                                        dct_item['vchr_item_name'] = 'GDEW (EXTENDED WARRANTY)'
                                        dct_item['vchr_item_code'] = dct_gdp_data['GDEW (EXTENDED WARRANTY)'].get('item_code')
                                        dct_item['json_imei'] = {"imei" : imei_list}
                                        dct_item['int_quantity'] = dct_enquiry['intQty']
                                        dct_item['dbl_amount'] = float(dct_enquiry['dbl_gdew'])
                                        dct_item['int_status'] = 1
                                        dct_item['dbl_discount'] = 0.0
                                        dct_item['dbl_buyback'] = 0.0
                                        lst_item_pos.append(dct_item)


                                                                # fk_stockdetails = ins_stock_details)----un comment only when stock details consider
                                else:
                                    ins_item_enq = ItemEnquiry(fk_enquiry_master = ins_master,
                                                                fk_product_id=int_product_id,
                                                                fk_brand = Brands.objects.get(pk_bint_id = dct_enquiry['fk_brand_id']),
                                                                fk_item = Items.objects.get(pk_bint_id = dct_enquiry['fk_item_id']),
                                                                int_quantity = dct_enquiry['intQty'],
                                                                dbl_amount = dct_enquiry['dbl_estimated_amount'],
                                                                vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                dbl_imei_json = {'imei' : imei_list},
                                                                dbl_buy_back_amount = dct_enquiry['dbl_buyback_amount'],
                                                                dbl_discount_amount =dct_enquiry['dbl_discount_amount'],
                                                                dbl_gdp_amount = 0,
                                                                dbl_gdew_amount = 0,
                                                                dbl_actual_gdp = dct_enquiry['dbl_actual_gdp'] ,
                                                                dbl_actual_gdew = dct_enquiry['dbl_actual_gdew'],
                                                                dbl_actual_est_amt = dct_enquiry['dbl_actual_amount'],
                                                                )
                                                                # fk_stockdetails = ins_stock_details)----un comment only when stock details consider

                                ins_item_enq.save()
                                if ins_item_enq and dct_enquiry.get('vchr_enquiry_status','') == 'BOOKED':
                                    ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company,fk_product_id=int_product_id).exclude(vchr_enquiry_status__in =['BOOKED','INVOICED']).exclude(fk_enquiry_master = ins_master)
                                    # if ins_item_enq_exist:
                                    #     ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                                    #     lst_query_set = []
                                    #     for ins_data in ins_item_enq_exist:
                                    #         ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                    #                                           vchr_notes = dct_sub+' '+ str_enquiry_no + ' is booked',
                                    #                                           vchr_enquiry_status = 'LOST',
                                    #                                           int_status = 1,
                                    #                                           dbl_amount = 0.0,
                                    #                                           fk_user = ins_user,
                                    #                                           int_quantity = 0,
                                    #                                           fk_updated = ins_user,
                                    #                                           dat_followup = dat_created_at,
                                    #                                           dat_updated = dat_created_at)
                                    #         lst_query_set.append(ins_follow_up)
                                    #     ItemFollowup.objects.bulk_create(lst_query_set);


                                    # for notifications
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

                                    ################
                                ins_item_foll = ItemFollowup(  fk_item_enquiry = ins_item_enq,
                                                                dat_followup = datetime.now(),
                                                                fk_user = ins_user,
                                                                vchr_notes = request.data.get('remarks',''),
                                                                int_quantity = dct_enquiry['intQty'],
                                                                vchr_enquiry_status = dct_enquiry['vchr_enquiry_status'],
                                                                dbl_amount = dct_enquiry['dbl_estimated_amount'],
                                                                fk_updated = ins_user,
                                                                dat_updated = datetime.now())
                                ins_item_foll.save()
                                # --------------------- POS -------------------
                                if ins_item_enq and dct_enquiry.get('vchr_enquiry_status','') == 'BOOKED':
                                    bln_post_rqst = True
                                    dct_pos_data['dbl_total_amt'] += float(dct_enquiry['dbl_estimated_amount'])
                                    dct_pos_data['dbl_discount'] += float(dct_enquiry['dbl_discount_amount'])
                                    dct_item = {}
                                    dct_item['item_enquiry_id'] = ins_item_enq.pk_bint_id
                                    dct_item['vchr_item_name'] = ins_item.vchr_item_name
                                    dct_item['vchr_item_code'] = ins_item.vchr_item_code
                                    dct_item['json_imei'] = {"imei" : imei_list}
                                    dct_item['int_quantity'] = int(dct_enquiry['intQty'])
                                    dct_item['dbl_amount'] = float(dct_enquiry['dbl_estimated_amount'])
                                    dct_item['dbl_discount'] = float(dct_enquiry['dbl_discount_amount'])
                                    dct_item['dbl_buyback'] = float(dct_enquiry['dbl_buyback_amount'])
                                    dct_item['int_status'] = 1
                                    dct_pos_data['lst_item'].append(dct_item)
                                    dct_pos_data['lst_item'].extend(lst_item_pos)
                    if bln_post_rqst:
                        url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
                        try:
                            res_data = requests.post(url,json=dct_pos_data)
                            if res_data.json().get('status')=='1':
                                pass
                            else:
                                return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                        except Exception as e:
                            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
                    # -----------------------------------------------------------------

                                # ====================================================na enquiry details

                if dct_enquirystatus['naEnquiry']:
                    ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'NAENQUIRY',fk_company = ins_user.fk_company)
                    str_code = ins_document[0].vchr_short_code
                    int_doc_num = ins_document[0].int_number + 1
                    ins_document.update(int_number = int_doc_num)
                    str_number = str(int_doc_num).zfill(4)
                    str_naenquiry_no = str_code + '-' + str_number
                    dct_na_details=request.data.get('naproduct')

                    if dct_na_details:
                        ins_enquiry = NaEnquiryMaster.objects.create_enquiry_num(str_naenquiry_no)

                        NaEnquiryMaster.objects.filter(pk_bint_id = ins_enquiry.pk_bint_id).update(
                            # vchr_enquiry_num = str_naenquiry_no
                            fk_customer = ins_customer
                            ,fk_source = Source.objects.get(pk_bint_id=dct_customer_data.get('fk_enquiry_source'))
                            # ,fk_priority = Priority.objects.get(pk_bint_id=dct_customer_data.get('fk_enquiry_priority'))
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

                                if not dct_data['intQty']:
                                    dct_data['intQty'] = '0'

                                ins_details = NaEnquiryDetails(
                                    fk_na_enquiry_master = ins_enquiry
                                    ,vchr_product = dct_data['str_product'].upper()
                                    ,vchr_brand = dct_data['strStockBrand'].strip().upper()
                                    ,vchr_item = dct_data['strStockItem'].strip().upper()
                                    # ,vchr_color = dct_computer['vchr_color']
                                    ,int_quantity = int(dct_data['intQty'])
                                    # ,vchr_remarks = dct_data['vchr_remarks'].strip()
                                    ,json_product_spec = json.dumps(dct_data['specification'])
                                )
                                ins_details.save()
            #======================================================================
            if dct_enquirystatus['enquiry']:
                # dct_cust_rating = request.data.get('customer_rating')
                # vchr_feedback = dct_cust_rating['vchr_feedback']
                # dbl_rating = dct_cust_rating['dbl_rating']
                # fk_customer = dct_cust_rating['fk_customer_id']
                # fk_user = dct_cust_rating['fk_user_id']
                # ins_rating =  CustomerRating(
                #     vchr_feedback = vchr_feedback
                #     ,dbl_rating = dbl_rating
                #     ,fk_customer = CustomerModel.objects.get(id= fk_customer)
                #     , fk_user = UserModel.objects.get(user_ptr_id = fk_user)
                # )
                # ins_rating.save()
                # # error bug
                # str_hash = hash_enquiry(ins_master)
                # EnquiryMaster.objects.filter(chr_doc_status='N',pk_bint_id = ins_master.pk_bint_id).update(vchr_hash = str_hash)
                # enquiry_print(str_enquiry_no,request,ins_user)

                return JsonResponse({'status': 1,'data':str_enquiry_no,'enqId':ins_master.pk_bint_id})
            elif dct_enquirystatus['naEnquiry']:
                return JsonResponse({'status': 1,'data':str_naenquiry_no,'enqId':ins_enquiry.pk_bint_id})

        except Exception as e:
            if 'ins_master' in locals():
                ItemFollowup.objects.filter(fk_item_enquiry__fk_enquiry_master = ins_master.pk_bint_id).delete()
                ItemEnquiry.objects.filter(fk_enquiry_master = ins_master.pk_bint_id).delete()
                EnquiryMaster.objects.filter(pk_bint_id = ins_master.pk_bint_id).delete()
            if 'ins_enquiry' in locals():
                NaEnquiryDetails.objects.filter(fk_na_enquiry_master = ins_enquiry.pk_bint_id).delete()
                NaEnquiryMaster.objects.filter(pk_bint_id = ins_enquiry.pk_bint_id).delete()
            return JsonResponse({'status': 0,'data':str(e)})

class GetDetailsForAddMobileLead(APIView):
    def post(self,request):
        try:
            
            dct_for_enquiry = {}
            int_user = User.objects.get(id = int(request.data.get('user_id',0)))
            int_companyId = request.GET.get('company_id',request.user.userdetails.fk_company_id)

            # for getting sources
            lst_source = list(Source.objects.filter(bln_status=True,fk_company = int(int_companyId)).values('vchr_source_name','pk_bint_id').order_by('pk_bint_id'))

            # for getting priorities
            lst_priority = list(Priority.objects.filter(bln_status=True,fk_company = int(int_companyId)).values('vchr_priority_name','pk_bint_id').order_by('pk_bint_id'))

            # for getting products
            lst_product_visible = []
            lst_product = []
            ins_product = Products.objects.filter(fk_company = int(int_companyId)).exclude(vchr_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY','GDP']).values('pk_bint_id','vchr_name','bln_visible','dct_product_spec').order_by('pk_bint_id')
            # ins_product = Products.objects.filter(fk_company = int(int_companyId)).exclude(vchr_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY']).values('id','vchr_name','bln_visible','dct_product_spec').order_by('id')
            # ins_product = Products.objects.filter(fk_company = int(int_companyId)).values('id','vchr_name','bln_visible').exclude(vchr_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY']).order_by('id')
            lst_other_prodcuts = []
            dct_na_stock_product = {}

            if ins_product:
                for itr_item in ins_product:
                    dct_product = {}
                    if not itr_item['bln_visible']:
                        if itr_item['vchr_name'] not in lst_other_prodcuts:
                            lst_other_prodcuts.append(itr_item['vchr_name'])
                            if itr_item['dct_product_spec']:
                                dct_na_stock_product[itr_item['vchr_name']] = []
                                for str_spec in itr_item['dct_product_spec']:
                                    if itr_item['dct_product_spec'][str_spec]:
                                        dct_na_stock_product[itr_item['vchr_name']].append(str_spec)
                                # dct_na_stock_product[itr_item['vchr_name']] = itr_item['dct_product_spec'].keys()
                            else:
                                dct_na_stock_product[itr_item['vchr_name']] = []
                    else:
                        dct_product['name'] = itr_item['vchr_name']
                        dct_product['id'] = itr_item['pk_bint_id']
                        dct_product['checked'] = False
                        lst_product_visible.append(dct_product)
                        if itr_item['dct_product_spec']:
                            dct_na_stock_product[itr_item['vchr_name']] = []
                            for str_spec in itr_item['dct_product_spec']:
                                if itr_item['dct_product_spec'][str_spec]:
                                    dct_na_stock_product[itr_item['vchr_name']].append(str_spec)
                            # dct_na_stock_product[itr_item['vchr_name']] = itr_item['dct_product_spec'].keys()
                        else:
                            dct_na_stock_product[itr_item['vchr_name']] = []
                        # dct_na_stock_product[itr_item['vchr_name']] = itr_item['vchr_order']

            # for getting reminders
            lst_reminder = list(Reminder.objects.filter(fk_user=int_user).values())

            # for getting calender reminders
            current_date = datetime.strptime(datetime.today().strftime("%d/%m/%Y"), "%d/%m/%Y").date()
            lst_calender_reminder = list(Reminder.objects.filter(fk_user=int_user,dat_reminder__gte = current_date ).values('dat_reminder'))
            dct_data = {}
            for dct_temp in lst_calender_reminder:
                if dct_temp['dat_reminder'].strftime('%d-%m-%Y') in dct_data:
                    dct_data[dct_temp['dat_reminder'].strftime('%d-%m-%Y')]['title'] += 1
                else:
                    dct_data[dct_temp['dat_reminder'].strftime('%d-%m-%Y')] = {'title':1,'start': dct_temp['dat_reminder'],'color': 'colors.red'}
            lst_calender_reminder = []
            for key in dct_data:
                lst_calender_reminder.append(dct_data[key])

            # for getting sticky notes
            # notes_list = list(StickyNotes.objects.filter(fk_user = int_user).values('pk_bint_id','fk_user', 'vchr_head', 'vchr_description', 'vchr_colour'))

            # for getting assignee
            if UserModel.objects.filter(is_active=True,id=request.user.id).values('fk_branch'):
                int_branch_id = UserModel.objects.filter(is_active=True,id=request.user.id).values('fk_branch')[0]['fk_branch']

            if int_companyId == '0':
                userListData=list(UserModel.objects.filter(is_active=True).values('id','first_name','last_name','fk_branch','fk_branch__vchr_name','bint_phone','username','fk_group__vchr_name','fk_company__vchr_name','username').order_by('-id'))
            else:
                # branch = UserModel.objects.get(id = request.user.id).fk_branch
                userListData = UserModel.objects.filter(is_active = True,fk_company =int(int_companyId),fk_branch=int_branch_id).values('id', 'first_name','last_name','fk_branch','fk_branch__vchr_name','bint_phone','username','fk_group__vchr_name','username').exclude(fk_group__vchr_name__in = ['BRANCH MANAGER','TERRITORY MANAGER','ZONE MANAGER','STATE HEAD','COUNTRY HEAD']).order_by('id')
            for dct_data in userListData:
                dct_data['full_name'] = dct_data['first_name'] + ' ' + dct_data['last_name']

            rst_gdp_range = list(GDPRange.objects.values('dbl_from','dbl_to','dbl_amt','int_type'))
            if rst_gdp_range:
                dct_for_enquiry['gdp_range'] = rst_gdp_range


            dct_for_enquiry['lst_source'] = lst_source
            dct_for_enquiry['lst_priority'] = lst_priority
            dct_for_enquiry['lst_product_visible'] = lst_product_visible
            dct_for_enquiry['lst_other_prodcuts'] = lst_other_prodcuts
            dct_for_enquiry['lst_reminder'] = lst_reminder
            dct_for_enquiry['lst_calender_reminder'] = lst_calender_reminder
            # dct_for_enquiry['notes_list'] = notes_list
            dct_for_enquiry['userListData'] = userListData
            dct_for_enquiry['dct_na_stock'] = dct_na_stock_product
            return Response(dct_for_enquiry)
        except Exception as e:
            return Response({'status':'failled','data':str(e)})


class SavePartialAmount(APIView):
    permission_classes=[IsAuthenticated]
    """Save amount of inauguration enquiry"""
    def post(self,request):
        try:
            dct_details = request.data.get('details')
            flt_partial_amt = request.data.get('partial_amt')


            for key in dct_details.keys():
                for dct_data in dct_details[key]:

                    if 'item_id' in dct_data:
                        ins_item_enq = ItemEnquiry.objects.filter(pk_bint_id = dct_data['item_id'])
                        ins_item_enq.update(vchr_enquiry_status = 'PARTIALLY PAID',vchr_remarks = request.data.get('remark'),dbl_buy_back_amount=dct_data['dbl_buy_back_amount'],dbl_discount_amount=dct_data['discount'])

            EnquiryMaster.objects.filter(pk_bint_id=int(request.data.get('enquiry_id'))).update(dat_created_at=datetime.now(),dbl_partial_amt = flt_partial_amt)
            return Response({'status':'success'})
        except Exception as e:
            return Response({'status':'failed','data':str(e)})
    def get(self,request):
        try:
            lst_offers = list(Offers.objects.filter(bln_active=True).values('pk_bint_id','vchr_code','vchr_details','bln_item'))
            return Response({'status':'success','data':lst_offers})
        except Exception as e:
            return Response({'status':'failed','data':str(e)})


class SaveOfferDetails(APIView):
    permission_classes=[IsAuthenticated]
    """Save offer details of inauguration enquiry"""
    def post(self,request):
        try:
            offer_id = request.data.get('offer_id')
            enquiry_id = request.data.get('enquiry_id')

            if enquiry_id and offer_id:
                ItemEnquiry.objects.filter(pk_bint_id = enquiry_id).update(vchr_enquiry_status = 'OFFER ADDED')
                EnquiryMaster.objects.filter(pk_bint_id=ItemEnquiry.objects.get(pk_bint_id = enquiry_id).fk_enquiry_master_id).update(dat_created_at=datetime.now(),fk_offers_id = int(offer_id))
            else:
                return Response({'status':'failed'})
            return Response({'status':'success'})
        except Exception as e:
            return Response({'status':'failed','data':str(e)})
class UpdateGdp(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            lst_company=list(AdminSettings.objects.filter(fk_company_id=request.user.userdetails.fk_company_id,bln_enabled=True,vchr_name__icontains="REWARDS").values_list('vchr_name',flat=True))
            # import pdb;
            # pdb.set_trace()
            if lst_company:
                    if lst_company[0]=="REWARDS2":

                                dbl_gdp = request.data["int_GDP"]
                                dbl_gdew = request.data["int_GDEW"]
                                int_id = request.data["int_service_id"]
                                int_types = request.data["int_type"]
                                # import pdb;
                                # pdb.set_trace()
                                # ins_user = UserModel.objects.get(id = request.user.id)
                                lst_dbl_gdp_amount = ItemEnquiry.objects.filter(pk_bint_id = int_id).update(pk_bint_id=int_id,dbl_gdp_amount=dbl_gdp,dbl_gdew_amount=dbl_gdew,int_type=int_types)

                                if int_types in [1,3]:
                                    if not ItemEnquiry.objects.filter(pk_bint_id = int_id).values('dat_gdp').first()['dat_gdp']:
                                        ItemEnquiry.objects.filter(pk_bint_id = int_id).update(dat_gdp=datetime.now())
                                if int_types in [2,3]:
                                    if not ItemEnquiry.objects.filter(pk_bint_id = int_id).values('dat_gdew').first()['dat_gdew']:
                                        ItemEnquiry.objects.filter(pk_bint_id = int_id).update(dat_gdew=datetime.now())

                                ####rewards handling

                                lst_item_enquiry_all= ItemEnquiry.objects.filter(pk_bint_id = int_id,vchr_enquiry_status='INVOICED').values('pk_bint_id','fk_item_id','fk_item__fk_product_id','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_discount_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew').first()
                                int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()
                                lst_available=[int_promoter['promo'],1]
                                if not UserModel.objects.filter(id=lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF').values():
                                    lst_available.pop(0)
                                product_total_qty={}
                                item_amount={}
                                lst_available=[]

                                if not int_promoter['fk_brand_id']:
                                    lst_available=[3,1]
                                elif lst_item_enquiry_all['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                                    lst_available=[3,1]
                                elif int_promoter['fk_brand_id']==lst_item_enquiry_all['fk_item__fk_brand_id']:
                                    lst_available=[2,1]

                                # if request.data["int_type"] in [1,3]:
                                #     int_gdp=Products.objects.filter(vchr_name='GDP').values('id').first()['id']
                                #     item_data=RewardAssigned2.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0,  fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id =request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=int_gdp,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to','fk_reward_details').first()
                                #     total_reward=0
                                #     if item_data:
                                #         if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                #             # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                #             if not lst_item_enquiry_all['dbl_actual_gdp'] :
                                #                 pass
                                #             elif lst_item_enquiry_all['dbl_actual_gdp']>lst_item_enquiry_all['dbl_gdp_amount']:
                                #                 pass
                                #             else:
                                #                 if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                #                     reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                #                 elif item_data['dbl_slab1_percentage']:
                                #                     reward=lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                #                 elif item_data['dbl_slab1_amount']:
                                #                     reward=item_data['dbl_slab1_amount']
                                #                 total_reward+=reward
                                #         elif item_data:
                                #             if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                #                 reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                #             elif item_data['dbl_slab1_percentage']:
                                #                 reward=lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                #             elif item_data['dbl_slab1_amount']:
                                #                 reward=item_data['dbl_slab1_amount']
                                #             total_reward+=reward
                                #         # else:
                                #         #     if data['fk_item__fk_product_id'] in product_total_qty:
                                #         #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                #         #     else:
                                #         #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                #         if total_reward:
                                #             if not RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values():
                                #
                                #                 lst_reawards_assigned = list(RewardAssigned2.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))
                                #
                                #                 json_staffs = {}
                                #                 for dct_assign in lst_reawards_assigned:
                                #
                                #                     int_assign_id = lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']
                                #                     str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                #
                                #                     if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                #                         if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                #                             json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                #                         elif dct_assign['int_to'] == 1:
                                #                             json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                #                     elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                #                         if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                #                     elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                #                 if json_staffs:
                                #                     ins_item_reward=RewardsAvailable2(json_staff=json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id'],dbl_mop_amount=lst_item_enquiry_all['dbl_actual_gdp'],dat_reward=datetime.now())
                                #                     ins_item_reward.save()
                                #
                                # ############ GDEW
                                # if request.data["int_type"] in [2,3]:
                                #     int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                                #     item_data=RewardAssigned2.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=int_gdew,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(request.user.userdetails.fk_branch_id)]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to').first()
                                #
                                #     total_reward=0
                                #     if item_data:
                                #         if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                #             # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                #             if not lst_item_enquiry_all['dbl_actual_gdew'] :
                                #                 pass
                                #             elif lst_item_enquiry_all['dbl_actual_gdew']>lst_item_enquiry_all['dbl_gdew_amount']:
                                #                 pass
                                #             else:
                                #                 if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                #                     reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                #                 elif item_data['dbl_slab1_percentage']:
                                #                     reward=lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                #                 elif item_data['dbl_slab1_amount']:
                                #                     reward=item_data['dbl_slab1_amount']
                                #                 total_reward+=reward
                                #         elif item_data:
                                #             if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                #                 reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                #             elif item_data['dbl_slab1_percentage']:
                                #                 reward=lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                #             elif item_data['dbl_slab1_amount']:
                                #                 reward=item_data['dbl_slab1_amount']
                                #             total_reward+=reward
                                #         # else:
                                #         #     if data['fk_item__fk_product_id'] in product_total_qty:
                                #         #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                #         #     else:
                                #         #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                #         if total_reward:
                                #             if not RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values():
                                #
                                #                 lst_reawards_assigned = list(RewardAssigned2.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))
                                #
                                #                 json_staffs = {}
                                #                 for dct_assign in lst_reawards_assigned:
                                #
                                #                     int_assign_id = lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']
                                #                     str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                #
                                #                     if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                #                         if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                #                             json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                #                         elif dct_assign['int_to'] == 1:
                                #                             json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                #                     elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                #                         if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                #                     elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                #                 if json_staffs:
                                #                     ins_item_reward=RewardsAvailable2(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id'],dbl_mop_amount=lst_item_enquiry_all['dbl_actual_gdew'] ,dat_reward=datetime.now())
                                #                     ins_item_reward.save()
                                            ############GDP
                                if request.data['int_type'] in [1,3]:
                                                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']
                                                item_data=RewardsDetails2.objects.filter(int_to__in=lst_available,fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,int_map_type=0,int_map_id=int_gdp,fk_rewards_master__dat_from__lte=datetime.now().date(),fk_rewards_master__dat_to__gte=datetime.now().date(),fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_rewards_master_id','int_quantity_from','int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','int_mop_sale').order_by('int_quantity_to').first()
                                                total_reward=0
                                                if item_data:
                                                    if item_data and item_data['int_mop_sale']==1:
                                                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                        if not lst_item_enquiry_all['dbl_actual_gdp'] :
                                                            pass
                                                        elif lst_item_enquiry_all['dbl_actual_gdp']>lst_item_enquiry_all['dbl_gdp_amount']:
                                                            pass
                                                        else:
                                                            if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_percentage']:
                                                                reward=data['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount']
                                                            total_reward+=reward
                                                    elif item_data:
                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_percentage']:
                                                            reward=lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount']
                                                        total_reward+=reward
                                                    # else:
                                                    #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                    #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                    #     else:
                                                    #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                    if total_reward:
                                                        lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values('json_staff')
                                                        if not lst_json1:
                                                            json_staff={str(lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                        elif lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id'] not in lst_json1.first()['json_staff']:
                                                            json_staff={str(lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}

                                                        if UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()):
                                                            fk_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']
                                                            if not lst_json1:
                                                                if fk_user==lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']:
                                                                        json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                if fk_user==lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']:
                                                                        json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:

                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})

                                                        ins_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first())
                                                        if ins_user:
                                                            if not lst_json1:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})

                                                        if json_staff:
                                                            ins_item_reward=RewardsAvailable2(json_staff=json_staff,fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id'],dbl_mop_amount=lst_item_enquiry_all['dbl_actual_gdp'],dat_reward=datetime.now())
                                                            ins_item_reward.save()
                                            ############ GDEW
                                if request.data['int_type'] in [2,3]:
                                                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                                                item_data=RewardsDetails2.objects.filter(int_to__in=lst_available,fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,int_map_type=0,int_map_id=int_gdew,fk_rewards_master__dat_from__lte=datetime.now().date(),fk_rewards_master__dat_to__gte=datetime.now().date(),fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_rewards_master_id','int_quantity_from','int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','int_mop_sale').order_by('int_quantity_to').first()
                                                total_reward=0
                                                if item_data:
                                                    if item_data and item_data['int_mop_sale']==1:
                                                        item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                                        if not lst_item_enquiry_all['dbl_actual_gdew'] :
                                                            pass
                                                        elif lst_item_enquiry_all['dbl_actual_gdew']>lst_item_enquiry_all['dbl_gdew_amount']:
                                                            pass
                                                        else:
                                                            if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_percentage']:
                                                                reward=lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                            elif item_data['dbl_slab1_amount']:
                                                                reward=item_data['dbl_slab1_amount']
                                                            total_reward+=reward
                                                    elif item_data:
                                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_percentage']:
                                                            reward=lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                                        elif item_data['dbl_slab1_amount']:
                                                            reward=item_data['dbl_slab1_amount']
                                                        total_reward+=reward
                                                    # else:
                                                    #     if data['fk_item__fk_product_id'] in product_total_qty:
                                                    #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                                    #     else:
                                                    #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                                    if total_reward:
                                                        lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values('json_staff')
                                                        if not lst_json1:
                                                            json_staff={str(lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}
                                                        elif lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id'] not in lst_json1.first()['json_staff']:
                                                            json_staff={str(lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']):total_reward/100*80}

                                                        if UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()):
                                                            fk_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']
                                                            if not lst_json1:
                                                                if fk_user==lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id'] not in lst_json1.first()['json_staff']:
                                                                if fk_user==lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']:
                                                                    json_staff[str(fk_user)]=json_staff[str(fk_user)]+((total_reward/100)*20)/100*60
                                                                else:
                                                                    json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*60})
                                                        ins_user=UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first())
                                                        if ins_user:
                                                            lst_json1=RewardsAvailable2.objects.filter(fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values('json_staff')
                                                            if not lst_json1:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']):((total_reward/100)*20)/100*40})
                                                            elif UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']  not in lst_json1.first()['json_staff']:
                                                                json_staff.update({str(UserModel.objects.filter(fk_branch_id=int_promoter['fk_branch_id'],is_active=True,fk_group_id=Groups.objects.filter(vchr_name='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']['user_ptr_id']):((total_reward/100)*20)/100*40})



                                                        if json_staff:
                                                            ins_item_reward=RewardsAvailable2(json_staff=json_staff,fk_rewards_master_id=item_data['fk_rewards_master_id'],fk_rewards_details_id=item_data['pk_bint_id'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id'],dbl_mop_amount=lst_item_enquiry_all['dbl_actual_gdew'],dat_reward=datetime.now())

                                                            ins_item_reward.save()




                                return JsonResponse({'status':'success','data':lst_dbl_gdp_amount,})
                    elif lst_company[0]=="REWARDS1":
                        dbl_gdp = request.data["int_GDP"]
                        dbl_gdew = request.data["int_GDEW"]
                        int_id = request.data["int_service_id"]
                        int_types = request.data["int_type"]
                        # ins_user = UserModel.objects.get(id = request.user.id)
                        lst_dbl_gdp_amount = ItemEnquiry.objects.filter(pk_bint_id = int_id).update(pk_bint_id=int_id,dbl_gdp_amount=dbl_gdp,dbl_gdew_amount=dbl_gdew,int_type=int_types)

                        if int_types in [1,3]:
                            if not ItemEnquiry.objects.filter(pk_bint_id = int_id).values('dat_gdp').first()['dat_gdp']:
                                ItemEnquiry.objects.filter(pk_bint_id = int_id).update(dat_gdp=datetime.now())
                        if int_types in [2,3]:
                            if not ItemEnquiry.objects.filter(pk_bint_id = int_id).values('dat_gdew').first()['dat_gdew']:
                                ItemEnquiry.objects.filter(pk_bint_id = int_id).update(dat_gdew=datetime.now())

                        ####rewards handling

                        lst_item_enquiry_all= ItemEnquiry.objects.filter(pk_bint_id = int_id,vchr_enquiry_status='INVOICED').values('pk_bint_id','fk_item_id','fk_item__fk_product_id','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_discount_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew').first()
                        int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()
                        lst_available=[int_promoter['promo'],1]
                        if not UserModel.objects.filter(id=lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF').values():
                            lst_available.pop(0)
                        product_total_qty={}
                        item_amount={}
                        lst_available=[]

                        if not int_promoter['fk_brand_id']:
                            lst_available=[3,1]
                        elif lst_item_enquiry_all['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                            lst_available=[3,1]
                        elif int_promoter['fk_brand_id']==lst_item_enquiry_all['fk_item__fk_brand_id']:
                            lst_available=[2,1]

                        if request.data["int_type"] in [1,3]:
                            int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']
                            item_data=RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0,  fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id =request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=int_gdp,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to','fk_reward_details').first()
                            total_reward=0
                            if item_data:
                                if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                    # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                    if not lst_item_enquiry_all['dbl_actual_gdp'] :
                                        pass
                                    elif lst_item_enquiry_all['dbl_actual_gdp']>lst_item_enquiry_all['dbl_gdp_amount']:
                                        pass
                                    else:
                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                            reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                        elif item_data['dbl_slab1_percentage']:
                                            reward=lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                        elif item_data['dbl_slab1_amount']:
                                            reward=item_data['dbl_slab1_amount']
                                        total_reward+=reward
                                elif item_data:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward=lst_item_enquiry_all['dbl_gdp_amount']/100*item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward=item_data['dbl_slab1_amount']
                                    total_reward+=reward
                                # else:
                                #     if data['fk_item__fk_product_id'] in product_total_qty:
                                #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                #     else:
                                #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                if total_reward:
                                    if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values():

                                        lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))

                                        json_staffs = {}
                                        for dct_assign in lst_reawards_assigned:

                                            int_assign_id = lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']
                                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                                            if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                                if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                    json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                                elif dct_assign['int_to'] == 1:
                                                    json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                            elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                            elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                        if json_staffs:
                                            ins_item_reward=RewardsAvailable(json_staff=json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id'],dbl_mop_amount=lst_item_enquiry_all['dbl_actual_gdp'],dat_reward=datetime.now())
                                            ins_item_reward.save()

                        ############ GDEW
                        if request.data["int_type"] in [2,3]:
                            int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                            item_data=RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=request.user.userdetails.fk_company_id,fk_reward_details__int_map_type=0,fk_reward_details__int_map_id=int_gdew,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(request.user.userdetails.fk_branch_id)]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id','fk_reward_details__int_quantity_from','fk_reward_details__int_quantity_to','int_to','dbl_slab1_percentage','dbl_slab1_amount','fk_reward_details__int_mop_sale','fk_reward_details').order_by('fk_reward_details__int_quantity_to').first()

                            total_reward=0
                            if item_data:
                                if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                                    # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                                    if not lst_item_enquiry_all['dbl_actual_gdew'] :
                                        pass
                                    elif lst_item_enquiry_all['dbl_actual_gdew']>lst_item_enquiry_all['dbl_gdew_amount']:
                                        pass
                                    else:
                                        if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                            reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                        elif item_data['dbl_slab1_percentage']:
                                            reward=lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                        elif item_data['dbl_slab1_amount']:
                                            reward=item_data['dbl_slab1_amount']
                                        total_reward+=reward
                                elif item_data:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward=item_data['dbl_slab1_amount'] if lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']>item_data['dbl_slab1_amount'] else lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward=lst_item_enquiry_all['dbl_gdew_amount']/100*item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward=item_data['dbl_slab1_amount']
                                    total_reward+=reward
                                # else:
                                #     if data['fk_item__fk_product_id'] in product_total_qty:
                                #         product_total_qty['fk_item__fk_product_id']+=data['int_sold']
                                #     else:
                                #         product_total_qty['fk_item__fk_product_id']=data['int_sold']
                                if total_reward:
                                    if not RewardsAvailable.objects.filter(fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id']).values():

                                        lst_reawards_assigned = list(RewardAssigned.objects.filter(fk_reward_details = item_data['fk_reward_details'],int_status__gte = 0).values('pk_bint_id','fk_reward_details','int_to','fk_group__vchr_name','dbl_slab1_percentage', 'dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount'))

                                        json_staffs = {}
                                        for dct_assign in lst_reawards_assigned:

                                            int_assign_id = lst_item_enquiry_all['fk_enquiry_master__fk_assigned_id']
                                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']

                                            if dct_assign['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF':
                                                if (dct_assign['int_to'] == 3) and (3 in lst_available):
                                                    json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                                elif dct_assign['int_to'] == 1:
                                                    json_staffs[int_assign_id] = dct_assign['dbl_slab1_amount']
                                            elif dct_assign['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                                if UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=request.user.userdetails.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                            elif dct_assign['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                                if UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=request.user.userdetails.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=dct_assign['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = dct_assign['dbl_slab1_amount']
                                        if json_staffs:
                                            ins_item_reward=RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=lst_item_enquiry_all['pk_bint_id'],dbl_mop_amount=lst_item_enquiry_all['dbl_actual_gdew'] ,dat_reward=datetime.now())
                                            ins_item_reward.save()




                        return JsonResponse({'status':'success','data':lst_dbl_gdp_amount,})

            else:
                    return JsonResponse({'status':'0'})

        except Exception as e:
            return JsonResponse({'status':'failed'})




# class AddImei(APIView):
#     permission_classes=[AllowAny]
#     def post(self,request):
#         try:
#
#             int_item_id=request.data.get('item_pk_bint_id')
#             # imei_list = []
#             # imei_list = request.data.get('imeinumbers')
#             # imei_list = [item['imei'] for item in imei_list]
#             # json_imei_structured = {'imei' : imei_list }
#
#             # if request.data.get('imeinumbers'):
#             #         json_imei=request.data.get('imeinumbers')
#             #         json_imei_structured={}
#             #         for i in range(len(json_imei)):
#             #             json_imei_structured[i]=json_imei[i]['imei']
#
#             json_imei_structured = {}
#             imei_list = []
#
#             if(request.data.get('request_response')):
#
#                 if request.data.get('imeinumbers')[0]:
#                     imei_list = request.data.get('imeinumbers')[0]
#                 json_imei_structured = {'imei' : imei_list }
#                 if(ItemEnquiry.objects.filter(pk_bint_id=int_item_id)):
#                     vchr_status=request.data.get('request_response')
#                     if(vchr_status=="Approve"):
#                         ins_item = ItemEnquiry.objects.filter(pk_bint_id=int_item_id).update(vchr_enquiry_status="BOOKED",dbl_imei_json=json_imei_structured)
#                         # ItemFollowup.objects.create(fk_item_enquiry_id = int_item_id,vchr_enquiry_status='BOOKED')
#
#                         if ins_item:
#                             ins_data= ItemEnquiry.objects.get(pk_bint_id=int_item_id)
#                             EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_data.fk_enquiry_master_id).update(vchr_finance_status = 'PROCESSED')
#
#                             # ---------------POS API--------------
#                             ins_cust_enq_finance = FinanceCustomerDetails.objects.filter(fk_enquiry_finance__fk_enquiry_master = ins_data.fk_enquiry_master_id).values('fk_enquiry_finance__fk_financiers__vchr_name', 'fk_enquiry_finance__fk_financier_schema__vchr_schema', 'fk_enquiry_finance__dbl_max_amt', 'dbl_down_payment_amount', 'fk_enquiry_finance__vchr_delivery_order_no', 'fk_enquiry_finance__fk_enquiry_master__fk_customer_id', 'fk_enquiry_finance__fk_enquiry_master_id','fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num', 'fk_enquiry_finance__fk_enquiry_master__fk_assigned__username', 'fk_enquiry_finance__fk_enquiry_master__fk_branch__vchr_code', 'dbl_net_loan_amount', 'fk_enquiry_finance__fk_enquiry_master__vchr_remarks').first()
#                             ins_customer = CustomerModel.objects.get(id=ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_customer_id'])
#
#                             dct_pos_data = {}
#                             dct_pos_data['vchr_cust_name'] = ins_customer.cust_fname+' '+ins_customer.cust_lname
#                             dct_pos_data['vchr_cust_email'] = ins_customer.cust_email
#                             dct_pos_data['int_cust_mob'] = ins_customer.cust_mobile
#                             dct_pos_data['vchr_gst_no'] = ins_customer.vchr_gst_no
#                             dct_pos_data['int_enq_master_id'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master_id']
#                             dct_pos_data['vchr_enquiry_num'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num']
#                             dct_pos_data['vchr_location'] = ''
#                             dct_pos_data['int_pin_code'] = ''
#                             dct_pos_data['txt_address'] = ''
#                             if ins_customer.fk_location:
#                                 dct_pos_data['vchr_location'] = ins_customer.fk_location.vchr_name
#                                 dct_pos_data['vchr_district'] = ins_customer.fk_location.vchr_district
#                                 dct_pos_data['vchr_pin_code'] = ins_customer.fk_location.vchr_pin_code
#                             dct_pos_data['vchr_state_code'] = ''
#                             if ins_customer.fk_state:
#                                 dct_pos_data['vchr_state_code'] = ins_customer.fk_state.vchr_code
#                             dct_pos_data['vchr_staff_code'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_assigned__username']
#                             dct_pos_data['vchr_branch_code'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_branch__vchr_code']
#                             dct_pos_data['str_remarks'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__vchr_remarks']
#                             dct_pos_data['dat_enquiry'] = datetime.now().strftime('%Y-%m-%d')
#                             dct_pos_data['dct_products'] = {}
#                             dct_pos_data['dbl_total_amt'] = 0
#                             dct_pos_data['dbl_total_tax'] = 0
#                             dct_pos_data['dbl_discount'] = 0
#                             dct_pos_data['vchr_finance_name'] = ins_cust_enq_finance['fk_enquiry_finance__fk_financiers__vchr_name']
#                             dct_pos_data['vchr_finance_schema'] = ins_cust_enq_finance['fk_enquiry_finance__fk_financier_schema__vchr_schema']
#                             dct_pos_data['dbl_finance_amt'] = ins_cust_enq_finance['dbl_net_loan_amount']
#                             dct_pos_data['dbl_emi'] = 0
#                             dct_pos_data['dbl_down_payment'] = ins_cust_enq_finance['dbl_down_payment_amount']
#                             dct_pos_data['vchr_fin_ordr_num'] = ins_cust_enq_finance['fk_enquiry_finance__vchr_delivery_order_no']
#                             dct_pos_data['lst_item'] = []
#                             bln_post_rqst = False
#                             if ins_data.vchr_enquiry_status == 'BOOKED':
#                                 bln_post_rqst = True
#                                 dct_pos_data['dbl_total_amt'] += float(ins_data.dbl_amount)
#                                 dct_pos_data['dbl_discount'] += float(ins_data.dbl_discount_amount)
#                                 dct_item = {}
#                                 dct_item['item_enquiry_id'] = int_item_id
#                                 dct_item['vchr_item_name'] = ins_data.fk_item.vchr_item_name
#                                 dct_item['vchr_item_code'] = ins_data.fk_item.vchr_item_code
#                                 dct_item['json_imei'] = ins_data.dbl_imei_json
#                                 dct_item['int_quantity'] = int(ins_data.int_quantity)
#                                 dct_item['dbl_amount'] = float(ins_data.dbl_amount)
#                                 dct_item['dbl_discount'] = float(ins_data.dbl_discount_amount)
#                                 dct_item['dbl_buyback'] = float(ins_data.dbl_buy_back_amount)
#                                 dct_item['vchr_remarks'] = ins_data.vchr_remarks
#                                 dct_item['int_status'] = 1
#                                 dct_pos_data['lst_item'].append(dct_item)
#                             if bln_post_rqst:
#                                 url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
#                                 try:
#                                     res_data = requests.post(url,json=dct_pos_data)
#                                     if res_data.json().get('status')=='1':
#                                         pass
#                                     else:
#                                         return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
#                                 except Exception as e:
#                                     ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#                             # --------------------------------------------------------------
#
#                         return Response({'status':'success','message':'BOOKED'})
#
#                     elif(vchr_status=="Reject"):
#                         ins_item = ItemEnquiry.objects.filter(pk_bint_id=int_item_id).update(vchr_enquiry_status="IMEI REJECTED")
#                         if ins_item:
#                             ins_data= ItemEnquiry.objects.get(pk_bint_id=int_item_id)
#                             EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_data.fk_enquiry_master_id).update(vchr_finance_status = 'IMEI REJECTED')
#
#                         return Response({'status':'success','message':'Rejected'})
#
#             else:
#
#
#                 imei_list = request.data.get('imeinumbers')
#                 if imei_list:
#                     imei_list = [item['imei'] for item in imei_list]
#                 json_imei_structured = {'imei' : imei_list }
#
#                 dct_imei = {v:k for v,k in enumerate(imei_list)}
#
#
#                 if(ItemEnquiry.objects.filter(pk_bint_id=int_item_id)):
#                     ins_item = ItemEnquiry.objects.filter(pk_bint_id=int_item_id).update(dbl_imei_json=json_imei_structured,vchr_enquiry_status="IMEI REQUESTED")
#                     if ins_item:
#                         ins_data= ItemEnquiry.objects.get(pk_bint_id=int_item_id)
#                         EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_data.fk_enquiry_master_id).update(vchr_finance_status = 'IMEI REQUESTED')
#                     return Response({'status':'success','imeinumber':dct_imei})
#                 else:
#                     return Response({'status':'failed','message':"Doesn't Exist"})
#         except Exception as e:
#             return Response({'status':'failed'})

class AddImei(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                int_item_id=request.data.get('item_pk_bint_id')
                json_imei_structured = {}
                imei_list = []
                if(request.data.get('request_response')):

                    if request.data.get('imeinumbers')[0]:
                        imei_list = request.data.get('imeinumbers')[0]
                    json_imei_structured = {'imei' : imei_list }
                    if(ItemEnquiry.objects.filter(pk_bint_id=int_item_id)):
                        vchr_status=request.data.get('request_response')
                        if(vchr_status=="Approve"):
                            ins_item = ItemEnquiry.objects.filter(pk_bint_id=int_item_id).update(vchr_enquiry_status="BOOKED",dbl_imei_json=json_imei_structured)
                            # ItemFollowup.objects.create(fk_item_enquiry_id = int_item_id,vchr_enquiry_status='BOOKED')

                            if ins_item:
                                ins_data= ItemEnquiry.objects.get(pk_bint_id=int_item_id)
                                EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_data.fk_enquiry_master_id).update(vchr_finance_status = 'PROCESSED')

                                ins_item_foll = ItemFollowup(  fk_item_enquiry = ins_data,
                                                                dat_followup = datetime.now(),
                                                                fk_user_id = request.user.id,
                                                                vchr_notes = 'IMEI APPROVED',
                                                                int_quantity = ins_data.int_quantity,
                                                                vchr_enquiry_status = 'BOOKED',
                                                                dbl_amount = ins_data.dbl_amount,
                                                                fk_updated_id = request.user.id,
                                                                dat_updated = datetime.now())
                                ins_item_foll.save()

                                if not ItemEnquiry.objects.filter(~Q(vchr_enquiry_status="BOOKED"),fk_enquiry_master_id = ins_data.fk_enquiry_master_id):
                                    dct_pos_data = {}
                                    dct_pos_data['fk_enquiry_master_id'] = ins_data.fk_enquiry_master_id
                                    dct_pos_data['vchr_enquiry_status'] = 'BOOKED'

                                    url = settings.POS_HOSTNAME+"/invoice/bajajapprovereject/"
                                    try:
                                        res_data = requests.put(url,json=dct_pos_data)
                                        if res_data.json().get('status')==1:
                                            pass
                                        else:
                                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                                    except Exception as e:
                                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
                                # --------------------------------------------------------------

                            return Response({'status':'success','message':'BOOKED'})

                        elif(vchr_status=="Reject"):
                            with transaction.atomic():
                                str_remark = request.data.get('strRemark')
                                ins_enq = ItemEnquiry.objects.filter(pk_bint_id=int_item_id).first()
                                ins_enq.vchr_enquiry_status = "IMEI REJECTED"
                                ins_enq.save()
                                if ins_enq:
                                    ins_data= ItemEnquiry.objects.get(pk_bint_id=int_item_id)
                                    EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_enq.fk_enquiry_master_id).update(vchr_finance_status = 'IMEI REJECTED')

                                    ins_item_foll = ItemFollowup(  fk_item_enquiry = ins_data,
                                                                    dat_followup = datetime.now(),
                                                                    fk_user_id = request.user.id,
                                                                    vchr_notes = str_remark,
                                                                    int_quantity = ins_data.int_quantity,
                                                                    vchr_enquiry_status = 'IMEI REJECTED',
                                                                    dbl_amount = ins_data.dbl_amount,
                                                                    fk_updated_id = request.user.id,
                                                                    dat_updated = datetime.now())
                                    ins_item_foll.save()

                                    dct_pos_data = {}
                                    dct_pos_data['int_enquiry_master_id'] = ins_enq.fk_enquiry_master_id
                                    dct_pos_data['vchr_enquiry_status'] = ins_enq.vchr_enquiry_status
                                    dct_pos_data['int_item_enq_id'] = ins_enq.pk_bint_id
                                    dct_pos_data['str_remark'] = str_remark

                                    # ===========================POS=======================================================
                                    url = settings.POS_HOSTNAME+"/invoice/bajajapprovereject/"
                                    try:
                                        res_data = requests.post(url,json=dct_pos_data)
                                        if res_data.json().get('status')==1:
                                            pass
                                        else:
                                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                                    except Exception as e:
                                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})

                                    # =====================================================================================

                                return Response({'status':'success','message':'Rejected'})

                # else:
                #         imei_list = request.data.get('imeinumbers')
                #         if imei_list:
                #             imei_list = [item['imei'] for item in imei_list]
                #         json_imei_structured = {'imei' : imei_list }
                #
                #         dct_imei = {v:k for v,k in enumerate(imei_list)}
                #
                #         if(ItemEnquiry.objects.filter(pk_bint_id=int_item_id)):
                #             ins_item = ItemEnquiry.objects.filter(pk_bint_id=int_item_id).update(dbl_imei_json=json_imei_structured,vchr_enquiry_status="IMEI REQUESTED")
                #             if ins_item:
                #                 ins_data= ItemEnquiry.objects.get(pk_bint_id=int_item_id)
                #                 EnquiryFinance.objects.filter(fk_enquiry_master_id = ins_data.fk_enquiry_master_id).update(vchr_finance_status = 'IMEI REQUESTED')
                #             return Response({'status':'success','imeinumber':dct_imei})
                #         else:
                #             return Response({'status':'failed','message':"Doesn't Exist"})
        except Exception as e:
            return Response({'status':'failed'})


# def partial_incentive_cal(dct_data):
#     for key in dct_data:
#         lst_product_wise_data={data['fk_item__fk_product_id']:[data['fk_item_id'],data['int_sold']]for data in lst_item_enquiry_all}
#         dct_iter_data={}
#         for key in lst_product_wise_data:
#             if key not in dct_iter_data:
#                 dct_iter_data[key]={'item':lst_product_wise_data[key][0],'qty':lst_product_wise_data[key][1]}
#             else:
#                 dct_iter_data[key]['item'].append(lst_product_wise_data[key][0])
#                 dct_iter_data[key]['qty'].append(lst_product_wise_data[key][1])
#         for key in dct_iter_data:
#             partial_incentive=partial_incentive_cal(dct_iter_data[key])
#             full_incentive=full_incentive_cal(dct_iter_data[key])

#========================= enquiry_finance_images =======================================================
class EnquiryFinanceImage(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:

            with transaction.atomic():
                fk_enquiry_master_id = request.data.get('fk_enquiry_master_id')
                img_bill = request.FILES.get('bill_image')
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                str_filename = fs.save(img_bill.name, img_bill)
                str_bill_image = fs.url(str_filename)
                str_bill_image = str_bill_image[1:]

                img_delivery = request.FILES.get('delivery_image')
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                str_filename = fs.save(img_delivery.name, img_delivery)
                str_delivery_image = fs.url(str_filename)
                str_delivery_image = str_delivery_image[1:]

                img_proof1 = request.FILES.get('img_proof1')
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                str_filename = fs.save(img_proof1.name, img_proof1)
                str_img_proof1 = fs.url(str_filename)
                str_img_proof1 = str_img_proof1[1:]

                str_img_proof2 = None
                if request.FILES.get('img_proof2'):

                    img_proof2 = request.FILES.get('img_proof2')
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                    str_filename = fs.save(img_proof2.name, img_proof2)
                    str_img_proof2 = fs.url(str_filename)
                    str_img_proof2 = str_img_proof2[1:]

                ins_enq_fin_img=EnquiryFinanceImages.objects.create(vchr_bill_image = str_bill_image,
                                                                    vchr_delivery_image = str_delivery_image,
                                                                    vchr_proof1 = str_img_proof1,
                                                                    vchr_proof2 = str_img_proof2,
                                                                    fk_enquiry_master_id =fk_enquiry_master_id
                                                                    )

                ins_item_enq = ItemEnquiry.objects.filter(fk_enquiry_master=fk_enquiry_master_id,vchr_enquiry_status='IMAGE PENDING')
                lst_item = ins_item_enq.values('pk_bint_id','dbl_amount','int_quantity')
                for item in lst_item:
                        ins_item_foll = ItemFollowup(fk_item_enquiry_id = item['pk_bint_id'],
                                                        dat_followup = datetime.now(),
                                                        fk_user_id = request.user.id,
                                                        vchr_notes = 'Invoiced',
                                                        int_quantity = item['int_quantity'],
                                                        vchr_enquiry_status = 'INVOICED',
                                                        dbl_amount = (item['dbl_amount'] * item['int_quantity']),
                                                        fk_updated_id = request.user.id,
                                                        dat_updated = datetime.now())
                        ins_item_foll.save()

                ins_item_enq.update(vchr_enquiry_status='INVOICED')


                return Response({'status':1})
        except Exception as e:
            return Response({'status':0})
# def custome_enq(int_enq_master_id,request):
#     try:
#         if AdminSettings.objects.filter(vchr_code = 'staff_rating_sms').values('bln_enabled').first()['bln_enabled'] == True:
#             ins_enquiry = EnquiryMaster.objects.filter(pk_bint_id=51129).values().order_by('-pk_bint_id')
#             staffurl =request.scheme+'://'+request.get_host()+"/invoice_feedback/"+ins_enquiry[0]['vchr_hash']
#             int_customer_phone = 9656321683
#             # vchr_content = "Dear Customer, Thank you for purchasing from MYGE. Please Rate Us Thank You"
#             # subject = 'FEEDBACK'
#             # html_content = vchr_content
#             # """send Feedback"""
#             # security_key = 'f1290511-f274-11ea-9fa5-0200cd936042' #Amrutha
#             # dct_data = {
#             #             'From': "TFCTOR",
#             #             'To' : 9656321683,
#             #             'Msg' : "Haiii Amrutha",
#             #             }
#             # url = 'http://2factor.in/API/V1/'+security_key+'/ADDON_SERVICES/SEND/TSMS'
#             # url = 'http://2factor.in/API/V1/f1290511-f274-11ea-9fa5-0200cd936042/ADDON_SERVICES/SEND/TSMS'
#             # ins_response = requests.post(url = url, data = dct_data)

#             rsp_request=requests.get("https://app.smsbits.in/api/users?id=OTg0NjY2OTk1NQ&senderid=myGsms&to=9656321683&msg=Dear Customer, Thank you for purchasing from MYGE. Please Rate Us "+staffurl+"&port=TA")
#         else:
#             pass
#     except Exception as e:
#         print(str(e))
#         return True

class EnquiryInvoiceUpdate(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                # 

                str_remark = request.data.get('str_remarks') or ""
                dct_item_data = request.data.get('dct_item_data')
                int_type=request.data.get('int_type')
                lst_item_data = list(dct_item_data.values())
                int_enq_master_id = request.data.get('int_enq_master_id')
                ins_user_id = EnquiryMaster.objects.filter(pk_bint_id=int_enq_master_id).values('fk_assigned_id').first()['fk_assigned_id']
                lst_item_code_cur_all = ItemEnquiry.objects.filter(fk_enquiry_master_id = int_enq_master_id,vchr_enquiry_status__in=['BOOKED','FINANCED','SPECIAL SALE']).values_list('pk_bint_id',flat=True)
                if not lst_item_code_cur_all:
                    return Response({'status':'success'})
                int_sale_type = EnquiryMaster.objects.get(pk_bint_id=int_enq_master_id).int_customer_type
                str_status = 'INVOICED'
                if int_sale_type and int_sale_type == 1:
                    str_status = 'IMAGE PENDING'
                lst_old_item = []
                lst_service_item = []
                # Structure the old item details with item enquiry id keys to update item enquiry table

                """Data to payment_details"""

                if request.data.get('bi_payment_details'):
                    lst_payment_details=[]
                    for data in request.data['bi_payment_details']:
                        ins_payment_details=PaymentDetails(fk_enquiry_master_id = int_enq_master_id, int_fop = data['int_fop'], dbl_amount = data['dbl_amt'], dat_created = datetime.today())
                        lst_payment_details.append(ins_payment_details)
                    PaymentDetails.objects.bulk_create(lst_payment_details)
                else:
                    if request.data.get("credit_sale"):
                        dct_item_data_ = request.data.get("dct_item_data")
                        if dct_item_data_:
                            total_amount_ = sum([dct_item_data_[x]['dblAmount'] for x in dct_item_data_])
                            ins_payment_details = PaymentDetails.objects.create(fk_enquiry_master_id=int_enq_master_id, int_fop= -1,
                            dbl_amount = total_amount_, dat_created = datetime.today()) # -1 for credit sale



                for str_data in dct_item_data:
                    apx_amount = None
                    if str_data.split('-')[0] == '0' and ItemEnquiry.objects.filter(pk_bint_id =  str_data.split('-')[1]).exclude(vchr_enquiry_status='INVOICED'):
                        ins_item_enq = ItemEnquiry.objects.filter(pk_bint_id =  str_data.split('-')[1])
                        ins_product = ins_item_enq.values('fk_product__vchr_product_name')[0]['fk_product__vchr_product_name']
                        if ins_product.upper() != 'SERVICE':
                            apx_amount = ins_item_enq.values('fk_item__dbl_apx_amount')[0]['fk_item__dbl_apx_amount']
                        else:
                            lst_service_item.append(str_data)

                        lst_old_item.append(int(str_data.split('-')[1]))
                        ins_item_enq.update(dbl_buy_back_amount = dct_item_data[str_data]['dblBuyBack'],
                                                dbl_discount_amount = dct_item_data[str_data]['dblDiscount'],
                                                dbl_amount = dct_item_data[str_data]['dblAmount'] +dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                dbl_imei_json = {'imei' : dct_item_data[str_data].get('jsonImei')},
                                                int_sold = dct_item_data[str_data]['intQuantity'],
                                                dbl_sup_amount = dct_item_data[str_data]['dbl_supp_amnt'],
                                                vchr_remarks = str_remark,
                                                vchr_enquiry_status = str_status,
                                                dat_sale = datetime.now(),
                                                dbl_indirect_discount_amount=dct_item_data[str_data]['dblIndirectDis'],

                                                # LG
                                                dbl_cost_price = dct_item_data[str_data]['dbl_cost_amnt'],
                                                dbl_dealer_price  = dct_item_data[str_data]['dbl_dealer_amnt'],
                                                dbl_mop_price = dct_item_data[str_data]['dbl_mop_amnt'],
                                                dbl_myg_price = dct_item_data[str_data]['dbl_myg_amnt'],
                                                dbl_mrp_price = dct_item_data[str_data]['dbl_mrp_amnt'],

                                                dbl_tax = dct_item_data[str_data]['dbl_tax'],
                                                json_tax = dct_item_data[str_data]['json_tax']
                                                )



                        ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = str_data.split('-')[1],
                                                            vchr_notes = str_status,
                                                            vchr_enquiry_status = str_status,
                                                            int_status = 1,
                                                            dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack']+dct_item_data[str_data]['dblDiscount'],
                                                            fk_user_id = ins_user_id,
                                                            int_quantity = dct_item_data[str_data]['intQuantity'],
                                                            fk_updated_id = ins_user_id,
                                                            dat_followup = datetime.now(),
                                                            dat_updated = datetime.now())

                    else:
                        ins_item = Items.objects.filter(vchr_item_code= dct_item_data[str_data]['strItemCode'])
                        ins_product = ins_item.values('fk_product__vchr_product_name')[0]['fk_product__vchr_product_name']
                        if ins_product.upper() != 'SERVICE':
                            # ins_item_enq.update(dbl_actual_est_amt = dct_old_item[int_id]['data']['apx_amount'])
                            apx_amount = ins_item.values('dbl_apx_amount')[0]['dbl_apx_amount']
                        else:
                            lst_service_item.append(str_data)
                        if dct_item_data[str_data]['status']==1:
                            ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
                                                        fk_item_id = ins_item.values('id')[0]['id'],
                                                        dbl_buy_back_amount = dct_item_data[str_data]['dblBuyBack'],
                                                        dbl_discount_amount = dct_item_data[str_data]['dblDiscount'],
                                                        dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                        # dbl_imei_json = dct_item_data[str_data]['jsonImei'],
                                                        dbl_imei_json = {'imei' : dct_item_data[str_data].get('jsonImei')},
                                                        int_quantity = dct_item_data[str_data]['intQuantity'],
                                                        int_sold = dct_item_data[str_data]['intQuantity'],
                                                        fk_product_id = ins_item.values('fk_product_id')[0]['fk_product_id'],
                                                        fk_brand_id =  ins_item.values('fk_brand_id')[0]['fk_brand_id'],
                                                        vchr_enquiry_status = str_status,
                                                        dbl_actual_est_amt = apx_amount,
                                                        dbl_sup_amount = dct_item_data[str_data]['dbl_supp_amnt'],
                                                        dat_sale = datetime.now(),
                                                        vchr_remarks = str_remark,
                                                        dbl_indirect_discount_amount=dct_item_data[str_data]['dblIndirectDis'],

                                                        # LG
                                                        dbl_cost_price = dct_item_data[str_data]['dbl_cost_amnt'],
                                                        dbl_dealer_price  = dct_item_data[str_data]['dbl_dealer_amnt'],
                                                        dbl_mop_price = dct_item_data[str_data]['dbl_mop_amnt'],
                                                        dbl_myg_price = dct_item_data[str_data]['dbl_myg_amnt'],
                                                        dbl_mrp_price = dct_item_data[str_data]['dbl_mrp_amnt'],

                                                        dbl_tax = dct_item_data[str_data]['dbl_tax'],
                                                        json_tax = dct_item_data[str_data]['json_tax']
                                                        )
                            ins_item_enq.save()

                            ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
                                                                vchr_notes =str_status,
                                                                vchr_enquiry_status = str_status,
                                                                int_status = 1,
                                                                dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                                fk_user_id = ins_user_id,
                                                                int_quantity = dct_item_data[str_data]['intQuantity'],
                                                                fk_updated_id = ins_user_id,
                                                                dat_followup = datetime.now(),
                                                                dat_updated = datetime.now())
                        elif dct_item_data[str_data]['status']==0:
                            ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
                                                        fk_item_id = ins_item.values('id')[0]['id'],
                                                        dbl_buy_back_amount = dct_item_data[str_data]['dblBuyBack'],
                                                        dbl_discount_amount = dct_item_data[str_data]['dblDiscount'],
                                                        dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                        # dbl_imei_json = dct_item_data[str_data]['jsonImei'],
                                                        dbl_imei_json = {'imei' : dct_item_data[str_data].get('jsonImei')},
                                                        int_quantity = dct_item_data[str_data]['intQuantity'],
                                                        int_sold = dct_item_data[str_data]['intQuantity'],
                                                        fk_product_id = ins_item.values('fk_product_id')[0]['fk_product_id'],
                                                        fk_brand_id =  ins_item.values('fk_brand_id')[0]['fk_brand_id'],
                                                        vchr_enquiry_status = 'RETURNED',
                                                        dbl_actual_est_amt = apx_amount,
                                                        dbl_sup_amount = dct_item_data[str_data]['dbl_supp_amnt'],
                                                        dat_sale = datetime.now(),
                                                        vchr_remarks = str_remark,

                                                        # LG
                                                        dbl_cost_price = dct_item_data[str_data]['dbl_cost_amnt'],
                                                        dbl_dealer_price  = dct_item_data[str_data]['dbl_dealer_amnt'],
                                                        dbl_mop_price = dct_item_data[str_data]['dbl_mop_amnt'],
                                                        dbl_myg_price = dct_item_data[str_data]['dbl_myg_amnt'],
                                                        dbl_mrp_price = dct_item_data[str_data]['dbl_mrp_amnt'],

                                                        dbl_tax = dct_item_data[str_data]['dbl_tax'],
                                                        json_tax = dct_item_data[str_data]['json_tax']
                                                        )
                            ins_item_enq.save()
                            ins_enquiry_master=EnquiryMaster.objects.get(pk_bint_id=int_enq_master_id)
                            ins_item_enquiry_return=ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id=ins_enquiry_master.fk_customer_id,dbl_imei_json__contains={'imei':dct_item_data[str_data]['jsonImei']})
                            if ins_item_enquiry_return:
                                ins_avaialble=RewardsAvailable.objects.filter(fk_item_enquiry_id=ins_item_enquiry_return[0].pk_bint_id).values()
                                if ins_avaialble:
                                    for data in ins_avaialble:
                                        RewardsAvailable.objects.create(fk_rewards_master_id=data['fk_rewards_master_id'],fk_rewards_details_id=data['fk_rewards_details_id'],fk_item_enquiry_id=data['fk_item_enquiry_id'],dat_reward=datetime.now(),dbl_mop_amount=data['dbl_mop_amount'],json_staff={dct_rwd_data:-data['json_staff'][dct_rwd_data] for dct_rwd_data in data['json_staff']})
                            ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
                                                            vchr_notes = 'RETURNED',
                                                            vchr_enquiry_status = 'RETURNED',
                                                            int_status = 1,
                                                            dbl_amount = dct_item_data[str_data]['dblAmount']+dct_item_data[str_data]['dblBuyBack'] + dct_item_data[str_data]['dblDiscount'],
                                                            fk_user_id = ins_user_id,
                                                            int_quantity = dct_item_data[str_data]['intQuantity'],
                                                            fk_updated_id = ins_user_id,
                                                            dat_followup = datetime.now(),
                                                            dat_updated = datetime.now())
                lst_deleted_item = list(set(lst_item_code_cur_all)-set(lst_old_item))
                # 
                # IMAGE PENDING -NOTIFICATION
                if str_status == 'IMAGE PENDING':
                    if str_data.split('-')[0] == '0' and ItemEnquiry.objects.filter(pk_bint_id =  str_data.split('-')[1]).exclude(vchr_enquiry_status='INVOICED'):
                        ins_assigned = EnquiryMaster.objects.filter(pk_bint_id = ins_item_enq[0].fk_enquiry_master_id).values('fk_assigned_id').first()
                    else:
                        ins_assigned = EnquiryMaster.objects.filter(pk_bint_id = ins_item_enq.fk_enquiry_master_id).values('fk_assigned_id').first()

                    int_assigned = ins_assigned['fk_assigned_id']
                    ins_rem = Reminder.objects.filter(fk_user = int_assigned, vchr_description__icontains = '(IMAGE PENDING)')
                    count_old = ItemEnquiry.objects.filter(fk_enquiry_master_id__fk_assigned_id = int_assigned,vchr_enquiry_status = 'IMAGE PENDING').values('fk_enquiry_master_id__fk_assigned_id').count()
                    actual_count = count_old
                    if actual_count > 1:
                        str_notification = str(actual_count) + ' enquiries need to be updated with proper images(IMAGE PENDING)'

                    elif actual_count == 1:
                        str_notification = str(actual_count) + ' enquiry needs to be updated with proper images(IMAGE PENDING)'

                    if actual_count != 0:
                        ins_reminder = Reminder.objects.create(fk_user_id        = int_assigned,
                                                                dat_created_at   = datetime.now(),
                                                                dat_updated_at   = datetime.now(),
                                                                vchr_title       = 'IMAGE PENDING ENQUIRY',
                                                                vchr_description = str_notification,
                                                                dat_reminder     = datetime.now()
                                                                )
                # NOTIFICATION END
                for int_enq_id in lst_deleted_item:
                    ins_item_enq=ItemEnquiry.objects.filter(pk_bint_id =  int_enq_id)
                    ins_item_enq.update(vchr_enquiry_status = 'PENDING')
                    ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = int_enq_id,
                                                        vchr_notes = 'PENDING',
                                                        vchr_enquiry_status = 'PENDING',
                                                        int_status = 1,
                                                        dbl_amount = ins_item_enq[0].dbl_amount,
                                                        fk_user_id = ins_user_id,
                                                        int_quantity = ins_item_enq[0].int_quantity,
                                                        fk_updated_id = ins_user_id,
                                                        dat_followup = datetime.now(),
                                                        dat_updated = datetime.now()
                    )
                for str_data in lst_service_item:
                    if dct_item_data[str_data]['int_type']==1 or dct_item_data[str_data]['int_type']==2:
                        ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei')),fk_enquiry_master_id=int_enq_master_id).values('fk_item__dbl_apx_amount','int_type','int_quantity').exclude(fk_product__vchr_product_name='SERVICE').first()
                        if not ins_up_item_enq:
                            ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei'))).values('fk_item__dbl_apx_amount','int_type','int_quantity').exclude(fk_product__vchr_product_name='SERVICE').first()
                        ins_up_item_enq['fk_item__dbl_apx_amount'] = ins_up_item_enq['fk_item__dbl_apx_amount'] if ins_up_item_enq.get('fk_item__dbl_apx_amount') else 0
                        gdp_value=GDPRange.objects.filter(dbl_from__lte=(ins_up_item_enq['fk_item__dbl_apx_amount']),dbl_to__gte=(ins_up_item_enq['fk_item__dbl_apx_amount']),int_type=dct_item_data[str_data]['int_type']).values('dbl_amt').first()
                        if ins_up_item_enq['int_type']!=0:
                            if ins_up_item_enq['int_type']!=dct_item_data[str_data]['int_type']:
                                ins_up_item_enq.update(int_type=3)
                        else:
                            ins_up_item_enq.update(int_type=dct_item_data[str_data]['int_type'])
                        gdp_value = gdp_value['dbl_amt'] if gdp_value else 0
                        if dct_item_data[str_data]['int_type']==1:
                            ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei')),fk_item__vchr_item_code='GDC00001',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value)
                        if dct_item_data[str_data]['int_type']==2:
                            ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[str_data].get('jsonImei')})|Q(dbl_imei_json__contains=dct_item_data[str_data].get('jsonImei')),fk_item__vchr_item_name='GDC00002',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value)
                special_rewards_script_sudheesh(int_enq_master_id)
                # custome_enq(int_enq_master_id,request)
                # Uncomment When using celery
                send_feedback_sms.delay(int_enq_master_id)
                # send_feedback_sms(int_enq_master_id)

                return Response({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return JsonResponse({'status':'failed','message':str(e)})

    # def post(self,request):
        # try:
        #     with transaction.atomic():
        #         # 
        #         str_remark = request.data.get('str_remarks') or ""
        #         dct_item_data = request.data.get('dct_item_data')
        #         int_type=request.data.get('int_type')
        #         lst_item_data = list(dct_item_data.values())
        #         int_enq_master_id = request.data.get('int_enq_master_id')
        #         ins_user_id = EnquiryMaster.objects.filter(pk_bint_id=int_enq_master_id).values('fk_assigned_id').first()['fk_assigned_id']
        #
        #         lst_item_code_cur_all = ItemEnquiry.objects.filter(fk_enquiry_master_id = int_enq_master_id,vchr_enquiry_status='BOOKED').values_list('pk_bint_id',flat=True)
        #         lst_item_code_updt_all = list({x.get('itemEnqId') for x in lst_item_data}) #list comprehenson for getting updated item codes
        #         lst_dlt_item_code = list(set(lst_item_code_cur_all) - set(lst_item_code_updt_all))
        #         lst_new_item_code =  list(set(lst_item_code_updt_all) - set(lst_item_code_cur_all))
        #         lst_new_item_code = [ x['strItemCode'] for x in lst_item_data if not x['itemEnqId']]
        #         lst_item_details = list(Items.objects.filter(vchr_item_code__in =lst_new_item_code).values('fk_product_id','fk_brand_id','vchr_item_code','id'))
        #         # if ItemFollowup.objects.filter(fk_item_enquiry__fk_enquiry_master_id = int_enq_master_id,vchr_enquiry_status__in=['IMEI PENDING','IMEI REJECTED','IMEI REQUESTED','IMEI APPROVED']).exists():
        #         #     str_status = 'IMAGE PENDING'
        #         # else:
        #         #     str_status = 'INVOICED'
        #         str_status = 'INVOICED'
        #         dct_item_code_details = {item['vchr_item_code']:item for item in lst_item_details}
        #         int_type=1
        #         # lst_new_item_code = []
        #         # ==============================================================New Block of Code with enquiry id ================================================================================================
        #
        #
        #         dct_old_item = {}
        #         dct_new_item = {}
        #         # Structure the old item details with item enquiry id keys to update item enquiry table
        #         # 
        #
        #         """Data to payment_details"""
        #         lst_payment_details=[]
        #         for data in request.data['bi_payment_details']:
        #             ins_payment_details=PaymentDetails(fk_enquiry_master_id = int_enq_master_id, int_fop = data['int_fop'], dbl_amount = data['dbl_amt'], dat_created = datetime.today())
        #             lst_payment_details.append(ins_payment_details)
        #         PaymentDetails.objects.bulk_create(lst_payment_details)
        #
        #         # 
        #         for dct_enquiry in lst_item_data:
        #             if dct_enquiry['itemEnqId'] and dct_enquiry['itemEnqId'] not in dct_old_item:
        #                 dct_old_item[dct_enquiry['itemEnqId']] ={}
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']=dct_enquiry
        #
        #                 # Find apx amount of item from item table
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['apx_amount'] = Items.objects.filter(vchr_item_code=dct_enquiry['strItemCode']).values('dbl_apx_amount').order_by('-id').first()['dbl_apx_amount']
        #
        #                 dct_old_item[dct_enquiry['itemEnqId']]['item_code'] = dct_enquiry['strItemCode']
        #
        #             elif dct_enquiry['itemEnqId'] and dct_enquiry['itemEnqId'] in dct_old_item:
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblBuyBack'] +=dct_enquiry['dblBuyBack']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblDiscount'] +=dct_enquiry['dblDiscount']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['intQuantity'] +=dct_enquiry['intQuantity']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dbl_supp_amnt'] +=dct_enquiry['dbl_supp_amnt']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblAmount'] +=dct_enquiry['dblAmount']
        #                 # LG
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblCostPrice'] = dct_enquiry['dbl_cost_amnt']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblDealerPrice'] = dct_enquiry['dbl_dealer_amnt']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblMopPrice'] = dct_enquiry['dbl_mop_amnt']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblMygPrice'] = dct_enquiry['dbl_myg_amnt']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dblMRP'] = dct_enquiry['dbl_mrp_amnt']
        #
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['dbltax'] = dct_enquiry['dbl_tax']
        #                 dct_old_item[dct_enquiry['itemEnqId']]['data']['json_tax'] = dct_enquiry['json_tax']
        #
        #         # Structure the new item details with item code to insert to item enquiry table
        #         for dct_enquiry in lst_item_data:
        #             bln_log = False
        #             # To check new added item already exists in item enquiry table
        #             if not dct_enquiry['itemEnqId']:
        #                 for str_code in dct_old_item:
        #                     if dct_enquiry['strItemCode'] == dct_old_item[str_code]['item_code'] and (dct_enquiry['dblAmount']/dct_enquiry['intQuantity']) == (dct_old_item[str_code]['data']['dblAmount']/dct_old_item[str_code]['data']['intQuantity']):
        #                         dct_old_item[str_code]['data']['dblBuyBack'] +=dct_enquiry['dblBuyBack']
        #                         dct_old_item[str_code]['data']['dblDiscount'] +=dct_enquiry['dblDiscount']
        #                         dct_old_item[str_code]['data']['intQuantity'] +=dct_enquiry['intQuantity']
        #                         dct_old_item[str_code]['data']['dbl_supp_amnt'] +=dct_enquiry['dbl_supp_amnt']
        #                         dct_old_item[str_code]['data']['dblAmount'] +=dct_enquiry['dblAmount']
        #                         # LG
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['dblCostPrice'] = dct_enquiry['dbl_cost_amnt']
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['dblDealerPrice'] = dct_enquiry['dbl_dealer_amnt']
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['dblMopPrice'] = dct_enquiry['dbl_mop_amnt']
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['dblMygPrice'] = dct_enquiry['dbl_myg_amnt']
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['dblMRP'] = dct_enquiry['dbl_mrp_amnt']
        #
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['dbl_tax'] = dct_enquiry['dbl_tax']
        #                         dct_old_item[dct_enquiry['itemEnqId']]['data']['json_tax'] = dct_enquiry['json_tax']
        #                         bln_log = True
        #                         break
        #                 if not bln_log: #Item not item enquiry table in this enquiry
        #                     if dct_enquiry['strItemCode'] not in dct_new_item:
        #                         dct_new_item[dct_enquiry['strItemCode']]={}
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']=dct_enquiry
        #                         ins_items = Items.objects.filter(vchr_item_code=dct_enquiry['strItemCode']).values('dbl_apx_amount').order_by('-id').first()
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['apx_amount'] = ins_items['dbl_apx_amount']  if ins_items else 0
        #                     else:
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblBuyBack'] +=dct_enquiry['dblBuyBack']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblDiscount'] +=dct_enquiry['dblDiscount']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['intQuantity'] +=dct_enquiry['intQuantity']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dbl_supp_amnt'] +=dct_enquiry['dbl_supp_amnt']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblAmount'] +=dct_enquiry['dblAmount']
        #                         # LG
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblCostPrice'] = dct_enquiry['dbl_cost_amnt']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblDealerPrice'] = dct_enquiry['dbl_dealer_amnt']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblMopPrice'] = dct_enquiry['dbl_mop_amnt']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblMygPrice'] = dct_enquiry['dbl_myg_amnt']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dblMRP'] = dct_enquiry['dbl_mrp_amnt']
        #
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['dbl_tax'] = dct_enquiry['dbl_tax']
        #                         dct_new_item[dct_enquiry['strItemCode']]['data']['json_tax'] = dct_enquiry['json_tax']
        #
        #         # 
        #         for int_id in dct_old_item:
        #             ins_item_enq = ItemEnquiry.objects.filter(pk_bint_id =  dct_old_item[int_id]['data']['itemEnqId'])
        #
        #             # find product to update apx amount for non service products
        #             ins_product = ins_item_enq.values('fk_product__vchr_product_name')[0]['fk_product__vchr_product_name']
        #             if ins_product.upper() != 'SERVICE':
        #                 ins_item_enq.update(dbl_actual_est_amt = dct_old_item[int_id]['data']['apx_amount'])
        #
        #             """indirect discount check"""
        #             if not dct_old_item[int_id]['data']['dblDiscount'] and ins_item_enq.values()[0]['dbl_discount_amount'] and  dct_old_item[int_id]['data'].get('dblIndirectDis'):
        #
        #                 ins_item_enq.update(dbl_buy_back_amount = dct_old_item[int_id]['data']['dblBuyBack'],
        #                                         dbl_discount_amount = dct_old_item[int_id]['data']['dblDiscount'],
        #                                         dbl_amount = dct_old_item[int_id]['data']['dblAmount']+dct_old_item[int_id]['data']['dblBuyBack']+dct_old_item[int_id]['data']['dblDiscount'],
        #                                         dbl_imei_json = {'imei' : dct_old_item[int_id]['data']['jsonImei']},
        #                                         int_sold = dct_old_item[int_id]['data']['intQuantity'],
        #                                         dbl_sup_amount = dct_old_item[int_id]['data']['dbl_supp_amnt'],
        #                                         vchr_remarks = str_remark + " , indriect discount added '"+dct_old_item[int_id]['data'].get('dblIndirectDis')+"'",
        #                                         vchr_enquiry_status = str_status,
        #                                         dbl_indirect_discount_amount = dct_old_item[int_id]['data'].get('dblIndirectDis'),
        #                                         dat_sale = datetime.now(),
        #                                         #LG
        #                                         dbl_cost_price = dct_old_item[int_id]['data']['dbl_cost_amnt'],
        #                                         dbl_dealer_price  = dct_old_item[int_id]['data']['dbl_dealer_amnt'],
        #                                         dbl_mop_price = dct_old_item[int_id]['data']['dbl_mop_amnt'],
        #                                         dbl_myg_price = dct_old_item[int_id]['data']['dbl_myg_amnt'],
        #                                         dbl_mrp_price = dct_old_item[int_id]['data']['dbl_mrp_amnt'],
        #
        #                                         dbl_tax = dct_old_item[int_id]['data']['dbl_tax'],
        #                                         json_tax = dct_old_item[int_id]['data']['json_tax']
        #                                         )
        #
        #
        #             else:
        #                 ins_item_enq.update(dbl_buy_back_amount = dct_old_item[int_id]['data']['dblBuyBack'],
        #                                         dbl_discount_amount = dct_old_item[int_id]['data']['dblDiscount'],
        #                                         dbl_amount = dct_old_item[int_id]['data']['dblAmount']+dct_old_item[int_id]['data']['dblDiscount']+dct_old_item[int_id]['data']['dblBuyBack'],
        #                                         dbl_imei_json = {'imei' : dct_old_item[int_id]['data']['jsonImei']},
        #                                         int_sold = dct_old_item[int_id]['data']['intQuantity'],
        #                                         dbl_sup_amount = dct_old_item[int_id]['data']['dbl_supp_amnt'],
        #                                         vchr_remarks = str_remark,
        #                                         vchr_enquiry_status = str_status,
        #                                         dbl_indirect_discount_amount = dct_old_item[int_id]['data'].get('dblIndirectDis'),
        #                                         dat_sale = datetime.now(),
        #                                         #LG
        #                                         dbl_cost_price = dct_old_item[int_id]['data']['dbl_cost_amnt'],
        #                                         dbl_dealer_price  = dct_old_item[int_id]['data']['dbl_dealer_amnt'],
        #                                         dbl_mop_price = dct_old_item[int_id]['data']['dbl_mop_amnt'],
        #                                         dbl_myg_price = dct_old_item[int_id]['data']['dbl_myg_amnt'],
        #                                         dbl_mrp_price = dct_old_item[int_id]['data']['dbl_mrp_amnt'],
        #
        #                                         dbl_tax = dct_old_item[int_id]['data']['dbl_tax'],
        #                                         json_tax = dct_old_item[int_id]['data']['json_tax']
        #                                         )
        #
        #
        #             ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = dct_old_item[int_id]['data']['itemEnqId'],
        #                                                   vchr_notes = str_status,
        #                                                   vchr_enquiry_status = str_status,
        #                                                   int_status = 1,
        #                                                   dbl_amount = dct_old_item[int_id]['data']['dblAmount']+dct_old_item[int_id]['data']['dblBuyBack']+dct_old_item[int_id]['data']['dblDiscount'],
        #                                                   fk_user_id = ins_user_id,
        #                                                   int_quantity = dct_old_item[int_id]['data']['intQuantity'],
        #                                                   fk_updated_id = ins_user_id,
        #                                                   dat_followup = datetime.now(),
        #                                                   dat_updated = datetime.now())
        #
        #
        #         # To add new item enquiry
        #         for int_id in dct_new_item:
        #             # New item invoiced in POS
        #             # dct_new_item[int_id]['data']['dblAmount'] = '25000'
        #             # int_type = '1'
        #             # int_type = '2'
        #
        #             # 
        #             if dct_new_item[int_id]['data']['status'] == 1:
        #
        #                 rst_data = Items.objects.values('vchr_item_name').filter(id = dct_item_code_details[int_id]['id'],vchr_item_name__in = ['GDOT','GDEW']).first()
        #                 int_type_gdp = ""
        #                 dbl_actual_gdew = 0
        #                 if rst_data:
        #                     if rst_data['vchr_item_name'] =="GDOT":
        #                         int_type_gdp = '1'
        #                     elif rst_data['vchr_item_name'] == 'GDEW':
        #                         int_type_gdp = '2'
        #
        #                     if int_type_gdp:
        #                         obj_gdp_range = GDPRange.objects.filter(dbl_from__lte=dct_new_item[int_id]['data']['dblAmount'],dbl_to__gte=dct_new_item[int_id]['data']['dblAmount'],int_type=int_type_gdp).values('dbl_amt')
        #                         dbl_actual_gdew = obj_gdp_range[0]['dbl_amt']
        #                 else:
        #                     rst_data = Items.objects.values('vchr_item_name').filter(id = dct_item_code_details[int_id]['id']).values('dbl_apx_amount')
        #                     dbl_actual_gdew = rst_data[0]['dbl_apx_amount'] if rst_data else 0
        #
        #                 ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
        #                                             fk_item_id = dct_item_code_details[int_id]['id'],
        #                                             dbl_buy_back_amount = dct_new_item[int_id]['data']['dblBuyBack'],
        #                                             dbl_discount_amount = dct_new_item[int_id]['data']['dblDiscount'],
        #                                             dbl_amount = dct_new_item[int_id]['data']['dblAmount']+dct_new_item[int_id]['data']['dblBuyBack']+dct_new_item[int_id]['data']['dblDiscount'],
        #                                             # dbl_imei_json = dct_new_item[int_id]['data']['jsonImei'],
        #                                             dbl_imei_json = {'imei' : dct_new_item[int_id]['data']['jsonImei']},
        #                                             int_quantity = dct_new_item[int_id]['data']['intQuantity'],
        #                                             int_sold = dct_new_item[int_id]['data']['intQuantity'],
        #                                             fk_product_id = dct_item_code_details[dct_new_item[int_id]['data']['strItemCode']]['fk_product_id'],
        #                                             fk_brand_id =  dct_item_code_details[dct_new_item[int_id]['data']['strItemCode']]['fk_brand_id'],
        #                                             vchr_enquiry_status = str_status,
        #                                             dbl_actual_est_amt = dbl_actual_gdew,
        #                                             dbl_sup_amount = dct_new_item[int_id]['data']['dbl_supp_amnt'],
        #                                             dat_sale = datetime.now(),
        #                                             vchr_remarks = str_remark,
        #                                             #LG
        #                                             dbl_cost_price = dct_new_item[int_id]['data']['dbl_cost_amnt'],
        #                                             dbl_dealer_price  = dct_new_item[int_id]['data']['dbl_dealer_amnt'],
        #                                             dbl_mop_price = dct_new_item[int_id]['data']['dbl_mop_amnt'],
        #                                             dbl_myg_price = dct_new_item[int_id]['data']['dbl_myg_amnt'],
        #                                             dbl_mrp_price = dct_new_item[int_id]['data']['dbl_mrp_amnt'],
        #
        #                                             dbl_tax = dct_new_item[int_id]['data']['dbl_tax'],
        #                                             json_tax = dct_new_item[int_id]['data']['json_tax']
        #                                             )
        #                 ins_item_enq.save()
        #
        #                 ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
        #                                                     vchr_notes =str_status,
        #                                                     vchr_enquiry_status = str_status,
        #                                                     int_status = 1,
        #                                                     dbl_amount = dct_new_item[int_id]['data']['dblAmount']+dct_new_item[int_id]['data']['dblBuyBack']+dct_new_item[int_id]['data']['dblDiscount'],
        #                                                     fk_user_id = ins_user_id,
        #                                                     int_quantity = dct_new_item[int_id]['data']['intQuantity'],
        #                                                     fk_updated_id = ins_user_id,
        #                                                     dat_followup = datetime.now(),
        #                                                     dat_updated = datetime.now())
        #
        #             # New Item returned from POS
        #             if dct_new_item[int_id]['data']['status'] == 0:
        #                 ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
        #                                             fk_item_id = dct_item_code_details[dct_new_item[int_id]['data']['strItemCode']]['id'],
        #                                             dbl_buy_back_amount = dct_new_item[int_id]['data']['dblBuyBack'],
        #                                             dbl_discount_amount = dct_new_item[int_id]['data']['dblDiscount'],
        #                                             dbl_amount = dct_new_item[int_id]['data']['dblAmount']+dct_new_item[int_id]['data']['dblBuyBack']+dct_new_item[int_id]['data']['dblDiscount'],
        #                                             dbl_imei_json = {'imei' : dct_new_item[int_id]['data']['jsonImei']},
        #                                             # dbl_imei_json = dct_new_item[int_id]['data']['jsonImei'],
        #                                             int_quantity = dct_new_item[int_id]['data']['intQuantity'],
        #                                             int_sold = dct_new_item[int_id]['data']['intQuantity'],
        #                                             fk_product_id = dct_item_code_details[dct_new_item[int_id]['data']['strItemCode']]['fk_product_id'],
        #                                             fk_brand_id =  dct_item_code_details[dct_new_item[int_id]['data']['strItemCode']]['fk_brand_id'],
        #                                             dbl_actual_est_amt = dct_new_item[int_id]['data']['apx_amount'],
        #                                             vchr_remarks = str_remark,
        #                                             vchr_enquiry_status = 'RETURNED',
        #                                             dbl_sup_amount = dct_new_item[int_id]['data']['dbl_supp_amnt'],
        #                                             dat_sale = datetime.now(),
        #                                             #LG
        #                                             dbl_cost_price = dct_new_item[int_id]['data']['dbl_cost_amnt'],
        #                                             dbl_dealer_price  = dct_new_item[int_id]['data']['dbl_dealer_amnt'],
        #                                             dbl_mop_price = dct_new_item[int_id]['data']['dbl_mop_amnt'],
        #                                             dbl_myg_price = dct_new_item[int_id]['data']['dbl_myg_amnt'],
        #                                             dbl_mrp_price = dct_new_item[int_id]['data']['dbl_mrp_amnt'],
        #
        #                                             dbl_tax = dct_new_item[int_id]['data']['dbl_tax'],
        #                                             json_tax = dct_new_item[int_id]['data']['json_tax']
        #                                             )
        #                 ins_item_enq.save()
        #                 ins_enquiry_master=EnquiryMaster.objects.get(pk_bint_id=int_enq_master_id)
        #
        #
        #                 ins_item_enquiry_return=ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id=ins_enquiry_master.fk_customer_id,dbl_imei_json__contains={'imei':dct_new_item[int_id]['data']['jsonImei']})
        #                 if ins_item_enquiry_return:
        #                     ins_avaialble=RewardsAvailable.objects.filter(fk_item_enquiry_id=ins_item_enquiry_return[0].pk_bint_id).values()
        #                     if ins_avaialble:
        #                         for data in ins_avaialble:
        #                             RewardsAvailable.objects.create(fk_rewards_master_id=data['fk_rewards_master_id'],fk_rewards_details_id=data['fk_rewards_details_id'],fk_item_enquiry_id=data['fk_item_enquiry_id'],dat_reward=datetime.now(),dbl_mop_amount=data['dbl_mop_amount'],json_staff={dct_rwd_data:-data['json_staff'][dct_rwd_data] for dct_rwd_data in data['json_staff']})
        #
        #
        #                 ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
        #                                                   vchr_notes = 'RETURNED',
        #                                                   vchr_enquiry_status = 'RETURNED',
        #                                                   int_status = 1,
        #                                                   dbl_amount = dct_new_item[int_id]['data']['dblAmount']+dct_new_item[int_id]['data']['dblBuyBack']+dct_new_item[int_id]['data']['dblDiscount'],
        #                                                   fk_user_id = ins_user_id,
        #                                                   int_quantity = dct_new_item[int_id]['data']['intQuantity'],
        #                                                   fk_updated_id = ins_user_id,
        #                                                   dat_followup = datetime.now(),
        #                                                   dat_updated = datetime.now())
        #
        #         lst_deleted_item = list(set(lst_item_code_cur_all)-set(lst_old_item))
        #         # Lost item enquiries which are deleted from POS
        #         for int_enq_id in lst_dlt_item_code:
        #             ins_item_enq=ItemEnquiry.objects.filter(pk_bint_id =  int_enq_id)
        #             ins_item_enq.update(vchr_enquiry_status = 'LOST')
        #             ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = int_enq_id,
        #                                                 vchr_notes = 'LOST',
        #                                                 vchr_enquiry_status = 'LOST',
        #                                                 int_status = 1,
        #                                                 dbl_amount = ins_item_enq[0].dbl_amount,
        #                                                 fk_user_id = ins_user_id,
        #                                                 int_quantity = ins_item_enq[0].int_quantity,
        #                                                 fk_updated_id = ins_user_id,
        #                                                 dat_followup = datetime.now(),
        #                                                 dat_updated = datetime.now())
        #
        #
        #         for ins_data in dct_item_data:
        #             if dct_item_data[ins_data]['int_type']==1 or dct_item_data[ins_data]['int_type']==2:
        #                 ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[ins_data]['jsonImei']})|Q(dbl_imei_json__contains=dct_item_data[ins_data]['jsonImei']),fk_enquiry_master_id=int_enq_master_id).values('fk_item__dbl_apx_amount','int_type','int_quantity').exclude(fk_product__vchr_product_name='SERVICE').first()
        #                 gdp_value=GDPRange.objects.filter(dbl_from__lte=(ins_up_item_enq['fk_item__dbl_apx_amount']*ins_up_item_enq['int_quantity']),dbl_to__gte=(ins_up_item_enq['fk_item__dbl_apx_amount']*ins_up_item_enq['int_quantity']),int_type=dct_item_data[ins_data]['int_type']).values('dbl_amt').first()
        #                 if ins_up_item_enq['int_type']!=0:
        #                     if ins_up_item_enq['int_type']!=dct_item_data[ins_data]['int_type']:
        #                         ins_up_item_enq.update(int_type=3)
        #                 else:
        #                     ins_up_item_enq.update(int_type=dct_item_data[ins_data]['int_type'])
        #                 if dct_item_data[ins_data]['int_type']==1:
        #                     ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[ins_data]['jsonImei']})|Q(dbl_imei_json__contains=dct_item_data[ins_data]['jsonImei']),fk_item__vchr_item_name='GDP',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value['dbl_amt'])
        #                 if dct_item_data[ins_data]['int_type']==2:
        #                     ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[ins_data]['jsonImei']})|Q(dbl_imei_json__contains=dct_item_data[ins_data]['jsonImei']),fk_item__vchr_item_name='GDEW (EXTENDED WARRANTY)',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value['dbl_amt'])
        #
        #                     # ==============================================================New Block of Code with enquiry id ================================================================================================
        #
        #
        #
        #
        #
        #
        #                     # =========================================================new code will substitute the following block of code =====================================================
        #
        #         #creating dictionary with item code as keys and  'fk_product_id','fk_brand_id','vchr_item_code','pk_bint_id' as values
        #
        #         # for ins_data in dct_item_data:
        #         #         apx_amount = Items.objects.filter(vchr_item_code=dct_item_data[ins_data]['strItemCode']).values('dbl_apx_amount').order_by('-id').first()['dbl_apx_amount']
        #         #         # if dct_item_data[ins_data]['strItemCode'] not in lst_dlt_item_code and dct_item_data[ins_data]['strItemCode'] not in  lst_new_item_code:
        #         #         #vchr_item_code which are already in database
        #         #         ins_item_enq = ItemEnquiry.objects.filter(fk_item__vchr_item_code =  dct_item_data[ins_data]['strItemCode'],fk_enquiry_master = int_enq_master_id)
        #         #         ins_product = ins_item_enq.values('fk_product__vchr_product_name')[0]['fk_product__vchr_product_name']
        #         #         if ins_product.upper() != 'SERVICE':
        #         #             ins_item_enq.update(dbl_actual_est_amt = apx_amount)
        #         #
        #         #         ins_item_enq.update(dbl_buy_back_amount = dct_item_data[ins_data]['dblBuyBack'],
        #         #                             dbl_discount_amount = dct_item_data[ins_data]['dblDiscount'],
        #         #                             # dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #         #                             # dbl_imei_json = dct_item_data[ins_data]['jsonImei'],
        #         #                             dbl_imei_json = {'imei' : dct_item_data[ins_data]['jsonImei']},
        #         #                             int_sold = dct_item_data[ins_data]['intQuantity'],
        #         #                             dbl_sup_amount = dct_item_data[ins_data]['dbl_supp_amnt'],
        #         #                             vchr_remarks = str_remark,
        #         #                             vchr_enquiry_status = str_status,
        #         #                             dat_sale = datetime.now()
        #         #                                                             )
        #         #         ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.first().pk_bint_id,
        #         #                                           vchr_notes = str_status,
        #         #                                           vchr_enquiry_status = str_status,
        #         #                                           int_status = 1,
        #         #                                           dbl_amount = dct_item_data[ins_data]['dblAmount']+dct_item_data[ins_data]['dblBuyBack']+dct_item_data[ins_data]['dblDiscount'],
        #         #                                           fk_user_id = ins_user_id,
        #         #                                           int_quantity = dct_item_data[ins_data]['intQuantity'],
        #         #                                           fk_updated_id = ins_user_id,
        #         #                                           dat_followup = datetime.now(),
        #         #                                           dat_updated = datetime.now())
        #         #
        #         #         #
        #         #     if dct_item_data[ins_data]['strItemCode'] in lst_new_item_code:
        #         #         #vchr_item_code which are newly added
        #         #         #if intstatus=1 itemenquiry : vchr_enquiry_status = INVOICED
        #         #         #if intstatus=0 itemenquiry : vchr_enquiry_status = RETURNED
        #         #         if dct_item_data[ins_data]['status'] == 1:
        #         #             ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
        #         #                                         fk_item_id = dct_item_code_details[dct_item_data[ins_data]['strItemCode']]['id'],
        #         #                                         dbl_buy_back_amount = dct_item_data[ins_data]['dblBuyBack'],
        #         #                                         dbl_discount_amount = dct_item_data[ins_data]['dblDiscount'],
        #         #                                         dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #         #                                         # dbl_imei_json = dct_item_data[ins_data]['jsonImei'],
        #         #                                         dbl_imei_json = {'imei' : dct_item_data[ins_data]['jsonImei']},
        #         #                                         int_quantity = dct_item_data[ins_data]['intQuantity'],
        #         #                                         int_sold = dct_item_data[ins_data]['intQuantity'],
        #         #                                         fk_product_id = dct_item_code_details[dct_item_data[ins_data]['strItemCode']]['fk_product_id'],
        #         #                                         fk_brand_id =  dct_item_code_details[dct_item_data[ins_data]['strItemCode']]['fk_brand_id'],
        #         #                                         vchr_enquiry_status = str_status,
        #         #                                         dbl_actual_est_amt = apx_amount,
        #         #                                         dbl_sup_amount = dct_item_data[ins_data]['dbl_supp_amnt'],
        #         #                                         dat_sale = datetime.now(),
        #         #                                         vchr_remarks = str_remark,
        #         #                                                                         )
        #         #             ins_item_enq.save()
        #         #
        #         #             ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
        #         #                                                 vchr_notes =str_status,
        #         #                                                 vchr_enquiry_status = str_status,
        #         #                                                 int_status = 1,
        #         #                                                 dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #         #                                                 fk_user_id = ins_user_id,
        #         #                                                 int_quantity = dct_item_data[ins_data]['intQuantity'],
        #         #                                                 fk_updated_id = ins_user_id,
        #         #                                                 dat_followup = datetime.now(),
        #         #                                                 dat_updated = datetime.now())
        #         #         if dct_item_data[ins_data]['status'] == 0:
        #         #             ins_item_enq = ItemEnquiry(fk_enquiry_master_id = int_enq_master_id,
        #         #                                         fk_item_id = dct_item_code_details[dct_item_data[ins_data]['strItemCode']]['id'],
        #         #                                         dbl_buy_back_amount = dct_item_data[ins_data]['dblBuyBack'],
        #         #                                         dbl_discount_amount = dct_item_data[ins_data]['dblDiscount'],
        #         #                                         dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #         #                                         dbl_imei_json = {'imei' : dct_item_data[ins_data]['jsonImei']},
        #         #                                         # dbl_imei_json = dct_item_data[ins_data]['jsonImei'],
        #         #                                         int_quantity = dct_item_data[ins_data]['intQuantity'],
        #         #                                         int_sold = dct_item_data[ins_data]['intQuantity'],
        #         #                                         fk_product_id = dct_item_code_details[dct_item_data[ins_data]['strItemCode']]['fk_product_id'],
        #         #                                         fk_brand_id =  dct_item_code_details[dct_item_data[ins_data]['strItemCode']]['fk_brand_id'],
        #         #                                         dbl_actual_est_amt = apx_amount,
        #         #                                         vchr_remarks = str_remark,
        #         #                                         vchr_enquiry_status = 'RETURNED',
        #         #                                         dbl_sup_amount = dct_item_data[ins_data]['dbl_supp_amnt'],
        #         #                                         dat_sale = datetime.now()
        #         #                                                                         )
        #         #             ins_item_enq.save()
        #         #
        #         #             ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq.pk_bint_id,
        #         #                                               vchr_notes = 'RETURNED',
        #         #                                               vchr_enquiry_status = 'RETURNED',
        #         #                                               int_status = 1,
        #         #                                               dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #         #                                               fk_user_id = ins_user_id,
        #         #                                               int_quantity = dct_item_data[ins_data]['intQuantity'],
        #         #                                               fk_updated_id = ins_user_id,
        #         #                                               dat_followup = datetime.now(),
        #         #                                               dat_updated = datetime.now())
        #
        #
        #
        #             # if dct_item_data[ins_data]['strItemCode'] in lst_dlt_item_code:
        #             #     #vchr_item_code which are deleted
        #             #     ins_item_enq=ItemEnquiry.objects.filter(fk_enquiry_master = int_enq_master_id,fk_item__vchr_item_code =  dct_item_data[ins_data]['strItemCode'])
        #             #     # ins_service_item = ins_item_enq.values('fk_item__vchr_name','dbl_json_imei')
        #             #     # if ins_service_item[0]['fk_item__vchr_name'] == 'GDP':
        #
        #             #     ins_item_enq.update(vchr_enquiry_status = 'LOST')
        #
        #             #     ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq[0].pk_bint_id,
        #             #                                       vchr_notes = 'LOST',
        #             #                                       vchr_enquiry_status = 'LOST',
        #             #                                       int_status = 1,
        #             #                                       dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #             #                                       fk_user_id = ins_user_id,
        #             #                                       int_quantity = dct_item_data[ins_data]['intQuantity'],
        #             #                                       fk_updated_id = ins_user_id,
        #             #                                       dat_followup = datetime.now(),
        #             #                                       dat_updated = datetime.now())
        #
        #
        #         # for str_item_code in lst_dlt_item_code:
        #         #     ins_item_enq=ItemEnquiry.objects.filter(fk_enquiry_master = int_enq_master_id,fk_item__vchr_item_code =  str_item_code)
        #         #         # ins_service_item = ins_item_enq.values('fk_item__vchr_name','dbl_json_imei')
        #         #         # if ins_service_item[0]['fk_item__vchr_name'] == 'GDP':
        #         #
        #         #     ins_item_enq.update(vchr_enquiry_status = 'LOST')
        #         #
        #         #     ins_follow_up = ItemFollowup.objects.create(fk_item_enquiry_id = ins_item_enq[0].pk_bint_id,
        #         #                                         vchr_notes = 'LOST',
        #         #                                         vchr_enquiry_status = 'LOST',
        #         #                                         int_status = 1,
        #         #                                         dbl_amount = dct_item_data[ins_data]['dblAmount'],
        #         #                                         fk_user_id = ins_user_id,
        #         #                                         int_quantity = dct_item_data[ins_data]['intQuantity'],
        #         #                                         fk_updated_id = ins_user_id,
        #         #                                         dat_followup = datetime.now(),
        #         #                                         dat_updated = datetime.now())
        #
        #         # for ins_data in dct_item_data:
        #         #     if dct_item_data[ins_data]['int_type']==1 or dct_item_data[ins_data]['int_type']==2:
        #         #         ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[ins_data]['jsonImei']})|Q(dbl_imei_json__contains=dct_item_data[ins_data]['jsonImei']),fk_enquiry_master_id=int_enq_master_id).values('fk_item__dbl_apx_amount','int_type','int_quantity').exclude(fk_product__vchr_product_name='SERVICE').first()
        #         #         gdp_value=GDPRange.objects.filter(dbl_from__lte=(ins_up_item_enq['fk_item__dbl_apx_amount']*ins_up_item_enq['int_quantity']),dbl_to__gte=(ins_up_item_enq['fk_item__dbl_apx_amount']*ins_up_item_enq['int_quantity']),int_type=dct_item_data[ins_data]['int_type']).values('dbl_amt').first()
        #         #         if ins_up_item_enq['int_type']!=0:
        #         #             if ins_up_item_enq['int_type']!=dct_item_data[ins_data]['int_type']:
        #         #                 ins_up_item_enq.update(int_type=3)
        #         #         else:
        #         #             ins_up_item_enq.update(int_type=dct_item_data[ins_data]['int_type'])
        #         #         if dct_item_data[ins_data]['int_type']==1:
        #         #             ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[ins_data]['jsonImei']})|Q(dbl_imei_json__contains=dct_item_data[ins_data]['jsonImei']),fk_item__vchr_item_name='GDP',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value['dbl_amt'])
        #         #         if dct_item_data[ins_data]['int_type']==2:
        #         #             ins_up_item_enq=ItemEnquiry.objects.filter(Q(dbl_imei_json__contains={'imei':dct_item_data[ins_data]['jsonImei']})|Q(dbl_imei_json__contains=dct_item_data[ins_data]['jsonImei']),fk_item__vchr_item_name='GDEW (EXTENDED WARRANTY)',fk_enquiry_master_id=int_enq_master_id).update(dbl_actual_est_amt=gdp_value['dbl_amt'])
        #
        #         # ======================================================new code will substitute the above block of code =======================================
        #     special_rewards(int_enq_master_id)
        #
        #
        #     return Response({'status':'success'})
        # except Exception as e:
        #     ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
        #     return JsonResponse({'status':'failed','message':str(e)})


def special_rewards_script_sudheesh(str_pk_id):
    try:
        # enquiry_num
        # 
        with transaction.atomic():
            int_eq_pk_bint_id=int(str_pk_id)
            user_id = EnquiryMaster.objects.get(pk_bint_id = int_eq_pk_bint_id).fk_assigned_id
            user_instance = UserModel.objects.get(user_ptr_id = user_id)

            lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master__pk_bint_id = int_eq_pk_bint_id,vchr_enquiry_status='INVOICED').\
            values('pk_bint_id','fk_item_id','dat_sale','fk_item__vchr_item_name','fk_item__fk_item_group_id','fk_item__vchr_item_code','fk_item__fk_product_id','fk_enquiry_master__dat_created_at','fk_item__fk_product__vchr_product_name','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_actual_est_amt','dbl_discount_amount',\
            'dbl_buy_back_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew').exclude(Q(fk_brand__vchr_brand_name__iexact = 'apple',fk_product__vchr_product_name__in =['HVA','ACC BGN']) | Q(fk_brand__vchr_brand_name__iexact = 'xiaomi',fk_product__vchr_product_name__in =['HVA','ACC BGN']) |\
             Q(fk_brand__vchr_brand_name__iexact = 'redmi',fk_product__vchr_product_name__in =['HVA','ACC BGN']) | Q(fk_brand__vchr_brand_name__iexact = 'sandisk',fk_product__vchr_product_name__in =['HVA','ACC BGN'])| Q(fk_item__vchr_item_name__iexact = 'F120B JIO DIGITAL LIFE') | Q(fk_product__vchr_product_name__iexact ='SMART CHOICE'))

            if not lst_item_enquiry_all:
                return JsonResponse({'status':'success'})

            int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],is_active=True).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()

            lst_available=[int_promoter['promo'],1]
            if not UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF',is_active=True).values():
                lst_available.pop(0)


            product_total_qty={}
            item_amount={}


            for data in lst_item_enquiry_all:
                # if data['']
                data['fk_enquiry_master__dat_created_at'] = data['dat_sale'] # due to date create issue and reward change
                lst_available=[]
                if not int_promoter['fk_brand_id']:
                    lst_available=[3,1]
                elif data['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                    lst_available=[3,1]
                elif int_promoter['fk_brand_id']==data['fk_item__fk_brand_id']:
                    lst_available=[2,1]


                """value wise rewards"""
                """map type product value"""
                total_reward=0

                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 14,fk_reward_details__int_map_id = data['fk_item__fk_item_group_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")
                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                            if not data['dbl_actual_est_amt'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)

                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward


                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                    if json_staffs:
                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()

                """value wise rewards"""
                """map type product value"""

                total_reward=0

                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")
                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                            if not data['dbl_actual_est_amt'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)

                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward


                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                    if json_staffs:
                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


                """map type brand value"""
                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 6,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                            if not data['dbl_actual_est_amt'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100)* item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


                """map type item value"""
                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 7,fk_reward_details__int_map_id = data['fk_item_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                            if not data['dbl_actual_est_amt'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward




                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


                # """GDP value"""
                #
                # if data['int_type'] in [1,3]:
                #     int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']
                #
                #
                #     total_reward=0
                #     # item_amount['dbl_apx_amount']=0
                #
                #     item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                #     fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                #     'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                #     'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")
                #
                #     if item_data_all:
                #         json_staffs = {}
                #         int_branch_manager = 0
                #         int_ast_manager = 0
                #         for item_data in item_data_all:
                #             total_reward=0
                #             if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                #                 if not data['dbl_actual_gdp'] :
                #                     pass
                #                 else:
                #                     """slab1"""
                #                     if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp']) * 100:
                #                         if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_percentage']:
                #                             reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #                         """slab2"""
                #                     elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp'])  * 100:
                #                         if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                #                             reward = item_data['dbl_slab2_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                #                         elif item_data['dbl_slab2_percentage']:
                #                             reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                #                         elif item_data['dbl_slab2_amount']:
                #                             reward = item_data['dbl_slab2_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #                         """slab3"""
                #                     elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp']) * 100:
                #                         if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                #                             reward = item_data['dbl_slab3_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100 )* item_data['dbl_slab3_percentage']
                #                         elif item_data['dbl_slab3_percentage']:
                #                             reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                #                         elif item_data['dbl_slab3_amount']:
                #                             reward = item_data['dbl_slab3_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #             if total_reward:
                #                 total_reward = round(total_reward,2)
                #                 if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():
                #
                #                     int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                #                     str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                #                     str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                #
                #                     if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                #                         #non-promoter
                #                         if (item_data['int_to'] == 3) and (3 in lst_available):
                #                             json_staffs[int_assign_id] = total_reward
                #                         #all
                #                         elif item_data['int_to'] == 1:
                #                             json_staffs[int_assign_id] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM4':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'B TEAM':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #
                #
                #
                #         if json_staffs:
                #
                #             ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                #             ins_item_reward.save()
                #
                #
                # """GDEW value"""
                # if data['int_type'] in [2,3]:
                #     int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                #
                #     total_reward=0
                #     # item_amount['dbl_apx_amount']=0
                #
                #     item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                #     fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                #     'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                #     'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")
                #
                #     if item_data_all:
                #         json_staffs = {}
                #         int_branch_manager = 0
                #         int_ast_manager = 0
                #         for item_data in item_data_all:
                #             total_reward=0
                #             if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                #                 if not data['dbl_actual_gdew'] :
                #                     pass
                #                 else:
                #                     """slab1"""
                #                     if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                #                         if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_percentage']:
                #                             reward = ((data['dbl_gdew_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #                         """slab2"""
                #                     elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                #                         if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                #                             reward = item_data['dbl_slab2_amount'] if ((data['dbl_gdew_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                #                         elif item_data['dbl_slab2_percentage']:
                #                             reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                #                         elif item_data['dbl_slab2_amount']:
                #                             reward = item_data['dbl_slab2_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #                         """slab3"""
                #                     elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                #                         if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                #                             reward = item_data['dbl_slab3_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                #                         elif item_data['dbl_slab3_percentage']:
                #                             reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                #                         elif item_data['dbl_slab3_amount']:
                #                             reward = item_data['dbl_slab3_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #             if total_reward:
                #                 total_reward = round(total_reward,2)
                #                 if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():
                #
                #                     int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                #                     str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                #                     str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                #
                #                     if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                #                         #non-promoter
                #                         if (item_data['int_to'] == 3) and (3 in lst_available):
                #                             json_staffs[int_assign_id] = total_reward
                #                         #all
                #                         elif item_data['int_to'] == 1:
                #                             json_staffs[int_assign_id] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM4':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'B TEAM':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #
                #
                #
                #         if json_staffs:
                #
                #             ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                #             ins_item_reward.save()

                # ===========================================================================================================================================================================================================================================================================================================================================================================================================
                """price band wise rewards"""


                """map type product price"""
                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
                fk_reward_details__dbl_value_to__gte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
                fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                            if not data['dbl_actual_est_amt']:
                                pass
                            elif data['dbl_actual_est_amt'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 )* item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'].upper() == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward


                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


                """map type brand"""
                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
                fk_reward_details__dbl_value_to__gte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
                fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 9,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                            if not data['dbl_actual_est_amt'] :
                                pass
                            elif data['dbl_actual_est_amt'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()

                # """GDP price"""
                #
                # if data['int_type'] in [1,3]:
                #     int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']
                #
                #
                #     total_reward=0
                #     # item_amount['dbl_apx_amount']=0
                #
                #     item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_gdp_amount']) / data['int_sold']),\
                #     fk_reward_details__dbl_value_to__gte = ((data['dbl_gdp_amount']) / data['int_sold']),\
                #     fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                #     fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                #     'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")
                #
                #     if item_data_all:
                #         json_staffs = {}
                #         int_branch_manager = 0
                #         int_ast_manager = 0
                #         for item_data in item_data_all:
                #             total_reward=0
                #             if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                #                 if not data['dbl_actual_gdp'] :
                #                     pass
                #                 elif data['dbl_actual_gdp'] <= ((data['dbl_gdp_amount']) / data['int_sold']):
                #                     """slab1"""
                #                     if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_gdp_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_gdp_amount']) / data['int_sold']):
                #                         if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_percentage']:
                #                             reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #             if total_reward:
                #                 total_reward = round(total_reward,2)
                #                 if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():
                #
                #                     int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                #                     str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                #                     str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                #
                #                     if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                #                         #non-promoter
                #                         if (item_data['int_to'] == 3) and (3 in lst_available):
                #                             json_staffs[int_assign_id] = total_reward
                #                         #all
                #                         elif item_data['int_to'] == 1:
                #                             json_staffs[int_assign_id] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM4':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'B TEAM':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #
                #
                #
                #         if json_staffs:
                #
                #             ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                #             ins_item_reward.save()
                #
                #
                # """GDEW price"""
                # if data['int_type'] in [2,3]:
                #     int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']
                #
                #     total_reward=0
                #     # item_amount['dbl_apx_amount']=0
                #
                #     item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_gdew_amount']) / data['int_sold']),\
                #     fk_reward_details__dbl_value_to__gte = ((data['dbl_gdew_amount']) / data['int_sold']),\
                #     fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                #     fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                #     'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")
                #
                #     if item_data_all:
                #         json_staffs = {}
                #         int_branch_manager = 0
                #         int_ast_manager = 0
                #         for item_data in item_data_all:
                #             total_reward=0
                #             if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                #                 if not data['dbl_actual_gdew'] :
                #                     pass
                #                 elif data['dbl_actual_gdew'] <= ((data['dbl_gdew_amount']) / data['int_sold']):
                #                     """slab1"""
                #                     if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_gdew_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_gdew_amount']) / data['int_sold']):
                #                         if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_percentage']:
                #                             reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                #                         elif item_data['dbl_slab1_amount']:
                #                             reward = item_data['dbl_slab1_amount']
                #                         total_reward += reward * data ['int_sold']
                #
                #
                #             if total_reward:
                #                 total_reward = round(total_reward,2)
                #                 if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():
                #
                #                     int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                #                     str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                #                     str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                #
                #                     if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                #                         #non-promoter
                #                         if (item_data['int_to'] == 3) and (3 in lst_available):
                #                             json_staffs[int_assign_id] = total_reward
                #                         #all
                #                         elif item_data['int_to'] == 1:
                #                             json_staffs[int_assign_id] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'].upper() == 'FLOOR MANAGER1':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM4':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM3':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'ASM2':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #
                #                     elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                #                         if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                             int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                #                     elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                #                         if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #                     elif item_data['fk_group__vchr_name'] == 'B TEAM':
                #                         if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                #                             json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                #
                #
                #
                #         if json_staffs:
                #
                #             ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                #             ins_item_reward.save()


            # ===========================================================================================================================================================================================================================================================================================================================================================================================


        return "Success"
    except Exception as e:
        data = str(e)
        return data





class BookCreditEnquiry(APIView):
    """
    setting Enquiry status as booked for credit purchases
    """
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        try:
            with transaction.atomic():
                int_item_enq_id = request.data.get('intItemEnqId')

                ItemEnquiry.objects.filter(fk_enquiry_master_id=int_item_enq_id).update(vchr_enquiry_status='BOOKED')

                int_customer_id=EnquiryMaster.objects.filter(pk_bint_id=int_item_enq_id).values_list('fk_customer_id',flat=True)[0]
                # int_enquiry_master_id =ItemEnquiry.objects.filter(pk_bint_id=int_item_enq_id).values_list('fk_enquiry_master_id',flat=True)[0]

                ins_item_enq =  ItemEnquiry.objects.filter(fk_enquiry_master_id=int_item_enq_id).values('dbl_amount','dbl_discount_amount','fk_item__vchr_item_name','fk_item__vchr_item_code','dbl_imei_json','int_quantity','dbl_amount','dbl_discount_amount','dbl_buy_back_amount','vchr_remarks')

                # ----------- POS ------------
                ins_customer = CustomerModel.objects.filter(id = int_customer_id).first()
                ins_enq_master = EnquiryMaster.objects.filter(pk_bint_id=int_item_enq_id).first()
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
                dct_pos_data['str_remarks'] = ins_enq_master.vchr_remarks
                dct_pos_data['dat_enquiry'] = ins_enq_master.dat_created_at.strftime('%Y-%m-%d')
                dct_pos_data['dct_products'] = {}
                dct_pos_data['lst_item'] = []
                dct_pos_data['dbl_total_amt'] = 0
                dct_pos_data['dbl_discount'] = 0
                # 

                for ins_item in ins_item_enq:
                    dct_item = {}
                    dct_pos_data['dbl_total_amt'] += ins_item['dbl_amount']
                    dct_pos_data['dbl_discount'] += ins_item['dbl_discount_amount']
                    dct_item['vchr_item_name'] = ins_item['fk_item__vchr_item_name']
                    dct_item['vchr_item_code'] = ins_item['fk_item__vchr_item_code']
                    dct_item['json_imei'] = ins_item['dbl_imei_json']
                    dct_item['int_quantity'] = ins_item['int_quantity']
                    dct_item['dbl_amount'] = ins_item['dbl_amount']
                    dct_item['dbl_discount'] = ins_item['dbl_discount_amount']
                    dct_item['dbl_buyback'] = ins_item['dbl_buy_back_amount']
                    dct_item['vchr_remarks'] = ins_item['vchr_remarks']
                    dct_item['int_status'] = 1
                    dct_pos_data['lst_item'].append(dct_item)

                url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
                try:
                    res_data = requests.post(url,json=dct_pos_data)
                    if res_data.json().get('status')=='1':
                        pass
                    else:
                        return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                except Exception as e:
                    raise

                return Response({'status':1})
        except Exception as e:
            return Response({'status':'failed','message':str(e)})




# reward function
def special_rewards_script(str_pk_id):
    try:
        # enquiry_num
        int_eq_pk_bint_id=int(str_pk_id)
        user_id = EnquiryMaster.objects.get(pk_bint_id = int_eq_pk_bint_id).fk_assigned_id
        user_instance = UserModel.objects.get(user_ptr_id = user_id)

        lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master__pk_bint_id = int_eq_pk_bint_id,vchr_enquiry_status='INVOICED').\
        values('pk_bint_id','fk_item_id','fk_item__vchr_item_name','fk_item__vchr_item_code','fk_item__fk_product_id','fk_enquiry_master__dat_created_at','fk_item__fk_product__vchr_product_name','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_actual_est_amt','dbl_discount_amount',\
        'dbl_buy_back_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew').exclude(Q(fk_brand__vchr_brand_name__iexact = 'apple',fk_product__vchr_product_name__in =['HVA','ACC BGN']) | Q(fk_brand__vchr_brand_name__iexact = 'xiaomi',fk_product__vchr_product_name__in =['HVA','ACC BGN']) |\
         Q(fk_brand__vchr_brand_name__iexact = 'redmi',fk_product__vchr_product_name__in =['HVA','ACC BGN']) | Q(fk_brand__vchr_brand_name__iexact = 'sandisk',fk_product__vchr_product_name__in =['HVA','ACC BGN'])| Q(fk_item__vchr_item_name__iexact = 'F120B JIO DIGITAL LIFE') | Q(fk_product__vchr_product_name__iexact ='SMART CHOICE'))

        if not lst_item_enquiry_all:
            return JsonResponse({'status':'success'})

        int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],is_active=True).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()

        lst_available=[int_promoter['promo'],1]
        if not UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF',is_active=True).values():
            lst_available.pop(0)


        product_total_qty={}
        item_amount={}


        for data in lst_item_enquiry_all:
            # if data['']

            lst_available=[]
            if not int_promoter['fk_brand_id']:
                lst_available=[3,1]
            elif data['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                lst_available=[3,1]
            elif int_promoter['fk_brand_id']==data['fk_item__fk_brand_id']:
                lst_available=[2,1]

            """value wise rewards"""
            """map type product value"""
            total_reward=0

            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
            fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward


                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                if json_staffs:

                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                    ins_item_reward.save()


            """map type brand value"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
            fk_reward_details__int_map_type = 6,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100)* item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                if json_staffs:

                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                    ins_item_reward.save()


            """map type item value"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
            fk_reward_details__int_map_type = 7,fk_reward_details__int_map_id = data['fk_item_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward




                if json_staffs:

                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                    ins_item_reward.save()


            """GDP value"""

            if data['int_type'] in [1,3]:
                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']


                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdp'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp'])  * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100 )* item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


            """GDEW value"""
            if data['int_type'] in [2,3]:
                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']

                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdew'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = ((data['dbl_gdew_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if ((data['dbl_gdew_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()

# ===========================================================================================================================================================================================================================================================================================================================================================================================================
            """price band wise rewards"""
            # 

            """map type product price"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__dbl_value_to__gte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
            fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt']:
                            pass
                        elif data['dbl_actual_est_amt'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                            if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 )* item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                if json_staffs:

                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                    ins_item_reward.save()


            """map type brand"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__dbl_value_to__gte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
            fk_reward_details__int_map_type = 9,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        elif data['dbl_actual_est_amt'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                            if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                if json_staffs:

                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                    ins_item_reward.save()

            """GDP price"""

            if data['int_type'] in [1,3]:
                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']


                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_gdp_amount']) / data['int_sold']),\
                fk_reward_details__dbl_value_to__gte = ((data['dbl_gdp_amount']) / data['int_sold']),\
                fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdp'] :
                                pass
                            elif data['dbl_actual_gdp'] <= ((data['dbl_gdp_amount']) / data['int_sold']):
                                """slab1"""
                                if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_gdp_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_gdp_amount']) / data['int_sold']):
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


            """GDEW price"""
            if data['int_type'] in [2,3]:
                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']

                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_gdew_amount']) / data['int_sold']),\
                fk_reward_details__dbl_value_to__gte = ((data['dbl_gdew_amount']) / data['int_sold']),\
                fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=data['fk_enquiry_master__dat_created_at'].date(),fk_reward_details__fk_rewards_master__dat_to__gte=data['fk_enquiry_master__dat_created_at'].date(),\
                fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdew'] :
                                pass
                            elif data['dbl_actual_gdew'] <= ((data['dbl_gdew_amount']) / data['int_sold']):
                                """slab1"""
                                if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_gdew_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_gdew_amount']) / data['int_sold']):
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']


                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:

                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=data['fk_enquiry_master__dat_created_at'])
                        ins_item_reward.save()


# ===========================================================================================================================================================================================================================================================================================================================================================================================


        return "Success"
    except Exception as e:
        data = str(e)
        return data


def special_rewards(str_pk_id):
    try:
        # enquiry_num
        int_eq_pk_bint_id=int(str_pk_id)
        user_id = EnquiryMaster.objects.get(pk_bint_id = int_eq_pk_bint_id).fk_assigned_id
        user_instance = UserModel.objects.get(user_ptr_id = user_id)

        lst_item_enquiry_all = ItemEnquiry.objects.filter(fk_enquiry_master__pk_bint_id = int_eq_pk_bint_id,vchr_enquiry_status='INVOICED').\
        values('pk_bint_id','fk_item_id','fk_item__fk_product_id','fk_enquiry_master__dat_created_at','fk_item__fk_product__vchr_product_name','fk_item__fk_brand_id','int_sold','fk_enquiry_master__fk_assigned_id','dbl_amount','dbl_actual_est_amt','dbl_discount_amount',\
        'dbl_buy_back_amount','int_type','dbl_gdp_amount','dbl_gdew_amount','dbl_actual_gdp','dbl_actual_gdew').exclude(Q(fk_brand__vchr_brand_name__iexact = 'apple',fk_product__vchr_product_name__in =['HVA','ACC BGN']) | Q(fk_brand__vchr_brand_name__iexact = 'xiaomi',fk_product__vchr_product_name__in =['HVA','ACC BGN']) |\
         Q(fk_brand__vchr_brand_name__iexact = 'redmi',fk_product__vchr_product_name__in =['HVA','ACC BGN']) | Q(fk_brand__vchr_brand_name__iexact = 'sandisk',fk_product__vchr_product_name__in =['HVA','ACC BGN'])| Q(fk_product__vchr_product_name__iexact ='SMART CHOICE'))

        if not lst_item_enquiry_all:
            return JsonResponse({'status':'success'})

        int_promoter=UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],is_active=True).annotate(promo=Case(When(fk_brand_id__gte=1,then=Value(2)),default=Value(3),output_field=IntegerField())).values('promo','fk_branch_id','fk_brand_id').first()

        lst_available=[int_promoter['promo'],1]
        if not UserModel.objects.filter(id=lst_item_enquiry_all[0]['fk_enquiry_master__fk_assigned_id'],fk_group__vchr_name='STAFF',is_active=True).values():
            lst_available.pop(0)


        product_total_qty={}
        item_amount={}


        for data in lst_item_enquiry_all:

            lst_available=[]
            if not int_promoter['fk_brand_id']:
                lst_available=[3,1]
            elif data['fk_item__fk_brand_id']!=int_promoter['fk_brand_id']:
                lst_available=[3,1]
            elif int_promoter['fk_brand_id']==data['fk_item__fk_brand_id']:
                lst_available=[2,1]

            """value wise rewards"""
            """map type product value"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward


                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                if json_staffs:
                    # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER3"""
                    #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                    #


                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """map type brand value"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 6,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100)* item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward


                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                if json_staffs:
                    # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER3"""
                    #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                    #


                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """map type item value"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 7,fk_reward_details__int_map_id = data['fk_item_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
            'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        else:
                            """slab1"""
                            if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                                """slab2"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                elif item_data['dbl_slab2_amount']:
                                    reward = item_data['dbl_slab2_amount']
                                total_reward += reward * data ['int_sold']

                                """slab3"""
                            elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / data['dbl_actual_est_amt']) * 100:
                                if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                elif item_data['dbl_slab3_amount']:
                                    reward = item_data['dbl_slab3_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']
                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward




                if json_staffs:
                    # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER3"""
                    #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                    #


                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """GDP value"""

            if data['int_type'] in [1,3]:
                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']


                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdp'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp'])  * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_gdp_amount']) / data['int_sold']) / data['dbl_actual_gdp']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100 )* item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:
                        # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER3"""
                        #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                        #


                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=datetime.now())
                        ins_item_reward.save()


            """GDEW value"""
            if data['int_type'] in [2,3]:
                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']

                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
                fk_reward_details__int_map_type = 5,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'fk_reward_details__fk_rewards_master__dbl_slab1_percentage','fk_reward_details__fk_rewards_master__dbl_slab2_percentage','fk_reward_details__fk_rewards_master__dbl_slab3_percentage',\
                'int_to','dbl_slab1_percentage','dbl_slab1_amount','dbl_slab2_percentage','dbl_slab2_amount','dbl_slab3_percentage','dbl_slab3_amount','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdew'] :
                                pass
                            else:
                                """slab1"""
                                if item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab1_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = ((data['dbl_gdew_amount']) / data['int_sold']) / 100 * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab2"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab2_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                                    if item_data['dbl_slab2_percentage'] and item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount'] if ((data['dbl_gdew_amount'])/data['int_sold']) / 100 * item_data['dbl_slab2_percentage'] > item_data['dbl_slab2_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_percentage']:
                                        reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab2_percentage']
                                    elif item_data['dbl_slab2_amount']:
                                        reward = item_data['dbl_slab2_amount']
                                    total_reward += reward * data ['int_sold']

                                    """slab3"""
                                elif item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] and item_data['fk_reward_details__fk_rewards_master__dbl_slab3_percentage'] <= (((data['dbl_gdew_amount']) / data['int_sold']) / data['dbl_actual_gdew']) * 100:
                                    if item_data['dbl_slab3_percentage'] and item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab3_percentage'] > item_data['dbl_slab3_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_percentage']:
                                        reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab3_percentage']
                                    elif item_data['dbl_slab3_amount']:
                                        reward = item_data['dbl_slab3_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward



                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:
                        # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER3"""
                        #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)



                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=datetime.now())
                        ins_item_reward.save()

# ===========================================================================================================================================================================================================================================================================================================================================================================================================
            """price band wise rewards"""
            # 

            """map type product price"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__dbl_value_to__gte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = data['fk_item__fk_product_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt']:
                            pass
                        elif data['dbl_actual_est_amt'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                            if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100 )* item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward


                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward


                if json_staffs:
                    # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER3"""
                    #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                    #


                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=datetime.now())
                    ins_item_reward.save()


            """map type brand"""
            total_reward=0
            # item_amount['dbl_apx_amount']=0

            item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__dbl_value_to__gte = ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']),\
            fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
            fk_reward_details__int_map_type = 9,fk_reward_details__int_map_id = data['fk_item__fk_brand_id'],fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
            'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

            if item_data_all:
                json_staffs = {}
                int_branch_manager = 0
                int_ast_manager = 0
                for item_data in item_data_all:
                    total_reward=0
                    if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                        # item_amount=Items.objects.filter(id=data['fk_item_id']).values('dbl_apx_amount').first()
                        if not data['dbl_actual_est_amt'] :
                            pass
                        elif data['dbl_actual_est_amt'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                            if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']):
                                if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount'] if (((data['dbl_amount'] - data['dbl_discount_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_percentage']:
                                    reward = (((data['dbl_amount'] - data['dbl_discount_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                elif item_data['dbl_slab1_amount']:
                                    reward = item_data['dbl_slab1_amount']
                                total_reward += reward * data ['int_sold']

                    if total_reward:
                        total_reward = round(total_reward,2)
                        if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                            int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                            str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                            str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                            if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                #non-promoter
                                if (item_data['int_to'] == 3) and (3 in lst_available):
                                    json_staffs[int_assign_id] = total_reward
                                #all
                                elif item_data['int_to'] == 1:
                                    json_staffs[int_assign_id] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM4':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM3':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'ASM2':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                            elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                    int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                            elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                            elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                    json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(data['fk_item__fk_product_id'])]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                if json_staffs:
                    # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER3"""
                    #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """FLOOR MANAGER1"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 3"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                    #
                    # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                    #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                    #     json_staffs[int_branch_manager] = 0
                    #     json_staffs[int_ast_manager] = 0
                    #     """ASSISTANT BRANCH MANAGER 2"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                    #     """ASSISTANT BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                    #     """BRANCH MANAGER"""
                    #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                    #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                    #


                    ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_est_amt'],dat_reward=datetime.now())
                    ins_item_reward.save()

            """GDP price"""

            if data['int_type'] in [1,3]:
                int_gdp=Products.objects.filter(vchr_product_name='GDP').values('id').first()['id']


                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_gdp_amount']) / data['int_sold']),\
                fk_reward_details__dbl_value_to__gte = ((data['dbl_gdp_amount']) / data['int_sold']),\
                fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
                fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = int_gdp,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdp'] :
                                pass
                            elif data['dbl_actual_gdp'] <= ((data['dbl_gdp_amount']) / data['int_sold']):
                                """slab1"""
                                if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_gdp_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_gdp_amount']) / data['int_sold']):
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdp_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdp_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_gdp_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']

                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdp)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:
                        # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER3"""
                        #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)
                        #


                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdp'],dat_reward=datetime.now())
                        ins_item_reward.save()


            """GDEW price"""
            if data['int_type'] in [2,3]:
                int_gdew=Products.objects.filter(vchr_product_name='GDEW').values('id').first()['id']

                total_reward=0
                # item_amount['dbl_apx_amount']=0

                item_data_all= RewardAssigned.objects.filter(fk_reward_details__dbl_value_from__lte = ((data['dbl_gdew_amount']) / data['int_sold']),\
                fk_reward_details__dbl_value_to__gte = ((data['dbl_gdew_amount']) / data['int_sold']),\
                fk_reward_details__int_status__gte = 0,int_status__gte = 0, fk_reward_details__fk_rewards_master__fk_created_by__fk_company_id=user_instance.fk_company_id,fk_reward_details__fk_rewards_master__dat_from__lte=datetime.now().date(),fk_reward_details__fk_rewards_master__dat_to__gte=datetime.now().date(),\
                fk_reward_details__int_map_type = 8,fk_reward_details__int_map_id = int_gdew,fk_reward_details__fk_rewards_master__json_branch__contains={'branch_id':[str(int_promoter['fk_branch_id'])]}).values('pk_bint_id','fk_reward_details__fk_rewards_master_id',\
                'int_to','fk_reward_details__int_mop_sale','fk_reward_details','fk_group__vchr_name','fk_reward_details__dbl_value_from','fk_reward_details__dbl_value_to','dbl_slab1_percentage','dbl_slab1_amount').order_by("-pk_bint_id")

                if item_data_all:
                    json_staffs = {}
                    int_branch_manager = 0
                    int_ast_manager = 0
                    for item_data in item_data_all:
                        total_reward=0
                        if item_data and item_data['fk_reward_details__int_mop_sale']==1:
                            if not data['dbl_actual_gdew'] :
                                pass
                            elif data['dbl_actual_gdew'] <= ((data['dbl_gdew_amount']) / data['int_sold']):
                                """slab1"""
                                if item_data['fk_reward_details__dbl_value_from'] <= ((data['dbl_gdew_amount']) / data['int_sold']) and item_data['fk_reward_details__dbl_value_to'] >= ((data['dbl_gdew_amount']) / data['int_sold']):
                                    if item_data['dbl_slab1_percentage'] and item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount'] if (((data['dbl_gdew_amount'])/data['int_sold']) / 100) * item_data['dbl_slab1_percentage'] > item_data['dbl_slab1_amount'] else (((data['dbl_gdew_amount']) / data['int_sold'] ) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_percentage']:
                                        reward = (((data['dbl_gdew_amount']) / data['int_sold']) / 100) * item_data['dbl_slab1_percentage']
                                    elif item_data['dbl_slab1_amount']:
                                        reward = item_data['dbl_slab1_amount']
                                    total_reward += reward * data ['int_sold']


                        if total_reward:
                            total_reward = round(total_reward,2)
                            if not RewardsAvailable.objects.filter(fk_rewards_master_id = item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id']).values():

                                int_assign_id = EnquiryMaster.objects.filter(pk_bint_id = int_eq_pk_bint_id).values('fk_assigned_id').first()['fk_assigned_id']
                                str_assign_group = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_group__vchr_name').first()['fk_group__vchr_name']
                                str_assign_brand = UserModel.objects.filter(user_ptr_id = int_assign_id).values('fk_brand__vchr_brand_name').first()['fk_brand__vchr_brand_name']

                                if (item_data['fk_group__vchr_name'] == 'STAFF' and str_assign_group == 'STAFF') and ((str_assign_brand != "NPS") or (str_assign_brand == "NPS" and data['fk_item__fk_product__vchr_product_name'] != "LAPTOPS")):
                                    #non-promoter
                                    if (item_data['int_to'] == 3) and (3 in lst_available):
                                        json_staffs[int_assign_id] = total_reward
                                    #all
                                    elif item_data['int_to'] == 1:
                                        json_staffs[int_assign_id] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'CUSTOMER EXPERIENCE EXICUTIVE':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='CUSTOMER EXPERIENCE EXICUTIVE').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'FLOOR MANAGER1':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM4':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM4').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM3':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'ASM2':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward

                                elif item_data['fk_group__vchr_name'] == 'TERRITORY MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_branch_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ASSISTANT BRANCH MANAGER':
                                    if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                        int_ast_manager = UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']
                                elif item_data['fk_group__vchr_name'] == 'ZONE MANAGER':
                                    if UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,int_area_id=user_instance.fk_branch.fk_territory.fk_zone_id,fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'PRODUCT MANAGER':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward
                                elif item_data['fk_group__vchr_name'] == 'B TEAM':
                                    if UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id'):
                                        json_staffs[UserModel.objects.filter(is_active=True,json_product_id__contains={"productId":[str(int_gdew)]},fk_group_id=Groups.objects.filter(vchr_name=item_data['fk_group__vchr_name']).first()).values('user_ptr_id').order_by("user_ptr_id").first()['user_ptr_id']] = total_reward



                    if json_staffs:
                        # if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER3"""
                        #     json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """FLOOR MANAGER1"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='FLOOR MANAGER1').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (10 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 3"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM3').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (15 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (25 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (35 / 100),2)
                        #
                        # elif UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id') and int_branch_manager and int_ast_manager:
                        #     dbl_new_reward = json_staffs[int_branch_manager] + json_staffs[int_ast_manager]
                        #     json_staffs[int_branch_manager] = 0
                        #     json_staffs[int_ast_manager] = 0
                        #     """ASSISTANT BRANCH MANAGER 2"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASM2').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (20 / 100),2)
                        #     """ASSISTANT BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='ASSISTANT BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (30 / 100),2)
                        #     """BRANCH MANAGER"""
                        #     if UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id'):
                        #         json_staffs[UserModel.objects.filter(is_active=True,fk_branch_id=user_instance.fk_branch_id,fk_group_id=Groups.objects.filter(vchr_name__iexact='BRANCH MANAGER').first()).values('user_ptr_id').first()['user_ptr_id']] = round(dbl_new_reward * (50 / 100),2)



                        ins_item_reward =  RewardsAvailable(json_staff = json_staffs,fk_rewards_master_id=item_data['fk_reward_details__fk_rewards_master_id'],fk_rewards_details_id=item_data['fk_reward_details'],fk_item_enquiry_id=data['pk_bint_id'],dbl_mop_amount=data['dbl_actual_gdew'],dat_reward=datetime.now())
                        ins_item_reward.save()


# ===========================================================================================================================================================================================================================================================================================================================================================================================


        return "Success"
    except Exception as e:
        data = str(e)
        return data



# =================================================================================================================================================================================================================================================================


def enquiry_for_pos(int_enq_id):
    try:
        session = Session
        rst_enquiry=ItemEnquiry.objects.filter(fk_enquiry_master_id=int_enq_id,vchr_enquiry_status='BOOKED').values('fk_enquiry_master__fk_customer__cust_fname','fk_enquiry_master__fk_customer__cust_lname','fk_enquiry_master__fk_customer__cust_email','fk_enquiry_master__fk_customer__cust_mobile','fk_enquiry_master__fk_customer__vchr_gst_no','fk_enquiry_master_id','fk_enquiry_master__fk_customer__fk_location__vchr_name','fk_enquiry_master__fk_customer__fk_location__vchr_district','fk_enquiry_master__fk_customer__fk_location__vchr_pin_code','fk_enquiry_master__fk_customer__fk_state__vchr_code','fk_enquiry_master__fk_assigned__username','fk_enquiry_master__fk_branch__vchr_code','vchr_remarks','fk_enquiry_master__dat_created_at','fk_item__vchr_item_name','fk_item__vchr_item_code','dbl_imei_json','int_quantity','dbl_amount','dbl_discount_amount','dbl_buy_back_amount','bln_smart_choice','fk_product__vchr_product_name','pk_bint_id','fk_enquiry_master_id','fk_enquiry_master__vchr_enquiry_num','fk_enquiry_master__vchr_remarks')
        rst_exchange = ItemExchange.objects.filter(fk_item_enquiry__fk_enquiry_master_id = int_enq_id,fk_item_enquiry__vchr_enquiry_status='BOOKED').values('fk_item__vchr_item_code','vchr_filename_json','dbl_exchange_amt')
        dct_pos_data = {}
        dct_pos_data['lst_item'] = []
        dct_pos_data['dbl_total_amt'] = 0
        dct_pos_data['dbl_total_tax'] = 0
        dct_pos_data['dbl_discount'] = 0
        if rst_enquiry:
            # bln_post_rqst = True
            for ins_enquiry in rst_enquiry:
                dct_item = {}
                dct_item['item_enquiry_id'] = ins_enquiry['pk_bint_id']
                dct_item['vchr_item_name'] = ins_enquiry['fk_item__vchr_item_name']
                dct_item['vchr_item_code'] = ins_enquiry['fk_item__vchr_item_code']
                dct_item['json_imei'] = ins_enquiry['dbl_imei_json']
                dct_item['int_quantity']= ins_enquiry['int_quantity']
                dct_item['dbl_amount'] = ins_enquiry['dbl_amount']
                dct_item['dbl_discount'] = ins_enquiry['dbl_discount_amount']
                dct_item['dbl_buyback'] = ins_enquiry['dbl_buy_back_amount']
                dct_item['vchr_remarks'] = ins_enquiry['vchr_remarks']
                dct_pos_data['dbl_total_amt'] += float(ins_enquiry['dbl_amount'])
                dct_pos_data['dbl_discount'] += float(ins_enquiry['dbl_discount_amount'])
                dct_item['int_status'] = 1
                if dct_item['vchr_item_name'].upper()=='F120B JIO DIGITAL LIFE':
                    dct_item['int_status'] = 4
                    dct_pos_data['int_status']=4
                elif ins_enquiry['fk_product__vchr_product_name'].upper()=='SMART CHOICE':
                    dct_item['int_status'] = 2
                    if rst_exchange:
                        for ins_exc in rst_exchange:
                            if 'bln_smart' not in ins_exc and ins_exc['fk_item__vchr_item_code'] == ins_enquiry['fk_item__vchr_item_code'] and ins_exc['dbl_exchange_amt'] == (ins_enquiry['dbl_amount']*(-1)):
                                ins_exc['bln_smart'] = True
                                dct_item['dct_images'] = ins_exc['vchr_filename_json']
                                break

                dct_pos_data['lst_item'].append(dct_item)


            dct_pos_data['vchr_cust_name'] = ins_enquiry['fk_enquiry_master__fk_customer__cust_fname']+' '+ins_enquiry['fk_enquiry_master__fk_customer__cust_lname']
            dct_pos_data['vchr_cust_email'] = ins_enquiry['fk_enquiry_master__fk_customer__cust_email']
            dct_pos_data['int_cust_mob'] = ins_enquiry['fk_enquiry_master__fk_customer__cust_mobile']
            dct_pos_data['vchr_gst_no'] = ins_enquiry['fk_enquiry_master__fk_customer__vchr_gst_no']
            dct_pos_data['int_enq_master_id'] = ins_enquiry['fk_enquiry_master_id']
            dct_pos_data['vchr_enquiry_num'] = ins_enquiry['fk_enquiry_master__vchr_enquiry_num']
            dct_pos_data['vchr_location'] = ''
            dct_pos_data['int_pin_code'] = ''
            dct_pos_data['txt_address'] = ''
            dct_pos_data['vchr_state_code'] = ''
            dct_pos_data['vchr_district'] = ''
            if ins_enquiry['fk_enquiry_master__fk_customer__fk_location__vchr_name']:
                dct_pos_data['vchr_location'] = ins_enquiry['fk_enquiry_master__fk_customer__fk_location__vchr_name']
                dct_pos_data['vchr_district'] = ins_enquiry['fk_enquiry_master__fk_customer__fk_location__vchr_district']
                dct_pos_data['vchr_pin_code'] = ins_enquiry['fk_enquiry_master__fk_customer__fk_location__vchr_pin_code']
            if ins_enquiry['fk_enquiry_master__fk_customer__fk_state__vchr_code']:
                dct_pos_data['vchr_state_code'] = ins_enquiry['fk_enquiry_master__fk_customer__fk_state__vchr_code']
            dct_pos_data['vchr_staff_code'] = ins_enquiry['fk_enquiry_master__fk_assigned__username']
            dct_pos_data['vchr_branch_code'] = ins_enquiry['fk_enquiry_master__fk_branch__vchr_code']
            dct_pos_data['str_remarks'] = ins_enquiry['fk_enquiry_master__vchr_remarks']
            dct_pos_data['dat_enquiry'] = datetime.strftime(ins_enquiry['fk_enquiry_master__dat_created_at'],'%Y-%m-%d')

            url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
            try:
                res_data = requests.post(url,json=dct_pos_data)
                if res_data.json().get('status')=='1':
                    pass
                else:
                    return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
            except Exception as e:
                raise
        return
        # --------------------------------------------------------------
    except Exception as e:
        ins_logger.logger.error(e, extra={'details':traceback.format_exc()})
        return JsonResponse({'status': 'Failed','data':str(e)})


class AddReturnItemEnquiry(APIView):
    """
        To create new  enquiry of a return item.
        param : dct_enquiry_data
        return : success

    """
    permission_classes=[AllowAny]
    def post(self,request):
        try:

            with transaction.atomic():
                dct_datas = request.data['dct_enquiry_data']
                for dct_data in dct_datas:
                    if dct_data['vchr_item_code'] not in ['GDC00001','GDC00002']:

                        dct_data['vchr_customer_name'].split(" ")
                        int_cust = CustomerModel.objects.filter( cust_mobile = dct_data['int_customer_mobile']).first()
                        ins_user  = UserModel.objects.filter(username=dct_data['vchr_user_code']).first()
                        ins_branch = Branch.objects.filter(vchr_code=dct_data['vchr_branch_code']).first()
                        ins_item = Items.objects.filter(vchr_item_code=dct_data['vchr_item_code']).first()

                        if not int_cust or not ins_user or not ins_branch or not ins_item:
                            return Response({'status':0,'message':'Failed'})

                        ins_document = Document.objects.filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
                        str_code = ins_document[0].vchr_short_code
                        int_doc_num = ins_document[0].int_number + 1
                        ins_document.update(int_number = int_doc_num)
                        str_number = str(int_doc_num).zfill(4)
                        str_enquiry_no = str_code + '-' + str_number
                        #ins_master = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
                        ins_master = EnquiryMaster.objects.create(
                                                    vchr_enquiry_num = str_enquiry_no,
                                                    fk_customer_id = int_cust.id,
                                                    fk_source = Source.objects.get(vchr_source_name='WALK IN'),
                                                    fk_assigned_id = ins_user.id,
                                                    fk_branch_id = ins_branch.pk_bint_id,
                                                    chr_doc_status = 'N',
                                                    fk_created_by_id = ins_user.id,
                                                    dat_created_at = datetime.now(),
                                                    fk_company_id = ins_user.fk_company_id,
                                                    vchr_remarks = dct_data.get('vchr_remarks')
                                                )
                        ins_master.save()
                        if ins_master:
                            ins_item_enq = ItemEnquiry(
                                                        fk_enquiry_master = ins_master,
                                                        fk_product_id=ins_item.fk_product_id,
                                                        fk_brand_id = ins_item.fk_brand_id,
                                                        fk_item_id = ins_item.id,
                                                        int_quantity = 1,
                                                        dbl_amount = dct_data['dbl_amount']+dct_data.get('dbl_discount',0)+dct_data.get('dbl_buyback',0),
                                                        vchr_enquiry_status = 'RETURNED',
                                                        int_sold = 1,
                                                        dbl_imei_json = dct_data['dbl_imei_json'],
                                                        dbl_discount_amount = dct_data['dbl_discount'] or 0,
                                                        dbl_buy_back_amount = dct_data['dbl_buyback'] or 0,
                                                        dbl_gdp_amount = 0,
                                                        dbl_gdew_amount = 0,
                                                        int_type = 0,
                                                        dbl_actual_gdp = 0,
                                                        dbl_actual_gdew = 0,
                                                        dbl_actual_est_amt = 0,
                                                        dbl_indirect_discount_amount = dct_data['dbl_indirect_discount'],
                                                        dat_sale = datetime.now(),
                                                        dbl_sup_amount = -1 * dct_data.get('dbl_supp_amnt',0),
                                                        dbl_mop_price = -1 * dct_data.get('dbl_mop_amnt',0),
                                                        dbl_mrp_price = -1 * dct_data.get('dbl_mrp_amnt',0),
                                                        dbl_cost_price = -1 * dct_data.get('dbl_cost_amnt',0),
                                                        dbl_myg_price = -1 * dct_data.get('dbl_myg_amnt',0),
                                                        dbl_dealer_price = -1 * dct_data.get('dbl_dealer_amnt',0),
                                                        dbl_tax = dct_data.get('dbl_tax',0),
                                                        json_tax = dct_data.get('json_tax')
                                                    )
                            ins_item_enq.save()

                            if ins_item_enq:
                                ins_item_foll = ItemFollowup(
                                                                fk_item_enquiry = ins_item_enq,
                                                                dat_followup = datetime.now(),
                                                                fk_user_id = ins_user.id,
                                                                vchr_notes = dct_data.get('vchr_remarks'),
                                                                int_quantity = 1,
                                                                vchr_enquiry_status = 'RETURNED',
                                                                dbl_amount = dct_data['dbl_amount']+dct_data.get('dbl_discount',0)+ dct_data.get('dbl_buyback',0),
                                                                fk_updated_id = ins_user.id,
                                                                dat_updated = datetime.now()
                                                            )
                                ins_item_foll.save()



                    else:
                        # ========================================== GDOT ==================================================================
                        if dct_data['dbl_imei_json']['imei']:
                            # rst_gdot= ItemEnquiry.objects.filter( Q(fk_product_id__vchr_product_name = 'SERVICE'),Q(dbl_imei_json__contains =dct_data['dbl_imei_json']),~Q(vchr_enquiry_status='RETURNED')).values()
                            # if rst_gdot:
                            #
                                # dbl_amount = (ins_gdot['dbl_amount']/ins_gdot['int_quantity'])*(-1) if (ins_gdot['int_quantity'] and ins_gdot['dbl_amount']) else 0
                            ins_item = Items.objects.filter(vchr_item_code=dct_data['vchr_item_code']).first()

                            ins_gdot_enq = ItemEnquiry(
                                                        fk_enquiry_master = ins_master,
                                                        fk_product_id= ins_item.fk_product_id,
                                                        fk_brand_id = ins_item.fk_brand_id,
                                                        fk_item_id = ins_item.id,
                                                        int_quantity = 1,
                                                        dbl_amount = dct_data['dbl_amount']+dct_data.get('dbl_discount',0)+ dct_data.get('dbl_buyback',0),
                                                        vchr_enquiry_status = 'RETURNED',
                                                        int_sold = 1,
                                                        dbl_imei_json = dct_data['dbl_imei_json'],
                                                        dbl_discount_amount = dct_data['dbl_discount'] or 0,
                                                        dbl_buy_back_amount =  dct_data['dbl_buyback'] or 0,
                                                        dbl_gdp_amount = 0,
                                                        dbl_gdew_amount = 0,
                                                        int_type = 0,
                                                        dbl_actual_gdp = 0,
                                                        dbl_actual_gdew = 0,
                                                        dbl_actual_est_amt = 0,
                                                        dat_sale = datetime.now(),
                                                        dbl_tax = dct_data.get('dbl_tax',0),
                                                        json_tax = dct_data.get('json_tax')
                                                    )
                            ins_gdot_enq.save()

                            if ins_item_enq:
                                ins_gdot_foll = ItemFollowup(
                                                                fk_item_enquiry = ins_gdot_enq,
                                                                dat_followup = datetime.now(),
                                                                fk_user_id = ins_user.id,
                                                                vchr_notes = dct_data.get('vchr_remarks'),
                                                                int_quantity = 1,
                                                                vchr_enquiry_status = 'RETURNED',
                                                                dbl_amount = dct_data['dbl_amount']+dct_data.get('dbl_discount',0)+ dct_data.get('dbl_buyback',0),
                                                                fk_updated_id = ins_user.id,
                                                                dat_updated = datetime.now()
                                                            )
                                ins_gdot_foll.save()

                # ============================================================================================================
                # a=1/0
                # 
                return Response({'status':'success'})

        except Exception as e:
            ins_logger.logger.error(e, extra={'details':traceback.format_exc()})
            return JsonResponse({'status': 'Failed','data':str(e)})



class CreateExchangeItem(APIView):
      permission_classes=[AllowAny]
      def post(self,request):
          with transaction.atomic():
            # 
            ins_company=CompanyDetails.objects.filter(vchr_code__iexact='myg').first()
            ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_company)
            str_code = ins_document[0].vchr_short_code
            int_doc_num = ins_document[0].int_number + 1
            ins_document.update(int_number = int_doc_num)
            str_number = str(int_doc_num).zfill(4)
            str_enquiry_no = str_code + '-' + str_number
            ins_customer=CustomerModel.objects.filter(cust_mobile=request.data.get('cust_mobile')).first()

            ins_staff=UserModel.objects.filter(username=request.data.get('staff')).first()
            ins_source = Source.objects.filter(vchr_source_name__iexact='walk in').first()
            int_job_master_id = request.data.get("int_enq_master_id")
            # ins_enq_master = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
            """Data to payment_details"""
            if request.data.get('bi_payment_details'):
                lst_payment_details = []
                for data in request.data['bi_payment_details']:
                    ins_payment_details=PaymentDetails(fk_enquiry_master_id = int_job_master_id, int_fop = data['int_fop'], dbl_amount = data['dbl_amt'], dat_created = datetime.today())
                    lst_payment_details.append(ins_payment_details)
                PaymentDetails.objects.bulk_create(lst_payment_details)

            ins_enq_master = EnquiryMaster.objects.create(vchr_enquiry_num=str_enquiry_no,fk_source=ins_source,fk_customer=ins_customer,fk_branch=ins_staff.fk_branch,fk_company=ins_company,fk_created_by=ins_staff,fk_assigned=ins_staff,dat_created_at=datetime.now(),vchr_remarks=request.data.get('str_remarks'),chr_doc_status='N')
            lst_item_data=request.data.get('dct_item_data')

            for data in lst_item_data:
                ins_item= Items.objects.filter(vchr_item_code=lst_item_data[data]['strItemCode']).first()
                if lst_item_data[data]['jsonImei']:
                    json_imei={'imei':lst_item_data[data]['jsonImei']}
                else:
                    json={'imei':[]}
                ins_item_enq=ItemEnquiry.objects.create(vchr_enquiry_status='INVOICED',dbl_imei_json=json_imei,dbl_amount=lst_item_data[data]['dblAmount'],fk_enquiry_master=ins_enq_master,fk_product=ins_item.fk_product,fk_item=ins_item,fk_brand=ins_item.fk_brand,dat_sale=datetime.now(),int_quantity=lst_item_data[data]['intQuantity'])


            #   ins_item=ItemEnquiry.objects.create(fk_enquiry_master=ins_enq_master,fk_product=Products.objects.filter(vchr_product_name__icontains='smart choice').first(),fk_item=)
            return Response({'status':'success'})

class AddCreditPayment(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            with transaction.atomic():
                int_fop = request.data.get('fop')
                int_enq_id = request.data.get('enq_id')
                dbl_amount = request.data.get('amount')
                ins_payment_details=PaymentDetails(fk_enquiry_master_id = int_enq_id, int_fop = int_fop, dbl_amount = dbl_amount, dat_created = datetime.today())
                ins_payment_details.save()
                return Response({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'details':traceback.format_exc()})
            return Response({'status': 'Failed','data':str(e)})
