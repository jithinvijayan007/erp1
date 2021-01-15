from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import authentication, permissions
from priority.models import Priority
from django.db.models import Q
from enquiry.models import EnquiryMaster

# Create your views here.


class PriorityAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request,):
        try:
            import pdb; pdb.set_trace()
            id = int(request.GET.get('id',0))
            if id > 0:
                lst_priority = list(Priority.objects.filter(pk_bint_id = id,bln_status=True).values('vchr_priority_name'))
            else:
                lst_priority = list(Priority.objects.filter(bln_status=True).values('vchr_priority_name','pk_bint_id').order_by('pk_bint_id'))
            return Response(lst_priority)

        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

    def post(self, request,):
        try:
            str_name = request.data['vchr_name'].upper()
            ins_name = Priority.objects.filter(vchr_priority_name = str_name,bln_status=True)
            in_count=Priority.objects.filter(bln_status=True).count()
            if in_count>=7:
                return JsonResponse({'status':'failed','reason':'Reached maximum number of enquiry sources. Please contact:support@enquirytrack.com'})
            elif ins_name:
                return JsonResponse({'status':'failed','reason':'Name already exist'})
            else:
                ins_priority = Priority(vchr_priority_name = str_name,bln_status=True)
                ins_priority.save()
                return JsonResponse({'status':'success'})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

    def patch(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_id = int(request.data['id'])
            str_name = request.data['vchr_name'].upper()

            ins_name = Priority.objects.filter(~Q(pk_bint_id=int_id) & Q(bln_status=True) & Q(vchr_priority_name = str_name))

            if not ins_name:
                Priority.objects.filter(pk_bint_id = int_id,bln_status=True).update(vchr_priority_name = str_name)
                return JsonResponse({'status':'success'})
            else:
                return JsonResponse({'status':'failed','reason':'Name already exist'})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

class PriorityDeleteAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request,):
        try:
            int_id = request.data['id']
            ins_priority = EnquiryMaster.objects.filter(chr_doc_status='N',fk_priority_id = int_id)
            if not ins_priority:
                ins_priority = Priority.objects.filter(pk_bint_id = int_id).update(bln_status=False)
                return JsonResponse({'status':'success','result':'Status changed successfully'})
            else:
                return JsonResponse({'status':'failed', 'reason': 'This enquiry priority has already been involved in transactions or this is the default enquiry priority of the company. Cannot be deleted.'})
        except Exception as e:
            return Response({'result':'failed'})
