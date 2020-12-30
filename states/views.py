from django.shortcuts import render

# Create your views here.
# -*- coding: utf-8 -*-
from django.shortcuts import render
from states.models import States

from rest_framework.response import Response
from rest_framework.views import APIView
from states.models import States,Location
from rest_framework.permissions import IsAuthenticated,AllowAny
import datetime
from django.db.models import Q
import traceback
######error logg

from POS import ins_logger
import sys, os


# class StatesTypeHead(APIView):
#     permission_classes = [AllowAny]
#     def post(self,request):
#         try:
#
#             str_search_term = request.data.get('term',-1)
#             lst_state = []
#             if str_search_term != -1:
#
#                 ins_brand = States.objects.filter(vchr_name__icontains=str_search_term).values('pk_bint_id','vchr_name')
#                 if ins_brand:
#                     for itr_item in ins_brand:
#                         dct_state = {}
#                         dct_state['name'] = itr_item['vchr_name']
#                         dct_state['id'] = itr_item['pk_bint_id']
#                         lst_state.append(dct_state)
#                 return Response({'status':1,'data':lst_state})
#
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#             return Response({'result':0,'reason':e})




class StatesTypeahead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            str_search_term = request.data.get('term')
            list_states = []
            if str_search_term:
                list_states = list(States.objects.filter(Q(vchr_name__icontains=str_search_term)|Q(vchr_code__icontains=str_search_term)).values('pk_bint_id','vchr_name','vchr_code'))
            return Response({'status':1,'list_states':list_states})


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def get(self,request):
        try:
            list_states = list(States.objects.values('pk_bint_id','vchr_name','vchr_code'))
            return Response({'status':1,'list_states':list_states})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})



class DistrictTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term')
            list_district=[]
            if str_search_term:
                list_district = list(District.objects.filter(vchr_name__icontains=str_search_term).values('pk_bint_id','vchr_name'))

            return Response({'status':1,'list_states':list_district})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class LocationTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data.get('term')
            list_location=[]
            if str_search_term:
                list_location = list(Location.objects.filter(Q(vchr_name__icontains=str_search_term)|Q(vchr_pin_code__icontains=str_search_term)).values('pk_bint_id','vchr_name','vchr_pin_code'))

            return Response({'status':1,'list_states':list_location})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
