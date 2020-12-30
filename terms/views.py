from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny

from datetime import datetime

from .models import Terms,Type

# Create your views here.
class AddType(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            str_type=request.data.get('strType')
            if not Type.objects.filter(vchr_name=str_type):
                Type.objects.create(vchr_name=str_type)
                return Response({'status':1})
            else:
                return Response({'status':0,'reason':'Term type already exists!'})
        except Exception as e:
            return Response({'status':0,'reason':e})
class AddTerms(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:

            jsn_terms = request.data.get('jsnTerms')
            fk_type = request.data.get('fkType')

            if Terms.objects.filter(fk_type_id=fk_type):
                int_id=Terms.objects.filter(fk_type_id=fk_type).values('pk_bint_id').order_by("pk_bint_id").last()['pk_bint_id']
                Terms.objects.filter(pk_bint_id=int_id).update(int_status=0,fk_updated_id=request.user.id,dat_updated=datetime.now())
            Terms.objects.create(jsn_terms=jsn_terms,fk_type_id=fk_type,int_status=1,fk_created_id=request.user.id,dat_created=datetime.now())
            return Response({'status':1})
        except Exception as e:
            return Response({'status':0,'reason':e})


class EditTerms(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            jsn_terms = request.data.get('jsnTerms')
            fk_type = request.data.get('fkType')
            int_status = request.data.get('intStatus')
            int_id=request.data.get('intId')
            Terms.objects.filter(pk_bint_id=int_id).update(jsn_terms=jsn_terms,fk_type=fk_type,int_status=1,fk_updated_id=request.user.id,dat_updated=datetime.now())
        except Exception as e:
            return Response({'status':0,'reason':e})


class ListTerms(APIView):
        permission_classes=[AllowAny]
        def post(self,request):
            try:
                lst_terms=list(Terms.objects.filter(int_status=0).values('fk_type_id','int_status','fk_type__vchr_name','pk_bint_id','dat_created','dat_updated','fk_created','fk_updated'))
                return Response({'status':1,'list':lst_terms})
            except Exception as e:
                return Response({'status':0,'reason':e})

class ViewTerms(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            int_id=request.data.get('intId')
            if Terms.objects.filter(pk_bint_id=int_id):
                lst_terms=list(Terms.objects.filter(pk_bint_id=int_id).values('jsn_terms','fk_type_id','fk_type__vchr_name','pk_bint_id','dat_created','dat_updated','fk_created','fk_updated'))
                return Response({'status':1,'list':lst_terms})
            else:
                return Response({'status':"Doesn't exist"})
        except Exception as e:
            return Response({'status':0})
