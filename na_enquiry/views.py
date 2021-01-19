from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny

from user_app.models import UserModel
from enquiry.models import EnquiryMaster,Document
from na_enquiry.models import NaEnquiryDetails,NaEnquiryMaster
from customer_app.models import CustomerModel
from datetime import datetime, timedelta
from source.models import Source
from priority.models import Priority
from enquiry_mobile.models import ComputersFollowup,TabletFollowup,AccessoriesFollowup,MobileFollowup
from inventory.models import Products,Brands,Items
from customer_rating.models import CustomerRating
from hasher.views import hash_enquiry
from enquiry_print.views import enquiry_print
from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry
from branch.models import Branch
from inventory.models import Brands,Items
from globalMethods import show_data_based_on_role

'''for alchemy'''
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from sqlalchemy import desc

def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

EnquiryMasterSA = EnquiryMaster.sa
CustomerSA = CustomerModel.sa
UserSA=UserModel.sa
AuthUserSA = User.sa
MobileEnquirySA = MobileEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
ComputersEnquirySA = ComputersEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
BranchSA = Branch.sa
BrandSA = Brands.sa
ItemSA = Items.sa
NaEnquiryMasterSA=NaEnquiryMaster.sa
NaEnquiryDetailsSA=NaEnquiryDetails.sa
SourceSA=Source.sa
PrioritySA=Priority.sa
# Create your views here.
class SaveEnquiry(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            dct_customer = request.data.get('customer_data',0)
            lst_mobile= request.data.get('mobile_data',0)
            lst_tablet= request.data.get('tablet_data',0)
            lst_computer= request.data.get('computer_data',0)
            lst_accessories= request.data.get('accessories_data',0)
            dct_cust_rating = request.data.get('customer_rating')
            bln_status = request.data.get('status')
            ins_user = UserModel.objects.get(id = request.user.id)
            # Customer Save Section
            if bln_status.get('MOBILESTATUS'):
                ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
                str_code = ins_document[0].vchr_short_code
                int_doc_num = ins_document[0].int_number + 1
                ins_document.update(int_number = int_doc_num)
                str_number = str(int_doc_num).zfill(4)
                str_enquiry_no = str_code + '-' + str_number
                int_status = 1
                if not dct_customer['fk_assigned_id'] :
                    dct_customer['fk_assigned_id']  = ins_user
                else:
                    dct_customer['fk_assigned_id'] = UserModel.objects.get(id = dct_customer['fk_assigned_id'])
                if dct_customer['fk_assigned_id'].id != ins_user.id:
                    int_status = 0
                dat_created = datetime.now()
                ins_enquiry = NaEnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
                NaEnquiryMaster.objects.filter(pk_bint_id = ins_enquiry.pk_bint_id).update(
                    # vchr_enquiry_num = str_enquiry_no
                    fk_customer = CustomerModel.objects.get(id = dct_customer['fk_customer_id'])
                    ,fk_source = Source.objects.get(pk_bint_id=dct_customer['fk_enquiry_source'])
                    # ,fk_priority = Priority.objects.get(pk_bint_id=dct_customer['fk_enquiry_priority'])
                    ,vchr_customer_type = dct_customer['vchr_customer_type']
                    ,fk_assigned = dct_customer['fk_assigned_id']
                    ,fk_branch = ins_user.fk_branch
                    ,fk_created_by = ins_user
                    ,dat_created_at = dat_created
                    ,fk_company = ins_user.fk_company
                )
                # Computer Save Section
                if bln_status.get('computerNa'):
                    for dct_computer in lst_computer:

                        if not dct_computer['dbl_estimated_amount']:
                            dct_computer['dbl_estimated_amount'] = '0.0'

                        if not dct_computer['intQty']:
                            dct_computer['intQty'] = '0'

                        ins_details = NaEnquiryDetails(
                            fk_na_enquiry_master = ins_enquiry
                            ,vchr_product = 'COMPUTER'
                            ,vchr_brand = dct_computer['strStockBrand'].strip().upper()
                            ,vchr_item = dct_computer['strStockItem'].strip().upper()
                            # ,vchr_color = dct_computer['vchr_color']
                            ,int_quantity = int(dct_computer['intQty'])
                            ,vchr_remarks = dct_computer['vchr_remarks'].strip()
                        )
                        ins_details.save()
                        # if ins_details and dct_computer.get('vchr_enquiry_status','') == 'BOOKED':
                        #     ins_details_exist = NaEnquiryDetails.objects.filter(fk_enquiry_master__fk_customer = dct_customer['fk_customer_id'],fk_enquiry_master__fk_company = ins_user.fk_company).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        #     if ins_details_exist:
                        #         ins_details_exist.update(vchr_enquiry_status = 'LOST')
                        #         lst_query_set = []
                        #         for data in ins_details_exist:
                        #             ins_follow_up = ComputersFollowup(
                        #             fk_computers = data
                        #             ,vchr_notes = 'Computer in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
                        #             ,vchr_enquiry_status = 'LOST'
                        #             ,int_status = 1
                        #             ,dbl_amount = 0.0
                        #             ,fk_user = ins_user
                        #             ,fk_updated = ins_user
                        #             ,dat_followup = dat_created
                        #             ,dat_updated = dat_created
                        #             )
                        #             lst_query_set.append(ins_follow_up)
                        #         if lst_query_set:
                        #             ComputersFollowup.objects.bulk_create(lst_query_set);
                        # ins_details_follow_up = ComputersFollowup.objects.create(
                        #     fk_computers = ins_details
                        #     ,vchr_notes = dct_computer['vchr_remarks']
                        #     ,vchr_enquiry_status = dct_computer.get('vchr_enquiry_status','NEW')
                        #     ,int_status = int_status
                        #     ,dbl_amount = float(dct_computer.get('dbl_estimated_amount','0.0'))
                        #     ,fk_user = ins_user
                        #     ,fk_updated = ins_user
                        #     ,dat_followup = dat_created
                        #     ,dat_updated = dat_created
                        # )
                # Tablet Save Section
                if bln_status.get('tabletNa'):
                    for dct_tablet in lst_tablet:

                        if not dct_tablet['dbl_estimated_amount']:
                            dct_tablet['dbl_estimated_amount'] = '0.0'

                        if not dct_tablet['intQty']:
                            dct_tablet['intQty'] = '0'

                        ins_details = NaEnquiryDetails(
                            fk_na_enquiry_master = ins_enquiry
                            ,vchr_product = 'TABLET'
                            ,vchr_brand = dct_tablet['strStockBrand'].strip().upper()
                            ,vchr_item = dct_tablet['strStockItem'].strip().upper()
                            # ,vchr_color = dct_tablet['vchr_color']
                            ,int_quantity = int(dct_tablet['intQty'])
                            ,vchr_remarks = dct_tablet['vchr_remarks'].strip()
                        )
                        ins_details.save()
                        # if ins_tablet and dct_tablet.get('vchr_enquiry_status','') == 'BOOKED':
                        #     ins_tablet_exist = TabletEnquiry.objects.filter(fk_enquiry_master__fk_customer = dct_customer['fk_customer_id']).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        #     if ins_tablet_exist:
                        #         ins_tablet_exist.update(vchr_enquiry_status = 'LOST')
                        #         lst_query_set = []
                        #         for data in ins_tablet_exist:
                        #             ins_follow_up = TabletFollowup(
                        #             fk_tablet = data
                        #             ,vchr_notes = 'Tablet in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
                        #             ,vchr_enquiry_status = 'LOST'
                        #             ,int_status = int_status
                        #             ,dbl_amount = '0.0'
                        #             ,fk_user = ins_user
                        #             ,fk_updated = ins_user
                        #             ,dat_followup = dat_created
                        #             ,dat_updated = dat_created
                        #             )
                        #             lst_query_set.append(ins_follow_up)
                        #         if lst_query_set:
                        #             TabletFollowup.objects.bulk_create(lst_query_set);
                        # ins_tablet_follow_up = TabletFollowup.objects.create(
                        #     fk_tablet = ins_tablet
                        #     ,vchr_notes = dct_tablet['vchr_remarks']
                        #     ,vchr_enquiry_status = dct_tablet.get('vchr_enquiry_status','NEW')
                        #     ,int_status = int_status
                        #     ,dbl_amount = float(dct_tablet.get('dbl_estimated_amount','0.0'))
                        #     ,fk_user = ins_user
                        #     ,fk_updated = ins_user
                        #     ,dat_followup = dat_created
                        #     ,dat_updated = dat_created
                        # )
                # Mobile Save Section
                if bln_status.get('mobileNa'):
                    for dct_mobile in lst_mobile:

                        if not dct_mobile['dbl_estimated_amount']:
                            dct_mobile['dbl_estimated_amount'] = '0.0'

                        if not dct_mobile['intQty']:
                            dct_mobile['intQty'] = '0'

                        ins_details = NaEnquiryDetails(
                            fk_na_enquiry_master = ins_enquiry
                            ,vchr_product = 'MOBILE'
                            ,vchr_brand = dct_mobile['strStockBrand'].strip().upper()
                            ,vchr_item = dct_mobile['strStockItem'].strip().upper()
                            ,vchr_color = dct_mobile['vchr_colour']
                            ,int_quantity = int(dct_mobile['intQty'])
                            ,vchr_remarks = dct_mobile['vchr_remarks'].strip()
                        )
                        ins_details.save()

                        # if ins_mobile and dct_mobile.get('vchr_enquiry_status','') == 'BOOKED':
                        #     ins_mobile_exist = MobileEnquiry.objects.filter(fk_enquiry_master__fk_customer = dct_customer['fk_customer_id']).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        #     if ins_mobile_exist:
                        #         ins_mobile_exist.update(vchr_enquiry_status = 'LOST')
                        #         lst_query_set = []
                        #         for data in ins_mobile_exist:
                        #             ins_follow_up = MobileFollowup(
                        #             fk_mobile = data
                        #             ,vchr_notes = 'Mobile in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
                        #             ,vchr_enquiry_status = 'LOST'
                        #             ,int_status = int_status
                        #             ,dbl_amount = '0.0'
                        #             ,fk_user = ins_user
                        #             ,fk_updated = ins_user
                        #             ,dat_followup = dat_created
                        #             ,dat_updated = dat_created
                        #             )
                        #             lst_query_set.append(ins_follow_up)
                        #         if lst_query_set:
                        #             MobileFollowup.objects.bulk_create(lst_query_set);
                        # ins_mobile_follow_up = MobileFollowup.objects.create(
                        #     fk_mobile = ins_mobile
                        #     ,vchr_notes = dct_mobile['vchr_remarks']
                        #     ,vchr_enquiry_status = dct_mobile.get('vchr_enquiry_status','NEW')
                        #     ,int_status = int_status
                        #     ,dbl_amount = float(dct_mobile.get('dbl_estimated_amount','0.0'))
                        #     ,fk_user = ins_user
                        #     ,fk_updated = ins_user
                        #     ,dat_followup = dat_created
                        #     ,dat_updated = dat_created
                        # )
                # Accessories Save Section
                if bln_status.get('accessoriesNa'):
                    for dct_accessories in lst_accessories:

                        if not dct_accessories['dbl_estimated_amount']:
                            dct_accessories['dbl_estimated_amount'] = '0.0'

                        if not dct_accessories['intQty']:
                            dct_accessories['intQty'] = '0'

                        ins_details = NaEnquiryDetails(
                            fk_na_enquiry_master = ins_enquiry
                            ,vchr_product = 'ACCESSORIES'
                            ,vchr_brand = dct_accessories['strStockBrand'].strip().upper()
                            ,vchr_item = dct_accessories['strStockItem'].strip().upper()
                            # ,vchr_color = dct_accessories['vchr_color']
                            ,int_quantity = int(dct_accessories['intQty'])
                            ,vchr_remarks = dct_accessories['vchr_remarks'].strip()
                        )
                        ins_details.save()
                        # if ins_accessories and dct_accessories.get('vchr_enquiry_status','') == 'BOOKED':
                        #     ins_accessories_exist = AccessoriesEnquiry.objects.filter(fk_enquiry_master__fk_customer = dct_customer['fk_customer_id']).exclude(vchr_enquiry_status = 'BOOKED').exclude(vchr_enquiry_status = 'UNQUALIFIED')
                        #     if ins_accessories_exist:
                        #         ins_accessories_exist.update(vchr_enquiry_status = 'LOST')
                        #         lst_query_set = []
                        #         for data in ins_accessories_exist:
                        #             ins_follow_up = AccessoriesFollowup(
                        #             fk_accessories = data
                        #             ,vchr_notes = 'Accessories in ' + data.fk_enquiry_master.vchr_enquiry_num + ' is booked'
                        #             ,vchr_enquiry_status = 'LOST'
                        #             ,int_status = int_status
                        #             ,dbl_amount = '0.0'
                        #             ,fk_user = ins_user
                        #             ,fk_updated = ins_user
                        #             ,dat_followup = dat_created
                        #             ,dat_updated = dat_created
                        #             )
                        #             lst_query_set.append(ins_follow_up)
                        #         if lst_query_set:
                        #             AccessoriesFollowup.objects.bulk_create(lst_query_set);
                        # ins_accessories_follow_up = AccessoriesFollowup.objects.create(
                        #     fk_accessories = ins_accessories
                        #     ,vchr_notes = dct_accessories['vchr_remarks']
                        #     ,vchr_enquiry_status = dct_accessories.get('vchr_enquiry_status','NEW')
                        #     ,int_status = int_status
                        #     ,dbl_amount = float(dct_accessories.get('dbl_estimated_amount','0.0'))
                        #     ,fk_user = ins_user
                        #     ,fk_updated = ins_user
                        #     ,dat_followup = dat_created
                        #     ,dat_updated = dat_created
                        # )
                # dct_cust_rating = dct_rating.get('customerRating')
                vchr_feedback = dct_cust_rating['vchr_feedback']
                dbl_rating = dct_cust_rating['dbl_rating']
                fk_customer = dct_cust_rating['fk_customer_id']
                fk_user = dct_cust_rating['fk_user_id']
                ins_rating =  CustomerRating(
                    vchr_feedback = vchr_feedback
                    ,dbl_rating = dbl_rating
                    ,fk_customer = CustomerModel.objects.get(id= fk_customer)
                    , fk_user = UserModel.objects.get(user_ptr_id = fk_user)
                )
                ins_rating.save()
                # str_hash = hash_enquiry(ins_enquiry)
                # EnquiryMaster.objects.filter(chr_doc_status='N',pk_bint_id = ins_enquiry.pk_bint_id).update(vchr_hash = str_hash)
                # enquiry_print(str_enquiry_no,request,ins_user)
                return Response({'status':'0','result':str_enquiry_no,'enqId':ins_enquiry.pk_bint_id})
            else:
                return Response({'status':'1'})
        except Exception as e:
            ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
            str_code = ins_document[0].vchr_short_code
            int_doc_num = ins_document[0].int_number
            int_update_num = int_doc_num - 1
            str_number = str(int_doc_num).zfill(4)
            str_enquiry_no = str_code + '-' + str_number
            ins_document.update(int_number = int_update_num)
            EnquiryMaster.objects.filter(chr_doc_status='N',vchr_enquiry_num = str_enquiry_no).update(chr_doc_status='D')
            return Response({'status':'1','data':str(e)})
class PendingEnquiryList(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            int_company_id = int(request.data.get('company_id'))
            if not int_company_id:
                return Response({'status':'1','data':["No company found"]})
            else:
                fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ).date()
                todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ).date()
                # todate = todate + timedelta(days = 1)
                int_cust_id=request.data.get('custId')
                int_branch_id=request.data.get('branchId')
                session = Session()
                lst_enquiry_data = []

                rst_enquiry = session.query(NaEnquiryMasterSA.pk_bint_id,NaEnquiryMasterSA.dat_created_at,NaEnquiryMasterSA.vchr_enquiry_num,\
                                        NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item,BranchSA.vchr_name,BranchSA.pk_bint_id,CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                        CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
                                        .filter(and_( NaEnquiryMasterSA.fk_company_id == int_company_id,cast(NaEnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(NaEnquiryMasterSA.dat_created_at,Date) <= todate))\
                                        .join(NaEnquiryDetailsSA,and_(NaEnquiryDetailsSA.fk_na_enquiry_master_id == NaEnquiryMasterSA.pk_bint_id))\
                                        .join(CustomerSA,NaEnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, NaEnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == NaEnquiryMasterSA.fk_branch_id)\
                                        .group_by(NaEnquiryMasterSA.pk_bint_id,NaEnquiryMasterSA.vchr_enquiry_num,NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item, CustomerSA.cust_fname,\
                                        NaEnquiryMasterSA.dat_created_at,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name,BranchSA.vchr_name,BranchSA.pk_bint_id)

                                                    # , EnquiryMasterSA.int_company_id == int_company_id )\
                                        # .filter(EnquiryMasterSA.dat_created_at >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end, EnquiryMasterSA.fk_company_id == int_company_id )\

                # if dat_start:
                #         rst_enquiry = rst_enquiry.filter(NaEnquiryMasterSA.dat_created_at >= dat_start)
                # if dat_end:
                #     rst_enquiry = rst_enquiry.filter(cast(NaEnquiryMasterSA.dat_created_at,Date) <= dat_end)
                # if int_cust_id:
                #     rst_enquiry = rst_enquiry.filter(NaEnquiryMasterSA.fk_customer_id == int_cust_id)
                # # import pdb; pdb.set_trace()
                # if int_branch_id:
                #     rst_enquiry = rst_enquiry.filter(NaEnquiryMasterSA.fk_branch_id == int_branch_id)

                """Permission wise filter for data"""
                if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    rst_enquiry = rst_enquiry.filter(BranchSA.pk_bint_id == request.user.userdetails.fk_branch_id)
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    rst_enquiry = rst_enquiry.filter(BranchSA.pk_bint_id.in_(lst_branch))
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})
                if request.data.get("branch_id"):
                    rst_enquiry = rst_enquiry.filter(BranchSA.pk_bint_id == int(request.data.get("branch_id")))
                rst_enquiry = rst_enquiry.order_by(desc(NaEnquiryMasterSA.dat_created_at))
                # for a in rst_enquiry.order_by(EnquiryMasterSA.dat_created_at.desc()).all() : a.dat_created_at
                dct_enquiries = {}
                if not rst_enquiry.all():
                    session.close()
                    return Response({'status':'failled','data':'No Data'})
                dct_data={}
                dct_data['product_all']={}
                dct_data['brand_all']={}
                dct_data['item_all']={}
                dct_data['branch_all']={}
                dct_data['product_brand']={}
                dct_data['product_item']={}
                dct_data['product_branch']={}
                dct_data['product_brand_item']={}
                dct_data['product_brand_branch']={}
                dct_data['product_brand_item_branch']={}

                for ins_data in rst_enquiry.all():

                    if ins_data.vchr_enquiry_num == dct_enquiries.get('enquiry'):
                        dct_enquiries['services'].append(ins_data.vchr_product)
                        dct_enquiries['brands'].append(ins_data.vchr_brand)
                        dct_enquiries['items'].append(ins_data.vchr_item)
                    else:
                        if dct_enquiries == {}:
                            dct_enquiries = {'enquiry_id':ins_data.pk_bint_id,'enquiry':ins_data.vchr_enquiry_num,'date':ins_data.dat_created_at,'customer_name':ins_data.customer_first_name+' '+ins_data.customer_last_name,'customer_contact':ins_data.customer_mobile,'staff_name':ins_data.staff_first_name+' '+ins_data.staff_last_name,'services':[ins_data.vchr_product],'brands':[ins_data.vchr_brand],'items':[ins_data.vchr_item]}
                        else:
                            lst_enquiry_data.append(dct_enquiries)
                            dct_enquiries = {'enquiry_id':ins_data.pk_bint_id,'enquiry':ins_data.vchr_enquiry_num,'date':ins_data.dat_created_at,'customer_name':ins_data.customer_first_name+' '+ins_data.customer_last_name,'customer_contact':ins_data.customer_mobile,'staff_name':ins_data.staff_first_name+' '+ins_data.staff_last_name,'services':[ins_data.vchr_product],'brands':[ins_data.vchr_brand],'items':[ins_data.vchr_item]}



                    if ins_data.vchr_product not in dct_data['product_all']:
                        dct_data['product_all'][ins_data.vchr_product]=1

                        dct_data['product_brand'][ins_data.vchr_product]={}
                        dct_data['product_item'][ins_data.vchr_product]={}
                        dct_data['product_branch'][ins_data.vchr_product]={}
                        dct_data['product_brand'][ins_data.vchr_product][ins_data.vchr_brand]=1
                        dct_data['product_item'][ins_data.vchr_product][ins_data.vchr_item]=1
                        dct_data['product_branch'][ins_data.vchr_product][ins_data.vchr_name]=1

                        dct_data['product_brand_item'][ins_data.vchr_product]={}
                        dct_data['product_brand_branch'][ins_data.vchr_product]={}
                        dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand]={}
                        dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand]={}
                        dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]=1
                        dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_name]=1

                        dct_data['product_brand_item_branch'][ins_data.vchr_product]={}
                        dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand]={}
                        dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]={}
                        dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item][ins_data.vchr_name]=1


                    else:
                        dct_data['product_all'][ins_data.vchr_product]+=1
                        if ins_data.vchr_brand not in dct_data['product_brand'][ins_data.vchr_product]:
                            dct_data['product_brand'][ins_data.vchr_product][ins_data.vchr_brand]=1
                        else:
                            dct_data['product_brand'][ins_data.vchr_product][ins_data.vchr_brand]+=1

                        if ins_data.vchr_item not in dct_data['product_item'][ins_data.vchr_product]:
                            dct_data['product_item'][ins_data.vchr_product][ins_data.vchr_item]=1
                        else:
                            dct_data['product_item'][ins_data.vchr_product][ins_data.vchr_item]+=1
                        if ins_data.vchr_name not in dct_data['product_branch'][ins_data.vchr_product]:
                            dct_data['product_branch'][ins_data.vchr_product][ins_data.vchr_name]=1
                        else:
                            dct_data['product_branch'][ins_data.vchr_product][ins_data.vchr_name]+=1
                        if ins_data.vchr_brand not in dct_data['product_brand_item'][ins_data.vchr_product]:
                            dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand]={}
                            dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand]={}
                            dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]=1
                            dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_name]=1
                        else:
                            if ins_data.vchr_item not in dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand]:
                                dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]=1
                            else:
                                dct_data['product_brand_item'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]+=1
                            if ins_data.vchr_name not in dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand]:
                                dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_name]=1
                            else:
                                dct_data['product_brand_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_name]+=1

                        if ins_data.vchr_brand not in dct_data['product_brand_item_branch'][ins_data.vchr_product]:
                            dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand]={}
                            dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]={}
                            dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item][ins_data.vchr_name]=1
                        else:
                            if ins_data.vchr_item not in dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand]:
                                dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]={}
                                dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item][ins_data.vchr_name]=1
                            else:
                                if ins_data.vchr_name not in dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item]:
                                    dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item][ins_data.vchr_name]=1
                                else:
                                    dct_data['product_brand_item_branch'][ins_data.vchr_product][ins_data.vchr_brand][ins_data.vchr_item][ins_data.vchr_name]+=1



                    if ins_data.vchr_brand not in dct_data['brand_all']:
                        dct_data['brand_all'][ins_data.vchr_brand]=1
                    else:
                        dct_data['brand_all'][ins_data.vchr_brand]+=1
                    if ins_data.vchr_item not in dct_data['item_all']:
                        dct_data['item_all'][ins_data.vchr_item]=1
                    else:
                        dct_data['item_all'][ins_data.vchr_item]+=1
                    if ins_data.vchr_name not in dct_data['branch_all']:
                        dct_data['branch_all'][ins_data.vchr_name]=1
                    else:
                        dct_data['branch_all'][ins_data.vchr_name]+=1
                lst_enquiry_data.append(dct_enquiries)
                dct_data['table_data']=lst_enquiry_data


                dct_data['brand_all']=paginate_data(dct_data['brand_all'],10)
                dct_data['item_all']=paginate_data(dct_data['item_all'],10)
                dct_data['branch_all']=paginate_data(dct_data['branch_all'],10)
                for key in dct_data['product_brand']:
                        dct_data['product_brand'][key]=paginate_data(dct_data['product_brand'][key],10)
                for key in dct_data['product_item']:
                        dct_data['product_item'][key]=paginate_data(dct_data['product_item'][key],10)
                for key in dct_data['product_branch']:
                        dct_data['product_branch'][key]=paginate_data(dct_data['product_branch'][key],10)
                for key in dct_data['product_brand_item']:
                    for key1 in dct_data['product_brand_item'][key]:
                        dct_data['product_brand_item'][key][key1]=paginate_data(dct_data['product_brand_item'][key][key1],10)
                for key in dct_data['product_brand_branch']:
                    for key1 in dct_data['product_brand_branch'][key]:
                        dct_data['product_brand_branch'][key][key1]=paginate_data(dct_data['product_brand_branch'][key][key1],10)
                # import pdb;pdb.set_trace()
                for key in dct_data['product_brand_item_branch']:
                    for key1 in dct_data['product_brand_item_branch'][key]:
                        for key2 in dct_data['product_brand_item_branch'][key][key1]:
                            dct_data['product_brand_item_branch'][key][key1][key2]=paginate_data(dct_data['product_brand_item_branch'][key][key1][key2],10)



                #             dct_enquiries = {'enquiry':ins_data.vchr_enquiry_num,'date':dct_table_data._asdict()['dat_created_at'],'customer_name':dct_table_data._asdict()['customer_first_name']+' '+dct_table_data._asdict()['customer_last_name'],'customer_contact':dct_table_data._asdict()['customer_mobile'],'staff_name':dct_table_data._asdict()['staff_first_name']+' '+dct_table_data._asdict()['staff_last_name'],'services':[dct_table_data._asdict()['vchr_brand']]}
                session.close()
                return Response({'status':'success','data':dct_data,})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            session.close()
            return Response({'status':'failed','data':[str(e)]})

class EnquiryList(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            int_company_id = request.user.userdetails.fk_company_id
            # int_company_id=1
            if not int_company_id:
                return Response({'status':'1','data':["No company found"]})
            else:
                fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ).date()
                todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ).date()
                # fromdate =  datetime.strptime('2018-01-01', '%Y-%m-%d' ).date()
                # todate =  datetime.strptime('2018-11-11', '%Y-%m-%d' ).date()
                # todate = todate + timedelta(days = 1)
                int_cust_id=request.data.get('custId')
                int_branch_id=request.data.get('branchId')
                session = Session()
                lst_enquiry_data = []

                rst_enquiry = session.query(NaEnquiryMasterSA.pk_bint_id.label('master_id'),NaEnquiryMasterSA.dat_created_at,NaEnquiryMasterSA.vchr_enquiry_num,\
                                        NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item,BranchSA.vchr_name,BranchSA.pk_bint_id,(CustomerSA.cust_fname+' '+CustomerSA.cust_lname).label('customer_fullname'),\
                                        CustomerSA.cust_mobile.label('customer_mobile'),(AuthUserSA.first_name+' '+AuthUserSA.last_name).label("staff_fullname"))\
                                        .filter(and_( NaEnquiryMasterSA.fk_company_id == int_company_id,cast(NaEnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(NaEnquiryMasterSA.dat_created_at,Date) <= todate))\
                                        .join(NaEnquiryDetailsSA,and_(NaEnquiryDetailsSA.fk_na_enquiry_master_id == NaEnquiryMasterSA.pk_bint_id))\
                                        .join(CustomerSA,NaEnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, NaEnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == NaEnquiryMasterSA.fk_branch_id)\
                                        .group_by(NaEnquiryMasterSA.pk_bint_id,NaEnquiryMasterSA.vchr_enquiry_num,NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item, CustomerSA.cust_fname,\
                                        NaEnquiryMasterSA.dat_created_at,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name,BranchSA.vchr_name,BranchSA.pk_bint_id)\
                                        .order_by(desc(NaEnquiryMasterSA.dat_created_at))
                lst_data=[]
                tmp_dct={}
                ####permision wise
                if request.user.userdetails.fk_group.vchr_name.upper()=='ADMIN':
                    pass
                elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                    rst_enquiry = rst_enquiry.filter(BranchSA.pk_bint_id == request.user.userdetails.fk_branch_id)
                elif request.user.userdetails.int_area_id:
                    lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                    rst_enquiry = rst_enquiry.filter(BranchSA.pk_bint_id.in_(lst_branch))
                elif request.user.userdetails.fk_group.vchr_name.upper()=='STAFF':
                    rst_enquiry =rst_enquiry.filter(NaEnquiryMasterSA.fk_branch_id== request.user.userdetails.fk_branch_id,NaEnquiryMasterSA.fk_assigned_id==request.user.id)
                else:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})
                if not rst_enquiry.all():
                    session.close()
                    return Response({'status':'success','data':lst_data})
                dct_tmp={'id':rst_enquiry.first().master_id,'date':rst_enquiry.first().dat_created_at,'customer_name':rst_enquiry.first().customer_fullname,'service':[rst_enquiry.first().vchr_product],'staff_name':rst_enquiry.first().staff_fullname,'enquiry_number':rst_enquiry.first().vchr_enquiry_num}
                for ins_enquiry in rst_enquiry.all()[1:]:
                    if ins_enquiry.master_id == dct_tmp['id']:
                        dct_tmp['service'].append(ins_enquiry.vchr_product)
                    else:
                        lst_data.append(dct_tmp)
                        dct_tmp={}
                        dct_tmp={'id':ins_enquiry.master_id,'date':ins_enquiry.dat_created_at,'customer_name':ins_enquiry.customer_fullname,'service':[ins_enquiry.vchr_product],'staff_name':ins_enquiry.staff_fullname,'enquiry_number':ins_enquiry.vchr_enquiry_num}
                lst_data.append(dct_tmp)
                session.close()
                return Response({'status':'success','data':lst_data})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            session.close()
            return Response({'status':'failed','data':[str(e)]})

class EnquiryView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            # int_company_id = int(request.data.get('company_id'))
            # int_company_id=1
            if not request.data.get('Id'):
                return Response({'status':'failed','data':["No record found"]})
            else:
                # fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ).date()
                # todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ).date()
                # fromdate =  datetime.strptime('2018-01-01', '%Y-%m-%d' ).date()
                # todate =  datetime.strptime('2018-11-11', '%Y-%m-%d' ).date()
                # todate = todate + timedelta(days = 1)
                # int_cust_id=request.data.get('custId')
                int_enquiry_id=request.data.get('Id')
                session = Session()
                lst_enquiry_data = []

                rst_enquiry = session.query(NaEnquiryMasterSA.pk_bint_id.label('master_id'),NaEnquiryMasterSA.dat_created_at,NaEnquiryMasterSA.vchr_enquiry_num,SourceSA.vchr_source_name.label('source_name'),\
                                        NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item,BranchSA.vchr_name,BranchSA.pk_bint_id,(CustomerSA.cust_fname+' '+CustomerSA.cust_lname).label('customer_fullname'),CustomerSA.cust_contactsrc.label('contact_source'),\
                                        CustomerSA.cust_mobile.label('customer_mobile'),CustomerSA.cust_email.label('customer_email'),(AuthUserSA.first_name+' '+AuthUserSA.last_name).label("staff_fullname"),NaEnquiryDetailsSA.int_quantity,NaEnquiryDetailsSA.vchr_remarks)\
                                        .filter(NaEnquiryMasterSA.pk_bint_id==int_enquiry_id)\
                                        .join(NaEnquiryDetailsSA,and_(NaEnquiryDetailsSA.fk_na_enquiry_master_id == NaEnquiryMasterSA.pk_bint_id))\
                                        .join(CustomerSA,NaEnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                        .join(AuthUserSA, NaEnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                        .join(BranchSA,BranchSA.pk_bint_id == NaEnquiryMasterSA.fk_branch_id)\
                                        .join(SourceSA,SourceSA.pk_bint_id == NaEnquiryMasterSA.fk_source_id)\
                                        .group_by(NaEnquiryMasterSA.pk_bint_id,NaEnquiryMasterSA.vchr_enquiry_num,NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item, CustomerSA.cust_fname,\
                                        NaEnquiryMasterSA.dat_created_at,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name,BranchSA.vchr_name,BranchSA.pk_bint_id,CustomerSA.cust_email,NaEnquiryDetailsSA.int_quantity,NaEnquiryDetailsSA.vchr_remarks,SourceSA.vchr_source_name,CustomerSA.cust_contactsrc)\
                                        .order_by(NaEnquiryMasterSA.pk_bint_id)

                dct_customer_data={'id':rst_enquiry.first().master_id,'date':rst_enquiry.first().dat_created_at,'customer_name':rst_enquiry.first().customer_fullname,'staff_name':rst_enquiry.first().staff_fullname,'enquiry_number':rst_enquiry.first().vchr_enquiry_num,'customer_email':rst_enquiry.first().customer_email,'customer_mobile':rst_enquiry.first().customer_mobile,'branch_name':rst_enquiry.first().vchr_name,'source_name':rst_enquiry.first().source_name,'contact_source':rst_enquiry.first().contact_source}
                dct_service_data={}
                dct_service_data[rst_enquiry.first().vchr_product]=[{'brand':rst_enquiry.first().vchr_brand,'item':rst_enquiry.first().vchr_item,'int_quantity':rst_enquiry.first().int_quantity,'vchr_remarks':rst_enquiry.first().vchr_remarks}]
                for ins_enquiry in rst_enquiry.all()[1:]:
                    if ins_enquiry.vchr_product in dct_service_data:
                        dct_temp={'brand':ins_enquiry.vchr_brand,'item':ins_enquiry.vchr_item,'int_quantity':ins_enquiry.int_quantity,'vchr_remarks':ins_enquiry.vchr_remarks}
                        dct_service_data[ins_enquiry.vchr_product].append(dct_temp)
                    else:
                        dct_service_data[ins_enquiry.vchr_product]=[{'brand':ins_enquiry.vchr_brand,'item':ins_enquiry.vchr_item,'int_quantity':ins_enquiry.int_quantity,'vchr_remarks':ins_enquiry.vchr_remarks}]
                session.close()
                return Response({'status':'success','customer_data':dct_customer_data,'service_data':dct_service_data})
        except Exception as e:
            # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            session.close()
            return Response({'status':'failed','data':[str(e)]})
def paginate_data(dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    for key in dct_data:
        if int_count not in dct_paged:
            dct_paged[int_count]={}
            dct_paged[int_count][key]=dct_data[key]
        elif len(dct_paged[int_count]) < int_page_legth:
            dct_paged[int_count][key]= dct_data[key]
        else:
            int_count += 1
            dct_paged[int_count] ={}
            dct_paged[int_count][key] = dct_data[key]
    return dct_paged
