# -*- coding: utf-8 -*-

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from item_group.models import ItemGroup
from rest_framework.permissions import IsAuthenticated,AllowAny
import datetime
from django.db.models import Q


######error logg

from POS import ins_logger
import sys, os
class ListItemGroup(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        try:

            if request.data.get('datTo') and request.data.get('datFrom'):
                dat_start=datetime.datetime.strptime(request.data.get('datFrom'),'%d-%m-%Y')
                dat_end=datetime.datetime.strptime(request.data.get('datTo')+" "+'23:59:59','%d-%m-%Y  %H:%M:%S')
                lst_item_group= list(ItemGroup.objects.filter(int_status=0,dat_created__gte=dat_start,dat_created__lte=dat_end).values('vchr_item_group','pk_bint_id').order_by("-dat_created"))
            else:
                lst_item_group= list(ItemGroup.objects.filter(int_status=0).values('vchr_item_group','pk_bint_id').order_by("-dat_created"))

            return Response({'status':1,'lst_item_group':lst_item_group})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
class AddItemGroup(APIView):
    permission_classes= [AllowAny]

    def post(self,request):
        '''Add item group'''
        try:
            str_item_group= request.data.get("vchr_item_group")
            if (ItemGroup.objects.filter(vchr_item_group=str_item_group,int_status=1)):
                        return Response({'status':0,'reason':'Already exists'})
            else:
                ItemGroup.objects.create(vchr_item_group=str_item_group,int_status=0,fk_created_id=request.user.id,dat_created=datetime.datetime.now(), fk_company_id = 1)
                return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def put(self,request):
        '''Edit item group'''
        try:
            str_item_group = request.data.get("item_group")
            pk_bint_id = request.data.get("pk_bint_id")
            if (ItemGroup.objects.filter(vchr_item_group=str_item_group,int_status=0).exclude(pk_bint_id=pk_bint_id)):
                return Response({'status':0,'reason':'Already exists'})
            else:
                ItemGroup.objects.filter(pk_bint_id=pk_bint_id).update(vchr_item_group=str_item_group,fk_updated_id=request.user.id,dat_updated=datetime.datetime.now())
                return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
    def patch(self,request):
        '''delete item group'''
        try:
            pk_bint_id = request.data.get("intId")
            ins_update = ItemGroup.objects.filter(pk_bint_id=pk_bint_id).update(int_status=-1,fk_updated_id=request.user.id,dat_updated=datetime.datetime.now())
            if ins_update:
                return Response({"status":1})
            return Response({'status':0,'reason':'Error in Delete'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class ItemGroupTypeHead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            lst_item_group = []
            if str_search_term != -1:
                ins_item_group = ItemGroup.objects.filter(Q(vchr_item_group__icontains=str_search_term),int_status=0).values('pk_bint_id','vchr_item_group')
                if ins_item_group:
                    for itr_item in ins_item_group:
                        dct_items = {}
                        dct_items['name'] = itr_item['vchr_item_group']
                        dct_items['id'] = itr_item['pk_bint_id']
                        lst_item_group.append(dct_items)
                return Response({'status':1,'data':lst_item_group})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})
