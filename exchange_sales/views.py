from django.shortcuts import render
from exchange_sales.models import ExchangeStock
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import sys
from POS import ins_logger
from tool_settings.models import Tools
from invoice.models import SalesDetails
from datetime import datetime
from invoice.views import tools_keys
from django.db.models import FloatField, F,CharField, IntegerField, Case, Value, When,Sum
import pandas as pd
from item_category.models import Item,TaxMaster,ItemCategory
from django.conf import settings
from item_category.models import Item
from brands.models import Brands
from products.models import Products
from branch.models import Branch
from global_methods import get_user_privileges

# Create your views here.
class ExchangeSales(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):

        try:
            if request.data.get('intId'):
                # import pdb; pdb.set_trace()
                #dct_invoice=SalesDetails.objects.filter(pk_bint_id=request.data.get('intId')).values('json_imei','dbl_amount','fk_item_id','fk_item__vchr_name','fk_item__vchr_item_code','fk_master__fk_staff__last_name','fk_master__fk_staff__first_name','int_qty','fk_master__fk_customer__fk_state_id','fk_master__fk_customer__vchr_gst_no').first()
                dct_invoice=ExchangeStock.objects.filter(pk_bint_id=request.data.get('intId')).values('jsn_imei','dbl_unit_price','fk_item_id','fk_item__vchr_name','fk_item__vchr_item_code','int_avail','fk_sales_details_id').first()
                dct_invoice['fk_details_id']=dct_invoice['fk_sales_details_id']
                if dct_invoice['fk_details_id']:
                    dct_invoice = SalesDetails.objects.filter(pk_bint_id=dct_invoice['fk_details_id']).values('pk_bint_id','json_imei','dbl_amount','fk_item_id','fk_item__vchr_name','fk_item__vchr_item_code','fk_master__fk_staff__last_name','fk_master__fk_staff__first_name','int_qty','fk_master__fk_customer__fk_state_id','fk_master__fk_customer__vchr_gst_no').first()
                    dct_invoice['fk_details_id']=dct_invoice['pk_bint_id']
                else:
                    dct_invoice['int_qty']=dct_invoice['int_avail']
                    dct_invoice['json_imei']=dct_invoice['jsn_imei']
                dct_data={}
                dct_data['bln_exchange'] = True
                dct_data['intSalesCustId'] =0
                dct_data['edit_count']=0
                dct_data['txtRemarks'] = ''
                dct_data['int_status'] = 0
                dct_data['sales_status'] = None
                dct_data['intLoyaltyPoint'] = 0

                dct_data['job_status']=''
                dct_data['partial_id'] = 0
                dct_data['intAmtPerPoints'] = 0
                dct_data['blnIGST'] = False
                dct_data['dbl_kfc_amount'] = 0.0

                dct_data['intCustId']= ''
                dct_data['strCustName'] = ''
                dct_data['strCustEmail'] = ''
                dct_data['intContactNo'] = ''
                dct_data['txtAddress'] = ''
                dct_data['strGSTNo'] = ''
                dct_data['intLocation'] = ''
                dct_data['strLocation'] = ''
                dct_data['intPinCode'] = ''
                dct_data['intState'] = ''
                dct_data['strState'] = ''
                dct_data['strStaffName']= dct_invoice['fk_master__fk_staff__last_name'] if dct_invoice['fk_details_id'] else request.user.last_name +' '+dct_invoice['fk_master__fk_staff__first_name'] if dct_invoice['fk_details_id'] else request.user.first_name
                dct_data['lstItems'] = []
                # dct_data['vchrFinanceName'] = ''
                # dct_data['vchrFinanceSchema'] = ''
                dct_data['dblFinanceAmt'] = 0
                dct_data['dblEMI'] = 0
                dct_data['dblDownPayment'] = 0
                dct_data['int_fin_id']=''

                dct_item = {}
                dct_item['strItemCode'] = dct_invoice['fk_item__vchr_item_code']
                dct_item['intItemId'] = dct_invoice['fk_item_id']
                dct_item['intsalesid'] = request.data.get('intId')
                dct_item['strItemName'] = dct_invoice['fk_item__vchr_name']
                if dct_invoice['json_imei']:
                    dct_item['strImei'] = dct_invoice['json_imei'][0]
                else:
                    dct_item['strImei'] = ''
                dct_item['dblAmount'] = dct_invoice['dbl_amount'] if dct_invoice['fk_details_id'] else dct_invoice['dbl_unit_price']
                dct_item['dblRate'] = 0

                dct_item['intQuantity'] = dct_invoice['int_qty']
                dct_item['intStatus'] = 1
# <<<<<<< HEAD
                # dct_item['itemEnqId'] = ins_items_data['item_enquiry_id']
                dct_item['itemEnqId'] = None

                dct_item['dctImages'] = {}
                dct_item['blnVerified'] = True

                dct_item['strImei'] = dct_invoice['json_imei'][0]

                dct_item['dblBuyBack'] = 0
                dct_item['dblDiscount'] = 0

                dct_item['dblIGSTPer'] = 0
                dct_item['dblIGST'] = 0

                dct_item['dblSGSTPer'] = 0
                dct_item['dblSGST'] = 0

                dct_item['dblSGSTPer'] = 0
                dct_item['dblSGST'] = 0

                dct_item['dblSGSTPer'] = dct_item['dblCGSTPer'] =0
                dct_item['dblSGST'] = dct_item['dblCGST'] = 0

                dct_item['dblIGSTPer'] = 0.0
                dct_item['dblCGSTPer'] = 0.0
                dct_item['dblSGSTPer'] = 0.0
                dct_item['dblIGST'] = 0.0
                dct_item['dblCGST'] = 0.0
                dct_item['dblSGST'] = 0.0
                ####nikhil changed for extra amount tax calculation
                # import pdb; pdb.set_trace()
                dct_item['exchange_sale_amount']=-abs(dct_invoice['dbl_amount']) if dct_invoice['fk_details_id'] else dct_invoice['dbl_unit_price']
                ins_tax_master=TaxMaster.objects.values()
                dct_tax={data['pk_bint_id']:data['vchr_name']for data in ins_tax_master}
                ins_item_data=Item.objects.filter(pk_bint_id = dct_invoice['fk_item_id']).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master').first()
                for int_tax in ins_item_data['fk_item_category__json_tax_master']:
                    if dct_tax[int(int_tax)]=='IGST':
                        dct_item['dblIGSTPer'] = ins_item_data['fk_item_category__json_tax_master'][int_tax]
                    elif dct_tax[int(int_tax)]=='CGST':
                        dct_item['dblCGSTPer'] = ins_item_data['fk_item_category__json_tax_master'][int_tax]
                    elif dct_tax[int(int_tax)]=='SGST':
                        dct_item['dblSGSTPer'] = ins_item_data['fk_item_category__json_tax_master'][int_tax]
                if dct_invoice['fk_details_id'] and (dct_invoice['fk_master__fk_customer__fk_state_id'] == request.user.userdetails.fk_branch.fk_states_id and not dct_invoice['fk_master__fk_customer__vchr_gst_no']):
                    dct_item['dblKFCPer']=1.0
                else:
                    dct_item['dblKFCPer']=0.0

                dct_item['dblRate'] = 0

                dct_item['dblAmount'] = 0

                #gst generating-----------------------

                dct_data['lstItems'].append(dct_item)
                if dct_data['blnIGST']:
                    dct_item['GST'] = dct_item['dblIGSTPer']
                else :
                    dct_item['GST'] = dct_item['dblSGSTPer'] +  dct_item['dblCGSTPer']

                if not dct_item['GST']:
                    dct_item['dblKFCPer']=0.0
                dct_item['dblMarginAmount'] = 0
                dct_item['dblMopAmount'] = abs(dct_invoice['dbl_amount']) if dct_invoice['fk_details_id'] else dct_invoice['dbl_unit_price']
                dct_data['int_approve'] = 0
                # dct_item['dblMopAmount'] = dct_invoice['dbl_amount']
                #-------------------------------------

                tools_keys(dct_data,request)

                return Response({'status':1,'data':dct_data})
            else:

                # import pdb; pdb.set_trace()
                dct_filter={}
                bln_export = request.data.get('blnExport')
                if request.data.get('intProductId'):
                    dct_filter['fk_item__fk_product_id']=request.data.get('intProductId')
                if request.data.get('intBrandId'):
                    dct_filter['fk_item__fk_brand_id']=request.data.get('intBrandId')
                if request.data.get('intItemId'):
                    dct_filter['fk_item_id']=request.data.get('intItemId')
                if request.data.get('strImei'):
                    dct_filter['jsn_imei__icontains']=request.data.get('strImei')

                if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER - SMART CHOICE'] or request.user.userdetails.fk_branch.int_type in [2,3]:
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER', 'ASSISTANT BRANCH MANAGER', 'ASM1', 'ASM2', 'ASM3', 'ASM4']:
                    dct_filter['fk_branch_id__in']=[request.user.userdetails.fk_branch_id]
                else:
                    dct_privilege = get_user_privileges(request)
                    if dct_privilege.get('lst_branches'):
                        dct_filter['fk_branch_id__in']=dct_privilege['lst_branches']
                    else:
                        dct_filter['fk_branch_id__in']=[request.user.userdetails.fk_branch_id]


                lst_exchange=ExchangeStock.objects.filter(int_status=0,**dct_filter).extra(select ={'dat_exchanged_words':"to_char(dat_exchanged,'DD/MM/YYYY')"}).values('fk_item__fk_product__vchr_name','fk_item__fk_brand__vchr_name','fk_branch__vchr_name','fk_branch_id','pk_bint_id','fk_item_id','fk_item__vchr_name','fk_sales_details__fk_master__vchr_invoice_num','int_avail','dat_exchanged_words','fk_sales_details_id','fk_sales_details__dbl_amount','jsn_imei','dbl_unit_price').annotate(item_age=(datetime.now()-F('dat_exchanged'))).order_by('-dat_exchanged')
                # lst_exchange.first()["dbl_unit_price"]=abs(lst_exchange.first()["dbl_unit_price"])

                if request.data.get('datTo'):
                    lst_exchange=lst_exchange.filter(dat_exchanged__lte=request.data.get('datTo'),dat_exchanged__gte=request.data.get('datFrom'))
                if request.data.get('intBranchId'):
                    lst_exchange=lst_exchange.filter(fk_branch_id=request.data.get('intBranchId'))

                for data in lst_exchange:
                    data["fk_sales_details_id"]=data["pk_bint_id"]
                    data["fk_sales_details__dbl_amount"]=abs(round(data["fk_sales_details__dbl_amount"])) if data.get("fk_sales_details__dbl_amount") else data["dbl_unit_price"]
                    data["item_age"]=data["item_age"].days if data.get("item_age") else data.get("item_age")

                if bln_export:
                    if lst_exchange:
                        exp_data = exchange_export(request,lst_exchange)
                        return Response({'status':1,'lst_exchange':lst_exchange,'export_data':exp_data})
                return Response({'status':1,'lst_exchange':lst_exchange})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class BranchTypeaheadExchange(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            lst_branch = []
            if(request.data['term']):
                str_search_term=request.data['term']
                ins_branch = Branch.objects.filter(vchr_name__icontains=str_search_term,int_status=0).values('pk_bint_id','vchr_name')
            else:
                ins_branch = Branch.objects.filter(int_status=0).values('pk_bint_id','vchr_name')

            if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER - SMART CHOICE'] or request.user.userdetails.fk_branch.int_type in [2,3]:
                pass
            elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER', 'ASSISTANT BRANCH MANAGER', 'ASM1', 'ASM2', 'ASM3', 'ASM4']:
                ins_branch = ins_branch.filter(pk_bint_id = request.user.userdetails.fk_branch_id)
            else:
                dct_privilege = get_user_privileges(request)
                if dct_privilege:
                    ins_branch = ins_branch.filter(pk_bint_id__in = dct_privilege['lst_branches'])
                else:
                    ins_branch = ins_branch.filter(pk_bint_id = request.user.userdetails.fk_branch_id)

            if ins_branch:
                for itr_item in ins_branch:
                    dct_branch = {}
                    dct_branch['branchname'] = itr_item['vchr_name'].capitalize()
                    dct_branch['id'] = itr_item['pk_bint_id']
                    lst_branch.append(dct_branch)
            return Response({'status':1,'data':lst_branch})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})

def exchange_export(request,lst_exchange):
    dat_to = request.data.get("datTo")
    dat_drom = request.data.get("datFrom")
    df_data = pd.DataFrame(list(lst_exchange))
    excel_file = settings.MEDIA_ROOT+'/exchange_stock.xlsx'
    str_product_filter ='PRODUCT                :  ALL'
    str_brand_filter ='BRAND                    :  ALL'
    str_item_filter ='ITEM                       :  ALL'

    df_export_data =  pd.DataFrame()

    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    sheet_name1 ='sheet1'

    df_export_data['S.No'] = list(range(1,len(df_data.index)+1))
    df_export_data['DATE'] = df_data['dat_exchanged_words']
    if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','MANAGER - SMART CHOICE'] or request.user.userdetails.fk_branch.int_type in [2,3]:
        df_export_data['BRANCH'] = df_data['fk_branch__vchr_name']
        str_branch_filter = 'BRANCH                  :  ALL'
        if request.data.get('intBranchId'):
            str_branch_filter = 'BRANCH                  :  '+ Branch.objects.filter(pk_bint_id = int(request.data.get('intBranchId'))).values('vchr_name').first()['vchr_name']
    else:
        str_branch_filter = 'BRANCH                  :  '+request.user.userdetails.fk_branch.vchr_name.upper()

    if request.data.get('intProductId'):
        vchr_product_name = Products.objects.filter(pk_bint_id = request.data.get('intProductId')).values('vchr_name').first()['vchr_name']
        str_product_filter = 'PRODUCT                 :  '+ vchr_product_name

    if request.data.get('intBrandId'):
        vchr_brand_name= Brands.objects.filter(pk_bint_id = request.data.get('intBrandId')).values('vchr_name').first()['vchr_name']
        str_brand_filter = 'BRAND                   :  '+vchr_brand_name
    if request.data.get('intItemId'):
        vchr_item_name =Item.objects.filter(pk_bint_id = request.data.get('intItemId')).values('vchr_name').first()['vchr_name']
        str_item_filter = 'ITEM                     :'+vchr_item_name
    df_export_data['BRAND'] = df_data['fk_item__fk_brand__vchr_name']
    df_export_data['ITEM'] = df_data['fk_item__vchr_name']
    df_export_data['IMEI'] =  df_data['jsn_imei'].astype(str).str.strip("[],'")
    df_export_data['AGE'] = df_data['item_age']
    df_export_data['RATE'] = df_data['fk_sales_details__dbl_amount']
    df_export_data.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=10, startcol=0)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name1]

    merge_format1 = workbook.add_format({
        'bold': 20,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size':23
        })

    merge_format2 = workbook.add_format({
    'bold': 6,
    'border': 1,
    'align': 'left',
    'valign': 'vleft',
    'font_size':13
    })
    for i, col in enumerate(df_export_data.columns):

        # find length of column i
        column_len = df_export_data[col].astype(str).str.len().max()
        # Setting the length if the column header is larger
        # than the max column value length
        column_len = max(column_len, len(col)) + 2
        # set the column length
        worksheet.set_column(i, i, column_len)
    # import pdb; pdb.set_trace()
    worksheet.merge_range('A1+:G2', 'EXCHANGE STOCK REPORT', merge_format1)
    worksheet.merge_range('A4+:D4', 'Taken By                 :  '+request.user.username, merge_format2)
    worksheet.merge_range('A5+:D5', 'Action Date            :  '+datetime.strftime(datetime.now(),'%d-%m-%Y , %I:%M %p'), merge_format2)

    worksheet.merge_range('A6+:D6',str_branch_filter, merge_format2)
    worksheet.merge_range('A7+:D7',str_product_filter, merge_format2)
    worksheet.merge_range('A8+:D8',str_brand_filter, merge_format2)
    worksheet.merge_range('A9+:D9',str_item_filter, merge_format2)


    writer.save()
    data = settings.HOSTNAME+'/media/exchange_stock.xlsx'


    return data








class ImeiTypeahead(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
            str_search_term = request.data.get('term',-1)
            lst_imei = []
            lst_imei_dct=[]
            if str_search_term != -1:
                ins_exchange_stock = ExchangeStock.objects.filter(jsn_imei__icontains=str_search_term).values('jsn_imei','pk_bint_id')
                if ins_exchange_stock:
                    for itr_item in ins_exchange_stock:
                        for imei in itr_item['jsn_imei']:
                            if str_search_term in imei and imei not in lst_imei:
                                dct_imei={}
                                dct_imei['imei']=imei
                                lst_imei_dct.append(dct_imei)
                                lst_imei.append(imei)
                return Response({'status':1,'data':lst_imei_dct})
