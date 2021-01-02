from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from user_model.models import UserDetails
from url_check.models import SessionHandler
from django.db.models import Case, CharField, Value, When,Q
from django.db.models import F
from group_permission.models import GroupPermissions
from company_permission.models import MenuCategory,CategoryItems
from POS import ins_logger
import traceback
import sys, os
class OneSessionPerUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            bln_logout = False
            bln_per = False
            vchr_current_url = request.data.get('url')
            # import pdb; pdb.set_trace()

            # import pdb; pdb.set_trace()
            ins_session_handler = SessionHandler.objects.filter(fk_user_id  = request.user.id).values('vchr_session_key').first()
            #checking the stored session key and current session key are same or not.
            if ins_session_handler and ins_session_handler['vchr_session_key'] != request.data["strSessionKey"]:
                bln_logout = True
            if request.user.is_superuser:
                return Response({'status':1,'bln_per':True,'bln_logout': bln_logout})
            # ins_user = UserDetails.objects.get(user_ptr_id = request.user.id)
            # ins_perm = GroupPermissions.objects.filter(fk_desig = ins_user.fk_desig,fk_category_items = ins_category_items.pk_bint_id, bln_view = True)
            # if ins_perm:
            #     return Response({'status':1,'bln_per':True,'bln_logout':bln_status})
            # else:
            #     return Response({'status':1,'bln_per':True, 'bln_logout':bln_status})
            int_desig_id = request.user.userdetails.fk_desig_id
            int_company_id = request.user.userdetails.fk_company_id
            ins_menu_category = MenuCategory.objects.filter(Q(Q(vchr_addurl = vchr_current_url)|Q(vchr_editurl = vchr_current_url)|Q(vchr_viewurl = vchr_current_url)|Q(vchr_listurl = vchr_current_url))).annotate(type_perm = Case( When(Q(vchr_addurl = vchr_current_url),then = Value('add')), When(Q(vchr_editurl = vchr_current_url),then = Value('edit')), When(Q(vchr_viewurl = vchr_current_url),then = Value('view')), When(Q(vchr_listurl = vchr_current_url),then = Value('list')), output_field=CharField())).values('type_perm','pk_bint_id')
            # ins_group_per = GroupPermissions.objects.filter(Q(Q(fk_category_items__fk_menu_category__vchr_addurl = vchr_current_url)|Q(fk_category_items__fk_menu_category__vchr_editurl = vchr_current_url)|Q(fk_category_items__fk_menu_category__vchr_viewurl = vchr_current_url)|Q(fk_category_items__fk_menu_category__vchr_listurl = vchr_current_url)),Q(fk_desig_id = int_desig_id)).values('bln_view','bln_add','bln_delete','bln_edit')


            if ins_menu_category:
                ins_category_items = CategoryItems.objects.get(fk_menu_category = ins_menu_category[0]['pk_bint_id'],fk_company_id = request.user.userdetails.fk_company_id)
                ins_group_per = GroupPermissions.objects.filter(fk_desig_id = int_desig_id,fk_category_items = ins_category_items.pk_bint_id).values()

                if not ins_group_per:
                    return Response({'status':1,'bln_per':False, 'bln_logout':bln_logout})

                if ins_menu_category[0]['type_perm'] == 'add':
                    bln_perm = ins_group_per[0]['bln_add']
                elif ins_menu_category[0]['type_perm'] == 'edit':
                    bln_perm = ins_group_per[0]['bln_edit']
                elif ins_menu_category[0]['type_perm'] == 'view' or ins_menu_category[0]['type_perm'] == 'list' :
                    bln_perm = ins_group_per[0]['bln_view']
                elif ins_menu_category[0]['type_perm'] == 'delete':
                    bln_perm = ins_group_per[0]['delete']

                if bln_perm:
                    return Response({'status':1,'bln_per':True,'bln_logout':bln_logout})
                else:
                    return Response({'status':1,'bln_per':False, 'bln_logout':bln_logout})
            return Response({'status':1,'bln_per':False, 'bln_logout':bln_logout})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
