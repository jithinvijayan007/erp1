from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics,pagination

from datetime import datetime
from pricelist.models import PriceList
from .serializers import PriceListSerializer
import pandas as pd
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.conf import settings
from django.db.models import F, Func, Value, CharField
from brands.models import Brands
from products.models import Products


# from sqlalchemy.orm.session import sessionmaker
# from sqlalchemy.orm import mapper, aliased
# from sqlalchemy import and_,func ,cast,Date
# from sqlalchemy.sql.expression import literal,union_all
# from aldjemy.core import get_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import case, literal_column
# from sqlalchemy import desc

from POS import ins_logger
import sys, os

from purchase.models import GrnMaster,GrnDetails
from branch_stock.models import BranchStockImeiDetails,BranchStockMaster
from internal_stock.models import StockTransferImeiDetails

from django.db.models import Sum
# Create your views here.
# GrnDetailsSA=GrnDetails.sa
# BranchStockImeiDetailsSA=BranchStockImeiDetails.sa
# BranchStockMasterSA=BranchStockMaster.sa
#
# def Session():
#     from aldjemy.core import get_engine
#     engine=get_engine()
#     _Session = sessionmaker(bind=engine)
#     return _Session()

class AddPriceList(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:

            fk_item=request.data.get("fk_item")
            dbl_supp_amnt=request.data.get("int_supplier_amount")
            dbl_dealer_amnt=request.data.get("int_dealer_amount")
            dbl_mg_amnt=request.data.get("int_myg_amount")
            dbl_cost_amnt=request.data.get("int_cost_price")
            dbl_mop=request.data.get("int_MOP")
            dbl_mrp=request.data.get("int_MRP")
            dat_efct_from=datetime.strptime(request.data.get("date_effective_from"),'%Y-%m-%d')
            PriceList.objects.create(fk_item_id=fk_item,dbl_supp_amnt=dbl_supp_amnt,dbl_cost_amnt=dbl_cost_amnt,\
            dbl_mop=dbl_mop,dbl_mrp=dbl_mrp,dat_efct_from=dat_efct_from,int_status=0,dbl_my_amt=dbl_mg_amnt,dbl_dealer_amt=dbl_dealer_amnt,fk_created_id=request.user.id,dat_created=datetime.now())
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})


class EditPriceList(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb;
            # pdb.set_trace()
            dbl_supp_amnt=request.data.get("int_supplier_amount")
            dbl_cost_amnt=request.data.get("int_cost_price")
            dbl_mop=request.data.get("int_MOP")
            dbl_mrp=request.data.get("int_MRP")
            int_price_id=request.data.get('pk_bint_id')
            dat_efct_from=datetime.strptime(request.data.get("date_effective_from"),'%Y-%m-%d')
            dbl_dealer_amnt=request.data.get("int_dealer_amount")
            dbl_mg_amnt=request.data.get("int_myg_amount")
            PriceList.objects.filter(pk_bint_id=int_price_id).update(dbl_supp_amnt=dbl_supp_amnt,dbl_cost_amnt=dbl_cost_amnt,\
            dbl_mop=dbl_mop,dbl_mrp=dbl_mrp,dat_efct_from=dat_efct_from,dbl_my_amt=dbl_mg_amnt,dbl_dealer_amt=dbl_dealer_amnt\
            ,fk_updated_id=request.user.id,dat_updated=datetime.now())
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class DeletePriceList(APIView):
    permission_classes=[AllowAny]
    def patch(self,request):
        try:

            int_price_id=request.data.get('pk_bint_id')
            PriceList.objects.filter(pk_bint_id=int_price_id).update(int_status=-1,fk_updated_id=request.user.id,dat_updated=datetime.now())
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class ListPriceList(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            dat_to= request.data.get('datTo')
            dat_from= request.data.get('datFrom')
            if(request.GET.get('id')):
                lst_pricelist=list(PriceList.objects.filter(pk_bint_id=request.GET.get('id')).values('fk_item__vchr_name','fk_item__vchr_item_code','fk_item_id','pk_bint_id','dbl_supp_amnt','dbl_cost_amnt','dbl_mop','dbl_mrp','dat_efct_from','dbl_my_amt','dbl_dealer_amt'))
                lst_pricelist[0]['code_name']=lst_pricelist[0]['fk_item__vchr_item_code']+" - "+lst_pricelist[0]['fk_item__vchr_name']
            else:
                lst_pricelist=list(PriceList.objects.filter(int_status=0,dat_efct_from__lte=dat_to,dat_efct_from__gte = dat_from).values('fk_item__vchr_item_code','fk_item_id','pk_bint_id','dbl_supp_amnt','dbl_cost_amnt','dbl_mop','dbl_mrp','dat_efct_from','dbl_my_amt','dbl_dealer_amt'))
            for i in lst_pricelist:
                # i['dat_efct_from']=i['dat_efct_from'].strftime('%d-%m-%Y')
                i['dat_efct_from']=str(i['dat_efct_from']).split(" ")[0]
            return Response({'status':1,'list':lst_pricelist})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})
    def get(self,request):
        try:
            if(request.GET.get('id')):
                lst_pricelist=list(PriceList.objects.filter(pk_bint_id=request.GET.get('id')).values('fk_item__vchr_name','fk_item__vchr_item_code','fk_item_id','pk_bint_id','dbl_supp_amnt','dbl_cost_amnt','dbl_mop','dbl_mrp','dat_efct_from','dbl_my_amt','dbl_dealer_amt'))
                lst_pricelist[0]['code_name']=lst_pricelist[0]['fk_item__vchr_item_code']+" - "+lst_pricelist[0]['fk_item__vchr_name']
            else:
                lst_pricelist=list(PriceList.objects.filter(int_status=0).values('fk_item__vchr_item_code','fk_item_id','pk_bint_id','dbl_supp_amnt','dbl_cost_amnt','dbl_mop','dbl_mrp','dat_efct_from','dbl_my_amt','dbl_dealer_amt'))
            for i in lst_pricelist:
                # i['dat_efct_from']=i['dat_efct_from'].strftime('%d-%m-%Y')
                i['dat_efct_from']=str(i['dat_efct_from']).split(" ")[0]
            return Response({'status':1,'list':lst_pricelist})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'reason':e})

class HistoryPriceList(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb;
            # import pdb; pdb.set_trace()
            int_id=request.data.get('fk_item_id')
            # int_id=1
            # pdb.set_trace()
            # rst_enquiry_grn = session.query(func.sum(GrnDetailsSA.int_qty).label("qtyGRN"),func.sum(BranchStockImeiDetailsSA.int_qty).label("qtyBRA").\
            #                   filter(GrnDetailsSA.fk_item==int_id).\
            #                   outerjoin(BranchStockMasterSA,GrnDetailsSA.pk_bint_id==BranchStockImeiDetailsSA.fk_grn_details))
            # lst_grn_brafk=list(GrnDetails.objects.values_list('fk_purchase__fk_branch',flat=True))
            # lst_branch_fk = list(StockTransferImeiDetails.objects.filter(fk_details__fk_transfer__fk_from_in=(lst_grn_brafk)).aggregate(Sum('fk_details__int_qty')))
            # int_sum_grn=GrnDetails.objects.filter(fk_purchase__fk_branch_in=(lst_branch_fk)).aggregate(Sum('int_qty'))
            # lst_grn_fk=list(StockTransferImeiDetails.objects.values_list('fk_grn_details',flat=True))
            # int_sum_bra=list(GrnDetails.objects.filter(pk_bint_id_in=(lst_grn_fk)).aggregate(Sum('int_qty')))

            lst_item_grn=GrnDetails.objects.filter(fk_item_id=int_id)
            lst_grn=list(lst_item_grn.values('dbl_costprice','fk_purchase__dat_purchase','int_qty','int_avail','pk_bint_id'))

            lst_grn_pk = list(lst_item_grn.values_list('pk_bint_id',flat=True))
            lst_sum_branch = list(BranchStockImeiDetails.objects.filter(fk_grn_details_id__in=(lst_grn_pk)).values('fk_grn_details_id').annotate(Sum('int_qty')))
            for j in lst_grn:
                for i in lst_sum_branch:
                     if i['fk_grn_details_id']==j['pk_bint_id']:
                            j['int_left']=j['int_avail']+i['int_qty__sum']
                if 'int_left' not in j:
                    j['int_left']=j['int_avail']
                j.pop('int_avail')


            if lst_grn:
                for i in lst_grn:
                    if i['fk_purchase__dat_purchase']:
                        i['fk_purchase__dat_purchase']=i['fk_purchase__dat_purchase'].strftime('%d-%m-%y')
            return Response({'status':1,'list':lst_grn})
        except Exception as e:
            return Response({'status':0,'reason':e})
class CustomPagination(pagination.PageNumberPagination):
    page_size = 50
    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages*10,
            'results': data
        })

class PriceListData(generics.ListAPIView,APIView):
    permission_classes=[AllowAny]

    serializer_class = PriceListSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = PriceList.objects.annotate(vchr_item_name=Concat('fk_item__vchr_item_code', Value('-'), 'fk_item__vchr_name'),
                                              str_formatted_date=Func( F('dat_efct_from'), Value('dd-MM-yyyy'), function='to_char', output_field=CharField() )).values(
                                                                                                                                                            'vchr_item_name',
                                                                                                                                                            'fk_item__vchr_item_code',
                                                                                                                                                            'fk_item__vchr_name',
                                                                                                                                                            'fk_item__fk_brand_id',
                                                                                                                                                            'fk_item__fk_brand__vchr_name',
                                                                                                                                                            'fk_item__fk_product_id',
                                                                                                                                                            'fk_item__fk_product__vchr_name',
                                                                                                                                                            'dat_efct_from',
                                                                                                                                                            'str_formatted_date',
                                                                                                                                                            'dbl_supp_amnt',
                                                                                                                                                            'dbl_cost_amnt',
                                                                                                                                                            'dbl_mop',
                                                                                                                                                            'dbl_mrp',
                                                                                                                                                            'dbl_my_amt',
                                                                                                                                                            'dbl_dealer_amt','fk_item_id').order_by('-dat_efct_from','fk_item__fk_product__vchr_name','fk_item__fk_brand__vchr_name')
        int_pd_id = self.request.query_params.get('pd_id', None)
        int_bd_id = self.request.query_params.get('bd_id', None)
        int_it_id = self.request.query_params.get('it_id', None)

        if int_pd_id :
            queryset = queryset.filter(fk_item__fk_product_id =int_pd_id)
        if int_bd_id :
            queryset = queryset.filter(fk_item__fk_brand_id =int_bd_id)

        if int_it_id :
            queryset = queryset.filter(fk_item__id =int_it_id)
        return queryset

    def post(self,request):

        lst_data = self.get_queryset()
        int_bd_id = request.data.get('IntBrandId')
        int_pd_id = request.data.get('IntProductId')
        str_brand_filter = 'ALL'
        str_product_filter = 'ALL'
        if int_bd_id:
            lst_data = lst_data.filter(fk_item__fk_brand_id = int_bd_id )
            ins_brand = Brands.objects.filter(pk_bint_id =int_bd_id).values('vchr_name').first()
            str_brand_filter =ins_brand['vchr_name'] if ins_brand else str_brand_filter
        if int_pd_id:
            lst_data = lst_data.filter(fk_item__fk_product_id = int_pd_id )
            ins_product = Products.objects.filter(pk_bint_id =int_pd_id).values('vchr_name').first()

            str_product_filter = ins_product['vchr_name'] if ins_product else str_product_filter

        if not lst_data:
            return Response({'status':0})


        
        df_temp_data = pd.DataFrame(list(lst_data))
        df_exp_data =   pd.DataFrame()
        # df_exp_data['S.No'] = list(range(1,len(df_temp_data.index)+1))

        df_exp_data['Product'] = df_temp_data['fk_item__fk_product__vchr_name']
        df_exp_data['Brand'] = df_temp_data['fk_item__fk_brand__vchr_name']
        df_exp_data['Item/Model Name'] = df_temp_data['vchr_item_name']
        df_exp_data['Date Effect From'] = df_temp_data['str_formatted_date']       
        # df_exp_data['Supplier Amount'] = df_temp_data['dbl_supp_amnt']
        df_exp_data['Cost Price'] = df_temp_data['dbl_cost_amnt']
        df_exp_data['Dealer Amount'] = df_temp_data['dbl_dealer_amt']
        df_exp_data['Mop'] = df_temp_data['dbl_mop']
        df_exp_data['Myg price'] = df_temp_data['dbl_my_amt']
        df_exp_data['Mrp'] = df_temp_data['dbl_mrp']





        # df_exp_data.index = pd.Series(start=1, stop=df_exp_data.shape[0]+1, step=1)

        sheet_name1 = 'sheet_1'
        str_file = datetime.now().strftime('%d-%m-%Y_%H_%M_%S')+'_pricelist.xlsx'
        filename =settings.MEDIA_ROOT+'/'+str_file
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df_exp_data.to_excel(writer,index=False, sheet_name=sheet_name1,startrow=13, startcol=0)

        workbook = writer.book
        merge_format1 = workbook.add_format({
        'bold': 20,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size':23
        })

        merge_format2 = workbook.add_format({
        'bold': 4,
        'border': 1,
        'align': 'left',
        'valign': 'vleft',
        'font_size':12
        })
        merge_format3 = workbook.add_format({
        'bold': 6,
        'border': 1,
        'align': 'left',
        'valign': 'vleft',
        'font_size':16
        })

        worksheet = writer.sheets[sheet_name1]

        str_report = 'Price List Report'
        worksheet.merge_range('A1+:I2', str_report, merge_format1)
        worksheet.merge_range('A2+:S3',"",merge_format2)
        worksheet.merge_range('A5+:D5',"REPORT DATE          : "+datetime.strftime(datetime.now(),'%d-%m-%Y ,%I:%M %p'),merge_format2)
        worksheet.merge_range('A6+:D6', 'Taken By                 :  '+request.user.username, merge_format2)
        worksheet.merge_range('A7+:D7', 'Product                  :  '+str_product_filter, merge_format2)
        worksheet.merge_range('A8+:D8', 'Brand                     :  '+str_brand_filter, merge_format2)




        for i, col in enumerate(df_exp_data.columns):



            # find length of column i
            column_len = df_exp_data[col].astype(str).str.len().max()
            # Setting the length if the column header is larger
            # than the max column value length
            column_len = max(column_len, len(col))
            # set the column length
            worksheet.set_column(i, i, column_len)

        writer.save()



        str_exp_path = settings.HOSTNAME+'/media/'+str_file

        return Response({'status':1,'export':str_exp_path,'str_file_name':str_file})
