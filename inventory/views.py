from django.shortcuts import render

# Create your views here.

from userdetails.models import UserDetails as UserModel
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from item_category.models import Item as Items,ItemGroup, ItemCategory
from inventory.models import ItemDetails
from brands.models import Brands
from products.models import Products
from rest_framework.serializers import (ModelSerializer,ValidationError)
from rest_framework.views import APIView
from django.db.models import Q,F
from stock_app.models import Stockmaster,Stockdetails
from company.models import Company as CompanyDetails
from branch.models import Branch
from django.db.models import Sum
from django.conf import settings
import operator
from functools import reduce
from POS import ins_logger
# Create your views here.
import psycopg2
import requests
import json
import urllib.request
import psycopg2
import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date,case, literal_column,or_
from sqlalchemy.sql.expression import literal,union_all
from bulk_update.helper import bulk_update

ItemCategorySA = ItemCategory.sa
ItemsSA = Items.sa
ProductsSA = Products.sa


def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()


class CategorySerializer(ModelSerializer):

    class Meta:
        model = Products
        fields = '__all__'

class CategoryApiView(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class CategoryTypeahead(APIView):
    def post(self,request,):
        try:
            str_search_term = request.data.get('term',-1)
            lst_category = []
            if str_search_term != -1:
                ins_category = Products.objects.filter(vchr_product_name__icontains=str_search_term,fk_company = request.user.userdetails.fk_company).exclude(vchr_product_name__in=['MYG CARE','SMART CHOICE','PROFITABILITY','GDP']).values('id','vchr_product_name')
                if ins_category:
                    for itr_item in ins_category:
                        dct_category = {}
                        dct_category['name'] = itr_item['vchr_product_name'].title()
                        dct_category['id'] = itr_item['id']
                        lst_category.append(dct_category)
                return Response({'status':'success','data':lst_category})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

class SubCategoryView(APIView):
    """Add,edit,view and delete subcategory"""
    def get(self, request):
        try:
            # 
            # id used for get brand for edit
            int_id = int(request.GET.get('id',0))
            if int_id > 0:
                lst_subcategory = list(Brands.objects.filter(id = int_id, fk_company = request.user.userdetails.fk_company_id).values('id','vchr_brand_name'))
            else:
                lst_subcategory = list(Brands.objects.filter(fk_company = request.user.userdetails.fk_company_id).values('id','vchr_brand_name'))
            return Response({'lst_subcategory':lst_subcategory})
        except Exception as e:
            return Response({'result':'failed','reason':e})

    def post(self, request):
        try:
            # 
            vchr_subcategory = request.data['vchr_subcategory'].upper()
            # fk_category = request.data['fk_category']
            fk_company = request.data['fk_company']
            ins_duplicate = Brands.objects.filter(vchr_brand_name = vchr_subcategory, fk_company = CompanyDetails.objects.get(pk_bint_id = fk_company)).values()
            if not ins_duplicate:
                ins_subcategory = Brands(vchr_brand_name = vchr_subcategory, fk_company = CompanyDetails.objects.get(pk_bint_id = fk_company))
                ins_subcategory.save()
                return Response({'status':'successfully created'})
            else:
                return Response({'status':'already exist'})
        except Exception as e:
            return Response({'result':'failed','reason':e})

    def put(self,request):
        try:
            # 
            int_id = request.data['id']
            vchr_subcategory = request.data['vchr_subcategory'].upper()
            fk_company = request.data['fk_company']
            # fk_category = request.data['fk_category']
            ins_duplicate = Brands.objects.filter(~Q(id = int_id) & Q(vchr_brand_name = vchr_subcategory) & Q(fk_company = CompanyDetails.objects.get(pk_bint_id = fk_company))).values()
            if not ins_duplicate:
                ins_subCategory = Brands.objects.filter(id = int_id, fk_company = CompanyDetails.objects.get(pk_bint_id = fk_company)).update(vchr_brand_name = vchr_subcategory)
                return Response({'status':'successfully updated'})
            else:
                return Response({'status':'already exist'})
        except Exception as e:
            return Response({'status':'failed','reason':str(e)})

    def delete(self,request):
        try:
            # 
            int_id = request.GET['id']
            ins_product = Items.objects.filter(fk_brand = Brands.objects.get(id = int_id)).values()
            if not ins_product:
                Brands.objects.filter(id = int_id).delete()
                return Response({'status':'success'} )
            else:
                return Response({'status':'cannot delete'})
        except Exception as e:
            return Response({'status':'failed','reason':str(e)})

class SubCategoryTypeahead(APIView):
    def post(self,request,):
        try:
            # 
            str_search_term = request.data.get('term',-1)
            int_category = request.data.get('category',-1)
            lst_subcategory = []
            if str_search_term != -1:
                ins_subcategory = Brands.objects.filter(vchr_brand_name__icontains=str_search_term, fk_company = request.user.userdetails.fk_company_id).values('id','vchr_brand_name')
                if ins_subcategory:
                    for itr_item in ins_subcategory:
                        dct_subcategory = {}
                        dct_subcategory['name'] = itr_item['vchr_brand_name'].title()
                        dct_subcategory['id'] = itr_item['id']
                        lst_subcategory.append(dct_subcategory)
                return Response({'status':'success','data':lst_subcategory})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

class ProductView(APIView):
    def post(self,request):
        try:
            # 
            ins_product_code_exist = Items.objects.filter(vchr_item_code= request.data.get('itemcode').upper(), fk_product__fk_company = request.user.userdetails.fk_company)
            if ins_product_code_exist :
                return Response({'status':'failed','reason':'code already exist'})
            ins_product_name_exist = Items.objects.filter( vchr_name =  request.data.get('product').upper(),fk_product = request.data.get('category'),fk_brand = request.data.get('subcategory'), fk_product__fk_company = request.user.userdetails.fk_company)
            if ins_product_name_exist :
                return Response({'status':'failed','reason':'name already exist'})
            ins_product_barcode_exist = Items.objects.filter( vchr_barcode =  request.data.get('barcode').upper(),fk_product__fk_company = request.user.userdetails.fk_company)
            if ins_product_barcode_exist:
                return Response({'status':'failed','reason':'barcode already exist'})
            ins_product = Items.objects.create(vchr_item_code= request.data.get('itemcode').upper(),vchr_barcode= request.data.get('barcode').upper(),dbl_apx_amount=float(request.data.get('itemprice')),vchr_name = request.data.get('product').upper(),fk_product = Products.objects.get(id = request.data.get('category')),fk_brand = Brands.objects.get(id = request.data.get('subcategory')),fk_item_group_id = request.data.get('intItemGroup'))
            # ins_product.save()

            return Response({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

    def get(self,request):
        try:
            # import pdb;pdb.set_trace()
            int_id = int(request.GET.get('id',0))
            if int_id > 0:
                lst_data = list(Items.objects.filter(id = int_id,fk_brand_id__isnull=False).values('vchr_item_code','vchr_barcode','vchr_name','fk_product__vchr_product_name','fk_brand__vchr_brand_name','id','dbl_apx_amount','fk_item_group_id','fk_item_group__vchr_item_group'))
            else:
                lst_data = list(Items.objects.filter(fk_product__fk_company = request.user.userdetails.fk_company,fk_brand_id__isnull=False).values('vchr_item_code','vchr_barcode','vchr_name','fk_product__vchr_product_name','fk_brand__vchr_brand_name','id','dbl_apx_amount','fk_item_group__vchr_item_group'))
            return Response(lst_data)
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

    def patch(self,request):
        try:
            # 
            ins_code_exist = Items.objects.filter(~Q(id = int(request.data.get('id'))) & Q(vchr_item_code= request.data.get('itemcode').upper()) & Q(fk_product__fk_company = request.user.userdetails.fk_company))
            if ins_code_exist:
                return Response({'status':'failed','reason':'code exist'})
            ins_name_exist = Items.objects.filter(~Q(id = int(request.data.get('id'))) & Q(vchr_name= request.data.get('product').upper()) & Q(fk_brand = request.data.get('subcategory'))  & Q(fk_product__fk_company = request.user.userdetails.fk_company))
            if ins_name_exist:
                return Response({'status':'failed','reason':'name exist'})
            # 
            ins_barcode_exist = Items.objects.filter(~Q(id = int(request.data.get('id'))) & Q(vchr_barcode= request.data.get('barcode').upper()) & Q(fk_product__fk_company = request.user.userdetails.fk_company))
            if ins_barcode_exist:
                return Response({'status':'failed','reason':'barcode exist'})
            ins_product = Items.objects.filter(id = int(request.data.get('id')))
            ins_product.update(vchr_barcode =request.data.get('barcode').upper(),dbl_apx_amount=float(request.data.get('itemprice')),vchr_item_code =request.data.get('itemcode').upper(), vchr_name= request.data.get('product').upper(),fk_product = Products.objects.get(id = request.data.get('category')),fk_brand = Brands.objects.get(id = request.data.get('subcategory')),fk_item_group_id = request.data.get('intItemGroup'))
            return Response({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

class GetProductById(APIView):
    def get(self,request):
        try:
            lst_data = list(Items.objects.filter(id = int(request.GET.get('id'))).values('vchr_barcode','vchr_item_code','vchr_name','fk_product__vchr_product_name','fk_brand__vchr_brand_name','id','fk_product','fk_brand','dbl_apx_amount','fk_item_group_id','fk_item_group__vchr_item_group'))
            return Response(lst_data)
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

    def post(self,request):
        try:
            ins_stock = Stockdetails.objects.filter(fk_item_id = int(request.data.get('id')), fk_stock_master__fk_company_id = request.user.userdetails.fk_company_id).values()
            if ins_stock:
                return Response({'status':'failed', 'reason':'already used'})
            else:
                ins_product = Items.objects.filter(id = int(request.data.get('id')))
                ins_product.delete()
            return Response({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})


class SubCategoryByCat(APIView):
    def post(self,request,):
        try:
            # 
            str_search_term = request.data['term']
            str_product = request.data['product']
            # 
            lst_subcategory = []
            if str_search_term != -1:
                # ins_product_id=Products.objects.filter(vchr_product_name=request.data['product']).values('id')
                # ins_subcategory = Items.objects.filter(fk_brand__vchr_brand_name__icontains=str_search_term,fk_product__vchr_product_name = str_product,fk_brand__fk_company=request.user.userdetails.fk_company).values('fk_brand','fk_brand__vchr_brand_name').distinct()
                ins_subcategory = Items.objects.filter(fk_brand__vchr_name__icontains=str_search_term,fk_product__vchr_name = str_product,fk_brand__fk_company_id=request.user.userdetails.fk_company_id).annotate(fk_brand__vchr_brand_name = F('fk_brand__vchr_name')).values('fk_brand','fk_brand__vchr_brand_name').distinct()
                for itr_item in ins_subcategory:
                    dct_subcategory = {}
                    dct_subcategory['name'] = itr_item['fk_brand__vchr_brand_name']
                    dct_subcategory['id'] = itr_item['fk_brand']
                    lst_subcategory.append(dct_subcategory)
                return Response({'status':'success','data':lst_subcategory})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})


class itemBySub(APIView):
    def post(self,request,):
        try:
            
            str_search_term = request.data['term']
            str_brand = request.data['brandId']
            str_product = request.data['product']
            lst_subcategory = []
            int_company_id = request.user.userdetails.fk_company
            lst_branch = []
            # lst_branch = list(UserModel.objects.filter(id=request.user.id).values('fk_branch','fk_branch__fk_territory'))
            # if lst_branch:
            #     int_branch_id = lst_branch[0]['fk_branch']
            #     int_territory_id = lst_branch[0]['fk_branch__fk_territory']
            if str_search_term != -1:
                lst_term = str_search_term.split()
                lst_search_term=[[str_search_term.strip()]]
                if len(lst_term)>1 and lst_term[1]!='':     # if search_term word length grater than 1 then create search term words combinations
                    for i in range(len(lst_term)-1,0,-1):   # last word split
                        lst=[]
                        lft_string=''
                        for j in range(0,i):                # left side string
                            lft_string+=lst_term[j]+' '
                        lst.append(lft_string.strip())
                        for j in range(i,len(lst_term)):    # right side words append to list
                            lst.append(lst_term[j])
                        lst_search_term.append(lst)
                ins_subcategory=[]
                for search_term in lst_search_term:         # search term combinations list check with items db
                    query = reduce(operator.and_, (Q(vchr_name__icontains = item) for item in search_term))
                    ins_data = list(Items.objects.filter(query | Q(vchr_item_code__icontains = str_search_term), fk_brand = str_brand , fk_product__vchr_name__icontains = str_product,fk_product__fk_company = int_company_id ).annotate(id = F('pk_bint_id'),vchr_name= F('vchr_name')).values('id','vchr_name','vchr_item_code')[:50])
                    for item in ins_data:
                        if item not in ins_subcategory:
                            ins_subcategory.append(item)
                    if len(ins_subcategory)>50:
                        break
                # ins_subcategory = Items.objects.filter(Q(vchr_item_name__icontains = str_search_term) | Q(vchr_item_code__icontains = str_search_term), fk_brand = str_brand , fk_product__vchr_product_name__icontains = str_product,fk_product__fk_company = int_company_id ).values('id','vchr_name','vchr_item_code')[:50]
                
                for itr_item in ins_subcategory[:50]:
                    dct_subcategory = {}
                    dct_subcategory['name'] = itr_item['vchr_name']
                    dct_subcategory['id'] = itr_item['id']
                    dct_subcategory['code'] = itr_item['vchr_item_code']
                    if lst_branch:
                        lst_stock = list(Stockdetails.objects.filter(fk_item_id = itr_item['id'],fk_stock_master__fk_branch =int_branch_id,int_available__gt=0).values('dbl_min_selling_price','dbl_max_selling_price','int_available').order_by('fk_stock_master__dat_added'))
                        if lst_stock:
                            dct_subcategory['stock'] = lst_stock[0]
                        else:
                            lst_stock_in = list(Stockdetails.objects.filter(fk_item_id = itr_item['id'],fk_stock_master__fk_branch__fk_territory=int_territory_id).values('fk_stock_master__fk_branch').annotate(Sum('int_available')))
                            dct_subcategory['stockInOthrBranch']=[]
                            for dct_item in lst_stock_in:
                                dct_temp = {}
                                ins_branch = Branch.objects.filter(pk_bint_id=dct_item['fk_stock_master__fk_branch']).values('vchr_name')
                                dct_temp['branch'] = ins_branch[0]['vchr_name']
                                dct_temp['int_qty'] = dct_item['int_available__sum']
                                dct_subcategory['stockInOthrBranch'].append(dct_temp)
                    lst_details = ItemDetails.objects.filter(fk_item_id = itr_item['id']).values('json_spec','vchr_item_img')
                    dct_details={}
                    if lst_details:
                        dct_details=lst_details.first()
                        dct_subcategory['spec'] = dct_details['json_spec']
                        dct_subcategory['img'] = dct_details['vchr_item_img']
                    lst_order = Products.objects.filter(vchr_name__icontains = str_product).values('dct_product_spec','vchr_product_img')

                    if lst_order:
                        dct_details=lst_order.first()
                        if dct_details['dct_product_spec']:
                            dct_subcategory['order'] = dct_details['dct_product_spec'].keys()
                        if not dct_subcategory.get('img'):
                            dct_subcategory['img'] = dct_details['vchr_product_img']
                    if 'spec' not in dct_subcategory:
                        dct_subcategory['spec']={}
                    if 'img' not in dct_subcategory:
                        dct_subcategory['img']=settings.HOSTNAME+'/media/'+dct_subcategory['img']
                    lst_subcategory.append(dct_subcategory)
                return Response({'status':'success','data':lst_subcategory})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})


class itemByBrand(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data['term']
            str_product = request.data['productId']
            int_company_id = request.user.userdetails.fk_company_id
            if str_search_term != -1:
                lst_items = []
                if str_product:
                    ins_item = Items.objects.filter(Q(vchr_name__icontains = str_search_term) | Q(vchr_item_code__icontains = str_search_term), fk_product = str_product ,fk_product__fk_company = int_company_id ).values('pk_bint_id','vchr_name','vchr_item_code','fk_brand_id','fk_product_id','fk_brand_id__vchr_name','fk_product_id__vchr_name')[:50]
                else:
                    ins_item = Items.objects.filter(Q(vchr_name__icontains = str_search_term) | Q(vchr_item_code__icontains = str_search_term),fk_product__fk_company = int_company_id ).values('pk_bint_id','vchr_name','vchr_item_code','fk_brand_id','fk_product_id','fk_brand_id__vchr_name','fk_product_id__vchr_name')[:50]
                for itr_item in ins_item:
                    dct_item = {}
                    dct_item['name'] = itr_item['vchr_name']
                    dct_item['id'] = itr_item['pk_bint_id']
                    dct_item['code'] = itr_item['vchr_item_code']
                    dct_item['brand_id'] = itr_item['fk_brand_id']
                    dct_item['product_id'] = itr_item['fk_product_id']
                    dct_item['brand_name'] = itr_item['fk_brand_id__vchr_name']
                    dct_item['product_name'] = itr_item['fk_product_id__vchr_name']

                    # 
                    # lst_stock = list(BranchStock.objects.filter(fk_item_id = 29064,fk_branch= request.user.userdetails.fk_branch_id , int_available__gt=0).values('pk_bint_id','int_available','json_avail_imei','fk_item__vchr_item_name').order_by('dat_added'))
                    # lst_stock = list(BranchStock.objects.filter(fk_item_id = itr_item['id'],fk_branch= request.user.userdetails.fk_branch_id , int_available__gt=0).values('pk_bint_id','int_available','json_avail_imei','fk_item__vchr_item_name','fk_stock_details__dbl_cost','fk_stock_details__fk_stock_master__fk_supplier').order_by('dat_added'))
                    #
                    # if lst_stock:
                    #     dct_item['stock'] = lst_stock

                    lst_items.append(dct_item)

            return Response({'status':'1','data':lst_items})
        except Exception as e:
            return Response({"status":"0","message":str(e)})

class SynchronizeView(APIView):
    def post(self,request):
        try:
            # 
            conn = None
            conn = psycopg2.connect(host="localhost",database="myg_database_trail", user="admin", password="sSHeEfZ74u")
            # conn = psycopg2.connect(host="localhost",database="myg_db", user="admin", password="tms@123")
            conn.autocommit = True
        except Exception as e:
            return JsonResponse({'status':'failed','reason':'cannot connect to database'})
        try:
            cwd = os.getcwd()
            t=datetime.datetime.now()
            filename=cwd+'/'+t.strftime('%m_%d_%Y_%M')+'.txt'
            f= open(filename,"w+")
            cur = conn.cursor()
            if request.data.get('productId'):
                    cur.execute("select vchr_product_name,id from products where id ="+str(request.data.get('productId'))+" order by id ")
            else:
                cur.execute("select vchr_product_name,id from products order by id ")
            lst_product=cur.fetchall()
            dct_products={data[0]:data[1] for data in lst_product}
            cur.execute("select vchr_item_code from items order by id ")
            lst_items=cur.fetchall()
            lst_items_code=[data[0] for data in lst_items]
            for dct_pro in dct_products:
                print(dct_pro)
                str_to_wtite=''
                # 
                if request.data.get('brandId'):
                        cur.execute("select vchr_brand_name,id from brands where id "+str(request.data.get('brandId'))+" order by id ")
                else:
                    cur.execute("select vchr_brand_name,id from brands where id in (select distinct(fk_brand_id) from items where fk_product_id="+str(dct_products[dct_pro])+") order by id ")
                lst_brand=cur.fetchall()
                dct_brands={data[0]:data[1] for data in lst_brand}
                for dct_bran in dct_brands:
                    f.write(str_to_wtite+"\n")
                    str_to_wtite=''
                    str_to_wtite+='product:'+dct_pro + ' ' + 'Brand:' + dct_bran
                    print(dct_bran)
                    time.sleep(15)
                    r=requests.get("http://13.71.85.222/api/apxapi/GetItemModelInfo?CompanyCode=myG&Product="+dct_pro+"&Brand="+dct_bran,headers={"USERID":"apx","SECURITYCODE":"5423-1477-8162-2791"})
                    # 
                    if r.status_code != 200:
                        print("no valid respondse from apx "+ r.status_code)
                        str_to_wtite+=" no valid respondse from apx "+ r.status_code
                        # cur.close()
                        # conn.close()
                        f.write(str_to_wtite+"\n")
                        continue
                    elif not r.text:
                        print("no data got from apx")
                        str_to_wtite+=" no data got from apx"
                        f.write(str_to_wtite+"\n")
                        continue
                    apx_row_data=json.loads(r.text)
                    # lst_new_data = [ data for data in lst_data if dt.strptime(str(lst_data[-1]['CREATED_ON']),'%Y%m%d') > dat_yesterday ]
                    if not apx_row_data:
                        print("no data got in list apx")
                        str_to_wtite+=" no data got in list apx"
                        # cur.close()
                        # conn.close()
                        continue
                    lst_apx_code=[dt['ITEM_CODE'] for dt in apx_row_data]
                    item_code_diff=set(lst_apx_code)-set(lst_items_code)
                    print("diif items "+str(len(item_code_diff)))
                    str_to_wtite+=" diif items "+str(len(item_code_diff))
                    if not item_code_diff:
                        f.write(str_to_wtite+"\n")
                        continue
                        # cur.close()
                        # conn.close()
                        # return True
                    lst_diff_data=[data for data in apx_row_data if data['ITEM_CODE'] in item_code_diff]
                    for dct_data in lst_diff_data:
                        if dct_data['BRAND_NAME'] in dct_brands:
                            try:
                                cur.execute("insert into items (vchr_name,vchr_item_code,fk_brand_id,fk_product_id,vchr_barcode,dat_updated) values ('" +dct_data['ITEM_NAME'].split(':')[0]+ "','" +dct_data['ITEM_CODE']+ "',"+str(dct_brands[dct_data['BRAND_NAME']])+ ","+str(dct_products[dct_data['PRODUCT_NAME']])+ ",'"+dct_data['ITEM_CODE']+"','"+str(datetime.datetime.now().date())+"');")
                            except Exception as e:
                                print("item_cant update")
                                str_to_wtite+=" item_cant update"
                                f.write(str_to_wtite+"\n")
                                pass
                        else:
                            cur.execute("insert into brands (vchr_brand_name,fk_company_id) values ('"+dct_data['BRAND_NAME']+"',1);")
                            cur.execute("select vchr_brand_name,id from brands order by id")
                            lst_brand=cur.fetchall()
                            dct_brands={data[0]:data[1] for data in lst_brand}
                            try:
                                cur.execute("insert into items (vchr_name,vchr_item_code,fk_brand_id,fk_product_id,vchr_barcode,dat_updated) values ('" +dct_data['ITEM_NAME'].split(':')[0]+ "','" +dct_data['ITEM_CODE']+ "',"+str(dct_brands[dct_data['BRAND_NAME']])+ ","+str(dct_products[dct_data['PRODUCT_NAME']])+ ",'"+dct_data['ITEM_CODE']+"','"+str(datetime.datetime.now().date())+"');")
                            except Exception as e:
                                print("item_cant update")
                                str_to_wtite+=" item_cant update"
                                f.write(str_to_wtite+"\n")
                                pass
            cur.close()
            conn.close()
            # 
            f.close()
            # file1 = open(filename,"r")
            # attachment = MIMEText(file1.read())
            # server = smtplib.SMTP('smtp.pepipost.com', 587)
            # server.login("shafeer","Tdx@9846100662")
            # msg = MIMEMultipart()
            # msg['Subject'] = 'Item update info'
            # attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            # msg.attach(attachment)
            # server.sendmail("info@enquirytrack.com", 'nikhil@travidux.com', msg.as_string())
            os.remove(filename)
            return JsonResponse({'status':'success'})
        except Exception as e:
            cur.close()
            conn.close()
            f.close()
            # file1 = open(filename,"r")
            # attachment = MIMEText(file1.read())
            # server = smtplib.SMTP('smtp.pepipost.com', 587)
            # server.login("shafeer","Tdx@9846100662")
            # msg = MIMEMultipart()
            # msg['Subject'] = 'Item update info'
            # attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            # msg.attach(attachment)
            # server.sendmail("info@enquirytrack.com", ['nikhil@travidux.com','arunkumar@travidux.com'], msg.as_string())

            os.remove(filename)
            return JsonResponse({'status':'failed'})

class ProductTypeAhead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            user = UserModel.objects.filter(id = request.user.id)
            str_search_term = request.data.get('term',-1)
            lst_product = []
            if str_search_term != -1:
                ins_product = Products.objects.filter(~Q(vchr_product_name='SMART CHOICE'),Q(vchr_product_name__icontains = str_search_term),fk_company=user[0].fk_company).exclude(vchr_product_name__in =['GDP','GDEW']).values('id','vchr_product_name')

                if ins_product:
                    for item in ins_product:
                        dct_product = {}
                        dct_product['name'] = item['vchr_product_name']
                        # dct_product['product'] = item['fk_product__vchr_product_name']
                        dct_product['id'] = item['id']
                        lst_product.append(dct_product)
                return Response({'status':'success','data':lst_product})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            return Response({"status":"0","message":str(e)})


class AddItemGroupApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_item_group = request.data.get('strItemGroup')
            if ItemGroup.objects.filter(int_status=1,vchr_item_group = str_item_group).exists():
                return Response({'status':'0','message':'Group Already Exists'})
            ins_item_group = ItemGroup(
                vchr_item_group = str_item_group.upper(),
                int_status = 1,
                fk_created_id = request.user.id,
                dat_created = datetime.datetime.now(),
                fk_updated_id = request.user.id,
                dat_updated = datetime.datetime.now()
            )
            ins_item_group.save()
            return Response({'status':'1'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({"status":"0","message":str(e)})
    def get(self,request):
        try:
            lst_group = []
            int_group_id = request.GET.get('intGroupId')
            if int_group_id:
                lst_group = list(ItemGroup.objects.filter(pk_bint_id=int_group_id).values('pk_bint_id','vchr_item_group'))
            else:
                lst_group = list(ItemGroup.objects.filter(int_status=1).values('pk_bint_id','vchr_item_group'))
            return Response({'status':'1','lst_group':lst_group})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({"status":"0","message":str(e)})
    def put(self,request):
        try:
            int_group_id = request.data.get('intGroupId')
            ItemGroup.objects.filter(pk_bint_id=int_group_id).update(int_status=-1,fk_updated_id = request.user.id,dat_updated=datetime.datetime.now())
            return Response({'status':'1'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'0','message':str(e)})
    def patch(self,request):
        try:
            int_group_id = request.data.get('intGroupId')
            str_item_group = request.data.get('strItemGroup').upper()
            if ItemGroup.objects.filter(int_status=1,vchr_item_group = str_item_group).exclude(pk_bint_id=int_group_id).exists():
                return Response({'status':'0','message':'Group Already Exists'})
            ItemGroup.objects.filter(pk_bint_id=int_group_id).update(vchr_item_group = str_item_group,fk_updated_id = request.user.id,dat_updated=datetime.datetime.now())
            return Response({'status':'1'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'status':'0','message':str(e)})

class ItemGroupTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data['term']
            # 
            lst_item_group = []
            if str_search_term != -1:
                ins_item_group = ItemGroup.objects.filter(vchr_item_group__icontains=str_search_term,int_status=1).values('pk_bint_id','vchr_item_group').distinct()
                for itr_item in ins_item_group:
                    dct_item_group = {}
                    dct_item_group['name'] = itr_item['vchr_item_group']
                    dct_item_group['id'] = itr_item['pk_bint_id']
                    lst_item_group.append(dct_item_group)
                return Response({'status':'success','data':lst_item_group})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})





class getStock(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # 
            int_qty = request.data.get("int_qty",1)
            str_branch_code = request.data.get("str_branch_code",request.user.userdetails.fk_branch.vchr_code)
            str_item_code = request.data.get("vchrItemCode")

            # if not request.data.get("str_branch_code"):
            #     str_branch_code = request.user.userdetails.fk_branch_id


            dct_param={"int_qty":int_qty,"str_branch_code":str_branch_code,"str_item_code":str_item_code}

            url = settings.POS_HOSTNAME + "/enquiry/get_stock/"
            res_data=requests.post(url,json=dct_param)
            if res_data.status_code == 200:
                json_resd=res_data.json()

                return Response({'status':'success','data':json_resd['data']})
            return Response({'status':'empty','data':[]})


        except Exception as e:
            ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'user': 'user_id:' + str(request.user.id)})
            return Response({"status":"0","message":str(e)})


class NearByStockCheck(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            int_branch_id = request.data.get("intBranchId",request.user.userdetails.fk_branch_id)
            str_item_code = request.data.get("vchrItemCode")
            if not int_branch_id:
                str_branch_code = request.user.userdetails.fk_branch.vchr_code
            else:
                str_branch_code = Branch.objects.filter(pk_bint_id = int_branch_id).values('vchr_code').first()['vchr_code']

            dct_param={"str_branch_code":str_branch_code,"str_item_code":str_item_code}

            url = settings.POS_HOSTNAME + "/enquiry/stock_nearby_branchs/"
            res_data=requests.post(url,json=dct_param)

            if res_data.status_code == 200:
                json_read=res_data.json()
                if json_read and json_read['status'] == 1:
                    lst_branch = json_read['data']

                    lst_branch_id = Branch.objects.filter(vchr_code__in = lst_branch).values_list('pk_bint_id',flat = True)

                    return Response({'status':"1",'data':lst_branch_id})
                else:
                    return Response({'status':'empty','data':"no branchs available"})

            return Response({'status':'empty','data':"some error in pos"})


        except Exception as e:
            ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'user': 'user_id:' + str(request.user.id)})
            return Response({"status":"0","message":str(e)})


class ItemAgingCheck(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # int_branch_id = request.data.get("intBranchId",request.user.userdetails.fk_branch_id)
            str_item_code = request.data.get("vchrItemCode")
            str_imei = request.data.get("vchrImei")
            #if not int_branch_id:
            str_branch_code = request.user.userdetails.fk_branch.vchr_code
            # 
            #else:
                #str_branch_code = Branch.objects.filter(pk_bint_id = str_branch_id).values('vchr_code').first()['vchr_code']


            dct_param={"str_branch_code":str_branch_code,"str_item_code":str_item_code,"str_imei":str_imei}

            url = settings.POS_HOSTNAME + "/enquiry/item_aging_check/"
            res_data=requests.post(url,json=dct_param)

            if res_data.status_code == 200:
                json_read=res_data.json()
                if json_read and json_read['status'] == 1:
                    lst_imei = json_read['data']

                    return Response({'status':1,'data':lst_imei})

                elif json_read and json_read['status'] == 0:
                    return Response({'status':0,'data':"no aged batch number found"})
                else:
                    return Response({'status':-1,'data':"no item found with cooresponding batch number"})

            return Response({'status':'failed','data':"some error in pos"})

        except Exception as e:
            ins_logger.logger.error(e, extra={'details':traceback.format_exc(),'user': 'user_id:' + str(request.user.id)})
            return Response({"status":"0","message":str(e)})

class ItemTypeahead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            str_search_term = request.data['term']
            lst_brand = request.data.get('brand') or []
            lst_product = request.data.get('product') or []
            lst_item = []
            if str_search_term != -1:
                if lst_brand  and lst_product:
                    ins_item_group = Items.objects.filter(Q(fk_brand_id__in = lst_brand),Q(fk_product_id__in = lst_product),Q(Q(vchr_name__icontains=str_search_term)|Q(vchr_item_code__icontains=str_search_term))).values('id','vchr_item_code','vchr_name').distinct()
                elif lst_brand:
                    ins_item_group = Items.objects.filter(Q(fk_brand_id__in = lst_brand),Q(Q(vchr_name__icontains=str_search_term)|Q(vchr_item_code__icontains=str_search_term))).values('id','vchr_item_code','vchr_name').distinct()
                elif lst_product:
                    ins_item_group = Items.objects.filter(Q(fk_product_id__in = lst_product),Q(Q(vchr_name__icontains=str_search_term)|Q(vchr_item_code__icontains=str_search_term))).values('id','vchr_item_code','vchr_name').distinct()
                else:
                    ins_item_group = Items.objects.filter(Q(Q(vchr_name__icontains=str_search_term)|Q(vchr_item_code__icontains=str_search_term))).values('id','vchr_item_code','vchr_name').distinct()

                for itr_item in ins_item_group:
                    dct_item = {}
                    dct_item['name'] = itr_item['vchr_item_code'] +' - '+ itr_item['vchr_name']
                    dct_item['id'] = itr_item['id']
                    lst_item.append(dct_item)
                return Response({'status':'success','data':lst_item})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})



class ProductSpecAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            # dat_from = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days = 1),'%Y-%m-%d %H:%M:%S')
            lst_specifications_keys = []
            # url = 'http://myglive.tmicloud.net:8084/api/master/Item'
            # PARAMS = {'FDate':dat_from}
            # res_data=requests.get(url=url,params=PARAMS)
            # if res_data.status_code == 200:
            #     str_data = res_data.json()
            #     if str_data:
            #         dct_data = str_data
            #         if dct_data:
            #             lst_all_keys = dct_data[0].keys()
            #             lst_known_keys = ['BrandName','ProductName','ITEMTYPE','BatchNum','SERIALNO','Status','ProductCategory','ItemCategory', 'Image Path','U_MODELNO1','U_MODELNO','U_SARRATE','U_TYPE','validFor', 'U_SUPPLIERS', 'U_ITEMTYPE','SerialNum','U_BRAND','ItemName','U_PRODUCTCATEGORY','HsnCode', 'ItemCode', 'U_ITEMCATEGORY', 'U_CATEGORY', 'U_GST','ItmsGrpNam']
            #             lst_unknown_keys = ['InvntryUom','BuyUnitMsr','SalUnitMsr']
            #             lst_specifications_keys = list(set(lst_all_keys) - set(lst_known_keys) - set(lst_unknown_keys))
            #             # lst_specifications_keys=[data.split("U_")[1].upper() for data in lst_specifications_keys if "U_" in data]
            #             lst_specifications_keys = [data.split('U_')[1].upper() if 'U_' in data else data.upper() for data in lst_specifications_keys]

            # if not lst_specifications_keys:
            lst_specifications_keys = ['BATTERY', 'RAM', 'WIFI', 'STEC_RMS', 'SARRATE', 'DISPLAY', 'BINLOCATION', 'BLUETOOTH', 'OS', 'FACEDETECTION', 'WATERRESISTANT', 'NFC', 'USB', 'SCREENTYPE', 'SIM', 'GPS', 'STARRATING', 'FRONTCAMERA', 'SLRVARIENT', 'HDMI', 'FLASH', 'FRONTCAMERAPIXEL', 'QUALITY', 'EXTERNALSTORAGE', 'WEIGHT', 'SCREENSIZE', 'BATTERY', 'REARCAMERA', 'REARCAMERAPIXEL', 'MATERIAL', 'PROCESSOR', 'DVDDRIVE', 'GRAPHICSCARD', 'OTG', 'ITEMCOLOR', 'IRISSCANNER', 'FINGERPRINT', 'GENERATION', 'INTERNALSTORAGE', 'SCANNER', 'NETWORK']

            lst_specifications_keys_new = []
            for ins_spec in lst_specifications_keys:
                dct_spec = {}
                dct_spec['name'] = ins_spec
                lst_specifications_keys_new.append(dct_spec)


            # 
            rst_item_category = ItemCategory.objects.filter(int_status = 1).values('pk_bint_id','vchr_category','json_specs')

            lst_data = []
            for ins_data in rst_item_category:
              dct_data = {}
              dct_data['id'] = ins_data['pk_bint_id']
              dct_data['name'] = ins_data['vchr_category']
              dct_data['lst_selected_specs'] = []
              if type(ins_data['json_specs']) == str:
                  lst_specs = json.loads(ins_data['json_specs'])
              else:
                  lst_specs = ins_data['json_specs']
              for ins_spec in lst_specs:
                  dct_spec = {}
                  dct_spec['name'] = ins_spec
                  dct_data['lst_selected_specs'].append(dct_spec)
              dct_data['lst_specs'] = lst_specifications_keys_new
              lst_data.append(dct_data)

            return Response({'status':'success','data':lst_data})

        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})

    def post(self,request):
        try:
            # 
            dct_data = request.data.get('dctData')
            lst_category_id = dct_data['lst_category_id']
            if not lst_category_id:
                return Response({'result':'failed','reason':'not data'})

            rst_item_category = ItemCategory.objects.filter(pk_bint_id__in = lst_category_id)

            for ins_data in rst_item_category:
                lst_selected_keys = dct_data[str(ins_data.vchr_category).upper()]['lst_selected_keys']
                lst_selected_keys_new = [d['name'] for d in lst_selected_keys]
                ins_data.json_specs = json.dumps(lst_selected_keys_new)

            bulk_update(rst_item_category)

            return Response({'status':'success'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})
