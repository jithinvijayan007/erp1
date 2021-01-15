
from django.db import transaction
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from user_app.models import UserModel
from enquiry.models import EnquiryMaster
from enquiry_mobile.models import ItemEnquiry,ItemFollowup
from customer_app.models import CustomerModel
# from enquiry_mobile.models import EnquiryFinance
from finance_enquiry.models import FinanceSchema,FinanceCustomerDetails,EnquiryFinance
from datetime import datetime
from django.conf import settings
from CRM import ins_logger
import traceback
import requests


class UpdateFinanceEligibility(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            dbl_amount = None
            id = request.data.get('intEnquiryFinance')
            if request.data['eligible']:
                vchr_remarks = request.data.get('remark',None)
                dbl_amount = request.data.get('amount')
                vchr_status = 'eligible'
                EnquiryFinance.objects.filter(pk_bint_id = id).update(
                vchr_finance_status = vchr_status.upper(),
                vchr_remarks = vchr_remarks,
                dbl_max_amt = dbl_amount)
            else:
                vchr_remarks = request.data.get('remark',None)
                if not vchr_remarks:
                    return Response({'status':'0','status':'remarks is needed'})
                vchr_status = 'not eligible'
                EnquiryFinance.objects.filter(pk_bint_id = id).update(
                vchr_finance_status = vchr_status.upper(),
                vchr_remarks = vchr_remarks,
                dbl_max_amt = dbl_amount,
                bln_eligible = False)

            return Response({'status':'1','message':'finance details updated successfully'})

        except Exception as e:
            return Response({'status':'0','message':str(e)})

class UpdateFinanceEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_enquiry_master_id = request.data.get('idEnquiry')
            str_card_name = request.data.get('strCardName').upper()
            str_order_no = request.data.get('strOrderNo')
            ins_customer_id=ItemEnquiry.objects.filter(fk_enquiry_master=int_enquiry_master_id).values('fk_enquiry_master__fk_customer_id').first()['fk_enquiry_master__fk_customer_id']

            if EnquiryFinance.objects.filter(fk_enquiry_master=int_enquiry_master_id):
                ins_finance = EnquiryFinance.objects.filter(fk_enquiry_master = int_enquiry_master_id).update(vchr_name_in_card = str_card_name , vchr_delivery_order_no = str_order_no,vchr_finance_status='PROCESSED')
                if ins_finance:
                    lst_item_enq_id = list(ItemEnquiry.objects.filter(fk_enquiry_master=int_enquiry_master_id,vchr_enquiry_status = 'TO PROCESS').values_list('pk_bint_id', flat=True))
                    ItemEnquiry.objects.filter(fk_enquiry_master = int_enquiry_master_id,vchr_enquiry_status = 'TO PROCESS').update(vchr_enquiry_status='BOOKED',int_fop = 1)
                    ins_obj = ItemEnquiry.objects.filter(pk_bint_id__in = lst_item_enq_id)

                    ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id = ins_customer_id,fk_enquiry_master__fk_company = request.user.usermodel.fk_company,fk_product_id=ins_obj.first().fk_product_id).exclude(vchr_enquiry_status = 'BOOKED')
                    if ins_item_enq_exist:
                        '''Following code commented in order to prevent lost case if same product booked multiple times'''

                        '''ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                        lst_query_set = []
                        for ins_data in ins_item_enq_exist:
                            ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                                              vchr_notes = ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                              vchr_enquiry_status = 'LOST',
                                                              int_status = 1,
                                                              dbl_amount = 0.0,
                                                              int_quantity = 0,
                                                              fk_user = request.user.usermodel,
                                                              fk_updated = request.user.usermodel,
                                                              dat_followup = datetime.now(),
                                                              dat_updated = datetime.now())
                            lst_query_set.append(ins_follow_up)
                        if lst_query_set:
                            ItemFollowup.objects.bulk_create(lst_query_set);'''

                        # ---------------POS API--------------
                        ins_cust_enq_finance = FinanceCustomerDetails.objects.filter(fk_enquiry_finance__fk_enquiry_master = int_enquiry_master_id).values('fk_enquiry_finance__fk_financiers__vchr_name', 'fk_enquiry_finance__fk_financier_schema__vchr_schema', 'fk_enquiry_finance__dbl_max_amt', 'dbl_down_payment_amount', 'fk_enquiry_finance__vchr_delivery_order_no', 'fk_enquiry_finance__fk_enquiry_master__fk_customer_id', 'fk_enquiry_finance__fk_enquiry_master_id','fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num', 'fk_enquiry_finance__fk_enquiry_master__fk_assigned__username', 'fk_enquiry_finance__fk_enquiry_master__fk_branch__vchr_code', 'dbl_net_loan_amount').first()
                        ins_customer = CustomerModel.objects.get(id=ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_customer_id'])

                        dct_pos_data = {}
                        dct_pos_data['vchr_cust_name'] = ins_customer.cust_fname+' '+ins_customer.cust_lname
                        dct_pos_data['vchr_cust_email'] = ins_customer.cust_email
                        dct_pos_data['int_cust_mob'] = ins_customer.cust_mobile
                        dct_pos_data['vchr_gst_no'] = ins_customer.vchr_gst_no
                        dct_pos_data['int_enq_master_id'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master_id']
                        dct_pos_data['vchr_enquiry_num'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num']
                        dct_pos_data['vchr_location'] = ''
                        dct_pos_data['int_pin_code'] = ''
                        dct_pos_data['txt_address'] = ''
                        if ins_customer.fk_location:
                            dct_pos_data['vchr_location'] = ins_customer.fk_location.vchr_name
                            dct_pos_data['vchr_district'] = ins_customer.fk_location.vchr_district
                            dct_pos_data['vchr_pin_code'] = ins_customer.fk_location.vchr_pin_code
                        if ins_customer.fk_state:
                            dct_pos_data['vchr_state_code'] = ins_customer.fk_state.vchr_code
                        dct_pos_data['vchr_staff_code'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_assigned__username']
                        dct_pos_data['vchr_branch_code'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_branch__vchr_code']
                        dct_pos_data['str_remarks'] = request.data.get('vchr_remarks')
                        dct_pos_data['dat_enquiry'] = datetime.now().strftime('%Y-%m-%d')
                        dct_pos_data['dct_products'] = {}
                        dct_pos_data['dbl_total_amt'] = 0
                        dct_pos_data['dbl_total_tax'] = 0
                        dct_pos_data['dbl_discount'] = 0
                        dct_pos_data['vchr_finance_name'] = ins_cust_enq_finance['fk_enquiry_finance__fk_financiers__vchr_name']
                        dct_pos_data['vchr_finance_schema'] = ins_cust_enq_finance['fk_enquiry_finance__fk_financier_schema__vchr_schema']
                        dct_pos_data['dbl_finance_amt'] = ins_cust_enq_finance['dbl_net_loan_amount']
                        dct_pos_data['dbl_emi'] = 0
                        dct_pos_data['dbl_down_payment'] = ins_cust_enq_finance['dbl_down_payment_amount']
                        dct_pos_data['vchr_fin_ordr_num'] = ins_cust_enq_finance['fk_enquiry_finance__vchr_delivery_order_no']
                        dct_pos_data['lst_item'] = []
                        bln_post_rqst = False
                        for ins_item in ins_obj:
                            if ins_item.vchr_enquiry_status == 'BOOKED':
                                bln_post_rqst = True
                                dct_pos_data['dbl_total_amt'] += float(ins_item.dbl_amount) if ins_item.dbl_amount else 0.0
                                dct_pos_data['dbl_discount'] += float(ins_item.dbl_discount_amount) if ins_item.dbl_discount_amount else 0.0
                                dct_item = {}
                                dct_item['item_enquiry_id'] = ins_item.pk_bint_id
                                dct_item['vchr_item_name'] = ins_item.fk_item.vchr_item_name
                                dct_item['vchr_item_code'] = ins_item.fk_item.vchr_item_code
                                dct_item['json_imei'] = ins_item.dbl_imei_json
                                dct_item['int_quantity'] = int(ins_item.int_quantity)
                                dct_item['dbl_amount'] = float(ins_item.dbl_amount) if ins_item.dbl_amount else 0.0
                                dct_item['dbl_discount'] = float(ins_item.dbl_discount_amount) if ins_item.dbl_discount_amount else 0.0
                                dct_item['dbl_buyback'] = float(ins_item.dbl_buy_back_amount) if ins_item.dbl_buy_back_amount else 0.0
                                dct_item['vchr_remarks'] = ins_item.vchr_remarks
                                dct_pos_data['lst_item'].append(dct_item)
                        if bln_post_rqst:
                            url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
                            try:
                                res_data = requests.post(url,json=dct_pos_data)
                                if res_data.json().get('status')=='1':
                                    pass
                                else:
                                    return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                            except Exception as e:
                                ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'user': 'user_id:' + str(request.user.id)})
                        # --------------------------------------------------------------


                    return Response({'status':'1','data':'Finance Approved'})
                else:
                    return Response({'status':'0','data':'Finance Approval Failed'})
            else:
                return Response({'status':'0','data':'No data'})

        except Exception as e:
            return Response({'status':'0','data':str(e)})


class AddFinanceCustomerAPIView(APIView):
    def get(self,request):
        try:
            dct_data = list(FinanceSchema.objects.all().values('pk_bint_id','vchr_schema'))
            return Response({'status':'1','data':dct_data})
        except Exception as e:
            return Response({'status':'0','data':str(e)})

    def post(self,request):
        try:
            fk_finance_schema = request.data.get('schema')
            ins_schema = None
            if fk_finance_schema:
                ins_schema = FinanceSchema.objects.get(pk_bint_id=fk_finance_schema)
            str_enquiry_num = request.data.get('enqno')
            str_id_type = request.data.get('idType')
            str_id_num = request.data.get('idNo')
            str_pan_num = request.data.get('pancardNo')
            str_bank_name = request.data.get('bankName')
            int_account_num = request.data.get('accno')
            str_branch_name = request.data.get('branchName')
            str_cheque_num = request.data.get('chequeNo')
            str_initial_paymet_type = request.data.get('type')
            # ----------------add new field--------------------------------
            int_finance_id = request.data.get('financeId')
            str_card_name = request.data.get('nameOnCard').upper()
            str_order_no = request.data.get('deliveryNo')

            dbl_down_payment_amount = 0
            dbl_processing_fee = 0
            dbl_margin_money = 0
            dbl_service_charge = 0
            dbl_net_loan_amount = 0
            dbdCharge = 0

            if request.data.get('downpayment'):
                dbl_down_payment_amount = request.data.get('downpayment')
            if request.data.get('processfee'):
                dbl_processing_fee = request.data.get('processfee')
            if request.data.get('marginMoney'):
                dbl_margin_money = request.data.get('marginMoney')
            if request.data.get('serCharge'):
                dbl_service_charge = request.data.get('serCharge')
            if request.data.get('loanAmt'):
                dbl_net_loan_amount = request.data.get('loanAmt')
            if request.data.get('dbdCharge'):
                dbdCharge = request.data.get('dbdCharge')

            dbl_total_amount = request.data.get('total_amount')

            dbl_dbd_amount = (dbl_total_amount*float(dbdCharge))/100
            # ---------------------------------------------------------------


            with transaction.atomic():
                ins_finance = EnquiryFinance.objects.filter(pk_bint_id = int_finance_id).update(vchr_name_in_card = str_card_name , vchr_delivery_order_no = str_order_no, vchr_finance_status='PROCESSED')
                fk_enquiry_master=EnquiryMaster.objects.get(vchr_enquiry_num=str_enquiry_num)
                ins_finance_customer = FinanceCustomerDetails(fk_schema = ins_schema,
                                                                    fk_enquiry_finance = EnquiryFinance.objects.get(fk_enquiry_master=fk_enquiry_master,int_status=0),
                                                                    vchr_id_type = str_id_type,
                                                                    vchr_id_number = str_id_num,
                                                                    vchr_pan_number = str_pan_num,
                                                                    vchr_bank_name = str_bank_name,
                                                                    bint_account_number = int_account_num,
                                                                    vchr_branch_name = str_branch_name,
                                                                    vchr_cheque_number = str_cheque_num,
                                                                    vchr_initial_payment_type = str_initial_paymet_type,
                                                                    dbl_down_payment_amount = dbl_down_payment_amount,
                                                                    dbl_processing_fee = dbl_processing_fee,
                                                                    dbl_margin_money = dbl_margin_money,
                                                                    dbl_dbd_amount = dbl_dbd_amount,
                                                                    dbl_service_charge = dbl_service_charge,
                                                                    dbl_net_loan_amount = dbl_net_loan_amount

                                                                    )
                ins_finance_customer.save()


                if ins_finance:
                    lst_item_enq_id = list(ItemEnquiry.objects.filter(fk_enquiry_master = fk_enquiry_master,vchr_enquiry_status = 'TO PROCESS').values_list('pk_bint_id', flat=True))
                    ItemEnquiry.objects.filter(fk_enquiry_master = fk_enquiry_master,vchr_enquiry_status = 'TO PROCESS').update(vchr_enquiry_status='BOOKED',int_fop = 1)
                    ins_obj = ItemEnquiry.objects.filter(pk_bint_id__in = lst_item_enq_id)
                    '''Following code commented in order to prevent lost case if same product booked multiple times'''

                    '''ins_item_enq_exist = ItemEnquiry.objects.filter(fk_enquiry_master__fk_customer_id = fk_enquiry_master.fk_customer_id,fk_enquiry_master__fk_company = request.user.usermodel.fk_company,fk_product_id=ins_obj.first().fk_product_id).exclude(vchr_enquiry_status = 'BOOKED')
                    if ins_item_enq_exist:
                        ins_item_enq_exist.update(vchr_enquiry_status = 'LOST')
                        lst_query_set = []
                        for ins_data in ins_item_enq_exist:
                            ins_follow_up = ItemFollowup(fk_item_enquiry = ins_data,
                                                              vchr_notes = ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                              vchr_enquiry_status = 'LOST',
                                                              int_status = 1,
                                                              dbl_amount = 0.0,
                                                              int_quantity = 0,
                                                              fk_user = request.user.usermodel,
                                                              fk_updated = request.user.usermodel,
                                                              dat_followup = datetime.now(),
                                                              dat_updated = datetime.now())
                            lst_query_set.append(ins_follow_up)
                        if lst_query_set:
                            ItemFollowup.objects.bulk_create(lst_query_set);'''

                # ---------------POS API--------------
                ins_cust_enq_finance = FinanceCustomerDetails.objects.filter(fk_enquiry_finance__fk_enquiry_master = fk_enquiry_master).values('fk_enquiry_finance__fk_financiers__vchr_name', 'fk_enquiry_finance__fk_financier_schema__vchr_schema', 'fk_enquiry_finance__dbl_max_amt', 'dbl_down_payment_amount', 'fk_enquiry_finance__vchr_delivery_order_no', 'fk_enquiry_finance__fk_enquiry_master__fk_customer_id', 'fk_enquiry_finance__fk_enquiry_master_id','fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num', 'fk_enquiry_finance__fk_enquiry_master__fk_assigned__username', 'fk_enquiry_finance__fk_enquiry_master__fk_branch__vchr_code', 'dbl_net_loan_amount', 'fk_enquiry_finance__fk_enquiry_master__vchr_remarks').first()
                ins_customer = CustomerModel.objects.get(id=ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_customer_id'])

                dct_pos_data = {}
                dct_pos_data['vchr_cust_name'] = ins_customer.cust_fname+' '+ins_customer.cust_lname
                dct_pos_data['vchr_cust_email'] = ins_customer.cust_email
                dct_pos_data['int_cust_mob'] = ins_customer.cust_mobile
                dct_pos_data['vchr_gst_no'] = ins_customer.vchr_gst_no
                dct_pos_data['int_enq_master_id'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master_id']
                dct_pos_data['vchr_enquiry_num'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num']
                dct_pos_data['vchr_location'] = ''
                dct_pos_data['int_pin_code'] = ''
                dct_pos_data['txt_address'] = ''
                if ins_customer.fk_location:
                    dct_pos_data['vchr_location'] = ins_customer.fk_location.vchr_name
                    dct_pos_data['vchr_district'] = ins_customer.fk_location.vchr_district
                    dct_pos_data['vchr_pin_code'] = ins_customer.fk_location.vchr_pin_code
                if ins_customer.fk_state:
                    dct_pos_data['vchr_state_code'] = ins_customer.fk_state.vchr_code
                dct_pos_data['vchr_staff_code'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_assigned__username']
                dct_pos_data['vchr_branch_code'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__fk_branch__vchr_code']
                dct_pos_data['str_remarks'] = ins_cust_enq_finance['fk_enquiry_finance__fk_enquiry_master__vchr_remarks']
                dct_pos_data['dat_enquiry'] = datetime.now().strftime('%Y-%m-%d')
                dct_pos_data['dct_products'] = {}
                dct_pos_data['dbl_total_amt'] = 0
                dct_pos_data['dbl_total_tax'] = 0
                dct_pos_data['dbl_discount'] = 0
                dct_pos_data['vchr_finance_name'] = ins_cust_enq_finance['fk_enquiry_finance__fk_financiers__vchr_name']
                dct_pos_data['vchr_finance_schema'] = ins_cust_enq_finance['fk_enquiry_finance__fk_financier_schema__vchr_schema']
                dct_pos_data['dbl_finance_amt'] = ins_cust_enq_finance['dbl_net_loan_amount']
                dct_pos_data['dbl_emi'] = 0
                dct_pos_data['dbl_down_payment'] = ins_cust_enq_finance['dbl_down_payment_amount']
                dct_pos_data['vchr_fin_ordr_num'] = ins_cust_enq_finance['fk_enquiry_finance__vchr_delivery_order_no']
                dct_pos_data['lst_item'] = []
                bln_post_rqst = False
                for ins_item in ins_obj:
                    if ins_item.vchr_enquiry_status == 'BOOKED':
                        bln_post_rqst = True
                        dct_pos_data['dbl_total_amt'] += float(ins_item.dbl_amount) if ins_item.dbl_amount else 0.0
                        dct_pos_data['dbl_discount'] += float(ins_item.dbl_discount_amount) if ins_item.dbl_discount_amount else 0.0
                        dct_item = {}
                        dct_item['item_enquiry_id'] = ins_item.pk_bint_id
                        dct_item['vchr_item_name'] = ins_item.fk_item.vchr_item_name
                        dct_item['vchr_item_code'] = ins_item.fk_item.vchr_item_code
                        dct_item['json_imei'] = ins_item.dbl_imei_json
                        dct_item['int_quantity'] = int(ins_item.int_quantity)
                        dct_item['dbl_amount'] = float(ins_item.dbl_amount) if ins_item.dbl_amount else 0.0
                        dct_item['dbl_discount'] = float(ins_item.dbl_discount_amount) if ins_item.dbl_discount_amount else 0.0
                        dct_item['dbl_buyback'] = float(ins_item.dbl_buy_back_amount) if ins_item.dbl_buy_back_amount else 0.0
                        dct_item['vchr_remarks'] = ins_item.vchr_remarks
                        dct_item['int_status'] = 1
                        dct_pos_data['lst_item'].append(dct_item)
                if bln_post_rqst:
                    url = settings.POS_HOSTNAME+"/invoice/add_sales_api/"
                    try:
                        res_data = requests.post(url,json=dct_pos_data)
                        if res_data.json().get('status')=='1':
                            pass
                        else:
                            return JsonResponse({'status': 'Failed','data':res_data.json().get('message',res_data.json())})
                    except Exception as e:
                        ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'user': 'user_id:' + str(request.user.id)})
                # --------------------------------------------------------------
            return Response({'status':'1','data':'Successfully Saved'})
        except Exception as e:
            return Response({'status':'0','data':str(e)})

class ListSchemeByItem(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
            try:
                lst_item_id = request.data['lst_item']
                dat_current = datetime.now()
                dct_data = list(FinanceSchema.objects.filter(fk_item_id__in=lst_item_id,dat_from__lte=dat_current,dat_to__gte=dat_current,fk_financier_id__vchr_name='Bajaj Finance Limited').values('pk_bint_id','vchr_schema'))
                return Response({'status':'1','data':dct_data})
            except Exception as e:
                return Response({'status':'0','data':str(e)})
