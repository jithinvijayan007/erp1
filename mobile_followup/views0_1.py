from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_404_NOT_FOUND
from datetime import datetime
from django.contrib.auth.models import User
from user_app.models import UserModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import and_,func ,cast,Date
from groups.models import MainCategory,GroupPermissions,SubCategory
from enquiry.models import EnquiryMaster
from customer_app.models import CustomerModel
from enquiry_print.views import enquiry_print
from enquiry_mobile.models import ComputersEnquiry,ComputersFollowup,TabletEnquiry,TabletFollowup,AccessoriesEnquiry,AccessoriesFollowup,MobileEnquiry,MobileFollowup
from django.db import transaction
from stock_app.models import Stockmaster,Stockdetails
from django.db.models import Case,  Value, When,F
from django.db.models import Q

EnquiryMasterSA = EnquiryMaster.sa
CustomerSA = CustomerModel.sa
AuthUserSA = User.sa

ComputersEnquirySA = ComputersEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
MobileEnquirySA = MobileEnquiry.sa

ComputersFollowupSA = ComputersFollowup.sa
TabletFollowupSA = TabletFollowup.sa
AccessoriesFollowupSA = AccessoriesFollowup.sa
MobileFollowupSA = MobileFollowup.sa

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

class AddFollowup(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            dat_created = datetime.now()
            if request.data['vchr_servicetype'] == 'computers':
                try:
                    with transaction.atomic():
                        str_enquiry_no = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                        if ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.username == request.data['vchr_current_user_name'] :
                            dat_updated_time = dat_created
                            fk_updated_by = UserModel.objects.get(username = request.data['vchr_current_user_name']).id
                            int_status = 1
                        else :
                            dat_updated_time = None
                            fk_updated_by = None
                            int_status = 0

                        if request.data.get('vchr_followup_status') == 'BOOKED':
                            int_status = 1
                            rst_enq = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
                            ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
                            if ins_stock:
                                Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
                            else:
                                ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
                                int_available = ins_stock.int_available
                                return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
                        ins_computers_follow_up = ComputersFollowup(fk_computers = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
                            vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
                            int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(username = request.data['vchr_current_user_name']),\
                            fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                        ins_computers_follow_up.save()
                        if request.data.get('vchr_followup_status')== 'BOOKED':
                            ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
                        if int_status:
                            ins_obj = ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                            ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                            dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
                        if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                            ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                            dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
                            ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})

                except Exception as e:
                    return Response({'status':'1', 'error':str(e)})
            if int_status:
                ins_user = UserModel.objects.get(username = request.data['vchr_current_user_name'])
                enquiry_print(str_enquiry_no,request,ins_user)
            int_enquiry_id = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_enquiry_num = str_enquiry_no, fk_company_id = request.user.usermodel.fk_company_id).pk_bint_id
            return JsonResponse({'status':'success','value':'Follow-up completed successfully!','remarks':request.data['vchr_followup_remarks'],'followup':request.data['vchr_followup_status'],'amount':request.data['int_followup_amount'],'change':int_status,'enqId':int_enquiry_id,'int_quantity':request.data.get('int_followup_quantity')})

        except Exception as e:
            return JsonResponse({'status':'0','data':str(e)})
