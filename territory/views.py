from rest_framework.response import Response
from rest_framework.views import APIView
from territory.models import Territory
from rest_framework.permissions import IsAuthenticated,AllowAny
from POS import ins_logger
import traceback
import sys, os
class TerritoryList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            if request.data.get('intZoneId'):
                lst_territory = list(Territory.objects.filter(bln_active = True,fk_zone_id = int(request.data.get('intZoneId')) ).values('pk_bint_id','vchr_name'))
            else:
                lst_territory = list(Territory.objects.filter(bln_active = True ).values('pk_bint_id','vchr_name'))

            return Response({'status':1,'lst_territory':lst_territory})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':e})
