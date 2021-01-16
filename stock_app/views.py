from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
# Create your views here.

from supplier.models import Supplier
from branch.models import Branch
from inventory.models import Products,Brands,Items
from stock_app.models import Stockmaster,Stockdetails
from user_app.models import UserModel
from enquiry.models import Document

class SupplierTypeHead(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            ins_object =[]
            if request.data.get('TYPE') == 'SUPPLIER':
                ins_object = list(Supplier.objects.filter(vchr_name__icontains= request.data.get('term') , fk_company = request.user.userdetails.fk_company)
                    .values('pk_bint_id','vchr_code','vchr_name'))
            elif request.data.get('TYPE') == 'BRANCH':
                ins_object = list(Branch.objects.filter(vchr_name__icontains= request.data.get('term') , fk_company = request.user.userdetails.fk_company)
                    .values('pk_bint_id','vchr_code','vchr_name'))
            elif request.data.get('TYPE') == 'PRODUCT':
                ins_object = list(Products.objects.filter(vchr_product_name__icontains= request.data.get('term')).exclude(vchr_product_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY'])
                    .values('id','vchr_product_name'))
            elif request.data.get('TYPE') == 'BRAND':
                if request.data.get('product_id'):
                    # ins_object = list(Brands.objects.filter(vchr_brand_name__icontains= request.data.get('term') ,
                    #         fk_company = request.user.userdetails.fk_company_id)
                    #     .values('id','vchr_brand_name'))
                    ins_object = list(Items.objects.filter(fk_brand__vchr_brand_name__icontains= request.data.get('term'),fk_product = request.data.get('product_id'))
                        .values('fk_brand','fk_brand__vchr_brand_name').distinct())
            elif request.data.get('TYPE') == 'ITEM':
                # import pdb; pdb.set_trace()
                if request.data.get('product_id') and request.data.get('brand_id') :
                    ins_object = list(Items.objects.filter(vchr_item_name__icontains= request.data.get('term'),
                        fk_product = request.data.get('product_id') , fk_brand = request.data.get('brand_id') )
                        .values('id','vchr_item_name','vchr_item_code'))
            return Response({'status': 'success', 'data':ins_object})
        except Exception as e:
            print(str(e))


class AddStock(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'PURCHASEORDER',fk_company = request.user.userdetails.fk_company)
            if not ins_document:
                ins_document_object = Document.objects.create(fk_company_id = request.user.userdetails.fk_company_id, vchr_module_name = 'PURCHASEORDER',vchr_short_code = 'PO',int_number = 0)
                ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'PURCHASEORDER',fk_company = request.user.userdetails.fk_company)
            str_code = ins_document[0].vchr_short_code
            int_doc_num = ins_document[0].int_number + 1
            ins_document.update(int_number = int_doc_num)
            str_number = str(int_doc_num).zfill(4)
            str_order_no = str_code + '-' + str_number


            lst_product = request.data['productData']
            lst_stock = request.data['stockData']
            if lst_stock['vchr_mode'] == 'credit':
                ins_stock = Stockmaster.objects.create(dat_added= lst_stock['dat_stock'],fk_supplier_id = lst_stock['fk_supplier'],vchr_payment_mode = lst_stock['vchr_mode'],dbl_paid_amount = float(0),
                    fk_branch_id = lst_stock['fk_branch'],fk_company = request.user.userdetails.fk_company,fk_user = request.user.userdetails, vchr_purchase_order_number=str_order_no )
            else:
                ins_stock = Stockmaster.objects.create(dat_added= lst_stock['dat_stock'],fk_supplier_id = lst_stock['fk_supplier'],vchr_payment_mode = lst_stock['vchr_mode'],dbl_paid_amount = float(lst_stock.get('int_paid_amount')),
                    fk_branch_id = lst_stock['fk_branch'],fk_company = request.user.userdetails.fk_company,fk_user = request.user.userdetails, vchr_purchase_order_number=str_order_no)
            if ins_stock.pk_bint_id:
                lst_query_set = []
                for data in lst_product:
                    ins_product_info = Stockdetails(
                        fk_stock_master_id = ins_stock.pk_bint_id,
                        fk_item_id = data['fk_item'],
                        int_qty = data['int_qty'],
                        int_available = data['int_qty'],
                        dbl_cost = data['int_cost'],
                        dbl_min_selling_price = data['int_min_price'],
                        dbl_max_selling_price = data['int_max_price']
                    )
                    lst_query_set.append(ins_product_info)
                if lst_query_set:
                    Stockdetails.objects.bulk_create(lst_query_set);

            # import pdb; pdb.set_trace()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'PURCHASEORDER',fk_company = ins_user.fk_company)
            str_code = ins_document[0].vchr_short_code
            int_doc_num = ins_document[0].int_number
            int_update_num = int_doc_num - 1
            str_number = str(int_doc_num).zfill(4)
            str_enquiry_no = str_code + '-' + str_number
            ins_document.update(int_number = int_update_num)

            print(str(e))
            return JsonResponse({'status': str(e)})


class ListStock(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            dat_start = '';
            dat_end = '';
            if request.data['start_date']:
                dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y').replace(day=1)
            if request.data['end_date']:
                dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')+timedelta(days=1)
            ins_stock = list(Stockmaster.objects.filter(dat_added__gte =dat_start ,dat_added__lte = dat_end).values('dat_added','fk_supplier_id__vchr_name','fk_branch__vchr_name',
                'fk_user_id__first_name','fk_user_id__last_name','pk_bint_id', 'vchr_purchase_order_number'))
            return JsonResponse({'status': 'success', 'data':ins_stock})
        except Exception as e:
            print(str(e))



class ViewStock(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            # import pdb; pdb.set_trace()
            if request.GET.get('id'):
                ins_stock_detail = list(Stockdetails.objects.filter(fk_stock_master =  request.GET.get('id')).values('pk_bint_id','fk_item__vchr_item_name',
                'fk_item','fk_item__fk_brand__vchr_brand_name','fk_item__fk_product__vchr_product_name','int_qty','int_available','dbl_cost','dbl_cost','dbl_min_selling_price','dbl_max_selling_price'))
                ins_stock_master = list(Stockmaster.objects.filter(pk_bint_id= request.GET.get('id')).values('dat_added','fk_supplier_id__vchr_name','fk_branch__vchr_name',
                    'fk_user_id__first_name','fk_user_id__last_name', 'vchr_purchase_order_number'))
                return JsonResponse({'status': 'success', 'ins_stock_detail':ins_stock_detail,'ins_stock_master': ins_stock_master})
        except Exception as e:
            print(str(e))
