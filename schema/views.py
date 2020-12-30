from django.shortcuts import render
from invoice.models import FinanceScheme
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from datetime import datetime,time
from django.conf import settings
import requests
# Create your views here.

# LG
class addScheme(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dat_date_from = request.data.get('datFrom') or datetime.strftime(datetime.now(),'%Y-%m-%d')
            dat_date_to = request.data.get('datTo') or datetime.strftime(datetime.now(),'%Y-%m-%d')
            str_scheme = request.data.get('scheme')
            ins_scheme_exists = FinanceScheme.objects.filter(vchr_schema=str_scheme)
            if ins_scheme_exists:
                return Response({'status': 0,'message':'Scheme already exists'})

            if request.data.get('scheme'):
                dct_data = {}
                dct_data['datFrom'] = str(dat_date_from)
                dct_data['datTo'] = str(dat_date_to)
                dct_data['strScheme'] = request.data['scheme']
                url = settings.BI_HOSTNAME+"/schema/AddSchemapos/"
                try:
                    res_data = requests.post(url,json=dct_data)
                    if res_data.json().get('status')==1:
                        pass
                    else:
                        return Response({"status" : 0,"message" : "Unable to add Scheme! please Try again.."})
                except Exception as e:
                    return Response({'status':'failed','message':'Some Thing happined in BI'})

            ins_scheme = FinanceScheme.objects.create(vchr_schema = str_scheme,dat_from = dat_date_from,dat_to = dat_date_to)
            ins_scheme.save()
            if ins_scheme:
                return Response({"status" : 1,"message" : "Success"})
            else:
                return Response({"status" : 0,"message" : "Unable to add Scheme! please Try again.."})
        except Exception as e:
            return Response({"status" : 0,"message" : "Some Thing Went Wrong! please Try again.."+str(e)})
    def get(self,request):
        try:
            """ List """
            lst_schema = FinanceScheme.objects.values('pk_bint_id','vchr_schema','dat_from','dat_to').order_by('-pk_bint_id')
            lst_data = []
            for data in lst_schema:
                dct_data = {}
                dct_data['pk_bint_id'] = data['pk_bint_id']
                dct_data['vchr_schema'] = data['vchr_schema']
                dct_data['dat_from'] = datetime.strftime(data['dat_from'],'%d-%m-%Y')
                dct_data['dat_to'] = datetime.strftime(data['dat_to'],'%d-%m-%Y') if data['dat_to'] else None
                lst_data.append(dct_data)
            return Response({'status':'1','data':lst_data})
        except Exception as e:
            return Response({'status':'1','data':[str(e)]})


# LG
class addSchemefrombi(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dat_date_from = request.data.get('datFrom').split(' ')[0] or datetime.strftime(datetime.now(),'%Y-%m-%d')
            dat_date_to = request.data.get('datTo').split(' ')[0] or datetime.strftime(datetime.now(),'%Y-%m-%d')
            str_scheme = request.data.get('strScheme')
            ins_scheme = FinanceScheme.objects.create(vchr_schema = str_scheme,dat_from = dat_date_from,dat_to = dat_date_to)
            ins_scheme.save()
            if ins_scheme:
                return Response({"status" : 1,"message" : "Success"})
            else:
                return Response({"status" : 0,"message" : "Unable to add Scheme! please Try again.."})
        except Exception as e:
            return Response({"status" : 0,"message" : "Some Thing Went Wrong! please Try again.."+str(e)})
