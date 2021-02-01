from uuid import uuid3, NAMESPACE_DNS
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from userdetails.models import UserDetails,DocumentHrms,GuestUserDetails, UserPermissions,EmpReferences,ReligionCaste, WPS ,UserHistory ,EmpFamily,EmpEduDetails,EmpExpDetails
from shift_schedule.models import ShiftSchedule, EmployeeShift
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
from url_check.models import SessionHandler
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Value, BooleanField, Case, When,F
from django.db.models.functions import Concat
from django.conf import settings
from tool_settings.models import Tools
from POS import ins_logger
import sys, os
import requests
import json
import pandas as pd
from userdetails.models import ReligionCaste
from django.db.models import F, Q, Value, Case, When,TextField, IntegerField, CharField, DateField,BooleanField,DurationField,ExpressionWrapper, Func, FloatField
# from company_permission.models import SubCategory, MenuCategory
from company_permissions.models import SubCategory,MenuCategory
from os import path
from django.db.models.functions import Concat, Substr, Cast
from userdetails.models import SalaryDetails
# Create your views here.



class ReligionCasteList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            lst_religion = list(ReligionCaste.objects.filter(bln_active=True).annotate(intId=F('pk_bint_id'),strName=F('vchr_name')).values('intId','strName').order_by('strName'))
            return Response({'status': 1, 'data':lst_religion})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

            
class UpdateUserPassword(APIView):
    '''Change user password'''
    permission_classes=[AllowAny]


    def post(self,request):
        try:
            
            user_ptr_id=int(request.data.get("intId"))
            password=request.data.get("strNewPassword")
            userobject=UserDetails.objects.get(id = user_ptr_id )
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
            # 
            if request.GET.get("id"):
                pk_bint_id=int(request.GET.get("id"))
                if(UserDetails.objects.filter(user_ptr_id=pk_bint_id,is_active=1)):
                    lst_userdetails= list(UserDetails.objects.filter(user_ptr_id=pk_bint_id).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','fk_branch_id','fk_branch__vchr_name','fk_brand_id','fk_group_id','fk_company_id','bint_usercode','fk_company__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined')) #passes as a list object
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
                    lst_userdetails= list(UserDetails.objects.filter(is_active=True).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))

                else:

            # lst_userdetails= list(Userdetails.objects.filter(is_active=True).values('pk_bint_id','bint_phone','fk_group','fk_company','fk_branch', 'fk_brand','bint_usercode','vchr_profpic','dat_resapp','int_areaid','dat_creaed','dat_updated','fk_created','fk_updated')) #passes as a list object
                    lst_userdetails= list(UserDetails.objects.filter(is_active=True,fk_branch_id = request.user.userdetails.fk_branch_id).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))
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
                lst_userdetails= list(UserDetails.objects.filter(is_active=True).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))

            else:

                lst_userdetails= list(UserDetails.objects.filter(is_active=True,fk_branch_id = request.user.userdetails.fk_branch_id).values('user_ptr_id','bint_phone','fk_group__vchr_name','fk_brand__vchr_name','bint_usercode','fk_company__vchr_name','fk_branch_id','fk_branch__vchr_name','vchr_profpic','dat_resapp','int_areaid','dat_created','dat_updated','username','first_name','last_name','email','is_active','date_joined').order_by('-dat_created','-dat_updated'))
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

# class AddUsers(APIView):
#     permission_classes=[AllowAny]


#     def post(self,request):
#         '''add users'''
#         try:
#             # 
#             with transaction.atomic():
#                 # 
#                 first_name  = str(request.data.get('firstname'))
#                 bint_phone = int(request.data.get('contactno'))
#                 # str_pssrsttkn= str(request.data.get('vchr_pssrsttkn'))
#                 # bint_pssrstflg= int(request.data.get('bint_pssrstflg'))
#                 # dat_passrsttim= request.data.get('dat_passrsttim')
#                 # fk_group= request.data.get('fk_group')

#                 # fk_company = int(request.data.get('companyid'))
#                 fk_branch= int(request.data.get('branch_id'))
#                 fk_group= int(request.data.get('group_id'))
#                 bln_loop=True
#                 while bln_loop:
#                         bint_usercode=randint(10000,99999)
#                         if not (Userdetails.objects.filter(bint_usercode=bint_usercode)):
#                             bln_loop=False



#                 # bint_usercode= int(request.data.get('vchr_user_code'))
#                 vchr_prof = request.FILES.get('image')

#                 if vchr_prof:
#                         my_file = request.FILES.get('image')
#                         fs = FileSystemStorage(location=settings.MEDIA_ROOT)
#                         filename = fs.save(my_file.name, my_file)
#                         str_profpic = fs.url(filename)


#                 # dat_resapp= request.data.get('dat_resapp')
#                 # int_areaid= request.data.get('int_areaid')
#                 # dat_created= request.data.get('dat_created')
#                 # dat_updated= request.data.get('dat_updated')
#                 # fk_created= request.data.get('fk_created')
#                 # fk_updated= request.data.get('fk_updated')
#                 # json_product = request.data.get('json_product')
#                 # id1=request.data.get('id')
#                 # last_login=request.data.get('last_login')
#                 # is_superuser=request.data.get('is_superuser')
#                 username = str(request.data.get('vchr_user_code'))
#                 # first_name=request.data.get('firstname')
#                 last_name=str(request.data.get('lastname'))
#                 email=str(request.data.get('email'))
#                 # is_staff=request.data.get('is_staff')

#                 # date_joined=request.data.get('date_joined')
#                 # if Userdetails.objects.filter(username=username,bint_usercode=bint_usercode,is_active=True):
#                 #     return Response({'status':0,'reason':'already exists'})
#                 # else:
#                     # Userdetails.objects.create(bint_phone=bint_phone,vchr_pssrsttkn=str_pssrsttkn,bint_pssrstflg=bint_pssrstflg,dat_passrsttim=dat_passrsttim,fk_group=fk_group,fk_company=fk_company,fk_branch=fk_branch,fk_brand=fk_brand,bint_usercode=bint_usercode,vchr_profpic=str_profpic,dat_resapp=dat_resapp,int_areaid=int_areaid,dat_created=dat_created,dat_updated=dat_updated,fk_created=fk_created,fk_updated=fk_updated,json_product=json_product,id=id1,password=password,last_login=last_login,is_superuser=is_superuser,username=username,first_name=first_name,last_name=last_name,email=email,is_staff=is_staff,date_joined=date_joined,is_active=True)
#                     #
#                 if Userdetails.objects.filter(username=username):
#                     return Response({'status':0,'message':'Usercode already exists'})
#                 else:
#                     if request.data.get('brand'):
#                         fk_brand= int(request.data.get('brand'))
#                         userobject=Userdetails(bint_phone=bint_phone,bint_usercode=bint_usercode,fk_brand_id=fk_brand,fk_branch_id=fk_branch,fk_group_id=fk_group,vchr_profpic=str_profpic,username=username,first_name=first_name,last_name=last_name,email=email,is_active=True,is_superuser=False,date_joined=datetime.now(),fk_created_id=request.user.id,dat_created=datetime.now(),fk_company_id=request.user.userdetails.fk_company_id)
#                     else:
#                         userobject=Userdetails(bint_phone=bint_phone,bint_usercode=bint_usercode,fk_group_id=fk_group,fk_branch_id=fk_branch,vchr_profpic=str_profpic,username=username,first_name=first_name,last_name=last_name,email=email,is_active=True,is_superuser=False,date_joined=datetime.now(),fk_created_id=request.user.id,dat_created=datetime.now(),fk_company_id=request.user.userdetails.fk_company_id)
#                 userobject.set_password(request.data.get('password'))
#                 userobject.save()
#                 lst_branch = [int(int_id) for int_id in request.data.get('lstBranchId').split(',')] if request.data.get('lstBranchId') else []
#                 lst_product = [int(int_id) for int_id in request.data.get('lstProductId').split(',')] if request.data.get('lstProductId') else []
#                 lst_item_groups = [int(int_id) for int_id in request.data.get('lstItemGroupId').split(',')] if request.data.get('lstItemGroupId') else []
#                 lst_branch_type = [int(int_id) for int_id in request.data.get('lstBranchType').split(',')] if request.data.get('lstBranchType') else []
#                 dct_price_perm = request.data.get('dctPriceList') if   request.data.get('dctPriceList') else None
#                 if lst_branch or lst_product or lst_item_groups or dct_price_perm or lst_branch_type:
#                     ins_user_permission = UserPermissions(fk_user = userobject, jsn_branch_type = lst_branch_type, jsn_branch = lst_branch, jsn_product = lst_product, jsn_item_group = lst_item_groups,json_price_perm = request.data.get('dctPriceList') )
#                     ins_user_permission.save()

#                 # ins_user_permission = UserPermissions.objects.filter(fk_user=userobject, bln_active=True)
#                 # if ins_user_permission:
#                 #     ins_user_permission.update(jsn_branch_type = lst_branch_type)
#                 # elif request.data.get('blnSalesCounter'):
#                 #     UserPermissions.objects.create(fk_user=userobject,jsn_branch_type = lst_branch_type, jsn_branch = [], jsn_product = [], jsn_item_group = [])

#                 return Response({'status':1,'message':'created successfully'})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'status':0,'reason':e})

class AddUsers(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
          
            with transaction.atomic():
                username = str(request.data.get('strUserName'))
                if UserDetails.objects.filter(username = username):
                    return Response({'status':0,'message':'Username already exists'})

                str_category_code = request.data.get('strCategoryCode') if request.data.get('strCategoryCode') !='null' else ""
                int_company_id = request.data.get("intCompanyId") or request.user.userdetails.fk_company_id
                ins_document = DocumentHrms.objects.get(vchr_module_name = 'EMPLOYEE CODE',fk_company_id = int_company_id)
                str_employee_code = ins_document.vchr_short_code+str_category_code.upper()+"-"+str(ins_document.int_number)
                ins_document.int_number = ins_document.int_number+1
                ins_document.save()
                str_img_path = ""
                if request.data.get('imgSrc'):
                    img_emp = request.data.get('imgSrc')
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT+'/UserProfilePics', base_url=settings.MEDIA_URL+'UserProfilePics/')
                    str_img = fs.save(str_employee_code+datetime.now().strftime('-%Y%m%d%H%M%S%f.')+img_emp.name.split('.')[-1], img_emp)
                    str_img_path = fs.url(str_img)
                '''add users'''
                int_salary_struct_id = int(request.data.get("intSalaryStructId")) if request.data.get("intSalaryStructId") else None
                dct_allowances = json.loads(request.data.get('dctAllowances'))
                lst_phy_loc = json.loads(request.data.get('lstLoc')) if request.data.get('lstLoc') else None
                dbl_gross = int(request.data.get("dblGrossPay")) if request.data.get("dblGrossPay") else None
                int_category_id = int(request.data.get("intCategoryId")) if request.data.get("intCategoryId") else None
                ins_user = UserDetails(vchr_employee_code = str_employee_code,
                                       vchr_salutation = request.data.get('strSalutation',None),
                                       first_name = request.data.get("strFirstName"),
                                       last_name = request.data.get("strLastName"),
                                       username = str_employee_code,
                                       bint_phone = request.data.get("intPhoneNumber"),
                                       email = request.data.get("strEmail"),
                                       vchr_email = request.data.get("strEmail"),
                                       dat_doj = request.data.get("datJoin"),
                                       dat_dob = request.data.get("datDob"),
                                       vchr_gender = request.data.get("strGender"),
                                       vchr_marital_status = request.data.get('strMaritalStatus',None),
                                       vchr_blood_group = request.data.get('strBloodGroup',None),
                                       fk_department_id = int(request.data.get("intDptId")) if request.data.get("intDptId") else None,
                                       fk_category_id = int_category_id,
                                       fk_branch_id = int(request.data.get("intBranchId")) if request.data.get("intBranchId") else None,
                                       fk_company_id = int(int_company_id),
                                       dat_created = datetime.now(),
                                       fk_created_id = request.user.id,
                                       is_active = True,
                                       fk_salary_struct_id = int_salary_struct_id,
                                    #    fk_desig_id = int(request.data.get("intDesigId")) if request.data.get("intDesigId") else None,
                                       vchr_level = request.data.get("strGrade"),
                                       vchr_grade = request.data.get("strLevelofGrade"),
                                       json_allowance = dct_allowances,
                                       dbl_gross = dbl_gross,
                                       vchr_middle_name = request.data.get("strMiddleName", None),
                                       int_payment = int(request.data.get("intPaymentMode")) if request.data.get("intPaymentMode") else None,
                                       vchr_pan_no = request.data.get("intPanNo", None),
                                       vchr_aadhar_no = request.data.get("intAadharNo", None),
                                       vchr_img = str_img_path or "",
                                       vchr_bank_name = request.data.get("strBankName", None),
                                       vchr_acc_no = request.data.get("intAccountNum").zfill(16) if request.data.get("intAccountNum") else None,
                                       vchr_ifsc = request.data.get("strIfscCode", None),
                                       fk_brand_id = int(request.data.get("intBrandId")) if request.data.get("intBrandId") else None,
                                    #    fk_product_id = int(request.data.get("intProductId")) if request.data.get("intProductId") else None,
                                       json_function = request.data.get("intProductId") if request.data.get("intProductId") else None,
                                       vchr_file_no = request.data.get("strFileNo", None),
                                       json_physical_loc = lst_phy_loc,
                                       vchr_address = request.data.get("strAddress", None),
                                       int_weekoff_type = int(request.data.get("intWeekOffType")) if request.data.get("intWeekOffType") else None,
                                       vchr_po = request.data.get("strPo", None),
                                       vchr_land_mark = request.data.get("strLandMark", None),
                                       vchr_place = request.data.get("strPlace", None),
                                       fk_dist_id = request.data.get("intDistId") if request.data.get("intDistId")  else None,
                                       int_pincode =  request.data.get("intPincode")  if request.data.get("intPincode") else None,
                                       vchr_pf_no = request.data.get('strPfNo', None),
                                       vchr_esi_no = request.data.get('strEsiNo', None),
                                       vchr_uan_no = request.data.get('strUanNo', None),
                                       vchr_wwf_no = request.data.get('strWwfNo', None),
                                       vchr_weekoff_day  =request.data.get('strDay', None),
                                       vchr_father_name = request.data.get('strFatherName', None),
                                       vchr_emergency_person = request.data.get('strEmerPerson',None),
                                       vchr_emergency_relation = request.data.get('strEmerRelation',None),
                                       bint_emergency_phno = request.data.get('intEmPhNo', None),
                                       fk_religion_id = int(request.data.get('intReligionId',None)),
                                       is_superuser = False,
                                       fk_wps_id = request.data.get('intWpsId') if request.data.get('intWpsId') and request.data.get('intWpsId')!='null' else None,
                                       vchr_disease = request.data.get('strIllnessDetails', None),
                                       vchr_emp_remark = request.data.get('strEmpRemarks') if request.data.get('strEmpRemarks') else None,
                                       int_official_num = int(request.data.get('intOfficialNumber')) if request.data.get('intOfficialNumber') else None,
                                       fk_hierarchy_data_id = request.data.get('lstLoc', None),
                                       fk_group_id = request.data.get('groupId', None),
                                       fk_hierarchy_group_id = request.data.get('hGroup') if request.data.get('hGroup') !='null' else None)
                                    #    )
                                    #    fk_hierarchy_group_id = request.data.get('hGroup', None))
                                    #    fk_group_id = request.data.get('groupId', None),


                ins_user.set_password(request.data.get('strPassword'))
                # import pdb; pdb.set_trace()
                ins_user.save()
                # ============================================= Reference =================================================
                lst_ref = json.loads(request.data.get('lstReference'))
                lst_ins_ref = []
                for data in lst_ref:
                    if data.get('strRefName') or data.get('strRefDesig') or data.get('intRefPhone') or data.get('strRefEmail'):
                        if not data.get('intRefId'):
                            ins_ref = EmpReferences(fk_employee_id = ins_user.user_ptr_id,
                                                    vchr_name = data.get('strRefName'),
                                                    vchr_company_name = data.get('strCompName'),
                                                    vchr_desig = data.get('strRefDesig'),
                                                    vchr_phone = data.get('intRefPhone'),
                                                    vchr_email = data.get('strRefEmail'),
                                                    int_status = 1)
                            lst_ins_ref.append(ins_ref)
                EmpReferences.objects.bulk_create(lst_ins_ref)
                # ==========================================================================================================

                # ============================================= Family Details =============================================
                lst_family_details = json.loads(request.data.get("lstFamilyDetails")) if request.data.get("lstFamilyDetails") else []
                if lst_family_details:
                    lst_ins_family = []
                    for data in lst_family_details:
                        if data.get('strRelation') or data.get('strRelativeName') or data.get('strOccupation') or data.get('isAlive') or data.get('relativeDOB'):
                            if not data.get('intFamilyId'):
                                ins_fmly= EmpFamily(fk_employee_id = ins_user.user_ptr_id,
                                                vchr_name = data.get('strRelativeName'),
                                                vchr_realation = data.get('strRelation'),
                                                dat_dob = data.get('relativeDOB'),
                                                vchr_occupation = data.get('strOccupation'),
                                                vchr_alive = data.get('isAlive'),
                                                int_status = 1)
                                lst_ins_family.append(ins_fmly)
                    EmpFamily.objects.bulk_create(lst_ins_family)
                # ==========================================================================================================

                # =========================================== Education Details ============================================
                lst_edu_detail =  json.loads(request.data.get("lstEduDetails")) if request.data.get("lstEduDetails") else []
                if lst_edu_detail:
                    lst_ins_edu = []
                    for dct_data in lst_edu_detail:
                        if dct_data.get('intYear') or dct_data.get('strInstituion') or dct_data.get('strCourse') or dct_data.get('strUniversity') or dct_data.get('strQualif'):
                            if not dct_data.get('pk_bint_id'):
                                ins_edu = EmpEduDetails(fk_employee_id = ins_user.user_ptr_id,
                                                        bln_highest_qualif = dct_data.get('blnHighest'),
                                                        vchr_qualif = dct_data.get('strQualif'),
                                                        vchr_course = dct_data.get('strCourse'),
                                                        vchr_institution = dct_data.get('strInstituion'),
                                                        int_pass_year = int(dct_data.get('intYear')),
                                                        vchr_university = dct_data.get('strUniversity'),
                                                        vchr_place = dct_data.get('strPlace'),
                                                        dbl_percentage = dct_data.get('fltPercentage'),
                                                        vchr_specialzation = dct_data.get('strSpecialization'),
                                                        bln_active = True)
                                lst_ins_edu.append(ins_edu)
                    EmpEduDetails.objects.bulk_create(lst_ins_edu)
                # ==========================================================================================================

                # ========================================= Experiance Details =============================================
                lst_exp_detail =  json.loads(request.data.get("lstExpDetails")) if request.data.get("lstExpDetails") else []
                if lst_exp_detail:
                    lst_ins_exp = []
                    for dct_data in lst_exp_detail:
                        if dct_data.get('strEmployer') or dct_data.get('vchrExpDetails') or dct_data.get('strDesig'):
                            if not dct_data.get('pk_bint_id'):
                                ins_exp = EmpExpDetails(fk_employee_id =  ins_user.user_ptr_id,
                                                              vchr_employer = dct_data.get('strEmployer'),
                                                              vchr_designation = dct_data.get('strDesig'),
                                                              txt_exp_details = dct_data.get('vchrExpDetails'),
                                                              bln_active = True)
                                lst_ins_exp.append(ins_exp)
                    EmpExpDetails.objects.bulk_create(lst_ins_exp)
                # ==========================================================================================================

                #================================Employee Shift ============================================================
                #assigning shift type in employee_shift table
                if request.data.get("intShiftType") or json.loads(request.data.get("jsonShiftId")):
                    ins_employee_shift = EmployeeShift.objects.create(fk_employee_id = ins_user.user_ptr_id,
                                                                      int_shift_type = int(request.data.get("intShiftType")) if request.data.get("intShiftType") else None,
                                                                      json_shift = json.loads(request.data.get("jsonShiftId")),
                                                                      bln_active = True,
                                                                      dat_created = datetime.now(),
                                                                      fk_created_id = request.user.id)


                #==================================salary details==============================================================
                dct_data = {}
                if int_salary_struct_id and dct_allowances and dbl_gross :
                    if request.data.get('strSalaryStructName') == 'Slab-0':
                        dct_data = eval(request.data.get('dctSalarySplit'))
                        dct_data['Deductions']['Charity'] = int(request.data.get('dblCharity')) if request.data.get('dblCharity') else 0
                        dct_data['Deductions']['TDS'] = int(request.data.get('dblTds')) if request.data.get('dblTds') else 0
                    else:
                        dct_structure = SalaryStructure.objects.filter(pk_bint_id = int_salary_struct_id, bln_active=True).values('vchr_name', 'dbl_bp_da',
                                                                                                                              'dbl_bp_da_per', 'dbl_da',
                                                                                                                              'json_rules').first()
                        dct_structure['dblCharity'] = int(request.data.get('dblCharity')) if request.data.get('dblCharity') else 0
                        dct_structure['dblTds'] = int(request.data.get('dblTds')) if request.data.get('dblTds') else 0
                        dct_struct = {data['vchr_type']:{'Allowances':data['dbl_empr_share'], 'Deductions':data['dbl_empy_share']} for data in PfandEsiStructure.objects.filter(Q(int_end_month__isnull=True, int_end_year__isnull=True) | Q(int_end_month__gte=datetime.now().month, int_end_year__gte=datetime.now().year), int_start_month__lte=datetime.now().month, int_start_year__lte=datetime.now().year).values('vchr_type', 'dbl_empr_share', 'dbl_empy_share')}
                        if dct_structure.get('json_rules', {}).get('Allowances', {}).get('PF') != None and dct_struct.get('PF', {}).get('Allowances') != None:
                            dct_structure['json_rules']['Allowances']['PF'] = dct_struct['PF']['Allowances']
                        if dct_structure.get('json_rules', {}).get('Deductions', {}).get('PF') != None and dct_struct.get('PF', {}).get('Deductions') != None:
                            dct_structure['json_rules']['Deductions']['PF'] = dct_struct['PF']['Deductions']
                        dct_data = GenerateSalaryProcess(dbl_gross, dct_structure, dct_allowances)

                if dct_data:
                    SalaryDetails.objects.create(fk_employee_id = ins_user.user_ptr_id,
                                                 dbl_bp = dct_data.get('BP_DA'),
                                                 dbl_da = dct_data.get('DA', 0),
                                                 dbl_hra = dct_data.get('HRA'),
                                                 dbl_cca = dct_data.get('CCA'),
                                                 dbl_sa = dct_data.get('SA'),
                                                 dbl_wa = dct_data.get('WA'),
                                                 dbl_gross = dbl_gross,
                                                 json_deduction = dct_data.get('Deductions'),
                                                 json_allowance = dct_data.get('Allowances'),
                                                 fk_created_id = request.user.id,
                                                 int_status = 1 )
                # ===============================================================================================================

                # ==================================================== History ==================================================
                # 
                if request.data.get('blnNewEmp') == 'true':
                    AppliedJobDetails.objects.filter(pk_bint_id=request.data.get('intNewEmpJobId')).update(int_offer_status=7)
                    AppliedJobDetails.objects.filter(Q(fk_applicant_id=request.data.get('intNewEmpId')) & ~Q(pk_bint_id=request.data.get('intNewEmpJobId'))).update(int_offer_status=-2)
                dct_history = {}
                dct_history['vchr_employee_code'] = {'Value':str_employee_code, 'bln_change':False}
                dct_history['username'] =  {'Value':str_employee_code, 'bln_change':False}
                dct_history['first_name'] =  {'Value':request.data.get('strFirstName'), 'bln_change':False}
                dct_history['middle_name'] =  {'Value':request.data.get('strMiddleName'), 'bln_change':False}
                dct_history['last_name'] =  {'Value':request.data.get('strLastName'), 'bln_change':False}
                dct_history['email'] =  {'Value':request.data.get('strEmail'), 'bln_change':False}
                dct_history['dat_joined'] =  {'Value':request.data.get('datJoin'), 'bln_change':False}
                dct_history['fk_category_id'] =  {'Value':int_category_id, 'bln_change':False}
                dct_history['bint_phone'] =  {'Value':request.data.get('intPhoneNumber'), 'bln_change':False}
                dct_history['dat_dob'] =  {'Value':request.data.get('datDob'), 'bln_change':False}
                dct_history['vchr_gender'] =  {'Value':request.data.get('strGender'), 'bln_change':False}
                dct_history['vchr_level'] =  {'Value':request.data.get('strGrade'), 'bln_change':False}
                dct_history['vchr_grade'] =  {'Value':request.data.get('strLevelofGrade'), 'bln_change':False}
                dct_history['fk_salary_struct_id'] =  {'Value':int_salary_struct_id, 'bln_change':False}
                dct_history['fk_branch_id'] =  {'Value':int(request.data.get("intBranchId")) if request.data.get("intBranchId") else None, 'bln_change':False}
                dct_history['fk_department_id'] =  {'Value':int(request.data.get("intDptId")) if request.data.get("intDptId") else None, 'bln_change':False}
                dct_history['fk_company_id'] =  {'Value':int(int_company_id), 'bln_change':False}
                dct_history['dbl_gross'] =  {'Value':dbl_gross, 'bln_change':False}
                # dct_history['fk_desig_id'] =  {'Value':int(request.data.get("intDesigId")) if request.data.get("intDesigId") else None, 'bln_change':False}
                dct_history['int_payment'] =  {'Value':int(request.data.get("intPaymentMode")) if request.data.get("intPaymentMode") else None, 'bln_change':False}
                dct_history['vchr_pan_no'] =  {'Value':request.data.get("intPanNo"), 'bln_change':False}
                dct_history['vchr_aadhar_no'] =  {'Value':request.data.get("intAadharNo"), 'bln_change':False}
                dct_history['vchr_img'] =  {'Value':str_img_path or "", 'bln_change':False}
                dct_history['vchr_bank_name'] =  {'Value':request.data.get("strBankName"), 'bln_change':False}
                dct_history['vchr_acc_no'] =  {'Value':request.data.get("intAccountNum").zfill(16) if request.data.get("intAccountNum") else None, 'bln_change':False}
                dct_history['vchr_ifsc'] =  {'Value':request.data.get('strIfscCode'), 'bln_change':False}
                dct_history['fk_brand_id'] =  {'Value':int(request.data.get("intBrandId")) if request.data.get("intBrandId") else None, 'bln_change':False}
                dct_history['json_function'] =  {'Value':request.data.get("intProductId") if request.data.get("intProductId") else None, 'bln_change':False}
                dct_history['vchr_file_no'] =  {'Value':request.data.get("strFileNo"), 'bln_change':False}
                dct_history['vchr_address'] =  {'Value':request.data.get('strAddress'), 'bln_change':False}
                dct_history['int_weekoff_type'] =  {'Value':int(request.data.get("intWeekOffType")) if request.data.get("intWeekOffType") else None, 'bln_change':False}
                dct_history['json_physical_loc'] =  {'Value':lst_phy_loc, 'bln_change':False}
                dct_history['vchr_po'] =  {'Value':request.data.get("strPo"), 'bln_change':False}
                dct_history['vchr_land_mark'] =  {'Value':request.data.get('strLandMark'), 'bln_change':False}
                dct_history['vchr_place'] =  {'Value':request.data.get('strPlace'), 'bln_change':False}
                dct_history['int_pincode'] =  {'Value':request.data.get("intPincode") if request.data.get("intPincode") else None, 'bln_change':False}
                dct_history['fk_dist_id'] =  {'Value':request.data.get("intDistId") if request.data.get("intDistId")  else None, 'bln_change':False}
                dct_history['vchr_esi_no'] =  {'Value':request.data.get('strEsiNo'), 'bln_change':False}
                dct_history['vchr_uan_no'] =  {'Value':request.data.get('strUanNo'), 'bln_change':False}
                dct_history['vchr_wwf_no'] =  {'Value':request.data.get('strWwfNo'), 'bln_change':False}
                dct_history['vchr_weekoff_day'] =  {'Value':request.data.get('strDay'), 'bln_change':False}
                dct_history['bint_emergency_phno'] =  {'Value':request.data.get('intEmPhNo'), 'bln_change':False}
                dct_history['vchr_father_name'] =  {'Value':request.data.get('strFatherName'), 'bln_change':False}
                dct_history['vchr_salutation'] =  {'Value':request.data.get('strSalutation'), 'bln_change':False}
                dct_history['vchr_marital_status'] =  {'Value':request.data.get('strMaritalStatus', None), 'bln_change':False}
                dct_history['vchr_blood_group'] =  {'Value':request.data.get('strBloodGroup'), 'bln_change':False}
                dct_history['vchr_emergency_person'] =  {'Value':request.data.get('strEmerPerson'), 'bln_change':False}
                dct_history['vchr_emergency_relation'] =  {'Value':request.data.get('strEmerRelation'), 'bln_change':False}
                dct_history['fk_religion_id'] =  {'Value':request.data.get('intReligionId', None), 'bln_change':False}
                dct_history['fk_wps_id'] = {'Value':request.data.get('intWpsId'), 'bln_change':False}
                dct_history['vchr_disease'] = {'Value':request.data.get('strIllnessDetails'), 'bln_change':False}
                dct_history['lst_reference'] = []
                for ref_data in json.loads(request.data.get('lstReference')):
                    if ref_data.get('strRefName') or ref_data.get('strCompName') or ref_data.get('strRefDesig') or ref_data.get('strRefEmail') or ref_data.get('intRefPhone'):
                        dct_ref = {}
                        dct_ref['strRefName'] = {'Value':ref_data.get('strRefName'), 'bln_change':False}
                        dct_ref['strCompName'] = {'Value':ref_data.get('strCompName'), 'bln_change':False}
                        dct_ref['strRefDesig'] = {'Value':ref_data.get('strRefDesig'), 'bln_change':False}
                        dct_ref['strRefEmail'] = {'Value':ref_data.get('strRefEmail'), 'bln_change':False}
                        dct_ref['intRefPhone'] = {'Value':ref_data.get('intRefPhone'), 'bln_change':False}
                        dct_history['lst_reference'].append(dct_ref)
                dct_history['lst_family_details'] = []
                for fam_data in json.loads(request.data.get("lstFamilyDetails")):
                    if fam_data.get('strRelativeName') or fam_data.get('strRelation') or fam_data.get('relativeDOB') or fam_data.get('strOccupation') or fam_data.get('isAlive'):
                        dct_fan = {}
                        dct_fan['strRelativeName'] = {'Value':fam_data.get('strRelativeName'), 'bln_change':False}
                        dct_fan['strRelation'] = {'Value':fam_data.get('strRelation'), 'bln_change':False}
                        dct_fan['relativeDOB'] = {'Value':fam_data.get('relativeDOB'), 'bln_change':False}
                        dct_fan['strOccupation'] = {'Value':fam_data.get('strOccupation'), 'bln_change':False}
                        dct_fan['isAlive'] = {'Value':fam_data.get('isAlive'), 'bln_change':False}
                        dct_history['lst_family_details'].append(dct_fan)
                dct_history['lst_edu_details'] = []
                for edu_data in json.loads(request.data.get("lstEduDetails")):
                    if edu_data.get('blnHighest') or edu_data.get('strQualif') or edu_data.get('strCourse') or edu_data.get('strInstituion') or edu_data.get('intYear') or edu_data.get('strUniversity') or edu_data.get('strPlace') or edu_data.get('fltPercentage') or edu_data.get('strSpecialization'):
                        dct_edu = {}
                        dct_edu['blnHighest'] = {'Value':edu_data.get('blnHighest'), 'bln_change':False}
                        dct_edu['strQualif'] = {'Value':edu_data.get('strQualif'), 'bln_change':False}
                        dct_edu['strCourse'] = {'Value':edu_data.get('strCourse'), 'bln_change':False}
                        dct_edu['strInstituion'] = {'Value':edu_data.get('strInstituion'), 'bln_change':False}
                        dct_edu['intYear'] = {'Value':edu_data.get('intYear'), 'bln_change':False}
                        dct_edu['strUniversity'] = {'Value':edu_data.get('strUniversity'), 'bln_change':False}
                        dct_edu['strPlace'] = {'Value':edu_data.get('strPlace'), 'bln_change':False}
                        dct_edu['fltPercentage'] = {'Value':edu_data.get('fltPercentage'), 'bln_change':False}
                        dct_edu['strSpecialization'] = {'Value':edu_data.get('strSpecialization'), 'bln_change':False}
                        dct_history['lst_edu_details'].append(dct_edu)
                dct_history['lst_exp_details'] = []
                for exp_data in json.loads(request.data.get("lstExpDetails")):
                    if exp_data.get('strEmployer') or exp_data.get('vchrExpDetails') or exp_data.get('strDesig'):
                        dct_exp = {}
                        dct_exp['strEmployer'] = {'Value':exp_data.get('strEmployer'), 'bln_change':False}
                        dct_exp['vchrExpDetails'] = {'Value':exp_data.get('vchrExpDetails'), 'bln_change':False}
                        dct_exp['strDesig'] = {'Value':exp_data.get('strDesig'), 'bln_change':False}
                        dct_history['lst_exp_details'].append(dct_exp)
                dct_history['json_shift'] = {}
                dct_history['json_shift']['int_shift_type'] = {'Value':int(request.data.get("intShiftType")), 'bln_change':False}
                dct_history['json_shift']['dct_shift'] = {'Value':json.loads(request.data.get("jsonShiftId")), 'bln_change':False}
                dct_history['json_salary_details'] = {}
                dct_history['json_salary_details']['salary_struct_name'] = {'Value':request.data.get('strSalaryStructName'), 'bln_change':False}
                dct_history['json_salary_details']['salary_struct_id'] = {'Value':int_salary_struct_id, 'bln_change':False}
                dct_history['json_salary_details']['dct_allowances_rules'] = {}
                for allw_data in dct_allowances:
                    dct_history['json_salary_details']['dct_allowances_rules'][allw_data] = {'Value':dct_allowances[allw_data], 'bln_change':False}
                dct_history['json_salary_details']['dct_details'] = {}
                if dct_data:
                    dct_history['json_salary_details']['dct_details']['BP_DA'] = {'Value':dct_data['BP_DA'], 'bln_change':False}
                    dct_history['json_salary_details']['dct_details']['HRA'] = {'Value':dct_data['HRA'], 'bln_change':False}
                    dct_history['json_salary_details']['dct_details']['CCA'] = {'Value':dct_data['CCA'], 'bln_change':False}
                    dct_history['json_salary_details']['dct_details']['WA'] = {'Value':dct_data['WA'], 'bln_change':False}
                    dct_history['json_salary_details']['dct_details']['SA'] = {'Value':dct_data['SA'], 'bln_change':False}
                    dct_history['json_salary_details']['dct_details']['Allowances'] = {}
                    for allw_data in dct_data['Allowances']:
                        dct_history['json_salary_details']['dct_details']['Allowances'][allw_data] = {'Value':dct_data['Allowances'][allw_data], 'bln_change':False}
                    dct_history['json_salary_details']['dct_details']['Deductions'] = {}
                    for deduct_data in dct_data['Deductions']:
                        dct_history['json_salary_details']['dct_details']['Deductions'][deduct_data] = {'Value':dct_data['Deductions'][deduct_data], 'bln_change':False}
                UserHistory.objects.create(fk_user = ins_user, json_details = dct_history, int_type = 1, fk_created = request.user, fk_approved = request.user, dat_approved = datetime.now(), int_status = 1)
                # ================================================================================================================
                return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def get(self,request):
        try:
            """View User"""
            
            int_user_id = request.GET.get("id")
            if int_user_id:
                lst_user_details= list(UserDetails.objects.filter(user_ptr_id = int(int_user_id)).annotate(fk_desig__vchr_name = F('fk_group__vchr_name'),fk_desig_id= F('fk_group_id')).values('vchr_employee_code',
                                                                                                   'first_name','last_name',
                                                                                                   'username','bint_phone',
                                                                                                   'vchr_email','dat_doj',
                                                                                                   'dat_dob','vchr_gender',
                                                                                                   'fk_department__vchr_name',
                                                                                                   'fk_department_id',
                                                                                                   'fk_category__vchr_name',
                                                                                                   'fk_category_id',
                                                                                                   'fk_category__vchr_code',
                                                                                                   'fk_branch__vchr_name',
                                                                                                   'fk_branch_id',
                                                                                                   'fk_company__vchr_name',
                                                                                                   'fk_company_id','dat_created',
                                                                                                   'fk_salary_struct__vchr_name',
                                                                                                   'fk_salary_struct_id',
                                                                                                   'fk_desig_id','dbl_gross',
                                                                                                   'fk_desig__vchr_name','vchr_level',
                                                                                                   'vchr_grade','json_allowance',
                                                                                                   'vchr_middle_name','int_payment',
                                                                                                   'vchr_pan_no','vchr_aadhar_no',
                                                                                                   'vchr_img','vchr_bank_name',
                                                                                                   'vchr_acc_no','vchr_ifsc',
                                                                                                   'fk_brand_id','json_function','int_weekoff_type',
                                                                                                   'fk_brand__vchr_name',
                                                                                                   'vchr_file_no','json_physical_loc','vchr_address',
                                                                                                   'vchr_po','vchr_land_mark','vchr_place','int_pincode','fk_dist__vchr_name','fk_dist_id',
                                                                                                   'fk_dist__fk_state__vchr_name','fk_dist__fk_state_id',
                                                                                                   'fk_dist__fk_state__fk_country__vchr_name','fk_dist__fk_state__fk_country_id', 'vchr_pf_no',
                                                                                                   'vchr_esi_no','vchr_uan_no','vchr_wwf_no','vchr_weekoff_day','vchr_father_name','bint_emergency_phno',
                                                                                                   'is_active','dat_resignation','txt_resignation_reason',
                                                                                                   'vchr_salutation','fk_religion_id','fk_religion__vchr_name','vchr_marital_status','vchr_blood_group',
                                                                                                   'vchr_emergency_person','vchr_emergency_relation',
                                                                                                   'fk_wps__vchr_name','fk_wps_id','vchr_disease',
                                                                                                   'vchr_emp_remark', 'int_official_num', 'json_documents',
                                                                                        'fk_hierarchy_data__fk_hierarchy_id','fk_group_id','fk_hierarchy_data_id','fk_hierarchy_group_id'))
                dict_products =[]
                if lst_user_details[0].get('json_function'):
                    dict_products = Products.objects.filter(pk_bint_id__in = json.loads(lst_user_details[0].get('json_function'))).values("pk_bint_id","vchr_name")

                lst_ref_details= list(EmpReferences.objects.filter(fk_employee_id = int(int_user_id), int_status = 1).annotate(intRefId = F('pk_bint_id'),
                                                                                                            strRefName = F('vchr_name'),
                                                                                                            strCompName = F('vchr_company_name'),
                                                                                                            strRefDesig = F('vchr_desig'),
                                                                                                            intRefPhone = F('vchr_phone'),
                                                                                                            strRefEmail = F('vchr_email')).values('intRefId',
                                                                                                            'strRefName',
                                                                                                            'strCompName',
                                                                                                            'strRefDesig',
                                                                                                            'intRefPhone',
                                                                                                            'strRefEmail'))
                lst_family_details = list(EmpFamily.objects.filter(fk_employee_id = int(int_user_id), int_status = 1).annotate(intFamilyId = F('pk_bint_id'),
                                                                                                                strRelativeName = F('vchr_name'),
                                                                                                                strRelation = F('vchr_realation'),
                                                                                                                relativeDOB = F('dat_dob'),
                                                                                                                strOccupation = F('vchr_occupation'),
                                                                                                                isAlive = F('vchr_alive')).values('intFamilyId',
                                                                                                                'strRelativeName',
                                                                                                                'strRelation',
                                                                                                                'relativeDOB',
                                                                                                                'strOccupation',
                                                                                                                'isAlive'))

                lst_edu_details = list(EmpEduDetails.objects.filter(fk_employee_id = int(int_user_id),bln_active=True).annotate(intEduId = F('pk_bint_id'),
                                                                                                    blnHighest = F('bln_highest_qualif'),
                                                                                                    strQualif=F('vchr_qualif'),
                                                                                                    strCourse=F('vchr_course'),
                                                                                                    strInstituion=F('vchr_institution'),
                                                                                                    intYear=F('int_pass_year'),
                                                                                                    strUniversity = F('vchr_university'),
                                                                                                    strPlace = F('vchr_place'),
                                                                                                    fltPercentage = F('dbl_percentage'),
                                                                                                    strSpecialization = F('vchr_specialzation')).values('intEduId',
                                                                                                    'strCourse',
                                                                                                    'strInstituion',
                                                                                                    'intYear',
                                                                                                    'strUniversity',
                                                                                                    'blnHighest',
                                                                                                    'strPlace',
                                                                                                    'fltPercentage',
                                                                                                    'strQualif',
                                                                                                    'strSpecialization'))

                lst_exp_details = list(EmpExpDetails.objects.filter(fk_employee_id = int(int_user_id),bln_active=True).annotate(intExpId = F('pk_bint_id'),
                                                                                                                    strEmployer=F('vchr_employer'),
                                                                                                                    strDesig=F('vchr_designation'),
                                                                                                                    vchrExpDetails=F('txt_exp_details')).values('intExpId',
                                                                                                                    'strEmployer',
                                                                                                                    'strDesig',
                                                                                                                    'vchrExpDetails'))
                lst_phy_loc_id = lst_user_details[0]['json_physical_loc']
                # if lst_phy_loc_id :
                #     lst_phy_loc_name = PhysicalLocation.objects.filter(pk_bint_id__in  = lst_phy_loc_id).values_list('vchr_physical_loc',flat=True)
                #     lst_user_details[0].update({'lst_phy_loc_name':lst_phy_loc_name})

                ins_employee_shift = EmployeeShift.objects.filter(fk_employee_id = int(int_user_id),bln_active = True).values('json_shift','int_shift_type').first()

                if ins_employee_shift:
                    if ins_employee_shift.get('json_shift'):
                        lst_shift_id = ins_employee_shift['json_shift']['lstShift']

                        lst_shift_shedule = list(ShiftSchedule.objects.filter(pk_bint_id__in = lst_shift_id).annotate(vchr_shift_code = F('vchr_code'),
                                                                                                                  vchr_shift_name = F('vchr_name')).values('vchr_shift_code',
                                                                                                                                                             'bln_night','pk_bint_id',
                                                                                                                                                             'vchr_shift_name'))

                        int_shift_type = ins_employee_shift['int_shift_type']
                        lst_user_details[0].update({'lst_shift_shedule':lst_shift_shedule,'int_shift_type': int_shift_type})
                    else:
                        int_shift_type = ins_employee_shift['int_shift_type']
                        lst_user_details[0].update({'int_shift_type': int_shift_type})

                if SalaryDetails.objects.filter(fk_employee_id = int(int_user_id),int_status = 1):
                    dct_salary_details = SalaryDetails.objects.filter(fk_employee_id = int(int_user_id),int_status = 1).annotate(dbl_gross_amt = Case(When(Q(dbl_gross=None) | Q(dbl_gross=0), then=F('fk_employee__dbl_gross')),default=F('dbl_gross'),output_field=FloatField())).values().first()
                    dct_struct = {data['vchr_type']:{'ER':data['dbl_empr_share'], 'EE':data['dbl_empy_share']} for data in PfandEsiStructure.objects.filter(Q(int_end_month__isnull=True, int_end_year__isnull=True) | Q(int_end_month__gte=date.today().month, int_end_year__gte=date.today().year), int_start_month__lte=date.today().month, int_start_year__lte=date.today().year).values('vchr_type', 'dbl_empr_share', 'dbl_empy_share')}
                    dct_data = {}
                    dct_data['BP_DA'] = dct_salary_details['dbl_bp']
                    dct_data['DA'] = dct_salary_details['dbl_da']
                    dct_data['HRA'] = dct_salary_details['dbl_hra']
                    dct_data['CCA'] = dct_salary_details['dbl_cca']
                    dct_data['SA'] = dct_salary_details['dbl_sa']
                    dct_data['WA'] = dct_salary_details['dbl_wa']
                    dct_data['Deductions'] = dct_salary_details['json_deduction']
                    dct_data['Allowances'] = dct_salary_details['json_allowance']
                    if dct_struct.get('PF') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_hra',0)) < 15000 and lst_user_details[0].get('json_allowance').get('bln_pf'):
                        dct_data['Deductions']['PF'] = round((dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_hra',0)) * ((dct_struct.get('PF', {}).get('EE'))/100), 0)
                    elif dct_struct.get('PF') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_hra',0)) > 15000 and lst_user_details[0].get('json_allowance').get('bln_pf'):
                        dct_data['Deductions']['PF'] = round(15000 * ((dct_struct.get('PF', {}).get('EE'))/100), 0)

                    if dct_struct.get('PF') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_hra',0)) < 15000 and lst_user_details[0].get('json_allowance').get('bln_pf'):
                        dct_data['Allowances']['PF'] = round((dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_hra',0)) * ((dct_struct.get('PF', {}).get('ER'))/100), 0)
                    elif dct_struct.get('PF') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_hra',0)) > 15000 and lst_user_details[0].get('json_allowance').get('bln_pf'):
                        dct_data['Allowances']['PF'] = round(15000 * ((dct_struct.get('PF', {}).get('ER'))/100), 0)

                    if dct_struct.get('ESI') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_wa')) < 21000 and lst_user_details[0].get('json_allowance').get('bln_esi'):
                        dct_data['Deductions']['ESI'] = math.ceil((dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_wa')) * ((dct_struct.get('ESI', {}).get('EE'))/100))
                    elif dct_struct.get('ESI') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_wa')) > 21000 and lst_user_details[0].get('json_allowance').get('bln_esi'):
                        dct_data['Deductions']['ESI'] = 0

                    if dct_struct.get('ESI') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_wa')) < 21000 and lst_user_details[0].get('json_allowance').get('bln_esi'):
                        dct_data['Deductions']['ESI'] = math.ceil((dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_wa')) * ((dct_struct.get('ESI', {}).get('ER'))/100))
                    elif dct_struct.get('ESI') and (dct_salary_details.get('dbl_gross_amt',0) - dct_salary_details.get('dbl_wa')) > 21000 and lst_user_details[0].get('json_allowance').get('bln_esi'):
                        dct_data['Deductions']['ESI'] = 0

                    dct_data['VariablePay'] = 0
                    lst_user_details[0].update({'dct_salary_details':dct_data})
                    ins_amt = VariablePay.objects.filter(fk_employee_id = int(int_user_id),int_status = 1).values('dbl_amount')
                    if ins_amt:
                        dct_data['VariablePay'] = ins_amt[0]['dbl_amount']
                    dct_data['FixedAllowance'] = 0
                    ins_fixd_amt = FixedAllowance.objects.filter(fk_employee_id = int(int_user_id),int_status = 1).values('dbl_amount')
                    if ins_fixd_amt:
                        dct_data['FixedAllowance'] = ins_fixd_amt[0]['dbl_amount']

                return Response({'status':1,'lst_userdetailsview':lst_user_details,'lstRefDetails':lst_ref_details,'lstFamilyDetails':lst_family_details,'lstEduDetails':lst_edu_details,'lstExpDetails':lst_exp_details,'lstfunctions':dict_products})

            else:
                """List User"""
                bln_active =True
                if request.GET.get('intRes') == '1':
                    bln_active = False

                lst_user_details = list(UserDetails.objects.filter(is_active = bln_active).annotate(fk_desig__vchr_name=F('fk_group__vchr_name'),fullname=Concat('first_name', Value(' '),'vchr_middle_name', Value(' ') ,'last_name'), int_emp_id=Cast(Substr('vchr_employee_code',6), TextField())).extra(select ={'dat_doj' :"to_char(dat_doj,'DD-MM-YYYY')"}).values(
                                                                                         'int_emp_id',
                                                                                         'fullname','vchr_employee_code',
                                                                                         'first_name','last_name',
                                                                                         'username','bint_phone',
                                                                                         'vchr_email','dat_doj',
                                                                                         'dat_dob','vchr_gender',
                                                                                         'fk_department__vchr_name',
                                                                                         'fk_category__vchr_name',
                                                                                         'fk_branch__vchr_name',
                                                                                         'fk_brand__vchr_name',
                                                                                         'fk_company__vchr_name',
                                                                                         'fk_desig__vchr_name','vchr_level',
                                                                                         'vchr_grade','user_ptr_id').order_by('-int_emp_id'))
                return Response({'status':1,'lst_userdetailsview':lst_user_details})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            
            with transaction.atomic():
                """Update User """

                int_user_id = int(request.data.get("intId"))
                username = request.data.get('strUserName')
                bln_approve = True

                if UserDetails.objects.filter(username = username).exclude(user_ptr_id = int_user_id):
                    return Response({'status':0,'message':'Usercode already exists'})

                str_img_path = ""
                if type(request.data.get('imgSrc')) != str:
                    img_emp = request.data.get('imgSrc')
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT+'/UserProfilePics', base_url=settings.MEDIA_URL+'UserProfilePics/')
                    str_img = fs.save(username+datetime.now().strftime('-%Y%m%d%H%M%S%f.')+img_emp.name.split('.')[-1], img_emp)
                    str_img_path = fs.url(str_img)
                else:
                    str_img_path = request.data.get('imgSrc')

                lst_phy_loc = json.loads(request.data.get('lstLoc')) if request.data.get("lstLoc") else None
                int_salary_struct_id = int(request.data.get("intSalaryStructId")) if request.data.get("intSalaryStructId") else None
                dct_allowances = json.loads(request.data.get('dctAllowances'))
                dbl_gross = int(request.data.get("dblGrossPay")) if request.data.get("dblGrossPay") else None
                int_category_id = int(request.data.get("intCategoryId")) if request.data.get("intCategoryId") else None
                str_category_code = request.data.get('strCategoryCode')
                ins_user = UserDetails.objects.filter(user_ptr_id = int_user_id)
                dbl_cur_gross  = ins_user.values('dbl_gross')[0]['dbl_gross'] if ins_user.values('dbl_gross')[0] else None
                bln_changed = False
                if int_category_id != ins_user.first().fk_category_id :
                    str_cur_emp_code = ins_user.first().vchr_employee_code
                    str_new_code = str_cur_emp_code.replace(str_cur_emp_code[3],str_category_code)
                    bln_changed = True
                dct_data_salary = {}
                if int_salary_struct_id and dct_allowances and dbl_gross :
                    if request.data.get('strSalaryStructName') == 'Slab-0':
                        dct_data_salary = json.loads(request.data.get('dctSalarySplit'))
                        dct_data_salary['Deductions']['Charity'] = int(request.data.get('dblCharity')) if request.data.get('dblCharity') else 0
                        dct_data_salary['Deductions']['TDS'] = int(request.data.get('dblTds')) if request.data.get('dblTds') else 0
                    else:
                        dct_structure = SalaryStructure.objects.filter(pk_bint_id = int_salary_struct_id, bln_active=True).values('vchr_name', 'dbl_bp_da',
                                                                                                                              'dbl_bp_da_per', 'dbl_da',
                                                                                                                              'json_rules').first()
                        dct_structure['dblCharity'] = int(request.data.get('dblCharity')) if request.data.get('dblCharity') else 0
                        dct_structure['dblTds'] = int(request.data.get('dblTds')) if request.data.get('dblTds') else 0
                        dct_struct = {data['vchr_type']:{'Allowances':data['dbl_empr_share'], 'Deductions':data['dbl_empy_share']} for data in PfandEsiStructure.objects.filter(Q(int_end_month__isnull=True, int_end_year__isnull=True) | Q(int_end_month__gte=datetime.now().month, int_end_year__gte=datetime.now().year), int_start_month__lte=datetime.now().month, int_start_year__lte=datetime.now().year).values('vchr_type', 'dbl_empr_share', 'dbl_empy_share')}
                        if dct_structure.get('json_rules', {}).get('Allowances', {}).get('PF') != None and dct_struct.get('PF', {}).get('Allowances') != None:
                            dct_structure['json_rules']['Allowances']['PF'] = dct_struct['PF']['Allowances']
                        if dct_structure.get('json_rules', {}).get('Deductions', {}).get('PF') != None and dct_struct.get('PF', {}).get('Deductions') != None:
                            dct_structure['json_rules']['Deductions']['PF'] = dct_struct['PF']['Deductions']
                        dct_data_salary = GenerateSalaryProcess(dbl_gross, dct_structure, dct_allowances)

                # =============================================================================================================================================
                ins_user_details = UserDetails.objects.filter(user_ptr_id = int_user_id).first()
                dct_history = {}
                dct_history['vchr_employee_code'] = {'Value':str_new_code if bln_changed else ins_user_details.vchr_employee_code, 'bln_change':bln_changed}
                dct_history['username'] = {'Value':username if username else str_new_code if bln_changed else ins_user_details.username, 'bln_change':ins_user_details.username != username if username else str_new_code if bln_changed else ins_user_details.username}
                dct_history['vchr_salutation'] = {'Value':request.data.get('strSalutation'), 'bln_change':ins_user_details.vchr_salutation != request.data.get('strSalutation')}
                dct_history['first_name'] = {'Value':request.data.get('strFirstName'), 'bln_change':ins_user_details.first_name != request.data.get('strFirstName')}
                dct_history['middle_name'] = {'Value':request.data.get('strMiddleName'), 'bln_change':ins_user_details.vchr_middle_name != request.data.get('strMiddleName')}
                dct_history['last_name'] = {'Value':request.data.get('strLastName'), 'bln_change':ins_user_details.last_name != request.data.get('strLastName')}
                dct_history['email'] = {'Value':request.data.get('strEmail'), 'bln_change':ins_user_details.vchr_email != request.data.get('strEmail')}
                dct_history['dat_joined'] = {'Value':request.data.get('datJoin'), 'bln_change':(str(ins_user_details.dat_doj.date()) if ins_user_details.dat_doj else None) != request.data.get('datJoin')}
                dct_history['fk_category_id'] = {'Value':int_category_id, 'bln_change':ins_user_details.fk_category_id != int_category_id}
                dct_history['bint_phone'] = {'Value':request.data.get('intPhoneNumber'), 'bln_change':(str(ins_user_details.bint_phone) if ins_user_details.bint_phone else None) != request.data.get('intPhoneNumber')}
                dct_history['dat_dob'] = {'Value':request.data.get('datDob'), 'bln_change':str(ins_user_details.dat_dob) != request.data.get('datDob')}
                dct_history['vchr_gender'] = {'Value':request.data.get('strGender'), 'bln_change':ins_user_details.vchr_gender != request.data.get('strGender')}
                dct_history['vchr_level'] = {'Value':request.data.get('strGrade'), 'bln_change':ins_user_details.vchr_level != request.data.get('strGrade')}
                dct_history['vchr_grade'] = {'Value':request.data.get('strLevelofGrade'), 'bln_change':ins_user_details.vchr_grade != request.data.get('strLevelofGrade')}
                dct_history['fk_salary_struct_id'] = {'Value':int_salary_struct_id, 'bln_change':ins_user_details.fk_salary_struct_id != int_salary_struct_id}
                dct_history['fk_branch_id'] = {'Value':int(request.data.get("intBranchId")) if request.data.get("intBranchId") else None, 'bln_change':ins_user_details.fk_branch_id != int(request.data.get('intBranchId')) if request.data.get("intBranchId") else None}
                dct_history['fk_department_id'] = {'Value':int(request.data.get("intDptId")) if request.data.get("intDptId") else None, 'bln_change':ins_user_details.fk_department_id != int(request.data.get('intDptId')) if request.data.get("intDptId") else None}
                dct_history['fk_company_id'] = {'Value':ins_user_details.fk_company_id, 'bln_change':False}
                dct_history['dbl_gross'] = {'Value':dbl_gross, 'bln_change':ins_user_details.dbl_gross != dbl_gross}
                dct_history['fk_group_id'] = {'Value':int(request.data.get("intDesigId")) if request.data.get("intDesigId") else None, 'bln_change':ins_user_details.fk_desig_id != int(request.data.get('intDesigId')) if request.data.get("intDesigId") else None}
                dct_history['int_payment'] = {'Value':int(request.data.get("intPaymentMode")) if request.data.get("intPaymentMode") else None, 'bln_change':ins_user_details.int_payment != int(request.data.get('intPaymentMode')) if request.data.get("intPaymentMode") else None}
                dct_history['vchr_pan_no'] = {'Value':request.data.get("intPanNo"), 'bln_change':ins_user_details.vchr_pan_no != request.data.get('intPanNo')}
                dct_history['vchr_aadhar_no'] = {'Value':request.data.get("intAadharNo"), 'bln_change':ins_user_details.vchr_aadhar_no != request.data.get('intAadharNo')}
                dct_history['vchr_img'] = {'Value':str_img_path if str_img_path else ins_user_details.vchr_img, 'bln_change':ins_user_details.vchr_img != str_img_path if str_img_path else ins_user_details.vchr_img}
                dct_history['vchr_bank_name'] = {'Value':request.data.get("strBankName"), 'bln_change':ins_user_details.vchr_bank_name != request.data.get('strBankName')}
                dct_history['vchr_acc_no'] = {'Value':request.data.get("intAccountNum").zfill(16) if request.data.get("intAccountNum") else None, 'bln_change':ins_user_details.vchr_acc_no != request.data.get("intAccountNum").zfill(16) if request.data.get("intAccountNum") else None}
                dct_history['vchr_ifsc'] ={'Value': request.data.get('strIfscCode'), 'bln_change':ins_user_details.vchr_ifsc != request.data.get('strIfscCode')}
                dct_history['fk_brand_id'] = {'Value':int(request.data.get("intBrandId")) if request.data.get("intBrandId") else None, 'bln_change':ins_user_details.fk_brand_id != int(request.data.get('intBrandId')) if request.data.get("intBrandId") else False}
                dct_history['json_function'] = {'Value':(request.data.get("intProductId")) if request.data.get("intProductId") else None, 'bln_change':ins_user_details.json_function != (request.data.get('intProductId')) if request.data.get("intProductId") else False}
                dct_history['vchr_file_no'] = {'Value':request.data.get("strFileNo"), 'bln_change':ins_user_details.vchr_file_no != request.data.get('strFileNo')}
                dct_history['vchr_address'] = {'Value':request.data.get('strAddress'), 'bln_change':ins_user_details.vchr_address != request.data.get('strAddress')}
                dct_history['int_weekoff_type'] = {'Value':int(request.data.get("intWeekOffType")) if request.data.get("intWeekOffType") else None, 'bln_change':ins_user_details.int_weekoff_type != int(request.data.get("intWeekOffType")) if request.data.get("intWeekOffType") else None}
                dct_history['json_physical_loc'] = {'Value':lst_phy_loc, 'bln_change':ins_user_details.json_physical_loc != lst_phy_loc}
                dct_history['vchr_po'] = {'Value':request.data.get("strPo"), 'bln_change':ins_user_details.vchr_po != request.data.get('strPo')}
                dct_history['vchr_land_mark'] = {'Value':request.data.get('strLandMark'), 'bln_change':ins_user_details.vchr_land_mark != request.data.get('strLandMark')}
                dct_history['vchr_place'] = {'Value':request.data.get('strPlace'), 'bln_change':ins_user_details.vchr_place != request.data.get('strPlace')}
                dct_history['int_pincode'] = {'Value':request.data.get("intPincode") if request.data.get("intPincode") else None, 'bln_change':ins_user_details.int_pincode != int(request.data.get('intPincode')) if request.data.get("intPincode") else None}
                dct_history['fk_dist_id'] = {'Value':request.data.get("intDistId") if request.data.get("intDistId")  else None, 'bln_change':ins_user_details.fk_dist_id != int(request.data.get('intDistId')) if request.data.get("intDistId")  else None}
                dct_history['vchr_esi_no'] = {'Value':request.data.get('strEsiNo'), 'bln_change':ins_user_details.vchr_esi_no != request.data.get('strEsiNo')}
                dct_history['vchr_uan_no'] = {'Value':request.data.get('strUanNo'), 'bln_change':ins_user_details.vchr_uan_no != request.data.get('strUanNo')}
                dct_history['vchr_wwf_no'] = {'Value':request.data.get('strWwfNo'), 'bln_change':ins_user_details.vchr_wwf_no != request.data.get('strWwfNo')}
                dct_history['vchr_weekoff_day'] = {'Value':request.data.get('strDay'), 'bln_change':ins_user_details.vchr_weekoff_day != request.data.get('strDay')}
                dct_history['bint_emergency_phno'] = {'Value':request.data.get('intEmPhNo'), 'bln_change':ins_user_details.bint_emergency_phno != int(request.data.get('intEmPhNo') if request.data.get('intEmPhNo') else None)}
                dct_history['vchr_father_name'] = {'Value':request.data.get('strFatherName'), 'bln_change':ins_user_details.vchr_father_name != request.data.get('strFatherName')}
                dct_history['vchr_marital_status'] = {'Value':request.data.get('strMaritalStatus', None), 'bln_change':ins_user_details.vchr_marital_status != request.data.get('strMaritalStatus')}
                dct_history['vchr_blood_group'] = {'Value':request.data.get('strBloodGroup'), 'bln_change':ins_user_details.vchr_blood_group != request.data.get('strBloodGroup')}
                dct_history['vchr_emergency_person'] = {'Value':request.data.get('strEmerPerson'), 'bln_change':ins_user_details.vchr_emergency_person != request.data.get('strEmerPerson')}
                dct_history['vchr_emergency_relation'] = {'Value':request.data.get('strEmerRelation'), 'bln_change':ins_user_details.vchr_emergency_relation != request.data.get('strEmerRelation')}
                dct_history['fk_religion_id'] = {'Value':request.data.get('intReligionId', None), 'bln_change':ins_user_details.fk_religion_id != int(request.data.get('intReligionId')) if request.data.get('intReligionId') else False}
                dct_history['fk_wps_id'] = {'Value':request.data.get('intWpsId'), 'bln_change':ins_user_details.fk_wps_id != int(request.data.get('intWpsId')) if request.data.get('intWpsId') else False}
                dct_history['vchr_disease'] = {'Value':request.data.get('strIllnessDetails'), 'bln_change':ins_user_details.vchr_disease != request.data.get('strIllnessDetails')}
                dct_history['lst_reference'] = []
                for ref_data in json.loads(request.data.get('lstReference')):
                    if ref_data.get('strRefName') or ref_data.get('strCompName') or ref_data.get('strRefDesig') or ref_data.get('strRefEmail') or ref_data.get('intRefPhone'):
                        dct_ref = {}
                        ins_ref = None
                        if ref_data.get('intRefId'):
                            ins_ref = EmpReferences.objects.filter(pk_bint_id = int(ref_data.get('intRefId')), int_status = 1).first()
                        dct_ref['intRefId'] = {'Value':int(ref_data.get('intRefId')) if ref_data.get('intRefId') else None, 'bln_change':False if ref_data.get('intRefId') else True}
                        dct_ref['strRefName'] = {'Value':ref_data.get('strRefName'), 'bln_change': ins_ref.vchr_name != ref_data.get('strRefName') if ins_ref else True}
                        dct_ref['strCompName'] = {'Value':ref_data.get('strCompName'), 'bln_change': ins_ref.vchr_company_name != ref_data.get('strCompName') if ins_ref else True}
                        dct_ref['strRefDesig'] = {'Value':ref_data.get('strRefDesig'), 'bln_change':ins_ref.vchr_desig != ref_data.get('strRefDesig') if ins_ref else True}
                        dct_ref['strRefEmail'] = {'Value':ref_data.get('strRefEmail'), 'bln_change':ins_ref.vchr_email != ref_data.get('strRefEmail') if ins_ref else True}
                        dct_ref['intRefPhone'] = {'Value':ref_data.get('intRefPhone'), 'bln_change':ins_ref.vchr_phone != ref_data.get('intRefPhone') if ins_ref else True}
                        dct_history['lst_reference'].append(dct_ref)
                dct_history['lst_family_details'] = []
                if json.loads(request.data.get("lstDeletedFamily")):
                    dct_history['lst_deleted_famly'] = json.loads(request.data.get("lstDeletedFamily"))
                for fam_data in json.loads(request.data.get("lstFamilyDetails")):
                    if fam_data.get('strRelativeName') or fam_data.get('strRelation') or fam_data.get('relativeDOB') or fam_data.get('strOccupation') or fam_data.get('isAlive'):
                        dct_fan = {}
                        ins_famly = None
                        if fam_data.get('intFamilyId'):
                            ins_famly = EmpFamily.objects.filter(pk_bint_id=fam_data['intFamilyId'], int_status=1).first()
                        dct_fan['intFamilyId'] = {'Value':fam_data.get('intFamilyId') if fam_data.get('intFamilyId') else None, 'bln_change':False if fam_data.get('intFamilyId') else True}
                        dct_fan['strRelativeName'] = {'Value':fam_data.get('strRelativeName'), 'bln_change':ins_famly.vchr_name != fam_data.get('strRelativeName') if ins_famly else True}
                        dct_fan['strRelation'] = {'Value':fam_data.get('strRelation'), 'bln_change':ins_famly.vchr_realation != fam_data.get('strRelation') if ins_famly else True}
                        dct_fan['relativeDOB'] = {'Value':fam_data.get('relativeDOB'), 'bln_change':ins_famly.dat_dob != fam_data.get('relativeDOB') if ins_famly else True}
                        dct_fan['strOccupation'] = {'Value':fam_data.get('strOccupation'), 'bln_change':ins_famly.vchr_occupation != fam_data.get('strOccupation') if ins_famly else True}
                        dct_fan['isAlive'] = {'Value':fam_data.get('isAlive'), 'bln_change':ins_famly.vchr_alive != fam_data.get('isAlive') if ins_famly else True}
                        dct_history['lst_family_details'].append(dct_fan)
                dct_history['lst_edu_details'] = []
                if json.loads(request.data.get("lstDeletedEductn")):
                    dct_history['lst_deleted_eductn'] = json.loads(request.data.get("lstDeletedEductn"))
                for edu_data in json.loads(request.data.get("lstEduDetails")):
                    if edu_data.get('blnHighest') or edu_data.get('strQualif') or edu_data.get('strCourse') or edu_data.get('strInstituion') or edu_data.get('intYear') or edu_data.get('strUniversity') or edu_data.get('strPlace') or edu_data.get('fltPercentage') or edu_data.get('strSpecialization'):
                        dct_edu = {}
                        ins_edu = None
                        if edu_data.get('intEduId'):
                            ins_edu = EmpEduDetails.objects.filter(pk_bint_id = edu_data.get('intEduId'), bln_active = True).first()
                        dct_edu['intEduId'] = {'Value':edu_data.get('intEduId') if edu_data.get('intEduId') else None, 'bln_change':False if edu_data.get('intEduId') else True}
                        dct_edu['blnHighest'] = {'Value':edu_data.get('blnHighest'), 'bln_change':ins_edu.bln_highest_qualif != edu_data.get('blnHighest') if ins_edu else True}
                        dct_edu['strQualif'] = {'Value':edu_data.get('strQualif'), 'bln_change':ins_edu.vchr_qualif != edu_data.get('strQualif') if ins_edu else True}
                        dct_edu['strCourse'] = {'Value':edu_data.get('strCourse'), 'bln_change':ins_edu.vchr_course != edu_data.get('strCourse') if ins_edu else True}
                        dct_edu['strInstituion'] = {'Value':edu_data.get('strInstituion'), 'bln_change':ins_edu.vchr_institution != edu_data.get('strInstituion') if ins_edu else True}
                        dct_edu['intYear'] = {'Value':edu_data.get('intYear'), 'bln_change':ins_edu.int_pass_year != edu_data.get('intYear') if ins_edu else True}
                        dct_edu['strUniversity'] = {'Value':edu_data.get('strUniversity'), 'bln_change':ins_edu.vchr_university != edu_data.get('strUniversity') if ins_edu else True}
                        dct_edu['strPlace'] = {'Value':edu_data.get('strPlace'), 'bln_change':ins_edu.vchr_place != edu_data.get('strPlace') if ins_edu else True}
                        dct_edu['fltPercentage'] = {'Value':edu_data.get('fltPercentage'), 'bln_change':ins_edu.dbl_percentage != edu_data.get('fltPercentage') if ins_edu else True}
                        dct_edu['strSpecialization'] = {'Value':edu_data.get('strSpecialization'), 'bln_change':ins_edu.vchr_specialzation != edu_data.get('strSpecialization') if ins_edu else True}
                        dct_history['lst_edu_details'].append(dct_edu)
                dct_history['lst_exp_details'] = []
                if json.loads(request.data.get("lstDeletedExp")):
                    dct_history['lst_deleted_exprnc'] = json.loads(request.data.get("lstDeletedExp"))
                for exp_data in json.loads(request.data.get("lstExpDetails")):
                    if exp_data.get('strEmployer') or exp_data.get('vchrExpDetails') or exp_data.get('strDesig'):
                        dct_exp = {}
                        ins_exp = None
                        if exp_data.get('intExpId'):
                            ins_exp = EmpExpDetails.objects.filter(pk_bint_id = exp_data.get('intExpId'), bln_active = True).first()
                        dct_exp['intExpId'] = {'Value':exp_data.get('intExpId') if exp_data.get('intExpId') else None, 'bln_change':False if exp_data.get('intExpId') else True}
                        dct_exp['strEmployer'] = {'Value':exp_data.get('strEmployer'), 'bln_change':ins_exp.vchr_employer != exp_data.get('strEmployer') if ins_exp else True}
                        dct_exp['vchrExpDetails'] = {'Value':exp_data.get('vchrExpDetails'), 'bln_change':ins_exp.vchr_designation != exp_data.get('vchrExpDetails') if ins_exp else True}
                        dct_exp['strDesig'] = {'Value':exp_data.get('strDesig'), 'bln_change':ins_exp.txt_exp_details != exp_data.get('strDesig') if ins_exp else True}
                        dct_history['lst_exp_details'].append(dct_exp)
                ins_eshift = EmployeeShift.objects.filter(fk_employee_id = int_user_id, bln_active = True).first()
                dct_history['json_shift'] = {}
                dct_history['json_shift']['int_shift_type'] = {'Value':int(request.data.get("intShiftType")), 'bln_change':ins_eshift.int_shift_type != (int(request.data.get("intShiftType")) if request.data.get("intShiftType") else None) if ins_eshift else True}
                dct_history['json_shift']['dct_shift'] = {'Value':json.loads(request.data.get("jsonShiftId")), 'bln_change':ins_eshift.json_shift != json.loads(request.data.get("jsonShiftId")) if ins_eshift else True}
                dct_history['json_salary_details'] = {}
                dct_history['json_salary_details']['salary_struct_name'] =  {'Value':request.data.get('strSalaryStructName'), 'bln_change':ins_user_details.fk_salary_struct_id != int_salary_struct_id}
                dct_history['json_salary_details']['salary_struct_id'] = {'Value':int_salary_struct_id, 'bln_change':ins_user_details.fk_salary_struct_id != int_salary_struct_id}
                dct_history['json_salary_details']['dct_allowances_rules'] = {}
                for allw_data in dct_allowances:
                    dct_history['json_salary_details']['dct_allowances_rules'][allw_data] = {'Value':dct_allowances[allw_data], 'bln_change':dct_allowances[allw_data] != (ins_user_details.json_allowance.get(allw_data) if ins_user_details.json_allowance else False)}
                dct_history['json_salary_details']['dct_details'] = {}
                if dct_data_salary:
                    ins_sal_detals = SalaryDetails.objects.filter(fk_employee_id = int_user_id,int_status = 1).first()
                    dct_history['json_salary_details']['dct_details']['BP_DA'] = {'Value':dct_data_salary['BP_DA'], 'bln_change':dct_data_salary['BP_DA'] != ins_sal_detals.dbl_bp if ins_sal_detals else True}
                    dct_history['json_salary_details']['dct_details']['HRA'] = {'Value':dct_data_salary['HRA'], 'bln_change':dct_data_salary['HRA'] != ins_sal_detals.dbl_hra if ins_sal_detals else True}
                    dct_history['json_salary_details']['dct_details']['CCA'] = {'Value':dct_data_salary['CCA'], 'bln_change':dct_data_salary['CCA'] != ins_sal_detals.dbl_cca if ins_sal_detals else True}
                    dct_history['json_salary_details']['dct_details']['WA'] = {'Value':dct_data_salary['WA'], 'bln_change':dct_data_salary['WA'] != ins_sal_detals.dbl_wa if ins_sal_detals else True}
                    dct_history['json_salary_details']['dct_details']['SA'] = {'Value':dct_data_salary['SA'], 'bln_change':dct_data_salary['SA'] != ins_sal_detals.dbl_sa if ins_sal_detals else True}
                    dct_history['json_salary_details']['dct_details']['Allowances'] = {}
                    for allw_data in dct_data_salary['Allowances']:
                        dct_history['json_salary_details']['dct_details']['Allowances'][allw_data] = {'Value':dct_data_salary['Allowances'][allw_data], 'bln_change':dct_data_salary['Allowances'][allw_data] != ins_sal_detals.json_allowance.get(allw_data, 0) if ins_sal_detals else True}
                    dct_history['json_salary_details']['dct_details']['Deductions'] = {}
                    for deduct_data in dct_data_salary['Deductions']:
                        dct_history['json_salary_details']['dct_details']['Deductions'][deduct_data] = {'Value':dct_data_salary['Deductions'][deduct_data], 'bln_change':dct_data_salary['Deductions'][deduct_data] != ins_sal_detals.json_deduction.get(deduct_data, 0) if ins_sal_detals else True}
                ins_history = UserHistory.objects.filter(fk_user_id = ins_user_details.user_ptr_id, int_type = 2, bln_changed = True, int_status = 0)
                if not ins_history:
                    if UserHistory.objects.filter(fk_user_id = ins_user_details.user_ptr_id, json_details = dct_history):
                        UserHistory.objects.create(fk_user = ins_user_details, json_details = dct_history, int_type = 2, bln_changed = False, fk_created = request.user, int_status = 0)
                    else:
                        UserHistory.objects.create(fk_user = ins_user_details, json_details = dct_history, int_type = 2, bln_changed = True, fk_created = request.user, int_status = 0)
                else:
                    if bln_approve:
                        if UserHistory.objects.filter(fk_user_id = ins_user_details.user_ptr_id, json_details = dct_history):
                            UserHistory.objects.create(fk_user = ins_user_details, json_details = dct_history, int_type = 2, bln_changed = False, fk_created = request.user, int_status = 1, fk_approved = request.user, dat_approved = datetime.now())
                        else:
                            UserHistory.objects.create(fk_user = ins_user_details, json_details = dct_history, int_type = 2, bln_changed = True, fk_created = request.user, int_status = 1, fk_approved = request.user, dat_approved = datetime.now())
                    else:
                        return Response({'status':0,'message':'Pending Approval'})
                # =============================================================================================================================================

                # ===================================================== Employee ==============================================================================
                if bln_approve:
                    ins_user.update(username = str_new_code if bln_changed else ins_user.first().username,
                                    vchr_employee_code = str_new_code if bln_changed else ins_user.first().vchr_employee_code,
                                    vchr_salutation = request.data.get('strSalutation',None),
                                    first_name = request.data.get("strFirstName"),
                                    last_name = request.data.get("strLastName"),
                                    bint_phone = request.data.get("intPhoneNumber"),
                                    email = request.data.get("strEmail"),
                                    vchr_email = request.data.get("strEmail"),
                                    dat_doj = request.data.get("datJoin"),
                                    dat_dob = request.data.get("datDob"),
                                    vchr_gender = request.data.get("strGender"),
                                    vchr_marital_status = request.data.get('strMaritalStatus',None),
                                    vchr_blood_group = request.data.get('strBloodGroup',None),
                                    fk_department_id = int(request.data.get("intDptId")) if request.data.get("intDptId") else None,
                                    fk_category_id = int_category_id,
                                    fk_branch_id = int(request.data.get("intBranchId")) if request.data.get("intBranchId") else None,
                                    dat_created = datetime.now(),
                                    fk_created_id = request.user.id,
                                    fk_salary_struct_id = int_salary_struct_id,
                                    fk_group_id = int(request.data.get("intDesigId")) if request.data.get("intDesigId") else None,
                                    vchr_level = request.data.get("strGrade"),
                                    vchr_grade = request.data.get("strLevelofGrade"),
                                    json_allowance =  dct_allowances,
                                    dbl_gross = dbl_gross,
                                    vchr_middle_name = request.data.get("strMiddleName"),
                                    int_payment = int(request.data.get("intPaymentMode")) if request.data.get("intPaymentMode") else None,
                                    vchr_pan_no = request.data.get("intPanNo"),
                                    vchr_aadhar_no = request.data.get("intAadharNo"),
                                    vchr_img = str_img_path or "",
                                    vchr_bank_name = request.data.get("strBankName"),
                                    vchr_acc_no = request.data.get("intAccountNum").zfill(16) if request.data.get("intAccountNum") else None,
                                    vchr_ifsc = request.data.get("strIfscCode"),
                                    fk_brand_id = int(request.data.get("intBrandId")) if request.data.get("intBrandId") else None,
                                    json_function = request.data.get("intProductId") if request.data.get("intProductId") else None,
                                    vchr_file_no = request.data.get("strFileNo"),
                                    vchr_address = request.data.get("strAddress"),
                                    json_physical_loc = lst_phy_loc,
                                    int_weekoff_type = int(request.data.get("intWeekOffType")) if request.data.get("intWeekOffType") else None,
                                    vchr_po = request.data.get("strPo"),
                                    vchr_land_mark = request.data.get("strLandMark"),
                                    vchr_place = request.data.get("strPlace"),
                                    fk_dist_id = request.data.get("intDistId") if request.data.get("intDistId")  else None,
                                    int_pincode =  request.data.get("intPincode")  if request.data.get("intPincode") else None,
                                    vchr_pf_no = request.data.get('strPfNo'),
                                    vchr_esi_no = request.data.get('strEsiNo'),
                                    vchr_uan_no = request.data.get('strUanNo'),
                                    vchr_wwf_no = request.data.get('strWwfNo'),
                                    vchr_weekoff_day  =request.data.get('strDay'),
                                    vchr_father_name= request.data.get('strFatherName'),
                                    vchr_emergency_person = request.data.get('strEmerPerson',None),
                                    vchr_emergency_relation = request.data.get('strEmerRelation',None),
                                    bint_emergency_phno= request.data.get('intEmPhNo'),
                                    fk_religion_id = int(request.data.get('intReligionId',None)),
                                    fk_wps_id = request.data.get('intWpsId') if request.data.get('intWpsId') and request.data.get('intWpsId')!='null' else None,
                                    vchr_disease = request.data.get('strIllnessDetails'),
                                    vchr_emp_remark = request.data.get('strEmpRemarks'),
                                    int_official_num = request.data.get('intOfficialNumber'))
                    # ====================================================================================================

                    # ========================================== Reference ===============================================
                    lst_ref = json.loads(request.data.get('lstReference'))
                    lst_ins_ref = []
                    for data in lst_ref:
                        if not data.get('intRefId'):
                            if data.get('strRefName') or data.get('strRefDesig') or data.get('intRefPhone') or data.get('strRefEmail'):
                                ins_ref = EmpReferences(fk_employee_id = int_user_id,
                                                        vchr_name = data.get('strRefName'),
                                                        vchr_company_name = data.get('strCompName'),
                                                        vchr_desig = data.get('strRefDesig'),
                                                        vchr_phone = data.get('intRefPhone'),
                                                        vchr_email = data.get('strRefEmail'),
                                                        int_status = 1)
                                lst_ins_ref.append(ins_ref)
                        else:
                            EmpReferences.objects.filter(pk_bint_id = data.get('intRefId')).update(vchr_name = data.get('strRefName'),
                                                    vchr_company_name = data.get('strCompName'),
                                                    vchr_desig = data.get('strRefDesig') ,
                                                    vchr_phone = data.get('intRefPhone'),
                                                    vchr_email = data.get('strRefEmail'))
                    EmpReferences.objects.bulk_create(lst_ins_ref)
                    # ======================================================================================================

                    # ========================================== Family Details ============================================
                    lst_del_family = json.loads(request.data.get("lstDeletedFamily")) if request.data.get("lstDeletedFamily") else {}
                    if lst_del_family:
                        EmpFamily.objects.filter(pk_bint_id__in=lst_del_family).update(int_status = -1)
                    lst_family_details = json.loads(request.data.get("lstFamilyDetails")) if request.data.get("lstFamilyDetails") else {}
                    lst_ins_family = []
                    for data in lst_family_details:
                        if not data.get('intFamilyId'):
                            if data.get('strRelation') or data.get('strRelativeName') or data.get('strOccupation') or data.get('isAlive') or data.get('relativeDOB'):
                                ins_fmly= EmpFamily(fk_employee_id = int_user_id,
                                                vchr_name = data.get('strRelativeName'),
                                                vchr_realation = data.get('strRelation'),
                                                dat_dob = data.get('relativeDOB'),
                                                vchr_occupation = data.get('strOccupation'),
                                                vchr_alive = data.get('isAlive'),
                                                int_status = 1)
                                lst_ins_family.append(ins_fmly)
                        else:
                            EmpFamily.objects.filter(pk_bint_id = data.get('intFamilyId')).update(vchr_name = data.get('strRelativeName'),
                                                        vchr_realation = data.get('strRelation'),
                                                        dat_dob = data.get('relativeDOB'),
                                                        vchr_occupation = data.get('strOccupation'),
                                                        vchr_alive = data.get('isAlive'),
                                                        int_status = 1)

                    EmpFamily.objects.bulk_create(lst_ins_family)
                    # ========================================================================================================

                    # ========================================= Education Details ============================================
                    lst_del_edu_details = json.loads(request.data.get("lstDeletedEductn")) if request.data.get("lstDeletedEductn") else []
                    if lst_del_edu_details:
                        ins_applicant_edu_details = EmpEduDetails.objects.filter(pk_bint_id__in=lst_del_edu_details).update(bln_active = False)
                    lst_edu_detail =  json.loads(request.data.get("lstEduDetails")) if request.data.get("lstEduDetails") else {}
                    if lst_edu_detail:
                        lst_ins_edu = []
                        for dct_data in lst_edu_detail:
                            if dct_data.get('intYear') or dct_data.get('strInstituion') or dct_data.get('strCourse') or dct_data.get('strUniversity') or dct_data.get('blnHighest') or dct_data.get('strQualif'):
                                if not dct_data.get('intEduId'):
                                    ins_edu = EmpEduDetails(fk_employee_id = int_user_id,
                                                          vchr_qualif = dct_data.get('strQualif'),
                                                          vchr_course = dct_data.get('strCourse'),
                                                          bln_highest_qualif = dct_data.get('blnHighest'),
                                                          vchr_institution = dct_data.get('strInstituion'),
                                                          int_pass_year = int(dct_data.get('intYear')) if dct_data.get('intYear') else None,
                                                          vchr_university = dct_data.get('strUniversity'),
                                                          vchr_place = dct_data.get('strPlace'),
                                                          dbl_percentage = dct_data.get('fltPercentage'),
                                                          vchr_specialzation = dct_data.get('strSpecialization'),
                                                          bln_active = True)
                                    lst_ins_edu.append(ins_edu)
                                else:
                                    EmpEduDetails.objects.filter(pk_bint_id=dct_data.get('intEduId')).update(vchr_course = dct_data.get('strCourse'),
                                                          bln_highest_qualif = dct_data.get('blnHighest'),
                                                          vchr_qualif = dct_data.get('strQualif'),
                                                          vchr_institution = dct_data.get('strInstituion'),
                                                          int_pass_year = int(dct_data.get('intYear')) if dct_data.get('intYear') else None,
                                                          vchr_university = dct_data.get('strUniversity'),
                                                          vchr_place = dct_data.get('strPlace'),
                                                          dbl_percentage = dct_data.get('fltPercentage'),
                                                          bln_active = True,
                                                          vchr_specialzation = dct_data.get('strSpecialization'))
                        EmpEduDetails.objects.bulk_create(lst_ins_edu)
                    # ===========================================================================================================

                    # ====================================== Experiance Details =================================================
                    lst_del_exp_details = json.loads(request.data.get("lstDeletedExp")) if request.data.get("lstDeletedExp") else []
                    if lst_del_exp_details:
                        ins_applicant_exp_details = EmpExpDetails.objects.filter(pk_bint_id__in=lst_del_exp_details).update(bln_active=False)
                    lst_exp_detail =  json.loads(request.data.get("lstExpDetails")) if request.data.get("lstExpDetails") else {}
                    if lst_exp_detail:
                        lst_ins_exp = []
                        for dct_data in lst_exp_detail:
                            if dct_data.get('strEmployer') or dct_data.get('vchrExpDetails') or dct_data.get('strDesig'):
                                if not dct_data.get('intExpId'):
                                    ins_exp = EmpExpDetails(fk_employee_id =  int_user_id,
                                                                  vchr_employer = dct_data.get('strEmployer'),
                                                                  vchr_designation = dct_data.get('strDesig'),
                                                                  txt_exp_details = dct_data.get('vchrExpDetails'),
                                                                  bln_active = True)
                                    lst_ins_exp.append(ins_exp)
                                else:
                                    EmpExpDetails.objects.filter(pk_bint_id=dct_data.get('intExpId')).update(vchr_employer = dct_data.get('strEmployer'),
                                                                  vchr_designation = dct_data.get('strDesig'),
                                                                  txt_exp_details = dct_data.get('vchrExpDetails'),
                                                                  bln_active = True)
                        EmpExpDetails.objects.bulk_create(lst_ins_exp)
                    # ============================================================================================================

                    # ============================================ Employee Shift ================================================
                    ins_employee_shift = EmployeeShift.objects.filter(fk_employee_id = int_user_id,bln_active = True).values('int_shift_type','json_shift').first()
                    if ins_employee_shift:
                        if request.data.get('intShiftType') or json.loads(request.data.get('jsonShiftId')):
                            if ins_employee_shift['int_shift_type'] != int(request.data.get('intShiftType')) or ins_employee_shift['json_shift'] != json.loads(request.data.get('jsonShiftId')):
                                #if shift is changed  old shift data will be disabled  and new employee_shift data will be created
                                EmployeeShift.objects.filter(fk_employee_id = int_user_id,bln_active = True).update(bln_active = False,
                                                                                                                  dat_updated = datetime.now(),
                                                                                                                  fk_updated_id = request.user.id)
                                EmployeeShift.objects.create(fk_employee_id = int_user_id,
                                                             int_shift_type = int(request.data.get("intShiftType")),
                                                             json_shift = json.loads(request.data.get("jsonShiftId")),
                                                             bln_active = True,
                                                             dat_created = datetime.now(),
                                                             fk_created_id = request.user.id)
                    else:
                        if request.data.get('intShiftType') or json.loads(request.data.get('jsonShiftId')):
                            EmployeeShift.objects.create(fk_employee_id = int_user_id,
                                                         int_shift_type = int(request.data.get("intShiftType")),
                                                         json_shift = json.loads(request.data.get("jsonShiftId")),
                                                         bln_active = True,
                                                         dat_created = datetime.now(),
                                                         fk_created_id = request.user.id)
                    # =============================================================================================================

                    # ============================================ Salary Details =================================================
                    if dct_data_salary:
                        SalaryDetails.objects.filter(fk_employee_id = int_user_id,int_status = 1).update(int_status= 0, fk_updated_id=request.user.id, dat_updated=datetime.now())
                        ins_data = SalaryDetails.objects.create(fk_employee_id = int_user_id,
                                                     dbl_bp = dct_data_salary.get('BP_DA'),
                                                     dbl_da = dct_data_salary.get('DA', 0),
                                                     dbl_hra = dct_data_salary.get('HRA'),
                                                     dbl_cca = dct_data_salary.get('CCA'),
                                                     dbl_sa = dct_data_salary.get('SA'),
                                                     dbl_wa = dct_data_salary.get('WA'),
                                                     dbl_gross = dbl_gross,
                                                     json_deduction = dct_data_salary.get('Deductions'),
                                                     json_allowance = dct_data_salary.get('Allowances'),
                                                     fk_created_id = request.user.id,
                                                     int_status = 1)
                    # =============================================================================================================
                return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def patch(self,request):
        try:
            """Delete user"""
            int_user_id = request.data.get("intId")
            dat_resignation = request.data.get('datResignation', None)
            txt_reason = request.data.get('txtReason', None)
            UserDetails.objects.filter(user_ptr_id = int_user_id).update(is_active = False, fk_updated = request.user, dat_updated = datetime.now(), dat_resignation = dat_resignation, txt_resignation_reason = txt_reason)
            if not request.data.get('blnReflectGap'):
                ins_user = UserDetails.objects.get(user_ptr_id = int_user_id)
                int_branch_id = ins_user.fk_branch_id
                int_desig_id = ins_user.fk_desig_id
                int_department_id = ins_user.fk_department_id
                ins_desig_allocation = BranchDesigAlloc.objects.filter(fk_branch_id=int_branch_id,fk_desig_id=int_desig_id).first()
                if ins_desig_allocation:
                    if ins_desig_allocation.json_brand:
                        int_brand_id=ins_user.fk_brand_id
                        json_brand = ins_desig_allocation.json_brand
                        if str(int_brand_id) in json_brand.keys():
                            if (json_brand[str(int_brand_id)]-1) == 0:
                                json_brand.pop(str(int_brand_id))
                            else:
                                json_brand[str(int_brand_id)] = json_brand[str(int_brand_id)]-1
                            ins_desig_allocation.json_brand = json_brand
                            ins_desig_allocation.int_count = ins_desig_allocation.int_count-1
                            if not json_brand:
                                ins_desig_allocation.int_status = 0
                            ins_desig_allocation.save()
                    else:
                        ins_desig_allocation.int_count=(ins_desig_allocation.int_count-1)
                        if ins_desig_allocation.int_count == 0:
                            ins_desig_allocation.int_status = 0
                        ins_desig_allocation.save()
                else:
                    ins_desig_allocation = BranchDesigAlloc.objects.filter(fk_dept_id=int_department_id,fk_desig_id=int_desig_id).first()
                    if ins_desig_allocation:
                        ins_desig_allocation.int_count=(ins_desig_allocation.int_count-1)
                        if ins_desig_allocation.int_count == 0:
                            ins_desig_allocation.int_status = 0
                        ins_desig_allocation.save()

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})



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
            # 
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
            # 
            str_username= request.data['_UserId']
            str_password=request.data['_Password']
            user = authenticate(request, username=str_username, password=str_password)
            if user:
                if user.is_staff:
                    login(request, user)
                    # if settings.DEBUG:
                    #     token_json = requests.post(request.scheme+'://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                    # else:
                    #     token_json = requests.post(request.scheme+'://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                    token_json = requests.post(request.scheme+'://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                    token = json.loads(token_json._content.decode("utf-8"))['token']
                    str_name = 'Super User'
                    email = user.email or ''
                    userdetails={'Name':str_name,'email':email}
                    SessionHandler.objects.filter(fk_user_id = user.id).delete()
                    SessionHandler.objects.create(vchr_session_key = request.session.session_key,fk_user_id = user.id)

                    lst_menu_data=[]
                    dct_insert = {'NAME':'',
                        'ADD': False,
                        'VIEW': False,
                        'EDIT': False,
                        'DELETE': False
                        }

                    rst_menu_group = MenuCategory.objects.values('pk_bint_id','vchr_menu_category_name','fk_sub_category__vchr_sub_category_name').order_by('fk_sub_category_id','int_menu_category_order')
                    for dct_data in rst_menu_group:
                        dct_insert = {}
                        dct_insert['NAME'] = dct_data['vchr_menu_category_name']
                        dct_insert['ADD'] = True
                        dct_insert['EDIT'] = True
                        dct_insert['VIEW'] = True
                        dct_insert['SUBCATEGORY'] = dct_data['fk_sub_category__vchr_sub_category_name']
                        dct_insert['DELETE'] = True
                        lst_menu_data.append(dct_insert)

                    return Response({'status':1,'token':token,'userdetails':userdetails,"str_session_key":request.session.session_key,'lst_menu_data':lst_menu_data})
                else:
                    login(request,user)
                    token_json = requests.post(request.scheme+'://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
                    token = json.loads(token_json._content.decode("utf-8"))['token']
                    email = user.email or ''
                    if request.user.userdetails.bln_pass_reset:
                        UserDetails.objects.filter(user_ptr_id=request.user.id).update(bln_pass_reset=False)
                    rst_user = UserDetails.objects.filter(user_ptr_id=request.user.id).values('user_ptr_id','first_name','last_name','vchr_middle_name','fk_branch_id','fk_branch_id__vchr_name','fk_company_id','fk_department_id','fk_department_id__vchr_name','fk_desig_id','fk_desig__vchr_name','vchr_img','fk_group__vchr_name','fk_branch__int_type')

                    str_name = rst_user[0]['first_name'] +" "+rst_user[0]['last_name']

                    if rst_user[0]['vchr_middle_name']:
                        str_name = rst_user[0]['first_name'] +" "+rst_user[0]['vchr_middle_name']+" "+rst_user[0]['last_name']

                    branch_id = rst_user[0]['fk_branch_id']
                    branch_name = rst_user[0]['fk_branch_id__vchr_name']
                    company_id=rst_user[0]['fk_company_id']
                    str_department = rst_user[0]['fk_department_id__vchr_name']
                    int_department = rst_user[0]['fk_department_id']
                    str_designation = rst_user[0]['fk_desig__vchr_name']
                    int_designation = rst_user[0]['fk_desig_id']
                    group_name = rst_user[0]['fk_group__vchr_name']
                    branch_type = rst_user[0]['fk_branch__int_type']
                    str_img = None
                    if path.exists(settings.MEDIA_ROOT.rstrip('/media')+rst_user[0]['vchr_img']):
                        str_img = request.scheme+'://'+request.get_host()+rst_user[0]['vchr_img']
                    userdetails={'Name':str_name.title(),'int_user_id':rst_user[0]['user_ptr_id'],'email':email,'branch_id':branch_id,'branch_name':branch_name,'company_id':company_id,'str_department':str_department,'int_department':int_department,'str_designation':str_designation,'int_designation':int_designation, 'str_user_img':str_img,'group_name':group_name,'bln_indirect_discount':"",'bln_direct_discount':"",'branch_type':branch_type}
                    SessionHandler.objects.filter(fk_user_id = user.id).delete()
                    SessionHandler.objects.create(vchr_session_key = request.session.session_key,fk_user_id = user.id)

                    lst_menu_data=[]
                    dct_insert = {'NAME':'',
                        'ADD': False,
                        'VIEW': False,
                        'EDIT': False,
                        'DELETE': False
                        }
                    int_desig_id = request.user.userdetails.fk_group_id
                    if int_desig_id:
                        rst_menu_group = GroupPermissions.objects.filter( fk_groups_id = int_desig_id).values('pk_bint_id','fk_category_items__fk_menu_category__vchr_menu_category_name','fk_category_items__fk_sub_category__vchr_sub_category_name','bln_add','bln_edit','bln_view','bln_delete').order_by('fk_category_items__fk_menu_category__int_menu_category_order')
                        for dct_data in rst_menu_group:
                            dct_insert = {}
                            dct_insert['NAME'] = dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name']
                            dct_insert['ADD'] = dct_data['bln_add']
                            dct_insert['EDIT'] = dct_data['bln_edit']
                            dct_insert['VIEW'] = dct_data['bln_view']
                            dct_insert['DELETE'] = dct_data['bln_delete']
                            dct_insert['SUBCATEGORY'] = dct_data['fk_category_items__fk_sub_category__vchr_sub_category_name']
                            lst_menu_data.append(dct_insert)

                    return Response({'status':1,'token':token,'userdetails':userdetails,"str_session_key":request.session.session_key,'lst_menu_data':lst_menu_data})
            else:
                return Response({'status':0,'reason':'No user'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})



# class loginCheck(APIView):
    # permission_classes=[AllowAny]
    # def post(self,request):
    #     try :
    #         # 
    #         str_username= request.data['_UserId']
    #         str_password=request.data['_Password']
    #         # if(Userdetails.objects.filter(username=str_username)):
    #         #
    #         user = authenticate(request, username=str_username, password=str_password)


    #         if user.is_staff:
    #             login(request, user)
    #             if settings.DEBUG:
    #                 token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
    #             else:
    #                 token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
    #             token = json.loads(token_json._content.decode("utf-8"))['token']
    #             str_name='Super User'
    #             email=user.email or ''
    #             userdetails={'Name':str_name,'email':email}
    #         else:
    #             login(request,user)
    #             if settings.DEBUG:
    #                 token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
    #             else:
    #                 token_json = requests.post('http://'+request.get_host()+'/api-token-auth/',{'username':str_username,'password':str_password})
    #             token = json.loads(token_json._content.decode("utf-8"))['token']
    #             str_name=(user.first_name +' '+ user.last_name).title()
    #             email=user.email or ''
    #             # 
    #             rst_user = UserDetails.objects.filter(user_ptr_id=request.user.id).values('fk_branch_id','fk_branch_id__vchr_name','fk_company_id','fk_group__vchr_name','fk_branch__vchr_code')
    #             branch_id = rst_user[0]['fk_branch_id']
    #             bln_indirect_discount = False
    #             bln_direct_discount = False
    #             if branch_id:
    #                 ins_indirect = Tools.objects.filter(jsn_data__contains=branch_id,vchr_tool_code = 'INDIRECT_DISCOUNT')
    #                 ins_direct = Tools.objects.filter(jsn_data__contains=branch_id,vchr_tool_code = 'DIRECT_DISCOUNT')
    #                 bln_indirect_discount = True if ins_indirect else False
    #                 bln_direct_discount = True if ins_direct else False

    #             branch_name = rst_user[0]['fk_branch_id__vchr_name']
    #             branch_code=rst_user[0]['fk_branch__vchr_code']
    #             group_name=rst_user[0]['fk_group__vchr_name'].upper()
    #             company_id=rst_user[0]['fk_company_id']
    #             branch_type =  user.userdetails.fk_branch.int_type if user.userdetails.fk_branch else ''
    #             userdetails={'Name':str_name,'email':email,'branch_id':branch_id,'branch_type':branch_type,'branch_code':branch_code,'branch_name':branch_name,'company_id':company_id,'group_name':group_name,'bln_indirect_discount':bln_indirect_discount,'bln_direct_discount':bln_direct_discount}
    #         ins_guest=UserDetails.objects.filter(id=user.id).values('int_guest_user').first()
    #         if ins_guest and ins_guest['int_guest_user']==1:
    #             ins_guest=GuestUserDetails.objects.filter(fk_user_id=user.id).values('session_expiry_time').first()
    #             if datetime.now()>=ins_guest['session_expiry_time']:
    #                 pass
    #             else:
    #                 ins_guest.update(int_guest_user=-1)

    #                 return Response({'status':0})


    #         lst_groups = []
    #         dct_insert = {'NAME':'',
    #             'ADD': False,
    #             'VIEW': False,
    #             'EDIT': False,
    #             'DELETE': False,
    #             'DOWNLOAD': False
    #             }

    #         """Uncomment below code for getting location details(IP address)

    #         obj_ip_location=geocoder.ip(str(request.META.get('REMOTE_ADDR')))
    #         dict_location={}
    #         dict_location['latlng']=obj_ip_location.latlng
    #         dict_location['city']=obj_ip_location.city
    #         dict_location=json.dumps(dict_location)
    #         ins_user=UserLogDetails.objects.filter(fk_user_id=user.id,dat_start_active__contains=datetime.today().date(),dat_last_active__contains=datetime.today().date(),json_ip__isnull=False).values('json_ip','pk_bint_id')
    #         if ins_user:
    #             if ins_user.last()['json_ip']['city'] != dict_location['city']:

    #                 UserLogDetails.objects.create(fk_user_id=user.id,dat_start_active=datetime.today(),dat_last_active=datetime.today(),json_ip=dict_location)
    #         else:
    #             UserLogDetails.objects.create(fk_user_id=user.id,dat_start_active=datetime.today(),dat_last_active=datetime.today(),json_ip=dict_location)

    #         """



    #         if not request.user.is_staff:
    #             ins_group_perm = GroupPermissions.objects.filter(fk_groups_id=user.userdetails.fk_group_id).values('fk_category_items__fk_sub_category__vchr_sub_category_name','pk_bint_id', 'fk_category_items__fk_menu_category__vchr_menu_category_name','fk_category_items__fk_main_category__vchr_main_category_name','bln_view','bln_add','bln_delete','bln_edit','bln_download')
    #             for dct_data in ins_group_perm :
    #                 dct_insert = {}
    #                 dct_insert['NAME'] = dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name']
    #                 dct_insert['ADD'] = dct_data['bln_add']
    #                 dct_insert['EDIT'] = dct_data['bln_edit']
    #                 dct_insert['VIEW'] = dct_data['bln_view']
    #                 dct_insert['DELETE'] = dct_data['bln_delete']
    #                 dct_insert['DOWNLOAD'] = dct_data['bln_download']
    #                 dct_insert['PARENT'] = dct_data['fk_category_items__fk_sub_category__vchr_sub_category_name']
    #                 dct_insert['MENU'] = dct_data['fk_category_items__fk_main_category__vchr_main_category_name']
    #                 lst_groups.append(dct_insert)
    #         else:
    #             # ins_group_perm = MenuCategory.objects.filter().values('fk_sub_category__vchr_sub_category_name','pk_bint_id', 'fk_category_items__fk_menu_category__vchr_menu_category_name','fk_category_items__fk_main_category__vchr_main_category_name','bln_view','bln_add','bln_delete','bln_edit','bln_download')
    #             # for dct_data in ins_group_perm :
    #             #     dct_insert = {}
    #             #     dct_insert['NAME'] = dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name']
    #             #     dct_insert['ADD'] = dct_data['bln_add']
    #             #     dct_insert['EDIT'] = dct_data['bln_edit']
    #             #     dct_insert['VIEW'] = dct_data['bln_view']
    #             #     dct_insert['DELETE'] = dct_data['bln_delete']
    #             #     dct_insert['DOWNLOAD'] = dct_data['bln_download']
    #             #     dct_insert['PARENT'] = dct_data['fk_category_items__fk_sub_category__vchr_sub_category_name']
    #             #     dct_insert['MENU'] = dct_data['fk_category_items__fk_main_category__vchr_main_category_name']
    #             #     lst_groups.append(dct_insert)
    #             return Response({'status':1,'token':token,'userdetails':userdetails})


    #         return Response({'status':1,'token':token,'userdetails':userdetails,'permission':lst_groups})
    #         # else:
    #         #     return Response({'status':1,'reason':"User doesn't exist"})

    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
    #         return Response({'status':0})


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
                    ins_user = UserDetails.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(full_name__icontains = str_terms) | Q(username__icontains = str_terms), fk_company = request.user.userdetails.fk_company, is_active = True).values('username', 'user_ptr_id','full_name')
                else:
                    ins_user = UserDetails.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')).filter(Q(full_name__icontains = str_terms) | Q(username__icontains = str_terms), is_active = True).values('username', 'user_ptr_id','full_name')
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
            # 
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

                    UserDetails.objects.get(user_ptr_id = ins_expired.values('fk_user_id')[0]['fk_user_id']).set_password(password)

                    UserDetails.objects.filter(user_ptr_id = ins_expired.values('fk_user_id')[0]['fk_user_id']).update(fk_group_id=fk_group,fk_created_id=request.user.id,dat_created=datetime.now(),int_guest_user=1)
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
                        if not (UserDetails.objects.filter(bint_usercode=bint_usercode)):
                            bln_loop=False

                bln_check = True
                while bln_check:
                    code=randint(100,999)
                    usercode = branch_code + str(code)
                    if not(UserDetails.objects.filter(username=usercode)):
                        bln_check = False

                password = uuid3(NAMESPACE_DNS,branch_code).hex[:9]

                username = usercode

                userobject = UserDetails(bint_usercode=bint_usercode,fk_group_id=fk_group,fk_branch_id=fk_branch,username=username,is_active=True,is_superuser=False,fk_created_id=request.user.id,dat_created=datetime.now(),fk_company_id=request.user.userdetails.fk_company_id,int_guest_user = 1)
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
            # 
            if request.data.get('update_password'):
                """to change password"""
                userobject = UserDetails.objects.get(username = request.data.get('str_username'))
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
                int_created_id = UserDetails.objects.filter(username = str_created_username).values_list('id',flat = True).first()

                # 
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
                    if str_username != str_old_username  and UserDetails.objects.filter(username=str_username):
                        return Response({'status':0,'message':'Usercode already exists'})

                    userobject = UserDetails.objects.filter(username = str_username).update(bint_phone  =  flt_phone,
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
                        if not (UserDetails.objects.filter(bint_usercode = bint_usercode)):
                            bln_loop = False

                    if UserDetails.objects.filter(username=str_username):
                        return Response({'status':0,'message':'Usercode already exists'})

                    userobject = UserDetails(bint_phone  =  flt_phone,
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
            # 
            _username= request.data.get('userName')
            _password=request.data.get('oldPassword')
            new_password = request.data.get('newPassword')
            user = authenticate(request, username=_username, password=_password)
            if user:
                user_ = UserDetails.objects.get(id = user.id)
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


            userobject = UserDetails(bint_phone  =  int_phone,
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
