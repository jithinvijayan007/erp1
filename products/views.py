from django.shortcuts import render
from django.views import generic
from rest_framework import generics
from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from rest_framework.response import Response
from products.models import Products,Specifications
from category.models import Category
from django.views.generic import View,TemplateView,CreateView
from rest_framework.views import APIView
from django.db.models import Q
# Create your views here.
from POS import ins_logger
import sys, os
from datetime import datetime

class AddProduct(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            """add products"""
            # import pdb; pdb.set_trace()
            vchr_name = request.data.get('vchr_name')
            fk_category_id = request.data.get('fk_category_id')
            # bln_sales = request.data.get('bln_sales')
            json_sales = request.data.get('json_sales')
            if not json_sales:
                json_sales = 0
            elif "Sales" in json_sales and len(json_sales) == 1:
                json_sales = 1
            elif "Service" in json_sales and len(json_sales) == 1:
                json_sales = 2
            else:
                json_sales = 3
            #validation if product already exists
            ins_product_name = list(Products.objects.values('pk_bint_id','vchr_name').filter(vchr_name = vchr_name))
            if ins_product_name:
                    return Response({'status':0 , 'reason' : "product already exists"})

            ins_product_add = Products.objects.create(vchr_name = vchr_name,fk_category_id =  fk_category_id, int_sales = json_sales,fk_created_id=request.user.id,dat_created = datetime.now())

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def get(self,request):
        try:
            """list products"""
            # import pdb; pdb.set_trace()
            product_id = request.GET.get('product_id')
            #update
            if product_id:
                ins_product_list = list(Products.objects.values('pk_bint_id','vchr_name','fk_category_id','fk_category__vchr_name','int_sales').filter(pk_bint_id = product_id))
                # for ins_product in ins_product_list:
                #     dct_product[ins_product['pk_bint_id']]={}
                #     dct_product[ins_product['pk_bint_id']]['vchr_name']=ins_product['vchr_name']
                #     dct_product[ins_product['pk_bint_id']]['fk_category_id']=ins_product['fk_category_id']
                #     dct_product[ins_product['pk_bint_id']]['fk_category__vchr_name']=ins_product['fk_category__vchr_name']
                #     dct_product[ins_product['pk_bint_id']]['vchr_hsn_code']=ins_product['vchr_hsn_code']
                #     if ins_product['bln_sales'] == True:
                #         dct_product[ins_product['pk_bint_id']]['bln_sales']="SALES"
                #     else:
                #         dct_product[ins_product['pk_bint_id']]['bln_sales']="SERVICE"
                for ins_product in ins_product_list:
                    json_sales =[]
                    ins_product.update({'json_sales':json_sales})
                    if ins_product['int_sales'] == 0:
                        ins_product['json_sales'] = None
                    elif ins_product['int_sales'] == 1:
                        ins_product['json_sales'].append("Sales")
                    elif ins_product['int_sales'] == 2 :
                        ins_product['json_sales'].append("Service")
                    else:
                        ins_product['json_sales'].append("Sales")
                        ins_product['json_sales'].append("Service")

                return Response({'status':1 ,'data' : ins_product_list})
            #listing
            ins_product_list = list(Products.objects.values('pk_bint_id','vchr_name','fk_category_id','fk_category__vchr_name','int_sales','dat_created').filter(int_status = 0).order_by('-pk_bint_id'))
            # for ins_product in ins_product_list:
                # dct_product[ins_product['pk_bint_id']]={}
                # dct_product[ins_product['pk_bint_id']]['vchr_name']=ins_product['vchr_name']
                # dct_product[ins_product['pk_bint_id']]['fk_category_id']=ins_product['fk_category_id']
                # dct_product[ins_product['pk_bint_id']]['fk_category__vchr_name']=ins_product['fk_category__vchr_name']
                # dct_product[ins_product['pk_bint_id']]['vchr_hsn_code']=ins_product['vchr_hsn_code']
                # dct_product[ins_product['pk_bint_id']]['dat_created']=ins_product['dat_created']
                # if ins_product['bln_sales'] == True:
                #     dct_product[ins_product['pk_bint_id']]['bln_sales']="SALES"
                # else:
                #     dct_product[ins_product['pk_bint_id']]['bln_sales']="SERVICE"

            for ins_product in ins_product_list:
                json_sales =[]
                ins_product.update({'json_sales':json_sales})
                if ins_product['int_sales'] == 0:
                    ins_product['json_sales'] = None
                elif ins_product['int_sales'] == 1:
                    ins_product['json_sales'].append("Sales")
                elif ins_product['int_sales'] == 2 :
                    ins_product['json_sales'].append("Service")
                else:
                    ins_product['json_sales'].append("Sales")
                    ins_product['json_sales'].append("Service")

            return Response({'status':1 , 'data' : ins_product_list})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def put(self,request):
        try:
            """update products"""
            #update
            # import pdb; pdb.set_trace()
            product_id = request.data.get('product_id')
            vchr_name = request.data.get('vchr_name')
            fk_category_id = request.data.get('fk_category_id')
            # bln_sales = request.data.get('bln_sales')
            json_sales = request.data.get('json_sales')
            if not json_sales:
                json_sales = 0
            elif "Sales" in json_sales and len(json_sales) == 1:
                json_sales = 1
            elif "Service" in json_sales and len(json_sales) == 1:
                json_sales = 2
            else:
                json_sales = 3
            #validation if product already exists
            ins_product_name = list(Products.objects.values('pk_bint_id','vchr_name').filter(vchr_name = vchr_name,int_status = 0).exclude(pk_bint_id = product_id))
            if ins_product_name:
                    return Response({'status':0 , 'reason' : "product already exists"})

            ins_product_update = Products.objects.filter(pk_bint_id = product_id).update(vchr_name = vchr_name,fk_category_id =  fk_category_id,int_sales = json_sales, fk_updated_id = request.user.id)
            return Response({'status':1 })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def patch(self,request):
        try:
            """delete produts"""

            product_id = request.data.get('pk_bint_id')
            ins_product_update = Products.objects.filter(pk_bint_id = product_id).update(int_status = -1)
            return Response({'status':1 })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class GetCategoryData(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            # ins_specification = list(Specifications.objects.values('pk_bint_id','vchr_name'))
            ins_category = list(Category.objects.values('pk_bint_id','vchr_name').filter(int_status = 0))
            return Response({'status':1 , 'category' : ins_category})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


class ProductTypeHead(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            dct_product = Products.objects.filter(int_status = 0).values('pk_bint_id','vchr_name')
            return Response({'status':1,'data':dct_product})
        except Exception as e:
            return Response({'status':0,'reason':e})
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            lst_products = []
            if str_search_term != -1:
                ins_product = Products.objects.filter(Q(int_status = 0),Q(vchr_name__icontains=str_search_term)).values('pk_bint_id','vchr_name','int_sales')
                if ins_product:
                    for itr_item in ins_product:
                        dct_product = {}
                        dct_product['name'] = itr_item['vchr_name']
                        dct_product['id'] = itr_item['pk_bint_id']
                        dct_product['int_sales'] = itr_item['int_sales']
                        lst_products.append(dct_product)
                return Response({'status':1,'data':lst_products})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})
