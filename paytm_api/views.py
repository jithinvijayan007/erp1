
import json
from django.conf.urls import url
from requests.api import request
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import sys
from .models import PaytmPointData
from POS import ins_logger
# from POS import ins_logger,settings

from datetime import datetime
import requests
import json

class GetPaytmPoints(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            URL = "http://mqst.mloyalpos.com/Service.svc/GET_CUSTOMER_TRANS_INFO"
            HEADER = {'userid':'mob_usr',
            'pwd':'@pa$$w0rd'}
            int_mobile = request.data.get('mobile')
            # int_mobile = 9745020448


            dct_data = {'objClass':{'customer_mobile':int_mobile}}
            paytm_data = requests.post(URL,json =dct_data ,headers = HEADER)
            if paytm_data.status_code == 200:
                paytm_data = paytm_data.json()['GET_CUSTOMER_TRANS_INFOResult']
                # paytm_data = paytm_data.json()
                if paytm_data['Success']:
                    lst_customer_details    = json.loads(paytm_data['output']['response'])['CUSTOMER_DETAILS']
                    float_loyaltypoint      = lst_customer_details[0]['LoyalityPoints']
                    if float(lst_customer_details[0]['LoyalityPoints'])!=0:
                        float_loyalty_amount    = round(lst_customer_details[0]['LoyalityPointsValue']/float(lst_customer_details[0]['LoyalityPoints']))
                    else:
                        float_loyalty_amount=0

                    return  Response({'status':1,'data':{'loyal_point':float_loyaltypoint,'loyal_amt':float_loyalty_amount}})
            return  Response({'status':1,'data':{'loyal_point':0,'loyal_amt':0}})

        except Exception as e:
            return Response({'reason':e,'status':0,'data':{'loyal_point':0,'loyal_amt':0}})

class ValidateCustPoint(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            URL = "http://mqst.mloyalpos.com/Service.svc/GET_POINTS_VALIDATION_INFO"
            HEADER = {'userid':'mob_usr',
            'pwd':'@pa$$w0rd'}
            dct_data = {}
            dct_data['customer_mobile'] = request.data.get("mobile")
            dct_data['customer_points'] = request.data.get("points")
            dct_data['store_code'] = request.user.userdetails.fk_branch.vchr_code
            # import pdb; pdb.set_trace()
            # dct_data['customer_mobile'] = 9645454751
            # dct_data['customer_points'] = 5
            # dct_data['store_code'] = 'TDP'
            paytm_reponse = requests.post(URL,json={'objClass':dct_data},headers = HEADER)

            if paytm_reponse.status_code == 200:
                dct_response= {}
                # paytm_reponse = json.dumps(paytm_reponse.text['GET_POINTS_VALIDATION_INFOResult'])
                paytm_reponse = paytm_reponse.json()['GET_POINTS_VALIDATION_INFOResult']
                if paytm_reponse['Success']:
                    dct_response['points'] = paytm_reponse['output']['points']
                    dct_response['points_value'] = paytm_reponse['output']['points_value']


                    return  Response({'status':1,'data':dct_response})
                else:
                    dct_response= {}
                    dct_response['points'] = 0
                    dct_response['points_value'] = 0
                    return  Response({'status':0,'data':dct_response})
            return  Response({'status':0,'data':dct_response})
        except Exception as e:
            dct_response= {}
            dct_response['points'] = 0
            dct_response['points_value'] = 0
            return  Response({'status':0,'data':dct_response})


class RedeemLoyaltyPoint(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            URL = "http://mqst.mloyalpos.com/Service.svc/REDEEM_LOYALTY_POINTS_ACTION"
            HEADER = {'userid':'mob_usr',
            'pwd':'@pa$$w0rd'}
            time_now = datetime.now()
            dct_data = {}
            dct_data['customer_mobile'] = request.data['mobile']
            dct_data['customer_points'] = request.data['point']
            dct_data['passcode'] = request.data['otp']
            dct_data['ref_bill_no'] = request.data['partial_bill_no']
            dct_data['store_code'] = request.user.userdetails.fk_branch.vchr_code

            # dct_data['customer_mobile'] = 9645454751
            # dct_data['customer_points'] = 5
            # dct_data['passcode'] = 962133
            # dct_data['ref_bill_no'] = 65515
            # dct_data['store_code'] = 'TDP'


            paytm_reponse = requests.post(URL,json={'objClass':dct_data},headers = HEADER)

            if paytm_reponse.status_code == 200:
                dct_response= {}
                # paytm_reponse = json.dumps(paytm_reponse.text['GET_POINTS_VALIDATION_INFOResult'])
                paytm_reponse = paytm_reponse.json()['REDEEM_LOYALTY_POINTS_ACTIONResult']
                if paytm_reponse['Success']:


                    dct_response['balance_points'] = paytm_reponse['output']['balance_points']
                    dct_response['points_value'] = paytm_reponse['output']['points_value']
                    dct_response['redeem_points'] = paytm_reponse['output']['redeem_points']
                    dct_response['referenceNo'] = paytm_reponse['output']['referenceNo']

                    ins_paytm_point = PaytmPointData(
                            fk_partial_id = dct_data['ref_bill_no'],
                            int_status = 0,
                            dat_created = time_now,
                            fk_created = request.user,
                            vchr_ref_num = paytm_reponse['output']['referenceNo'],
                            dbl_amount = paytm_reponse['output']['points_value'],
                            dbl_pts = paytm_reponse['output']['redeem_points']
                        )
                    ins_paytm_point.save()
                    dct_response['paytm_point_table_id'] = ins_paytm_point.pk_bint_id

                    return  Response({'status':1,'data':dct_response})
                else:
                    return  Response({'status':0,'data':dct_response})
            return Response({'status':0,'reson':'server_error'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class ReverseRedeemPoint(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            OUT_BOND_URL  = "http://mqst.mloyalpos.com/Service.svc/REVERSE_POINTS_BY_TRANSACTION_ID"
            HEADER = {'userid':'mob_usr','pwd':'@pa$$w0rd'}
            intPaytmPointId=request.data.get('id')
            str_ref_no = PaytmPointData.objects.filter(pk_bint_id=intPaytmPointId).values().first()['vchr_ref_num']
            dct_data = {'objClass':{"transaction_id":str_ref_no}}
            pytm_request = requests.post(OUT_BOND_URL,json =dct_data,headers = HEADER)
            if pytm_request.status_code == 200:
                pytm_request = pytm_request.json()['REVERSE_POINTS_BY_TRANSACTION_IDResult']
                if pytm_request['Success']:
                    PaytmPointData.objects.filter(pk_bint_id=intPaytmPointId).update(int_status=-1)
                    return  Response({'status':1})
                else:
                    return  Response({'status':0})
            else:
                return  Response({'status':0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
