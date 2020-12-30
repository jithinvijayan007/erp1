from django.shortcuts import render

# Create your views here.
from hierarchy.models import Hierarchy,HierarchyData

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db.models import Value, BooleanField
from django.conf import settings
from userdetails.models import Userdetails
import datetime
from django.db.models import Q
import traceback
######error logg

from POS import ins_logger
import sys, os


class AddHierarchyApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        try:
            """add hierarchy"""
            vchr_country_name = request.data.get('vchrCountryName')
            vchr_country_code = request.data.get('vchrCountryCode')
            vchr_zone_name = request.data.get('vchrZoneName')
            vchr_zone_code = request.data.get('vchrZoneCode')
            vchr_zone_country = request.data.get('vchrZoneCountry')
            vchr_state_name = request.data.get('vchrStateName')
            vchr_state_code = request.data.get('vchrStateCode')
            vchr_state_zone = request.data.get('vchrStateZone')
            vchr_teritory_name = request.data.get('vchrTeritoryName')
            vchr_teritory_code = request.data.get('vchrTeritoryCode')
            vchr_teritory_state = request.data.get('vchrTeritoryState')
            vchr_district_name = request.data.get('vchrDistrictName')
            vchr_district_code = request.data.get('vchrDistrictCode')
            vchr_district_teritory = request.data.get('vchrDistrictTeritory')
            vchr_branch_name = request.data.get('vchrBranchName')
            vchr_branch_code = request.data.get('vchrBranchCode')
            vchr_branch_district = request.data.get('vchrBranchDistrict')
            vchr_floor_name = request.data.get('vchrFloorName')
            vchr_floor_code = request.data.get('vchrFloorCode')
            vchr_floor_branch = request.data.get('vchrFloorBranch')
            vchr_team_name = request.data.get('vchrTeamName')
            vchr_team_code = request.data.get('vchrTeamCode')
            vchr_team_floor = request.data.get('vchrTeamFloor')
            if vchr_country_name:
                ins_country = HierarchyData.objects.filter(vchr_name = vchr_country_name).values()
                if ins_country:
                    return Response({'status':0,'data':'Country Already Exist'})
                else:
                    ins_country_data = HierarchyData.objects.create(vchr_name = vchr_country_name,vchr_code = vchr_country_code,fk_hierarchy_id = 8)
                    ins_country_data.save()
            elif vchr_zone_name:
                ins_country = HierarchyData.objects.filter(vchr_name = vchr_zone_country).values('pk_bint_id').first()
                ins_zone = HierarchyData.objects.filter(vchr_name = vchr_zone_name).values()
                if ins_zone:
                    return Response({'status':0,'data':'Zone Already Exist'})
                else:
                    ins_zone_data = HierarchyData.objects.create(vchr_name = vchr_zone_name,vchr_code = vchr_zone_code,fk_hierarchy_id = 7,fk_hierarchy_data_id = ins_country['pk_bint_id'])
                    ins_zone_data.save()
            elif vchr_state_name:
                ins_zone = HierarchyData.objects.filter(vchr_name = vchr_state_zone).values('pk_bint_id').first()
                ins_state = HierarchyData.objects.filter(vchr_name = vchr_state_name).values()
                if ins_state:
                    return Response({'status':0,'data':'State Already Exist'})
                else:
                    ins_state_data = HierarchyData.objects.create(vchr_name = vchr_state_name,vchr_code = vchr_state_code,fk_hierarchy_id = 6,fk_hierarchy_data_id = ins_zone['pk_bint_id'])
                    ins_state_data.save()
            elif vchr_teritory_name:
                ins_state = HierarchyData.objects.filter(vchr_name = vchr_teritory_state).values('pk_bint_id').first()
                ins_teritory = HierarchyData.objects.filter(vchr_name = vchr_teritory_name).values()
                if ins_teritory:
                    return Response({'status':0,'data':'State Already Exist'})
                else:
                    ins_teritory_data = HierarchyData.objects.create(vchr_name = vchr_teritory_name,vchr_code = vchr_teritory_code,fk_hierarchy_id = 5,fk_hierarchy_data_id = ins_state['pk_bint_id'])
                    ins_teritory_data.save()
            elif vchr_district_name:
                ins_teritory = HierarchyData.objects.filter(vchr_name = vchr_district_teritory).values('pk_bint_id').first()
                ins_district = HierarchyData.objects.filter(vchr_name = vchr_district_name).values()
                if ins_district:
                    return Response({'status':0,'data':'State Already Exist'})
                else:
                    ins_district_data = HierarchyData.objects.create(vchr_name = vchr_district_name,vchr_code = vchr_district_code,fk_hierarchy_id = 4,fk_hierarchy_data_id = ins_teritory['pk_bint_id'])
                    ins_district_data.save()
            elif vchr_branch_name:
                ins_district = HierarchyData.objects.filter(vchr_name = vchr_branch_district).values('pk_bint_id').first()
                ins_branch = HierarchyData.objects.filter(vchr_name = vchr_branch_name).values()
                if ins_branch:
                    return Response({'status':0,'data':'State Already Exist'})
                else:
                    ins_branch_data = HierarchyData.objects.create(vchr_name = vchr_branch_name,vchr_code = vchr_branch_code,fk_hierarchy_id = 3,fk_hierarchy_data_id = ins_district['pk_bint_id'])
                    ins_branch_data.save()
            elif vchr_floor_name:
                ins_branch = HierarchyData.objects.filter(vchr_name = vchr_floor_branch).values('pk_bint_id').first()
                ins_floor = HierarchyData.objects.filter(vchr_name = vchr_floor_name).values()
                if ins_floor:
                    return Response({'status':0,'data':'State Already Exist'})
                else:
                    ins_floor_data = HierarchyData.objects.create(vchr_name = vchr_floor_name,vchr_code = vchr_floor_code,fk_hierarchy_id = 2,fk_hierarchy_data_id = ins_branch['pk_bint_id'])
                    ins_floor_data.save()
            elif vchr_team_name:
                ins_floor = HierarchyData.objects.filter(vchr_name = vchr_team_floor).values('pk_bint_id').first()
                ins_team = HierarchyData.objects.filter(vchr_name = vchr_team_name).values()
                if ins_team:
                    return Response({'status':0,'data':'State Already Exist'})
                else:
                    ins_team_data = HierarchyData.objects.create(vchr_name = vchr_team_name,vchr_code = vchr_team_code,fk_hierarchy_id = 1,fk_hierarchy_data_id = ins_floor['pk_bint_id'])
                    ins_team_data.save()
            else:
                return Response({'status':1,'data':'Failed'})

            return Response({'status':1,'data':'Success'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
