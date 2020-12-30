from django.shortcuts import render
from branch.models import Branch
from tool_settings.models import Tools
from rest_framework.response import Response
from rest_framework.views import APIView
from userdetails.models import Userdetails,GuestUserDetails
from rest_framework.permissions import IsAuthenticated,AllowAny
from POS import ins_logger
import sys, os
import requests
import json

import datetime

class ToolsApi(APIView):
    """
    to add,edit,list,view of tools for pos
    """
    permissions_class = [IsAuthenticated]
    def post(self,request):
        try:
            if not request.data.get('intToolId'):
                return Response({'status':1,'data':{}})

            int_tool_id = request.data.get('intToolId')
            rst_data = Tools.objects.filter(pk_bint_id=int_tool_id).values('pk_bint_id','vchr_tool_name','vchr_tool_code','jsn_data','jsn_keys','dat_from','dat_to')
            dct_data = rst_data.first()
            if dct_data['jsn_data'] and dct_data['vchr_tool_code'] in ['INDIRECT_DISCOUNT','DIRECT_DISCOUNT','ADDITION','DEDUCTION','addition','deduction','ALLOW_SERVICER_PRINT']:
                lst_branch = list(Branch.objects.filter(pk_bint_id__in=dct_data['jsn_data']).values_list('vchr_name',flat=True))
                dct_data['content'] = [str_branch.title() for str_branch in lst_branch]
                if dct_data.get('jsn_keys'):
                    dct_data['additions'] = dct_data.get('jsn_keys')


            return Response({'status':1,'data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
    def get(self,request):
        try:
            rst_data = Tools.objects.filter().values('pk_bint_id','vchr_tool_name','jsn_data','vchr_tool_code','jsn_keys','dat_from','dat_to').order_by('pk_bint_id')
            if not rst_data:
                return Response({'status':0,'message':'No data'})
            if request.user.userdetails.fk_group.vchr_name.upper() not in ['HO','ADMIN']:
                rst_data = rst_data.exclude(vchr_tool_code ='MYG_CARE_NUMBER')


            for ins_tool in rst_data:
                ins_tool['bln_view'] = True
                if not ins_tool['jsn_data']:
                    ins_tool['bln_view'] =False
                else:
                    if ins_tool['vchr_tool_code'] in ['INDIRECT_DISCOUNT','DIRECT_DISCOUNT']:
                        lst_branch = list(Branch.objects.filter(pk_bint_id__in=ins_tool['jsn_data']).values_list('vchr_name',flat=True))
                        ins_tool['content'] = [str_branch.title() for str_branch in lst_branch]
                    elif ins_tool['vchr_tool_code'] in ['ADDITION','DEDUCTION','addition','deduction']:
                        ins_tool['additions'] = ins_tool.get('jsn_keys')
                        lst_branch = list(Branch.objects.filter(pk_bint_id__in=ins_tool.get('jsn_data')).values_list('vchr_name',flat=True))
                        ins_tool['content'] = [str_branch.title() for str_branch in lst_branch]

                        if ins_tool.get('dat_from'):
                            ins_tool['dat_from']=ins_tool.get('dat_from').strftime('%d/%m/%Y')

                        if ins_tool.get('dat_to'):
                            ins_tool['dat_to']=ins_tool.get('dat_to').strftime('%d/%m/%Y')
                    elif ins_tool['vchr_tool_code'] in ['MYG_CARE_NUMBER']:
                        # ins_tool['content'] =  ins_tool.get('jsn_data')
                        pass
                    else:
                        lst_branch = list(Branch.objects.filter(pk_bint_id__in=ins_tool['jsn_data']).values_list('vchr_name',flat=True))
                        ins_tool['content'] = [str_branch.title() for str_branch in lst_branch]


            return Response({'status':1,'data':rst_data})


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def put(self,request):
        try:
            # import pdb;pdb.set_trace()
            vchr_tool_name = request.data.get('strToolName')
            lst_branch = request.data.get('lstBranch')
            int_tool_id = request.data.get('intToolId')
            int_myg_care_num = request.data.get('intNumber')
            # lst_branch = [data['pk_bint_id'] for data in lst_branch if data['blnClicked']]
            if int_myg_care_num:
                Tools.objects.filter(pk_bint_id=int_tool_id).update(
                    jsn_data=int_myg_care_num)

            else:
                Tools.objects.filter(pk_bint_id=int_tool_id).update(
                    vchr_tool_name=vchr_tool_name,
                    jsn_data=lst_branch)


            return Response({'status':1,'message':'Success'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})



class BranchListApi(APIView):
    permissions_class = [IsAuthenticated]
    def get(self,request):
        try:
            lst_branch=list(Branch.objects.filter().values('pk_bint_id','vchr_name').order_by('vchr_name'))
            if lst_branch:
                for ins_branch in lst_branch:
                    ins_branch['vchr_name'] = ins_branch['vchr_name'].title()
            return Response({'status':1,'data':lst_branch})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})



class AddDeductApi(APIView):
    """
    to add,edit,list,view of tools(adddition and deduction) for pos

    """
    permissions_class = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_tool_id = request.data.get('intToolId')
            rst_data = Tools.objects.filter(pk_bint_id=int_tool_id).values('pk_bint_id','vchr_tool_name','vchr_tool_code','jsn_data')

            return Response({'status':1,'data':rst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def put(self,request):
        try:
            # checking whether request contains additions coming from the tool add pages
            if request.data.get('Additions'):
                ins_tools=Tools.objects.filter(vchr_tool_name=request.data.get('strToolName'),jsn_keys=None,jsn_data=None).first()
                if not ins_tools:
                    ins_tools=Tools()
                    ins_tools.vchr_tool_name=request.data.get('strToolName')
                    ins_tools.vchr_tool_code=request.data.get('strToolName')
                if request.data.get('blnUpdate'):
                    ins_tools=Tools.objects.filter(pk_bint_id=request.data.get('intToolId')).first()
                lst_branch=request.data.get('Branches')
                lst_additions=request.data.get('Additions')
                ins_tools.jsn_data=lst_branch
                ins_tools.jsn_keys=lst_additions
                ins_tools.int_status=0
                ins_tools.dat_from=datetime.datetime.strptime(request.data.get('dateFrom'),'%Y-%m-%d')
                ins_tools.dat_to=datetime.datetime.strptime(request.data.get('dateTo'),'%Y-%m-%d')
                ins_tools.save()

            else:

                vchr_tool_name = request.data.get('strToolName')
                int_tool_id = request.data.get('intToolId')
                str_values = request.data.get('strValues')
                if str_values:
                    lst_values = str_values.split(",")
                else:
                    lst_values = None


                Tools.objects.filter(pk_bint_id=int_tool_id).update(
                    vchr_tool_name=vchr_tool_name,
                    jsn_data=lst_values)

            return Response({'status':1,'message':'Success'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
