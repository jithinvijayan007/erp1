from django.shortcuts import render
from .models import RewardsMaster,RewardsDetails,RewardsAvailable,RewardsPaid,RewardAssigned
from rest_framework.views import APIView
from datetime import datetime, timedelta
from rest_framework.response import Response
from inventory.models import Products,Brands,Items
from django.db.models import Sum
from zone.models import Zone
from territory.models import Territory
from branch.models import Branch
from globalMethods import show_data_based_on_role
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Concat
from django.db.models import Value
from django.contrib.auth.models import User
import pandas as pd
from django.conf import settings
from groups.models import Groups
import requests
import random as rd


from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.db.models import Q
from user_app.models import UserModel


from sqlalchemy import case, literal_column, desc, tuple_, select, table, column
from sqlalchemy.orm.session import sessionmaker
import aldjemy
from sqlalchemy.orm import mapper,aliased
from sqlalchemy import and_,func,cast,Date,MetaData,or_
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy.types import TypeDecorator,BigInteger
from dateutil.relativedelta import relativedelta
from CRM.dftosql import Savedftosql
from enquiry.models import EnquiryMaster
from enquiry_mobile.models import ItemEnquiry
from globalMethods import convert_to_millions,show_data_based_on_role,get_user_products

from territory_hierarchy.models import State
from country.models import Countries

from itertools import chain

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)

def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

AuthUserSA = User.sa
UserModelSA = UserModel.sa
BranchSA = Branch.sa
RewardsPaidSA = RewardsPaid.sa
RewardsAvailableSA = RewardsAvailable.sa
GroupsSA = Groups.sa
ItemEnquirySA = ItemEnquiry.sa
EnquiryMasterSA = EnquiryMaster.sa
TerritorySA = Territory.sa
ZoneSA = Zone.sa
StateSA = State.sa
CountrySA = Countries.sa


RewardsAvailableJS = metadata.tables['rewards_available']


def GetUserList(request):


                userListData=UserModel.objects.filter(is_active=True,fk_company=request.user.userdetails.fk_company_id).exclude(username='TDX-ADMIN').values('id','fk_branch_id','fk_group__vchr_name','int_area_id','fk_group').order_by('-id')
                int_companyId=request.user.userdetails.fk_company_id

                if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
                    userListData=userListData.values_list('id',flat=True)
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    userListData = userListData.filter(fk_branch_id = request.user.userdetails.fk_branch_id).values_list('id',flat=True)
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    userListData = userListData.values_list('id',flat=True).filter(fk_branch_id__in=lst_branch,int_area_id=None)
                    if request.user.userdetails.fk_group.vchr_name == 'COUNTRY HEAD':
                        lst_managers = list(State.objects.filter(fk_country_id=request.user.userdetails.int_area_id).values_list('pk_bint_id',flat='True'))
                        lst_managers += list(Zone.objects.filter(fk_state_id__in=lst_managers).values_list('pk_bint_id',flat='True'))
                        lst_managers += list(Territory.objects.filter(fk_zone_id__in=lst_managers).values_list('pk_bint_id',flat='True'))
                        user = UserModel.objects.filter(Q(fk_group__vchr_name='STATE HEAD')|Q(fk_group__vchr_name='ZONE MANAGER')|Q(fk_group__vchr_name='TERRITORY MANAGER'),is_active=True,int_area_id__in=set(lst_managers)).exclude(fk_group__vchr_name='ADMIN').values_list('id',flat=True).order_by('-id')
                    elif request.user.userdetails.fk_group.vchr_name == 'STATE HEAD':
                        lst_managers = list(Zone.objects.filter(fk_state_id=request.user.userdetails.int_area_id).values_list('pk_bint_id',flat='True'))
                        lst_managers += list(Territory.objects.filter(fk_zone_id__in=lst_managers).values_list('pk_bint_id',flat='True'))
                        user = UserModel.objects.filter(Q(fk_group__vchr_name='ZONE MANAGER')|Q(fk_group__vchr_name='TERRITORY MANAGER'),is_active=True,int_area_id__in=set(lst_managers)).exclude(fk_group__vchr_name='ADMIN').values_list('id',flat=True).order_by('-id')
                    elif request.user.userdetails.fk_group.vchr_name == 'ZONE MANAGER':
                        lst_territory = Territory.objects.filter(fk_zone_id=request.user.userdetails.int_area_id).values_list('pk_bint_id',flat='True')
                        user = UserModel.objects.filter(is_active=True,int_area_id__in=lst_territory,fk_branch_id=None,fk_group__vchr_name='TERRITORY MANAGER').exclude(fk_group__vchr_name='ADMIN').values_list('id',flat=True).order_by('-id')
                    else:
                        user = []
                    curent_user=UserModel.objects.filter(is_active=True,fk_company=int(int_companyId),user_ptr_id=request.user.id).values_list('id',flat=True).order_by('-id')
                    userListData = list(chain(userListData,user,curent_user))
                else:
                    userListData = userListData.filter(id = request.user.id).values_list('id',flat=True)

                return userListData


# Create your views here.
class AddReward(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            from_date = datetime.strptime(request.data.get('fromDate'), '%d/%m/%Y' )
            to_date = datetime.strptime(request.data.get('toDate'), '%d/%m/%Y' )
            area_type = request.data.get('areaType')
            area_id = request.data.get('LstArea')
            lst_branch_id = []
            if area_type:
                if area_type.upper()=='ZONE':
                    for area in area_id:
                        lst_branch_id.extend(show_data_based_on_role('ZONE MANAGER',area))
                elif area_type.upper()=='TERRITORY':
                    for area in area_id:
                        lst_branch_id.extend(show_data_based_on_role('TERRITORY MANAGER',area))
                elif area_type.upper()=='BRANCH':
                    lst_branch_id = area_id
                else:
                    return Response({'status':'failed','reason':'Area Not Found'})
            else:
                lst_branch_id = area_id
            reward_name = request.data.get('rewardName')
            lst_branch_id = [str(data) for data in lst_branch_id]
            ins_reward_master = ''
            ins_details = request.data.get('addrewards')

            if request.data.get('id'):
                for branch in lst_branch_id:
                    ins_prev_reward = RewardsMaster.objects.filter(dat_to__gte=from_date,dat_from__lte=to_date,json_branch__contains={'branch_id':[branch]}).exclude(int_status=-1).exclude(pk_bint_id=request.data.get('id')).values('pk_bint_id')
                    if ins_prev_reward:
                        ins_prv_details = ''
                        if int(request.data.get('map_type')) == 0 or int(request.data.get('map_type')) == 1 or int(request.data.get('map_type')) == 2:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'],int_quantity_from = int(ins_details[0]['fromQty']), int_quantity_to = int(ins_details[0]['tillQty']))
                        elif int(request.data.get('map_type')) == 3:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'],dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))
                        elif int(request.data.get('map_type')) == 4:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')),dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))

                        if ins_prv_details:
                            return Response({'status':'failed','reason':'Reward Already Exist'})
                ins_reward_master = RewardsMaster.objects.get(pk_bint_id=request.data.get('id'))
                ins_reward_master.int_status = 0
                ins_reward_master.fk_updated_by = request.user.userdetails
                RewardsDetails.objects.filter(fk_rewards_master=ins_reward_master).update(int_status=-1)
                RewardAssigned.objects.filter(fk_reward_details_id__fk_rewards_master=ins_reward_master).update(int_status=-1)
            else:
                for branch in lst_branch_id:
                    ins_prev_reward = RewardsMaster.objects.filter(dat_to__gte=from_date,dat_from__lte=to_date,json_branch__contains={'branch_id':[branch]}).exclude(int_status=-1).values('pk_bint_id')
                    if ins_prev_reward:
                        ins_prv_details = ''
                        if int(request.data.get('map_type')) == 0 or int(request.data.get('map_type')) == 1 or int(request.data.get('map_type')) == 2:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'],int_quantity_from = int(ins_details[0]['fromQty']), int_quantity_to = int(ins_details[0]['tillQty']))
                        elif int(request.data.get('map_type')) == 3:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'],dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))
                        elif int(request.data.get('map_type')) == 4:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')),dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))
                        if ins_prv_details:
                            return Response({'status':'failed','reason':'Reward Already Exist'})

                ins_reward_master = RewardsMaster()
                ins_reward_master.int_status = 1
                ins_reward_master.fk_created_by = request.user.userdetails
            ins_reward_master.dat_from = from_date
            ins_reward_master.dat_to = to_date
            if area_type:
                ins_reward_master.vchr_area_type = area_type.upper()
            ins_reward_master.json_branch = {'branch_id':lst_branch_id}
            ins_reward_master.vchr_reward_name = reward_name
            if 'reward1' in request.data and request.data.get('reward1'):
                ins_reward_master.dbl_slab1_percentage = request.data.get('reward1')
            if 'reward2' in request.data and request.data.get('reward2'):
                ins_reward_master.dbl_slab2_percentage = request.data.get('reward2')
            if 'reward3' in request.data and request.data.get('reward3'):
                ins_reward_master.dbl_slab3_percentage = request.data.get('reward3')
            ins_reward_master.save()

            # RewardsDetails saving

            ins_reward_details = RewardsDetails()

            if request.data.get('id'):
                ins_reward_details.int_status=0
            else:
                ins_reward_details.int_status=1
            ins_reward_details.fk_rewards_master_id = ins_reward_master.pk_bint_id
            ins_reward_details.int_map_type = int(request.data.get('map_type'))
            if 'map_id' in ins_details[0]:
                ins_reward_details.int_map_id = int(ins_details[0]['map_id'])

            if 'fromQty' in ins_details[0] and 'tillQty' in ins_details[0]:
                ins_reward_details.int_quantity_from = int(ins_details[0]['fromQty'])
                ins_reward_details.int_quantity_to = int(ins_details[0]['tillQty'])
            elif 'fromAmt' in ins_details[0] and 'toAmt' in ins_details[0]:
                ins_reward_details.dbl_value_from = float(ins_details[0]['fromAmt'])
                ins_reward_details.dbl_value_to = float(ins_details[0]['toAmt'])

            if 'reward_mop' in ins_details[0] and ins_details[0]['reward_mop']:
                ins_reward_details.int_mop_sale = 1
            else:
                ins_reward_details.int_mop_sale = 0
            ins_reward_details.save()



            # RewardAssigned saving
            for items in ins_details:
                ins_reward_assigned = RewardAssigned()
                if request.data.get('id'):
                    ins_reward_assigned.int_status=0
                else:
                    ins_reward_assigned.int_status=1
                ins_reward_assigned.fk_reward_details_id = ins_reward_details.pk_bint_id
                # ins_reward_details.int_map_type = int(request.data.get('map_type')) # 0. Product, 1. Brand, 2. Item, 3. Value, 4. TurnOver
                # if 'map_id' in items:
                #     ins_reward_details.int_map_id = int(items['map_id'])
                #
                # if 'fromQty' in items and 'tillQty' in items:
                #     ins_reward_details.int_quantity_from = int(items['fromQty'])
                #     ins_reward_details.int_quantity_to = int(items['tillQty'])
                # elif 'fromAmt' in items and 'toAmt' in items:
                #     ins_reward_details.dbl_value_from = float(items['fromAmt'])
                #     ins_reward_details.dbl_value_to = float(items['toAmt'])
                if items['slab1_percentage']:
                    ins_reward_assigned.dbl_slab1_percentage = float(items['slab1_percentage'])
                if items['slab1_amount']:
                    ins_reward_assigned.dbl_slab1_amount = float(items['slab1_amount'])

                if 'slab2_percentage' in items and items['slab2_percentage']:
                    ins_reward_assigned.dbl_slab2_percentage = float(items['slab2_percentage'])
                if 'slab2_amount' in items and items['slab2_amount']:
                    ins_reward_assigned.dbl_slab2_amount = float(items['slab2_amount'])

                if 'slab3_percentage' in items and items['slab3_percentage']:
                    ins_reward_assigned.dbl_slab3_percentage = float(items['slab3_percentage'])
                if 'slab3_amount' in items and items['slab3_amount']:
                    ins_reward_assigned.dbl_slab3_amount = float(items['slab3_amount'])
                # if 'reward_mop' in items and items['reward_mop']:
                #     ins_reward_details.int_mop_sale = 1
                # else:
                #     ins_reward_details.int_mop_sale = 0
                if items['reward_to'] == 1 or items['reward_to'] == 2 or items['reward_to'] == 3:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'STAFF')
                elif items['reward_to'] == 5:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'BRANCH MANAGER')
                elif items['reward_to'] == 4:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ASSISTANT BRANCH MANAGER')
                elif items['reward_to'] == 6:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'TERRITORY MANAGER')
                elif items['reward_to'] == 7:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ZONE MANAGER')

                ins_reward_assigned.int_to = items['reward_to']
                ins_reward_assigned.save()
            return Response({'status':'success','data':{}})
        except Exception as e:
            return Response({"status":"0","reason":str(e)})

    def patch(self,request):
        try:
            id = request.data.get('id')
            confirm = request.data.get('confirm')
            if confirm:
                RewardsMaster.objects.filter(pk_bint_id=id).update(int_status=-1,fk_updated_by = request.user.userdetails)
                RewardsDetails.objects.filter(fk_rewards_master_id=id).update(int_status=-1)
                RewardAssigned.objects.filter(fk_reward_details_id__fk_rewards_master_id = id).update(int_status=-1)
            elif RewardsAvailable.objects.filter(fk_rewards_master_id=id):
                return Response({'status':'success','data':'This reward already used by some Staff'})
            else:
                return Response({'status':'success','data':'Reward not used'})
            return Response({'status':'success'})
        except Exception as e:
            return Response({"status":"0","reason":str(e)})


class GetRewardDetails(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:

            session = Connection()
            branch_id = request.data.get('branch_id')
            # branch_id = 1
            #listig all staff id's and it reward amount
            rst_staff_list =session.query(RewardsAvailableJS.c.json_staff.label('staff_id'))\
                                .join(ItemEnquirySA,ItemEnquirySA.pk_bint_id==RewardsAvailableJS.c.fk_item_enquiry_id)\
                                .join(EnquiryMasterSA,EnquiryMasterSA.pk_bint_id==ItemEnquirySA.fk_enquiry_master_id)\
                                .filter(EnquiryMasterSA.fk_branch_id==branch_id,RewardsAvailableJS.c.json_staff!=None)

            # rst_staff_list =session.query(RewardsAvailableJS.c.json_staff.label('staff_id'))

            lst_staff_data=[]
            lst_staff_id=[]
            for ins_staff in rst_staff_list.all():
                for data in ins_staff:
                    for ins_staff_details in data:
                        if int(ins_staff_details) not in [(data["int_staff_id"]) for data in lst_staff_data]:
                            dct_data = {}
                            dct_data['int_staff_id'] = int(ins_staff_details)
                            lst_staff_id.append(int(ins_staff_details))
                            dct_data['int_dbl_amount'] = data[ins_staff_details]
                            lst_staff_data.append(dct_data)
                        else:
                            for ins_data in lst_staff_data:
                                if int(ins_staff_details) == ins_data['int_staff_id']:
                                    data[ins_staff_details]=data[ins_staff_details] if data[ins_staff_details] else 0
                                    ins_data['int_dbl_amount'] += data[ins_staff_details]

            # print(lst_staff_data)
            lst_branch_id=[]
            if request.user.userdetails.fk_department.vchr_code.upper() == 'HOD':
                lst_branch_id = list(Branch.objects.filter().values_list('pk_bint_id',flat=True))
                rst_staff_details =session.query(UserModelSA.user_ptr_id.label('staff_id'),\
                                                            func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
                                                            GroupsSA.vchr_name.label('designation'),\
                                                            BranchSA.vchr_name.label('branch_name'))\
                                                            .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
                                                            .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
                                                            .join(BranchSA,(BranchSA.pk_bint_id == UserModelSA.fk_branch_id) |(BranchSA.fk_territory_id== UserModelSA.int_area_id)).filter(and_(BranchSA.pk_bint_id.in_(lst_branch_id),BranchSA.pk_bint_id==branch_id))\
                                                            .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))
                rst_rewards_paid =session.query(RewardsPaidSA.fk_staff_id.label('staff_id'),\
                                func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
                                BranchSA.vchr_name.label('branch_name'))\
                                .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                                .join(BranchSA,(BranchSA.pk_bint_id == UserModelSA.fk_branch_id) | (BranchSA.fk_territory_id== UserModelSA.int_area_id)).filter(and_(BranchSA.pk_bint_id.in_(lst_branch_id),BranchSA.pk_bint_id==branch_id))\
                                .filter(RewardsPaidSA.dat_paid>='2019-06-25')\
                                .group_by('staff_id','branch_name')
            elif request.user.userdetails.int_area_id:
                lst_branch_id=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                # if request.user.userdetails.fk_group.vchr_name.upper()=='TERRITORY MANAGER':
                #     lst_area_id.append(request.user.userdetails.int_area_id)
                # else:
                #     lst_area_id.append(Branch.objects.filter(pk_bint_id__in=lst_branch_id).values_list(fk_territory_id).group_by(fk_territory_id))
                rst_staff_details =session.query(UserModelSA.user_ptr_id.label('staff_id'),\
                                                            func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
                                                            GroupsSA.vchr_name.label('designation'),\
                                                            BranchSA.vchr_name.label('branch_name'))\
                                                            .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
                                                            .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
                                                            .join(BranchSA,(BranchSA.pk_bint_id == UserModelSA.fk_branch_id) |(BranchSA.fk_territory_id== UserModelSA.int_area_id)).filter(and_(BranchSA.pk_bint_id.in_(lst_branch_id),BranchSA.pk_bint_id==branch_id))\
                                                            .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))
                rst_rewards_paid =session.query(RewardsPaidSA.fk_staff_id.label('staff_id'),\
                                func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
                                BranchSA.vchr_name.label('branch_name'))\
                                .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                                .join(BranchSA,(BranchSA.pk_bint_id == UserModelSA.fk_branch_id) | (BranchSA.fk_territory_id== UserModelSA.int_area_id)).filter(and_(BranchSA.pk_bint_id.in_(lst_branch_id),BranchSA.pk_bint_id==branch_id))\
                                .filter(RewardsPaidSA.dat_paid>='2019-06-25')\
                                .group_by('staff_id','branch_name')




            else:
                    lst_branch_id.append(request.user.userdetails.fk_branch_id)
            #taking details of staff
                    rst_staff_details =session.query(UserModelSA.user_ptr_id.label('staff_id'),\
                                            func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
                                            GroupsSA.vchr_name.label('designation'),\
                                            BranchSA.vchr_name.label('branch_name'))\
                                            .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
                                            .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
                                            .filter(and_(BranchSA.pk_bint_id==request.user.userdetails.fk_branch_id,BranchSA.pk_bint_id==branch_id))\
                                            .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))
                    rst_rewards_paid =session.query(RewardsPaidSA.fk_staff_id.label('staff_id'),\
                                    func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
                                    BranchSA.vchr_name.label('branch_name'))\
                                    .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                                    .join(BranchSA,(BranchSA.pk_bint_id == UserModelSA.fk_branch_id) | (BranchSA.fk_territory_id== UserModelSA.int_area_id))\
                                    .filter(and_(BranchSA.pk_bint_id==request.user.userdetails.fk_branch_id,BranchSA.pk_bint_id==branch_id))\
                                    .filter(RewardsPaidSA.dat_paid>='2019-06-25')\
                                    .group_by('staff_id','branch_name')

            rst_staff_list.filter()
            rst_rewards_paid.filter(BranchSA.pk_bint_id==branch_id)
            #listing all rewards available
            # rst_rewards_available =session.query(RewardsAvailableSA.fk_staff_id.label('staff_id'),\
            #                             func.sum(func.coalesce(RewardsAvailableSA.dbl_reward,0)).label('total_reward_earn'),\
            #                             func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
            #                             GroupsSA.vchr_name.label('designation'),\
            #                             BranchSA.vchr_name.label('branch_name'))\
            #                             .join(UserModelSA,UserModelSA.user_ptr_id == RewardsAvailableSA.fk_staff_id)\
            #                             .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
            #                             .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
            #                             .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                             .filter(BranchSA.pk_bint_id == branch_id)\
            #                             .group_by('staff_id','staff_name','designation','branch_name')
            # print(rst_rewards_available.all())



            #listing all rewards paid

                                # .filter()
            # print(rst_rewards_paid.all())
            # import pdb;
            # pdb.set_trace()
            #structuring
            lst_rewards_all = []
            for ins_staff_query in rst_staff_details.all():
                for ins_data in lst_staff_data:
                    if ins_data['int_staff_id'] == ins_staff_query.staff_id:
                        dct_reward_data={}
                        dct_reward_data['staff_id'] = ins_data['int_staff_id']
                        dct_reward_data['staff_name'] = ins_staff_query.staff_name
                        dct_reward_data['designation'] = ins_staff_query.designation
                        dct_reward_data['branch_name'] = ins_staff_query.branch_name
                        dct_reward_data['to_pay'] = None
                        dct_reward_data['reward_mop'] = False
                        dct_reward_data['total_reward'] = round(ins_data['int_dbl_amount'],2)
                        # substracting rewards available to rewards paid
                        for ins_reward_paid in rst_rewards_paid.all():
                            if ins_staff_query.staff_id == ins_reward_paid.staff_id:

                                dct_reward_data['total_reward'] = round(dct_reward_data['total_reward'] - ins_reward_paid.total_reward_paid,2)
                        lst_rewards_all.append(dct_reward_data)



            #structuring
            # lst_rewards_all = []
            # for ins_reward_available in rst_rewards_available.all():
            #     dct_rewards_all = {}
            #     dct_rewards_all['staff_id'] = ins_reward_available.staff_id
            #     dct_rewards_all['staff_name'] = ins_reward_available.staff_name
            #     dct_rewards_all['designation'] = ins_reward_available.designation
            #     dct_rewards_all['branch_name'] = ins_reward_available.branch_name
            #     dct_rewards_all['to_pay'] = None
            #     dct_rewards_all['reward_mop'] = False
            #     dct_rewards_all['total_reward'] = ins_reward_available.total_reward_earn
            #     # substracting rewards available to rewards paid
            #     for ins_reward_paid in rst_rewards_paid.all():
            #         if ins_reward_available.staff_id == ins_reward_paid.staff_id:
            #             dct_rewards_all['total_reward'] = round(dct_rewards_all['total_reward'] - ins_reward_paid.total_reward_paid,3)
            #     lst_rewards_all.append(dct_rewards_all)
            # print(lst_rewards_all)
            session.close()
            return Response({'status':'success','data':lst_rewards_all})
        except Exception as e:
            session.close()
            return Response({'status':'0','reason':str(e)})
class RewardPaidSave(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            lst_reward_data = request.data
            vchr_transaction_id = rd.randint(10000000,99999999)
            lst_pos_data = []
            dct_pos_data = {}
            for ins_paid in lst_reward_data:
                if ins_paid['reward_mop'] == True:
                    staff_id = ins_paid['staff_id']
                    paid_amount = ins_paid['to_pay']
                    if staff_id and paid_amount:
                        ins_reward_paid = RewardsPaid.objects.create(fk_staff_id=int(staff_id),dbl_paid=paid_amount,dat_paid=datetime.now(),int_status=0,fk_created_by=request.user.userdetails,vchr_transaction_id=vchr_transaction_id,fk_branch_id=request.user.userdetails.fk_branch_id)
                        dct_item = {}
                        dct_item['staff_code'] = User.objects.get(id=staff_id,is_active=True).username
                        # dct_item['branch_code'] = request.user.userdetails.fk_branch.vchr_code
                        dct_item['amount'] = paid_amount
                        # dct_item['dat_created'] = datetime.now()
                        # dct_item['created_by'] = request.user.username
                        dct_item['vchr_transaction_id'] = vchr_transaction_id
                        lst_pos_data.append(dct_item)
                    else:
                        return Response({'status':'failed'})
            if lst_pos_data:
                dct_pos_data['branch_code'] = request.user.userdetails.fk_branch.vchr_code
                dct_pos_data['dat_created'] = datetime.strftime(datetime.now(),'%Y-%m-%d')
                dct_pos_data['created_by'] = request.user.username
                dct_pos_data['lstIncentive']=lst_pos_data
                url = settings.POS_HOSTNAME+"/payment/addincentive/"
                res_data = requests.post(url,json=dct_pos_data)
                if res_data.json().get('status')==1:
                    pass
                else:
                    return Response({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
            return Response({'status':'success', 'vchr_transaction_id' : vchr_transaction_id })
        except Exception as e:
            return Response({'status':'0','reason':str(e)})


class AreaSearch(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            area_type = request.data.get('area_type')
            lst_area=[]
            if area_type.upper() == 'ZONE':
                lst_area = Zone.objects.filter(chr_status = 'N').values('pk_bint_id','vchr_name')
            elif area_type.upper() == 'TERRITORY':
                lst_area = Territory.objects.filter(chr_status = 'N').values('pk_bint_id','vchr_name')
            elif area_type.upper() == 'BRANCH':
                lst_area = Branch.objects.filter().values('pk_bint_id','vchr_name')
            else:
                return Response({'status':'failed','reason':'No data'})
            return Response({'status':'success','data':lst_area})
        except Exception as e:
            return Response({'status':'0','reason':str(e)})


class RewardsList(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request):
        try:

            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            lst_id = []
            ins_reward_master = RewardsDetails.objects.filter(Q(fk_rewards_master__dat_from__range=(dat_from,dat_to))|Q(fk_rewards_master__dat_to__range=(dat_from,dat_to))|Q(fk_rewards_master__dat_from__lte=dat_from,fk_rewards_master__dat_to__gte=dat_from)|Q(fk_rewards_master__dat_from__lte=dat_to,fk_rewards_master__dat_to__gte=dat_to),int_map_type__lte=4).values('fk_rewards_master__pk_bint_id','fk_rewards_master__vchr_area_type','fk_rewards_master__vchr_reward_name','fk_rewards_master__dat_from','fk_rewards_master__dat_to','fk_rewards_master__json_branch','int_map_type').order_by('-pk_bint_id')
            # ins_reward_master = RewardsDetails.objects.filter(Q(fk_rewards_master__dat_from__range=(dat_from,dat_to))|Q(fk_rewards_master__dat_to__range=(dat_from,dat_to))).values('fk_rewards_master__pk_bint_id','fk_rewards_master__vchr_area_type','fk_rewards_master__vchr_reward_name','fk_rewards_master__dat_from','fk_rewards_master__dat_to','fk_rewards_master__json_branch','int_map_type').order_by('-pk_bint_id')
            lst_data = []
            ins_branch={data['pk_bint_id']:[data['vchr_name'],data] for data in Branch.objects.values('pk_bint_id','vchr_name','fk_territory__vchr_name','fk_territory__fk_zone__vchr_name')}
            for ins_data in ins_reward_master:
                dct_data = {}
                dct_data['id'] = ins_data['fk_rewards_master__pk_bint_id']
                dct_data['reward_name'] = ins_data['fk_rewards_master__vchr_reward_name'].title()
                dct_data['date_range'] = datetime.strftime(ins_data['fk_rewards_master__dat_from'],"%d-%m-%Y")+' - '+datetime.strftime(ins_data['fk_rewards_master__dat_to'],"%d-%m-%Y")
                if ins_data['int_map_type'] == 0:
                    dct_data['category'] = 'Product Wise'
                elif ins_data['int_map_type'] == 1:
                    dct_data['category'] = 'Brand Wise'
                elif ins_data['int_map_type'] == 2:
                    dct_data['category'] = 'Item Wise'
                elif ins_data['int_map_type'] == 3:
                    dct_data['category'] = 'Value Wise'
                elif ins_data['int_map_type'] == 4:
                    dct_data['category'] = 'TurnOver Wise'
                dct_data['branch'] = []
                for branch in ins_data['fk_rewards_master__json_branch']['branch_id']:
                    if ins_data['fk_rewards_master__vchr_area_type'] == 'TERRITORY' and ins_branch[int(branch)][1]['fk_territory__vchr_name'].title() not in dct_data['branch']:
                        dct_data['branch'].append(ins_branch[int(branch)][1]['fk_territory__vchr_name'].title())
                    elif ins_data['fk_rewards_master__vchr_area_type'] == 'ZONE' and ins_branch[int(branch)][1]['fk_territory__fk_zone__vchr_name'].title() not in dct_data['branch']:
                        dct_data['branch'].append(ins_branch[int(branch)][1]['fk_territory__fk_zone__vchr_name'].title())
                    elif ins_data['fk_rewards_master__vchr_area_type'] == 'BRANCH':
                        dct_data['branch'].append(ins_branch[int(branch)][0].title())
                    elif ins_data['int_map_type'] == 4:
                        dct_data['branch'].append(ins_branch[int(branch)][0].title())
                if len(dct_data['branch'])>1:
                    dct_data['branch'] = dct_data['branch'][0]+', ..'
                else:
                    dct_data['branch'] = dct_data['branch'][0]
                if ins_data['fk_rewards_master__pk_bint_id'] not in lst_id:
                    lst_data.append(dct_data)
                    lst_id.append(ins_data['fk_rewards_master__pk_bint_id'])
            return Response({'status':'success','data':lst_data})
        except Exception as e:
            return Response({'status':'0','reason':str(e)})

    def post(self,request):
        try:
            id = request.data.get('id')
            ins_reward_master = RewardsMaster.objects.filter(pk_bint_id=id).values('pk_bint_id','dat_from','dat_to','vchr_area_type','json_branch','vchr_reward_name','dbl_slab1_percentage','dbl_slab2_percentage','dbl_slab3_percentage')[0]

            ins_reward_details = RewardsDetails.objects.filter(fk_rewards_master_id = ins_reward_master['pk_bint_id']).exclude(int_status=-1).values()

            ins_reward_assigned = RewardAssigned.objects.filter(fk_reward_details_id = ins_reward_details[0]['pk_bint_id']).exclude(int_status=-1).values()
            dct_data = {}
            dct_data['from_date'] = ins_reward_master['dat_from']
            dct_data['to_date'] = ins_reward_master['dat_to']
            dct_data['branch'] = []
            dct_data['branch_id'] = []
            dct_data['zone'] = []
            dct_data['zone_id'] = []
            dct_data['territory'] = []
            dct_data['territory_id'] = []
            lst_branch_id = [int(id) for id in ins_reward_master['json_branch']['branch_id']]
            ins_branch = Branch.objects.filter(pk_bint_id__in=lst_branch_id).values('pk_bint_id','vchr_name','fk_territory__vchr_name','fk_territory__pk_bint_id','fk_territory__fk_zone__vchr_name','fk_territory__fk_zone__pk_bint_id')

            for branch in ins_branch:
                if ins_reward_master['vchr_area_type']=='TERRITORY' and branch['fk_territory__vchr_name'].title() not in dct_data['territory']:
                    dct_data['territory'].append(branch['fk_territory__vchr_name'].title())
                    dct_data['territory_id'].append(branch['fk_territory__pk_bint_id'])
                elif ins_reward_master['vchr_area_type']=='ZONE' and branch['fk_territory__fk_zone__vchr_name'].title() not in dct_data['zone']:
                    dct_data['zone'].append(branch['fk_territory__fk_zone__vchr_name'].title())
                    dct_data['zone_id'].append(branch['fk_territory__fk_zone__pk_bint_id'])
                elif ins_reward_master['vchr_area_type']=='BRANCH':
                    dct_data['branch'].append(branch['vchr_name'].title())
                    dct_data['branch_id'].append(branch['pk_bint_id'])
                elif ins_reward_details[0]['int_map_type']==4:
                    dct_data['branch'].append(branch['vchr_name'].title())
                    dct_data['branch_id'].append(branch['pk_bint_id'])

            if ins_reward_details[0]['int_map_type'] == 0:
                dct_data['category'] = 'Product Wise'
            elif ins_reward_details[0]['int_map_type'] == 1:
                dct_data['category'] = 'Brand Wise'
            elif ins_reward_details[0]['int_map_type'] == 2:
                dct_data['category'] = 'Item Wise'
            elif ins_reward_details[0]['int_map_type'] == 3:
                dct_data['category'] = 'Value Wise'
            elif ins_reward_details[0]['int_map_type'] == 4:
                dct_data['category'] = 'TurnOver Wise'

            dct_data['reward_name'] = ins_reward_master['vchr_reward_name'].title()
            dct_data['slab1_percentage'] = ins_reward_master['dbl_slab1_percentage']
            dct_data['slab2_percentage'] = ins_reward_master['dbl_slab2_percentage']
            dct_data['slab3_percentage'] = ins_reward_master['dbl_slab3_percentage']
            dct_data['items'] = []

            for items in ins_reward_assigned:
                dct_item = {}

                dct_item['quantity_from'] = ins_reward_details[0]['int_quantity_from']
                dct_item['quantity_to'] = ins_reward_details[0]['int_quantity_to']
                dct_item['value_from'] = ins_reward_details[0]['dbl_value_from']
                dct_item['value_to'] = ins_reward_details[0]['dbl_value_to']
                dct_item['slab1_percentage'] = items['dbl_slab1_percentage']
                dct_item['slab1_amount'] = items['dbl_slab1_amount']
                dct_item['slab2_percentage'] = items['dbl_slab2_percentage']
                dct_item['slab2_amount'] = items['dbl_slab2_amount']
                dct_item['slab3_percentage'] = items['dbl_slab3_percentage']
                dct_item['slab3_amount'] = items['dbl_slab3_amount']
                dct_item['assign_id'] = items['int_to']
                if ins_reward_details[0]['int_mop_sale'] == 1:
                    dct_item['mop_sale'] = True
                else:
                    ins_reward_details[0]['mop_sale'] = False

                if items['int_to'] == 1:
                    dct_item['assign_to'] = 'All Sales Men'
                elif items['int_to'] == 2:
                    dct_item['assign_to'] = 'Promoter'
                elif items['int_to'] == 3:
                    dct_item['assign_to'] = 'Non-Promoter'
                elif items['int_to'] == 4:
                    dct_item['assign_to'] = 'Ass.Branch Manager'
                elif items['int_to'] == 5:
                    dct_item['assign_to'] = 'Branch Manager'
                elif items['int_to'] == 6:
                    dct_item['assign_to'] = 'Territory Manager'
                elif items['int_to'] == 7:
                    dct_item['assign_to'] = 'Zone Manager'


                if ins_reward_details[0]['int_map_type'] == 0:
                    product = Products.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_product_name')[0]
                    dct_item['product_name'] = product['vchr_product_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 1:
                    product = Brands.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_brand_name')[0]
                    dct_item['brand_name'] = product['vchr_brand_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 2:
                    product = Items.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_item_name','fk_product__vchr_product_name','fk_product__id')[0]
                    dct_item['product_name'] = product['fk_product__vchr_product_name'].title()
                    dct_item['item_name'] = product['vchr_item_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 3:
                    product = Products.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_product_name')[0]
                    dct_item['product_name'] = product['vchr_product_name'].title()
                    dct_item['map_id'] = product['id']
                dct_data['items'].append(dct_item)

            return Response({'status':'success','data':dct_data})
        except Exception as e:
            return Response({'status':'0','reason':str(e)})




class StaffRewardList(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request):

        """ To list the staffs who got rewards.
            return : list of dictionary has values staff_name staff_id, branch_name, reward_earn, fk_staff_id, reward_paid, reward_balance """

        try:
            session = Connection()
            dat_from = datetime.strptime(request.data.get('datFrom'), '%d/%m/%Y' )
            dat_to = datetime.strptime(request.data.get('datTo'), '%d/%m/%Y' ) + timedelta(days = 1)
            str_type = request.data.get('strType') or  ""
            int_area_id = request.data.get('intAreaId') or None
            int_staff_id = request.data.get('intStaffId')
            lst_branch=[]

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MARKETING','AUDITOR','AUDITING ADMIN','B TEAM','PRODUCT MANAGER']:
                lst_branch = list(Branch.objects.filter(fk_company_id=request.user.userdetails.fk_company_id).values_list('pk_bint_id',flat=True))
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']:
                lst_branch = [request.user.userdetails.fk_branch_id]
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            # listig all staff id's and it reward amount
            rst_staff_list = session.query(RewardsAvailableJS.c.json_staff.label('staff_id'))\
                                .outerjoin(ItemEnquirySA,ItemEnquirySA.pk_bint_id==RewardsAvailableJS.c.fk_item_enquiry_id)\
                                .outerjoin(EnquiryMasterSA,EnquiryMasterSA.pk_bint_id==ItemEnquirySA.fk_enquiry_master_id)\
                                .filter(and_(or_(EnquiryMasterSA.fk_branch_id.in_(lst_branch),RewardsAvailableJS.c.fk_item_enquiry_id==None),RewardsAvailableJS.c.json_staff!=None))\
                                .filter(and_(RewardsAvailableJS.c.dat_reward >= dat_from,RewardsAvailableJS.c.dat_reward <= dat_to))

            lst_users_avail=GetUserList(request)
            dct_staff_data={}
            lst_staff_id=[]
            # for ins_staff in rst_staff_list.all():
            #     for data in ins_staff:
            #         for ins_staff_details in data:
            #             if int(ins_staff_details) not in [(data["int_staff_id"]) for data in lst_staff_data]:
            #                 dct_data = {}
            #                 dct_data['int_staff_id'] = int(ins_staff_details)
            #                 lst_staff_id.append(int(ins_staff_details))
            #                 dct_data['int_dbl_amount'] = data[ins_staff_details]
            #                 lst_staff_data.append(dct_data)
            #             else:
            #                 for ins_data in lst_staff_data:
            #                     if int(ins_staff_details) == ins_data['int_staff_id']:
            #                         ins_data['int_dbl_amount'] += data[ins_staff_details]
            for ins_staff in rst_staff_list.all():
                for data in ins_staff:
                    for ins_staff_details in data:
                        if int(ins_staff_details) not in list(dct_staff_data.keys()):

                            dct_staff_data[int(ins_staff_details)] = data[ins_staff_details]
                            lst_staff_id.append(int(ins_staff_details))
                        else:
                            dct_staff_data[int(ins_staff_details)] += data[ins_staff_details]

            rst_staff_details = session.query(UserModelSA.user_ptr_id.label('staff_id'),GroupsSA.vchr_name.label('group_name'),TerritorySA.vchr_name.label('territory_name'),BranchSA.pk_bint_id.label('branch_id'),\
                                            func.concat(AuthUserSA.first_name, " ", AuthUserSA.last_name).label('staff_name'),\
                                            case([(and_(UserModelSA.fk_branch_id != None, UserModelSA.int_area_id == None), BranchSA.vchr_name),(and_(UserModelSA.int_area_id != None, GroupsSA.vchr_name == 'TERRITORY MANAGER'), TerritorySA.vchr_name),(and_(UserModelSA.int_area_id != None, GroupsSA.vchr_name == 'ZONE MANAGER'), ZoneSA.vchr_name),(and_(UserModelSA.int_area_id != None, GroupsSA.vchr_name == 'STATE HEAD'), StateSA.vchr_name),(and_(UserModelSA.int_area_id != None, GroupsSA.vchr_name == 'COUNTRY MANAGER'), CountrySA.vchr_country_name)],else_=literal_column("NULL")).label('area_name'))\
                                            .join(AuthUserSA, AuthUserSA.id == UserModelSA.user_ptr_id)\
                                            .join(GroupsSA, GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
                                            .outerjoin(BranchSA, and_(BranchSA.pk_bint_id == UserModelSA.fk_branch_id, UserModelSA.fk_branch_id != None))\
                                            .outerjoin(TerritorySA, and_(TerritorySA.pk_bint_id == UserModelSA.int_area_id, GroupsSA.vchr_name == 'TERRITORY MANAGER'))\
                                            .outerjoin(ZoneSA, and_(ZoneSA.pk_bint_id == UserModelSA.int_area_id, GroupsSA.vchr_name == 'ZONE MANAGER'))\
                                            .outerjoin(StateSA, and_(TerritorySA.pk_bint_id == UserModelSA.int_area_id, GroupsSA.vchr_name == 'STATE MANAGER'))\
                                            .outerjoin(CountrySA, and_(TerritorySA.pk_bint_id == UserModelSA.int_area_id, GroupsSA.vchr_name == 'COUNTRY MANAGER'))\
                                            .filter(and_(UserModelSA.user_ptr_id.in_(lst_staff_id),UserModelSA.user_ptr_id.in_(lst_users_avail)))

            rst_rewards_paid = session.query(RewardsPaidSA.fk_staff_id.label('staff_id'),\
                                func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'))\
                                .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                                .filter(and_(RewardsPaidSA.dat_paid >= dat_from,RewardsPaidSA.dat_paid <= dat_to))\
                                .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))\
                                .group_by('staff_id')
            dct_rewards_paid={int(data[0]):data[1] for data in rst_rewards_paid.all()}

            flagt=False
            flagz=False
            flagb=False
            if str_type.upper() == 'ALL':
                rst_staff_details = rst_staff_details.filter(GroupsSA.vchr_name.in_(['TERRITORY MANAGER','ZONE MANAGER','STATE MANAGER','COUNTRY MANAGER','B TEAM','PRODUCT MANAGER']))
            elif str_type.upper() == 'BRANCH' and int_area_id:
                rst_staff_details = rst_staff_details.filter(and_(UserModelSA.fk_branch_id ==int_area_id,GroupsSA.vchr_name.in_(['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','STAFF','Floor Manager1','Floor Manager2','Floor Manager3','Floor Manager4','ASM1','ASM2','ASM3','ASM4'])))
            elif str_type.upper() == 'BRANCH' and  int_area_id==None and request.user.userdetails.fk_group.vchr_name!="STAFF":
                flagt=True
                # rst_rewards_paid = session.query(func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
                #                     BranchSA.pk_bint_id.label('branch_id'),\
                #                     BranchSA.vchr_name.label('branch_name'))\
                #                     .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                #                     .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
                #                     .filter(and_(RewardsPaidSA.dat_paid >= dat_from,RewardsPaidSA.dat_paid <= dat_to))\
                #                     .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))\
                #                     .group_by('branch_id','branch_name')

            elif str_type.upper() == 'TERRITORY' and int_area_id:
                        branch_list=show_data_based_on_role("TERRITORY MANAGER",int_area_id)

                        flagt=True
                        rst_staff_details = rst_staff_details.filter(UserModelSA.fk_branch_id.in_(branch_list))
                        if request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']:
                                                session.close()
                                                return Response({'status':'success','data':[]})


            elif str_type.upper() == 'ZONE' and int_area_id :
                branch_list=show_data_based_on_role("ZONE MANAGER",int_area_id)
                flagz=True
                territory_list=list(Territory.objects.filter(fk_zone_id=int_area_id).values_list("pk_bint_id",flat=True))
                rst_staff_details = rst_staff_details.filter(or_(UserModelSA.int_area_id.in_(territory_list),UserModelSA.fk_branch_id.in_(branch_list)))
                if request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']:
                                        session.close()
                                        return Response({'status':'success','data':[]})

            elif str_type.upper() == 'TERRITORY':
                rst_staff_details = rst_staff_details.filter(GroupsSA.vchr_name=='TERRITORY MANAGER')

            elif str_type.upper() == 'ZONE' :
                rst_staff_details = rst_staff_details.filter(GroupsSA.vchr_name=='ZONE MANAGER')
            elif str_type.upper() == 'PRODUCT MANAGER' or request.user.userdetails.fk_group.vchr_name.upper()=='' :
                rst_staff_details = rst_staff_details.filter(GroupsSA.vchr_name=='PRODUCT MANAGER')
                flagb=True
            elif str_type.upper() == 'B TEAM' or request.user.userdetails.fk_group.vchr_name.upper()=='B TEAM':
                rst_staff_details = rst_staff_details.filter(GroupsSA.vchr_name=='B TEAM')
                flagb=True

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ASSISTANT BRANCH MANAGER','FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']:
                rst_staff_details=rst_staff_details.filter(GroupsSA.vchr_name!='BRANCH MANAGER')
            if (str_type.upper()=='BRANCH' or (str_type.upper() == 'TERRITORY' and int_area_id) or (str_type.upper()=='ALL') and request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','STAFF','ASSISTANT BRANCH MANAGER','FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']) or request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN','ZONE MANAGER','TERRITORY MANAGER','PRODUCT MANAGER','B TEAM']:
                    pass
            else:
                session.close()
                return Response({'status':'success','data':[]})

            # if int_branch_id:
            #     #listing all rewards paid
            #     rst_rewards_paid = session.query(RewardsPaidSA.fk_staff_id.label('staff_id'),\
            #                         func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
            #                         BranchSA.vchr_name.label('branch_name'))\
            #                         .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
            #                         .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                         .filter(BranchSA.pk_bint_id == int_branch_id )\
            #                         .filter(and_(RewardsPaidSA.dat_paid >= dat_from,RewardsPaidSA.dat_paid <= dat_to))\
            #                         .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))\
            #                         .group_by('staff_id','branch_name')
            # else:
            #     #listing all rewards paid
            #     rst_rewards_paid = session.query(func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
            #                         BranchSA.pk_bint_id.label('branch_id'),\
            #                         BranchSA.vchr_name.label('branch_name'))\
            #                         .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
            #                         .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                         .filter(BranchSA.pk_bint_id == int_branch_id )\
            #                         .filter(and_(RewardsPaidSA.dat_paid >= dat_from,RewardsPaidSA.dat_paid <= dat_to))\
            #                         .group_by('branch_id','branch_name')
            #
            lst_data=[]
            # if int_staff_id:
            #     rst_staff_details = session.query(UserModelSA.user_ptr_id.label('staff_id'),\
            #                                     func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
            #                                     BranchSA.vchr_name.label('branch_name'))\
            #                                     .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
            #                                     .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                                     .filter(UserModelSA.user_ptr_id == int_staff_id)


            # if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN']:
            #     pass
            # elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
            #     rst_staff_details = session.query(UserModelSA.user_ptr_id.label('staff_id'),\
            #                                     func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
            #                                     BranchSA.vchr_name.label('branch_name'))\
            #                                     .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
            #                                     .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                                     .filter(BranchSA.pk_bint_id == request.user.userdetails.fk_branch_id)
            #
            #
            # elif request.user.userdetails.fk_group.vchr_name.upper()=='ASSISTANT BRANCH MANAGER':
            #     rst_staff_details = session.query(UserModelSA.user_ptr_id.label('staff_id'),\
            #                                     func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
            #                                     BranchSA.vchr_name.label('branch_name'))\
            #                                     .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
            #                                     .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
            #                                     .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                                     .filter(BranchSA.pk_bint_id == request.user.userdetails.fk_branch_id)\
            #                                     .filter(GroupsSA.vchr_name != 'BRANCH MANAGER' )
            #
            #
            # elif request.user.userdetails.int_area_id:
            #     lst_branch = show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
            #     rst_staff_details = session.query(UserModelSA.user_ptr_id.label('staff_id'),\
            #                                     func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
            #                                     BranchSA.vchr_name.label('branch_name'))\
            #                                     .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
            #                                     .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
            #                                     .filter(BranchSA.pk_bint_id.in_(lst_branch))
            #
            # if int_branch_id:
            #     rst_staff_details = rst_staff_details.filter(BranchSA.pk_bint_id==int_branch_id)
            #structuring
            lst_branch=Branch.objects.values("fk_territory__vchr_name","pk_bint_id")
            dct_branch={}
            dct_exists={}
            for ins_staff_query in rst_staff_details.all():
                        # if flag and ins_staff_query.group_name=="STAFF":
                            dct_reward_data={}
                            if not flagb:
                                dct_reward_data['strAreaName'] = ins_staff_query.area_name
                            else:
                                dct_reward_data['strAreaName'] = ins_staff_query.staff_name
                            dct_reward_data['reward_earn'] = round(dct_staff_data[int(ins_staff_query.staff_id)],2)
                            if (str_type.upper() == 'BRANCH STAFF' and int_area_id) or str_type.upper() != 'BRANCH STAFF' and not flagb :
                                dct_reward_data['strName'] = ins_staff_query.staff_name
                            dct_reward_data['reward_paid'] = 0
                            dct_reward_data['reward_balance'] = round(dct_staff_data[int(ins_staff_query.staff_id)],2)
                            # substracting rewards available to rewards paid
                            # for ins_reward_paid in rst_rewards_paid.all():
                            #     if ins_staff_query.staff_id == ins_reward_paid.staff_id:
                            #         dct_reward_data['reward_paid'] = round(ins_reward_paid.total_reward_paid,2)
                            #         dct_reward_data['reward_balance'] = round(dct_reward_data['reward_balance'] - ins_reward_paid.total_reward_paid,2)
                            if int(ins_staff_query.staff_id) in dct_rewards_paid:
                                dct_reward_data['reward_paid'] = round(dct_rewards_paid[int(ins_staff_query.staff_id)],2)
                                dct_reward_data['reward_balance'] = round(dct_reward_data['reward_balance'] - dct_rewards_paid[int(ins_staff_query.staff_id)],2)


                            if flagt:
                                if ins_staff_query.group_name=="STAFF" or ins_staff_query.group_name=="BRANCH MANAGER" or ins_staff_query.group_name=="ASSISTANT BRANCH MANAGER" or ins_staff_query.group_name.upper() in ['FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']:
                                    dct_reward_data['bt']=ins_staff_query.area_name
                            if flagz:
                                if ins_staff_query.group_name=="STAFF" or ins_staff_query.group_name=="BRANCH MANAGER" or ins_staff_query.group_name=="ASSISTANT BRANCH MANAGER" or ins_staff_query.group_name.upper() in ['FLOOR MANAGER1','FLOOR MANAGER2','FLOOR MANAGER3','FLOOR MANAGER4','ASM1','ASM2','ASM3','ASM4']:
                                    dct_reward_data['bt']=lst_branch.filter(pk_bint_id=ins_staff_query.branch_id).values('fk_territory__vchr_name').first()['fk_territory__vchr_name']
                                if ins_staff_query.group_name=="TERRITORY MANAGER":
                                    dct_reward_data['bt']=ins_staff_query.territory_name
                            if flagt or flagz:
                                if 'bt' in dct_reward_data:
                                        if not dct_reward_data['bt'] in dct_branch:
                                            dct_branch[dct_reward_data['bt']]={}
                                            if flagz:
                                                dct_branch[dct_reward_data['bt']]['strAreaName']=dct_reward_data['bt']
                                            else:
                                                dct_branch[dct_reward_data['bt']]['strAreaName']=dct_reward_data['strAreaName']
                                            dct_branch[dct_reward_data['bt']]['reward_earn']=dct_reward_data['reward_earn']
                                            dct_branch[dct_reward_data['bt']]['reward_balance']=dct_reward_data['reward_balance']
                                            dct_branch[dct_reward_data['bt']]['reward_paid']=dct_reward_data['reward_paid']
                                        else:
                                            dct_branch[dct_reward_data['bt']]['reward_earn']=dct_branch[dct_reward_data['bt']]['reward_earn']+dct_reward_data['reward_earn']
                                            dct_branch[dct_reward_data['bt']]['reward_paid']=dct_branch[dct_reward_data['bt']]['reward_paid']+dct_reward_data['reward_paid']
                                            dct_branch[dct_reward_data['bt']]['reward_balance']=dct_branch[dct_reward_data['bt']]['reward_balance']+dct_reward_data['reward_balance']
                            lst_data.append(dct_reward_data)
            # import pdb;pdb.set_trace()
            if flagt or flagz :
            #
            #         dct_branch={}
            #         dct_exists={}
            #         for dct_reward_data in lst_data:
            #
            #             if 'bt' in dct_reward_data:
            #                 if not dct_reward_data['bt'] in dct_branch:
            #                     dct_branch[dct_reward_data['bt']]={}
            #                     if flagz:
            #                         dct_branch[dct_reward_data['bt']]['strAreaName']=dct_reward_data['bt']
            #                     else:
            #                         dct_branch[dct_reward_data['bt']]['strAreaName']=dct_reward_data['strAreaName']
            #                     dct_branch[dct_reward_data['bt']]['reward_earn']=dct_reward_data['reward_earn']
            #                     dct_branch[dct_reward_data['bt']]['reward_balance']=dct_reward_data['reward_balance']
            #                     dct_branch[dct_reward_data['bt']]['reward_paid']=dct_reward_data['reward_paid']
            #                 else:
            #                     dct_branch[dct_reward_data['bt']]['reward_earn']=dct_branch[dct_reward_data['bt']]['reward_earn']+dct_reward_data['reward_earn']
            #                     dct_branch[dct_reward_data['bt']]['reward_paid']=dct_branch[dct_reward_data['bt']]['reward_paid']+dct_reward_data['reward_paid']
            #                     dct_branch[dct_reward_data['bt']]['reward_balance']=dct_branch[dct_reward_data['bt']]['reward_balance']+dct_reward_data['reward_balance']
            #         # import pdb; pdb.set_trace()
                    # lst_data1=[]
                    # for dct_reward_data in lst_data:
                    #         if 'bt' in dct_reward_data and dct_reward_data['bt'] not in dct_exists:
                    #             dct_exists[dct_reward_data['bt']]=False
                    #             lst_data1.append(dct_branch[dct_reward_data['bt']])
                    # for key in dct_branch:
                    #     lst_data1.append(dct_branch[key])
                    lst_data1=[dct_branch[key] for key in dct_branch]
                    session.close()
                    return Response({'status':'success','data':lst_data1})
            session.close()
            return Response({'status':'success','data':lst_data})
        except Exception as e:
            session.close()
            return Response({'status':'failed','reason':str(e)})

    def post(self,request):

        """ To list the staff's details who got rewards.
            param : datFrom,datTo,intBranchId,intStaffId
            return : list of dictionary has values dat_created_at, enq_number, staff_name, branch_name, reward_amount """

        try:
            session = Connection()
            dat_from = datetime.strptime(request.data.get('datFrom'), '%d/%m/%Y' )
            dat_to = datetime.strptime(request.data.get('datTo'), '%d/%m/%Y' ) + timedelta(days = 1)
            int_branch_id = request.data.get('intBranchId')
            int_staff_id = request.data.get('intStaffId')
            int_area_id=request.data.get('intAreaId')
            str_type=request.data.get('strType') or ""
            # ins_reward_available = RewardsAvailable.objects.values('fk_staff_id','fk_staff__fk_branch__vchr_name','fk_item_enquiry__fk_enquiry_master__vchr_enquiry_num').filter(dat_reward__range=(dat_from,dat_to)).annotate(reward_earn=Sum('dbl_reward'),dat_reward=Cast('dat_reward', DateField()),staff_name=Concat('fk_staff__first_name',Value(' '),'fk_staff__last_name')).order_by('-dat_reward','-fk_item_enquiry__fk_enquiry_master__vchr_enquiry_num')

            rst_staff_list =session.query(RewardsAvailableJS.c.json_staff.label('staff_id'),EnquiryMasterSA.vchr_enquiry_num.label('enquiry_num'),RewardsAvailableJS.c.dat_reward.label('dat_reward'))\
                                        .outerjoin(ItemEnquirySA,ItemEnquirySA.pk_bint_id == RewardsAvailableJS.c.fk_item_enquiry_id)\
                                        .outerjoin(EnquiryMasterSA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                        .filter(and_(RewardsAvailableJS.c.dat_reward >= dat_from,RewardsAvailableJS.c.dat_reward <= dat_to))

            lst_staff_data=[]
            lst_staff_id=[]
            lst_users_avail=GetUserList(request)
            for ins_staff in rst_staff_list.all():
                count = 0 #for taking only staff_id in query in looping
                for data in ins_staff:
                    if count == 0 :
                        count += 1
                        for ins_staff_details in data:
                            # if int(ins_staff_details) not in [(data["int_staff_id"]) for data in lst_staff_data]:
                            dct_data = {}
                            dct_data['int_staff_id'] = int(ins_staff_details)
                            lst_staff_id.append(int(ins_staff_details))
                            dct_data['int_dbl_amount'] = data[ins_staff_details]
                            dct_data['dat_created_at'] = datetime.strftime(ins_staff[2],"%d-%m-%Y")
                            dct_data['enq_number'] = ins_staff[1] if ins_staff[1] else "Not Applicable"
                            lst_staff_data.append(dct_data)
                            # else:
                            #     for ins_data in lst_staff_data:
                            #         if int(ins_staff_details) == ins_data['int_staff_id']:
                            #             ins_data['int_dbl_amount'] += data[ins_staff_details]

            flagt=False
            flagz=False
                #taking details of staff
            rst_staff_details =session.query(UserModelSA.user_ptr_id.label('staff_id'),ZoneSA.pk_bint_id.label('zone_id'),\
                                            func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
                                            BranchSA.vchr_name.label('branch_name'),\
                                            TerritorySA.vchr_name.label('t_name'))\
                                            .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
                                            .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
                                            .outerjoin(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
                                            .outerjoin(TerritorySA,and_(UserModelSA.int_area_id==TerritorySA.pk_bint_id,GroupsSA.vchr_name=="TERRITORY MANAGER"))\
                                            .outerjoin(ZoneSA,and_(UserModelSA.int_area_id==ZoneSA.pk_bint_id,GroupsSA.vchr_name=="ZONE MANAGER"))\
                                            .filter(and_(UserModelSA.user_ptr_id.in_(lst_staff_id),UserModelSA.user_ptr_id.in_(lst_users_avail)))

            if int_branch_id:
                # ins_reward_available = ins_reward_available.filter(fk_staff__fk_branch_id=int_branch_id)
                rst_staff_details = rst_staff_details.filter(BranchSA.pk_bint_id == int_branch_id)


            if int_staff_id:
                # ins_reward_available = ins_reward_available.filter(fk_staff_id=int_staff_id)

                rst_staff_details = rst_staff_details.filter(UserModelSA.user_ptr_id == int_staff_id)
            flagb=False
            lst_data = []
            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
                # ins_reward_available = ins_reward_available.filter(fk_staff__fk_branch=request.user.userdetails.fk_branch)
                rst_staff_details = rst_staff_details.filter(BranchSA.pk_bint_id == request.user.userdetails.fk_branch_id)
            elif request.user.userdetails.fk_group.vchr_name.upper()=='ASSISTANT BRANCH MANAGER':
                # ins_reward_available = ins_reward_available.filter(fk_staff__fk_branch=request.user.userdetails.fk_branch).exclude(fk_staff__fk_group__vchr_name='BRANCH MANAGER')
                rst_staff_details = rst_staff_details.filter(BranchSA.pk_bint_id == request.user.userdetails.fk_branch_id).filter(GroupsSA.vchr_name != 'BRANCH MANAGER')
            if str_type.upper()=='BRANCH':
                rst_staff_details=rst_staff_details.filter(and_(UserModelSA.fk_branch_id!=None,UserModelSA.int_area_id==None,GroupsSA.vchr_name.in_(['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','STAFF'])))
            if str_type.upper()=='BRANCH' and int_area_id:
                rst_staff_details=rst_staff_details.filter(and_(UserModelSA.fk_branch_id==int_area_id,UserModelSA.int_area_id==None,GroupsSA.vchr_name.in_(['BRANCH MANAGER','ASSISTANT BRANCH MANAGER','STAFF'])))

            if str_type.upper()=='TERRITORY' and int_area_id:
                flagt=True
                rst_staff_details=rst_staff_details.filter(and_(GroupsSA.vchr_name=="TERRITORY MANAGER",UserModelSA.int_area_id==int_area_id))
            elif str_type.upper()=='ZONE' and int_area_id:
                flagz=True
                rst_staff_details=rst_staff_details.filter(and_(GroupsSA.vchr_name=="ZONE MANAGER",UserModelSA.int_area_id==int_area_id))
            elif str_type.upper()=='PRODUCT MANAGER':
                rst_staff_details=rst_staff_details.filter(GroupsSA.vchr_name=="PRODUCT MANAGER")
                flagb=True
            elif str_type.upper()=='B TEAM':
                rst_staff_details=rst_staff_details.filter(GroupsSA.vchr_name=="B TEAM")
                flagb=True



            # for ins_data in ins_reward_available:
            #     dct_data = {}
            #     dct_data['dat_created_at'] = datetime.strftime(ins_data['dat_reward'],"%d-%m-%Y")
            #     dct_data['enq_number'] = ins_data['fk_item_enquiry__fk_enquiry_master__vchr_enquiry_num']
            #     dct_data['staff_name'] = ins_data['staff_name'].title()
            #     dct_data['branch_name'] = ins_data['fk_staff__fk_branch__vchr_name'].title()
            #     dct_data['reward_amount'] = round(ins_data['reward_earn'],2)
            #     lst_data.append(dct_data)


            lst_zone=Zone.objects.values()
            #structuring
            for ins_staff_query in rst_staff_details.all():
                for ins_data in lst_staff_data:
                    if ins_data['int_staff_id'] == ins_staff_query.staff_id:
                        dct_reward_data={}
                        dct_reward_data['dat_created_at'] = ins_data['dat_created_at']
                        dct_reward_data['enq_number'] = ins_data['enq_number']
                        if flagt:
                            dct_reward_data['branch_name'] = ins_staff_query.t_name
                        elif not flagb and flagz:
                            dct_reward_data['branch_name'] = lst_zone.filter(pk_bint_id=ins_staff_query.zone_id).values('vchr_name').first()['vchr_name']
                        elif not flagb:
                            dct_reward_data['branch_name'] = ins_staff_query.branch_name
                        if flagb:
                            dct_reward_data['branch_name'] = ins_staff_query.staff_name

                        dct_reward_data['reward_amount'] = round(ins_data['int_dbl_amount'],2)
                        # dct_reward_data['staff_id'] = ins_data['int_staff_id']
                        if not flagb:
                            dct_reward_data['staff_name'] = ins_staff_query.staff_name
                        # dct_reward_data['reward_paid'] = 0
                        # dct_reward_data['reward_balance'] = ins_data['int_dbl_amount']
                        # substracting rewards available to rewards paid
                        # for ins_reward_paid in rst_rewards_paid.all():
                        #     if ins_staff_query.staff_id == ins_reward_paid.staff_id:
                        #         dct_reward_data['reward_paid'] = ins_reward_paid.total_reward_paid
                        #         dct_reward_data['reward_balance'] = round(dct_reward_data['reward_balance'] - ins_reward_paid.total_reward_paid,2)
                        lst_data.append(dct_reward_data)




            session.close()
            return Response({'status':'success','data':lst_data})
        except Exception as e:
            session.close()
            return Response({'status':'failed','reason':str(e)})

class RewardPaidList(APIView):
    def post(self,request):
        try:
            dat_from = datetime.strptime(request.data.get('datFrom'), '%d/%m/%Y' )
            dat_to = datetime.strptime(request.data.get('datTo'), '%d/%m/%Y' ) + timedelta(days = 1)
            int_branch_id = request.data.get('intBranchId')
            # import pdb;
            # pdb.set_trace()
            ins_reward_paid = RewardsPaid.objects.filter(dat_paid__date__range=(dat_from,dat_to),int_status=1).values('pk_bint_id','vchr_transaction_id','dbl_paid','dat_paid','fk_staff__fk_branch__vchr_name').annotate(staff_name=Concat('fk_staff__first_name',Value(' '),'fk_staff__last_name'))

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
                ins_reward_paid = ins_reward_paid.filter(fk_staff__fk_branch=request.user.userdetails.fk_branch)
            elif request.user.userdetails.fk_group.vchr_name.upper()=='ASSISTANT BRANCH MANAGER':
                ins_reward_paid = ins_reward_paid.filter(fk_staff__fk_branch=request.user.userdetails.fk_branch).exclude(fk_staff__fk_group__vchr_name='BRANCH MANAGER')
            if int_branch_id:
                ins_reward_paid = ins_reward_paid.filter(fk_staff__fk_branch_id=int_branch_id)
            lst_data = []

            if request.user.userdetails.int_area_id:
                ins_reward_paid = RewardsPaid.objects.filter(dat_paid__date__range=(dat_from,dat_to),int_status=1).values('pk_bint_id','vchr_transaction_id','dbl_paid','dat_paid','fk_staff').annotate(staff_name=Concat('fk_staff__first_name',Value(' '),'fk_staff__last_name'))

                lst_branch = show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                lst_territory_id=Branch.objects.filter(pk_bint_id__in=lst_branch).values_list('fk_territory_id',flat=True)
                ins_reward_paid = ins_reward_paid.filter(Q(fk_staff__fk_branch__in=lst_branch) | Q (fk_staff__int_area_id__in=lst_territory_id))

                if int_branch_id:
                    lst_territory_id=Branch.objects.filter(pk_bint_id=int_branch_id).values_list('fk_territory_id',flat=True)
                    ins_reward_paid = ins_reward_paid.filter(Q(fk_staff__fk_branch=int_branch_id) | Q (fk_staff__int_area_id__in=lst_territory_id))
                    ins_reward_staff = ins_reward_paid.values('pk_bint_id','vchr_transaction_id','dbl_paid','dat_paid','fk_staff__fk_branch__vchr_name').annotate(staff_name=Concat('fk_staff__first_name',Value(' '),'fk_staff__last_name')).exclude(fk_staff__fk_branch__vchr_name__isnull = True)
                    ins_reward_territory=ins_reward_paid.values('pk_bint_id','vchr_transaction_id','dbl_paid','dat_paid','fk_staff__int_area_id').annotate(staff_name=Concat('fk_staff__first_name',Value(' '),'fk_staff__last_name')).exclude(fk_staff__int_area_id__isnull = True)

                    for ins_data in ins_reward_staff:
                        dct_data = {}
                        dct_data['strVoucher'] = ins_data['vchr_transaction_id']
                        dct_data['dblPaid'] = round(ins_data['dbl_paid'],2)
                        dct_data['datPaid'] = datetime.strftime(ins_data['dat_paid'],"%d-%m-%Y")
                        dct_data['strBranchName'] = ins_data.get('fk_staff__fk_branch__vchr_name')
                        dct_data['strStaffName'] = ins_data['staff_name']
                        lst_data.append(dct_data)
                    for ins_data in ins_reward_territory:
                        dct_data = {}
                        dct_data['strVoucher'] = ins_data['vchr_transaction_id']
                        dct_data['dblPaid'] = round(ins_data['dbl_paid'],2)
                        dct_data['datPaid'] = datetime.strftime(ins_data['dat_paid'],"%d-%m-%Y")
                        dct_data['strBranchName'] = "TERRITORY " + str(ins_data.get('fk_staff__int_area_id'))
                        dct_data['strStaffName'] = ins_data['staff_name']
                        lst_data.append(dct_data)
            else:
                for ins_data in ins_reward_paid:
                        dct_data = {}
                        dct_data['strVoucher'] = ins_data['vchr_transaction_id']
                        dct_data['dblPaid'] = round(ins_data['dbl_paid'],2)
                        dct_data['datPaid'] = datetime.strftime(ins_data['dat_paid'],"%d-%m-%Y")
                        dct_data['strBranchName'] = ins_data.get('fk_staff__fk_branch__vchr_name')
                        dct_data['strStaffName'] = ins_data['staff_name']
                        lst_data.append(dct_data)
            return Response({'status':'success','data':lst_data})
        except Exception as e:
            return Response({'status':'failed','reason':str(e)})


class StaffByBranch(APIView):
    """" Staff Typeahead By Branch """
    permission_classes = [IsAuthenticated,]
    def post(self,request):
        try:
            str_search_term = request.data.get('term')
            int_branch_id  = request.data.get('intBranchId')
            if str_search_term:
                lst_user = []
                if int_branch_id:
                    userListData = UserModel.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(username__icontains=str_search_term) | Q(full_name__icontains=str_search_term), fk_company = request.user.userdetails.fk_company,is_active=True,int_area_id=None,fk_branch_id=int_branch_id).exclude(username='TDX-ADMIN').values('id','full_name','username','fk_branch__vchr_name')
                else:
                    userListData = UserModel.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(username__icontains=str_search_term) | Q(full_name__icontains=str_search_term), fk_company = request.user.userdetails.fk_company,is_active=True,int_area_id=None).exclude(username='TDX-ADMIN').values('id','full_name','username','fk_branch__vchr_name')
                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN']:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
                    userListData = userListData.filter(fk_branch=request.user.userdetails.fk_branch)
                elif request.user.userdetails.fk_group.vchr_name.upper()=='ASSISTANT BRANCH MANAGER':
                    userListData = userListData.filter(fk_branch=request.user.userdetails.fk_branch).exclude(fk_group__vchr_name='BRANCH MANAGER')
                elif request.user.userdetails.int_area_id:
                    lst_branch = show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    userListData = userListData.filter(fk_branch_id__in=lst_branch)
                for value in list(userListData):
                    dct_temp = {}
                    dct_temp['name'] = value['full_name'].title()
                    dct_temp['code'] = value['username']
                    dct_temp['branch'] = value['fk_branch__vchr_name'].title()
                    dct_temp['id'] = value['id']
                    lst_user.append(dct_temp)

                return Response({'status':'success','data':lst_user})
            else:
                return Response({'status':'success','data':[]})
        except Exception as e:
            return Response({"status":"failed","message":str(e)})



class RewardPaidListDownload(APIView):
    def post(self,request):
        try:
            session = Session()
            dat_from = datetime.strptime(request.data.get('datFrom'), '%d/%m/%Y' )
            dat_to = datetime.strptime(request.data.get('datTo'), '%d/%m/%Y' ) + timedelta(days = 1)


            lst_branch = []

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN']:
                lst_branch = Branch.objects.filter(fk_company_id = request.user.userdetails.fk_company_id).values_list('pk_bint_id',flat=True)
            elif request.user.userdetails.fk_group.vchr_name.upper()=='BRANCH MANAGER':
                lst_branch.append(request.user.userdetails.fk_branch_id)

            elif request.user.userdetails.fk_group.vchr_name.upper()=='ASSISTANT BRANCH MANAGER':
                lst_branch.append(request.user.userdetails.fk_branch_id)

            elif request.user.userdetails.int_area_id:
                lst_branch = show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

            rst_reward = session.query(func.DATE(RewardsPaidSA.dat_paid).label('dat'),RewardsPaidSA.vchr_transaction_id.label('voucher_code'),RewardsPaidSA.dbl_paid.label('amount'),BranchSA.vchr_name.label('branch'),func.concat(AuthUserSA.first_name,' ',AuthUserSA.last_name).label('staff_name'),func.coalesce(" "," "))\
                                .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                                .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
                                .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
                                .filter(and_(cast(RewardsPaidSA.dat_paid,Date) >= dat_from,cast(RewardsPaidSA.dat_paid,Date) <= dat_to,RewardsPaidSA.int_status==1,BranchSA.pk_bint_id.in_(lst_branch)))

            if request.data.get('intBranchId'):
                rst_reward = rst_reward.filter(BranchSA.pk_bint_id == request.data.get('intBranchId'))

            if not rst_reward.all():
                session.close()
                return Response({'status':'failed','message':'No data'})

            sheet_name1 = 'Sheet1'
            dct_table_data = rst_reward.all()
            all_data = {}
            lst_all = list(zip(*dct_table_data))


            intCount = len(lst_all[4])+5
            intSum = round(sum(lst_all[2]),2)

            all_data['2_Date'] = list(map(lambda x:x.strftime('%d-%m-%y'),lst_all[0]))
            all_data['3_Name'] = lst_all[4]
            all_data['4_Branch'] = lst_all[3]
            all_data['1_Voucher Code'] = lst_all[1]
            all_data['5_Amount'] = [round(x,2) for x in lst_all[2]]
            all_data['6_Signature'] = lst_all[5]
                # all_data['Signature'] = lst_all[lst_tbl_index[int_index]]
            df = pd.DataFrame(all_data ,index = list(range(1,len(all_data['1_Voucher Code'])+1)))

            excel_file = settings.MEDIA_ROOT+'/reward_paid_list.xlsx'
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df.sort_values('1_Voucher Code').to_excel(writer,index=False, sheet_name=sheet_name1,startrow=3, startcol=0)

            workbook = writer.book
            worksheet = writer.sheets[sheet_name1]
            cell_format = workbook.add_format({'bold':True,'align': 'center'})

            for i,width in enumerate(get_col_widths(df)):
                worksheet.set_column(i-1, i-1, width)

            merge_format1 = workbook.add_format({
            'bold': 20,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size':23
            })

            worksheet.write('A4', 'Voucher Code', cell_format)
            worksheet.write('B4', 'Date', cell_format)
            worksheet.write('C4','Name' , cell_format)
            worksheet.write('D4', 'Branch', cell_format)
            worksheet.write('E4', 'Amount', cell_format)
            worksheet.write('F4', 'Signature', cell_format)

            worksheet.write('A'+str(intCount), 'Grand Total', cell_format)
            worksheet.write('E'+str(intCount), intSum, cell_format)

            worksheet.merge_range('A1+:F2', 'Reward Paid List', merge_format1)
            worksheet.protect()
            writer.save()
            # data = settings.HOSTNAME+'/media/reward_paid_list.xlsx'
            data = request.scheme+'://'+request.get_host()+'/media/reward_paid_list.xlsx'
            session.close()
            return Response({'status':'success','data':data})
        except Exception as e:
            session.close()
            return Response({'status':'failed','reason':str(e)})

def get_col_widths(dataframe):
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]
