from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from loyalty_card.models import LoyaltyCard,LoyaltyCardStatus
from invoice.models import LoyaltyCardInvoice
from customer.models import CustomerDetails
from django.contrib.auth.models import User
from datetime import datetime,date
from django.db.models import Q,Case,When,Value,IntegerField,Count,Sum,F
from django.conf import settings

from POS import ins_logger
import sys, os
import requests
# Create your views here.
from POS import ins_logger
import sys, os

from django.db import transaction


# =======charlson---- Loyalty Card=========
class LoyaltyCardAPIView(APIView):
    permission_classes=[AllowAny]
    # ====== list all Loyalty Card =======
    def get(self,request):
        try:
            with transaction.atomic():

            # import pdb; pdb.set_trace()
                lst_loyalty_card = list(LoyaltyCard.objects.filter(bln_status=True).values('pk_bint_id','vchr_card_name','int_price_range_from','int_price_range_to','dbl_loyalty_percentage','dbl_min_purchase_amount','int_min_redeem_days','int_min_redeem_point'))
                return Response({'status':1,'data':lst_loyalty_card})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'data':str(e)})

    # ===== Add New Loyalty Card =======
    def post(self,request):
        try:
            with transaction.atomic():
                    if LoyaltyCard.objects.filter(vchr_card_name=request.data.get('loyalty_card_name')).exclude(bln_status=False):
                        return Response({'status':0,'reason':'Name already exist'})
                    else:
                        user_name = request.data.get('user')
                        user = User.objects.filter(username = user_name,is_active=True).all().first()
                        loyalty_card_name = request.data.get('loyalty_card_name')
                        price_range_from = request.data.get('price_range_from')
                        price_range_to = request.data.get('price_range_to')
                        loyalty_percentage = request.data.get('loyalty_percentage')
                        min_purchase_amount = request.data.get('min_purchase_amount')
                        min_redeem_days = request.data.get('min_redeem_days')
                        min_redeem_point = request.data.get('min_redeem_point')
                        ins_loyalty = LoyaltyCard(
                        vchr_card_name=loyalty_card_name,
                        int_price_range_from=price_range_from,
                        int_price_range_to=price_range_to,
                        dbl_loyalty_percentage=loyalty_percentage,
                        dbl_min_purchase_amount=min_purchase_amount,
                        int_min_redeem_days=min_redeem_days,
                        int_min_redeem_point=min_redeem_point,
                        bln_status=True,fk_created_id=user,dat_created=datetime.now())
                        url =settings.BI_HOSTNAME + "/loyalty/loyalty_card/"
                        if request.data.get('blnBi'):
                                ins_loyalty.save()
                        else:
                            res_data = requests.post(url,json={'blnPos':True,'user':request.data.get('user'),'loyalty_card_name':request.data.get('loyalty_card_name'),"price_range_from":request.data.get('price_range_from'),"price_range_to":request.data.get('price_range_to'),"loyalty_percentage":request.data.get('loyalty_percentage'),"min_purchase_amount":request.data.get('min_purchase_amount'),"min_redeem_days":request.data.get('min_redeem_days'),"min_redeem_point":request.data.get('min_redeem_point')})
                            if res_data.json().get('status')=='success':
                                ins_loyalty.save()


                            else:
                                return Response({'status': 0,'data':res_data.json().get('message',res_data.json())})
                        return Response({'status':1})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'data':str(e)})
    # ======= Edit Loyalty Card ========
    def put(self,request):
        try:
            with transaction.atomic():
                if request.data.get('loyalty_card_id'):
                    user_name = request.data.get('user')
                    user = User.objects.filter(username = user_name,is_active=True).all().first()
                    loyalty_card_name = request.data.get('loyalty_card_name')
                    price_range_from = request.data.get('price_range_from')
                    price_range_to = request.data.get('price_range_to')
                    loyalty_percentage = request.data.get('loyalty_percentage')
                    min_purchase_amount = request.data.get('min_purchase_amount')
                    min_redeem_days = request.data.get('min_redeem_days')
                    min_redeem_point = request.data.get('min_redeem_point')
                    url =settings.BI_HOSTNAME + "/loyalty/loyalty_card/"
                    if request.data.get('blnBi'):
                            LoyaltyCard.objects.filter(vchr_card_name=request.data.get('card_name'),bln_status=True).update(
                            vchr_card_name=loyalty_card_name,
                            int_price_range_from=price_range_from,
                            int_price_range_to=price_range_to,
                            dbl_loyalty_percentage=loyalty_percentage,
                            dbl_min_purchase_amount=min_purchase_amount,
                            int_min_redeem_days=min_redeem_days,
                            int_min_redeem_point=min_redeem_point,fk_updated_id=user,dat_updated=datetime.now())
                    else:
                        res_data = requests.patch(url,json={'blnPos':True,'user':request.data.get('user'),'loyalty_card_name':request.data.get('loyalty_card_name'),"price_range_from":request.data.get('price_range_from'),"price_range_to":request.data.get('price_range_to'),"loyalty_percentage":request.data.get('loyalty_percentage'),"min_purchase_amount":request.data.get('min_purchase_amount'),"min_redeem_days":request.data.get('min_redeem_days'),"min_redeem_point":request.data.get('min_redeem_point'),"loyalty_card_id":request.data.get("loyalty_card_id"),'card_name':request.data.get('card_name')})
                        if res_data.json().get('status')=='success':
                                LoyaltyCard.objects.filter(pk_bint_id=int(request.data.get('loyalty_card_id'))).update(
                                vchr_card_name=loyalty_card_name,
                                int_price_range_from=price_range_from,
                                int_price_range_to=price_range_to,
                                dbl_loyalty_percentage=loyalty_percentage,
                                dbl_min_purchase_amount=min_purchase_amount,
                                int_min_redeem_days=min_redeem_days,
                                int_min_redeem_point=min_redeem_point,fk_updated_id=user,dat_updated=datetime.now())

                        else:
                            return Response({'status': 0,'data':res_data.json().get('message',res_data.json())})

                    return Response({'status':1})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'data':str(e)})

# ======= Delete Loyalty Card ========
class DeleteLoyaltyCardAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        try:
            with transaction.atomic():
                    if request.data.get('blnBi'):

                            LoyaltyCard.objects.filter(vchr_card_name=request.data.get('card_name'),bln_status=True).update(bln_status=False,fk_updated_id=request.user.id,dat_updated=datetime.now())
                    else:
                        url =settings.BI_HOSTNAME + "/loyalty/loyalty_card_delete/"
                        res_data = requests.post(url,json={'blnPos':True,'loyalty_card_id':request.data.get('loyalty_card_id'),'loyalty_card_name':request.data.get('card_name')})
                        if res_data.json().get('status')=='success':

                                LoyaltyCard.objects.filter(pk_bint_id=int(request.data.get('loyalty_card_id'))).update(bln_status=False,fk_updated_id=request.user.id,dat_updated=datetime.now())
                        else:
                            return Response({'status': 0,'data':res_data.json().get('message',res_data.json())})

                    return Response({'status':1})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'data':str(e)})


def loyalty_card(purchased_total_amount,ins_customer,ins_master,ins_user):
    with transaction.atomic():
        # import pdb; pdb.set_trace()
        if purchased_total_amount != 0:
            ins_customer.dbl_purchase_amount += purchased_total_amount
            bln_auto_change = False
            if bln_auto_change:
                ins_loyaltycard = LoyaltyCard.objects.filter(int_price_range_from__lte = ins_customer.dbl_purchase_amount, int_price_range_to__gte = ins_customer.dbl_purchase_amount,bln_status=True).first() # loyalty card selection in price range
                if ins_loyaltycard:
                    if ins_customer.fk_loyalty_id != ins_loyaltycard.pk_bint_id: # for loyalty card changes
                        if LoyaltyCardStatus.objects.filter(fk_customer = ins_customer): # add or change loyalty card status
                            LoyaltyCardStatus.objects.filter(fk_customer = ins_customer).update(int_status = 2)
                            LoyaltyCardStatus.objects.create(fk_old_card = ins_customer.fk_loyalty,
                                                            fk_new_card = ins_loyaltycard,
                                                            dat_eligible = date.today(),
                                                            dat_given = date.today(),
                                                            fk_staff = ins_user,
                                                            int_status = 0)
                        else:
                            LoyaltyCardStatus.objects.create(fk_customer = ins_customer,
                                                            fk_new_card = ins_loyaltycard,
                                                            dat_eligible = date.today(),
                                                            dat_given = date.today(),
                                                            fk_staff = ins_user,
                                                            int_status = 0)

                    ins_loyaltycard_status = LoyaltyCardStatus.objects.filter(fk_customer = ins_customer, int_status = 0).values('fk_old_card','fk_new_card').first()
                    ins_curr_loyaltycard = LoyaltyCard.objects.filter(pk_bint_id = ins_loyaltycard_status['fk_new_card']).first()

                    if ins_curr_loyaltycard.dbl_min_purchase_amount <= purchased_total_amount:
                        if (ins_customer.dbl_purchase_amount-purchased_total_amount) >= ins_curr_loyaltycard.int_price_range_from:
                            ins_customer.int_loyalty_points += round(purchased_total_amount*ins_curr_loyaltycard.dbl_loyalty_percentage/100)
                            LoyaltyCardInvoice.objects.create(fk_loyalty = ins_curr_loyaltycard,
                                                            fk_customer = ins_customer,
                                                            int_points = round(purchased_total_amount*ins_curr_loyaltycard.dbl_loyalty_percentage/100),
                                                            dbl_amount = purchased_total_amount,
                                                            fk_invoice = ins_master,
                                                            dat_invoice = datetime.now())
                        else:
                            ins_prev_loyaltycard = LoyaltyCard.objects.filter(pk_bint_id = ins_loyaltycard_status['fk_old_card']).first()
                            loyalty_amt = ins_prev_loyaltycard.int_price_range_to-(ins_customer.dbl_purchase_amount-purchased_total_amount)
                            int_points = round(loyalty_amt*ins_prev_loyaltycard.dbl_loyalty_percentage/100)
                            LoyaltyCardInvoice.objects.create(fk_loyalty = ins_prev_loyaltycard,
                                                            fk_customer = ins_customer,
                                                            int_points = round(loyalty_amt*ins_prev_loyaltycard.dbl_loyalty_percentage/100),
                                                            dbl_amount = loyalty_amt,
                                                            fk_invoice = ins_master,
                                                            dat_invoice = datetime.now())

                            loyalty_amt = ins_customer.dbl_purchase_amount-ins_curr_loyaltycard.int_price_range_from
                            int_points += round(loyalty_amt*ins_curr_loyaltycard.dbl_loyalty_percentage/100)
                            LoyaltyCardInvoice.objects.create(fk_loyalty = ins_prev_loyaltycard,
                                                            fk_customer = ins_customer,
                                                            int_points = round(loyalty_amt*ins_curr_loyaltycard.dbl_loyalty_percentage/100),
                                                            dbl_amount = loyalty_amt,
                                                            fk_invoice = ins_master,
                                                            dat_invoice = datetime.now())

                            ins_customer.int_loyalty_points += int_points
            else:
                ins_loyaltycard_id = LoyaltyCardStatus.objects.filter(fk_customer = ins_customer,int_status = 0).values('fk_customer_id').annotate(fk_loyalty_id = Case(When(dat_eligible__lte = date.today(),then='fk_new_card_id'),default = 'fk_old_card_id',output_field = IntegerField())).last()
                if ins_loyaltycard_id:
                    ins_loyaltycard = LoyaltyCard.objects.filter(pk_bint_id = ins_loyaltycard_id['fk_loyalty_id']).first()
                    if ins_loyaltycard.dbl_min_purchase_amount <= purchased_total_amount:
                        ins_customer.int_loyalty_points += round(purchased_total_amount*ins_loyaltycard.dbl_loyalty_percentage/100)
                        LoyaltyCardInvoice.objects.create(fk_loyalty = ins_loyaltycard,
                                                        fk_customer = ins_customer,
                                                        int_points = round(purchased_total_amount*ins_loyaltycard.dbl_loyalty_percentage/100),
                                                        dbl_amount = purchased_total_amount,
                                                        fk_invoice = ins_master,
                                                        dat_invoice = datetime.now())
            ins_customer.save()

class OtpVarification(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            import random
            int_cust_id = request.data.get('intCustId')
            int_otp_no = random.randint(100000,999999)
            ins_customer = CustomerDetails.objects.get(pk_bint_id=int_cust_id)
            mob_num = ins_customer.int_mobile
            ins_customer.int_otp_number = int_otp_no
            ins_customer.save()
            security_key = 'bf278-7563-11e9-ade6-0200cd936042'
            url = 'https://2factor.in/API/V1/'+security_key+'/SMS/'+str(mob_num)+'/'+str(int_otp_no)
            response = requests.request("GET", url)
            if response.json()['Status']=='Success':
                return Response({'status':1})
            else:
                return Response({'status':0,'message':response.json()['Status']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

    def put(self,request):
        try:
            int_cust_id = request.data.get('intCustId')
            int_otp = request.data.get('intOTP')
            ins_customer = CustomerDetails.objects.get(pk_bint_id=int_cust_id)
            if ins_customer.int_otp_number == int(int_otp):
                CustomerDetails.objects.filter(pk_bint_id=int_cust_id).update(int_otp_number=None)
                return Response({'status':1})
            else:
                return Response({'status':0,'message':'Invalid'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class LoyaltyFooterApi(APIView):
    def post(self,request):
        try:
            int_customer = request.data.get('intCustomer')
            rst_loyalty = CustomerDetails.objects.filter(pk_bint_id = int_customer).values('vchr_name','int_mobile','vchr_loyalty_card_number').annotate(total_loyalty_point=F('int_loyalty_points')-F('int_redeem_point'))
            if rst_loyalty:
                return Response({'status':1,'data':list(rst_loyalty)})
            else:
                return Response({'status':0,'message':'No data'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})
