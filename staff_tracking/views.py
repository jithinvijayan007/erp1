import pdb
from django.db.models.aggregates import Sum
from django.db.models.expressions import Value
from django.shortcuts import render
from rest_framework import request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from userdetails.models import UserLogDetails
from datetime import date
from django.db.models import F,Func,CharField,Value
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import ArrayAgg

# Create your views here.
class User_Track_list(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_from = request.data.get("datFrom")
            dat_To = request.data.get("datTo")
            lst_branch = request.data.get("lstBranch") or []
            int_user = request.data.get("intUser") or 0
            dct_filter = {}
            # lst_filter = ["fk_user__first_name","fk_user__last_name","fk_module__vchr_module_name","dat_last_active","fk_user__userdetails__fk_branch__vchr_name"]
            lst_filter = ["Name","module_name","last_active","branch_name","strDate","strTime"]
            if dat_from:
                dct_filter['dat_last_active__date__gte'] =  dat_from
            if dat_To:
                dct_filter['dat_last_active__date__lte'] =  dat_To

            if lst_branch:
                dct_filter['fk_user__userdetails__fk_branch_id__in'] = lst_branch

            if int_user:
                dct_filter['fk_user_id'] = int_user

            # ins_data = UserLogDetails.objects.filter(fk_user__userdetails__fk_branch_id__in = [20]).values("fk_user__first_name","fk_user__last_name","fk_user__userdetails__fk_branch__vchr_name","fk_module__vchr_module_name","fk_user__id").annotate(count = Sum('int_count'))
            ins_data = UserLogDetails.objects.filter(**dct_filter).values("fk_user__first_name","fk_user__last_name","fk_user__userdetails__fk_branch__vchr_name","fk_user__userdetails__fk_group__vchr_name","fk_module__vchr_module_name","fk_user__id","dat_last_active").annotate(count = Sum('int_count'),Date = Func(F("dat_last_active"),Value('dd-MM-yyyy'),function='to_char', output_field=CharField() ))
            dct_res = {}
            # import pdb; pdb.set_trace()
            for data in ins_data:
                dict_person_data = {}
                dict_login_det = {}
                # lst_details =[]
                if dct_res.get(data['fk_user__id']):
                    dict_login_det["Module"] = data["fk_module__vchr_module_name"]
                    dict_login_det["Count"] = data["count"]
                    dict_login_det["Date"] = data["Date"]

                    dct_res[data['fk_user__id']]["lst_log_data"].append(dict_login_det)
                    
                else:
                    dict_login_det["Module"] = data["fk_module__vchr_module_name"]
                    dict_login_det["Count"] = data["count"]
                    dict_login_det["Date"] = data["Date"]

                    dict_person_data['name'] = data['fk_user__first_name'] +" "+ data['fk_user__last_name']
                    dict_person_data['branch'] = data['fk_user__userdetails__fk_branch__vchr_name']
                    dict_person_data['group'] = data['fk_user__userdetails__fk_group__vchr_name']

                    dict_person_data['lst_log_data'] = [dict_login_det]

                    dct_res[data['fk_user__id']] = dict_person_data

            
            # import pdb; pdb.set_trace() 
            lst_data  = list(dct_res.values())
            return Response({"status":1,'data':lst_data})

        except Exception as e:
            return Response({"status":0,'reason':e})

# PriceList.objects.annotate(vchr_item_name=Concat('fk_item__vchr_item_code', Value('-'), 'fk_item__vchr_name'),
#                                               str_formatted_date=Func( F('dat_efct_from'), Value('dd-MM-yyyy'), function='to_char', output_field=CharField() ))

# ins_data = UserLogDetails.objects.filter(fk_user__userdetails__fk_branch_id__in = [20]).annotate(data_ =  Value(F("dat_last_active"),output_field = CharField())).values("fk_user__first_name","fk_user__userdetails__fk_branch__vchr_name","data_")
# ins_data = UserLogDetails.objects.filter(fk_user__userdetails__fk_branch_id__in = [20]).annotate(data_ =  Value(F("dat_last_active"),output_field = CharField())).values("fk_user__first_name","fk_user__userdetails__fk_branch__vchr_name","data_")
# ins_data = UserLogDetails.objects.filter(fk_user__userdetails__fk_branch_id__in = [20]).values("fk_user__first_name","fk_user__userdetails__fk_branch__vchr_name","fk_module__vchr_module_name").aggregate(name = ArrayAgg(Concat(Value("staff:"),F("fk_user__first_name"))))
# [{name:"fahad":branch:"SABA",data:[{},{},{}]}]



# ins_data = UserLogDetails.objects.filter(fk_user__userdetails__fk_branch_id__in = [20]).values("fk_user__first_name","fk_user__userdetails__fk_branch__vchr_name").annotate(name = ArrayAgg(Concat(Value("{'staff':"),F("fk_module__vchr_module_name"),Value(",'date':"),F('dat_last_active'),Value("}"),output_field = CharField())))
# ins_data = UserLogDetails.objects.filter(fk_user__userdetails__fk_branch_id__in = [20]).values("fk_user__first_name","fk_user__userdetails__fk_branch__vchr_name").annotate(name = ArrayAgg(Concat(Value("{'Module':"),F("fk_module__vchr_module_name"),Value(",'count':"),Sum('int_count'),Value("}"),output_field = CharField())))




