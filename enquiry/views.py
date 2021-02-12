from geopy.distance import geodesic

# Create your views here.
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
import sys, os
from branch.models import Branch
from branch_stock.models import BranchStockMaster,BranchStockDetails,NonSaleable
from datetime import datetime
from sqlalchemy.orm.session import sessionmaker
from item_category.models import Item
from POS import ins_logger
from datetime import datetime
# from sqlalchemy.orm import sessionmaker
from django.db.models import Count,Sum,IntegerField
from userdetails.models import UserDetails
from customer.models import CustomerDetails
from company.models import Company as CompanyDetails
from global_methods import get_user_products
from collections import OrderedDict


BranchStockMasterSA=BranchStockMaster.sa
BranchStockDetailsSA=BranchStockDetails.sa
BranchSA = Branch.sa
ItemSA = Item.sa
def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()


class Enquiry(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_qty = request.data.get("int_qty")
            str_branch_code = request.data.get("str_branch_code")
            str_item_code = request.data.get("str_item_code")
            #getting inputs from user
            session = Session()
            # import pdb; pdb.set_trace()

            if int_qty:


                int_current_quantity= BranchStockDetails.objects.filter(
                                                        fk_master__fk_branch__vchr_code = str_branch_code,
                                                        fk_item__vchr_item_code = str_item_code).values('int_qty')[0]['int_qty']

                if int_qty < int_current_quantity:

                    lst_phones=list(BranchStockDetails.objects.filter(fk_master__fk_branch__vchr_code=str_branch_code,fk_item__vchr_item_code = str_item_code).values('jsn_imei_avail','fk_master__dat_stock'))

                    for i in range(len(lst_phones)):

                        lst_phones[i]['days']=(datetime.now()-lst_phones[i]['fk_master__dat_stock']).days
                            #creating a new key days: to store difference between two dates

                    lst_phones=sorted(lst_phones, key = lambda i: i['days'],reverse=True)#sorting the dictionary by days
                    return Response({'status':1,'data':lst_phones,'int_cur_qyty':int_current_quantity})

                else:

                    rst_enquiry=session.query(BranchStockDetailsSA.int_qty.label("int_qty"),BranchSA.vchr_code.label("vchr_branch_code"),BranchSA.flt_latitude.label("flt_latitude"),BranchSA.flt_longitude.label("flt_longitude"),ItemSA.vchr_item_code.label("vchr_item_code"))\
                                .join(BranchStockMasterSA,BranchStockDetailsSA.fk_master_id == BranchStockMasterSA.pk_bint_id)\
                                .join(ItemSA,BranchStockDetailsSA.fk_item_id == ItemSA.pk_bint_id )\
                                .join(BranchSA,BranchStockMasterSA.fk_branch_id==BranchSA.pk_bint_id)\
                                .filter(ItemSA.vchr_item_code==str_item_code,BranchSA.vchr_code!=str_branch_code)

                    flt_cur_branch_coord = Branch.objects.filter(vchr_code=str_branch_code).values('flt_latitude','flt_longitude')[0]
                    #getting flt_latitude and flt_latitude of current branch
                    tpl_cur_coord=(flt_cur_branch_coord['flt_latitude'],flt_cur_branch_coord['flt_longitude'])
                    lst_branch=[]

                    for ins_enquiry in rst_enquiry.all():
                        dct_enquiry={}
                        dct_enquiry['vchr_item_code'] = ins_enquiry.vchr_item_code
                        dct_enquiry['vchr_branch_code'] = ins_enquiry.vchr_branch_code
                        dct_enquiry['int_qty'] = ins_enquiry.int_qty
                        flt_latitude = ins_enquiry.flt_latitude
                        flt_longitude = ins_enquiry.flt_longitude
                        tpl_other_coord=(flt_latitude,flt_longitude)
                        dct_enquiry['distance'] = round(geodesic(tpl_cur_coord,tpl_other_coord).km,2) #geopy function to calculate distance b/w two coordinates
                        lst_branch.append(dct_enquiry)
                        #creating a new dictionary which store all branch code and distance between current branch

                    # lst_branch=[]
                    # flt_cur_branch_coord = Branch.objects.filter(vchr_code=str_branch_code).values('flt_latitude','flt_longitude')[0]
                    # #getting flt_latitude and flt_latitude of current branch
                    # tpl_cur_coord=(flt_cur_branch_coord['flt_longitude'],flt_cur_branch_coord['flt_latitude'])
                    # #storring current cordinates tuple
                    # flt_other_branches= list(Branch.objects.values('vchr_code','flt_latitude','flt_longitude').exclude(vchr_code=str_branch_code))
                    # #gettting all branches flt_latitudes and flt_longitude
                    #
                    # for x in range(len(flt_other_branches)):
                    #     dic_branches={}
                    #     dic_branches['branch']=flt_other_branches[x]['vchr_code']
                    #     tpl_other_coord = (flt_other_branches[x]['flt_longitude'],flt_other_branches[x]['flt_latitude'])
                    #
                    #     dic_branches['distance'] = geodesic(tpl_cur_coord,tpl_other_coord).miles #geopy function to calculate distance b/w two coordinates
                    #     lst_branch.append(dic_branches)
                    #creating a new dictionary which store all branch code and distance between current branch
                    lst_branch=sorted(lst_branch, key = lambda i: i['distance'],reverse=False)  #sorting the dictionary by distance
                    session.close()
                    return Response({'status':1,'data':lst_branch,'int_cur_qyty':int_current_quantity})

            else:
                #else int_qty is None

                int_current_quantity = BranchStockDetails.objects.filter(
                                                        fk_master__fk_branch__vchr_code = str_branch_code,
                                                        fk_item__vchr_item_code = str_item_code).values('int_qty')[0]['int_qty']
                if int_current_quantity >1:
                    lst_phones = list(BranchStockDetails.objects.filter(fk_master__fk_branch__vchr_code=str_branch_code,fk_item__vchr_item_code = str_item_code).values('jsn_imei_avail','fk_master__dat_stock'))

                    for i in range(len(lst_phones)):

                        lst_phones[i]['days'] = (datetime.now()-lst_phones[i]['fk_master__dat_stock']).days
                            #creating a new key days: to store difference between two dates

                    lst_phones=sorted(lst_phones, key = lambda i: i['days'],reverse=True)
                    #sorting the dictionary by days
                    session.close()
                    return Response({'status':1,'data':lst_phones,"int_cur_qty":int_current_quantity})

                else:

                    rst_enquiry = session.query(BranchStockDetailsSA.int_qty.label("int_qty"),BranchSA.vchr_code.label("vchr_branch_code"),BranchSA.flt_latitude.label("flt_latitude"),BranchSA.flt_longitude.label("flt_longitude"),ItemSA.vchr_item_code.label("vchr_item_code"))\
                                .join(BranchStockMasterSA,BranchStockDetailsSA.fk_master_id == BranchStockMasterSA.pk_bint_id)\
                                .join(ItemSA,BranchStockDetailsSA.fk_item_id == ItemSA.pk_bint_id )\
                                .join(BranchSA,BranchStockMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                                .filter(ItemSA.vchr_item_code == str_item_code,BranchSA.vchr_code != str_branch_code)

                    flt_cur_branch_coord = Branch.objects.filter(vchr_code=str_branch_code).values('flt_latitude','flt_longitude')[0]
                    #getting flt_latitude and flt_latitude of current branch
                    tpl_cur_coord = (flt_cur_branch_coord['flt_latitude'],flt_cur_branch_coord['flt_longitude'])
                    lst_branch = []

                    for ins_enquiry in rst_enquiry.all():
                        dct_enquiry={}
                        dct_enquiry['vchr_item_code'] = ins_enquiry.vchr_item_code
                        dct_enquiry['vchr_branch_code'] = ins_enquiry.vchr_branch_code
                        dct_enquiry['int_qty'] = ins_enquiry.int_qty
                        flt_latitude = ins_enquiry.flt_latitude
                        flt_longitude = ins_enquiry.flt_longitude
                        tpl_other_coord=(flt_latitude,flt_longitude)
                        dct_enquiry['distance'] = round(geodesic(tpl_cur_coord,tpl_other_coord).km,2) #geopy function to calculate distance b/w two coordinates
                        lst_branch.append(dct_enquiry)

                    #creating a new dictionary which store all branch code and distance between current branch
                    lst_branch=sorted(lst_branch, key = lambda i: i['distance'],reverse=False)  #sorting the dictionary by distance
                    session.close()
                    return Response({'status':1,'data':lst_branch,'int_cur_qyty':int_current_quantity})






        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
            # else:
            #     rst_enquiry1=session.query(BranchSA.vchr_code.label("vchr_branch_code"),BranchSA.flt_latitude.label("flt_latitude"),BranchSA.flt_longitude.label("flt_longitude").filter(
            #                                                                                             BranchSA.vchr_code==str_branch_code)



class ImeiCheckApi(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            vchr_imei = request.data.get('vchr_imei')
            ins_item_code = BranchStockDetails.objects.filter(jsn_imei_avail__contains = {"imei":[str(vchr_imei)]}).values('fk_item_id__vchr_item_code')
            if ins_item_code:
                vchr_item_code = ins_item_code.first()['fk_item_id__vchr_item_code']
                return Response({'status':1,'data':vchr_item_code})
            else:
                return Response({'status':0,'data':"no item found"})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class StockNearbyBranchsApi(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_branch_code = request.data.get("str_branch_code")
            str_item_code = request.data.get("str_item_code")

            """getting coordinates of current branch"""
            ins_cur_branch_coord = Branch.objects.filter(vchr_code=str_branch_code).values('flt_latitude','flt_longitude')[0]
            tpl_cur_coord = (ins_cur_branch_coord['flt_latitude'],ins_cur_branch_coord['flt_longitude'])

            """getting list of branchs which have stock of the item"""
            ins_branch_stock = BranchStockDetails.objects.filter(fk_item_id__vchr_item_code = str_item_code,int_qty__gt = 0).values('fk_master__fk_branch__vchr_code','fk_master__fk_branch__flt_latitude','fk_master__fk_branch__flt_longitude')

            dct_stock = {}
            for ins_stock in ins_branch_stock:
                tpl_other_coord=(ins_stock['fk_master__fk_branch__flt_latitude'],ins_stock['fk_master__fk_branch__flt_longitude'])
                distance = round(geodesic(tpl_cur_coord,tpl_other_coord).km,2)

                dct_stock[ins_stock['fk_master__fk_branch__vchr_code']] = distance

            lst_branch=sorted(dct_stock, key = lambda i: dct_stock[i],reverse=False)
            if lst_branch:
                return Response({'status':1,'data':lst_branch})
            else:
                return Response({'status':0,'data':"no branchs found"})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class ItemAgingCheck(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            # import pdb; pdb.set_trace()
            str_branch_code = request.data.get("str_branch_code")
            str_item_code = request.data.get("str_item_code")
            str_imei = request.data.get("str_imei")
            lst_select_imei = request.data.get("lst_imei")
            """getting date of current imei-item"""
            imei_found = True
            dat_current_imei = BranchStockDetails.objects.filter(Q(fk_item_id__vchr_item_code = str_item_code,fk_master__fk_branch__vchr_code = str_branch_code) | Q(fk_item_id__vchr_item_code = str_item_code,fk_master__fk_branch__vchr_code = str_branch_code),int_qty__gt = 0).values('fk_master__dat_stock','int_qty')
            # dat_current_imei = BranchStockDetails.objects.filter(Q(fk_item_id__vchr_item_code = str_item_code,fk_master__fk_branch__vchr_code = str_branch_code,jsn_imei_avail__contains = {"imei":[str(str_imei)]}) | Q(fk_item_id__vchr_item_code = str_item_code,fk_master__fk_branch__vchr_code = str_branch_code,jsn_batch_no__contains = {"batch":[str(str_imei)]})).values('fk_master__dat_stock')
            """getting list of items with aging"""
            if not dat_current_imei:
                imei_found = False
                dat_current_imei = datetime.now()
            if dat_current_imei:
                if imei_found:
                    int_batch_count=dat_current_imei.first()['int_qty']
                    dat_current_imei = dat_current_imei.first()['fk_master__dat_stock']
                # rst_aging_item = BranchStockDetails.objects.filter(fk_item_id__vchr_item_code = str_item_code,fk_master__fk_branch__vchr_code = str_branch_code,int_qty__gt = 0,fk_master__dat_stock__date__lt = dat_current_imei).values('fk_master__dat_stock','jsn_imei_avail')
                rst_aging_item = BranchStockDetails.objects.filter(fk_item_id__vchr_item_code = str_item_code,fk_master__fk_branch__vchr_code = str_branch_code,int_qty__gt = 0).values('fk_master__dat_stock','jsn_imei_avail','jsn_batch_no','int_qty').order_by('fk_master__dat_stock')
                if rst_aging_item and imei_found:
                    lst_imei_data = []

                    dat_today = datetime.now()
                    for ins_data in rst_aging_item:
                        if ins_data['jsn_imei_avail']['imei']:
                            for ins_imei in ins_data['jsn_imei_avail']['imei']:
                                dct_imei = {}
                                if lst_select_imei:
                                    if ins_imei in lst_select_imei:
                                        continue
                                dct_imei['imei'] = ins_imei
                                dct_imei['day'] = (dat_today - ins_data['fk_master__dat_stock']).days
                                dct_imei['count']=1

                                lst_imei_data.append(dct_imei)

                        else:
                            if ins_data.get('int_qty'):
                                dct_imei = {}
                                dct_imei['imei'] = ins_data['jsn_batch_no']['batch'][0]
                                dct_imei['day'] = (dat_today - ins_data['fk_master__dat_stock']).days
                                dct_imei['count']=ins_data['int_qty']
                                lst_imei_data.append(dct_imei)
                    # lst_item = [{
                    #     'imei':'54654654684',
                    #     'day':4,
                    #     'count':1
                    # }]

                    # import pdb; pdb.set_trace()
                    lst_imei =sorted(lst_imei_data, key = lambda i: i['day'],reverse=True)
                    #lst_imei = lst_imei[:5]
                    # if imei_found:
                    #     dct_imei_new={}
                    #     # dct_imei_new['imei'] = str_imei/
                    #     dct_imei_new['day'] = (dat_today - dat_current_imei).days
                    #     lst_imei.append(dct_imei_new)

                    ins_non_sale=NonSaleable.objects.filter(fk_branch__vchr_code=str_branch_code,fk_item__vchr_item_code=str_item_code,int_status=0).values('jsn_non_saleable').first()
                    if ins_non_sale:
                        lst_no_sale_data=ins_non_sale['jsn_non_saleable']
                        lst_imei=[data for data in lst_imei if data['imei'] not in lst_no_sale_data]
                    lst_imei = lst_imei[:5]
                    return Response({'status':1,'data':lst_imei})
                else:
                    if imei_found:
                        return Response({'status':0,'data':"no aged imeis found"})
                    else:
                        return Response({'status':-1,'data':"no item found with correspond imeis"})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})



class StockCheck(APIView):
    """
        To check the availability of the item in the current branch.
        param : str_branch_code,str_item_code
        return : count of available item

    """
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            int_qty = request.data.get("int_qty")
            str_branch_code = request.data.get("str_branch_code")
            str_item_code = request.data.get("str_item_code")
            #getting inputs from user
            # import pdb; pdb.set_trace()
            session = Session()
            int_current_quantity = BranchStockDetails.objects.filter(fk_master__fk_branch__vchr_code = str_branch_code,fk_item__vchr_item_code = str_item_code).values('fk_master__fk_branch__vchr_code','fk_item__vchr_item_code').annotate(total_qty = Sum('int_qty',output_field = IntegerField()))

            if not int_current_quantity:
                session.close()
                return Response({'status':0,'message':'Item not available','int_cur_qyty':int_current_quantity})

            # Take non saleable IMEIs of the item and count of IMEIs substract from count of items in branch stock
            ins_non_sale=NonSaleable.objects.filter(fk_branch__vchr_code=str_branch_code,fk_item__vchr_item_code=str_item_code,int_status=0).values('jsn_non_saleable').first()
            if ins_non_sale:
                count_no_sale=len(ins_non_sale['jsn_non_saleable'])
                int_current_quantity[0]['total_qty'] -= count_no_sale


            if (int_qty < int_current_quantity[0]['total_qty']) or (int_qty == int_current_quantity[0]['total_qty']):
                str_message = 'Item Available'
                int_status = 1
            elif  int_current_quantity[0]['total_qty'] <= 0:
                str_message = 'Item not available'
                int_status = 0
            else:
                str_message = 'Only '+ str(int_current_quantity[0]['total_qty']) +" in stock. "
                int_status = -1
            session.close()
            return Response({'status':int_status,'message':str_message,'int_avail_qty':int_current_quantity[0]['total_qty']})

        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class EcomStockCheck(APIView):
    """
        To check the availability of the item in the current branch.
        param : str_branch_code,str_item_code
        return : count of available item

    """
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            int_selected_batch_count = request.data.get("batchCount")
            str_imei = request.data.get("strImei")
            str_item_code = request.data.get("strItemCode")
            str_branch_code = request.data.get("branchCode")
            bln_imei_status = request.data.get("blnImeiStatus")
            #getting inputs from user
            int_current_quantity = None


            # session = Session()
            if bln_imei_status:
                int_current_quantity = BranchStockDetails.objects.filter(fk_master__fk_branch__vchr_code = str_branch_code,fk_item__vchr_item_code = str_item_code,jsn_imei_avail__icontains = str_imei,int_qty__gt = 0)
                if not int_current_quantity:
                    return Response({'status':0,'message':'Imei not available'})


            else:
                int_current_quantity = BranchStockDetails.objects.filter(fk_master__fk_branch__vchr_code = str_branch_code,fk_item__vchr_item_code = str_item_code,jsn_batch_no__icontains = str_imei,int_qty__gt = 0).annotate(total_qty = Sum('int_qty',output_field = IntegerField()))
                if int_current_quantity:
                    int_batch_qty =  int_current_quantity[0].total_qty

                    if int_batch_qty<int_selected_batch_count:
                        return Response({'status':0,'message':'Batch number not available'})
                else :
                    return Response({'status':0,'message':'Batch number not available'})








            return Response({'status':1,'message':'Item available'})

            # Take non saleable IMEIs of the item and count of IMEIs substract from count of items in branch stock
            # ins_non_sale= NonSaleable.objects.filter(fk_branch__vchr_code=str_branch_code,fk_item__vchr_item_code=str_item_code,int_status=0).values('jsn_non_saleable').first()
            # if ins_non_sale:
            #     count_no_sale=len(ins_non_sale['jsn_non_saleable'])
            #     int_current_quantity[0]['total_qty'] -= count_no_sale
            #
            #
            # if (int_qty < int_current_quantity[0]['total_qty']) or (int_qty == int_current_quantity[0]['total_qty']):
            #     str_message = 'Item Available'
            #     int_status = 1
            # elif  int_current_quantity[0]['total_qty'] <= 0:
            #     str_message = 'Item not available'
            #     int_status = 0
            # else:
            #     str_message = 'Only '+ str(int_current_quantity[0]['total_qty']) +" in stock. "
            #     int_status = -1
            # session.close()
            # return Response({'status':int_status,'message':str_message,'int_avail_qty':int_current_quantity[0]['total_qty']})

        except Exception as e:
            session.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str_message,'int_avail_qty':int_current_quantity[0]['total_qty']})



class CustomerTypeahead(APIView):
    permission_classes=[IsAuthenticated]
    """this class was taken from bi suite to get customer deatils using
    customer mobile number
    """
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            str_username = request.data.get('username')
            ins_user = UserDetails.objects.get(username = str_username)
            lst_customers = []
            if str_search_term != -1:
                # .filter(fk_company = ins_user.fk_company)\
                ins_customer = CustomerDetails.objects.filter(Q(int_mobile__icontains=str_search_term))\
                .values('pk_bint_id','int_mobile','vchr_name','vchr_email','cust_salutation','int_cust_type','cust_smsaccess')[:50]
                if ins_customer:
                    for itr_item in ins_customer:
                        dct_customer = {}
                        dct_customer['mobile'] = itr_item['int_mobile']
                        dct_customer['fname'] = itr_item['vchr_name'].capitalize()
                        dct_customer['lname'] = "".capitalize()
                        dct_customer['id'] = itr_item['pk_bint_id']
                        dct_customer['email'] = itr_item['vchr_email']
                        dct_customer['salutation'] = itr_item['cust_salutation']
                        dct_customer['customertype'] = itr_item['int_cust_type']
                        dct_customer['sms'] = itr_item['cust_smsaccess']
                        lst_customers.append(dct_customer)
                return Response({'status':'success','data':lst_customers})
            else:
                return Response({'status':'empty','data':lst_customers})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'1','data':str(e)})

from aldjemy.core import get_engine
class MobileBranchReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            session = Session()
            dct_data={}
            int_company = request.data['company_id']
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
            # lst_branch = list(Branch.objects.filter(fk_company_id = ins_company[0].pk_bint_id).values())
            lst_branch = list(Branch.objects.all().values())
            fromdate =  request.data['date_from']
            todate =  request.data['date_to']
            # todate = todate + timedelta(days = 1)
            if request.data.get('show_type'):
                str_show_type = 'total_amount'
            else:
                str_show_type = 'int_quantity'


            # rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
            # rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
            # rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
            # rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
            # rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
            # rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service, CustomerModelSA.cust_fname.label('customer_first_name'),\
            #     CustomerModelSA.cust_lname.label('customer_last_name'),rst_data.c.status,CustomerModelSA.cust_mobile.label('customer_mobile'),AuthUserSA.id.label('user_id'),AuthUserSA.first_name.label('staff_first_name'),\
            #     AuthUserSA.last_name.label('staff_last_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name)\
            #     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == request.data['company_id'])\
            #     .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id))\
            #     .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
            #     .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
            #     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).join(UserSA, AuthUserSA.id == UserSA.user_ptr_id)\
            #     .join(BrandsSA,BrandsSA.id==rst_data.c.brand_id)\
            #     .join(ItemsSA,ItemsSA.id==rst_data.c.item_id)



            # materialized views
            engine = get_engine()
            conn = engine.connect()

            lst_mv_view = []
            lst_mv_view = request.data.get('lst_mv')
            # lst_mv_view = ['mv_enquiry_data']

            if not lst_mv_view:
                session.close()
                return Response({'status':'failed', 'reason':'No view list found'})
            query_set = ""
            if len(lst_mv_view) == 1:

                if request.data['type'].upper() == 'ENQUIRY':

                    query = "select vchr_enquiry_status as status, sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty, vchr_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name, user_id as fk_assigned, staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id, branch_name from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id, branch_name"
                else:

                    query = "select vchr_enquiry_status as status, sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name,user_id as fk_assigned,staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id, branch_name from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id, branch_name"

            else:

                if request.data['type'].upper() == 'ENQUIRY':

                    for data in lst_mv_view:
                        query_set += "select vchr_enquiry_status as status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned, branch_id, product_id, brand_id, branch_name from "+data+" {} group by  vchr_enquiry_status , vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned, branch_id, product_id, brand_id, branch_name union "
                else:

                     for data in lst_mv_view:

                        query_set +="select vchr_enquiry_status as status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty,user_id as fk_assigned, vchr_brand_name, vchr_item_name,promoter,is_resigned,branch_id, product_id, brand_id, branch_name from "+data+" {} group by vchr_enquiry_status, vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter,is_resigned,branch_id, product_id, brand_id, branch_name union "

                query = query_set.rsplit(' ', 2)[0]

            # rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status.label('status'),func.count(ProductsSA.vchr_product_name).label('counts'),
            #                     ProductsSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
            #                     AuthUserSA.last_name).label('vchr_staff_full_name'),
            #                     EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),
            #                     AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
            #                     AuthUserSA.first_name.label('staff_first_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
            #                     UserSA.fk_brand_id,UserSA.dat_resignation_applied,
            #                     # case([(UserSA.fk_brand_id > 0,literal_column("'promoter'"))],
            #                     #     else_=literal_column("'not promoter'")).label('is_promoter'),
            #                     case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
            #                         else_=literal_column("'not resigned'")).label("is_resigned"))\
            #                     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
            #                             cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
            #                             EnquiryMasterSA.fk_company_id == request.user.usermodel.fk_company_id,
            #                             EnquiryMasterSA.chr_doc_status == 'N')\
            #                     .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
            #                     .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
            #                     .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
            #                     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
            #                     .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
            #                     .join(ProductsSA,ProductsSA.id == ItemEnquirySA.fk_product_id)\
            #                     .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
            #                     .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)\
            #                     .group_by(ProductsSA.vchr_product_name,BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
            #                               ItemEnquirySA.vchr_enquiry_status,AuthUserSA.id,EnquiryMasterSA.fk_assigned_id,
            #                               UserSA.fk_brand_id,UserSA.dat_resignation_applied)
            """ data wise filtering """

            str_filter_data = "where dat_enquiry :: date BETWEEN '"+fromdate+"' AND '"+request.data['date_to']+"' AND int_company_id = "+int_company+""

            """Permission wise filter for data"""
            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.userdetails.fk_branch_id)+""
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
            elif request.user.userdetails.int_area_id:
                lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)

                str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"


                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
            else:
                session.close()
                return Response({'status':'failed','reason':'No data'})

            if request.data.get('branch'):

                str_filter_data += " AND branch_id IN ("+str(request.data.get('branch'))[1:-1]+")"
                # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(tuple(request.data.get('branch'))))

            # rst_enquiry = reversed(sorted(rst_enquiry, key=lambda k: (k.dat_followup)))

            if request.data.get('product'):

                str_filter_data += " AND product_id = "+str(request.data.get('product'))+""
                # rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_product_id == request.data.get('product'))
            if request.data.get('brand'):

                str_filter_data += " AND brand_id = "+str(request.data.get('brand'))+""

            # import pdb; pdb.set_trace()
            #for getting user corresponding products
            lst_user_id =[]
            lst_user_id.append(request.user.id)

            lst_user_products = get_user_products(lst_user_id)
            if lst_user_products:
                str_filter_data += " AND product_id in ("+str(lst_user_products)[1:-1]+")"



            if len(lst_mv_view) == 1:
                query = query.format(str_filter_data)
            else:
                query = query.format(str_filter_data,str_filter_data)
            rst_enquiry = conn.execute(query).fetchall()
            # import pdb; pdb.set_trace()
            if not rst_enquiry:
                return Response({'status': 0,'data':'No Data'})
    
            """structuring for branch report"""
            if request.data['type'].upper() == 'ENQUIRY':
                dct_data = structure_data_for_report_old(request,rst_enquiry)
            else:
                dct_data = structure_data_for_report_new(request,rst_enquiry)

            session.close()
            return Response({'status': 1,'data':dct_data})
        except Exception as e:
            session.close()
            return Response({'status':0,'data':str(e)})



def structure_data_for_report_old(request,rst_enquiry):
    try:
        dct_data={}
        dct_data['branch_all']={}
        dct_data['service_all']={}
        dct_data['brand_all']={}
        dct_data['item_all']={}
        dct_data['status_all']={}
        dct_data['branch_service']={}
        dct_data['branch_brand']={}
        dct_data['branch_item']={}
        dct_data['branch_status']={}
        dct_data['branch_service_brand']={}
        dct_data['branch_service_item']={}
        dct_data['branch_service_status']={}
        dct_data['branch_service_brand_item']={}
        dct_data['branch_service_brand_status']={}
        dct_data['branch_service_brand_item_status']={}

        for ins_data in rst_enquiry:
            if ins_data.branch_name.title() not in dct_data['branch_all']:
                dct_data['branch_all'][ins_data.branch_name.title()]={}
                dct_data['branch_all'][ins_data.branch_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_all'][ins_data.branch_name.title()]['Sale']=0
                dct_data['branch_all'][ins_data.branch_name.title()]['SaleQty']=0
                dct_data['branch_all'][ins_data.branch_name.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_all'][ins_data.branch_name.title()]['Sale'] = ins_data.counts
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleValue'] = ins_data.value

                dct_data['branch_service'][ins_data.branch_name.title()]={}
                dct_data['branch_brand'][ins_data.branch_name.title()]={}
                dct_data['branch_item'][ins_data.branch_name.title()]={}
                dct_data['branch_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=0
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=0
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=0
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']=0
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=ins_data.counts
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=ins_data.value
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']=ins_data.value

                dct_data['branch_service_brand'][ins_data.branch_name.title()]={}
                dct_data['branch_service_item'][ins_data.branch_name.title()]={}
                dct_data['branch_service_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=0
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=ins_data.value

                dct_data['branch_service_brand_item'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value

                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
            else:
                dct_data['branch_all'][ins_data.branch_name.title()]['Enquiry']+=ins_data.counts
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['branch_all'][ins_data.branch_name.title()]['Sale']+=ins_data.counts
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service'][ins_data.branch_name.title()]:
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=0
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=0
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=ins_data.counts
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Enquiry']+=ins_data.counts
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']+=ins_data.counts
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']+=ins_data.qty
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']+=ins_data.value
                if ins_data.vchr_brand_name.title() not in dct_data['branch_brand'][ins_data.branch_name.title()]:
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value
                if ins_data.vchr_item_name.title() not in dct_data['branch_item'][ins_data.branch_name.title()]:
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                if ins_data.status not in dct_data['branch_status'][ins_data.branch_name.title()]:
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue'] = ins_data.value
                else:
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Enquiry']+=ins_data.counts
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']+=ins_data.counts
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']+=ins_data.qty
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service_brand'][ins_data.branch_name.title()]:
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]={}
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=ins_data.value
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                else:
                    if ins_data.vchr_brand_name.title() not in dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    else:
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value
                    if ins_data.vchr_item_name.title() not in dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    else:
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                    if ins_data.status not in dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]={}
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']=ins_data.counts
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=0
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=0
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=ins_data.counts
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=ins_data.qty
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=ins_data.value
                    else:

                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']+=ins_data.counts
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']+=ins_data.counts
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']+=ins_data.qty
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service_brand_item'][ins_data.branch_name.title()]:
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value
                else:
                    if ins_data.vchr_brand_name.title() not in dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value
                    else:
                        if ins_data.vchr_item_name.title() not in dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]:
                            # Initialize Enquiry as 1 and Sale as 0
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0

                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        else:
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                        if ins_data.status not in dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]:
                            # Initialize Enquiry as 1 and Sale as 0
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0

                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value
                        else:
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']+=ins_data.counts
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']+=ins_data.counts
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']+=ins_data.qty
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()]:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                elif ins_data.vchr_brand_name.title() not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                elif ins_data.vchr_item_name.title() not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                elif ins_data.status not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']+=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']+=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']+=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']+=ins_data.value
            if ins_data.vchr_service.title() not in dct_data['service_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['service_all'][ins_data.vchr_service.title()]={}
                dct_data['service_all'][ins_data.vchr_service.title()]['Enquiry']=ins_data.counts
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryQty']=ins_data.qty
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryValue']=ins_data.value
                dct_data['service_all'][ins_data.vchr_service.title()]['Sale']=0
                dct_data['service_all'][ins_data.vchr_service.title()]['SaleQty']=0
                dct_data['service_all'][ins_data.vchr_service.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['service_all'][ins_data.vchr_service.title()]['Sale']=ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleQty']=ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleValue']=ins_data.value
            else:
                dct_data['service_all'][ins_data.vchr_service.title()]['Enquiry']+=ins_data.counts
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryQty']+=ins_data.qty
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['service_all'][ins_data.vchr_service.title()]['Sale']+=ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleQty']+=ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleValue']+=ins_data.value
            if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
            else:
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value
            if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
            else:
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
            if ins_data.status not in dct_data['status_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['status_all'][ins_data.status]={}
                dct_data['status_all'][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['status_all'][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['status_all'][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['status_all'][ins_data.status]['Sale']=0
                dct_data['status_all'][ins_data.status]['SaleQty']=0
                dct_data['status_all'][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['status_all'][ins_data.status]['Sale']=ins_data.counts
                    dct_data['status_all'][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['status_all'][ins_data.status]['SaleValue']=ins_data.value
            else:
                dct_data['status_all'][ins_data.status]['Enquiry']+=ins_data.counts
                dct_data['status_all'][ins_data.status]['EnquiryQty']+=ins_data.qty
                dct_data['status_all'][ins_data.status]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['status_all'][ins_data.status]['Sale']+=ins_data.counts
                    dct_data['status_all'][ins_data.status]['SaleQty']+=ins_data.qty
                    dct_data['status_all'][ins_data.status]['SaleValue']+=ins_data.value

        dct_data['brand_all']=paginate_data(dct_data['brand_all'],10)
        dct_data['branch_all']=paginate_data(dct_data['branch_all'],10)
        dct_data['item_all']=paginate_data(dct_data['item_all'],10)
        dct_data['service_all']=paginate_data(dct_data['service_all'],10)

        for key in dct_data['branch_service']:
                dct_data['branch_service'][key]=paginate_data(dct_data['branch_service'][key],10)
        for key in dct_data['branch_brand']:
                dct_data['branch_brand'][key]=paginate_data(dct_data['branch_brand'][key],10)
        for key in dct_data['branch_item']:
                dct_data['branch_item'][key]=paginate_data(dct_data['branch_item'][key],10)
        for key in dct_data['branch_service_brand']:
            for key1 in dct_data['branch_service_brand'][key]:
                dct_data['branch_service_brand'][key][key1]=paginate_data(dct_data['branch_service_brand'][key][key1],10)
        for key in dct_data['branch_service_item']:
            for key1 in dct_data['branch_service_item'][key]:
                dct_data['branch_service_item'][key][key1]=paginate_data(dct_data['branch_service_item'][key][key1],10)
        # import pdb;pdb.set_trace()
        for key in dct_data['branch_service_brand_item']:
            for key1 in dct_data['branch_service_brand_item'][key]:
                for key2 in dct_data['branch_service_brand_item'][key][key1]:
                    dct_data['branch_service_brand_item'][key][key1][key2]=paginate_data(dct_data['branch_service_brand_item'][key][key1][key2],10)


        return dct_data
    except Exception as msg:
        return str(msg)



"""structuring for branch report"""
def structure_data_for_report_new(request,rst_enquiry):
    try:
        # import pdb; pdb.set_trace()
        dct_data={}
        dct_data['IN_IT'] = {}

        if request.data['type'] == 'Sale':
            dct_data['BRANCH_SERVICE_BRAND_ITEM']={}

        elif request.data['type'] == 'Enquiry':
            dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']={}

        for ins_data in rst_enquiry:
            """sales -> branch report """
            if request.data['type'] == 'Sale':
                if ins_data.branch_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.status == 'INVOICED':
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value


                elif ins_data.vchr_service.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value


                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value


                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value


                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                elif ins_data.vchr_brand_name.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value


                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                elif ins_data.vchr_item_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                else:
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']+=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']+=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']+=ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']+=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']+=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']+=ins_data.value



            elif request.data['type'] == 'Enquiry':
                """enquiry -> branch report"""
                if ins_data.branch_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]  =  {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value



                elif ins_data.vchr_service.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_brand_name.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_item_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                elif ins_data.status not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                else:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] += ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] += ins_data.value



            # import pdb; pdb.set_trace()
        if request.data['type'] == 'Sale':

            """top 5 branch->product->brand->item"""
            dct_data['IN_IT']['BRANCHS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][i]['Sale']),reverse =True)[0]
            top_branch = dct_data['IN_IT']['BRANCHS']
            dct_data['IN_IT']['SERVICE'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][i]['Sale']),reverse =True)[0]
            top_product = dct_data['IN_IT']['SERVICE']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'][i]['Sale']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEMS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][i]['Sale']),reverse =True)[0]

            """paginating"""
            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE']:
                    for key2 in dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS']:
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE']:
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM']:
                dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'],10)

            dct_data['BRANCH_SERVICE_BRAND_ITEM'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'],10)


        elif request.data['type'] == 'Enquiry':

            """top 5 branch->product->brand->item->status"""
            dct_data['IN_IT']['BRANCHS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][i]['Enquiry']),reverse =True)[0]
            top_branch = dct_data['IN_IT']['BRANCHS']
            dct_data['IN_IT']['SERVICE'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][i]['Enquiry']),reverse =True)[0]
            top_product = dct_data['IN_IT']['SERVICE']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][i]['Enquiry']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEMS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][i]['Enquiry']),reverse =True)[0]
            top_item = dct_data['IN_IT']['ITEMS']
            dct_data['IN_IT']['STATUS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STATUS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STATUS'][i]['Enquiry']),reverse =True)[0]

            """paginating"""
            # for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
            #     for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
            #         for key2 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']:
            #             for key3 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']:
            #                 dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'][key3]['STATUS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'][key3]['STATUS'],10)
            #
            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
                    for key2 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']:
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
                dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'],10)

            dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'],10)






        return dct_data
    except Exception as msg:
        return str(msg)


def key_sort_sale_new(tup):
    key,data = tup
    return -data['Sale']
def key_sort_new(tup):
    key,data = tup
    return -data['Enquiry']



def paginate_data_new(request,dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    if request.data.get('type') == 'Sale':
        sorted_dct_data = sorted(dct_data.items(),key= key_sort_sale_new)
    else:
        sorted_dct_data = sorted(dct_data.items(),key= key_sort_new)

    dct_data = OrderedDict(sorted_dct_data)
    for key in dct_data:
        if int_count not in dct_paged:
            dct_paged[int_count]={}
            dct_paged[int_count][key]=dct_data[key]
        elif len(dct_paged[int_count]) < int_page_legth:
            dct_paged[int_count][key]= dct_data[key]
        else:
            int_count += 1
            dct_paged[int_count] ={}
            dct_paged[int_count][key] = dct_data[key]
    return dct_paged



