from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy import desc

from source.models import Source
from branch.models import Branch
from priority.models import Priority

from django.http import JsonResponse
from django.contrib.auth.models import User
from userdetails.models import UserDetails as UserModel
from enquiry.models import EnquiryMaster,Document
from stock_app.models import Stockmaster,Stockdetails
from source.models import Source
from priority.models import Priority
from customer.models import CustomerDetails as CustomerModel
from customer_rating.models import CustomerRating
from company.models import Company as CompanyDetails
from datetime import datetime
from os.path import splitext
from os import path,makedirs
from django.db import transaction

from enquiry_mobile.models import MobileEnquiry, MobileFollowup, TabletEnquiry, TabletFollowup, ComputersEnquiry, ComputersFollowup, AccessoriesEnquiry, AccessoriesFollowup

# from inventory.models import Brands, Products, Items
from brands.models import Brands
from products.models import  Products
from item_category.models import Item as Items

from django.db.models import Case,  Value, When,F
from django.db.models import Q

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

class AddEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            ins_user = UserModel.objects.get(id = request.user.id)
            ins_branch = UserModel.objects.filter(id = request.user.id).values('fk_branch')
            ins_user_branch = Branch.objects.get(pk_bint_id = ins_branch[0]['fk_branch'])
            ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
            str_code = ins_document[0].vchr_short_code
            int_doc_num = ins_document[0].int_number + 1
            ins_document.update(int_number = int_doc_num)
            str_number = str(int_doc_num).zfill(4)
            str_enquiry_no = str_code + '-' + str_number
            dat_created_at = datetime.now()
            # dct_customer_rating = request.data.get('customer_rating')
            # dct_status = request.data.get('status')
            ins_assigned_user = ins_user
            ins_customer = CustomerModel.objects.get(id = request.data.get('fk_customer_id'))
            ins_master = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
            EnquiryMaster.objects.filter(pk_bint_id = ins_master.pk_bint_id).update(
                    # vchr_enquiry_num = str_enquiry_no
                    fk_customer = ins_customer
                    ,fk_source = Source.objects.get(pk_bint_id=request.data.get('fk_enquiry_source'))
                    ,fk_priority = Priority.objects.get(pk_bint_id=request.data.get('fk_enquiry_priority'))
                    ,fk_assigned = ins_assigned_user
                    ,fk_branch = ins_user_branch
                    # ,bln_sms = dct_customer_data['bln_sms']
                    ,chr_doc_status = 'N'
                    ,fk_created_by = ins_user
                    ,dat_created_at = datetime.now(),
                    fk_company = ins_user.fk_company
                )
            ins_master.save()

            if request.data.get('MOBILE'):
                for dct_mob in request.data.get('MOBILE'):
                    ins_brand = Brands.objects.get(id = int(dct_mob['fk_brand']['id']))
                    ins_item = Items.objects.get(id = int(dct_mob['fk_item']['id']))

                    if not dct_mob['dbl_estimated_amount']:
                            dct_mob['dbl_estimated_amount'] = '0.0'

                    if not dct_mob['int_quantity']:
                        dct_mob['int_quantity'] = '0'

                    ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_mob['fk_item']['id']), int_available__gte = int(dct_mob['int_quantity'])).order_by('fk_stock_master__dat_added').values()
                    ins_stock_details = ''
                    if ins_stock:
                        int_stock_id = int(ins_stock[0]['pk_bint_id'])
                        ins_stock_details = Stockdetails.objects.get(pk_bint_id = int_stock_id)

                        if dct_mob.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            int_curr = int(ins_stock[0]['int_available']) - int(dct_mob['int_quantity'])
                            ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                        else:
                            ins_stock_details = None

                    else:
                        return Response({'status':'1', 'data':'Selected Mobile exceeds available stock amount'})


                    ins_mob_enq = MobileEnquiry(fk_enquiry_master = ins_master,
                                                fk_brand = Brands.objects.get(id = dct_mob['fk_brand']['id']),
                                                fk_item = Items.objects.get(id = dct_mob['fk_item']['id']),
                                                int_quantity = dct_mob['int_quantity'],
                                                dbl_amount = dct_mob['dbl_estimated_amount'],
                                                vchr_enquiry_status = dct_mob['vchr_enquiry_status'],
                                                vchr_colour = dct_mob['vchr_colour'],
                                                vchr_spec = dct_mob['vchr_spec'],
                                                vchr_remarks = dct_mob['vchr_remarks'],
                                                fk_stockdetails = ins_stock_details,
                                                dbl_imei_json = {'imei' : dct_mob.get('lst_imei',[])})
                    if dct_mob['vchr_enquiry_status'] == 'BOOKED':
                        ins_mob_enq.int_sold = int(dct_mob['int_quantity'])
                        ins_mob_enq.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                    ins_mob_enq.save()
                    if ins_mob_enq and dct_mob.get('vchr_enquiry_status','') == 'BOOKED':
                        ins_mob_enq_exist = MobileEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        if ins_mob_enq_exist:
                            ins_mob_enq_exist.update(vchr_enquiry_status = 'LOST')
                            lst_query_set = []
                            for ins_data in ins_mob_enq_exist:
                                ins_follow_up = MobileFollowup(fk_mobile = ins_data,
                                                                  vchr_notes = 'Mobile in ' + ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                                  vchr_enquiry_status = 'LOST',
                                                                  int_status = 1,
                                                                  dbl_amount = 0.0,
                                                                  fk_user = ins_user,
                                                                  fk_updated = ins_user,
                                                                  dat_followup = dat_created_at,
                                                                  dat_updated = dat_created_at)
                                lst_query_set.append(ins_follow_up)
                            if lst_query_set:
                                MobileFollowup.objects.bulk_create(lst_query_set);


                    ins_mob_foll = MobileFollowup(  fk_mobile = ins_mob_enq,
                                                    dat_followup = datetime.now(),
                                                    fk_user = ins_user,
                                                    vchr_notes = dct_mob['vchr_remarks'],
                                                    vchr_enquiry_status = dct_mob['vchr_enquiry_status'],
                                                    dbl_amount = dct_mob['dbl_estimated_amount'],
                                                    fk_updated = ins_user,
                                                    dat_updated = datetime.now())
                    ins_mob_foll.save()


            if request.data.get('tablets'):
                for dct_tab in request.data.get('tablets'):
                    if not dct_tab['dbl_estimated_amount']:
                            dct_tab['dbl_estimated_amount'] = '0.0'

                    if not dct_tab['int_quantity']:
                        dct_tab['int_quantity'] = '0'

                    ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_tab['fk_item']), int_available__gte = int(dct_tab['int_quantity'])).order_by('fk_stock_master__dat_added').values()
                    ins_stock_details = ''
                    if ins_stock:
                        int_stock_id = int(ins_stock[0]['pk_bint_id'])
                        ins_stock_details = Stockdetails.objects.get(pk_bint_id = int_stock_id)

                        if dct_tab.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            int_curr = int(ins_stock[0]['int_available']) - int(dct_tab['int_quantity'])
                            ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                        else:
                            ins_stock_details = None
                    else:
                        return Response({'status':'1', 'data':'Selected Tablet exceeds available stock amount'})

                    ins_tab_enq = TabletEnquiry(fk_enquiry_master = ins_master,
                                                fk_brand = Brands.objects.get(id = dct_tab['fk_brand']['id']),
                                                fk_item = Items.objects.get(id = dct_tab['fk_item']['id']),
                                                int_quantity = dct_tab['int_quantity'],
                                                dbl_amount = dct_tab['dbl_estimated_amount'],
                                                vchr_enquiry_status = dct_tab['vchr_enquiry_status'],
                                                vchr_remarks = dct_tab['vchr_remarks'],
                                                fk_stockdetails = ins_stock_details,
                                                dbl_imei_json = {'imei' : dct_tab.get('lst_imei',[])}
                                                )
                    if dct_tab['vchr_enquiry_status'] == 'BOOKED':
                        ins_tablet.int_sold = int(dct_tab['int_quantity'])
                        ins_tablet.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                    ins_tab_enq.save()
                    if ins_tab_enq and dct_tab.get('vchr_enquiry_status','') == 'BOOKED':
                        ins_tab_enq_exist = TabletEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        if ins_tab_enq_exist:
                            ins_tab_enq_exist.update(vchr_enquiry_status = 'LOST')
                            lst_query_set = []
                            for ins_data in ins_tab_enq_exist:
                                ins_follow_up = TabletFollowup(fk_tablet = ins_data,
                                                                  vchr_notes = 'Tablet in ' + ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                                  vchr_enquiry_status = 'LOST',
                                                                  int_status = 1,
                                                                  dbl_amount = 0.0,
                                                                  fk_user = ins_user,
                                                                  fk_updated = ins_user,
                                                                  dat_followup = dat_created_at,
                                                                  dat_updated = dat_created_at,
                                                                  int_quantity = dct_tab['int_quantity'])
                                lst_query_set.append(ins_follow_up)
                            if lst_query_set:
                                TabletFollowup.objects.bulk_create(lst_query_set);
                    ins_tab_foll = TabletFollowup(  fk_tablet = ins_tab_enq,
                                                    dat_followup = datetime.now(),
                                                    fk_user = ins_user,
                                                    vchr_notes = dct_tab['vchr_remarks'],
                                                    vchr_enquiry_status = dct_tab['vchr_enquiry_status'],
                                                    dbl_amount = dct_tab['dbl_estimated_amount'],
                                                    fk_updated = ins_user,
                                                    dat_updated = datetime.now(),
                                                    int_quantity = dct_tab['int_quantity'])
                    ins_tab_foll.save()

            if request.data.get('computers'):
                for dct_comp in request.data.get('computers'):
                    if not dct_comp['dbl_estimated_amount']:
                            dct_comp['dbl_estimated_amount'] = '0.0'

                    if not dct_comp['int_quantity']:
                        dct_comp['int_quantity'] = '0'

                    ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_comp['fk_item']), int_available__gte = int(dct_comp['int_quantity'])).order_by('fk_stock_master__dat_added').values()
                    ins_stock_details = ''
                    if ins_stock:
                        int_stock_id = int(ins_stock[0]['pk_bint_id'])
                        ins_stock_details = Stockdetails.objects.get(pk_bint_id = int_stock_id)

                        if dct_comp.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            int_curr = int(ins_stock[0]['int_available']) - int(dct_comp['int_quantity'])
                            ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                        else:
                            ins_stock_details = None

                    else:
                        return Response({'status':'1', 'data':'Selected Computer exceeds available stock amount'})

                    ins_comp_enq = ComputersEnquiry(fk_enquiry_master = ins_master,
                                                fk_brand = Brands.objects.get(id = dct_comp['fk_brand']['id']),
                                                fk_item = Items.objects.get(id = dct_comp['fk_item']['id']),
                                                int_quantity = dct_comp['int_quantity'],
                                                dbl_amount = dct_comp['dbl_estimated_amount'],
                                                vchr_enquiry_status = dct_comp['vchr_enquiry_status'],
                                                vchr_remarks = dct_comp['vchr_remarks'],
                                                fk_stockdetails = ins_stock_details,
                                                dbl_imei_json = {'imei' : dct_comp.get('lst_imei',[])})
                    if dct_comp['vchr_enquiry_status'] == 'BOOKED':
                        ins_comp_enq.int_sold = int(dct_comp['int_quantity'])
                        ins_comp_enq.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                    ins_comp_enq.save()
                    if ins_comp_enq and dct_comp.get('vchr_enquiry_status','') == 'BOOKED':
                        ins_comp_enq_exist = ComputersEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        if ins_comp_enq_exist:
                            ins_comp_enq_exist.update(vchr_enquiry_status = 'LOST')
                            lst_query_set = []
                            for ins_data in ins_comp_enq_exist:
                                ins_follow_up = ComputersFollowup(fk_computers = ins_data,
                                                                  vchr_notes = 'Tablet in ' + ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                                  vchr_enquiry_status = 'LOST',
                                                                  int_status = 1,
                                                                  dbl_amount = 0.0,
                                                                  fk_user = ins_user,
                                                                  fk_updated = ins_user,
                                                                  dat_followup = dat_created_at,
                                                                  dat_updated = dat_created_at)
                                lst_query_set.append(ins_follow_up)
                            if lst_query_set:
                                ComputersFollowup.objects.bulk_create(lst_query_set);
                    ins_comp_foll = ComputersFollowup(  fk_computers = ins_comp_enq,
                                                    dat_followup = datetime.now(),
                                                    fk_user = ins_user,
                                                    vchr_notes = dct_comp['vchr_remarks'],
                                                    vchr_enquiry_status = dct_comp['vchr_enquiry_status'],
                                                    dbl_amount = dct_comp['dbl_estimated_amount'],
                                                    fk_updated = ins_user,
                                                    dat_updated = datetime.now())
                    ins_comp_foll.save()

            if request.data.get('accessories'):
                for dct_acc in request.data.get('accessories'):
                    if not dct_acc['dbl_estimated_amount']:
                            dct_acc['dbl_estimated_amount'] = '0.0'

                    if not dct_acc['int_quantity']:
                        dct_acc['int_quantity'] = '0'

                    ins_stock = Stockdetails.objects.filter(fk_item_id = int(dct_acc['fk_item']), int_available__gte = int(dct_acc['int_quantity'])).order_by('fk_stock_master__dat_added').values()
                    ins_stock_details = ''
                    if ins_stock:
                        int_stock_id = int(ins_stock[0]['pk_bint_id'])
                        ins_stock_details = Stockdetails.objects.get(pk_bint_id = int_stock_id)

                        if dct_acc.get('vchr_enquiry_status','NEW') == 'BOOKED':
                            int_curr = int(ins_stock[0]['int_available']) - int(dct_acc['int_quantity'])
                            ins_stock_update = Stockdetails.objects.filter(pk_bint_id = int(ins_stock[0]['pk_bint_id'])).update(int_available = int_curr)
                        else:
                            ins_stock_details = None
                    else:
                        return Response({'status':'1', 'data':'Selected Accessories exceeds available stock amount'})

                    ins_acc_enq = AccessoriesEnquiry(fk_enquiry_master = ins_master,
                                                fk_brand = Brands.objects.get(id = dct_acc['fk_brand']['id']),
                                                fk_item = Items.objects.get(id = dct_acc['fk_item']['id']),
                                                int_quantity = dct_acc['int_quantity'],
                                                dbl_amount = dct_acc['dbl_estimated_amount'],
                                                vchr_enquiry_status = dct_acc['vchr_enquiry_status'],
                                                vchr_remarks = dct_acc['vchr_remarks'],
                                                fk_stockdetails = ins_stock_details,
                                                dbl_imei_json = {'imei' : dct_acc.get('lst_imei',[])})
                    if dct_acc['vchr_enquiry_status'] == 'BOOKED':
                        ins_acc_enq.int_sold = int(dct_acc['int_quantity'])
                        ins_acc_enq.dbl_sup_amount = Stockdetails.objects.get(pk_bint_id = int_stock_id).dbl_cost
                    ins_acc_enq.save()
                    if ins_acc_enq and dct_acc.get('vchr_enquiry_status','') == 'BOOKED':
                        ins_acc_enq_exist = AccessoriesEnquiry.objects.filter(fk_enquiry_master__fk_customer = ins_customer.id,fk_enquiry_master__fk_company = ins_user.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        if ins_acc_enq_exist:
                            ins_acc_enq_exist.update(vchr_enquiry_status = 'LOST')
                            lst_query_set = []
                            for ins_data in ins_acc_enq_exist:
                                ins_follow_up = AccessoriesFollowup(fk_accessories = ins_data,
                                                                  vchr_notes = 'Tablet in ' + ins_data.fk_enquiry_master.vchr_enquiry_num + ' is booked',
                                                                  vchr_enquiry_status = 'LOST',
                                                                  int_status = 1,
                                                                  dbl_amount = 0.0,
                                                                  fk_user = ins_user,
                                                                  fk_updated = ins_user,
                                                                  dat_followup = dat_created_at,
                                                                  dat_updated = dat_created_at)
                                lst_query_set.append(ins_follow_up)
                            if lst_query_set:
                                AccessoriesFollowup.objects.bulk_create(lst_query_set);
                    ins_acc_foll = AccessoriesFollowup(  fk_accessories = ins_acc_enq,
                                                    dat_followup = datetime.now(),
                                                    fk_user = ins_user,
                                                    vchr_notes = dct_acc['vchr_remarks'],
                                                    vchr_enquiry_status = dct_acc['vchr_enquiry_status'],
                                                    dbl_amount = dct_acc['dbl_estimated_amountff'],
                                                    fk_updated = ins_user,
                                                    dat_updated = datetime.now())
                    ins_acc_foll.save()

            return JsonResponse({'status': 'Success','data':str_enquiry_no})

        except Exception as e:
            if 'ins_master' in locals():
                MobileFollowup.objects.filter(fk_mobile__fk_enquiry_master = ins_master.pk_bint_id).delete()
                ComputersFollowup.objects.filter(fk_computers__fk_enquiry_master = ins_master.pk_bint_id).delete()
                TabletFollowup.objects.filter(fk_tablet__fk_enquiry_master = ins_master.pk_bint_id).delete()
                AccessoriesFollowup.objects.filter(fk_accessories__fk_enquiry_master = ins_master.pk_bint_id).delete()

                MobileEnquiry.objects.filter(fk_enquiry_master = ins_master.pk_bint_id).delete()
                TabletEnquiry.objects.filter(fk_enquiry_master = ins_master.pk_bint_id).delete()
                ComputersEnquiry.objects.filter(fk_enquiry_master = ins_master.pk_bint_id).delete()
                AccessoriesEnquiry.objects.filter(fk_enquiry_master = ins_master.pk_bint_id).delete()

                EnquiryMaster.objects.filter(pk_bint_id = ins_master.pk_bint_id).delete()
            return JsonResponse({'status': 'Failed','data':str(e)})


# class AddFollowup(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             dat_created = datetime.now()
#
#             if request.data['vchr_servicetype'] == 'MOBILE':
#                 if MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
#                     dat_updated_time = dat_created
#                     fk_updated_by = UserModel.objects.get(id = request.user.id).id
#                     int_status = 1
#                 else :
#                     dat_updated_time = None
#                     fk_updated_by = None
#                     int_status = 0
#                 if request.data['vchr_followup_status'] == 'BOOKED':
#                     ins_mobile_exist = MobileEnquiry.objects.filter(fk_enquiry_master__fk_company = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
#                     if ins_mobile_exist:
#                         ins_mobile_exist.update(vchr_enquiry_status = 'LOST')
#                         lst_query_set = []
#                         for data in ins_mobile_exist:
#                             ins_follow_up = MobileFollowup(
#                             fk_mobile = data
#                             ,vchr_notes = 'Mobile in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
#                             ,vchr_enquiry_status = 'LOST'
#                             ,int_status = 1
#                             ,dbl_amount = 0.0
#                             ,fk_user = UserModel.objects.get(id = request.user.id)
#                             ,fk_updated_id = fk_updated_by
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_updated_time
#                             )
#                             lst_query_set.append(ins_follow_up)
#                         if lst_query_set:
#                             MobileFollowup.objects.bulk_create(lst_query_set)
#
#                 ins_mobile_follow_up = MobileFollowup(fk_mobile = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                     vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                     int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
#                     fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time)
#                 ins_mobile_follow_up.save()
#                 if int_status:
#                     ins_mobile = MobileEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status=request.data['vchr_followup_status'],dbl_amount = request.data['int_followup_amount'])
#
#
#             elif request.data['vchr_servicetype'] == 'TABLET':
#                 if TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
#                     dat_updated_time = dat_created
#                     fk_updated_by = UserModel.objects.get(id = request.user.id).id
#                     int_status = 1
#                 else :
#                     dat_updated_time = None
#                     fk_updated_by = None
#                     int_status = 0
#                 if request.data['vchr_followup_status'] == 'BOOKED':
#                     ins_tablet_exist = TabletEnquiry.objects.filter(fk_enquiry_master__fk_company = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
#                     if ins_tablet_exist:
#                         ins_tablet_exist.update(vchr_enquiry_status = 'LOST')
#                         lst_query_set = []
#                         for data in ins_tablet_exist:
#                             ins_follow_up = TabletFollowup(
#                             fk_tablet = data
#                             ,vchr_notes = 'Tablet in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
#                             ,vchr_enquiry_status = 'LOST'
#                             ,int_status = 1
#                             ,dbl_amount = 0.0
#                             ,fk_user = UserModel.objects.get(id = request.user.id)
#                             ,fk_updated_id = fk_updated_by
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_updated_time
#                             )
#                             lst_query_set.append(ins_follow_up)
#                         if lst_query_set:
#                             TabletFollowup.objects.bulk_create(lst_query_set)
#                 ins_tablet_followup = TabletFollowup(fk_tablet = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                     vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                     int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
#                     fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time)
#                 ins_tablet_followup.save()
#                 if int_status:
#                     ins_tablet = TabletEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status=request.data['vchr_followup_status'],dbl_amount = request.data['int_followup_amount'])
#
#
#             elif request.data['vchr_servicetype'] == 'COMPUTER':
#                 if ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
#                     dat_updated_time = dat_created
#                     fk_updated_by = UserModel.objects.get(id = request.user.id).id
#                     int_status = 1
#                 else :
#                     dat_updated_time = None
#                     fk_updated_by = None
#                     int_status = 0
#                 if request.data['vchr_followup_status'] == 'BOOKED':
#                     ins_computer_exist = ComputersEnquiry.objects.filter(fk_enquiry_master__fk_company = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
#                     if ins_computer_exist:
#                         ins_computer_exist.update(vchr_enquiry_status = 'LOST')
#                         lst_query_set = []
#                         for data in ins_computer_exist:
#                             ins_follow_up = ComputersFollowup(
#                             fk_computers = data
#                             ,vchr_notes = 'Tablet in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
#                             ,vchr_enquiry_status = 'LOST'
#                             ,int_status = 1
#                             ,dbl_amount = 0.0
#                             ,fk_user = UserModel.objects.get(id = request.user.id)
#                             ,fk_updated_id = fk_updated_by
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_updated_time
#                             )
#                             lst_query_set.append(ins_follow_up)
#                         if lst_query_set:
#                             ComputersFollowup.objects.bulk_create(lst_query_set)
#                 ins_computer_follow_up = ComputersFollowup(fk_computers = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
#                     vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                     int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
#                     fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time)
#                 ins_computer_follow_up.save()
#                 if int_status:
#                     ins_computer= ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status=request.data['vchr_followup_status'],dbl_amount = request.data['int_followup_amount'])
#
#
#             elif request.data['vchr_servicetype'] == 'ACCESSORIES':
#                 if AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
#                     dat_updated_time = dat_created
#                     fk_updated_by = UserModel.objects.get(id = request.user.id).id
#                     int_status = 1
#                 else :
#                     dat_updated_time = None
#                     fk_updated_by = None
#                     int_status = 0
#                 if request.data['vchr_followup_status'] == 'BOOKED':
#                     ins_accessories_exist = AccessoriesEnquiry.objects.filter(fk_enquiry_master__fk_company = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
#                     if ins_accessories_exist:
#                         ins_accessories_exist.update(vchr_enquiry_status = 'LOST')
#                         lst_query_set = []
#                         for data in ins_accessories_exist:
#                             ins_follow_up = AccessoriesFollowup(
#                             fk_accessories = data
#                             ,vchr_notes = 'Tablet in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
#                             ,vchr_enquiry_status = 'LOST'
#                             ,int_status = 1
#                             ,dbl_amount = 0.0
#                             ,fk_user = UserModel.objects.get(id = request.user.id)
#                             ,fk_updated_id = fk_updated_by
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_updated_time
#                             )
#                             lst_query_set.append(ins_follow_up)
#                         if lst_query_set:
#                             AccessoriesFollowup.objects.bulk_create(lst_query_set)
#                 ins_accessories_follow_up = AccessoriesFollowup(fk_accessories = EventMakeup.objects.get(pk_bint_id = request.data['int_service_id']),\
#                     vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
#                     int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
#                     fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time)
#                 ins_accessories_follow_up.save()
#                 if int_status:
#                     ins_accessories = AccessoriesEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(vchr_enquiry_status=request.data['vchr_followup_status'],dbl_amount = request.data['int_followup_amount'])
#
#             return JsonResponse({'status':'success','value':'Follow-up completed successfully!','followup':request.data['vchr_followup_status'],'change':int_status})
#
#         except Exception as e:
#             return JsonResponse({'status':'0','data':str(e)})


class AddFollowup(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            dat_created = datetime.now()
            if request.data['vchr_servicetype'] == 'COMPUTER':
                try:
                    with transaction.atomic():
                        str_enquiry_no = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                        if ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
                            dat_updated_time = dat_created
                            fk_updated_by = UserModel.objects.get(id = request.user.id).id
                            int_status = 1
                        else :
                            dat_updated_time = None
                            fk_updated_by = None
                            int_status = 0
                        if int_status and request.data.get('vchr_followup_status') == 'BOOKED':
                            rst_enq = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
                            ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
                            if ins_stock:
                                Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
                            else:
                                ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
                                int_available = ins_stock.int_available
                                return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
                        ins_computers_follow_up = ComputersFollowup(fk_computers = ComputersEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
                            vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
                            int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
                            fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                        ins_computers_follow_up.save()
                        if request.data.get('vchr_followup_status')== 'BOOKED':
                            ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
                        if int_status:
                            ins_obj = ComputersEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                            ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                            dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
                        if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                            ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                            dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
                            ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})

                except Exception as e:
                    return Response({'status':'1', 'error':str(e)})

            elif request.data['vchr_servicetype'] == 'TABLET':
                try:
                    with transaction.atomic():
                        str_enquiry_no = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                        if TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
                            dat_updated_time = dat_created
                            fk_updated_by = UserModel.objects.get(id = request.user.id).id
                            int_status = 1
                        else :
                            dat_updated_time = None
                            fk_updated_by = None
                            int_status = 0
                        if int_status and request.data.get('vchr_followup_status') == 'BOOKED':
                            rst_enq = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
                            ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
                            if ins_stock:
                                Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
                            else:
                                ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
                                int_available = ins_stock.int_available
                                return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
                        ins_tablet_followup = TabletFollowup(fk_tablet = TabletEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
                            vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
                            int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
                            fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                        ins_tablet_followup.save()
                        if request.data.get('vchr_followup_status')== 'BOOKED':
                            TabletEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
                        if int_status:
                            ins_obj = TabletEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                            ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],dbl_amount = request.data['int_followup_amount'],int_quantity=request.data.get('int_followup_quantity'),
                            vchr_remarks= request.data['vchr_followup_remarks'])
                        if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                            ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                            dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
                            ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})

                except Exception as e:
                    return Response({'status':'1', 'error':str(e)})


            elif request.data['vchr_servicetype'] == 'ACCESSORIES':
                try:
                    with transaction.atomic():
                        str_enquiry_no = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                        if AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
                            dat_updated_time = dat_created
                            fk_updated_by = UserModel.objects.get(id = request.user.id).id
                            int_status = 1
                        else :
                            dat_updated_time = None
                            fk_updated_by = None
                            int_status = 0
                        if int_status and request.data.get('vchr_followup_status') == 'BOOKED':
                            rst_enq = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
                            ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
                            if ins_stock:
                                Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
                            else:
                                ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
                                int_available = ins_stock.int_available
                                return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
                        ins_accessories_follow_up = AccessoriesFollowup(fk_accessories = AccessoriesEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
                            vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
                            int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
                            fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                        ins_accessories_follow_up.save()
                        if request.data.get('vchr_followup_status')== 'BOOKED':
                            AccessoriesEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
                        if int_status:
                            ins_obj = AccessoriesEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                            ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                            dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
                        if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                            ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                            dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
                            ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})

                except Exception as e:
                    return Response({'status':'1', 'error':str(e)})

            elif request.data['vchr_servicetype'] == 'MOBILE':
                try:
                    with transaction.atomic():
                        if request.data.get('vchr_followup_status') == 'BOOKED':
                            rst_enq = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id'])
                            ins_stock = Stockdetails.objects.filter(fk_item_id = int(rst_enq.fk_item_id), int_available__gte = int(request.data.get('int_followup_quantity'))).order_by('fk_stock_master__dat_added').first()
                            if ins_stock:
                                Stockdetails.objects.filter(pk_bint_id = int(ins_stock.pk_bint_id)).update(int_available = F('int_available')-int(request.data.get('int_followup_quantity')))
                            else:
                                ins_stock = Stockdetails.objects.filter(Q(fk_item_id = int(rst_enq.fk_item_id)),~Q(int_available=0)).order_by('fk_stock_master__dat_added').first()
                                int_available = ins_stock.int_available
                                return Response({'status':'5', 'data':'Selected '+rst_enq.fk_brand.vchr_brand_name+'-'+rst_enq.fk_item.vchr_item_name+' quantity '+str(request.data.get('int_followup_quantity'))+' exceeds available stock quantity of '+str(int_available)+' in your branch'})
                        str_enquiry_no = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.vchr_enquiry_num
                        if MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']).fk_enquiry_master.fk_assigned.id == request.user.id :
                            dat_updated_time = dat_created
                            fk_updated_by = UserModel.objects.get(id = request.user.id).id
                            int_status = 1
                        else :
                            dat_updated_time = None
                            fk_updated_by = None
                            int_status = 0
                        ins_mobile_follow_up = MobileFollowup(fk_mobile = MobileEnquiry.objects.get(pk_bint_id = request.data['int_service_id']),\
                            vchr_notes = request.data['vchr_followup_remarks'],vchr_enquiry_status = request.data['vchr_followup_status'],\
                            int_status = int_status,dbl_amount = request.data['int_followup_amount'],fk_user = UserModel.objects.get(id = request.user.id),\
                            fk_updated_id = fk_updated_by,dat_followup = dat_created,dat_updated = dat_updated_time,int_quantity=request.data.get('int_followup_quantity'))
                        ins_mobile_follow_up.save()
                        if request.data.get('vchr_followup_status')== 'BOOKED':
                            MobileEnquiry.objects.filter(pk_bint_id=request.data['int_service_id']).update(dbl_imei_json={'imei' : request.data.get('lst_imei',[])})
                        if int_status:
                            ins_obj = MobileEnquiry.objects.filter(pk_bint_id=request.data['int_service_id'])
                            ins_obj.update(vchr_enquiry_status=request.data['vchr_followup_status'],int_quantity=request.data.get('int_followup_quantity'),
                            dbl_amount = request.data['int_followup_amount'], vchr_remarks= request.data['vchr_followup_remarks'])
                        if int_status and request.data.get('vchr_followup_status')== 'BOOKED':
                            ins_obj.update(dbl_sup_amount = ins_stock.dbl_cost,dbl_min_price = ins_stock.dbl_min_selling_price,
                            dbl_max_price = ins_stock.dbl_max_selling_price,int_sold = request.data.get('int_followup_quantity')
                            ,dbl_imei_json = {'imei' : request.data.get('lst_imei',[])})

                except Exception as e:
                    return Response({'status':'1', 'error':str(e)})
            if int_status:
                ins_user = UserModel.objects.get(id = request.user.id)
                # enquiry_print(str_enquiry_no,request,ins_user)
            int_enquiry_id = EnquiryMaster.objects.get(chr_doc_status = 'N',vchr_enquiry_num = str_enquiry_no, fk_company_id = request.user.usermodel.fk_company_id).pk_bint_id
            return JsonResponse({'status':'success','value':'Follow-up completed successfully!','remarks':request.data['vchr_followup_remarks'],'followup':request.data['vchr_followup_status'],'amount':request.data['int_followup_amount'],'change':int_status,'enqId':int_enquiry_id,'int_quantity':request.data.get('int_followup_quantity')})

        except Exception as e:
            return JsonResponse({'status':'0','data':str(e)})

class ProductTypeahead(APIView):
    """docstring for Typeahead."""
    permission_classes = [IsAuthenticated]
    def post(self,request,):
        try:
            lst_product = []
            ins_product = Products.objects.values('id','vchr_product_name').exclude(vchr_product_name = 'GDP').order_by('id')
            if ins_product:
                for itr_item in ins_product:
                    dct_product = {}
                    dct_product['id'] = itr_item['id']
                    dct_product['name'] = itr_item['vchr_product_name']
                    lst_product.append(dct_product)
                return Response({'status':'success','data':lst_product})
            else:
                return Response({'status':'empty'})
        except Exception as e:
            return Response({'result':'failed','reason':e})
