from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from group_level.models import GroupLevel
from groups.models import Groups
from rest_framework.permissions import AllowAny
from django.db.models import Q
# from CRM import ins_logger
# Create your views here.
class GetGroupforLevel(APIView):
    """Group for level"""
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            level_group={i:{'group':[],'filter':''} for i in range(1,16)}
            lst_total_group = Groups.objects.values_list('vchr_name',flat=True)
            ins_data=GroupLevel.objects.values('fk_group__vchr_name','vchr_filter','int_level').order_by('int_level')
            for data in ins_data :
                level_group[data['int_level']]['group'].append(data['fk_group__vchr_name'])
                level_group[data['int_level']]['filter']=data['vchr_filter']
            dct_data={'total_group':lst_total_group,'lst_exist':level_group}
            return Response({'status':'success','data':dct_data})
        except Exception as e:
            logger.error('Something went wrong!')
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
        # except Exception as e:
        #     return Response({'result':'failed','reason':e})

class SaveGroupLevel(APIView):
    """Saving level for Group"""
    def post(self,request):
        try:
            lst_groups=[]
            dct_data=request.data
            for dct_key in dct_data:
                for lst_dt in dct_data[dct_key]['group']:
                    lst_groups.append(lst_dt)
                    ins_exist=GroupLevel.objects.filter(fk_group__vchr_name=lst_dt)
                    if ins_exist:
                        ins_exist.update(int_level=int(dct_key),vchr_filter=dct_data[dct_key]['filter'])
                    else:
                        ins_group_level=GroupLevel(fk_group=Groups.objects.filter(vchr_name=lst_dt).first(),int_level=int(dct_key),vchr_filter=dct_data[dct_key]['filter'])
                        ins_group_level.save()
            GroupLevel.objects.filter(~Q(fk_group__vchr_name__in=lst_groups)).delete()
            # lst_not_group.extend(dct_data[dct_key])
            # Groups.objects.filter(vchr_name__in=dct_data[dct_key]).update(int_level=int(dct_key))
            # Groups.objects.exclude(vchr_name__in=lst_not_group).update(int_level=0)
            return Response({'status':'success'})
        except Exception as e:
            return Response({'result':'failed','reason':e})
