
from django.shortcuts import render
from django.views import generic
from rest_framework import generics
from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from rest_framework.response import Response
from item_category.models import ItemCategory,TaxMaster,Item
from products.models import Specifications,Products
from item_group.models import ItemGroup
from django.views.generic import View,TemplateView,CreateView
from rest_framework.views import APIView
from django.db.models import Value, CharField, BooleanField, Case, When , IntegerField ,FloatField
from django.db.models import Q
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import json
import requests
from PIL import Image
# Create your views here.
from POS import ins_logger
import sys, os
from userdetails.models import UserDetails as Userdetails
from brands.models import Brands
from category.models import Category
from dateutil.relativedelta import relativedelta
from datetime import timedelta,datetime
from django.db.models import F


class ItemCategoryAdd(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            vchr_item_category = request.data.get('strName')
            vchr_hsn_code = request.data.get('vchr_hsn_code')
            vchr_sac_code = request.data.get('vchr_sac_code')
            json_tax_master = request.data.get('lstTax')
            json_specification_id = request.data.get('lstSpec')
            dct_tax_master={}
            for ins_tax in json_tax_master:
                dct_tax_master[list(ins_tax.keys())[0]] = ins_tax[list(ins_tax.keys())[0]]
            ins_item_duplicate = list(ItemCategory.objects.filter(vchr_item_category = vchr_item_category).values('pk_bint_id'))
            if ins_item_duplicate:
                return Response({'status':0 , 'data' : 'item category already exists'})
            ins_item_add = ItemCategory.objects.create(vchr_item_category = vchr_item_category,vchr_hsn_code=vchr_hsn_code,vchr_sac_code=vchr_sac_code,json_tax_master = dct_tax_master,json_specification_id = json_specification_id, fk_created_id=request.user.id,dat_created = datetime.now(),fk_company_id =1)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def get(self,request):
        try:
            #listing
            # import pdb; pdb.set_trace()

            int_id = request.GET.get('pk_bint_id')
            if int_id:
                ins_item_list = list(ItemCategory.objects.filter(pk_bint_id = int(int_id)).values('pk_bint_id','vchr_item_category','vchr_hsn_code','vchr_sac_code','json_tax_master','json_specification_id'))

                dct_item_details = {}

                spec_name = dict(Specifications.objects.values_list('pk_bint_id','vchr_name'))
                tax_name = dict(TaxMaster.objects.values_list('pk_bint_id','vchr_name'))


                for ins_item in ins_item_list:
                    dct_item_details[ins_item['pk_bint_id']] ={}
                    dct_item_details[ins_item['pk_bint_id']]['vchr_item_category'] = ins_item['vchr_item_category']
                    dct_item_details[ins_item['pk_bint_id']]['vchr_hsn_code'] = ins_item['vchr_hsn_code']
                    dct_item_details[ins_item['pk_bint_id']]['vchr_sac_code'] = ins_item['vchr_sac_code']
                    dct_item_details[ins_item['pk_bint_id']]['tax_master'] = {}
                    dct_item_details[ins_item['pk_bint_id']]['specification'] = {}
                    for ins_spec in ins_item['json_specification_id']:
                        dct_item_details[ins_item['pk_bint_id']]['specification'][ins_spec]=spec_name[ins_spec]
                    for ins_tax in ins_item['json_tax_master']:
                        dct_item_details[ins_item['pk_bint_id']]['tax_master'][ins_tax] = {}
                        dct_item_details[ins_item['pk_bint_id']]['tax_master'][ins_tax][tax_name[int(ins_tax)]] = ins_item['json_tax_master'][ins_tax]

                ins_specification = list(Specifications.objects.values('pk_bint_id','vchr_name'))
                ins_tax = list(TaxMaster.objects.values('pk_bint_id','vchr_name'))


                return Response({'status':1 , 'data' : dct_item_details,'ins_specification' : ins_specification , 'ins_tax' : ins_tax })

            else:
                ins_item_list = list(ItemCategory.objects.filter(int_status = 0).values('pk_bint_id','vchr_item_category','vchr_hsn_code','vchr_sac_code','json_tax_master','json_specification_id','dat_created').order_by('-pk_bint_id'))
                dct_item_details = {}

                spec_name = dict(Specifications.objects.values_list('pk_bint_id','vchr_name'))
                tax_name = dict(TaxMaster.objects.values_list('pk_bint_id','vchr_name'))


                for ins_item in ins_item_list:
                    dct_item_details[ins_item['pk_bint_id']] ={}
                    dct_item_details[ins_item['pk_bint_id']]['vchr_item_category'] = ins_item['vchr_item_category']
                    dct_item_details[ins_item['pk_bint_id']]['vchr_hsn_code'] = ins_item['vchr_hsn_code']
                    dct_item_details[ins_item['pk_bint_id']]['vchr_sac_code'] = ins_item['vchr_sac_code']
                    dct_item_details[ins_item['pk_bint_id']]['dat_created'] = datetime.strftime(ins_item['dat_created'],'%d-%m-%Y')
                    dct_item_details[ins_item['pk_bint_id']]['tax_master'] = {}
                    dct_item_details[ins_item['pk_bint_id']]['specification'] = []
                    # for ins_spec in ins_item['json_specification_id']:
                    #     dct_item_details[ins_item['pk_bint_id']]['specification'].append(spec_name[ins_spec])
                    for ins_tax in ins_item['json_tax_master']:
                        dct_item_details[ins_item['pk_bint_id']]['tax_master'][tax_name[int(ins_tax)]] = ins_item['json_tax_master'][ins_tax]


                    ins_specification = list(Specifications.objects.values('pk_bint_id','vchr_name'))
                    ins_tax = list(TaxMaster.objects.values_list('vchr_name'))

                return Response({'status':1 , 'data' : dct_item_details, 'ins_specification' : ins_specification , 'ins_tax' : ins_tax  })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

    def put(self,request):
        try:
            #update
            int_id = request.data.get('pk_bint_id')
            vchr_item_category = request.data.get('strName')
            vchr_hsn_code = request.data.get('vchr_hsn_code')
            vchr_sac_code = request.data.get('vchr_sac_code')
            json_tax_master = request.data.get('lstTax')
            json_specification_id = request.data.get('lstSpec')
            dct_tax_master={}
            if json_tax_master:
                for ins_tax in json_tax_master:
                    dct_tax_master[list(ins_tax.keys())[0]] = ins_tax[list(ins_tax.keys())[0]]

            ins_item_duplicate = list(ItemCategory.objects.filter(vchr_item_category = vchr_item_category).values('pk_bint_id').exclude(pk_bint_id = int_id))

            if ins_item_duplicate:
                return Response({'status':0 , 'data' : 'item category already exists'})

            ins_item_add = ItemCategory.objects.filter(pk_bint_id = int_id).update(vchr_item_category = vchr_item_category,vchr_hsn_code=vchr_hsn_code,vchr_sac_code=vchr_sac_code,json_tax_master = dct_tax_master,json_specification_id = json_specification_id,fk_updated_id = request.user.id)
            # if json_tax_master and json_specification_id:
            #     ins_item_add = ItemCategory.objects.filter(pk_bint_id = int_id).update(vchr_item_category = vchr_item_category,json_tax_master = dct_tax_master,json_specification_id = json_specification_id,fk_updated_id = request.user.id)
            # elif json_tax_master:
            #     ins_item_add = ItemCategory.objects.filter(pk_bint_id = int_id).update(vchr_item_category = vchr_item_category,json_tax_master = dct_tax_master,fk_updated_id = request.user.id)
            # elif json_specification_id:
            #     ins_item_add = ItemCategory.objects.filter(pk_bint_id = int_id).update(vchr_item_category = vchr_item_category,json_specification_id = json_specification_id,fk_updated_id = request.user.id)
            # else:
            #     ins_item_add = ItemCategory.objects.filter(pk_bint_id = int_id).update(vchr_item_category = vchr_item_category,fk_updated_id = request.user.id)

            return Response({'status':1 })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})



    def patch(self,request):
        try:
            int_id = request.data.get('pk_bint_id')

            ins_item_update = ItemCategory.objects.filter(pk_bint_id = int_id).update(int_status = -1)

            return Response({'status':1 })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})



class GetTaxSpecification(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            # import pdb; pdb.set_trace()
            ins_specification = list(Specifications.objects.values('pk_bint_id','vchr_name'))
            ins_tax = list(TaxMaster.objects.values('pk_bint_id','vchr_name'))
            return Response({'status':1 , 'ins_specification' : ins_specification , 'ins_tax' : ins_tax})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})



class ItemAdd(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            item_name = request.data.get('vchr_item_name')
            bln_sales = request.data.get('bln_sales')
            product_id = request.data.get('product_id')
            brand_id = request.data.get('brand_id')
            vchr_item_code = request.data.get('vchr_item_code')
            item_category_id = request.data.get('item_category_id')
            item_group_id = request.data.get('item_group_id')
            dbl_supplier_cost = request.data.get('dbl_supplier_cost')
            dbl_dealer_cost = request.data.get('dbl_dealer_cost')
            dbl_mop = request.data.get('dbl_mop')
            dbl_mrp = request.data.get('dbl_mrp')
            int_reorder_level = request.data.get('int_reorder_level')
            json_specification_id = None if not request.data.get('int_specification_id') else json.loads(request.data.get('int_specification_id'))
            vchr_prefix = request.data.get('vchr_prefix')
            imei_status = request.data.get('imei_status')

            if request.data.get('user'):

                str_item_group= request.data.get("vchr_item_group")

                vchr_item_category = request.data.get('strName')
                vchr_hsn_code = request.data.get('vchr_hsn_code')
                vchr_sac_code = request.data.get('vchr_sac_code')
                json_tax_master = request.data.get('lstTax')
                json_specification_id = request.data.get('lstSpec')
                dct_tax_master={}
                if json_tax_master:
                    for ins_tax in json_tax_master:
                        dct_tax_master[list(ins_tax.keys())[0]] = ins_tax[list(ins_tax.keys())[0]]

                str_name = request.data.get('vchr_name')
                str_code = request.data.get('vchr_code')

                ins_user=Userdetails.objects.filter(username=request.data.get('user')).values('id').first()['id']
                if not str_item_group:
                    ins_item=ItemGroup.objects.filter(vchr_item_group="DEFAULT")
                    itemg_id=ins_item.values('pk_bint_id').first()['pk_bint_id']
                else:
                    ins_item=ItemGroup.objects.filter(vchr_item_group=str_item_group,int_status=1).values()
                    if ins_item:
                        itemg_id=ins_item.values('pk_bint_id').first()['pk_bint_id']

                    else:
                        ins_item=ItemGroup.objects.create(vchr_item_group=str_item_group,int_status=0,fk_created_id=ins_user,dat_created=datetime.now(),fk_category_id = 1)
                        itemg_id=ins_item.pk_bint_id
                if str_name or str_code:
                    ins_category = Category.objects.filter(Q(vchr_name=str_name) | Q(vchr_code=str_code),int_status=0)
                    if ins_category:
                        ins_category.update(vchr_name = str_name,vchr_code = str_code,fk_updated_id=ins_user,dat_updated=datetime.now(),int_status=1)
                    else:
                        ins_category = Category.objects.create(vchr_name = str_name,vchr_code = str_code,fk_created_id=ins_user,dat_created=datetime.now(),int_status=0)
                else:
                    ins_category = Category.objects.filter(Q(vchr_name="DEFAULT"),int_status=0)
                if vchr_item_category:

                    ins_item_duplicate = ItemCategory.objects.filter(vchr_item_category = vchr_item_category)
                    if ins_item_duplicate:
                            ins_item_duplicate.update(vchr_item_category = vchr_item_category,vchr_hsn_code=vchr_hsn_code,vchr_sac_code=vchr_sac_code,json_tax_master = dct_tax_master,json_specification_id = json_specification_id, fk_updated_id=ins_user)
                            itemic_id=ins_item_duplicate.values('pk_bint_id').first()['pk_bint_id']

                    else:
                        ins_item_duplicate = ItemCategory.objects.create(vchr_item_category = vchr_item_category,vchr_hsn_code=vchr_hsn_code,vchr_sac_code=vchr_sac_code,json_tax_master = dct_tax_master,json_specification_id = json_specification_id, fk_created_id=ins_user,dat_created = datetime.now())
                        itemic_id=ins_item_duplicate.pk_bint_id
                else:
                    ins_item_duplicate = ItemCategory.objects.filter(vchr_item_category = "DEFAULT")
                    itemic_id=ins_item_duplicate.values('pk_bint_id').first()['pk_bint_id']
                # import pdb;pdb.set_trace()

                if request.data.get('vchr_pname'):
                    ins_prod=Products.objects.filter(vchr_name=request.data.get('vchr_pname')).values()
                    if ins_prod:
                        int_prod_id=ins_prod.values('pk_bint_id').first()['pk_bint_id']

                    else:
                        ins_prod=Products.objects.create(vchr_name=request.data.get('vchr_pname'),fk_category_id=Category.objects.filter(vchr_name="DEFAULT").values('pk_bint_id').first()['pk_bint_id'],dat_created=datetime.now(),fk_created_id=ins_user)
                        int_prod_id=ins_prod.pk_bint_id
                if request.data.get('vchr_bname'):
                    ins_bra=Brands.objects.filter(vchr_name=request.data.get('vchr_bname')).values()
                    if ins_bra:
                        int_bra_id=ins_bra.values('pk_bint_id').first()['pk_bint_id']

                    else:
                        ins_bra=Brands.objects.create(vchr_name=request.data.get('vchr_bname'))
                        int_bra_id=ins_bra.pk_bint_id
                ins_duplicate = Item.objects.filter(vchr_item_code = vchr_item_code).values('pk_bint_id')
                if ins_duplicate:
                        ins_duplicate.update(int_status=0,vchr_name=item_name,fk_product_id=Products.objects.filter(vchr_name=request.data.get('vchr_pname')).values('pk_bint_id').first()['pk_bint_id'],fk_brand_id=Brands.objects.filter(vchr_name=request.data.get('vchr_bname')).values('pk_bint_id').first()['pk_bint_id'],\
                        vchr_item_code=vchr_item_code,fk_item_group_id=itemg_id,fk_item_category_id=itemic_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,fk_updated_id = ins_user)
                else:

                    ins_item_add = Item.objects.create(vchr_name=item_name,fk_product_id=int_prod_id,fk_brand_id=int_bra_id,vchr_item_code=vchr_item_code,\
                    fk_item_group_id=itemg_id,fk_item_category_id=itemic_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,\
                    dbl_mop=dbl_mop,fk_created_id = ins_user,dat_created = datetime.now(),json_specification_id={})
                return Response({'status':1})
            else:
                    if imei_status == 'true':
                        imei_status = True
                    else:
                        imei_status = False
                    if request.FILES.get('image1'):
                        my_file = request.FILES.get('image1')
                        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                        filename = fs.save(my_file.name, my_file)
                        image1 = fs.url(filename)

                        # to resize the image
                        if os.stat(settings.MEDIA_ROOT+'/'+filename):
                            basewidth = 300
                            img = Image.open(settings.MEDIA_ROOT+'/'+filename)
                            wpercent = (basewidth/float(img.size[0]))
                            hsize = int((float(img.size[1])*float(wpercent)))
                            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                            img.save(settings.MEDIA_ROOT+'/'+"img2"+filename)
                            image2 = fs.url("img2"+filename)

                            basewidth = 150
                            img = Image.open(settings.MEDIA_ROOT+'/'+filename)
                            wpercent = (basewidth/float(img.size[0]))
                            hsize = int((float(img.size[1])*float(wpercent)))
                            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                            img.save(settings.MEDIA_ROOT+'/'+"img3"+filename)
                            image3 = fs.url("img3"+filename)

                    if int(request.data.get('pk_bint_id')):
                        # update
                        # import pdb; pdb.set_trace()

                        ins_duplicate = list(Item.objects.filter(vchr_item_code = vchr_item_code).values('pk_bint_id').exclude(pk_bint_id= request.data.get('pk_bint_id')))
                        if ins_duplicate:
                            return Response({'status':0 , 'reason': "item code already exists"})
                        if request.FILES.get('image1'):
                            int_update = Item.objects.filter(pk_bint_id = request.data.get('pk_bint_id')).update(vchr_name=item_name,fk_product_id=product_id,fk_brand_id=brand_id,vchr_item_code=vchr_item_code,fk_item_category_id=item_category_id,fk_item_group_id=item_group_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,json_specification_id=json_specification_id,int_reorder_level=int_reorder_level,vchr_prefix=vchr_prefix,imei_status=imei_status,sale_status=bln_sales,fk_updated_id = request.user.id)
                            # int_update = Item.objects.filter(pk_bint_id = request.data.get('pk_bint_id')).update(vchr_name=item_name,fk_product_id=product_id,fk_brand_id=brand_id,vchr_item_code=vchr_item_code,fk_item_category_id=item_category_id,fk_item_group_id=item_group_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,json_specification_id=json_specification_id,int_reorder_level=int_reorder_level,vchr_prefix=vchr_prefix,imei_status=imei_status,sale_status=bln_sales,fk_updated_id = request.user.id,image1=image1,image2=image2,image3=image3)

                        else:
                            int_update = Item.objects.filter(pk_bint_id = request.data.get('pk_bint_id')).update(vchr_name=item_name,fk_product_id=product_id,fk_brand_id=brand_id,vchr_item_code=vchr_item_code,fk_item_category_id=item_category_id,fk_item_group_id=item_group_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,json_specification_id=json_specification_id,int_reorder_level=int_reorder_level,vchr_prefix=vchr_prefix,imei_status=imei_status,sale_status=bln_sales,fk_updated_id = request.user.id)
                        if int_update:
                            return Response({'status':1})
                        else:
                            return Response({'status':0,'reason':'Updation Failed'})

                    ins_duplicate = list(Item.objects.filter(vchr_item_code = vchr_item_code).values('pk_bint_id'))
                    if ins_duplicate:
                        return Response({'status':0 , 'reason': "item code already exists"})

                    # ins_item_add = Item.objects.create(vchr_name=item_name,fk_product_id=product_id,fk_brand_id=brand_id,vchr_item_code=vchr_item_code,fk_item_category_id=item_category_id,fk_item_group_id=item_group_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,json_specification_id=json_specification_id,int_reorder_level=int_reorder_level,vchr_prefix=vchr_prefix,imei_status=imei_status,sale_status=bln_sales,fk_created_id = request.user.id,image1=image1,image2=image2,image3=image3,dat_created = datetime.now())
                    ins_item_add = Item.objects.create(vchr_name=item_name,fk_product_id=product_id,fk_brand_id=brand_id,vchr_item_code=vchr_item_code,fk_item_category_id=item_category_id,fk_item_group_id=item_group_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,json_specification_id=json_specification_id,int_reorder_level=int_reorder_level,vchr_prefix=vchr_prefix,imei_status=imei_status,sale_status=bln_sales,fk_created_id = request.user.id,dat_created = datetime.now())

                    return Response({'status':1})
        except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                    return Response({'status':0})


    def get(self,request):
        try:

            int_id = request.GET.get('pk_bint_id')
            if int_id:
                ins_item_list = Item.objects.filter(pk_bint_id = int_id).values('pk_bint_id','fk_product_id','vchr_name','fk_product__vchr_name','fk_brand_id','fk_brand__vchr_name','vchr_item_code','fk_item_category_id','fk_item_category__vchr_item_category','fk_item_group_id','fk_item_group__vchr_item_group','dbl_supplier_cost','dbl_dealer_cost','dbl_mrp','dbl_mop','json_specification_id','int_reorder_level','vchr_prefix','imei_status','sale_status','image1').first()
                if ins_item_list['json_specification_id']:
                  spec_name = list(Specifications.objects.filter(pk_bint_id__in=ins_item_list['json_specification_id']).values_list('vchr_name',flat=True))
                  ins_item_list['spec_name'] = spec_name
                return Response({'status':1,'data':ins_item_list})
            # else:
            # #listing
            #     dat_from = request.data.get('')
            #     dat_to = request.data.get('')
            #     ins_item_list = list(Item.objects.values('pk_bint_id','fk_product_id','fk_product__vchr_name','fk_brand_id','fk_brand__vchr_name','vchr_item_code','fk_item_category_id','fk_item_category__vchr_item_category','fk_item_group_id','fk_item_group__vchr_item_group','dbl_supplier_cost','dbl_dealer_cost','dbl_mrp','dbl_mop','json_specification_id','int_reorder_level','vchr_prefix','imei_status','sale_status','dat_created').filter(int_status = 1))
            #     spec_name = dict(Specifications.objects.values_list('pk_bint_id','vchr_name'))
            #     lst_item = []
            #     for ins_item in ins_item_list:
            #         dct_item= {}
            #         dct_item['pk_bint_id'] = ins_item['pk_bint_id']
            #         dct_item['product_id'] = ins_item['fk_product_id']
            #         dct_item['product_name'] = ins_item['fk_product__vchr_name']
            #         dct_item['brand_id'] = ins_item['fk_brand_id']
            #         dct_item['brand_name'] = ins_item['fk_brand__vchr_name']
            #         dct_item['item_category_id'] = ins_item['fk_item_category_id']
            #         dct_item['item_category_name'] = ins_item['fk_item_category__vchr_item_category']
            #         dct_item['item_group_id'] = ins_item['fk_item_group_id']
            #         dct_item['item_group_name'] = ins_item['fk_item_group__vchr_item_group']
            #         dct_item['dbl_supplier_cost'] = ins_item['dbl_supplier_cost']
            #         dct_item['dbl_dealer_cost'] = ins_item['dbl_dealer_cost']
            #         dct_item['dbl_mrp'] = ins_item['dbl_mrp']
            #         dct_item['dbl_mop'] = ins_item['dbl_mop']
            #         dct_item['int_reorder_level'] = ins_item['int_reorder_level']
            #         dct_item['vchr_prefix'] = ins_item['vchr_prefix']
            #         dct_item['vchr_item_code'] = ins_item['vchr_item_code']
            #         dct_item['imei_status'] = ins_item['imei_status']
            #         dct_item['sale_status'] = ins_item['sale_status']
            #         dct_item['dat_created'] = ins_item['dat_created']
            #         dct_item['specification'] = ins_item['json_specification_id']
            #         lst_item.append(dct_item)


            return Response({'status':1 , 'data' : lst_item})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})


    # def put(self,request):
    #     try:
    #         # update
    #         bln_sales = request.data.get('bln_sales')
    #         product_id = request.data.get('product_id')
    #         brand_id = request.data.get('brand_id')
    #         vchr_item_code = request.data.get('vchr_item_code')
    #         item_category_id = request.data.get('item_category_id')
    #         item_group_id = request.data.get('item_group_id')
    #         dbl_supplier_cost = request.data.get('dbl_supplier_cost')
    #         dbl_dealer_cost = request.data.get('dbl_dealer_cost')
    #         dbl_mop = request.data.get('dbl_mop')
    #         dbl_mrp = request.data.get('dbl_mrp')
    #         int_reorder_level = request.data.get('int_reorder_level')
    #         json_specification_id = request.data.get('int_specification_id')
    #         vchr_prefix = request.data.get('vchr_prefix')
    #         imei_status = request.data.get('imei_status')
    #         int_id = request.data.get('pk_bint_id')
    #
    #         ins_item_update = Item.objects.filter(pk_bint_id = pk_bint_id).update(fk_product_id=product_id,fk_brand_id=brand_id,vchr_item_code=vchr_item_code,fk_item_category_id=item_category_id,fk_item_group_id=item_group_id,dbl_supplier_cost=dbl_supplier_cost,dbl_dealer_cost=dbl_dealer_cost,dbl_mrp=dbl_mrp,dbl_mop=dbl_mop,json_specification_id=json_specification_id,int_reorder_level=int_reorder_level,vchr_prefix=vchr_prefix,imei_status=imei_status,sale_status=bln_sales,fk_updated_id = request.user)
    #
    #         return Response({'status':1})
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
    #         return Response({'status':0})


    def patch(self,request):
        try:
            #delete
            int_id = request.data.get('pk_bint_id')

            ins_item_update = Item.objects.filter(pk_bint_id = int_id).update(int_status = 0)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class GetItemSpecData(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            ins_item_category = list(ItemCategory.objects.filter(int_status = 0).extra(select={'sgst':"json_tax_master->>'1'",'cgst':"json_tax_master->>'2'"}).values('pk_bint_id','vchr_item_category','sgst','cgst'))
            ins_item_group = list(ItemGroup.objects.filter(int_status = 0).values('pk_bint_id','vchr_item_group'))
            return Response({'status':1 ,'item_category':ins_item_category,'item_group':ins_item_group })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})
    def post(self,request):
        try:
            pk_bint_id = request.data.get('int_category')
            ins_specification = list( Specifications.objects.filter(pk_bint_id__in = ItemCategory.objects.filter(pk_bint_id = pk_bint_id).values_list('json_specification_id',flat=True).first()).values('pk_bint_id','vchr_name'))
            return Response({'status':1 , 'specification' : ins_specification})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})



class ListItemData(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
             #listing
            # import pdb; pdb.set_trace()
            dat_from = request.data.get('datFrom')
            dat_to = request.data.get('datTo')
            product_id = request.data.get('IntProductId')
            brand_id = request.data.get('IntBrandId')
            item_category = request.data.get('IntCategoryId')
            item_group = request.data.get('IntGroupId')
            item_id = request.data.get('IntItemId')

            ins_item_list = Item.objects.values('pk_bint_id','vchr_name','fk_product_id','fk_product__vchr_name','fk_brand_id','fk_brand__vchr_name','vchr_item_code','fk_item_category_id','fk_item_category__vchr_item_category','fk_item_group_id','fk_item_group__vchr_item_group','dbl_supplier_cost','dbl_dealer_cost','dbl_mrp','dbl_mop','json_specification_id','int_reorder_level','vchr_prefix','imei_status','sale_status','dat_created').filter(int_status = 0).order_by('-pk_bint_id')
            spec_name = dict(Specifications.objects.values_list('pk_bint_id','vchr_name'))
            if dat_from and dat_to:
                ins_item_list = ins_item_list.filter(dat_created__date__lte = dat_to,dat_created__date__gte = dat_from)
            if product_id:
                ins_item_list = ins_item_list.filter(fk_product_id = product_id)
            if brand_id:
                ins_item_list = ins_item_list.filter(fk_brand_id = brand_id)
            if item_category:
                ins_item_list = ins_item_list.filter(fk_item_category_id = item_category)
            if item_group:
                ins_item_list = ins_item_list.filter(fk_item_group_id = item_group)
            if item_id:
                ins_item_list = ins_item_list.filter(pk_bint_id = item_id)

            lst_item = list(ins_item_list)
            return Response({'status':1 , 'data' : lst_item})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0})

class ItemTypeHead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            int_item_code = request.data.get('intBrandId')
            int_product_id = request.data.get('intProductId')
            int_item_group_id = request.data.get('IntItemGroupId')
            lst_item = []
            if str_search_term != -1:
                ins_item = Item.objects.filter(Q(vchr_item_code__icontains = str_search_term) | Q(vchr_name__icontains = str_search_term),int_status =0).values('pk_bint_id','vchr_name','vchr_item_code')
                if request.data.get('product_id'):
                    ins_item = ins_item.filter(fk_product_id=request.data.get('product_id'))
                if request.data.get('brand_id'):
                    ins_item = ins_item.filter(fk_brand_id=request.data.get('brand_id'))
                if request.data.get('int_item_code'):
                    ins_item = ins_item.filter(fk_brand_id=int_item_code)

                if int_product_id:
                    ins_item = ins_item.filter(fk_product_id=int_product_id)
                if int_item_group_id:
                    ins_item = ins_item.filter(fk_item_group_id=int_item_group_id)

                if ins_item:
                    for itr_item in ins_item[:20]:
                        dct_items = {}
                        # dct_items['name'] = itr_item['vchr_name']
                        dct_items['code_name'] = itr_item['vchr_item_code'] +" - " + itr_item['vchr_name']
                        dct_items['id'] = itr_item['pk_bint_id']
                        lst_item.append(dct_items)
            return Response({'status':1,'data':lst_item})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})

class ItemTypeHeadWithProduct(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('strItem',-1)
            lst_item = []
            if str_search_term != -1:
                ins_item = Item.objects.filter(Q(vchr_name__icontains=str_search_term) | Q(vchr_item_code__icontains=str_search_term),int_status =0,fk_product_id=request.data.get('intProductId')).values('pk_bint_id','vchr_name','vchr_item_code')
                if request.data.get('product_id'):
                    ins_item = ins_item.filter(fk_product_id=request.data.get('product_id'))
                if request.data.get('brand_id'):
                    ins_item = ins_item.filter(fk_brand_id=request.data.get('brand_id'))
                if ins_item:
                    for itr_item in ins_item[:20]:
                        dct_items = {}
                        # dct_items['name'] = itr_item['vchr_name']
                        dct_items['code_name'] = itr_item['vchr_item_code'] +" - " + itr_item['vchr_name']
                        dct_items['id'] = itr_item['pk_bint_id']
                        lst_item.append(dct_items)
                return Response({'status':1,'data':lst_item})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})



class ItemCategoryTypeHead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            lst_item_category = []
            if str_search_term != -1:
                ins_item_category = ItemCategory.objects.filter(Q(vchr_item_category__icontains=str_search_term),int_status=0).values('pk_bint_id','vchr_item_category')
                if ins_item_category:
                    for itr_item in ins_item_category:
                        dct_items = {}
                        dct_items['name'] = itr_item['vchr_item_category']
                        dct_items['id'] = itr_item['pk_bint_id']
                        lst_item_category.append(dct_items)
                return Response({'status':1,'data':lst_item_category})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})


class ItemTypeaheadAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            int_item_code = request.data.get('intBrand')
            int_product_id = request.data.get('intProduct')
            int_item_id = request.data.get('intItemId')
            lst_items = []
            tax_name = dict(TaxMaster.objects.values_list('pk_bint_id','vchr_name'))
            if str_search_term != -1 or int_item_id:
                if int_item_id:
                    ins_items = Item.objects.filter(pk_bint_id=int_item_id,int_status = 0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master','imei_status','fk_product__vchr_name','dbl_mop')\
                                                                                                .annotate(bln_service=Case(When(fk_product__int_sales=2,then=True),default=False,output_field=BooleanField()))
                else:
                    ins_items = Item.objects.filter(Q(vchr_name__icontains=str_search_term) | Q(vchr_item_code__icontains=str_search_term),
                                                                                            int_status = 0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master','imei_status','fk_product__vchr_name','dbl_mop')\
                                                                                            .annotate(bln_service=Case(When(fk_product__int_sales=2,then=True),default=False,output_field=BooleanField()))
                if int_item_code:
                    ins_items = ins_items.filter(fk_brand_id = int_item_code)
                if int_product_id:
                    ins_items = ins_items.filter(fk_product_id = int_product_id)
                # ins_items = Item.objects.filter(Q(vchr_name__icontains=str_search_term)\
                # | Q(vchr_item_code__icontains=str_search_term),int_status = 0).values('pk_bint_id','vchr_name','vchr_item_code','fk_item_category__json_tax_master','imei_status').annotate(bln_service=Case(When(fk_product__int_sales=2,then=True),default=False,output_field=BooleanField()))
                # import pdb; pdb.set_trace()
                if ins_items:
                    for itr_item in ins_items[0:20]:
                        dct_item = {}
                        dct_item['strItemCode'] = itr_item['vchr_item_code'].upper()
                        dct_item['strItemName'] = itr_item['vchr_name'].title()
                        dct_item['strItemId'] = itr_item['pk_bint_id']
                        dct_item['blnService'] = itr_item['bln_service']
                        if  itr_item['fk_item_category__json_tax_master']:
                            dct_item['jsnTax']={}
                            for ins_tax in itr_item['fk_item_category__json_tax_master']:
                                # dct_item['jsn_tax'][ins_tax] ={}
                                dct_item['jsnTax'][tax_name[int(ins_tax)]] =  itr_item['fk_item_category__json_tax_master'][ins_tax]
                        else:
                            dct_item['jsnTax']=0
                        dct_item['vchr_product_name']=itr_item['fk_product__vchr_name']

                        if itr_item['fk_product__vchr_name']=="SIM" or itr_item['fk_product__vchr_name'] == "RECHARGE" or itr_item['fk_product__vchr_name'].upper() == "CARE PLUS":

                            dct_tax = {}
                            for ins_tax in TaxMaster.objects.filter(bln_active=True).values('pk_bint_id','vchr_name'):
                                dct_tax[ins_tax['vchr_name']] = str(ins_tax['pk_bint_id'])


                            dct_item['dblRate'] = itr_item.get('dbl_mop')
                            dct_item['dblAmount'] = itr_item.get('dbl_mop')
                            dct_item['dblMopAmount'] = itr_item.get('dbl_mop')
                            dct_item['dblMarginAmount'] = 0

                            dct_item['dblSGSTPer'] =  itr_item['fk_item_category__json_tax_master'].get(dct_tax['SGST'],0)
                            dct_item['dblSGST'] = itr_item.get('dbl_mop')* itr_item['fk_item_category__json_tax_master'].get(dct_tax['SGST'],0)/100
                            dct_item['dblCGSTPer'] =  itr_item['fk_item_category__json_tax_master'].get(dct_tax['CGST'],0)
                            dct_item['dblCGST'] = itr_item.get('dbl_mop')* itr_item['fk_item_category__json_tax_master'].get(dct_tax['CGST'],0)/100
                            dct_item['dblIGSTPer'] =  itr_item['fk_item_category__json_tax_master'].get(dct_tax['IGST'],0)
                            dct_item['dblIGST'] = itr_item.get('dbl_mop')* itr_item['fk_item_category__json_tax_master'].get(dct_tax['IGST'],0)/100
                            if request.data.get("blnIGST"):
                                dct_item['GST']=dct_item['dblIGSTPer']
                            else:
                                dct_item['GST']=dct_item['dblSGSTPer']+dct_item['dblCGSTPer']
                        dct_item['imei_status']=itr_item['imei_status']
                        # import pdb; pdb.set_trace()
                        if dct_item['strItemCode'] in ['GDC00001','GDC00002'] :
                            dct_item['imei_status']=True
                        lst_items.append(dct_item)
                return Response({'status':'1','data':lst_items})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':'failed','message':str(e)})


class BiItemUpdateAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            dat_to = datetime.now()
            dat_from = dat_to - timedelta(days=1)
            spec_details = []
            spec_values = {}
            rst_spec = Specifications.objects.all().values()

            # rst_item_data = list(Item.objects.filter(pk_bint_id__in = [181785,181784,181783,181782,181781] ).values('vchr_item_code','vchr_old_item_code','dbl_mop','fk_product__vchr_name','fk_brand__vchr_name','vchr_name','fk_item_category_id__json_specification_id','json_specification_id'))
            rst_item_data = list(Item.objects.filter(Q(dat_updated__date__gte = datetime.strftime(dat_from,'%Y-%m-%d'),dat_updated__date__lte = datetime.strftime(dat_to,'%Y-%m-%d')) | Q(dat_created__date__gte = datetime.strftime(dat_from,'%Y-%m-%d'),dat_created__date__lte = datetime.strftime(dat_to,'%Y-%m-%d'))).values('vchr_item_code','vchr_old_item_code','dbl_mop','dbl_mrp','dbl_myg_amount','fk_product__vchr_name','fk_brand__vchr_name','vchr_name','fk_item_category_id__json_specification_id','json_specification_id','fk_item_category__vchr_item_category','fk_item_group__vchr_item_group'))
            for ins_item in rst_item_data:
                # spec_details = list(rst_spec.filter(pk_bint_id__in = rst_item_data[0]['fk_item_category_id__json_specification_id'],bln_status = True ).values_list('vchr_name',flat = True))
                """updated by freddy"""
                spec_details = list(rst_spec.filter(pk_bint_id__in = ins_item['fk_item_category_id__json_specification_id'],bln_status = True ).values_list('vchr_name',flat = True))
                dct_spec = {}
                for str_data in spec_details:
                    dct_spec[str_data] = True
                ins_item['spec_name']= dct_spec
                if type(ins_item['json_specification_id']) == str:
                    dct_spec_id = eval(ins_item['json_specification_id'])
                else:
                    dct_spec_id = ins_item['json_specification_id']
                spec_values = {list(rst_spec.filter(pk_bint_id = key).values_list('vchr_name',flat=True))[0]: dct_spec_id[key] for key in dct_spec_id}
                ins_item['spec_values']= spec_values
            return Response({'status':1,'data': rst_item_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'message':str(e)})

class ItemMopMrp(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # id_item_id = 18
            id_item_id = request.data.get('itemid')
            # lst_item = []
            dict_item = Item.objects.filter(pk_bint_id=id_item_id).values('dbl_mrp','dbl_mop').first()
            if dict_item:
                return Response({'status':1,'data':dict_item})
            else:
                return Response({'status':0,'reason':'no data found'})
        except Exception as e:
            return Response({'result':0,'reason':e})



class ItemPriceAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # LG
            check_auth = request.META.get('REMOTE_ADDR')
            if check_auth not in ['94.237.66.244','94.237.77.193','149.28.131.169']:
                return Response({"status":0,"reason":"unauthorized access"})

            # # id_item_id = 18
            # int_auth = request.data.get('auth_key')
            # # int_auth_key = 7636
            # int_auth_key = '1122-3344-5566-7788'
            # if int(int_auth)  != int_auth_key:
            #     return Response({"status":0,"reason":"authentication failed"})
            str_item_code = request.data.get('ITEM_CODE')
            # lst_item = []
            dict_data={}
            dict_item = Item.objects.filter(vchr_item_code = str_item_code).values('dbl_mop','vchr_name','pk_bint_id').first()
            if dict_item:
                dict_data['ITEM_NAME']=dict_item['vchr_name']
                dict_data['ITEM_CODE'] = str_item_code
                dict_data['ITEM_PRICE']=dict_item['dbl_mop']

                return Response({'status':1,'data':dict_data})
            else:
                return Response({'status':1,'reason':'no data found'})
        except Exception as e:
            print("Error : ",e)
            return Response({'status':0,'reason':e})




class ItemTypeHeadStock(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            str_search_term = request.data.get('term',-1)
            int_brand_id = request.data.get('intBrandId')
            int_product_id = request.data.get('intProductId')
            lst_item = []
            if str_search_term != -1:
                ins_item = Item.objects.filter(Q(vchr_item_code__icontains = str_search_term) | Q(vchr_name__icontains = str_search_term),int_status =0).values('pk_bint_id','vchr_name','vchr_item_code')

                if int_product_id:
                    ins_item = ins_item.filter(fk_product_id=int_product_id)
                if int_brand_id:
                    ins_item = ins_item.filter(fk_brand_id=int_brand_id)

                if ins_item:
                    for itr_item in ins_item[:20]:
                        dct_items = {}
                        # dct_items['name'] = itr_item['vchr_name']
                        dct_items['code_name'] = itr_item['vchr_item_code'] +" - " + itr_item['vchr_name']
                        dct_items['id'] = itr_item['pk_bint_id']
                        lst_item.append(dct_items)




                # if request.data.get('product_id'):
                #     ins_item = ins_item.filter(fk_product_id=request.data.get('product_id'))
                # if request.data.get('intBrandId'):
                #     ins_item = ins_item.filter(fk_brand_id=request.data.get('brand_id'))
                #
                # if request.data.get('int_item_code'):
                #     ins_item = ins_item.filter(fk_brand_id=int_item_code)
                # if int_product_id:
                #     ins_item = ins_item.filter(fk_product_id=int_product_id)
                # if ins_item:
                #     for itr_item in ins_item[:20]:
                #         dct_items = {}
                #         # dct_items['name'] = itr_item['vchr_name']
                #         dct_items['code_name'] = itr_item['vchr_item_code'] +" - " + itr_item['vchr_name']
                #         dct_items['id'] = itr_item['pk_bint_id']
                #         lst_item.append(dct_items)
            return Response({'status':1,'data':lst_item})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})



class ECommerceItemPriceAPI(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            time_now = datetime.now()
            str_item_code = json.loads(request.data.get('ITEM_CODE'))
            str_buy_back =request.data.get('BUY_BACK') or []
            dict_buy_back = []
            if str_buy_back:
                str_buy_back = json.loads(str_buy_back)
                dict_buy_back = list(Item.objects.filter(vchr_item_code__in = str_buy_back).annotate(MRP = F("dbl_mrp"),ITEM_CODE = F("vchr_item_code"),MOP = F("dbl_mop"),MYG_PRICE = Case(When(dbl_myg_amount = None,then=0),default = F('dbl_myg_amount'), output_field = FloatField())).values('MOP','ITEM_CODE','MYG_PRICE','MRP'))

            time_now = time_now - timedelta(minutes=11)
            dict_item = list(Item.objects.filter((Q(dat_created__gte = time_now) | Q(dat_updated__gte = time_now)),vchr_item_code__in = str_item_code).annotate(MRP = F("dbl_mrp"),ITEM_CODE = F("vchr_item_code"),MOP = F("dbl_mop"),MYG_PRICE = Case(When(dbl_myg_amount = None,then=0),default = F('dbl_myg_amount'), output_field = FloatField())).values('MOP','ITEM_CODE','MYG_PRICE','MRP').exclude(vchr_item_code__in = str_buy_back))
            dict_item.extend(dict_buy_back)
            return Response({'status':1,'data':dict_item})
            # else:
            #     return Response({'status':1,'reason':'no data found'})
        except Exception as e:
            print("Error : ",e)
            return Response({'status':0,'reason':e})
