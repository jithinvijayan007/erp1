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
                .values('id','int_mobile','vchr_name','cust_email','cust_salutation','cust_customertype','cust_smsaccess')[:50]
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
