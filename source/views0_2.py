from django.shortcuts import render
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import authentication, permissions
from source.models import Source
from django.db.models import Q
from enquiry.models import EnquiryMaster

# Create your views here.


class SourceAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request,):
        try:
            id = int(request.GET.get('id',0))
            if id > 0:
                lst_source = list(Source.objects.filter(pk_bint_id = id,bln_status=True).values('vchr_source_name'))
            else:
                lst_source = list(Source.objects.filter(bln_status=True).values('vchr_source_name','pk_bint_id').order_by('pk_bint_id'))
            return Response(lst_source)

        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

    def post(self, request,):
        try:
            in_count=Source.objects.filter(bln_status=True).count()
            str_name = request.data['vchr_name'].upper()
            ins_name = Source.objects.filter(vchr_source_name = str_name,bln_status=True)
            if in_count>=7:
                return JsonResponse({'status':'failed','reason':'Reached maximum number of enquiry sources. Please contact:support@enquirytrack.com'})
            elif ins_name:
                return JsonResponse({'status':'failed','reason':'Name already exist'})
            else:
                ins_source = Source(vchr_source_name = str_name,bln_status=True)
                ins_source.save()
                return JsonResponse({'status':'success'})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

    def patch(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_id = int(request.data['id'])
            str_name = request.data['vchr_name'].upper()

            ins_name = Source.objects.filter(~Q(pk_bint_id=int_id) & Q(bln_status=True) & Q(vchr_source_name = str_name))

            if not ins_name:
                Source.objects.filter(pk_bint_id = int_id,bln_status=True).update(vchr_source_name = str_name)
                return JsonResponse({'status':'success'})
            else:
                return JsonResponse({'status':'failed','reason':'Name already exist'})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

class SourceDeleteAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request,):
        try:
            int_id = request.data['id']
            ins_source = EnquiryMaster.objects.filter(chr_doc_status='N',fk_source_id = int_id)
            if not ins_source:
                ins_source = Source.objects.filter(pk_bint_id = int_id).update(bln_status=False)
                return JsonResponse({'status':'success','result':'Status changed successfully'})
            else:
                return JsonResponse({'status':'failed', 'reason': 'This enquiry source has already been involved in transactions or this is the default enquiry source of the company. Cannot be deleted.'})
        except Exception as e:
            return Response({'result':'failed'})
