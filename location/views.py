
from rest_framework.response import Response
from rest_framework.views import APIView
from zone.models import Zone
from rest_framework.permissions import IsAuthenticated,AllowAny
from location.models import PhysicalLocation,Country,District
from states.models import States as State
# from location.models import Location
from POS import ins_logger
import traceback
import sys, os
class StatesList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            lst_state = list(State.objects.values('pk_bint_id','vchr_name').order_by('vchr_name'))

            return Response({'status':1,'lst_state':lst_state})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':e})

class PhysicalLocationList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            if not request.user.is_superuser and request.user.userdetails.fk_department.vchr_name.upper() == 'SALES':
                lst_loc = list(PhysicalLocation.objects.filter(pk_bint_id=request.user.userdetails.json_physical_loc).values('pk_bint_id','vchr_physical_loc').order_by('vchr_physical_loc'))
            else:
                lst_loc = list(PhysicalLocation.objects.values('pk_bint_id','vchr_physical_loc').order_by('vchr_physical_loc'))

            return Response({'status':1,'lst_loc':lst_loc})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':e})


class CountryList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            lst_country = list(Country.objects.values('pk_bint_id','vchr_name').order_by('vchr_name'))

            return Response({'status':1,'lst_country':lst_country})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':e})

class StateListNew(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_country_id = request.data.get('intCountryId')
            if int_country_id:
                lst_state = list(State.objects.filter(fk_country_id = int(int_country_id) ).values('pk_bint_id','vchr_name').order_by('vchr_name'))
            else:
                lst_state = list(State.objects.values('pk_bint_id','vchr_name').order_by('vchr_name'))
                
            return Response({'status':1,'lst_state':lst_state})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':e})

class DistrictList(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_state_id = request.data.get('intStateId')
            if int_state_id:
                lst_district = list(District.objects.filter(fk_state_id = int(int_state_id) ).values('pk_bint_id','vchr_name').order_by('vchr_name'))
            else:
                lst_district = list(District.objects.values('pk_bint_id','vchr_name').order_by('vchr_name'))

            return Response({'status':1,'lst_district':lst_district})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':e})

# class Location(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         try:
#             vchr_pin_code = request.GET['query']
#             lst_pin_code = Location.objects.filter(vchr_pin_code = vchr_pin_code).values()
#             return Response({'status':1, 'lst_pin_code':lst_pin_code})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':0,'reason':e})