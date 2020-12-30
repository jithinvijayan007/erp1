from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from quotation.models import Quotation
from django.conf import settings
from tool_settings.models import Tools
from branch.models import Branch
from item_category.models import Item,TaxMaster,ItemCategory
from quotation.models import Quotation
import sys, os
from django.db.models.functions import Concat
from POS import ins_logger
from purchase.models import Document
from purchase.views import doc_num_generator
from datetime import datetime
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from POS import ins_logger
from PyPDF2 import PdfFileWriter, PdfFileReader
from django.db import transaction
import pdfkit
import base64
from django.db.models import Value
from os import remove
import inflect
class AddQuotation(APIView):
    def post(self,request):
        try:
            permission_classes = [IsAuthenticated]

            # ins_document = Document.objects.select_for_update().filter(vchr_module_name = "QUOTATION",vchr_short_code = 'QTN').first()
            # if not ins_document:
            #     ins_document = Document.objects.create(vchr_module_name = "QUOTATION",vchr_short_code = ins_branch_code,int_number = 1)
            #     str_qtn_num = (ins_document.vchr_short_code).upper()+'-'+request.user.userdetails.fk_branch.vchr_code.upper()+'-'+str(ins_document.int_number).zfill(4)
            #     ins_document.int_number = ins_document.int_number+1
            #     ins_document.save()
            # else:
            #     str_qtn_num = (ins_document.vchr_short_code).upper()+'-'+request.user.userdetails.fk_branch.vchr_code.upper()+'-'+str(ins_document.int_number).zfill(4)
            #     Document.objects.filter(vchr_module_name = "QUOTATION",vchr_short_code = 'QTN').update(int_number = ins_document.int_number+1)

            # LG 27-06-2020
            with transaction.atomic():
                str_qtn_num = doc_num_generator('QUOTATION',request.user.userdetails.fk_branch.pk_bint_id)
                if not str_qtn_num:
                    return Response({'status':0,'message':'Document Numbering Series not Assigned!!....'})
            # [{'vchr_item_code':'MOB00961',
            # 'vchr_item_name':'SAMSUNG NOTE 3 64 GB',
            # 'int_qty':5,
            # 'dbl_unit_rate':2700,
            # 'dbl_unit_amount':3000,
            # 'dbl_total_rate':8100,
            # 'dbl_total_amount':15000,
            # 'dct_tax_perc':{'KFC':1,"dblCGST":9, "dblIGST": 0.0, "dblSGST": 9}
            # 'dct_total_tax': {"KFC":270,"dblCGST": 1380.5309734513273, "dblIGST": 0.0, "dblSGST": 1380.5309734513273},
            # 'dbl_discount': -200,
            #  "dbl_total_tax": 2600},
            #  {dict2}
            # ]
            #
            # intGrandTot
            # intDiscount
            # intTotSGST
            # intTotCGST
            # intTotIGST
            # intKfcTot
            # intBuyBack
            # blnCheckIGST
            #
            #
            # strName
            #
            # strCustState

            dct_data = request.data.get('dctItems')

            # ins_quotation = Quotation.objects.create_quotation_doc(str_inv_num)
            ins_quotation = Quotation.objects.create(
                            vchr_doc_num = str_qtn_num,
                            fk_branch_id =request.user.userdetails.fk_branch_id,
                            vchr_cust_name =request.data.get('strName'),
                            vchr_email =request.data.get('strEmail'),
                            bint_mobile =request.data.get('intContactNo'),
                            txt_address =request.data.get('strAddress'),
                            vchr_gst_no =request.data.get('strGSTNo'),
                            jsn_data =request.data.get('dct_item_data'),
                            fk_state_id =request.data.get('intCustStateId'),
                            txt_remarks = request.data.get('strRemarks'),
                            # fk_location_id =request.data.get('')
                            dat_created = datetime.now(),
                            fk_created_id =request.user.id,
                            dat_exp =request.data.get('datValidTill') )
            ins_quotation.save()
            return Response({'status':1,'intId':ins_quotation.pk_bint_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

    def get(self,request):
        try:
            dct_user = {}
            dct_user['int_id'] = request.user.id
            dct_user['vchr_state_name'] = request.user.userdetails.fk_branch.fk_states.vchr_name
            dct_user['int_state_id'] = request.user.userdetails.fk_branch.fk_states_id

            return Response({'status':0,'dct_data':dct_user})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class QuotationList(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            int_branch_id = request.user.userdetails.fk_branch.pk_bint_id
            if request.data.get('id'):
                lst_data = Quotation.objects.filter(pk_bint_id = int( request.data.get('id')),fk_branch_id = int_branch_id).extra(select = {'dat_exp_formated':"to_char(dat_exp,'DD-MM-YYYY')",'dat_created_formated':"to_char(dat_created,'DD-MM-YYYY')"}).annotate(vchr_staff_name=Concat('fk_created__first_name', Value(' '), 'fk_created__last_name')).values(  'pk_bint_id','vchr_doc_num',
                                                                                                                                                                                                                                                                                                                                        'fk_branch_id',
                                                                                                                                                                                                                                                                                                                                        'fk_branch__vchr_name',
                                                                                                                                                                                                                                                                                                                                        'fk_branch__vchr_address',
                                                                                                                                                                                                                                                                                                                                        'vchr_cust_name',
                                                                                                                                                                                                                                                                                                                                        'vchr_email',
                                                                                                                                                                                                                                                                                                                                        'bint_mobile',
                                                                                                                                                                                                                                                                                                                                        'txt_address',
                                                                                                                                                                                                                                                                                                                                        'vchr_gst_no',
                                                                                                                                                                                                                                                                                                                                        'jsn_data',
                                                                                                                                                                                                                                                                                                                                        'fk_state_id',
                                                                                                                                                                                                                                                                                                                                        'fk_state__vchr_name',
                                                                                                                                                                                                                                                                                                                                        'fk_location_id',
                                                                                                                                                                                                                                                                                                                                        'fk_location__vchr_name',
                                                                                                                                                                                                                                                                                                                                        'dat_created',
                                                                                                                                                                                                                                                                                                                                        'dat_exp',
                                                                                                                                                                                                                                                                                                                                        'dat_exp_formated',
                                                                                                                                                                                                                                                                                                                                        'txt_remarks',
                                                                                                                                                                                                                                                                                                                                        'vchr_staff_name',
                                                                                                                                                                                                                                                                                                                                        'dat_created_formated'
                                                                                                                                                                                                                                                                                                                                        )
            else:
                lst_data = Quotation.objects.filter(int_active = 0,dat_created__date__lte=dat_to,dat_created__date__gte = dat_from,fk_branch_id = int_branch_id).extra(select = {'dat_exp_formated':"to_char(dat_exp,'DD-MM-YYYY')",'dat_created_formated':"to_char(dat_created,'DD-MM-YYYY')"}).annotate(vchr_staff_name=Concat('fk_created__first_name', Value(' '), 'fk_created__last_name')).values(   'pk_bint_id',
                                                                                                                                                                                                                                                                                                              'vchr_doc_num',
                                                                                                                                                                                                                                                                                                              'fk_branch_id',
                                                                                                                                                                                                                                                                                                              'fk_branch__vchr_name',
                                                                                                                                                                                                                                                                                                              'vchr_cust_name',
                                                                                                                                                                                                                                                                                                              'vchr_email',
                                                                                                                                                                                                                                                                                                              'bint_mobile',
                                                                                                                                                                                                                                                                                                              'txt_address',
                                                                                                                                                                                                                                                                                                              'vchr_gst_no',
                                                                                                                                                                                                                                                                                                              'jsn_data',
                                                                                                                                                                                                                                                                                                              'fk_state_id',
                                                                                                                                                                                                                                                                                                              'fk_location_id',
                                                                                                                                                                                                                                                                                                              'fk_location__vchr_name',
                                                                                                                                                                                                                                                                                                              'dat_created',
                                                                                                                                                                                                                                                                                                              'dat_exp',
                                                                                                                                                                                                                                                                                                              'dat_exp_formated',
                                                                                                                                                                                                                                                                                                              'vchr_staff_name',
                                                                                                                                                                                                                                                                                                              'dat_created_formated'
                                                                                                                                                                                                                                                                                                              )
            return Response({'status':1,'lst_data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
    def get(self,request):
        try:
            lst_data = Quotation.objects.filter(int_active = 0).values(  'vchr_doc_num',
                                                                             'fk_branch_id',
                                                                             'fk_branch__vchr_name',
                                                                             'vchr_cust_name',
                                                                             'vchr_email',
                                                                             'bint_mobile',
                                                                             'txt_address',
                                                                             'vchr_gst_no',
                                                                             'jsn_data',
                                                                             'fk_state_id',
                                                                             'fk_location_id',
                                                                             'fk_location__vchr_name',
                                                                             'dat_created',
                                                                             'dat_exp'
                                                                             )
            return Response({'status':1,'lst_data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

#
class QuotationPrint(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:

            int_qtn_id = request.data.get('id')
            permission_classes = [IsAuthenticated]
            int_branch_id = request.data.get('intBranchId')
            dct_branch_dat = Branch.objects.filter(pk_bint_id = int_branch_id).values('vchr_name',
                                                                                      'vchr_code',
                                                                                      'vchr_address',
                                                                                      'vchr_email',
                                                                                      'vchr_phone',
                                                                                      'vchr_mygcare_no',
                                                                                      'fk_states_id').first()
            if dct_branch_dat:
                str_mygcare_num  = dct_branch_dat['vchr_mygcare_no'] if dct_branch_dat['vchr_mygcare_no'] else " "
            else:
                str_mygcare_num = " "

            ins_qtn = Quotation.objects.filter(pk_bint_id = int(int_qtn_id)).values('vchr_doc_num',
                                                                                    'fk_branch_id',
                                                                                    'fk_branch__vchr_name',
                                                                                    'fk_branch__vchr_address',
                                                                                    'fk_branch__vchr_code',
                                                                                    'fk_branch__vchr_email',
                                                                                    'fk_branch__vchr_phone',
                                                                                    'fk_branch__vchr_mygcare_no',
                                                                                    'fk_branch__vchr_mygcare_no',
                                                                                    'fk_branch__fk_states_id',
                                                                                    'fk_branch__fk_states__vchr_name',
                                                                                    'vchr_cust_name',
                                                                                    'vchr_email',
                                                                                    'bint_mobile',
                                                                                    'txt_address',
                                                                                    'vchr_gst_no',
                                                                                    'jsn_data',
                                                                                    'fk_state_id',
                                                                                    'fk_state__vchr_name',
                                                                                    'fk_state__vchr_code',
                                                                                    'fk_location_id',
                                                                                    'fk_location__vchr_name',
                                                                                    'fk_created__first_name',
                                                                                    'fk_created__last_name',
                                                                                    'dat_created',
                                                                                    'dat_exp').first()
            dct_quotation = {}
            dct_quotation['vchr_branch_name'] = ins_qtn['fk_branch__vchr_name']
            dct_quotation['vchr_branch_code'] = ins_qtn['fk_branch__vchr_code']
            dct_quotation['vchr_branch_address'] = ins_qtn['fk_branch__vchr_address']
            dct_quotation['vchr_branch_email'] = ins_qtn['fk_branch__vchr_email']
            dct_quotation['vchr_branch_phone'] = ins_qtn['fk_branch__vchr_phone']
            dct_quotation['fk_branch__vchr_mygcare_no'] = ins_qtn['fk_branch__vchr_mygcare_no']
            dct_quotation['branch_GSTIN'] = '32AAAFZ4615J1Z8'
            if ins_qtn['fk_branch__vchr_code']=='AGY':
                dct_quotation['branch_GSTIN'] = '32AAIFC7578H2Z7'
            dct_quotation['qtn_no'] = ins_qtn['vchr_doc_num']
            dct_quotation['qtn_date'] = str(ins_qtn['dat_created'].strftime('%d-%m-%Y'))
            dct_quotation['cust_state'] = ins_qtn['fk_state__vchr_name']
            dct_quotation['cust_state_code'] = ins_qtn['fk_state__vchr_code']
            dct_quotation['staff'] = ins_qtn['fk_created__first_name'] + ' ' +ins_qtn['fk_created__last_name']
            dct_quotation['cust_name'] = ins_qtn['vchr_cust_name']
            dct_quotation['cust_add'] = ins_qtn['txt_address']
            dct_quotation['cust_mobile'] = ins_qtn['bint_mobile']
            dct_quotation['cust_gst'] = ins_qtn['vchr_gst_no']
            dct_quotation['cust_email'] = ins_qtn['vchr_email'] if ins_qtn['vchr_email'] else ' '
            dct_quotation['lst_items'] = ins_qtn['jsn_data']
            dct_quotation['qtn_time'] = ins_qtn['dat_created'].strftime('%H:%M %p')
            dct_quotation['bln_igst'] = ins_qtn['jsn_data']['blnCheckIGST']
            dct_quotation['bln_kfc'] = ins_qtn['jsn_data']['intKfcTot']
            dct_quotation['dat_exp'] = str(ins_qtn['dat_exp'].strftime('%d-%m-%Y'))

            res_print  = quotation_print(dct_quotation,request)
            str_request_protocol = request.META.get('HTTP_REFERER').split(':')[0]



            return Response({'status':1,'data':res_print,'file_url':str_request_protocol+'://'+request.META['HTTP_HOST']+'/media/'+res_print['file_name']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ItemTypeaheadTax(APIView):
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_items = []
            if str_search_term != -1:
                ins_item = Item.objects.filter(Q(int_status = 0),(Q(vchr_name__icontains=str_search_term)|Q(vchr_item_code__icontains=str_search_term))).values('pk_bint_id','vchr_name',
                                                                                                                                                                'vchr_item_code','fk_product_id',
                                                                                                                                                                'fk_product__vchr_name',
                                                                                                                                                                'fk_brand_id','fk_brand__vchr_name',
                                                                                                                                                                 'fk_item_category__vchr_hsn_code')
                if ins_item:
                    for itr_item in ins_item:
                        dct_item = {}
                        dct_item['strItemName'] = itr_item['vchr_name']
                        dct_item['strItemCode'] = itr_item['vchr_item_code']
                        dct_item['strItemId'] = itr_item['pk_bint_id']
                        dct_item['strItemId'] = itr_item['pk_bint_id']
                        dct_item['strItemId'] = itr_item['pk_bint_id']
                        dct_item['intProductId']= itr_item['fk_product_id']
                        dct_item['strProductName'] = itr_item['fk_product__vchr_name']
                        dct_item['intBrandId'] = itr_item['fk_brand_id']
                        dct_item['strBrandName'] = itr_item['fk_brand__vchr_name']
                        dct_item['vchr_hsn_code'] = itr_item['fk_item_category__vchr_hsn_code']

                        lst_items.append(dct_item)
                return Response({'status':1,'lst_item':lst_items})

            elif request.data.get('intItemId'):
                ins_item = Item.objects.filter(pk_bint_id = int( request.data.get('intItemId'))).values('pk_bint_id','vchr_name',
                                                                                                        'fk_item_category__json_tax_master',
                                                                                                        'dbl_mop','vchr_item_code',
                                                                                                        'fk_product_id',
                                                                                                        'fk_product__vchr_name',
                                                                                                        'fk_brand_id',
                                                                                                        'fk_brand__vchr_name').first()

                dct_tax_master = dict(TaxMaster.objects.filter(pk_bint_id__in =ins_item['fk_item_category__json_tax_master'].keys()).values_list('vchr_name','pk_bint_id'))
                # dct_tax_master = {x[1]:y[1] for x in dct_tax_master.items() for y in ins_item['fk_item_category__json_tax_master'].items() if int(x[0])==int(y[0])}
                ins_item['dblSGSTPer'] = ins_item['fk_item_category__json_tax_master'].get(str(dct_tax_master.get('SGST')),0)
                ins_item['dblSGST'] = ins_item['dbl_mop']*ins_item['fk_item_category__json_tax_master'].get(str(dct_tax_master.get('SGST')),0)/100
                ins_item['dblCGSTPer'] = ins_item['fk_item_category__json_tax_master'].get(str(dct_tax_master.get('CGST')),0)
                ins_item['dblCGST'] =  ins_item['dbl_mop']*ins_item['fk_item_category__json_tax_master'].get(str(dct_tax_master.get('CGST')),0)/100
                ins_item['dblIGSTPer'] = ins_item['fk_item_category__json_tax_master'].get(str(dct_tax_master.get('IGST')),0)
                ins_item['dblIGST'] =  ins_item['dbl_mop']*ins_item['fk_item_category__json_tax_master'].get(str(dct_tax_master.get('IGST')),0)/100
                ins_item['dblMopAmount'] =  ins_item['dbl_mop']
                ins_item['strItemCode'] =  ins_item['vchr_item_code']

                if request.data.get("blnIGST"):
                    ins_item['GST']=ins_item['dblIGSTPer']
                else:
                    ins_item['GST']=ins_item['dblSGSTPer']+ins_item['dblCGSTPer']
                return Response({'status':1,'lst_item':ins_item})
            return Response({'status':0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


def quotation_print(dct_quotation,request):
    try:

        str_mygcare_num = dct_quotation['fk_branch__vchr_mygcare_no'] or " "
        html_data ="""<!doctype html>
                                    <html>
                                    <head>
                                    <meta charset="utf-8">
                                    <title>Invoice Format</title>
                                        <style>
              body{"""
        # if dct_invoice['bln_dup']:
        #     html_data += """
        #             background: url("""+settings.MEDIA_ROOT+"""/duplicate.png);
        #             background-size: contain;
        #             background-repeat: no-repeat;"""
        html_data += """font-family:Segoe, "Segoe UI", "DejaVu Sans", "Trebuchet MS", Verdana, "sans-serif";
                  }
                h6{
                    font-size: 0.85em;
                    padding-left: 10px;
                  }
                p{
                    font-size:17px;
                    word-spacing: 2px;
                    padding-left: 10px;
                    padding-right: 10px;
                 }
        .container{
                     width:1170px;
                     margin:auto;
                  }
            .clear{
                     clear:both;
                  }
         .imagebox{
                     width:100%;
                     float: left;
                     border-bottom: 1px solid #c7c2c2;
                     padding-bottom: 12px;margin-top: 20px;
                  }
            .ibox1{
                    width: 25%;
                    float: left;

                  }
            .ibox2{
                    width: 50%;
                    float: left;
                  }
         .ibox2 h6{
                   margin-bottom: 0;
                   margin-top: 10px;
                   padding-left: 0 !important;
                  }

          .ibox2 p{
                   margin-bottom: 0;
                   margin-top: 5px;
                   padding-right: 0;
                   padding-left: 0;
                  }
            .ibox3{
                    width: 25%;
                    float: left;
                  }
             .box1{
                    width:100%;
                    float: left;
                    padding-bottom: 16px;

                  }
         .section1{
                    width:64%;
                    float: left;
                  }
        .section1 h6{
                    margin-bottom: 0px;
                    margin-top: 14px;
                  }
        .section1 p{
                    margin-bottom: 0px;
                    margin-top: 10px;
                  }
         .section2{
                    width:32%;
                    float: right;
                    text-align: right;
                  }
        .section2 h6{
                    margin-bottom: 0px;
                    margin-top: 14px;
                  }
        .section2 p{
                    margin-bottom: 0px;
                    margin-top: 10px;
                  }
         .section3{
                    width:50%;
                    float: left;

                  }
        .section3 h6{
                    margin-bottom: 0px;
                    margin-top: 14px;
                  }
        .section3 p{
                    margin-bottom: 0px;
                    margin-top: 10px;

                  }
         .section4{
                    width:50%;
                    float: right;
                  }
        .section4 h6{
                    margin-bottom: 0px;
                    margin-top: 14px;

                  }
        .section4 p{
                    margin-bottom: 0px;
                    margin-top: 10px;
                  }
                  table{
                  border-collapse:collapse;
                  }
                th{
                    font-weight: 400;
                  }
           th, td {
                    padding: 15px;
                    text-align: center;
                  }
         .section5{
                    width:40%;
                    float: right;
                    text-align: right;
                  }
        .section5 h6{
                    margin-bottom: 0px;
                    margin-top: 14px;
                    padding-left: 0px !important;
                    font-size: 16px;
                  }
        .section5 p{
                    margin-bottom: 0px;
                    margin-top: 10px;
                  }
             .box2{
                    width:100%;
                    float: left;

                  }
            @page {
                   size: 7in 9.25in;
                   margin: 27mm 16mm 27mm 16mm;
                  }
                li{
                   font-size:17px;
                 }
          .header{
                    width:100%;
                    float: left;
                    text-align:center;
                    # color:  #e06a2b;

                  }

          .invoice{

                    background-color: #e06a2b;
                    color: white;
                    padding: 15px 10px 15px 10px;

                 }
        .innerbox{
                    background: white;
                    width: 100%;
                }
        </style>
        </head>

        <body>
        <div class="container">
        <div class="header">

                    <h3  style="font-size: 25px;margin-top: 0;margin-bottom: 0;padding:10px 10px 10px 10px;">QUOTATION </h3>
                <div class="clear"></div>
            </div>
        <div class="imagebox">

               <div class="ibox1">
                   <img src='"""+settings.MEDIA_ROOT+"""/myglogo.jpg' width="45%">
               </div>
               <div class="ibox2">

             <div style="width:100%;float:left;">
                    <div style="width:20%;float:left">
                    <p><span style="font-weight: 600;">ADDRESS  : </span></p>
                    </div>
                    <div style="width:79%;float: right">
                    <p> """+str(dct_quotation['vchr_branch_address'] or '')+"""</p>
                    </div>
                 </div>

                   <div style="width:50%;float:left;">

                       <div style="width:15%;float:left">
                       <p><span style="font-weight: 600;">PH : </span></p>
                       </div>
                       <div style="width:83%;float: right">
                        <p> """+(str(dct_quotation['vchr_branch_phone']) or " ")+"""</p>
                       </div>

               </div>
                     <div style="width:50%;float:right;">

                         <div style="width:25%;float:left">
                       <p><span style="font-weight: 600;">MOB : </span></p>
                       </div>
                       <div style="width:73%;float: right">
                        <p>   """
        if dct_quotation['vchr_branch_phone']:
            html_data+=str(dct_quotation['vchr_branch_phone'])
        else:
            html_data+="**********"
        html_data+="""</p>
                       </div>
                </div>
            <div style="width:50%;float:left;">
                   <div style="width:45%;float:left">
                  <p><span style="font-weight: 600;">MYG CARE : </span></p>
                   </div>
                   <div style="width:54%;float: right">
                    <p>"""+str(str_mygcare_num)+""" </p>
                   </div>

               </div>
                     <div style="width:50%;float:right;">
                        <div style="width:35%;float:left">
                         <p><span style="font-weight: 600;">EMAIL ID : </span></p>
                       </div>
                       <div style="width:65%;float: right">
                        <p>"""+str(dct_quotation['vchr_branch_email'])+"""</p>
                       </div>
                     </div>
                   <div style="width:100%;float:left;">
                    <p><span style="font-weight: 600;">GSTN : </span>"""+str(dct_quotation['branch_GSTIN'])+"""</p>
               </div>

             </div>
               <div class="ibox3" style="text-align: right;">
                   <div><img src='"""+settings.MEDIA_ROOT+"""/brandlogo.jpg' width="40%"></div>
                   <div> <img src='"""+settings.MEDIA_ROOT+"""/custumercare.jpg' width="40%"></div>
                   <div> <img src='"""+settings.MEDIA_ROOT+"""/socialmedia.jpg' width="40%"></div>
               </div>

        </div>





        <div style="float: left;width: 100%;">


            <div class="box1" style="border-bottom: 1px solid #c7c2c2;">
                <div class="section1">



                </div>
                <div class="section2" >"""
        html_data+=	"""<div style="width:50%;float:left;"><p>Quotation No :</p></div>
                    <div style="width:50%;float:right;font-weight:600"><p>"""+dct_quotation['qtn_no']+"""</p></div>
                    <div class="clear"></div>

                    <div style="width: 50%;float:left;"><p>Quotation Date :</p></div>
                    <div style="width:50%;float:right;font-weight:600"><p> """+str(dct_quotation['qtn_date'])+""" </p></div>
                    <div class="clear"></div>

                    <div style="width: 50%;float:left;"><p>Quotation Time :</p></div>
                    <div style="width:50%;float:right;font-weight:600"><p> """+str(dct_quotation['qtn_time'])+"""</p></div>
                    <div class="clear"></div>

                    <div style="width: 50%;float:left;"><p>Expiry Date :</p></div>
                    <div style="width:50%;float:right;font-weight:600"><p> """+str(dct_quotation['dat_exp'])+""" </p></div>
                    <div class="clear"></div>





                    <div style="width:50%;float:left;"><p>State :</p></div>
                    <div style="width:50%;float:right;font-weight:600"><p> """+dct_quotation['cust_state'].title()+""""""
        if dct_quotation['cust_state_code']:
            html_data+= """/"""+dct_quotation['cust_state_code']+""""""

        html_data+= """</p></div><div class="clear"></div>"""

        if dct_quotation['staff']:
            html_data += """<div style="width: 50%;float:left;"><p>Sales Person :</p></div>
                        <div style="width:50%;float:right;font-weight:600"><p> """+dct_quotation['staff'].title()+"""</p></div>
                        """

        html_data +="""</div>
                    <div class="section3">
                        <div style="border-right: 1px solid #c7c2c2;">
                             <div style="width:100%;float: left;"><h6 style="border-bottom: 1px solid #c7c2c2;padding-bottom: 6px;color: green;">BILLED TO</h6></div>

                             <div style="width:30%;float: left;"><h6>CUSTOMER NAME</h6></div>
                             <div style="width:70%;float:right;"><p>: """+dct_quotation['cust_name'].title()+"""</p></div>
                             <div class="clear"></div>"""
        if dct_quotation['cust_add']:
            html_data +=""" <div style="width:30%;float: left;"><h6>ADDRESS</h6></div>
                             <div style="width:70%;float:right;"><p>: """+dct_quotation['cust_add']+"""</p></div>
                             <div class="clear"></div>"""
        # if dct_invoice['cust_add']:
        #     html_data +="""   <div style="width:30%;float: left;"><h6>CITY PIN CODE</h6></div>
        # 				     <div style="width:70%;float:right;"><p>: """+"""680307"""+"""</p></div>
        # 				     <div class="clear"></div>"""
        html_data +="""	     <div style="width:30%;float: left;"><h6>MOB NO</h6></div>
                             <div style="width:70%;float:right;"><p>: """+str(dct_quotation['cust_mobile'])+"""</p></div>
                             <div class="clear"></div>"""
        if dct_quotation['cust_gst']:
            html_data +="""  <div style="width:30%;float: left;"><h6>GSTN NO</h6></div>
                             <div style="width:70%;float:right;"><p>: """+str(dct_quotation['cust_gst'])+"""</p></div>
                             <div class="clear"></div>"""
        if dct_quotation['cust_gst']:
            html_data +="""  <div style="width:30%;float: left;"><h6>Mail ID</h6></div>
                             <div style="width:70%;float:right;"><p>: """+str(dct_quotation['cust_email'])+"""</p></div>
                             <div class="clear"></div>"""
        if dct_quotation['cust_state']:
            html_data +="""  <div style="width:30%;float: left;"><h6>STATE</h6></div>
                             <div style="width:70%;float:right;"><p>: """+dct_quotation['cust_state'].title()+""""""
        if dct_quotation['cust_state_code']:
            html_data+=   """/"""+dct_quotation['cust_state_code']+""""""
        html_data  +="""                   </p></div><div class="clear"></div>"""



        html_data +="""</div>
                 </div>
                         <div class="clear"></div>
                          <div class="table-responsive print">
                              <table style="width:100%;border: 1px solid #cecdcd;">

                                  <tr style="background-color: #e06a2b;color: white;">
                                    <th style="border: 1px solid #cecdcd;">SLNO</th>
                                    <th style="border: 1px solid #cecdcd;">ITEM DESCRIPTION/DETAIL</th>
                                    <th style="border: 1px solid #cecdcd;">HSN/SAC</th>
                                    <th style="border: 1px solid #cecdcd;">QTY</th>
                                    <th style="border: 1px solid #cecdcd;">RATE</th>
                                    <th style="border: 1px solid #cecdcd;">DISCOUNT</th>"""

        if dct_quotation['bln_igst']:
            html_data +="""<th style="border: 1px solid #cecdcd;">IGST %</th>"""
        else:
            html_data +="""
                                    <th style="border: 1px solid #cecdcd;">SGST %</th>
                                    <th style="border: 1px solid #cecdcd;">CGST %</th>"""
        html_data +="""<th style="border: 1px solid #cecdcd;">GROSS AMOUNT</th>
                                  </tr>"""
        int_index = 1
        for dct_item in dct_quotation['lst_items']['lstItemDetails']:
            ins_category_id = Item.objects.filter(vchr_item_code = dct_item['strItemCode']).values('fk_item_category_id').first()
            ins_hsn = ItemCategory.objects.filter(pk_bint_id = ins_category_id['fk_item_category_id']).values('vchr_hsn_code').first()
            html_data +="""<tr>		<td style="border: 1px solid #cecdcd;">"""+str(int_index)+"""</td>
                                    <td style="text-align:left;border: 1px solid #cecdcd;">"""+dct_item['strItemName']
            html_data +="""</td>
                                    <td style="text-align:right;border: 1px solid #cecdcd;">"""+str(ins_hsn.get('vchr_hsn_code') or '')+"""</td>
                                    <td style="text-align:right;border: 1px solid #cecdcd;">"""+str(dct_item['intQty'])+"""</td>
                                    <td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(dct_item['dblMopAmount'],2)))+"""</td>
                                    <td style="text-align:right;border: 1px solid #cecdcd;">"""+str("{0:.2f}".format(round(dct_item['dblDiscount'],2)))+"""</td>"""
            if dct_quotation['bln_igst']:
                html_data +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(dct_item['dblIGST'])+"""</td>"""
            else:
                html_data +="""	<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(dct_item['dblSGSTPer'])+"""</td>
                                    <td style="text-align:right;border: 1px solid #cecdcd;">"""+str(dct_item['dblCGSTPer'])+"""</td>"""
            html_data +="""<td style="text-align:right;border: 1px solid #cecdcd;">"""+str(dct_item['dblAmount'])+"""</td>
                                  </tr>"""
            int_index +=1
        html_data+="""</table>
                          </div>
                       <div class="clear"></div>
                    <div class="box2">
                           <div class="section5">
                               <div style="margin-top: 10px;">"""
        if dct_quotation['bln_igst']:
            html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+"""IGST"""+""" :</p></div>
                                        <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_quotation['lst_items']['intTotIGST'],2)))+"""</p></div>
                                        <div class="clear"></div>"""
        else:
            html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+"""CGST"""+""" :</p></div>
                            <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_quotation['lst_items']['intTotCGST'],2)))+"""</p></div>
                            <div class="clear"></div>"""
            html_data+="""<div style="width:60%;float: left;">  <p><span style="font-size: 13px">(+) </span>"""+"""SGST"""+""" :</p></div>
                            <div style="width:40%;float:right;"><p>"""+str("{0:.2f}".format(round(dct_quotation['lst_items']['intTotSGST'],2)))+"""</p></div>
                            <div class="clear"></div>"""


        if dct_quotation['bln_kfc']:
            html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(+) </span>KERALA FLOOD CESS(1%) :</p></div>
            <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_quotation['lst_items']['intKfcTot'],2)))+"""</p></div>
            <div class="clear"></div>"""
        html_data+="""<div style="padding-bottom: 12px;background-color: #ffede3;margin-top: 12px;padding-right:2px;">
                                    <div style="width:60%;float: left;"><p>SUB TOTAL :</p></div>
                                    <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_quotation['lst_items']['intGrandTot'],2)))+"""</p></div>
                                    <div class="clear"></div>"""

        # if dct_invoice['coupon']:
        #     html_data+="""<div style="width:60%;float: left;"><p>COUPON AMOUNT :</p></div>
        #                             <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['coupon'],2)))+"""</p></div>
        #                             <div class="clear"></div>"""
        #
        # if dct_invoice['loyalty']:
        #     html_data+="""<div style="width:60%;float: left;"><p>LOYALTY AMOUNT :</p></div>
        #                             <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['loyalty'],2)))+"""</p></div>
        #                             <div class="clear"></div>"""
        # if dct_invoice['buyback']:
        #     html_data+="""<div style="width:60%;float: left;"><p><span style="font-size: 13px">(-) </span>BUYBACK AMOUNT :</p></div>
        #                             <div style="width:40%;float:right;"><p> """+str("{0:.2f}".format(round(dct_invoice['buyback'],2)))+"""</p></div>
        #                             <div class="clear"></div>"""
        dbl_total = round(dct_quotation['lst_items']['intGrandTot'],2)
        dbl_total_rounded = round(dct_quotation['lst_items']['intGrandTot'])
        p = inflect.engine()
        vchr_amount = p.number_to_words(dbl_total_rounded).title() +' Rupees only.'
        dbl_round_off = round(dbl_total_rounded - dbl_total,2)
        if dbl_round_off != 0.0:
            html_data+="""<div style="width:60%;float: left;"><p>ROUNDING OFF :</p></div>
                          <div style="width:40%;float:right;"><p> """+str(dbl_round_off)+"""</p></div>
                          <div class="clear"></div>"""

        html_data+="""<div style="width:60%;float: left;"><p style="margin-top: 5px;"><b>TOTAL : </b></p></div>
                      <div style="width:40%;float:right;"><p style="margin-top: 4px;"><b> """+str("{0:.2f}".format(round(dbl_total_rounded,2)))+""" </b></p></div>
                      <div class="clear"></div>
                              </div>
                               </div>
                         </div></div>

                         <div style="width:90%;float: left;"><p style="margin-top: 5px;"><b>TOTAL(in words) :  &nbsp&nbsp&nbsp"""+str(vchr_amount)+"""</b></p></div>


                         """
        html_data += """

                    <div style="width:100%;float: left;"><p style="margin-top: 20px;">Thank you very much for your kind enquiry. We are pleased to place our best prices for your consideration </p></div>

                    <div class="box2" style="border-top: 1px solid #c7c2c2;">
            						   <p style="font-weight: 600; text-align:center;color:#055f7a ;">KIND ATTENTION</p>
            							<ul style="list-style-type:disc;">

                                        <li style="font-weight:5000px">This quotation is valid for 7 days from the date of Quotation.  </li>
                                        <br>
                                        <li style="font-weight:5000px">The price quoted is inclusive of all taxes.   </li>
                                        <br>
                                        <li style="font-weight:5000px">Kindly co-operate in case of non availability of stock as well as delay in delivery of product due to any external factors.   </li>
                                        <br>
                                        <li style="font-weight:5000px">Price fluctuation due to any external factors may lead to revision of the above quotation. </li>
                                        <br>
                                        <li style="font-weight:5000px">In case of payment by Cheque/DD/NEFT/RTGS,account details are given below.  </li>


                                        <p style="font-weight: 400;">Payable to : 3G MOBILE WORLD <br>
                                        A/c No. &nbsp&nbsp&nbsp&nbsp : 0347083000000047 <br>
                                        BANK &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp : SIB,CALICUT MAVOOR ROAD BRANCH <br>
                                        IFSC &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp : SIBL0000347
                                        </p>

                                        <li style="font-weight:5000px">Delivery Terms: 100% payment by advance.  </li>

                                        </ul>
                                        </div>
                                        </div>
                                        <div style="width:30%;float: right;"><p style="margin-top: 5px;"><b>for myG <br> <br> <br> <br><br><br><br><br><br> Authorised name &  Signatory</b></p></div>






                                        """


        file_path = settings.MEDIA_ROOT
        # str_base_path = settings.MEDIA_ROOT+'/schemes'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        # ==================================================================================================

        options = {'margin-top': '10.00mm',
                   'margin-right': '10.00mm',
                   'margin-bottom': '10.00mm',
                   'margin-left': '10.00mm',
                   'dpi':400,
                   }



        str_file_name = dct_quotation['qtn_no']+'-'+dct_quotation['qtn_date']+'.pdf'
            # str_file_name = 'sd'+'.pdf'
        str_full_path =  file_path+'/'+str_file_name
        pdfkit.from_string(html_data,str_full_path,options=options)

        # str_file_name = 'invoice-'+dct_quotation['qtn_no']+'-'+dct_quotation['qtn_date']+'.pdf'
        filename =  file_path+'/'+str_file_name
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(filename)
        pdf_writer.addPage(pdf_reader.getPage(0))
        with open(filename, 'wb') as fh:
            pdf_writer.write(fh)
        fs = FileSystemStorage()
        # lst_file =[filename]
        # lst_encoded_string=[]
        encoded_string = ''
        # for filename in lst_file:
        if fs.exists(filename):
            with fs.open(filename) as pdf:
                encoded_string=str(base64.b64encode(pdf.read()))
                # lst_encoded_string.append(str(base64.b64encode(pdf.read())))
        file_details = {}
        file_details['file'] = encoded_string
        file_details['file_name'] = str_file_name

        return file_details
    except Exception as e:
        raise


    pdf_writer = PdfFileWriter()
    for path in lst_pdfs:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

    str_file_name = 'invoice-'+dct_invoice['invoice_no']+'-'+dct_invoice['invoice_date']+'.pdf'
    filename =  file_path+'/'+str_file_name
    with open(filename, 'wb') as fh:
        pdf_writer.write(fh)
