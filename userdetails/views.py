from uuid import uuid3, NAMESPACE_DNS
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from userdetails.models import Userdetails,GuestUserDetails, UserPermissions
from django.contrib.auth import authenticate, login
from company.models import Company
from brands.models import Brands
from groups.models import Groups
from branch.models import Branch
from products.models import Products
from item_group.models import ItemGroup
from company_permissions.models import GroupPermissions
from django.contrib.auth.models import User
from random import randint
from django.db import transaction

from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Value, BooleanField, Case, When
from django.db.models.functions import Concat
from django.conf import settings
from tool_settings.models import Tools
from POS import ins_logger
import sys, os
import requests
import json
import pandas as pd

# Create your views here.
class UpdateUserPassword(APIView):
    '''Change user password'''
    permission_classes=[AllowAny]


    def post(self,request):
        try:
            user_ptr_id=int(request.data.get("id"))
            password=request.data.get("password")
            userobject=Userdetails.objects.get(id = user_ptr_id )
            userobject.fk_updated_id=request.user.id
            userobject.dat_updated=datetime.now()

            userobject.set_password(password)
            userobject.save()

            return Response({'status':1})

        except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                    return Response({'status':0,'reason':e})


class ViewUser(APIView):
    '''View User'''
    permission_classes=[AllowAny]


    def get(self,request):
        '''list all users'''

        try:
            # import pdb; pdb.set_trace()
            if request.GET.get("id"):
                pk_bint_id=int(request.GET.get("id"))
                if(Userdetails.objects.filter(user_ptr_id=pk_bint_id,is_active=1)):
                    lst_userdetails= list(Userdetails.objects.filter(user_ptr_id=pk_bint_id).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','fk_branch_id','fk_branch__vchr_name','fk_brand_id','fk_group_id','fk_company_id','bint_usercode','fk_company__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined')) #passes as a list object
                    ins_user_permission = UserPermissions.objects.filter(fk_user_id=pk_bint_id, bln_active=True).values('jsn_branch', 'jsn_product', 'jsn_item_group','json_price_perm','jsn_branch_type').first()
                    # lst_userdetails[0]['lstItemGroupId'] = []
                    # lst_userdetails[0]['lstProductId'] =[]
                    # lst_userdetails[0]['lstBranchId'] = []

                    # if ins_user_permission["jsn_branch"]:
                    lst_userdetails[0]['lstBranchId'] = list(Branch.objects.filter(pk_bint_id__in=ins_user_permission['jsn_branch']).values('pk_bint_id', 'vchr_name')) if ins_user_permission and ins_user_permission['jsn_branch'] else []
                    # if ins_user_permission["jsn_product"]:
                    lst_userdetails[0]['lstProductId'] = list(Products.objects.filter(pk_bint_id__in=ins_user_permission['jsn_product']).values('pk_bint_id', 'vchr_name')) if ins_user_permission and ins_user_permission['jsn_product'] else []
                    # if ins_user_permission['jsn_item_group']:
                    lst_userdetails[0]['lstItemGroupId'] = list(ItemGroup.objects.filter(pk_bint_id__in=ins_user_permission['jsn_item_group']).values('pk_bint_id', 'vchr_item_group')) if ins_user_permission and ins_user_permission['jsn_item_group'] else []
                    lst_userdetails[0]['jsn_branch_type'] = ins_user_permission["jsn_branch_type"] if ins_user_permission and ins_user_permission["jsn_branch_type"] else []
                    lst_userdetails[0]['dct_price_perm'] = {}
                    lst_price_perm = []
                    if ins_user_permission:

                        dct_permission = json.loads(ins_user_permission.get('json_price_perm')) if ins_user_permission.get('json_price_perm') else {}
                        lst_userdetails[0]['dct_price_perm']= ins_user_permission.get('json_price_perm') if ins_user_permission.get('json_price_perm') else {}

                        if dct_permission:
                            lst_price_perm = [x[0].replace('bln_','').replace('_',' ').replace('dp','DEALER PRICE').upper() for x in dct_permission.items() if x[1] == True]



                    return Response({'status':1,'lst_userdetailsview':lst_userdetails,'lst_price_per':lst_price_perm})
                else:
                    return Response({'status':0,'reason':"User deleted or doesn't exist"})
            else:
                if request.user.userdetails.fk_branch.int_type in [2,3]  or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                    lst_userdetails= list(Userdetails.objects.filter(is_active=True).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))

                else:

            # lst_userdetails= list(Userdetails.objects.filter(is_active=True).values('pk_bint_id','bint_phone','fk_group','fk_company','fk_branch', 'fk_brand','bint_usercode','vchr_profpic','dat_resapp','int_areaid','dat_creaed','dat_updated','fk_created','fk_updated')) #passes as a list object
                    lst_userdetails= list(Userdetails.objects.filter(is_active=True,fk_branch_id = request.user.userdetails.fk_branch_id).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))
                for dict in lst_userdetails:
                    dict['fullname']=dict['first_name']+' '+dict['last_name']
                return Response({'status':1,'lst_userdetails':lst_userdetails})
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})
    def post(self,request):
        '''Export all users'''

        try:
            if request.user.userdetails.fk_branch.int_type in [2,3]  or request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                lst_userdetails= list(Userdetails.objects.filter(is_active=True).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))

            else:

                lst_userdetails= list(Userdetails.objects.filter(is_active=True,fk_branch_id = request.user.userdetails.fk_branch_id).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))
            dct_data = {'Slno':[],'Code':[],'Name':[],'Phone':[],
                    'Group':[]}
            count = 0
            for dict in lst_userdetails:
                count += 1
                dict['fullname']=dict['first_name']+' '+dict['last_name']
                dct_data['Slno'].append(count)
                dct_data['Code'].append(dict['username'])
                dct_data['Name'].append(dict['fullname'].title())
                dct_data['Phone'].append(dict['bint_phone'])
                dct_data['Group'].append(dict['fk_group__vchr_name'])
            df = pd.DataFrame(dct_data)
            str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S_%f')+'_userlist.xlsx'
            filename =settings.MEDIA_ROOT+'/'+str_file

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            workbook = writer.book
            cell_format = workbook.add_format()
            cell_format.set_align('center')
            cell_format1 = workbook.add_format()
            cell_format1.set_align('left')
            df.to_excel(writer,index=False, sheet_name='User List',columns=['Slno','Code','Name','Phone','Group'],startrow=6, startcol=0)
            worksheet = writer.sheets['User List']
            merge_format1 = workbook.add_format({
                'bold': 20,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size':23
                })

            merge_format2 = workbook.add_format({
            'bold': 6,
            'border': 1,
            'align': 'left',
            'valign': 'vleft',
            'font_size':13
            })
            worksheet.merge_range('A1+:E2', 'User List', merge_format1)
            worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
            worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)
            worksheet.set_column('B:B', 15,cell_format)
            worksheet.set_column('C:C', 20,cell_format1)
            worksheet.set_column('D:D', 15,cell_format)
            worksheet.set_column('E:E', 30,cell_format1)
            writer.save()
            return Response({'status':'1','file':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+str_file})
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})

class AddUsers(APIView):
    permission_classes=[AllowAny]


    def post(self,request):
        '''add users'''
        try:
            # import pdb; pdb.set_trace()
            with transaction.atomic():
                # import pdb; pdb.set_trace()
                first_name  = str(request.data.get('firstname'))
                bint_phone = int(request.data.get('contactno'))
                # str_pssrsttkn= str(request.data.get('vchr_pssrsttkn'))
                # bint_pssrstflg= int(request.data.get('bint_pssrstflg'))
                # dat_passrsttim= request.data.get('dat_passrsttim')
                # fk_group= request.data.get('fk_group')

                # fk_company = int(request.data.get('companyid'))
                fk_branch= int(request.data.get('branch_id'))
                fk_group= int(request.data.get('group_id'))
                bln_loop=True
                while bln_loop:
                        bint_usercode=randint(10000,99999)
                        if not (Userdetails.objects.filter(bint_usercode=bint_usercode)):
                            bln_loop=False



                # bint_usercode= int(request.data.get('vchr_user_code'))
                vchr_prof = request.FILES.get('image')

                if vchr_prof:
                        my_file = request.FILES.get('image')
                        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                        filename = fs.save(my_file.name, my_file)
                        str_profpic = fs.url(filename)


                # dat_resapp= request.data.get('dat_resapp')
                # int_areaid= request.data.get('int_areaid')
                # dat_created= request.data.get('dat_created')
                # dat_updated= request.data.get('dat_updated')
                # fk_created= request.data.get('fk_created')
                # fk_updated= request.data.get('fk_updated')
                # json_product = request.data.get('json_product')
                # id1=request.data.get('id')
                # last_login=request.data.get('last_login')
                # is_superuser=request.data.get('is_superuser')
                username = str(request.data.get('vchr_user_code'))
                # first_name=request.data.get('firstname')
                last_name=str(request.data.get('lastname'))
                email=str(request.data.get('email'))
                # is_staff=request.data.get('is_staff')

                # date_joined=request.data.get('date_joined')
                # if Userdetails.objects.filter(username=username,bint_usercode=bint_usercode,is_active=True):
                #     return Response({'status':0,'reason':'already exists'})
                # else:
                    # Userdetails.objects.create(bint_phone=bint_phone,vchr_pssrsttkn=str_pssrsttkn,bint_pssrstflg=bint_pssrstflg,dat_passrsttim=dat_passrsttim,fk_group=fk_group,fk_company=fk_company,fk_branch=fk_branch,fk_brand=fk_brand,bint_usercode=bint_usercode,vchr_profpic=str_profpic,dat_resapp=dat_resapp,int_areaid=int_areaid,dat_created=dat_created,dat_updated=dat_updated,fk_created=fk_created,fk_updated=fk_updated,json_product=json_product,id=id1,password=password,last_login=last_login,is_superuser=is_superuser,username=username,first_name=first_name,last_name=last_name,email=email,is_staff=is_staff,date_joined=date_joined,is_active=True)
                    #
                if Userdetails.objects.filter(username=username):
                    return Response({'status':0,'message':'Usercode already exists'})
                else:
                    if request.data.get('brand'):
                        fk_brand= int(request.data.get('brand'))
                        userobject=Userdetails(bint_phone=bint_phone,bint_usercode=bint_usercode,fk_brand_id=fk_brand,fk_branch_id=fk_branch,fk_group_id=fk_group,vchr_profpic=str_profpic,username=username,first_name=first_name,last_name=last_name,email=email,is_active=True,is_superuser=False,date_joined=datetime.now(),fk_created_id=request.user.id,dat_created=datetime.now(),fk_company_id=request.user.userdetails.fk_company_id)
                    else:
                        userobject=Userdetails(bint_phone=bint_phone,bint_usercode=bint_usercode,fk_group_id=fk_group,fk_branch_id=fk_branch,vchr_profpic=str_profpic,username=username,first_name=first_name,last_name=last_name,email=email,is_active=True,is_superuser=False,date_joined=datetime.now(),fk_created_id=request.user.id,dat_created=datetime.now(),fk_company_id=request.user.userdetails.fk_company_id)
                userobject.set_password(request.data.get('password'))
                userobject.save()
                lst_branch = [int(int_id) for int_id in request.data.get('lstBranchId').split(',')] if request.data.get('lstBranchId') else []
                lst_product = [int(int_id) for int_id in request.data.get('lstProductId').split(',')] if request.data.get('lstProductId') else []
                lst_item_groups = [int(int_id) for int_id in request.data.get('lstItemGroupId').split(',')] if request.data.get('lstItemGroupId') else []
                lst_branch_type = [int(int_id) for int_id in request.data.get('lstBranchType').split(',')] if request.data.get('lstBranchType') else []
                dct_price_perm = request.data.get('dctPriceList') if   request.data.get('dctPriceList') else None
                if lst_branch or lst_product or lst_item_groups or dct_price_perm or lst_branch_type:
                    ins_user_permission = UserPermissions(fk_user = userobject, jsn_branch_type = lst_branch_type, jsn_branch = lst_branch, jsn_product = lst_product, jsn_item_group = lst_item_groups,json_price_perm = request.data.get('dctPriceList') )
                    ins_user_permission.save()

                # ins_user_permission = UserPermissions.objects.filter(fk_user=userobject, bln_active=True)
                # if ins_user_permission:
                #     ins_user_permission.update(jsn_branch_type = lst_branch_type)
                # elif request.data.get('blnSalesCounter'):
                #     UserPermissions.objects.create(fk_user=userobject,jsn_branch_type = lst_branch_type, jsn_branch = [], jsn_product = [], jsn_item_group = [])

                return Response({'status':1,'message':'created successfully'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class ChangeUserStatus(APIView):
        permission_classes=[AllowAny]

        '''delete user'''
        def post(self,request):
            try:
                user_id = request.data.get('id')
                User.objects.filter(id=user_id).update(is_active=False)
                Userdetails.objects.filter(user_ptr_id=user_id).update(fk_updated_id=request.user.id,dat_updated=datetime.now())
                return Response({'status':1,'message':'successfully updated'})
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})

class UpdateUser(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        '''update user'''
        try:
            # import pdb; pdb.set_trace()
            with transaction.atomic():

                # str_pssrsttkn= request.data.get('vchr_pssrsttkn')
                # bint_pssrstflg= request.data.get('bint_pssrstflg')
                # dat_passrsttim= request.data.get('dat_passrsttim')
                fk_group= request.data.get('group_id')
                # bint_usercode= request.data.get('bint_usercode')
                # str_profpic= request.data.get('vchr_profpic')
                # dat_resapp= request.data.get('dat_resapp')
                # pk_bint_id=request.data.get('pk_bint_id')
                first_name=str(request.data.get('firstname'))
                bint_phone = int(request.data.get('contactno'))

                username=str(request.data.get('vchr_user_code'))
                last_name=str(request.data.get('lastname'))
                email=str(request.data.get('email'))
                user_ptr_id=int(request.data.get('id'))
                fk_branch=request.data.get('branch_id')
                if Userdetails.objects.filter(username=username,is_active=True).exclude(user_ptr_id=user_ptr_id):
                    return Response({'status':0,'reason':'already exists'})
                else:
                    if request.FILES.get('image'):
                        vchr_prof =request.FILES.get('image')
                        my_file = request.FILES.get('image')
                        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                        filename = fs.save(my_file.name, my_file)
                        str_profpic = fs.url(filename)

                        if request.data.get('brand'):
                            fk_brand= int(request.data.get('brand'))
                            Userdetails.objects.filter(user_ptr_id=user_ptr_id).update(bint_phone=bint_phone,fk_brand_id=fk_brand,fk_group_id=fk_group,fk_branch_id=fk_branch,vchr_profpic=str_profpic,username=username,first_name=first_name,last_name=last_name,email=email)
                        else:
                            Userdetails.objects.filter(user_ptr_id=user_ptr_id).update(bint_phone=bint_phone,fk_brand_id=None,fk_group_id=fk_group,fk_branch_id=fk_branch,vchr_profpic=str_profpic,username=username,first_name=first_name,last_name=last_name,email=email)

                    elif request.data.get('brand'):
                        fk_brand= int(request.data.get('brand'))
                        Userdetails.objects.filter(user_ptr_id=user_ptr_id).update(bint_phone=bint_phone,fk_brand_id=fk_brand,fk_group_id=fk_group,fk_branch_id=fk_branch,username=username,first_name=first_name,last_name=last_name,email=email,fk_updated_id=request.user.id,dat_updated=datetime.now())
                    else:
                        Userdetails.objects.filter(user_ptr_id=user_ptr_id).update(bint_phone=bint_phone,fk_brand_id=None,fk_group_id=fk_group,fk_branch_id=fk_branch,username=username,first_name=first_name,last_name=last_name,email=email)

                    lst_branch = [int(int_id) for int_id in request.data.get('lstBranchId').split(',')] if request.data.get('lstBranchId') else []
                    lst_product = [int(int_id) for int_id in request.data.get('lstProductId').split(',')] if request.data.get('lstProductId') else []
                    lst_item_groups = [int(int_id) for int_id in request.data.get('lstItemGroupId').split(',')] if request.data.get('lstItemGroupId') else []
                    lst_branch_type = [int(int_id) for int_id in request.data.get('lstBranchType').split(',')] if request.data.get('lstBranchType') else []
                    dct_price_perm = request.data.get('dctPriceList') if   request.data.get('dctPriceList') else None

                    if lst_branch or lst_product or lst_item_groups or dct_price_perm or lst_branch_type:

                        ins_user_permission = UserPermissions.objects.filter(fk_user_id=user_ptr_id, bln_active=True)
                        if ins_user_permission:
                            ins_user_permission.update(jsn_branch_type = lst_branch_type, jsn_branch = lst_branch, jsn_product = lst_product, jsn_item_group = lst_item_groups,json_price_perm = dct_price_perm)
                        else:
                            UserPermissions.objects.create(jsn_branch_type = lst_branch_type, fk_user_id = user_ptr_id,jsn_branch = lst_branch, jsn_product = lst_product, jsn_item_group = lst_item_groups,json_price_perm = dct_price_perm)

                    elif not lst_branch and not lst_product and not lst_item_groups and not dct_price_perm and not lst_branch_type:
                        UserPermissions.objects.filter(fk_user_id=user_ptr_id).update(bln_active=False)

                    return Response({'status':1,'message':'successfully updated'})
                # dat_resapp= request.data.get('dat_resapp')
                # int_areaid= request.data.get('int_areaid')
                # json_product = request.data.get('json_product')


        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})


class loginCheck(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try :
            str_username= request.data['_UserId']
            str_password=request.data['_Password']
            # if(Userdetails.objects.filter(username=str_username)):
            #import pdb; pdb.set_trace()
            user = authenticate(request, username=str_username, password=str_password)


            if user.is_staff:
                login(request, user)
                if settings.DEBUG:
                    token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                else:
                    token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                token = json.loads(token_json._content.decode("utf-8"))['token']
                str_name='Super User'
                email=user.email or ''
                userdetails={'Name':str_name,'email':email}
            else:
                login(request,user)
                if settings.DEBUG:
                    token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                else:
                    token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                token = json.loads(token_json._content.decode("utf-8"))['token']
                str_name=(user.first_name +' '+ user.last_name).title()
                email=user.email or ''
                # import pdb; pdb.set_trace()
                rst_user = Userdetails.objects.filter(user_ptr_id=request.user.id).values('fk_branch_id','fk_branch_id__vchr_name','fk_company_id','fk_group__vchr_name','fk_branch__vchr_code')
                branch_id = rst_user[0]['fk_branch_id']
                bln_indirect_discount = False
                bln_direct_discount = False
                if branch_id:
                    ins_indirect = Tools.objects.filter(jsn_data__contains=branch_id,vchr_tool_code = 'INDIRECT_DISCOUNT')
                    ins_direct = Tools.objects.filter(jsn_data__contains=branch_id,vchr_tool_code = 'DIRECT_DISCOUNT')
                    bln_indirect_discount = True if ins_indirect else False
                    bln_direct_discount = True if ins_direct else False

                branch_name = rst_user[0]['fk_branch_id__vchr_name']
                branch_code=rst_user[0]['fk_branch__vchr_code']
                group_name=rst_user[0]['fk_group__vchr_name'].upper()
                company_id=rst_user[0]['fk_company_id']
                branch_type =  user.userdetails.fk_branch.int_type if user.userdetails.fk_branch else ''
                userdetails={'Name':str_name,'email':email,'branch_id':branch_id,'branch_type':branch_type,'branch_code':branch_code,'branch_name':branch_name,'company_id':company_id,'group_name':group_name,'bln_indirect_discount':bln_indirect_discount,'bln_direct_discount':bln_direct_discount}
            ins_guest=Userdetails.objects.filter(id=user.id).values('int_guest_user').first()
            if ins_guest and ins_guest['int_guest_user']==1:
                ins_guest=GuestUserDetails.objects.filter(fk_user_id=user.id).values('session_expiry_time').first()
                if datetime.now()>=ins_guest['session_expiry_time']:
                    pass
                else:
                    ins_guest.update(int_guest_user=-1)

                    return Response({'status':0})


            lst_groups = []
            dct_insert = {'NAME':'',
                'ADD': False,
                'VIEW': False,
                'EDIT': False,
                'DELETE': False,
                'DOWNLOAD': False
                }

            """Uncomment below code for getting location details(IP address)

            obj_ip_location=geocoder.ip(str(request.META.get('REMOTE_ADDR')))
            dict_location={}
            dict_location['latlng']=obj_ip_location.latlng
            dict_location['city']=obj_ip_location.city
            dict_location=json.dumps(dict_location)
            ins_user=UserLogDetails.objects.filter(fk_user_id=user.id,dat_start_active__contains=datetime.today().date(),dat_last_active__contains=datetime.today().date(),json_ip__isnull=False).values('json_ip','pk_bint_id')
            if ins_user:
                if ins_user.last()['json_ip']['city'] != dict_location['city']:

                    UserLogDetails.objects.create(fk_user_id=user.id,dat_start_active=datetime.today(),dat_last_active=datetime.today(),json_ip=dict_location)
            else:
                UserLogDetails.objects.create(fk_user_id=user.id,dat_start_active=datetime.today(),dat_last_active=datetime.today(),json_ip=dict_location)

            """



            if not request.user.is_staff:
                ins_group_perm = GroupPermissions.objects.filter(fk_groups_id=user.userdetails.fk_group_id).values('fk_category_items__fk_sub_category__vchr_sub_category_name','pk_bint_id', 'fk_category_items__fk_menu_category__vchr_menu_category_name','fk_category_items__fk_main_category__vchr_main_category_name','bln_view','bln_add','bln_delete','bln_edit','bln_download')
                for dct_data in ins_group_perm :
                    dct_insert = {}
                    dct_insert['NAME'] = dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name']
                    dct_insert['ADD'] = dct_data['bln_add']
                    dct_insert['EDIT'] = dct_data['bln_edit']
                    dct_insert['VIEW'] = dct_data['bln_view']
                    dct_insert['DELETE'] = dct_data['bln_delete']
                    dct_insert['DOWNLOAD'] = dct_data['bln_download']
                    dct_insert['PARENT'] = dct_data['fk_category_items__fk_sub_category__vchr_sub_category_name']
                    dct_insert['MENU'] = dct_data['fk_category_items__fk_main_category__vchr_main_category_name']
                    lst_groups.append(dct_insert)
            else:
                # ins_group_perm = MenuCategory.objects.filter().values('fk_sub_category__vchr_sub_category_name','pk_bint_id', 'fk_category_items__fk_menu_category__vchr_menu_category_name','fk_category_items__fk_main_category__vchr_main_category_name','bln_view','bln_add','bln_delete','bln_edit','bln_download')
                # for dct_data in ins_group_perm :
                #     dct_insert = {}
                #     dct_insert['NAME'] = dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name']
                #     dct_insert['ADD'] = dct_data['bln_add']
                #     dct_insert['EDIT'] = dct_data['bln_edit']
                #     dct_insert['VIEW'] = dct_data['bln_view']
                #     dct_insert['DELETE'] = dct_data['bln_delete']
                #     dct_insert['DOWNLOAD'] = dct_data['bln_download']
                #     dct_insert['PARENT'] = dct_data['fk_category_items__fk_sub_category__vchr_sub_category_name']
                #     dct_insert['MENU'] = dct_data['fk_category_items__fk_main_category__vchr_main_category_name']
                #     lst_groups.append(dct_insert)
                return Response({'status':1,'token':token,'userdetails':userdetails})


            return Response({'status':1,'token':token,'userdetails':userdetails,'permission':lst_groups})
            # else:
            #     return Response({'status':1,'reason':"User doesn't exist"})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})
class CompanyTypeahead(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:


                lst_company = []

                ins_company = Company.objects.values('pk_bint_id','vchr_name')
                if ins_company:
                    for itr_item in ins_company:
                        dct_company = {}

                        dct_company['companyname'] = itr_item['vchr_name'].capitalize()
                        dct_company['id'] = itr_item['pk_bint_id']
                        lst_company.append(dct_company)
                return Response({'status':1,'data':lst_company})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})

class BrandTypeahead(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:


                lst_brands = []

                ins_brands = Brands.objects.filter(int_status=0).values('pk_bint_id','vchr_name','vchr_code')
                if ins_brands:
                    for itr_item in ins_brands:
                        dct_brands = {}

                        dct_brands['brandname'] = itr_item['vchr_name'].capitalize()
                        dct_brands['id'] = itr_item['pk_bint_id']
                        dct_brands['brandcode']=itr_item['vchr_code']
                        lst_brands.append(dct_brands)
                return Response({'status':1,'data':lst_brands})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})

class GroupTypeahead(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:


                lst_group = []

                ins_group = Groups.objects.filter(int_status=0).values('pk_bint_id','vchr_name','vchr_code')
                if ins_group:
                    for itr_item in ins_group:
                        dct_group = {}

                        dct_group['groupname'] = itr_item['vchr_name'].capitalize()
                        dct_group['id'] = itr_item['pk_bint_id']
                        dct_group['groupcode']=itr_item['vchr_code']
                        lst_group.append(dct_group)
                return Response({'status':1,'data':lst_group})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})

class BranchTypeahead(APIView):
    permission_classes = [AllowAny]

    def put(self,request):
        try:

                lst_branch = []
                if(request.data['strData']):
                    str_search_term=request.data['strData']
                    ins_branch = Branch.objects.filter(vchr_name__icontains=str_search_term,int_status=0).values('pk_bint_id','vchr_name')
                else:
                    ins_branch = Branch.objects.filter(int_status=0).values('pk_bint_id','vchr_name')
                if ins_branch:
                    for itr_item in ins_branch:
                        dct_branch = {}

                        dct_branch['branchname'] = itr_item['vchr_name'].capitalize()
                        dct_branch['id'] = itr_item['pk_bint_id']
                        lst_branch.append(dct_branch)
                return Response({'status':1,'data':lst_branch})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})


class UserTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_terms = request.data.get('terms')
            lst_user = []
            if str_terms:
                if not request.user.is_superuser:
                    ins_user = Userdetails.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(full_name__icontains = str_terms) | Q(username__icontains = str_terms), fk_company = request.user.userdetails.fk_company, is_active = True).values('username', 'user_ptr_id','full_name')
                else:
                    ins_user = Userdetails.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(full_name__icontains = str_terms) | Q(username__icontains = str_terms), is_active = True).values('username', 'user_ptr_id','full_name')
                for ins_data in ins_user:
                    dct_data = {}
                    dct_data['intId'] = ins_data['user_ptr_id']
                    dct_data['strUserCode'] = ins_data['username']
                    dct_data['strUserName'] = ins_data['full_name']
                    lst_user.append(dct_data)
            return Response({'status':1,'data':lst_user})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})


class GenerateGuest(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        '''add guest'''
        try:
            # import pdb; pdb.set_trace()
            branch_id = request.user.userdetails.fk_branch_id
            group_id = request.data['intGroup']
            branch_code = request.user.userdetails.fk_branch.vchr_code
            dat_expiry = datetime.strptime(request.data['datExpiry']+' '+request.data['expiryTime'],'%Y-%m-%d %H:%M')

            ins_guest = GuestUserDetails.objects.filter(fk_branch_id=branch_id).values()
            if len(ins_guest) >2:
                ins_expired = ins_guest.filter(Q(session_expiry_time__lte = datetime.now()) | Q(fk_user__int_guest_user = -1))
                if ins_expired:
                    fk_branch= branch_id
                    fk_group= group_id

                    # bln_loop=True
                    # while bln_loop:
                    #         bint_usercode=randint(10000,99999)
                    #         if not (Userdetails.objects.filter(bint_usercode=bint_usercode)):
                    #             bln_loop=False

                    # bln_check = True
                    # while bln_check:
                    #     code=randint(100,999)
                    #     usercode = branch_code + str(code)
                    #     if not(Userdetails.objects.filter(username=usercode)):
                    #         bln_check = False

                    password = uuid3(NAMESPACE_DNS,branch_code).hex[:9]
                    username = ins_expired.values('fk_user_id__username')[0]['fk_user_id__username']

                    Userdetails.objects.get(user_ptr_id = ins_expired.values('fk_user_id')[0]['fk_user_id']).set_password(password)

                    Userdetails.objects.filter(user_ptr_id = ins_expired.values('fk_user_id')[0]['fk_user_id']).update(fk_group_id=fk_group,fk_created_id=request.user.id,dat_created=datetime.now(),int_guest_user=1)
                    ins_expired[0].update(fk_group_id=group_id,session_expiry_time = dat_expiry,dat_created=datetime.now(),fk_created_id=request.user.id,fk_updated_id=request.user.id)

                    # return Response({'status':1,'data':{'username':username,'password':password}}})
                else:
                    return Response({'status':0,'message':'Maximum number of guest users reached'})
            else:
            # rst_user = GuestUserDetails.objects.filter(fk_user_id__in = lst_guest_user,fk_branch_id = branch_id,fk_group_id = group_id).values('fk_user_id','fk_group_id')
            # if not rst_user :
                fk_branch= branch_id
                fk_group= group_id

                bln_loop=True
                while bln_loop:
                        bint_usercode=randint(10000,99999)
                        if not (Userdetails.objects.filter(bint_usercode=bint_usercode)):
                            bln_loop=False

                bln_check = True
                while bln_check:
                    code=randint(100,999)
                    usercode = branch_code + str(code)
                    if not(Userdetails.objects.filter(username=usercode)):
                        bln_check = False

                password = uuid3(NAMESPACE_DNS,branch_code).hex[:9]

                username = usercode

                userobject = Userdetails(bint_usercode=bint_usercode,fk_group_id=fk_group,fk_branch_id=fk_branch,username=username,is_active=True,is_superuser=False,fk_created_id=request.user.id,dat_created=datetime.now(),fk_company_id=request.user.userdetails.fk_company_id,int_guest_user = 1)
                userobject.set_password(password)
                userobject.save()
                guest_user = GuestUserDetails(fk_user_id = userobject.user_ptr_id,session_expiry_time = dat_expiry,fk_group_id = fk_group,fk_branch_id=fk_branch,fk_company_id=request.user.userdetails.fk_company_id,dat_created=datetime.now(),fk_created_id=request.user.id)
                guest_user.save()

            return Response({'status':1,'data':{'username':username,'password':password}})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class GroupsList(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        try:
            lst_group = list(Groups.objects.filter(vchr_name__in=['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']).values('vchr_name','pk_bint_id'))
            return Response({'status':1,'lst_group':lst_group})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
class AddUserBI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            if request.data.get('update_password'):
                """to change password"""
                userobject = Userdetails.objects.get(username = request.data.get('str_username'))
                userobject.set_password(request.data['password'])
                userobject.save()

            else:
                str_username = request.data.get('str_username')
                str_first_name  = request.data.get('str_first_name')
                str_last_name = request.data.get('str_last_name')
                str_email = request.data.get('str_email')
                flt_phone = request.data.get('flt_phone')
                # str_dept =  request.data.get('str_dpt')
                str_group = request.data.get('str_group_name')
                str_branch_code = request.data.get('str_branch_code')
                str_brand = request.data.get('str_brand')
                str_company_name = request.data.get('str_company_name')
                json_product_names = request.data.get('json_product')
                password = request.data.get('password')
                # str_area_code = request.data.get('str_area_code')
                # str_area_name = request.data.get('str_area_name')
                # vchr_profile_pic = request.data.get('vchr_profile_pic')
                str_created_username = request.data.get('str_created_username')

                int_group_id = Groups.objects.filter(vchr_name__iexact = str_group).values_list('pk_bint_id',flat = True).first()
                int_branch_id = Branch.objects.filter(vchr_code = str_branch_code).values_list('pk_bint_id',flat = True).first()
                int_brand_id = Brands.objects.filter(vchr_name = str_brand).values_list('pk_bint_id',flat = True).first()
                int_company_id = Company.objects.filter(vchr_name__iexact = request.data.get('str_company_name')).values_list('pk_bint_id',flat = True).first()
                int_created_id = Userdetails.objects.filter(username = str_created_username).values_list('id',flat = True).first()

                # import pdb; pdb.set_trace()
                json_product = None
                if json_product_names:
                    json_product_id = list(Products.objects.filter(vchr_name__in = json_product_names).values_list('pk_bint_id',flat = True))
                    json_product = {"productId" : list(map(str,json_product_id))}
                if not int_group_id:
                    ins_group = Groups.objects.create(vchr_name = str_group,
                                                      int_status = 0,
                                                      fk_created_id = int_created_id,
                                                      dat_created = datetime.now())

                    int_group_id = ins_group.pk_bint_id


                if request.data.get('update'):
                    """to update"""
                    str_old_username = request.data.get('str_old_username')
                    if str_username != str_old_username  and Userdetails.objects.filter(username=str_username):
                        return Response({'status':0,'message':'Usercode already exists'})

                    userobject = Userdetails.objects.filter(username = str_username).update(bint_phone  =  flt_phone,
                                            fk_group_id = int_group_id,
                                            fk_company_id = int_company_id,
                                            fk_branch_id = int_branch_id,
                                            fk_brand_id = int_brand_id,
                                            vchr_profpic = '/media/default.jpg',
                                            fk_updated_id = int_created_id,
                                            json_product = json_product,
                                            first_name = str_first_name,
                                            last_name = str_last_name,
                                            email = str_email,
                                            username = str_username,
                                            is_active = True,
                                            is_superuser = False,
                                            dat_created = datetime.now(),
                                            dat_updated = datetime.now())

                else:
                    """to add"""

                    bln_loop = True
                    while bln_loop:
                        bint_usercode = randint(10000,99999)
                        if not (Userdetails.objects.filter(bint_usercode = bint_usercode)):
                            bln_loop = False

                    if Userdetails.objects.filter(username=str_username):
                        return Response({'status':0,'message':'Usercode already exists'})

                    userobject = Userdetails(bint_phone  =  flt_phone,
                                            fk_group_id = int_group_id,
                                            fk_company_id = int_company_id,
                                            fk_branch_id = int_branch_id,
                                            fk_brand_id = int_brand_id,
                                            bint_usercode = bint_usercode,
                                            vchr_profpic = '/media/default.jpg',
                                            fk_created_id = int_created_id,
                                            json_product = json_product,
                                            first_name = str_first_name,
                                            last_name = str_last_name,
                                            email = str_email,
                                            username = str_username,
                                            is_active = True,
                                            is_superuser = False,
                                            dat_created = datetime.now(),
                                            dat_updated = datetime.now())

                    userobject.set_password(password)
                    userobject.save()



            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})

class WebVersionGet(APIView):
    permission_classes = [AllowAny,]
    def post(self, request):
        # import pdb;pdb.set_trace()
        filepath = settings.BASE_DIR+"/webversion.txt"
        file1 = open(filepath,"r+")
        version = file1.read().splitlines()
        int_version = int(version[0])

        return Response({'status': '1','int_version':int_version})

class ChangePassword(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        """
        {
            userName:'MYGE-597',
            oldPassword = 'testpass',
            newPassword = 'testpass1',
        }
        """
        try:
            # import pdb; pdb.set_trace()
            _username= request.data.get('userName')
            _password=request.data.get('oldPassword')
            new_password = request.data.get('newPassword')
            user = authenticate(request, username=_username, password=_password)
            if user:
                user_ = Userdetails.objects.get(id = user.id)
                if user_.id == request.user.id:
                    user_.fk_updated_id = request.user.id
                    user_.dat_updated=datetime.now()
                    user_.set_password(new_password)
                    user_.save()

                    return Response({'status':1,"message":"Passward Changed Successfully..:)"})
                else:
                    return Response({'status':0,'message':"You are not Authorized To change User "+_username+"'s Passward.."})

            else:
                return Response({'status':0,'message':"Authentication Failed \n Incorrect Old Pasward..!, Try Again"})

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})
        finally:
            pass


class AddEcomUser(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:

            str_branch_code = request.data.get('str_branch_code')
            str_company_code = request.data.get('str_comp_code')

            int_branch_id = Branch.objects.filter(vchr_code = str_branch_code).values_list('pk_bint_id',flat = True).first()

            int_company_id = Company.objects.filter(vchr_name__icontains = str_company_code ).values_list('pk_bint_id',flat = True).first()
            str_first_name = request.data.get("first_name")
            str_last_name = request.data.get("last_name")
            int_phone = request.data.get("bint_phone")
            str_username = request.data.get("username")
            str_com_code = request.data.get("str_comp_code")


            userobject = Userdetails(bint_phone  =  int_phone,
                                    fk_company_id = int_company_id,
                                    fk_branch_id = int_branch_id,
                                    # bint_usercode = bint_usercode,
                                    vchr_profpic = '/media/default.jpg',
                                    first_name = str_first_name,
                                    last_name = str_last_name,
                                    email = '--',
                                    username = str_username,
                                    is_active = False,
                                    is_superuser = False,
                                    dat_created = datetime.now(),
                                    dat_updated = datetime.now())

            userobject.set_password('testpass')
            userobject.save()



            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})
