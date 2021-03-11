from django.shortcuts import render
from staff_rewards.models import RewardsMaster,RewardsDetails,RewardsAvailable,RewardsPaid,RewardAssigned
from rest_framework.views import APIView
from datetime import datetime, timedelta
from rest_framework.response import Response
# from inventory.models import Products,Brands,Items
from brands.models import Brands
from products.models import Products 
# from item_category import Item as Items 
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
from POS import ins_logger

import random as rd


from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.db.models import Q
# from user_app.models import UserModel
from userdetails.models import UserDetails as UserModel


from sqlalchemy import case, literal_column, desc, tuple_, select, table, column
from sqlalchemy.orm.session import sessionmaker
import aldjemy
from sqlalchemy.orm import mapper,aliased
from sqlalchemy import and_,func,cast,Date,MetaData
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy.types import TypeDecorator,BigInteger
from dateutil.relativedelta import relativedelta
from POS.dftosql import Savedftosql
from enquiry.models import EnquiryMaster
from enquiry_mobile.models import ItemEnquiry




sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)

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


# RewardsAvailableJS = metadata.tables['rewards_available']


class AddRewardApi(APIView):
    """
    To add reward for staff,branch manager,asm,tm
    parameter:reward details
    return:success/failed response
    """
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            from_date = datetime.strptime(request.data.get('fromDate'), '%d/%m/%Y' )
            to_date = datetime.strptime(request.data.get('toDate'), '%d/%m/%Y' )
            area_type = request.data.get('areaType')
            area_id = request.data.get('LstArea')
            lst_branch_id = []

            # Find Reward Effective Branches According to area
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
                    return Response({'status':'0','reason':'Area Not Found'})
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
                        if int(request.data.get('map_type')) == 5 or int(request.data.get('map_type')) == 6 or int(request.data.get('map_type')) == 7:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'])
                        elif int(request.data.get('map_type')) == 8 or int(request.data.get('map_type')) == 9 or int(request.data.get('map_type')) == 10 or int(request.data.get('map_type')) == 11:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'],dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))
                        # elif int(request.data.get('map_type')) == 4:
                        #     ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')),dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))

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
                        if int(request.data.get('map_type')) == 5 or int(request.data.get('map_type')) == 6 or int(request.data.get('map_type')) == 7:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'])
                        elif int(request.data.get('map_type')) == 8 or int(request.data.get('map_type')) == 9 or int(request.data.get('map_type')) == 10 or int(request.data.get('map_type')) == 11:
                            ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')), int_map_id=ins_details[0]['map_id'],dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))
                        # elif int(request.data.get('map_type')) == 4:
                        #     ins_prv_details = RewardsDetails.objects.filter(fk_rewards_master = ins_prev_reward[0]['pk_bint_id'],int_map_type=int(request.data.get('map_type')),dbl_value_from = int(ins_details[0]['fromAmt']), dbl_value_to = int(ins_details[0]['toAmt']))
                        if ins_prv_details:
                            return Response({'status':'0','reason':'Reward Already Exist'})

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
            if 'reward4' in request.data and request.data.get('reward4'):
                ins_reward_master.dbl_slab4_percentage = request.data.get('reward4')
            if 'reward5' in request.data and request.data.get('reward5'):
                ins_reward_master.dbl_slab5_percentage = request.data.get('reward5')
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

            ins_reward_details.dbl_value_from =  0.0
            ins_reward_details.dbl_value_to = 0.0
            # if 'fromQty' in ins_details[0] and 'tillQty' in ins_details[0]:
            #     ins_reward_details.int_quantity_from = int(ins_details[0]['fromQty'])
            #     ins_reward_details.int_quantity_to = int(ins_details[0]['tillQty'])
            #

            if 'fromAmt' in ins_details[0] and 'toAmt' in ins_details[0]:
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

                if 'slab4_percentage' in items and items['slab4_percentage']:
                    ins_reward_assigned.dbl_slab4_percentage = float(items['slab4_percentage'])
                if 'slab4_amount' in items and items['slab4_amount']:
                    ins_reward_assigned.dbl_slab4_amount = float(items['slab4_amount'])

                if 'slab5_percentage' in items and items['slab5_percentage']:
                    ins_reward_assigned.dbl_slab5_percentage = float(items['slab5_percentage'])
                if 'slab5_amount' in items and items['slab5_amount']:
                    ins_reward_assigned.dbl_slab5_amount = float(items['slab5_amount'])
                # if 'reward_mop' in items and items['reward_mop']:
                #     ins_reward_details.int_mop_sale = 1
                # else:
                #     ins_reward_details.int_mop_sale = 0
                if items['reward_to'] == 1 or items['reward_to'] == 2 or items['reward_to'] == 3:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'STAFF')
                elif items['reward_to'] == 4:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ASSISTANT BRANCH MANAGER')
                elif items['reward_to'] == 5:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'BRANCH MANAGER')
                elif items['reward_to'] == 6:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'TERRITORY MANAGER')
                elif items['reward_to'] == 7:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ZONE MANAGER')
                elif items['reward_to'] == 8:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'PRODUCT MANAGER')
                elif items['reward_to'] == 9:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'B TEAM')
                elif items['reward_to'] == 10:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'SERVICE ENGINEER')
                elif items['reward_to'] == 11:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'Floor Manager1')
                elif items['reward_to'] == 12:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'Floor Manager2')
                elif items['reward_to'] == 13:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'Floor Manager3')
                elif items['reward_to'] == 14:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ASM2')
                elif items['reward_to'] == 15:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ASM3')
                elif items['reward_to'] == 16:
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'ASM4')
                elif items['reward_to'] == 17:
                    # import pdb; pdb.set_trace()
                    ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'Customer Experience Executive')
                # elif items['reward_to'] == 10:
                #     ins_reward_assigned.fk_group = Groups.objects.get(vchr_name = 'SERVICE ENGINEER')

                ins_reward_assigned.int_to = items['reward_to']
                ins_reward_assigned.save()
            return Response({'status':'1','data':{}})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'0'})



class RewardsList(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request):
        try:
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')

            lst_id = []
            ins_reward_master = RewardsDetails.objects.filter(Q(fk_rewards_master__dat_from__range=(dat_from,dat_to))|Q(fk_rewards_master__dat_to__range=(dat_from,dat_to))|Q(fk_rewards_master__dat_from__lte=dat_from,fk_rewards_master__dat_to__gte=dat_from)|Q(fk_rewards_master__dat_from__lte=dat_to,fk_rewards_master__dat_to__gte=dat_to),int_map_type__gt=4).values('fk_rewards_master__pk_bint_id','fk_rewards_master__vchr_area_type','fk_rewards_master__vchr_reward_name','fk_rewards_master__dat_from','fk_rewards_master__dat_to','fk_rewards_master__json_branch','int_map_type').order_by('-pk_bint_id')
            # ins_reward_master = RewardsDetails.objects.filter(Q(fk_rewards_master__dat_from__range=(dat_from,dat_to))|Q(fk_rewards_master__dat_to__range=(dat_from,dat_to))).values('fk_rewards_master__pk_bint_id','fk_rewards_master__vchr_area_type','fk_rewards_master__vchr_reward_name','fk_rewards_master__dat_from','fk_rewards_master__dat_to','fk_rewards_master__json_branch','int_map_type').order_by('-pk_bint_id')
            lst_data = []
            ins_branch={data['pk_bint_id']:[data['vchr_name'],data] for data in Branch.objects.values('pk_bint_id','vchr_name','fk_territory__vchr_name','fk_territory__fk_zone__vchr_name')}
            for ins_data in ins_reward_master:
                dct_data = {}
                dct_data['id'] = ins_data['fk_rewards_master__pk_bint_id']
                dct_data['reward_name'] = ins_data['fk_rewards_master__vchr_reward_name'].title()
                dct_data['date_range'] = datetime.strftime(ins_data['fk_rewards_master__dat_from'],"%d-%m-%Y")+' - '+datetime.strftime(ins_data['fk_rewards_master__dat_to'],"%d-%m-%Y")
                if ins_data['int_map_type'] == 5:
                    dct_data['category'] = 'Product Value Wise'
                elif ins_data['int_map_type'] == 6:
                    dct_data['category'] = 'Brand Value Wise'
                elif ins_data['int_map_type'] == 7:
                    dct_data['category'] = 'Item Value Wise'
                elif ins_data['int_map_type'] == 8:
                    dct_data['category'] = 'Product Price Band'
                elif ins_data['int_map_type'] == 9:
                    dct_data['category'] = 'Brand Price Band'
                elif ins_data['int_map_type'] == 10:
                    dct_data['category'] = 'Product Price Band Growth'
                elif ins_data['int_map_type'] == 11:
                    dct_data['category'] = 'Brand Price Band Growth'
                elif ins_data['int_map_type'] == 13:
                    dct_data['category'] = 'TurnOver Wise'
                # elif ins_data['int_map_type'] == 4:
                #     dct_data['category'] = 'TurnOver Wise'
                dct_data['branch'] = []
                for branch in ins_data['fk_rewards_master__json_branch']['branch_id']:
                    if ins_data['fk_rewards_master__vchr_area_type'] == 'TERRITORY' and ins_branch[int(branch)][1]['fk_territory__vchr_name'].title() not in dct_data['branch']:
                        dct_data['branch'].append(ins_branch[int(branch)][1]['fk_territory__vchr_name'].title())
                    elif ins_data['fk_rewards_master__vchr_area_type'] == 'ZONE' and ins_branch[int(branch)][1]['fk_territory__fk_zone__vchr_name'].title() not in dct_data['branch']:
                        dct_data['branch'].append(ins_branch[int(branch)][1]['fk_territory__fk_zone__vchr_name'].title())
                    elif ins_data['fk_rewards_master__vchr_area_type'] == 'BRANCH':
                        dct_data['branch'].append(ins_branch[int(branch)][0].title())
                    # elif ins_data['int_map_type'] == 4:
                    #     dct_data['branch'].append(ins_branch[int(branch)][0].title())
                if len(dct_data['branch'])>1:
                    dct_data['branch'] = dct_data['branch'][0]+', ..'
                else:
                    if len(dct_data['branch']) != 0:
                        dct_data['branch'] = dct_data['branch'][0]
                if ins_data['fk_rewards_master__pk_bint_id'] not in lst_id:
                    lst_data.append(dct_data)
                    lst_id.append(ins_data['fk_rewards_master__pk_bint_id'])
            return Response({'status':'1','data':lst_data})
        except Exception as e:
            return Response({'status':'0','reason':str(e)})

    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            id = request.data.get('id')
            ins_reward_master = RewardsMaster.objects.filter(pk_bint_id=id).values('pk_bint_id','dat_from','dat_to','vchr_area_type','json_branch','vchr_reward_name','dbl_slab1_percentage','dbl_slab2_percentage','dbl_slab3_percentage','dbl_slab4_percentage','dbl_slab5_percentage')[0]

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
                # elif ins_reward_details[0]['int_map_type']==4:
                #     dct_data['branch'].append(branch['vchr_name'].title())
                #     dct_data['branch_id'].append(branch['pk_bint_id'])

            # if ins_reward_details[0]['int_map_type'] == 5:
            #     dct_data['category'] = 'Product Wise'
            # elif ins_reward_details[0]['int_map_type'] == 6:
            #     dct_data['category'] = 'Brand Wise'
            # elif ins_reward_details[0]['int_map_type'] == 7:
            #     dct_data['category'] = 'Item Wise'
            # elif ins_reward_details[0]['int_map_type'] == 8:
            #     dct_data['category'] = 'Price Band'
            if ins_reward_details[0]['int_map_type'] == 5:
                dct_data['category'] = 'Product Value Wise'
            elif ins_reward_details[0]['int_map_type'] == 6:
                dct_data['category'] = 'Brand Value Wise'
            elif ins_reward_details[0]['int_map_type'] == 7:
                dct_data['category'] = 'Item Value Wise'
            elif ins_reward_details[0]['int_map_type'] == 8:
                dct_data['category'] = 'Product Price Band'
            elif ins_reward_details[0]['int_map_type'] == 9:
                dct_data['category'] = 'Brand Price Band'
            elif ins_reward_details[0]['int_map_type'] == 10:
                dct_data['category'] = 'Product Price Band Growth'
            elif ins_reward_details[0]['int_map_type'] == 11:
                dct_data['category'] = 'Brand Price Band Growth'
            # elif ins_reward_details[0]['int_map_type'] == 4:
            #     dct_data['category'] = 'TurnOver Wise'

            dct_data['reward_name'] = ins_reward_master['vchr_reward_name'].title()
            dct_data['slab1_percentage'] = ins_reward_master['dbl_slab1_percentage']
            dct_data['slab2_percentage'] = ins_reward_master['dbl_slab2_percentage']
            dct_data['slab3_percentage'] = ins_reward_master['dbl_slab3_percentage']
            dct_data['slab4_percentage'] = ins_reward_master['dbl_slab4_percentage']
            dct_data['slab5_percentage'] = ins_reward_master['dbl_slab5_percentage']
            dct_data['map_type'] = ins_reward_details[0]['int_map_type']
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
                dct_item['slab4_percentage'] = items['dbl_slab4_percentage']
                dct_item['slab4_amount'] = items['dbl_slab4_amount']
                dct_item['slab5_percentage'] = items['dbl_slab5_percentage']
                dct_item['slab5_amount'] = items['dbl_slab5_amount']
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
                elif items['int_to'] == 8:
                    dct_item['assign_to'] = 'Product Manager'
                elif items['int_to'] == 9:
                    dct_item['assign_to'] = 'B team'
                elif items['int_to'] == 10:
                    dct_item['assign_to'] = 'Service Engineer'
                elif items['int_to'] == 11:
                    dct_item['assign_to'] = 'Floor Manager1'
                elif items['int_to'] == 12:
                    dct_item['assign_to'] = 'Floor Manager2'
                elif items['int_to'] == 13:
                    dct_item['assign_to'] = 'Floor Manager3'
                elif items['int_to'] == 14:
                    dct_item['assign_to'] = 'ASM2'
                elif items['int_to'] == 15:
                    dct_item['assign_to'] = 'ASM3'
                elif items['int_to'] == 16:
                    dct_item['assign_to'] = 'ASM4'
                elif items['int_to'] == 17:
                    dct_item['assign_to'] = 'Customer Experience Executive'

                if ins_reward_details[0]['int_map_type'] == 5:
                    product = Products.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_product_name')[0]
                    dct_item['product_name'] = product['vchr_product_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 6:
                    product = Brands.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_brand_name')[0]
                    dct_item['brand_name'] = product['vchr_brand_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 7:
                    product = Items.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_item_name','fk_product__vchr_product_name','fk_product__id')[0]
                    dct_item['product_name'] = product['fk_product__vchr_product_name'].title()
                    dct_item['item_name'] = product['vchr_item_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 8:
                    product = Products.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_product_name')[0]
                    dct_item['product_name'] = product['vchr_product_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 9:
                    product = Brands.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_brand_name')[0]
                    dct_item['brand_name'] = product['vchr_brand_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 10:
                    product = Products.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_product_name')[0]
                    dct_item['product_name'] = product['vchr_product_name'].title()
                    dct_item['map_id'] = product['id']
                elif ins_reward_details[0]['int_map_type'] == 11:
                    product = Brands.objects.filter(id=int(ins_reward_details[0]['int_map_id'])).values('id','vchr_brand_name')[0]
                    dct_item['brand_name'] = product['vchr_brand_name'].title()
                    dct_item['map_id'] = product['id']
                dct_data['items'].append(dct_item)

            return Response({'status':'1','data':dct_data})
        except Exception as e:
            return Response({'status':'0','reason':str(e)})



class GetRewardDetails(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            session = Connection()
            branch_id = request.data.get('branch_id')
            #listig all staff id's and it reward amount
            rst_staff_list = session.query(RewardsAvailableJS.c.json_staff.label('staff_id'))

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
            if request.user.usermodel.int_area_id:
                lst_branch_id=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)

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
                                .group_by('staff_id','branch_name')




            else:
                    lst_branch_id.append(request.user.usermodel.fk_branch_id)
            #taking details of staff
                    rst_staff_details =session.query(UserModelSA.user_ptr_id.label('staff_id'),\
                                            func.concat(AuthUserSA.first_name," ",AuthUserSA.last_name).label('staff_name'),\
                                            GroupsSA.vchr_name.label('designation'),\
                                            BranchSA.vchr_name.label('branch_name'))\
                                            .join(AuthUserSA,AuthUserSA.id == UserModelSA.user_ptr_id)\
                                            .join(GroupsSA,GroupsSA.pk_bint_id == UserModelSA.fk_group_id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == UserModelSA.fk_branch_id)\
                                            .filter(and_(BranchSA.pk_bint_id==request.user.usermodel.fk_branch_id,BranchSA.pk_bint_id==branch_id))\
                                            .filter(UserModelSA.user_ptr_id.in_(lst_staff_id))
                    rst_rewards_paid =session.query(RewardsPaidSA.fk_staff_id.label('staff_id'),\
                                    func.sum(func.coalesce(RewardsPaidSA.dbl_paid,0)).label('total_reward_paid'),\
                                    BranchSA.vchr_name.label('branch_name'))\
                                    .join(UserModelSA,UserModelSA.user_ptr_id == RewardsPaidSA.fk_staff_id)\
                                    .join(BranchSA,(BranchSA.pk_bint_id == UserModelSA.fk_branch_id) | (BranchSA.fk_territory_id== UserModelSA.int_area_id))\
                                    .filter(and_(BranchSA.pk_bint_id==request.user.usermodel.fk_branch_id,BranchSA.pk_bint_id==branch_id))\
                                    .group_by('staff_id','branch_name')

            rst_staff_list.filter()
            rst_rewards_paid.filter(BranchSA.pk_bint_id==branch_id)

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
            session.close()
            return Response({'status':'1','data':lst_rewards_all})
        except Exception as e:
            session.close()
            return Response({'status':'0','reason':str(e)})
