from django.shortcuts import render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

from brands.models import Brands
from products.models import Products
from item_category.models import Item as Items
from inventory.models import ItemDetails

from userdetails.models import UserDetails as UserModel
from stock_app.models import Stockdetails
from POS import settings
import requests
import json

# Create your views here.
class MobileItemsTypeahed(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            q = request.data['query']
            itemType = request.data['itemType']
            typeahed = request.data['typeahed']
            brand = request.data['brand']
            int_company = UserModel.objects.get(id = request.user.id).fk_company
            if typeahed == 'brand':
                lst_results = list(Items.objects.filter(fk_brand__vchr_brand_name__icontains = q, fk_product__fk_company = int_company, fk_product__vchr_product_name__iexact=itemType).values('fk_brand','fk_brand__vchr_brand_name').order_by('fk_brand__vchr_brand_name').distinct() )[:50]
                for d in lst_results:
                    d['name']=d['fk_brand__vchr_brand_name']
                    d['id'] = d['fk_brand']


            if typeahed == 'item':
                if int(brand) != 0:
                    lst_results = list(Items.objects.filter(Q(Q(vchr_item_name__icontains = q) | Q(vchr_item_code__icontains = q)),fk_brand=int(brand), fk_product__fk_company = int_company, fk_product__vchr_product_name__iexact=itemType).values('id','vchr_item_name','vchr_item_code','fk_brand').order_by('vchr_item_name') )[:50]
                else:
                    lst_results = list(Items.objects.filter(Q(Q(vchr_item_name__icontains = q) | Q(vchr_item_code__icontains = q)), fk_product__fk_company = int_company, fk_product__vchr_product_name__iexact=itemType).values('id','vchr_item_name','vchr_item_code','fk_brand').order_by('vchr_item_name') )[:50]
                for d in lst_results:
                    d['name']=d['vchr_item_name']+' - '+d['vchr_item_code']
                    lst_details = ItemDetails.objects.filter(fk_item_id = d['id']).values('json_spec','vchr_item_img')
                    if lst_details:
                        dct_details=lst_details.first()
                        d['spec'] = dct_details['json_spec']
                        d['img'] = dct_details['vchr_item_img']
                    lst_order = Products.objects.filter(vchr_product_name__iexact=itemType).values('dct_product_spec','vchr_product_img')
                    if lst_order:
                        dct_details = lst_order.first()
                        d['order'] = dct_details['dct_product_spec'].keys()
                        if not d.get('img'):
                            d['img'] = dct_details['vchr_product_img']
                    if 'spec' not in d:
                        d['spec'] = {}
                    d['img'] = settings.HOSTNAME+'/media/' + d['img']
            return Response(lst_results)
        except Exception as e:
            print(e)
            return Response({'status':'1'})
class MobileItemsWithBrandTypeahed(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            q = request.data['query']
            itemType = request.data['itemType']
            typeahed = request.data['typeahed']
            int_company = UserModel.objects.get(id = request.user.id).fk_company
            # if typeahed == 'brand':
            #     lst_results = list(Items.objects.filter(fk_brand__vchr_brand_name__icontains = q, fk_product__fk_company = int_company, fk_product__vchr_product_name__iexact=itemType).values('fk_brand','fk_brand__vchr_brand_name').order_by('fk_brand__vchr_brand_name').distinct() )[:50]
            #     for d in lst_results:
            #         d['name']=d['fk_brand__vchr_brand_name']
            #         d['id'] = d['fk_brand']


            if typeahed == 'item':
                # if int(brand) != 0:
                #     lst_results = list(Items.objects.filter(Q(Q(vchr_item_name__icontains = q) | Q(vchr_item_code__icontains = q)),fk_brand=int(brand), fk_product__fk_company = int_company, fk_product__vchr_product_name__iexact=itemType).values('id','vchr_item_name','vchr_item_code','fk_brand__vchr_brand_name').order_by('vchr_item_name') )[:50]
                # else:
                lst_results = list(Items.objects.filter(Q(Q(vchr_item_name__icontains = q) | Q(vchr_item_code__icontains = q)), fk_product__fk_company = int_company, fk_product__vchr_product_name__iexact=itemType).values('id','vchr_item_name','vchr_item_code','fk_brand','fk_brand__vchr_brand_name').order_by('vchr_item_name') )[:50]
                for d in lst_results:
                    d['name']=d['vchr_item_name']+' - '+d['vchr_item_code']
                    lst_details = ItemDetails.objects.filter(fk_item_id = d['id']).values('json_spec','vchr_item_img')
                    if lst_details:
                        dct_details=lst_details.first()
                        d['spec'] = dct_details['json_spec']
                        d['img'] = dct_details['vchr_item_img']
                    lst_order = Products.objects.filter(vchr_product_name__iexact=itemType).values('dct_product_spec','vchr_product_img')
                    if lst_order:
                        dct_details = lst_order.first()
                        d['order'] = dct_details['dct_product_spec'].keys()
                        if not d.get('img'):
                            d['img'] = dct_details['vchr_product_img']
                    if 'spec' not in d:
                        d['spec'] = {}
                    d['img'] = settings.HOSTNAME+'/media/' + d['img']
            return Response(lst_results)
        except Exception as e:
            return Response({'status':'1'})
class itemBySub(APIView):
    def post(self,request,):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data['term']
            str_brand = request.data['brandId']
            str_product = request.data['product']
            lst_subcategory = []
            lst_branch = list(UserModel.objects.filter(id=request.user.id).values('fk_branch','fk_branch__fk_territory'))
            int_branch_id = lst_branch[0]['fk_branch']
            int_territory_id = lst_branch[0]['fk_branch__fk_territory']
            if str_search_term != -1:
                ins_subcategory = Items.objects.filter(vchr_item_name__iexact=str_search_term['vchr_item_name'], fk_brand = str_brand , fk_product__vchr_product_name__iexact = str_product ).values('id','vchr_item_name')
                for itr_item in ins_subcategory:
                    dct_subcategory = {}
                    dct_subcategory['name'] = itr_item['vchr_item_name']
                    dct_subcategory['id'] = itr_item['id']
                    lst_stock = list(Stockdetails.objects.filter(fk_item_id = itr_item['id'],fk_stock_master__fk_branch =int_branch_id).values('dbl_min_selling_price','dbl_max_selling_price','int_available').order_by('-int_available'))
                    # import pdb; pdb.set_trace()
                    if lst_stock:
                        dct_subcategory['stock'] = lst_stock[0]
                    else:
                        lst_stock_in = list(Stockdetails.objects.filter(fk_item_id = itr_item['id'],fk_stock_master__fk_branch__fk_territory =int_territory_id).values('dbl_min_selling_price','dbl_max_selling_price','int_qty','fk_stock_master__fk_branch__vchr_name'))
                        dct_subcategory['stockInOthrBranch']=[]
                        for dct_item in lst_stock_in:
                            dct_temp = {}
                            dct_temp['branch'] = dct_item['fk_stock_master__fk_branch__vchr_name']
                            dct_temp['int_qty'] = dct_item['int_qty']

                            dct_subcategory['stockInOthrBranch'].append(dct_temp)

                    # ins_details = ProductDetails.objects.filter(fk_item_id = itr_item['id']).values_list('json_spec','vchr_item_img')
                    # if lst_details:
                    #     dct_details=ins_details.first()._asdict()
                    #     dct_subcategory['spec'] = dct_details['json_spec']
                    #     dct_subcategory['img'] = dct_details['vchr_item_img']
                    # ins_product=Products.objects.filter(vchr_product_name = str_product).values('vchr_order','vchr_product_img')
                    # if lst_order:
                    #     dct_product=ins_product._asdict()
                    #     dct_subcategory['order'] = dct_product['vchr_order']
                    #     if not dct_subcategory['img']:
                    #         dct_subcategory['img'] = dct_product['vchr_product_img']
                    # lst_subcategory.append(dct_subcategory)
                return Response({'status':'success','data':lst_subcategory})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            return Response({'result':'failed','reason':e})




class barcodeScan(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,):
        try:
            vchr_barcode = request.data['BARCODE'];
            vchr_product = request.data['PRODUCT'];
            flt_amount = 0
            if vchr_product == 'OTHERS':
                ins_item_details = list(Items.objects.filter(vchr_barcode = vchr_barcode, fk_product__bln_visible = False)\
                .values('dbl_apx_amount','id','vchr_item_name','vchr_item_code','fk_brand','fk_brand__vchr_brand_name','fk_product__vchr_product_img','fk_product__dct_product_spec','fk_product__vchr_product_name','fk_product__id'))
                if ins_item_details:
                    dbl_apx_amount = Items.objects.filter(vchr_barcode = vchr_barcode, fk_product__vchr_product_name__iexact = vchr_product).values('dbl_apx_amount')[0]['dbl_apx_amount']
                else:
                    return Response({'status':'failed','reason':'Item not found'})
            elif vchr_product == 'ALL':
                ins_item_details = list(Items.objects.filter(vchr_barcode = vchr_barcode)\
                .values('dbl_apx_amount','fk_product__bln_visible','id','vchr_item_name','vchr_item_code','fk_brand','fk_brand__vchr_brand_name','fk_product__vchr_product_img','fk_product__dct_product_spec','fk_product__vchr_product_name','fk_product__id'))
                if ins_item_details:
                    dbl_apx_amount = Items.objects.filter(vchr_barcode = vchr_barcode).values('dbl_apx_amount')[0]['dbl_apx_amount']
                else:
                    return Response({'status':'failed','reason':'Item not found'})
            else:
                ins_item_details = list(Items.objects.filter(vchr_barcode = vchr_barcode, fk_product__vchr_product_name__iexact = vchr_product)\
                .values('dbl_apx_amount','id','vchr_item_name','vchr_item_code','fk_brand','fk_brand__vchr_brand_name','fk_product__vchr_product_img','fk_product__dct_product_spec'))
                if ins_item_details:
                    dbl_apx_amount = Items.objects.filter(vchr_barcode = vchr_barcode, fk_product__vchr_product_name__iexact = vchr_product).values('dbl_apx_amount')[0]['dbl_apx_amount']
                else:
                    return Response({'status':'failed','reason':'Item not found'})
            if dbl_apx_amount:
                return Response({'status':'success','data':ins_item_details ,'item_amount':dbl_apx_amount})
            flt_amount = ins_item_details[0]['dbl_apx_amount']
            try:
                if not flt_amount:
                  url = 'http://devserv1.gdpplus.in/Item_Model_Selling_Price.aspx'
                  params = {'model':ins_item_details[0]['vchr_item_code']}
                  # params = {'model':'0'}
                  # len(data.split('\\')[0])
                  r = requests.get(url, params=params)
                  if r.status_code == 200:
                      data = json.dumps(r.text)
                      if data.split('\\')[0] != '"[]':
                          flt_amount = float(data.split('\\')[6].split(':')[1].split('}')[0])
                          Items.objects.filter(vchr_barcode = vchr_barcode).update(dbl_apx_amount = flt_amount)
            except Exception as e:
               flt_amount = 0
            int_selected_item =  ins_item_details[0]['id']
            lst_product_details = list(ItemDetails.objects.filter(fk_item_id = int_selected_item).values('json_spec','vchr_item_img'))
            if lst_product_details:
                ins_item_details[0]['spec'] = lst_product_details[0]['json_spec']
            if ins_item_details[0]['fk_product__dct_product_spec']:
                ins_item_details[0]['order'] = ins_item_details[0]['fk_product__dct_product_spec'].keys()
            if  ins_item_details[0].get('fk_product__vchr_product_img'):
                ins_item_details[0]['img'] = ins_item_details[0]['fk_product__vchr_product_img']
            else:
                # ins_item_details[0]['img'] = ins_item_details[0]['img']['vchr_item_img']
                ins_item_details[0]['img'] = ''
            if 'spec' not in ins_item_details[0]:
                ins_item_details[0]['spec'] = {}
            ins_item_details[0]['img'] = settings.HOSTNAME+'/static/media/' + ins_item_details[0]['img']
            return Response({'status':'success','data':ins_item_details ,'item_amount':flt_amount})

        except Exception as e:
            return Response({'status':'failed','reason':e})
