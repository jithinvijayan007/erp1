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
#from expenses.models import ExpensesCategory

# Create your views here.


class SourceAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request,):
        try:
            id = int(request.GET.get('id',0))
            if id > 0:
                lst_source = list(Source.objects.filter(pk_bint_id = id,bln_status=True).values('vchr_source_name','bln_is_campaign'))
            else:
                lst_source = list(Source.objects.filter(bln_status=True,fk_company=request.user.userdetails.fk_company).values('vchr_source_name','pk_bint_id').order_by('pk_bint_id'))
                # lst_source = list(Source.objects.filter(bln_status=True,fk_company=request.user.userdetails.fk_company).values('vchr_source_name','pk_bint_id','fk_category','fk_category__vchr_category_name').order_by('pk_bint_id'))
            return Response(lst_source)

        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

    def post(self, request,):
        try:
            int_company = request.user.userdetails.fk_company_id
            in_count=Source.objects.filter(bln_status=True,fk_company=int_company).count()
            str_name = request.data['vchr_name'].upper()
            ins_name = Source.objects.filter(vchr_source_name = str_name,bln_status=True,fk_company=int_company)
            if in_count>=7:
                return JsonResponse({'status':'failed','reason':'Reached maximum number of enquiry sources. Please contact:support@enquirytrack.com'})
            elif ins_name:
                return JsonResponse({'status':'failed','reason':'Name already exist'})
            else:
                #if request.data.get('category_id'):
                    #int_category_id = int(request.data.get('category_id'))
                    #ins_source = Source(vchr_source_name = str_name,fk_category=ExpensesCategory.objects.get(pk_bint_id=int_category_id),bln_status=True,bln_is_campaign=request.data['bln_is_campaign'],fk_company_id = int_company)
                #else:
                ins_source = Source(vchr_source_name = str_name,bln_status=True,bln_is_campaign=request.data['bln_is_campaign'],fk_company_id = int_company)
                ins_source.save()
                return JsonResponse({'status':'success'})
        except Exception as e:
            return JsonResponse({'status':'failed','reason':e})

    def patch(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_id = int(request.data['id'])
            str_name = request.data['vchr_name'].upper()
            #category=ExpensesCategory.objects.get(pk_bint_id=int(request.data.get('category_id')))

            ins_name = Source.objects.filter(~Q(pk_bint_id=int_id) & Q(bln_status=True) & Q(vchr_source_name = str_name) & Q(fk_company = request.user.userdetails.fk_company))

            if not ins_name:
                Source.objects.filter(pk_bint_id = int_id,bln_status=True).update(vchr_source_name = str_name,bln_is_campaign=request.data['bln_is_campaign'])
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
