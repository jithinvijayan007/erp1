from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from customer.models import CustomerDetails,SalesCustomerDetails
from invoice.models import SalesDetails,SalesMaster
from accounts_map.models import AccountsMap

from datetime import datetime
from POS import ins_logger
import sys, os
from datetime import datetime
from sales_return.models import SalesReturn
from sqlalchemy.orm.session import sessionmaker
from item_category.models import Item,TaxMaster
from django.db.models import Count,Sum

from global_methods import check_if_imei_exist


def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

SalesReturnSA = SalesReturn.sa
SalesDetailsSA = SalesDetails.sa
SalesMasterSA = SalesMaster.sa

# Create your views here.
class GetDetails(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dct_details_id = {}
            lst_imei = [request.data.get('imei')]
            int_customer = request.data.get('int_customer')
            str_invoice_no = request.data.get('invoiceNo')
            str_invoice = ""
            bln_igst=False
            # int_customer
            int_customerdetails=CustomerDetails.objects.get(pk_bint_id=int_customer).fk_state_id
            if request.user.userdetails.fk_branch.fk_states_id!=int_customerdetails:
                bln_igst=True
            if request.data.get('imei'):
                lst_imei = [request.data.get('imei')]
                rst_customer_current_status = SalesDetails.objects.filter(json_imei__contains=lst_imei).values('fk_master__fk_customer__fk_customer__fk_state_id','fk_master__fk_customer__fk_customer__fk_state__vchr_name','fk_master__fk_customer__fk_customer__vchr_gst_no')
                rst_customer_sale_status = SalesDetails.objects.filter(json_imei__contains=lst_imei).values('fk_master__fk_customer__fk_state_id','fk_master__fk_customer__fk_state__vchr_name','fk_master__fk_customer__vchr_gst_no')

                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state_id'] !=  rst_customer_sale_status[0]['fk_master__fk_customer__fk_state_id']:
                    if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state__vchr_name'].upper() !='KERALA' and rst_customer_sale_status[0]['fk_master__fk_customer__fk_state__vchr_name'].upper() !='KERALA' :
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if not rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})


                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if not rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if int_customer:
                    ins_sales_details = SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status = 1,fk_master__fk_customer_id__fk_customer_id=int_customer).values('pk_bint_id','fk_master__vchr_invoice_num','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                else:
                    ins_sales_details = SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                if not ins_sales_details:
                    return Response({'status':0,'message':"Item is not Purchased by this Customer"})
                str_invoice = ins_sales_details.first()['fk_master__vchr_invoice_num']
            elif request.data.get('datFrom'):
                dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d').date()
                dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d').date()
                if int_customer:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id__fk_customer_id=int_customer,fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                else:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')

            elif str_invoice_no :
                rst_customer_current_status = SalesDetails.objects.filter(fk_master__vchr_invoice_num=str_invoice_no).values('fk_master__fk_customer__fk_customer__fk_state_id','fk_master__fk_customer__fk_customer__fk_state__vchr_name','fk_master__fk_customer__fk_customer__vchr_gst_no')
                rst_customer_sale_status = SalesDetails.objects.filter(fk_master__vchr_invoice_num=str_invoice_no).values('fk_master__fk_customer__fk_state_id','fk_master__fk_customer__fk_state__vchr_name','fk_master__fk_customer__vchr_gst_no')

                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state_id'] !=  rst_customer_sale_status[0]['fk_master__fk_customer__fk_state_id']:
                    if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state__vchr_name'].upper() !='KERALA' and rst_customer_sale_status[0]['fk_master__fk_customer__fk_state__vchr_name'].upper() !='KERALA' :
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if not rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if not rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if int_customer:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status = 1,fk_master__fk_customer_id__fk_customer_id=int_customer).values('pk_bint_id','fk_master__vchr_invoice_num','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                else:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                str_invoice = str_invoice_no
                if not ins_sales_details:
                    return Response({'status':0,'message':"Item is not Purchased by this Customer"})

            else:
                if int_customer:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id__fk_customer_id=int_customer,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','dbl_indirect_discount','fk_master__jsn_deduction','fk_master__jsn_addition','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                # else:
                #     ins_sales_details = SalesDetails.objects.filter(int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                str_invoice = ins_sales_details.first()['fk_master__vchr_invoice_num']
                # ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
            # ins_sales_details = ins_sales_details.exclude(json_imei__in =  SalesReturn.objects.filter(fk_returned__vchr_invoice_num = str_invoice_no).values_list('jsn_imei',flat=True))

            lst_imei_returned = [ x.get('jsn_imei')[0] for x in SalesReturn.objects.filter(fk_returned__vchr_invoice_num = str_invoice).values('jsn_imei')]


            # lst_imei_sales_details = [x['json_imei'] for x in ins_sales_details]

            # SalesReturn.objects.filter(fk_returned__vchr_invoice_num = str_invoice_no,jsn_imei__in = lst_imei_sales_details).values('jsn_imei')

            # import pdb; pdb.set_trace()

            if ins_sales_details:
                lst_master_id = ins_sales_details.values_list('fk_master_id',flat=True).distinct('fk_master_id')
                lst_excluded_master_id = SalesReturn.objects.filter(fk_returned_id__in=lst_master_id).values_list('fk_returned_id')
                if lst_excluded_master_id:
                    ins_sales_details = ins_sales_details.exclude(fk_master_id__in = lst_excluded_master_id)
                lst_data=[]
                dct_tax_master = dict(TaxMaster.objects.values_list('vchr_name','pk_bint_id'))
                # dct_addition_deduction = dict(AccountsMap.objects.filter(int_status=0,vchr_module_name__in=['ADDITIONS','DEDUCTIONS']).values_list('pk_bint_id','vchr_category_name'))
                # for ins_tax in TaxMaster.objects.values('pk_bint_id','vchr_name'):
                #     dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
                if request.data.get('imei'):
                    for ins_data in ins_sales_details:
                    # if request.data.get('imei') not in lst_imei_returned:
                        ins_items = Item.objects.filter(vchr_item_code = ins_data['fk_item__vchr_item_code'],int_status=0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()
                        dct_details_id[ins_data['pk_bint_id']]=ins_data['int_qty']
                        dct_data={}
                        # dct_data['tax']={'dblCGST': 0, 'dblIGST': 0, 'dblSGST': 0}
                        dct_data['int_id']=ins_data['pk_bint_id']
                        dct_data['enquiry_num']=ins_data['fk_master__vchr_invoice_num']
                        dct_data['item_id']=ins_data['fk_item__pk_bint_id']
                        dct_data['item']=ins_data['fk_item__vchr_name']
                        dct_data['dblIndirectDis']=ins_data['dbl_indirect_discount']

                        dct_data['item_code']=ins_data['fk_item__vchr_item_code']
                        dct_data['imei']=request.data.get('imei')
                        dct_data['dbl_amount']=ins_data['dbl_amount']
                        # dct_data['dbl_Amount']=ins_data['dbl_amount']
                        dct_data['dblMopAmount']=ins_data['dbl_amount']
                        dct_data['dblMarginAmount']=ins_data['dbl_amount']

                        dct_data['dbl_buy_back']=ins_data['dbl_buyback']
                        dct_data['dbl_discount']=ins_data['dbl_discount']
                        dct_data['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(str(dct_tax_master['IGST']),0))
                        dct_data['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(str(dct_tax_master['CGST']),0))
                        dct_data['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(str(dct_tax_master['SGST']),0))
                        if bln_igst:
                            dct_data['GST']=dct_data['dblIGSTPer']
                        else:
                            dct_data['GST']=dct_data['dblSGSTPer']+dct_data['dblCGSTPer']
                        dct_data['tax'] = {}
                        for data in ins_data['json_tax']:
                            if ins_data['json_tax'][data]!=0:
                                dct_data['tax'][data] = ins_data['json_tax'][data]/ins_data['int_qty']
                            else:
                                dct_data['tax'][data] = ins_data['dbl_amount']*float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master[data[3:]],0))/100
                        # dct_data['tax']= {data:ins_data['json_tax'][data]/ins_data['int_qty'] for data in ins_data['json_tax'] if ins_data['json_tax'][data]!=0}
                        dct_data['dbl_selling_price']=ins_data['dbl_selling_price']/ins_data['int_qty']
                        dct_data['int_master_id']=ins_data['fk_master__pk_bint_id']

                        lst_data.append(dct_data)
                else:
                    for ins_data in ins_sales_details:
                        dct_details_id[ins_data['pk_bint_id']]=ins_data['int_qty']
                        for idx in range(0,ins_data['int_qty']):
                            if (not ins_data['json_imei']) or (ins_data['json_imei'] and ins_data['json_imei'][idx] not in lst_imei_returned):
                                # ins_data['json_imei'].get('idx') if ins_data.get('json_imei') else ''
                                ins_items = Item.objects.filter(vchr_item_code = ins_data['fk_item__vchr_item_code'],int_status=0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()

                                dct_data={}
                                # dct_data['tax']={'dblCGST': 0, 'dblIGST': 0, 'dblSGST': 0}
                                dct_data['int_id']=ins_data['pk_bint_id']
                                dct_data['enquiry_num']=ins_data['fk_master__vchr_invoice_num']
                                dct_data['item']=ins_data['fk_item__vchr_name']
                                dct_data['item_code']=ins_data['fk_item__vchr_item_code']
                                dct_data['item_id']=ins_data['fk_item__pk_bint_id']
                                dct_data['imei']=ins_data['json_imei'][idx] if ins_data.get('json_imei') else ''
                                dct_data['dbl_amount']=ins_data['dbl_amount']
                                dct_data['dbl_buy_back']=ins_data['dbl_buyback']
                                dct_data['dbl_discount']=ins_data['dbl_discount']
                                dct_data['dbl_amount']=ins_data['dbl_amount']
                                dct_data['dblIndirectDis']=ins_data['dbl_indirect_discount']

                        # dct_data['dbl_Amount']=ins_data['dbl_amount']
                                dct_data['dblMopAmount']=ins_data['dbl_amount']
                                dct_data['dblMarginAmount']=ins_data['dbl_amount']
                                dct_data['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(str(dct_tax_master['IGST']),0))
                                dct_data['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(str(dct_tax_master['CGST']),0))
                                dct_data['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(str(dct_tax_master['SGST']),0))
                                dct_data['tax'] = {}
                                if bln_igst:
                                    dct_data['GST']=dct_data['dblIGSTPer']
                                else:
                                    dct_data['GST']=dct_data['dblSGSTPer']+dct_data['dblCGSTPer']

                                for data in ins_data['json_tax']:
                                    if ins_data['json_tax'][data]!=0:
                                        dct_data['tax'][data] = ins_data['json_tax'][data]/ins_data['int_qty']
                                    else:
                                        dct_data['tax'][data] = ins_data['dbl_amount']*float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master[data[3:]],0))/100
                                # dct_data['tax']= {data:ins_data['json_tax'][data]/ins_data['int_qty'] for data in ins_data['json_tax'] if ins_data['json_tax'][data]!=0}
                                dct_data['dbl_selling_price']=ins_data['dbl_selling_price']/ins_data['int_qty']
                                dct_data['int_master_id']=ins_data['fk_master__pk_bint_id']
                                lst_data.append(dct_data)

                return Response({'status':1, 'data' : lst_data,'data_qty':dct_details_id})
            else:
                return Response({'status':0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class GetCustomer(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term=request.data.get('str_search')
            lst_customer=list(CustomerDetails.objects.filter(int_mobile__icontains = str_search_term).values('pk_bint_id','vchr_name','int_mobile'));
            return Response({'status':1, 'customer_list' : lst_customer})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class SalesReturnList(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_product_id = request.data.get("intProductId")
            int_item_id = request.data.get("intItemId")
            int_brand_id = request.data.get("intBrandId")
            int_staff_id = request.data.get("intStaffId")
            int_mob_num = request.data.get("IntPhone")
            lst_return_invoice_num = list(SalesReturn.objects.values_list('fk_sales__vchr_invoice_num',flat = True))
            # if request.data.get("datTo") and request.data.get("datFrom"):
            #     dat_to = (datetime.strptime(request.data.get("datTo"),'%Y-%m-%d')).date()
            #     dat_from = (datetime.strptime(request.data.get("datFrom"),'%Y-%m-%d')).date()
            #
            #     lst_sales_return = list(SalesDetails.objects.filter(fk_master__vchr_invoice_num__in = lst_return_invoice_num,fk_master__dat_invoice__gte = dat_from,fk_master__dat_invoice__lte = dat_to).values('fk_master__vchr_invoice_num',
            #                                                                                                                                                                                                     'fk_master__fk_branch__vchr_name',
            #                                                                                                                                                                                                     'fk_master__fk_customer__vchr_name',
            #                                                                                                                                                                                                     'fk_master__fk_staff__last_name',
            #                                                                                                                                                                                                     'fk_master__fk_staff__first_name',
            #                                                                                                                                                                                                     'fk_item__fk_product__vchr_name',
            #                                                                                                                                                                                                     'fk_master__dat_invoice',
            #                                                                                                                                                                                                     'fk_master__pk_bint_id',
            #                                                                                                                                                                                                     ).order_by('-fk_master__dat_invoice'))
            # # return Response({'status':1, 'lst_sales_return' : lst_sales_return})

            ins_sales_return = SalesDetails.objects.filter(fk_master__vchr_invoice_num__in = lst_return_invoice_num).values('fk_master__vchr_invoice_num',
                                                                                                                                'fk_master__fk_branch__vchr_name',
                                                                                                                                'fk_master__fk_customer__vchr_name',
                                                                                                                                'fk_master__fk_staff__last_name',
                                                                                                                                'fk_master__fk_staff__first_name',
                                                                                                                                'fk_item__fk_product__vchr_name',
                                                                                                                                'fk_master__dat_invoice',
                                                                                                                                'fk_master__pk_bint_id',
                                                                                                                                'fk_item__vchr_name'
                                                                                                                                 ).order_by('-fk_master__dat_invoice')

            if request.data.get("datTo") and request.data.get("datFrom"):
                dat_to = (datetime.strptime(request.data.get("datTo"),'%Y-%m-%d')).date()
                dat_from = (datetime.strptime(request.data.get("datFrom"),'%Y-%m-%d')).date()

                ins_sales_return = ins_sales_return.filter(fk_master__dat_invoice__gte = dat_from,fk_master__dat_invoice__lte = dat_to)

            if  int_mob_num:
                ins_sales_return =  ins_sales_return.filter(fk_master__fk_customer__int_mobile = int_mob_num)

            if int_item_id:
                ins_sales_return = ins_sales_return .filter(fk_item_id = int_item_id)

            if int_product_id:
                ins_sales_return = ins_sales_return.filter(fk_item__fk_product_id = int_product_id)

            if int_brand_id :
                ins_sales_return = ins_sales_return.filter(fk_item__fk_brand_id = int_brand_id)

            if int_staff_id:
                ins_sales_return = ins_sales_return.filter( fk_master__fk_staff_id = int_staff_id)

            if request.user.userdetails.fk_group.vchr_name.upper() == 'ADMIN':
                pass
            else:
                ins_sales_return = ins_sales_return.filter(fk_master__fk_branch_id=request.user.userdetails.fk_branch_id)
            lst_sales_return = list(ins_sales_return)
            # import pdb; pdb.set_trace()
            dict_sales_list = {}
            for ins_data in lst_sales_return:
                ins_data['fk_master__dat_invoice'] = datetime.strftime(ins_data['fk_master__dat_invoice'],'%d-%m-%Y')
                if ins_data['fk_master__vchr_invoice_num'] not in dict_sales_list.keys():
                    dict_sales_list[ins_data['fk_master__vchr_invoice_num']] = ins_data

                else:
                    if ins_data['fk_item__fk_product__vchr_name'] not in dict_sales_list[ins_data['fk_master__vchr_invoice_num']]['fk_item__fk_product__vchr_name']:
                        dict_sales_list[ins_data['fk_master__vchr_invoice_num']]['fk_item__fk_product__vchr_name'] += "," + ins_data['fk_item__fk_product__vchr_name']

            lst_data = sorted(dict_sales_list.values(), key = lambda i: i['fk_master__dat_invoice'],reverse=True )
            # import pdb; pdb.set_trace()

            return Response({'status':1, 'lst_data' : lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class SalesReturnView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            str_invoice_no = request.data.get('strInvoiceNo')
            int_sales_master_id = int(request.data.get('intSalesMasterId'))
            lst_master_details = list(SalesMaster.objects.filter(pk_bint_id = int_sales_master_id).values('dat_invoice','fk_branch__vchr_name','fk_customer__vchr_name','fk_staff__last_name','fk_staff__first_name','fk_customer__int_mobile','fk_customer__vchr_email','vchr_remarks','vchr_invoice_num'))
            #getting all returned items invoice number and imei
            lst_returned_invoice_num = list(SalesReturn.objects.filter(fk_sales__vchr_invoice_num = str_invoice_no).values('fk_returned__vchr_invoice_num','jsn_imei'))

            lst_detail_returned = []

            if lst_returned_invoice_num:
                lst_returned_imei = [x['jsn_imei'] for x in lst_returned_invoice_num]
                # to get all imei present in returned items ------- (1)

                for i in range(len(lst_returned_invoice_num)):
                    dct_detail = {}
                    #get SalesDetails object data  contain 'fk_item__vchr_name','fk_item__fk_brand__vchr_name','dbl_discount','dbl_tax','dbl_buyback','json_tax' which are not in sales return
                    lst_returned_data = list(SalesDetails.objects.filter(fk_master__vchr_invoice_num = lst_returned_invoice_num[i]['fk_returned__vchr_invoice_num'],json_imei__contains = lst_returned_invoice_num[i]['jsn_imei']).values(
                                                                                                                                                                                                        'fk_item__vchr_name',
                                                                                                                                                                                                        'fk_item__fk_brand__vchr_name',
                                                                                                                                                                                                        'fk_item__fk_product__vchr_name',
                                                                                                                                                                                                        'fk_item__vchr_name',
                                                                                                                                                                                                        'dbl_discount',
                                                                                                                                                                                                        'dbl_tax',
                                                                                                                                                                                                        'json_tax',
                                                                                                                                                                                                        'dbl_buyback'

                                                                                                                                                                                                        ))
                # import pdb; pdb.set_trace()
                lst_SalesReturn = list(SalesReturn.objects.filter(fk_returned__vchr_invoice_num = lst_returned_invoice_num[i]['fk_returned__vchr_invoice_num'],jsn_imei__contains = lst_returned_invoice_num[i]['jsn_imei']).values('fk_returned__vchr_invoice_num','vchr_remark','vchr_image','int_qty','dbl_amount','bln_damaged','dbl_selling_price','jsn_imei'))
                #get sales return object data

                dct_detail.update(lst_returned_data[0])
                dct_detail.update(lst_SalesReturn[0])
                lst_detail_returned.append(dct_detail)


            ins_all_data_except_return_data = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status__gt = 0).values('fk_item__vchr_name',
                                                                                                                                'fk_item__fk_brand__vchr_name',
                                                                                                                                'fk_item__vchr_name',
                                                                                                                                'fk_item__fk_product__vchr_name',
                                                                                                                                'int_qty','dbl_discount',
                                                                                                                                'dbl_amount','dbl_tax',
                                                                                                                                'json_tax','json_imei','int_sales_status',
                                                                                                                                'dbl_selling_price','dbl_buyback').exclude(json_imei__contains = lst_returned_imei)
            lst_all_data_except_return_data = list(ins_all_data_except_return_data)
            # all data except return data by excluding  ------- (1)
            # import pdb; pdb.set_trace()
            return Response({'status':1, 'lst_master_details' : lst_master_details,"lst_retuned_items":lst_detail_returned,"other_items":lst_all_data_except_return_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'0','message':str(e)})

class GetReturnDetails(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dct_details_id = {}
            lst_imei = [request.data.get('imei')]
            int_customer = request.data.get('int_customer')
            str_invoice_no = request.data.get('invoiceNo')
            str_invoice = ""
            if request.data.get('imei'):
                bln_stock = check_if_imei_exist(request.data.get('imei'),bln_transit=True)
                if bln_stock:
                    return Response({'status':0,'message':'Imei exists in stock'})

                rst_customer_current_status = SalesDetails.objects.filter(json_imei__contains=lst_imei).values('fk_master__fk_customer__fk_customer__fk_state_id','fk_master__fk_customer__fk_customer__fk_state__vchr_name','fk_master__fk_customer__fk_customer__vchr_gst_no')
                rst_customer_sale_status = SalesDetails.objects.filter(json_imei__contains=lst_imei).values('fk_master__fk_customer__fk_state_id','fk_master__fk_customer__fk_state__vchr_name','fk_master__fk_customer__vchr_gst_no')

                if not SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status = 1):
                    return Response({'status':0,'message':'Invalid Imei'})


                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state_id'] !=  rst_customer_sale_status[0]['fk_master__fk_customer__fk_state_id']:
                    if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state__vchr_name'].upper() !='KERALA' and rst_customer_sale_status[0]['fk_master__fk_customer__fk_state__vchr_name'].upper() !='KERALA' :
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if not rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if not rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})





                lst_imei = [request.data.get('imei')]
                if int_customer:
                    ins_sales_details = SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status = 1,fk_master__fk_customer_id__fk_customer_id=int_customer).values('pk_bint_id','fk_master__vchr_invoice_num','dbl_indirect_discount','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name').exclude(fk_item__fk_product__vchr_name__in = ['RECHARGE','SIM'])
                else:
                    ins_sales_details = SalesDetails.objects.filter(json_imei__contains=lst_imei,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_indirect_discount','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name').exclude(fk_item__fk_product__vchr_name__in = ['RECHARGE','SIM'])
                # str_invoice = ins_sales_details.first()['fk_master__vchr_invoice_num']
                lst_invoice = [ins_sales_details.first()['fk_master__vchr_invoice_num']]
            # elif request.data.get('datFrom'):
            #     dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d').date()
            #     dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d').date()
            #     if int_customer:
            #         ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name')
            #     else:
            #         ins_sales_details = SalesDetails.objects.filter(fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name')

            elif str_invoice_no :
                rst_customer_current_status = SalesDetails.objects.filter(fk_master__vchr_invoice_num=str_invoice_no).values('fk_master__fk_customer__fk_customer__fk_state_id','fk_master__fk_customer__fk_customer__fk_state__vchr_name','fk_master__fk_customer__fk_customer__vchr_gst_no')
                rst_customer_sale_status = SalesDetails.objects.filter(fk_master__vchr_invoice_num=str_invoice_no).values('fk_master__fk_customer__fk_state_id','fk_master__fk_customer__fk_state__vchr_name','fk_master__fk_customer__vchr_gst_no')

                if not SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status = 1,dbl_amount__gt = 0):
                    return Response({'status':0,'message':'Invalid Invoice No'})



                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state_id'] !=  rst_customer_sale_status[0]['fk_master__fk_customer__fk_state_id']:
                    if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__fk_state__vchr_name'].upper() !='KERALA' and rst_customer_sale_status[0]['fk_master__fk_customer__fk_state__vchr_name'].upper() !='KERALA' :
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if not rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})

                if rst_customer_current_status[0]['fk_master__fk_customer__fk_customer__vchr_gst_no']:
                    if not rst_customer_sale_status[0]['fk_master__fk_customer__vchr_gst_no']:
                        return Response({'status':0,'message':'Customer Tax Mode Changed Return not possible'})
                if int_customer:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status = 1,fk_master__fk_customer_id__fk_customer_id=int_customer).values('pk_bint_id', 'fk_master__vchr_invoice_num','fk_item__pk_bint_id','dbl_indirect_discount','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name').exclude(fk_item__fk_product__vchr_name__in = ['RECHARGE','SIM'])
                else:
                    ins_sales_details = SalesDetails.objects.filter(fk_master__vchr_invoice_num = str_invoice_no,int_sales_status = 1,dbl_amount__gte = 0).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','dbl_indirect_discount','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name').exclude(fk_item__fk_product__vchr_name__in = ['RECHARGE','SIM'])
                    # =========================================================================================
                    """ In case of non imei item, if any of this item  already returned,then it need to substract the returned qty from total sold qty """

                    lst_sales_return = SalesReturn.objects.filter(fk_returned__vchr_invoice_num = str_invoice_no).values('fk_item__pk_bint_id','fk_item__vchr_name').annotate(Count('fk_item__pk_bint_id'))

                    for int_index in range(len(ins_sales_details)):
                        for return_item in lst_sales_return:
                            if not ins_sales_details[int_index]['json_imei'] and (ins_sales_details[int_index]['fk_item__pk_bint_id'] == return_item['fk_item__pk_bint_id']):
                                int_amt_per_unit = ins_sales_details[int_index]['dbl_selling_price'] / ins_sales_details[int_index]['int_qty']
                                ins_sales_details[int_index]['int_qty'] = ins_sales_details[int_index]['int_qty']-return_item['fk_item__pk_bint_id__count']
                                if ins_sales_details[int_index]['int_qty'] == 0:
                                    del ins_sales_details[int_index]
                                else:
                                    ins_sales_details[int_index]['dbl_selling_price'] = int_amt_per_unit * ins_sales_details[int_index]['int_qty']
                            else:
                                continue
                    # =================================================================================================================================
                # str_invoice = str_invoice_no
                lst_invoice = [str_invoice_no]
                if not ins_sales_details:
                    return Response({'status':0,'message':'Invalid Invoice No'})

            else:
                if int_customer:
                    if request.data.get('datFrom'):
                        dat_from = datetime.strptime(request.data.get('datFrom'),'%Y-%m-%d').date()
                        dat_to = datetime.strptime(request.data.get('datTo'),'%Y-%m-%d').date()
                        ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id__fk_customer_id=int_customer,fk_master__dat_invoice__range=(dat_from,dat_to),int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','dbl_indirect_discount','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name').exclude(fk_item__fk_product__vchr_name__in = ['RECHARGE','SIM'])
                    else:
                    # ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                        ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id__fk_customer_id=int_customer,int_sales_status = 1).values('int_sales_status','pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','dbl_indirect_discount','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id','fk_item__fk_product__vchr_name').exclude(fk_item__fk_product__vchr_name__in = ['RECHARGE','SIM'])
                # else:
                #     ins_sales_details = SalesDetails.objects.filter(int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
                # str_invoice = ins_sales_details.first()['fk_master__vchr_invoice_num']
                lst_invoice = ins_sales_details.values_list('fk_master__vchr_invoice_num',flat=True)
                # ins_sales_details = SalesDetails.objects.filter(fk_master__fk_customer_id=int_customer,int_sales_status = 1).values('pk_bint_id','fk_master__vchr_invoice_num','fk_item__pk_bint_id','fk_item__vchr_name','fk_item__vchr_item_code','int_qty','dbl_discount','json_tax','dbl_amount','dbl_selling_price','dbl_buyback','json_imei','fk_master__pk_bint_id')
            # ins_sales_details = ins_sales_details.exclude(json_imei__in =  SalesReturn.objects.filter(fk_returned__vchr_invoice_num = str_invoice_no).values_list('jsn_imei',flat=True))

            lst_imei_returned = [ item.get('jsn_imei')[0] for item in SalesReturn.objects.filter(fk_returned__vchr_invoice_num__in = lst_invoice).values('jsn_imei') if  item.get('jsn_imei')]

# ====================================
            # lst_return_id = SalesReturn.objects.values_list('fk_returned_id',flat=True)
            # ====================================

            # lst_imei_sales_details = [x['json_imei'] for x in ins_sales_details]

            # SalesReturn.objects.filter(fk_returned__vchr_invoice_num = str_invoice_no,jsn_imei__in = lst_imei_sales_details).values('jsn_imei')
            # import pdb; pdb.set_trace()
            if ins_sales_details:
                lst_master_id = ins_sales_details.values_list('fk_master_id',flat=True).distinct('fk_master_id')
                lst_excluded_sales_id = SalesReturn.objects.filter(fk_returned_id__in=lst_master_id).values_list('fk_sales_details_id')

                if lst_excluded_sales_id:
                    ins_sales_details = ins_sales_details.exclude(pk_bint_id__in = lst_excluded_sales_id)

                lst_data=[]
                dct_tax_master = {}
                for ins_tax in TaxMaster.objects.values('pk_bint_id','vchr_name'):
                    dct_tax_master[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])
                # import pdb; pdb.set_trace()
                # import pdb; pdb.set_trace()
                 # if len(SalesDetails.objects.filter(json_imei__icontains = request.data.get('imei'),int_sales_status = 1).values('fk_master__dat_invoice').distinct('fk_master_id')) >1:

                if request.data.get('imei'):
                    for ins_data in ins_sales_details:
                        if ins_data['fk_item__vchr_item_code'] not in ['GDC00001','GDC00002']:
                            # if (request.data.get('imei') not in lst_imei_returned) and (ins_data['fk_item__fk_product__vchr_name'].upper() != 'SERVICE'):
                            if (ins_data['fk_item__fk_product__vchr_name'].upper() != 'SERVICE'):
                            # if ins_data['pk_bint_id'] not in lst_return_id:
                                # ins_items = Item.objects.filter(vchr_item_code = ins_data['fk_item__vchr_item_code'],int_status=0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()
                                dct_details_id[ins_data['pk_bint_id']]=ins_data['int_qty']
                                dct_data={}
                                # dct_data['tax']={'dblCGST': 0, 'dblIGST': 0, 'dblSGST': 0}
                                dct_data['int_id']=ins_data['pk_bint_id']
                                dct_data['enquiry_num']=ins_data['fk_master__vchr_invoice_num']
                                dct_data['item_id']=ins_data['fk_item__pk_bint_id']
                                dct_data['item']=ins_data['fk_item__vchr_name']
                                dct_data['item_code']=ins_data['fk_item__vchr_item_code']
                                dct_data['imei']=request.data.get('imei')
                                dct_data['bln_check'] = False
                                dct_data['dblIndirectDis']=ins_data['dbl_indirect_discount']

                                dct_data['bln_true'] = False
                                # dct_data['dbl_amount']=ins_data['dbl_amount']
                                # dct_data['dbl_buy_back']=ins_data['dbl_buyback']
                                # dct_data['dbl_discount']=ins_data['dbl_discount']
                                # dct_data['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
                                # dct_data['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0))
                                # dct_data['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
                                # dct_data['tax'] = {}
                                # for data in ins_data['json_tax']:
                                #     if ins_data['json_tax'][data]!=0:
                                #         dct_data['tax'][data] = ins_data['json_tax'][data]/ins_data['int_qty']
                                #     else:
                                #         dct_data['tax'][data] = ins_data['dbl_amount']*float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master[data[3:]],0))/100


                                # dct_data['tax']= {data:ins_data['json_tax'][data]/ins_data['int_qty'] for data in ins_data['json_tax'] if ins_data['json_tax'][data]!=0}
                                dct_data['dbl_selling_price']=ins_data['dbl_selling_price']/ins_data['int_qty']
                                dct_data['int_master_id']=ins_data['fk_master__pk_bint_id']

                                lst_data.append(dct_data)
                else:
                    for ins_data in ins_sales_details:
                        if ins_data['fk_item__vchr_item_code'] not in ['GDC00001','GDC00002']:
                            dct_details_id[ins_data['pk_bint_id']]=ins_data['int_qty']
                            for idx in range(0,ins_data['int_qty']):
                                # if ((not ins_data['json_imei']) or (ins_data['json_imei'] and ins_data['json_imei'][idx] not in lst_imei_returned)) and (ins_data['fk_item__fk_product__vchr_name'].upper() != 'SERVICE'):
                                if (ins_data['fk_item__fk_product__vchr_name'].upper() != 'SERVICE'):
                                # if ins_data['pk_bint_id'] not in lst_return_id:

                                    # ins_data['json_imei'].get('idx') if ins_data.get('json_imei') else ''
                                    # ins_items = Item.objects.filter(vchr_item_code = ins_data['fk_item__vchr_item_code'],int_status=0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()

                                    dct_data={}
                                    # dct_data['tax']={'dblCGST': 0, 'dblIGST': 0, 'dblSGST': 0}
                                    dct_data['int_id']=ins_data['pk_bint_id']
                                    dct_data['enquiry_num']=ins_data['fk_master__vchr_invoice_num']
                                    dct_data['item']=ins_data['fk_item__vchr_name']
                                    dct_data['item_code']=ins_data['fk_item__vchr_item_code']
                                    dct_data['item_id']=ins_data['fk_item__pk_bint_id']
                                    dct_data['imei']=ins_data['json_imei'][idx] if ins_data.get('json_imei') else ''
                                    dct_data['dbl_amount']=ins_data['dbl_amount']
                                    dct_data['bln_check'] = False
                                    dct_data['bln_true'] = False
                                    dct_data['dblIndirectDis']=ins_data['dbl_indirect_discount']

                                    # dct_data['dbl_buy_back']=ins_data['dbl_buyback']
                                    # dct_data['dbl_discount']=ins_data['dbl_discount']
                                    # dct_data['dblIGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['IGST'],0))
                                    # dct_data['dblCGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['CGST'],0))
                                    # dct_data['dblSGSTPer'] = float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master['SGST'],0))
                                    # dct_data['tax'] = {}
                                    # for data in ins_data['json_tax']:
                                    #     if ins_data['json_tax'][data]!=0:
                                    #         dct_data['tax'][data] = ins_data['json_tax'][data]/ins_data['int_qty']
                                    #     else:
                                    #         dct_data['tax'][data] = ins_data['dbl_amount']*float(ins_items['fk_item_category__json_tax_master'].get(dct_tax_master[data[3:]],0))/100
                                    #
                                    # dct_data['tax']= {data:ins_data['json_tax'][data]/ins_data['int_qty'] for data in ins_data['json_tax'] if ins_data['json_tax'][data]!=0}
                                    dct_data['dbl_selling_price']=ins_data['dbl_selling_price']/ins_data['int_qty']
                                    dct_data['int_master_id']=ins_data['fk_master__pk_bint_id']
                                    lst_data.append(dct_data)
                return Response({'status':1, 'data' : lst_data,'data_qty':dct_details_id})
            else:
                return Response({'status':0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})
class ImeiCheckView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            int_imei = request.data.get('intImi')
            int_item_id = request.data.get('intItemId')
            bln_sale = False
            bln_imei = Item.objects.filter(pk_bint_id = int_item_id).values('imei_status')
            if bln_imei[0]['imei_status'] == True:
                lst_imei = SalesDetails.objects.filter(json_imei__contains=str(int_imei),int_sales_status=1).values()
            else:
                int_customer_details = SalesCustomerDetails.objects.filter(int_mobile=request.data.get('intNum')).values('pk_bint_id')
                lst_imei = SalesDetails.objects.filter(json_imei__contains=str(int_imei),int_sales_status=1,fk_master__fk_customer_id=int_customer_details[0]['pk_bint_id']).values()
            if lst_imei:
                bln_sale = True
            bln_stock = check_if_imei_exist(str(int_imei),bln_transit=True)

            return Response({'status':1,'blnSale':bln_sale,'blnStock': bln_stock})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
