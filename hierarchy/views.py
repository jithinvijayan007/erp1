from django.db.models.expressions import Value
from django.http import response
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from hierarchy.models import Hierarchy,HierarchyData
from django.db.models import Q,Case, When,CharField
from django.db.models.functions import Concat
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
            return Response ({'status':0,'reason':e})


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
            return Response ({'status':0,'reason':e})

