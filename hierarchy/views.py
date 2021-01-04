from django.db.models.expressions import Value
from django.http import response
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from hierarchy.models import Hierarchy,HierarchyData,HierarchyGroups
from django.db.models import Q,Case, When,CharField
from django.db.models.functions import Concat
from POS  import ins_logger
import sys
class HierarchyApi(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_hierar_name = request.GET['hierarchy_name']
            ins_top_hierar = Hierarchy.objects.latest('int_level')     
            if ins_top_hierar.vchr_name.upper() == str_hierar_name.upper():
                return Response({'status':1,'data':[]})
            else:
                dct_hierar = Hierarchy.objects.filter(vchr_name__iexact = str_hierar_name).values().first()
                int_level = int(dct_hierar['int_level']) + 1
                dct_hierar = HierarchyData.objects.filter(fk_hierarchy__int_level = int_level).annotate(str_name=Case(When(fk_hierarchy_data_id__vchr_name = None ,then =  'vchr_name'),default =Concat('vchr_name', Value('-'), 'fk_hierarchy_data_id__vchr_name'),output_field = CharField())).values('pk_bint_id','str_name','vchr_code','fk_hierarchy_id','fk_hierarchy_data_id')
                return Response({'status':1,'data':dct_hierar})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':str(e)})


    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_hierar_name = request.data['hierarchy_name']
            str_name = request.data['vchr_name'].upper()     
            str_code = request.data['vchr_code'].upper()
            int_fk_master =   request.data.get('master_id')  
            ins_hierarchydataCheck =  HierarchyData.objects.filter(Q(vchr_name = str_name) | (Q(vchr_code = str_code) & Q(fk_hierarchy_data_id = int_fk_master ))).values()
            if ins_hierarchydataCheck:
                return Response ({'status':0,'reason':'Hierarchy Name or Code Already Exist'})
            int_hierarchy = Hierarchy.objects.get(vchr_name__iexact = str_hierar_name)

            ins_hierarchydata = HierarchyData(
                vchr_name = str_name,
                vchr_code = str_code,
                fk_hierarchy_id = int_hierarchy.pk_bint_id,
                fk_hierarchy_data_id = int_fk_master
            )
            ins_hierarchydata.save()
            return Response({'status':1,'data':'successfully added'})
            # if ins_top_hierar.vchr_name.upper() == str_hierar_name.upper():

                # )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':str(e)})

class Levels(APIView):

    permission_classes = [AllowAny]
    def get(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_level_name = request.GET.get('hierarchy_name')
            if str_level_name:
                dct_hierar = HierarchyData.objects.filter(fk_hierarchy__vchr_name = str_level_name).annotate(str_name=Case(When(vchr_name = None ,then =  'vchr_name'),default =Concat('vchr_name', Value(' - '), 'fk_hierarchy_data__vchr_name'),output_field = CharField())).values('pk_bint_id','str_name','vchr_code','fk_hierarchy_id','fk_hierarchy_data_id')
            else:
                dct_hierar = Hierarchy.objects.all().values()
            return Response({'status':1,'data':dct_hierar})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':str(e)})

# class GetHierarchy(APIView):
#     permission_classes = (IsAuthenticated,)
#     def get(self,request):
#         try:
#             int_department = request.GET.get('int_department')
#             lst_hierarchy = list(LevelHierarchy.objects.filter(fk_department = int_department,bln_active = True).values('pk_bint_id','json_group','vchr_filter','fk_department','int_level').order_by('pk_bint_id'))

#             lst_filter = []
#             lst_filter_group = []
#             if not lst_hierarchy:
#                 return JsonResponse({'status':'success', 'data':'No data'})
#             for dct_data in lst_hierarchy:
#                 lst_groups = []
#                 dct_filter = {}
#                 dct_filter['id'] = dct_data['pk_bint_id']
#                 dct_filter['GroupsId'] = dct_data['json_group']['groups']
#                 dct_filter['level_id'] = dct_data['int_level']
#                 dct_filter['selectedFilter'] = dct_data['vchr_filter']


#                 for int_group in dct_data['json_group']['groups']:
#                     dct_groups = {}
#                     rst_group_data = Groups.objects.filter(pk_bint_id = int_group,bln_status = True).values('vchr_name')
#                     if not rst_group_data:
#                         continue

#                     dct_groups['pk_bint_id'] = int_group
#                     dct_groups['vchr_name'] = rst_group_data.first()['vchr_name']
#                     lst_groups.append(dct_groups)
#                     lst_filter_group.append(int_group)

#                 dct_filter['Groups'] = lst_groups
#                 lst_filter.append(dct_filter)

#             return JsonResponse({'status':'success','data':lst_filter,'filter':lst_filter_group})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'result':0,'reason':str(e)})


class HierarchyGroup(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            dep_id = request.GET.get('dept_id')
            hierarchy_id = request.GET.get('hierar_id')
            dct_filter = {}
            if dep_id:
                dct_filter['fk_hierarchy__fk_department_id'] = dep_id
            if hierarchy_id:
                dct_filter['fk_hierarchy_id'] = hierarchy_id
            dct_data = HierarchyGroups.objects.filter(**dct_filter).values()
            return Response({"status":1,"data":dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':str(e)})
    
    def post(self,request):
        try:
            dct_data = request.data['data']
            dep_id = request.data['dept_id']
            dct_hierrachy_level = Hierarchy.objects.filter(fk_department = dep_id).values()
            dct_hierrachy_level = { data['vchr_name']:data for data in dct_hierrachy_level}
            for level in dct_data:
                for data in dct_data[level]:
                    HierarchyGroups.objects.create(
                        fk_hierarchy_id = dct_hierrachy_level[level]['pk_bint_id'],
                        vchr_name = data,
                        int_status = 1
                    )
            return Response({"status":1,"data":'success'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':str(e)})

class GetHierarchyGroup(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dep_id = request.data.get('dept_id')
            hierarchy_id = request.data.get('hierar_id')
            dct_filter = {}
            if dep_id:
                dct_filter['fk_hierarchy__fk_department_id'] = dep_id
            if hierarchy_id:
                dct_filter['fk_hierarchy_id'] = hierarchy_id
            dct_data = HierarchyGroups.objects.filter(**dct_filter).values()
            return Response({"status":1,"data":dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':str(e)})
