from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from rest_framework.permissions import AllowAny,IsAuthenticated
from branch.models import Branch
from rest_framework.response import Response
from datetime import date,datetime
from django.db.models import Q
from groups.models import Groups
from company_permissions.models import GroupPermissions,MainCategory,MenuCategory,SubCategory,CategoryItems
from company.models import Company
from django.db import transaction
from userdetails.models import Userdetails
# Create your views here.
from POS import ins_logger
from django.db.models import Value, BooleanField
lst_add_disabled=[]
lst_edit_disabled=[]
lst_view_disabled=[]
lst_delete_disabled=[]
lst_download_disabled=[]


class UserGroupsAdd(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        """listing groups"""
        try:
            # import pdb; pdb.set_trace()
            if request.data.get('groupId'):
                lst_groups = list(Groups.objects.filter(int_status=0,pk_bint_id=request.data.get('groupId')).values('pk_bint_id','vchr_code','vchr_name','fk_created_id','fk_updated_id','dat_created').order_by('-pk_bint_id'))
            else:
                lst_groups = list(Groups.objects.filter(int_status=0,fk_company_id = request.user.userdetails.fk_company_id).values('pk_bint_id','vchr_code','vchr_name','fk_created_id','fk_updated_id','dat_created').order_by('-pk_bint_id'))
            return Response({'status':1, 'lst_groups' : lst_groups})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def post(self,request):
        """adding groups"""
        try:
            # import pdb; pdb.set_trace()
            vchr_code = request.data.get('vchrCode')
            vchr_name = request.data.get('vchrName')
            ins_duplicate = Groups.objects.filter(vchr_code = vchr_code,int_status =0).values('pk_bint_id')
            if ins_duplicate:
                return Response({'status':0,'message': 'code already exists'})
            else:
                ins_group_save = Groups.objects.create(vchr_code=vchr_code,vchr_name=vchr_name,int_status = 0,dat_created=datetime.now(),fk_created_id= request.user.id,fk_company_id = request.user.userdetails.fk_company_id)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def put(self,request):
        """updating groups"""
        try:
            # import pdb; pdb.set_trace()
            vchr_code = request.data.get('vchr_code')
            vchr_name = request.data.get('vchr_name')
            group_id = request.data.get('pk_bint_id')
            if not group_id:
                return Response({'status':0,'message': 'no group selected'})
            ins_duplicate = Groups.objects.filter(vchr_code = vchr_code,int_status =0).values('pk_bint_id').exclude(pk_bint_id = group_id)
            if ins_duplicate:
                return Response({'status':0,'message': 'code already exists'})
            else:
                ins_group_save = Groups.objects.filter(pk_bint_id=group_id).update(vchr_code=vchr_code,vchr_name=vchr_name,fk_updated_id= request.user.id)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def patch(self,request):
        """deleting groups"""
        try:
            # import pdb; pdb.set_trace()
            group_id = request.data.get('pk_bint_id')
            if not group_id:
                return Response({'status':0,'message': 'no group selected'})
            ins_group_save = Groups.objects.filter(pk_bint_id=group_id).update(int_status = -1)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class GroupListView(APIView):
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            int_company_id = request.data['company_id']
            lst_groups = []
            lst_add_permission = []
            lst_edit_permission = []
            lst_view_permission = []
            lst_delete_permission = []
            lst_download_permission = []
            lst_grp=[]
            # if request.user.userdetails.fk_group.vchr_name=='ADMIN':
            #     lst_grp=['BRANCH MANAGER','TERRITORY MANAGER','ZONE MANAGER','STATE HEAD','COUNTRY HEAD','ADMIN','STAFF','FINANCIER']
            # elif request.user.userdetails.fk_group.vchr_name in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
            #     lst_grp=['STAFF','FINANCIER']
            # elif request.user.userdetails.fk_group.vchr_name=='TERRITORY MANAGER':
            #     lst_grp=['BRANCH MANAGER','STAFF','FINANCIER']
            # elif request.user.userdetails.fk_group.vchr_name=='ZONE MANAGER':
            #     lst_grp=['BRANCH MANAGER','TERRITORY MANAGER','STAFF','FINANCIER']
            # elif request.user.userdetails.fk_group.vchr_name=='STATE HEAD':
            #     lst_grp=['BRANCH MANAGER','TERRITORY MANAGER','ZONE MANAGER','STAFF','FINANCIER']
            # elif request.user.userdetails.fk_group.vchr_name=='COUNTRY HEAD':
            #     lst_grp=['BRANCH MANAGER','TERRITORY MANAGER','ZONE MANAGER','STATE HEAD','COUNTRY HEAD','STAFF','FINANCIER']
            ins_company = Company.objects.get(pk_bint_id = int_company_id)
            ins_group = Groups.objects.filter(fk_company = ins_company,int_status=0).values('pk_bint_id','vchr_name','fk_company__vchr_name')
            #if int_company_id>0:
                #ins_company = CompanyDetails.objects.get(pk_bint_id = int_company_id)
                #ins_group = Groups.objects.filter(fk_company = ins_company,bln_status = True).values('pk_bint_id','vchr_name','fk_company__vchr_name','fk_company__fk_company_type__vchr_company_type')

            lst_group_id =  ins_group.values_list('pk_bint_id',flat=True)
            lst_group_perm=GroupPermissions.objects.filter(fk_groups_id__in=lst_group_id).values()
            if ins_group:
                for dct_group in ins_group:
                    lst_add_permission = [x for x in lst_group_perm.filter(fk_groups_id = dct_group['pk_bint_id'],bln_add=True).values_list('fk_category_items__fk_sub_category__vchr_sub_category_name',flat=True).distinct() ]
                    lst_edit_permission = [x for x in lst_group_perm.filter(fk_groups_id = dct_group['pk_bint_id'],bln_edit=True).values_list('fk_category_items__fk_sub_category__vchr_sub_category_name',flat=True).distinct() ]
                    lst_view_permission = [x for x in lst_group_perm.filter(fk_groups_id = dct_group['pk_bint_id'],bln_view=True).values_list('fk_category_items__fk_sub_category__vchr_sub_category_name',flat=True).distinct()]
                    lst_delete_permission = [x for x in lst_group_perm.filter(fk_groups_id = dct_group['pk_bint_id'],bln_delete=True).values_list('fk_category_items__fk_sub_category__vchr_sub_category_name',flat=True).distinct()]
                    lst_download_permission = [x for x in lst_group_perm.filter(fk_groups_id = dct_group['pk_bint_id'],bln_download=True).values_list('fk_category_items__fk_sub_category__vchr_sub_category_name',flat=True).distinct()]
                    if int_company_id>0:
                        dct_insert = {'id':dct_group['pk_bint_id'],'name':dct_group['vchr_name'],
                        'sub_add':lst_add_permission,
                        'sub_edit':lst_edit_permission,
                        'sub_view':lst_view_permission,
                        'sub_delete':lst_delete_permission,
                        'sub_download':lst_download_permission}
                    else:
                        dct_insert = {'id':dct_group['pk_bint_id'],'name':dct_group['vchr_name'],'company':dct_group['fk_company__vchr_name'],
                        'sub_add':lst_add_permission,
                        'sub_edit':lst_edit_permission,
                        'sub_view':lst_view_permission,
                        'sub_delete':lst_delete_permission,
                        'sub_download':lst_download_permission}
                    lst_groups.append(dct_insert.copy())
                    dct_insert.clear()
                    lst_add_permission = []
                    lst_edit_permission = []
                    lst_view_permission = []
                    lst_delete_permission = []
                    lst_download_permission = []

            return Response({'status':1,'data':lst_groups})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'data':str(e)})

# class GroupEditView(APIView):
#     def post(self,request):
#         try:
#             # import pdb; pdb.set_trace()
#             if request.data.get('operation') == 'load':
#                 # if not request.data.get('company_id'):
#                 ins_groups = Groups.objects.filter(pk_bint_id = request.data.get('group_id')).values('fk_company_id')
#                 lst_categories = CategoryItems.objects.filter(fk_company_id = ins_groups[0]['fk_company_id']).values_list('fk_menu_category__vchr_menu_category_name',flat = True)
#                 # else:
#                     # ins_groups = CompanyDetails.objects.filter(pk_bint_id = request.data.get('company_id')).values('fk_company_type')
#                     # lst_categories = CategoryItems.objects.filter(fk_company_id = ins_groups[0]['fk_company_id']).values_list('fk_menu_category__vchr_menu_category_name',flat = True)
#                 lst_permission = []
#                 dct_final_perms = {}
#                 int_group_id = int(request.data['group_id'])
#
#                 ins_group = Groups.objects.select_related('fk_company').get(pk_bint_id = int_group_id,int_status = 1)
#                 str_group_name = ins_group.vchr_name
#                 str_company_name = ins_group.fk_company.vchr_name
#                 # str_company_code = ins_group.fk_company.vchr_code
#                 int_company_id = ins_group.fk_company.pk_bint_id
#                 ins_category = list(lst_categories)
#                 ins_main = SubCategory.objects.values('pk_bint_id', 'vchr_sub_category_name','fk_main_category_id__vchr_main_category_name','fk_main_category_id')
#                 ins_group = Groups.objects.get(pk_bint_id = int_group_id)
#                 lst_perms = []
#                 qry_menu=MenuCategory.objects.values()
#                 qry_gp_perm=GroupPermissions.objects.filter(fk_groups_id=int_group_id)
#
#
#                 for dct_temp in ins_main:
#                     ins_sub = qry_menu.annotate(bln_add_perm = Value(False, output_field=BooleanField()), bln_edit_perm = Value(False, output_field=BooleanField()), bln_delete_perm = Value(False, output_field=BooleanField()), bln_view_perm = Value(False, output_field=BooleanField()))\
#                     .filter(fk_sub_category_id = dct_temp['pk_bint_id'], vchr_menu_category_name__in = ins_category).values('fk_sub_category_id','pk_bint_id','vchr_menu_category_name','bln_add_perm', 'bln_edit_perm', 'bln_delete_perm', 'bln_view_perm')
#                     for dct_sub in ins_sub:
#                         lst_perms = []
#                         if dct_sub['vchr_menu_category_name'] in lst_categories:
#                             ins_group_perm = qry_gp_perm.filter(fk_category_items_id__fk_menu_category_id__vchr_menu_category_name = dct_sub['vchr_menu_category_name']).values()
#                             if ins_group_perm:
#                                 dct_sub['bln_add_perm'] = ins_group_perm[0]['bln_add']
#                                 dct_sub['bln_edit_perm'] = ins_group_perm[0]['bln_edit']
#                                 dct_sub['bln_delete_perm'] = ins_group_perm[0]['bln_delete']
#                                 dct_sub['bln_view_perm'] = ins_group_perm[0]['bln_view']
#                                 dct_sub['add_disabled'] = False
#                                 dct_sub['edit_disabled'] = False
#                                 dct_sub['view_disabled'] = False
#                                 dct_sub['delete_disabled'] = False
#                                 dct_sub['cat_id'] = ins_group_perm[0]['fk_category_items_id']
#
#                                 # if dct_sub['vchr_sub_category_name'] in lst_add_disabled:
#                                 #     dct_sub['add_disabled'] = True
#                                 # if dct_sub['vchr_sub_category_name'] in lst_edit_disabled:
#                                 #     dct_sub['edit_disabled'] = True
#                                 # if dct_sub['vchr_sub_category_name'] in lst_view_disabled:
#                                 #     dct_sub['view_disabled'] = True
#                                 # if dct_sub['vchr_sub_category_name'] in lst_delete_disabled:
#                                 #     dct_sub['delete_disabled'] = True
#                             else:
#                                 dct_sub['bln_add_perm'] = False
#                                 dct_sub['bln_edit_perm'] = False
#                                 dct_sub['bln_delete_perm'] = False
#                                 dct_sub['bln_view_perm'] = False
#                                 dct_sub['add_disabled'] = False
#                                 dct_sub['edit_disabled'] = False
#                                 dct_sub['view_disabled'] = False
#                                 dct_sub['delete_disabled'] = False
#                                 dct_sub['cat_id'] = list(lst_categories.filter(fk_menu_category__vchr_menu_category_name = dct_sub['vchr_menu_category_name']).values('pk_bint_id'))[0]['pk_bint_id']
#
#                                 # if dct_sub['vchr_sub_category_name'] in lst_add_disabled:
#                                 #     dct_sub['add_disabled'] = True
#                                 # if dct_sub['vchr_sub_category_name'] in lst_edit_disabled:
#                                 #     dct_sub['edit_disabled'] = True
#                                 # if dct_sub['vchr_sub_category_name'] in lst_view_disabled:
#                                 #     dct_sub['view_disabled'] = True
#                                 # if dct_sub['vchr_sub_category_name'] in lst_delete_disabled:
#                                 #     dct_sub['delete_disabled'] = True
#                     if ins_sub and (dct_sub['vchr_menu_category_name'] in lst_categories):
#                         lst_perms.append({'name':dct_temp['vchr_sub_category_name'],'id':dct_temp['pk_bint_id'], 'items':ins_sub, 'levelTwoClicked':False})
#
#                     if dct_temp['fk_main_category_id'] not in dct_final_perms:
#                         dct_final_perms[dct_temp['fk_main_category_id']] = {}
#                         dct_final_perms[dct_temp['fk_main_category_id']]['data'] = []
#                         dct_final_perms[dct_temp['fk_main_category_id']]['data'] = lst_perms
#                         dct_final_perms[dct_temp['fk_main_category_id']]['levelOneClicked'] = False
#                         dct_final_perms[dct_temp['fk_main_category_id']]['name'] = dct_temp['fk_main_category_id__vchr_main_category_name']
#                     else:
#                         dct_final_perms[dct_temp['fk_main_category_id']]['data'].extend(lst_perms)
#
#                 # import pdb; pdb.set_trace()
#
#                 # ins_permission = list(GroupPermissions.objects.filter(fk_groups_id = int_group_id).values('pk_bint_id','fk_category_items__fk_menu_category__vchr_menu_category_name','bln_add','bln_view','bln_edit','bln_delete').order_by('fk_category_items__fk_menu_category__vchr_menu_category_name'))
#                 # dct_insert = {'id':0,'name': '','selectedADD': False, 'selectedVIEW': False, 'selectedEDIT': False, 'selectedDELETE': False ,'edit_disabled':False,'delete_disabled':False, 'add_disabled':False, 'view_disabled':False}
#                 # if ins_permission:
#                 #     for dct_data in ins_permission:
#                 #         if dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name'] in ins_category:
#                 #             dct_insert['add_disabled'] = False
#                 #             dct_insert['edit_disabled'] = False
#                 #             dct_insert['view_disabled'] = False
#                 #             dct_insert['delete_disabled'] = False
#                 #             # if dct_data['fk_sub_category__vchr_sub_category_name'] in lst_add_disabled:
#                 #             #     dct_insert['add_disabled'] = True
#                 #             # if dct_data['fk_sub_category__vchr_sub_category_name'] in lst_edit_disabled:
#                 #             #     dct_insert['edit_disabled'] = True
#                 #             # if dct_data['fk_sub_category__vchr_sub_category_name'] in lst_view_disabled:
#                 #             #     dct_insert['view_disabled'] = True
#                 #             # if dct_data['fk_sub_category__vchr_sub_category_name'] in lst_delete_disabled:
#                 #             #     dct_insert['delete_disabled'] = True
#                 #             dct_insert['name'] = dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name']
#                 #             dct_insert['id'] = dct_data['pk_bint_id']
#                 #             dct_insert['selectedADD'] = dct_data['bln_add']
#                 #             dct_insert['selectedVIEW'] = dct_data['bln_view']
#                 #             dct_insert['selectedEDIT'] = dct_data['bln_edit']
#                 #             dct_insert['selectedDELETE'] = dct_data['bln_delete']
#                 #             ins_category.remove(dct_data['fk_category_items__fk_menu_category__vchr_menu_category_name'])
#                 #             lst_permission.append(dct_insert.copy())
#                     # if ins_category:
#                     #     for str_name in ins_category:
#                     #         ins_main = SubCategory.objects.filter(vchr_sub_category_name = str_name).values('pk_bint_id')
#                     #         # if ins_main
#                     #         dct_insert['name'] = str_name
#                     #         dct_insert['id'] = 0
#                     #         dct_insert['fk_main'] = ins_main[0]['pk_bint_id']
#                     #         dct_insert['selectedADD'] = False
#                     #         dct_insert['selectedVIEW'] = False
#                     #         dct_insert['selectedEDIT'] = False
#                     #         dct_insert['selectedDELETE'] = False
#                     #         lst_permission.append(dct_insert.copy())
#                 dct_company = {
#                     'id':int_company_id,
#                     # 'code':str_company_code,
#                     'name':str_company_name
#                 }
#                 return Response({'status':0,'perms':dct_final_perms,'group':str_group_name,'company':dct_company})
#
#             elif request.data.get('operation') == 'edit':
#                 # import pdb; pdb.set_trace()
#                 int_group_id = request.data['group_id']
#                 ins_group_check = Groups.objects.filter(vchr_name__iexact = request.data['group_name'],fk_company = request.data['company_id'],int_status=1).exclude(pk_bint_id = int_group_id)
#                 if ins_group_check:
#                     return Response({'status':1,'data':'Group already exists'})
#                 ins_group = Groups.objects.filter(pk_bint_id = int_group_id,int_status = 1)
#                 int_company_id = request.data['company_id']
#                 str_group_name = request.data['group_name']
#                 lst_group_data = request.data['group_data']
#                 ins_group.update(fk_company_id= int_company_id,vchr_name = str_group_name)
#                 ins_backup = GroupPermissions.objects.filter(fk_groups_id=int_group_id)
#
#                 GroupPermissions.objects.filter(fk_groups_id=int_group_id).delete()
#                 lst_gp_perms=[]
#                 for dct_data in lst_group_data:
#                     for dct_main in lst_group_data[dct_data]['data']:
#                         for dct_temp in dct_main['items']:
#                             if dct_temp['add_disabled']:
#                                 bln_add = False
#                             elif dct_temp['bln_add_perm']:
#                                 bln_add = True
#                             else:
#                                 bln_add = False
#
#                             if dct_temp['edit_disabled']:
#                                 bln_edit = False
#                             elif dct_temp['bln_edit_perm']:
#                                 bln_edit = True
#                             else:
#                                 bln_edit = False
#
#                             if dct_temp['view_disabled']:
#                                 bln_view = False
#                             elif dct_temp['bln_view_perm']:
#                                 bln_view = True
#                             else:
#                                 bln_view = False
#
#                             if dct_temp['delete_disabled']:
#                                 bln_delete = False
#                             elif dct_temp['bln_delete_perm']:
#                                 bln_delete = True
#                             else:
#                                 bln_delete = False
#
#                             int_GroupPermissions=GroupPermissions(
#                                 fk_groups_id = int_group_id,
#                                 fk_category_items_id = dct_temp['cat_id'],
#                                 bln_add = bln_add,
#                                 bln_edit = bln_edit,
#                                 bln_view = bln_view,
#                                 bln_delete = bln_delete
#                             )
#                             lst_gp_perms.append(int_GroupPermissions)
#
#                 GroupPermissions.objects.bulk_create(lst_gp_perms)
#                 return Response({'status':0,'group':str_group_name})
#             else:
#                 return Response({'status':1,'data':'No groups updated'})
#         except Exception as e:
#             if 'ins_backup' in locals():
#                 for ins in ins_backup:
#                     ins.save()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':1,'data':str(e)})

class CategoryListNew2(APIView):
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_company_id = request.data.get("role")
            lst_category_pks=CategoryItems.objects.filter(fk_company_id=int_company_id).values_list('fk_main_category_id',flat=True)
            ins_main = MainCategory.objects.filter(pk_bint_id__in=lst_category_pks).values('pk_bint_id', 'vchr_main_category_name')
            lst_perms = []
            ins_CategoryItems=CategoryItems.objects.filter(fk_company_id=int_company_id).values('pk_bint_id','fk_sub_category_id','fk_main_category_id','fk_menu_category_id','fk_sub_category__vchr_sub_category_name','fk_main_category__vchr_main_category_name','fk_menu_category__vchr_menu_category_name')
            lst_main=[]
            dct_main={}
            for data in ins_CategoryItems:
                if data['fk_main_category__vchr_main_category_name'] not in dct_main:
                    dct_main[data['fk_main_category__vchr_main_category_name']]={}
                    dct_main[data['fk_main_category__vchr_main_category_name']]['id']=data['fk_main_category_id']
                    dct_main[data['fk_main_category__vchr_main_category_name']]['name']=data['fk_main_category__vchr_main_category_name']
                    dct_main[data['fk_main_category__vchr_main_category_name']]['levelOneClicked']=False
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]={}
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['id']=data['fk_sub_category_id']
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['name']=data['fk_sub_category__vchr_sub_category_name']
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['levelTwoClicked']=False
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']].update({'sub_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False,'bln_download_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False, 'download_disabled': False})
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]={}
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['id']=data['fk_menu_category_id']
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['name']=data['fk_menu_category__vchr_menu_category_name']
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['cat_id']=data['pk_bint_id']
                    dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False,'bln_download_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False, 'download_disabled': False})
                    # lst_menu_category.append({'name':data['fk_menu_category__vchr_menu_category_name'],'menu_id':data['fk_menu_category_id'],'sub_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False})
                    # dct_main['sub_items'].append({'name':data['fk_sub_category__vchr_sub_category_name'],'sub_id':data['fk_sub_category_id'],'sub_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'menu_items':lst_menu_category})
                else:
                    if data['fk_sub_category__vchr_sub_category_name'] not in dct_main[data['fk_main_category__vchr_main_category_name']]:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]={}
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['id']=data['fk_sub_category_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['name']=data['fk_sub_category__vchr_sub_category_name']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['levelTwoClicked']=False
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']].update({'sub_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False,'bln_download_perm': False,'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'download_disabled': False})
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]={}
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['id']=data['fk_menu_category_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['name']=data['fk_menu_category__vchr_menu_category_name']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['cat_id']=data['pk_bint_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_download_perm': False,'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled':False,'download_disabled': False})
                    elif data['fk_menu_category__vchr_menu_category_name'] not in dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]={}
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['id']=data['fk_menu_category_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['name']=data['fk_menu_category__vchr_menu_category_name']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['cat_id']=data['pk_bint_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False,'bln_download_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'download_disabled': False})
            return Response({'status':1,'data':dct_main})
                    # lst_main.append({})
                    # dct_main[data['fk_main_category__vchr_main_category_name']]=len(lst_main)-1
                    # lst_index_main=dct_main[data['fk_main_category__vchr_main_category_name']]
                    # lst_main[lst_index_main]['main_id']=data['fk_main_category_id']
                    # lst_main[lst_index_main]['name']=data['fk_main_category__vchr_main_category_name']
                    # lst_main[lst_index_main]['main_status']=False

            # To check whether admin group is created

            # To check whether any user is created in admin group

            # lst_menu_category=[]
            # for dct_temp in ins_main:
            #     ins_sub = SubCategory.objects.filter(Q(fk_main_category = dct_temp['pk_bint_id'])).values('fk_main_category_id','pk_bint_id','vchr_sub_category_name')
            #     for dct_sub in ins_sub:
            #         ins_menu = MenuCategory.objects.annotate(bln_add_perm = Value(False, output_field=BooleanField()), bln_edit_perm = Value(False, output_field=BooleanField()), bln_delete_perm = Value(False, output_field=BooleanField()), bln_view_perm = Value(False, output_field=BooleanField())).filter(Q(fk_sub_category = dct_sub['pk_bint_id'])).\
            #         values('fk_sub_category_id','fk_sub_category__vchr_sub_category_name','pk_bint_id','vchr_menu_category_name')
            #         for itr_item in ins_menu:
            #                 itr_item['bln_add_perm'] = False
            #                 itr_item['bln_edit_perm'] = False
            #                 itr_item['bln_delete_perm'] = False
            #                 itr_item['bln_view_perm'] = False
            #                 itr_item['add_disabled'] = False
            #                 itr_item['edit_disabled'] = False
            #                 itr_item['view_disabled'] = False
            #                 itr_item['delete_disabled'] = False
            #
            #
            #
            #                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_add_disabled:
            #                     itr_item['add_disabled'] = True
            #                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_edit_disabled:
            #                     itr_item['edit_disabled'] = True
            #                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_view_disabled:
            #                     itr_item['view_disabled'] = True
            #                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_delete_disabled:
            #                     itr_item['delete_disabled'] = True
            #         if ins_menu:
            #             lst_menu_category.append({'name':dct_sub['vchr_sub_category_name'],'sub_id':dct_sub['pk_bint_id'],'sub_status':False,'bln_add_perm':False,'bln_edit_perm':False,'bln_delete_perm':False,'bln_view_perm':False,'add_disabled':False,'edit_disabled':False,'view_disabled':False,'delete_disabled':False,'menu_items':list(ins_menu)})
            #     if ins_sub:
            #         lst_perms.append({'name':dct_temp['vchr_main_category_name'],'main_id':dct_temp['pk_bint_id'], 'sub_items':lst_menu_category, 'main_status':False})
            #
            # import pdb; pdb.set_trace()
            # return Response({'status':1,'data':lst_perms})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'data':str(e)})

class GroupCreateViewNew(APIView):
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            ins_company = Company.objects.get(pk_bint_id = request.data['company_id'])
            dct_data = request.data['group_data']
            str_name = request.data['group_name']
            str_code = request.data['group_code']

            # int_department = int(request.data.get('department'))
            # ins_group_check = Groups.objects.filter(vchr_name__iexact = str_name,fk_company = ins_company,bln_status=True,fk_department_id = int_department)
            ins_group_check = Groups.objects.filter(vchr_name__iexact = str_name,fk_company = ins_company,int_status = 0)
            if ins_group_check:
                # ins_prv_grp = Groups.objects.filter(vchr_name__iexact = str_name,fk_company = ins_company,bln_status=True,fk_department_id = int_department)
                # if ins_prv_grp:
                return Response({'status':'1','data':'Group already exists'})
            # else:
            #     return Response({'status':'1','data':'Group already exists'})
            # ins_group = Groups.objects.create(vchr_name = str_name,fk_company = ins_company,bln_status=True,fk_department_id = int_department)
            with transaction.atomic():
                ins_group = Groups.objects.create(vchr_name = str_name,vchr_code = str_code,fk_company = ins_company,int_status=0)
                # import pdb; pdb.set_trace()
                if ins_group:
                    lst_gp_perms=[]
                    for main_key in dct_data:
                        if main_key in ['id','name','levelOneClicked','levelTwoClicked']:
                            continue
                        for sub_key in dct_data[main_key]:
                            if sub_key in ['id','name','levelOneClicked','levelTwoClicked','sub_status','bln_add_perm','bln_edit_perm','bln_delete_perm','bln_download_perm','bln_view_perm','add_disabled','edit_disabled','view_disabled','delete_disabled','download_disabled']:
                                continue
                            for menu_key in dct_data[main_key][sub_key]:
                                if menu_key in ['id','name','levelOneClicked','levelTwoClicked','sub_status','bln_add_perm','bln_edit_perm','bln_delete_perm','bln_download_perm','bln_view_perm','add_disabled','edit_disabled','view_disabled','delete_disabled','download_disabled']:
                                    continue
                                # import pdb; pdb.set_trace()
                                dct_temp=dct_data[main_key][sub_key][menu_key]
                                if dct_temp['add_disabled']:
                                    bln_add = False
                                elif dct_temp['bln_add_perm']:
                                    bln_add = True
                                else:
                                    bln_add = False

                                if dct_temp['edit_disabled']:
                                    bln_edit = False
                                elif dct_temp['bln_edit_perm']:
                                    bln_edit = True
                                else:
                                    bln_edit = False

                                if dct_temp['view_disabled']:
                                    bln_view = False
                                elif dct_temp['bln_view_perm']:
                                    bln_view = True
                                else:
                                    bln_view = False

                                if dct_temp['delete_disabled']:
                                    bln_delete = False
                                elif dct_temp['bln_delete_perm']:
                                    bln_delete = True
                                else:
                                    bln_delete = False
                                if dct_temp['download_disabled']:
                                    bln_download = False
                                elif dct_temp['bln_download_perm']:
                                    bln_download = True
                                else:
                                    bln_download = False

                                int_GroupPermissions=GroupPermissions(
                                    fk_groups_id = ins_group.pk_bint_id,
                                    fk_category_items_id = dct_temp['cat_id'],
                                    bln_add = bln_add,
                                    bln_edit = bln_edit,
                                    bln_view = bln_view,
                                    bln_delete = bln_delete,
                                    bln_download = bln_download
                                )
                                lst_gp_perms.append(int_GroupPermissions)
                    # import pdb; pdb.set_trace()
                    GroupPermissions.objects.bulk_create(lst_gp_perms)


            return Response({'status':1,'data':'Group was successfully created'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            Groups.objects.get(vchr_name = request.data['group_name']).delete()
            return Response({'status':0,'data':str(e)})

# class CategoryListNew(APIView):
#     permission_classes = [AllowAny]
#     def post(self,request):
#         try:
#
#
#             int_company_id = request.data.get("role")
#             lst_category_items = list(CategoryItems.objects.annotate(bln_add_perm = Value(False, output_field=BooleanField()), bln_edit_perm = Value(False, output_field=BooleanField()), bln_delete_perm = Value(False, output_field=BooleanField()), bln_view_perm = Value(False, output_field=BooleanField())).filter(fk_company = int_company_id).values('pk_bint_id','fk_main_category','fk_sub_category','fk_menu_category','fk_main_category__vchr_main_category_name','fk_sub_category__vchr_sub_category_name','fk_menu_category__vchr_menu_category_name','bln_add_perm', 'bln_edit_perm', 'bln_delete_perm', 'bln_view_perm').order_by('fk_main_category'))
#             int_temp = 0
#             dct_perms = {}
#             lst_perms = []
#             lst_items = []
#             data={}
#             for itr_item in lst_category_items:
#                 itr_item['bln_add_perm'] = False
#                 itr_item['bln_edit_perm'] = False
#                 itr_item['bln_delete_perm'] = False
#                 itr_item['bln_view_perm'] = False
#                 itr_item['add_disabled'] = False
#                 itr_item['edit_disabled'] = False
#                 itr_item['view_disabled'] = False
#                 itr_item['delete_disabled'] = False
#
#                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_add_disabled:
#                     itr_item['add_disabled'] = True
#                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_edit_disabled:
#                     itr_item['edit_disabled'] = True
#                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_view_disabled:
#                     itr_item['view_disabled'] = True
#                 if itr_item['fk_sub_category__vchr_sub_category_name'] in lst_delete_disabled:
#                     itr_item['delete_disabled'] = True
#
#
#                 if itr_itr_item['fk_main_category'] not in data:
#                     data[itr_item['fk_main_category_id']]={}
#                     data[itr_item['fk_main_category_id']]['status']=False
#                     data[itr_item['fk_main_category_id']]['id']=itr_itr_item['fk_main_category_id']
#                     data[itr_item['fk_main_category_id']]['items']={}
#                     data[itr_item['fk_main_category_id']]['items'][itr_item['fk_sub_category_id']]={}
#                     data[itr_item['fk_main_category_id']]['items'][itr_item['fk_sub_category_id']]['pk_bint_id']=itr_item['fk_sub_category_id']
#                     data[itr_item['fk_main_category_id']]['items'][itr_item['fk_sub_category_id']]['vchr_sub_category_name']=itr_item['fk_sub_category__vchr_sub_category_name']
#
#                                     if int_temp != itr_item['fk_main_category']:
#                     lst_perms.append(dct_perms)
#                     lst_items = [{'cat_item_id':itr_item['pk_bint_id'],'fk_main_category':itr_item['fk_main_category'],'pk_bint_id':itr_item['fk_sub_category'],'vchr_sub_category_name':itr_item['fk_sub_category__vchr_sub_category_name'],'bln_add_perm':itr_item['bln_add_perm'], 'bln_edit_perm':itr_item['bln_edit_perm'], 'bln_delete_perm':itr_item['bln_delete_perm'], 'bln_view_perm':itr_item['bln_view_perm'], 'add_disabled':itr_item['add_disabled'], 'edit_disabled':itr_item['edit_disabled'], 'view_disabled':itr_item['view_disabled'], 'delete_disabled':itr_item['delete_disabled']}]
#                     dct_perms = {'name':itr_item['fk_main_category__vchr_main_category_name'],'id':itr_item['fk_main_category'], 'items':lst_items, 'status':False}
#                     int_temp = itr_item['fk_main_category']
#                 else:
#                     dct_perms['items'].append({'cat_item_id':itr_item['pk_bint_id'],'fk_main_category':itr_item['fk_main_category'],'pk_bint_id':itr_item['fk_sub_category'],'vchr_sub_category_name':itr_item['fk_sub_category__vchr_sub_category_name'],'bln_add_perm':itr_item['bln_add_perm'], 'bln_edit_perm':itr_item['bln_edit_perm'], 'bln_delete_perm':itr_item['bln_delete_perm'], 'bln_view_perm':itr_item['bln_view_perm'], 'add_disabled':itr_item['add_disabled'], 'edit_disabled':itr_item['edit_disabled'], 'view_disabled':itr_item['view_disabled'], 'delete_disabled':itr_item['delete_disabled']})
#
#             lst_perms.append(dct_perms)
#             lst_perms.pop(0)
#             return Response({'status':'0','data':lst_perms})
#
#         except Exception as e:
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':'1','data':str(e)})



class GroupDeleteView(APIView):
    def post(self,request):
        try:
            int_group_id = request.data['pk_bint_id']
            ins_group = Groups.objects.filter(pk_bint_id = int_group_id,int_status = 0)
            ins_user = Userdetails.objects.filter(is_active=True,fk_group = ins_group)
            if ins_user:
                return Response({'status':'1','data':'Not deletable since users exist in this group.'})
            else:
                ins_permission = GroupPermissions.objects.filter(fk_groups_id = int_group_id)
                ins_permission.delete()
                ins_group.update(int_status = -1)
                return Response({'status':1,'data':'Group was deleted'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':1,'data':str(e)})

class GroupEditView(APIView):

    """"
        To Edit and View the group permissions.
        param : groud id, company id
        return : Dict of Category_item with group permissions
    """

    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # On edit or view page load
            if request.data.get('operation') == 'load':
                int_group_id = int(request.data.get('group_id'))
                int_company_id  = int(request.data.get('company_id', request.user.userdetails.fk_company_id))
                dct_group = Groups.objects.filter(pk_bint_id = int_group_id).values('pk_bint_id','vchr_name','vchr_code').first()
                ins_CategoryItems = CategoryItems.objects.filter(fk_company_id=int_company_id).values('pk_bint_id','fk_sub_category_id','fk_main_category_id','fk_menu_category_id','fk_sub_category__vchr_sub_category_name','fk_main_category__vchr_main_category_name','fk_menu_category__vchr_menu_category_name')
                qry_gp_perm = GroupPermissions.objects.filter(fk_groups_id=int_group_id)
                dct_main = {}
                for data in ins_CategoryItems:
                    if data['fk_main_category__vchr_main_category_name'] not in dct_main:
                        dct_main[data['fk_main_category__vchr_main_category_name']] = {}
                        dct_main[data['fk_main_category__vchr_main_category_name']]['id'] = data['fk_main_category_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']]['name'] = data['fk_main_category__vchr_main_category_name']
                        dct_main[data['fk_main_category__vchr_main_category_name']]['levelOneClicked'] = False
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']] = {}
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['id'] = data['fk_sub_category_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['name'] = data['fk_sub_category__vchr_sub_category_name']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['levelTwoClicked']=False
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']].update({'sub_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_view_perm': False,'bln_download_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'download_disabled': False})

                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']] = {}
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['id'] = data['fk_menu_category_id']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['name'] = data['fk_menu_category__vchr_menu_category_name']
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['cat_id'] = data['pk_bint_id']

                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_view_perm': False,'bln_download_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'download_disabled': False})
                        if qry_gp_perm.filter(fk_category_items_id = data['pk_bint_id']).values():
                            ins_group_perm = qry_gp_perm.filter(fk_category_items_id = data['pk_bint_id']).values().first()
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': ins_group_perm['bln_add'], 'bln_edit_perm': ins_group_perm['bln_edit'],'bln_download_perm': ins_group_perm['bln_download'], 'bln_delete_perm': ins_group_perm['bln_delete'], 'bln_view_perm': ins_group_perm['bln_view'], 'add_disabled': ins_group_perm['bln_add'], 'edit_disabled': ins_group_perm['bln_edit'], 'view_disabled': ins_group_perm['bln_view'], 'delete_disabled': ins_group_perm['bln_delete'],'download_disabled': ins_group_perm['bln_download']})

                    else:
                        if data['fk_sub_category__vchr_sub_category_name'] not in dct_main[data['fk_main_category__vchr_main_category_name']]:
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']] = {}
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['id'] = data['fk_sub_category_id']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['name'] = data['fk_sub_category__vchr_sub_category_name']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['levelTwoClicked'] = False
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']].update({'sub_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False,'bln_download_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'download_disabled': False})

                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']] = {}
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['id'] = data['fk_menu_category_id']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['name'] = data['fk_menu_category__vchr_menu_category_name']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['cat_id'] = data['pk_bint_id']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_download_perm': False, 'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled':False,'download_disabled': False})

                            if qry_gp_perm.filter(fk_category_items_id = data['pk_bint_id']).values():
                                ins_group_perm = qry_gp_perm.filter(fk_category_items_id = data['pk_bint_id']).values().first()
                                dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': ins_group_perm['bln_add'], 'bln_edit_perm': ins_group_perm['bln_edit'], 'bln_delete_perm': ins_group_perm['bln_delete'],'bln_download_perm': ins_group_perm['bln_download'], 'bln_view_perm': ins_group_perm['bln_view'], 'add_disabled': ins_group_perm['bln_add'], 'edit_disabled': ins_group_perm['bln_edit'], 'view_disabled': ins_group_perm['bln_view'], 'delete_disabled': ins_group_perm['bln_delete'],'download_disabled': ins_group_perm['bln_download']})

                        elif data['fk_menu_category__vchr_menu_category_name'] not in dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]:

                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']] = {}
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['id'] = data['fk_menu_category_id']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['name'] = data['fk_menu_category__vchr_menu_category_name']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']]['cat_id'] = data['pk_bint_id']
                            dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': False, 'bln_edit_perm': False, 'bln_delete_perm': False, 'bln_download_perm': False,'bln_view_perm': False, 'add_disabled': False, 'edit_disabled': False, 'view_disabled': False, 'delete_disabled': False,'download_disabled': False})

                            if qry_gp_perm.filter(fk_category_items_id = data['pk_bint_id']).values():
                                ins_group_perm = qry_gp_perm.filter(fk_category_items_id = data['pk_bint_id']).values().first()
                                dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][data['fk_menu_category__vchr_menu_category_name']].update({'menu_status': False, 'bln_add_perm': ins_group_perm['bln_add'], 'bln_edit_perm': ins_group_perm['bln_edit'], 'bln_delete_perm': ins_group_perm['bln_delete'],'bln_download_perm': ins_group_perm['bln_download'], 'bln_view_perm': ins_group_perm['bln_view'], 'add_disabled': ins_group_perm['bln_add'], 'edit_disabled': ins_group_perm['bln_edit'], 'view_disabled': ins_group_perm['bln_view'], 'delete_disabled': ins_group_perm['bln_delete'],'download_disabled': ins_group_perm['bln_download']})
                    # import pdb; pdb.set_trace()
                    lst_menu = list(dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']].keys()-['sub_status','bln_add_perm','bln_edit_perm','bln_delete_perm','bln_view_perm','bln_download_perm','add_disabled','edit_disabled','view_disabled','delete_disabled','download_disabled','id','levelTwoClicked','name'])
                    lst_add = []
                    lst_edit = []
                    lst_view = []
                    lst_delete = []
                    lst_download = []
                    for item in lst_menu:
                        lst_add.append(dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][item]['bln_add_perm'])
                        lst_edit.append(dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][item]['bln_edit_perm'])
                        lst_view.append(dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][item]['bln_view_perm'])
                        lst_delete.append(dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][item]['bln_delete_perm'])
                        lst_download.append(dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']][item]['bln_download_perm'])
                    if all(lst_add):
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_add_perm'] = True
                    else:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_add_perm'] = False
                    if all(lst_edit):
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_edit_perm'] = True
                    else:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_edit_perm'] = False
                    if all(lst_view):
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_view_perm'] = True
                    else:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_view_perm'] = False
                    if all(lst_delete):
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_delete_perm'] = True
                    else:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_delete_perm'] = False
                    if all(lst_download):
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_download_perm'] = True
                    else:
                        dct_main[data['fk_main_category__vchr_main_category_name']][data['fk_sub_category__vchr_sub_category_name']]['bln_download_perm'] = False

                return Response({'status':1,'data':dct_main,'dct_group':dct_group})

            # To upadte the group permissions after edit_disabled
            elif request.data.get('operation') == 'edit':
                int_group_id = int(request.data.get('group_id'))
                ins_group_check = Groups.objects.filter(vchr_name__iexact = request.data['group_name'],fk_company = request.data['company_id'],int_status=0).exclude(pk_bint_id = int_group_id)
                if ins_group_check:
                    return Response({'status':1,'data':'Group already exists'})
                int_company_id = request.data['company_id']
                str_group_name = request.data['group_name']
                str_group_code = request.data['group_code']
                dct_data = request.data['group_data']

                with transaction.atomic():
                    ins_group = Groups.objects.filter(pk_bint_id = int_group_id,int_status = 0)
                    ins_group.update(fk_company_id= int_company_id,vchr_name = str_group_name,vchr_code = str_group_code)
                    GroupPermissions.objects.filter(fk_groups_id = int_group_id).delete()
                    lst_gp_perms=[]
                    for main_key in dct_data:
                        if main_key in ['id','name','levelOneClicked','levelTwoClicked']:
                            continue
                        for sub_key in dct_data[main_key]:
                            if sub_key in ['id','name','levelOneClicked','levelTwoClicked','sub_status','bln_add_perm','bln_edit_perm','bln_delete_perm','bln_download_perm','bln_view_perm','add_disabled','edit_disabled','view_disabled','delete_disabled','download_disabled']:
                                continue
                            for menu_key in dct_data[main_key][sub_key]:
                                if menu_key in ['id','name','levelOneClicked','levelTwoClicked','sub_status','bln_add_perm','bln_edit_perm','bln_delete_perm','bln_download_perm','bln_view_perm','add_disabled','edit_disabled','view_disabled','delete_disabled','download_disabled']:
                                    continue
                                dct_temp=dct_data[main_key][sub_key][menu_key]

                                if dct_temp['bln_add_perm']:
                                    bln_add = True
                                else:
                                    bln_add = False
                                if dct_temp['bln_edit_perm']:
                                    bln_edit = True
                                else:
                                    bln_edit = False
                                if dct_temp['bln_view_perm']:
                                    bln_view = True
                                else:
                                    bln_view = False
                                if dct_temp['bln_delete_perm']:
                                    bln_delete = True
                                else:
                                    bln_delete = False
                                if dct_temp['bln_download_perm']:
                                    bln_download = True
                                else:
                                    bln_download = False

                                int_GroupPermissions=GroupPermissions(
                                    fk_groups_id = int_group_id,
                                    fk_category_items_id = dct_temp['cat_id'],
                                    bln_add = bln_add,
                                    bln_edit = bln_edit,
                                    bln_view = bln_view,
                                    bln_delete = bln_delete,
                                    bln_download = bln_download
                                )
                                lst_gp_perms.append(int_GroupPermissions)
                    GroupPermissions.objects.bulk_create(lst_gp_perms)
                return Response({'status':1,'data':'Group was successfully updated'})
            elif request.data.get('operation') == 'view':
                ins_groups = Groups.objects.filter(pk_bint_id = request.data.get('group_id')).values('fk_company_id')
                lst_categories = CategoryItems.objects.filter(fk_company_id = ins_groups[0]['fk_company_id']).values_list('fk_menu_category__vchr_menu_category_name',flat = True)
                lst_permission = []
                dct_final_perms = {}
                int_group_id = int(request.data['group_id'])

                ins_group = Groups.objects.select_related('fk_company').get(pk_bint_id = int_group_id,int_status = 0)
                str_group_name = ins_group.vchr_name
                str_company_name = ins_group.fk_company.vchr_name
                # str_company_code = ins_group.fk_company.vchr_code
                int_company_id = ins_group.fk_company.pk_bint_id
                ins_category = list(lst_categories)
                ins_main = SubCategory.objects.values('pk_bint_id', 'vchr_sub_category_name','fk_main_category_id__vchr_main_category_name','fk_main_category_id')
                ins_group = Groups.objects.get(pk_bint_id = int_group_id)
                lst_perms = []
                qry_menu=MenuCategory.objects.values()
                qry_gp_perm=GroupPermissions.objects.filter(fk_groups_id=int_group_id)


                for dct_temp in ins_main:
                    ins_sub = qry_menu.annotate(bln_add_perm = Value(False, output_field=BooleanField()), bln_edit_perm = Value(False, output_field=BooleanField()), bln_delete_perm = Value(False, output_field=BooleanField()), bln_download_perm = Value(False, output_field=BooleanField()), bln_view_perm = Value(False, output_field=BooleanField()))\
                    .filter(fk_sub_category_id = dct_temp['pk_bint_id'], vchr_menu_category_name__in = ins_category).values('fk_sub_category_id','pk_bint_id','vchr_menu_category_name','bln_add_perm', 'bln_edit_perm', 'bln_delete_perm', 'bln_view_perm', 'bln_download_perm')
                    for dct_sub in ins_sub:
                        lst_perms = []
                        if dct_sub['vchr_menu_category_name'] in lst_categories:
                            ins_group_perm = qry_gp_perm.filter(fk_category_items_id__fk_menu_category_id__vchr_menu_category_name = dct_sub['vchr_menu_category_name']).values()
                            if ins_group_perm:
                                dct_sub['bln_add_perm'] = ins_group_perm[0]['bln_add']
                                dct_sub['bln_edit_perm'] = ins_group_perm[0]['bln_edit']
                                dct_sub['bln_delete_perm'] = ins_group_perm[0]['bln_delete']
                                dct_sub['bln_download_perm'] = ins_group_perm[0]['bln_download']
                                dct_sub['bln_view_perm'] = ins_group_perm[0]['bln_view']
                                dct_sub['add_disabled'] = False
                                dct_sub['edit_disabled'] = False
                                dct_sub['view_disabled'] = False
                                dct_sub['delete_disabled'] = False
                                dct_sub['download_disabled'] = False
                                dct_sub['cat_id'] = ins_group_perm[0]['fk_category_items_id']

                            else:
                                dct_sub['bln_add_perm'] = False
                                dct_sub['bln_edit_perm'] = False
                                dct_sub['bln_delete_perm'] = False
                                dct_sub['bln_view_perm'] = False
                                dct_sub['bln_download_perm'] = False
                                dct_sub['add_disabled'] = False
                                dct_sub['edit_disabled'] = False
                                dct_sub['view_disabled'] = False
                                dct_sub['delete_disabled'] = False
                                dct_sub['download_disabled'] = False
                                dct_sub['cat_id'] = list(lst_categories.filter(fk_menu_category__vchr_menu_category_name = dct_sub['vchr_menu_category_name']).values('pk_bint_id'))[0]['pk_bint_id']

                    if ins_sub and (dct_sub['vchr_menu_category_name'] in lst_categories):
                        lst_perms.append({'name':dct_temp['vchr_sub_category_name'],'id':dct_temp['pk_bint_id'], 'items':ins_sub, 'levelTwoClicked':False})

                    if dct_temp['fk_main_category_id'] not in dct_final_perms:
                        dct_final_perms[dct_temp['fk_main_category_id']] = {}
                        dct_final_perms[dct_temp['fk_main_category_id']]['data'] = []
                        dct_final_perms[dct_temp['fk_main_category_id']]['data'] = lst_perms
                        dct_final_perms[dct_temp['fk_main_category_id']]['levelOneClicked'] = False
                        dct_final_perms[dct_temp['fk_main_category_id']]['name'] = dct_temp['fk_main_category_id__vchr_main_category_name']
                    else:
                        dct_final_perms[dct_temp['fk_main_category_id']]['data'].extend(lst_perms)

                dct_company = {
                    'id':int_company_id,
                    # 'code':str_company_code,
                    'name':str_company_name
                }
                return Response({'status':0,'perms':dct_final_perms,'group':str_group_name,'company':dct_company})

        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':1,'data':str(e)})
