from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated,AllowAny
from supplier.models import Supplier,ContactPersonSupplier,AddressSupplier,SupplierLog
from category.models import OtherCategory
from rest_framework.response import Response
from rest_framework.views import APIView
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from aldjemy.core import get_engine
from django.db.models import Q
from states.models import States
import json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import case, literal_column
from sqlalchemy import desc
from pytz import timezone

from POS import ins_logger
import sys, os

from datetime import datetime

from item_category.models import TaxMaster
# from dealer.models import OtherCategory
# localtz = timezone('Asia/Kolkata')
from django.db import transaction


SupplierSA=Supplier.sa
AddressSupplierSA=AddressSupplier.sa
ContactPersonSupplierSA=ContactPersonSupplier.sa
OtherCategorySA=OtherCategory.sa
TaxMasterSA=TaxMaster.sa
StatesSA=States.sa
# Create your views here.
def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()


class AddSupplier(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
            '''add'''
            try:
                with transaction.atomic():

                        lstaddress  =  request.data['address1']
                        lstcontact  = request.data['contact_person']
                        str_supplier_name  = request.data.get('vchr_supplier_name')
                        dat_supplier_from=datetime.strptime(request.data.get('int_supplierFrom'),'%d-%m-%Y')
                        str_supplier_code  =  request.data.get('vchr_supplier_code')
                        int_credit_days  =  request.data.get('intCreditDays')
                        bint_credit_limit  =  request.data.get('int_credit_limit')
                        int_po_expiry_days  =  request.data.get('int_poexpiry_days')
                        vchr_tin_no  =  request.data.get('intTinNumber')
                        vchr_cst_no  =  request.data.get('intCstNumber')
                        str_gstin  =  request.data.get('intGstNumber')
                        str_gstin_status  =  request.data.get('strGstStatus')
                        fk_supplier_category = request.data.get('strSupplierCategory')
                        # fk_supplier_tax_class = request.data.get('fk_supplier_tax_class')
                        str_account_group = request.data.get('strAccGroup')
                        str_bank_account =request.data.get('strBankAccount')
                        str_pan_no = request.data.get('strPanNumber')
                        str_pan_status = request.data.get('strPanStatus')
                        fk_tax_class = request.data.get('strSupplierTaxClass')
                        dct_test={}
                        str_exists=""
                        lst_supplier=list(Supplier.objects.filter(Q(vchr_pan_no=str_pan_no) | Q(vchr_code=str_supplier_code) | Q(vchr_tin_no=vchr_tin_no) | Q(vchr_bank_account=str_bank_account) | Q(vchr_gstin =str_gstin) | Q(vchr_cst_no=vchr_cst_no),is_act_del__in=[1,2]).values('vchr_pan_no','vchr_code','vchr_tin_no','vchr_bank_account','vchr_gstin','vchr_cst_no'))
                        if lst_supplier:
                            for i in lst_supplier:

                                if str_pan_no in i.values() and 'pan number,' not in dct_test:
                                        dct_test['pan number,']=None
                                        str_exists=str_exists+" pan number,"
                                if str_supplier_code in i.values() and 'supplier code,' not in dct_test:
                                        dct_test['supplier code,']=None
                                        str_exists=str_exists+" supplier code,"
                                if vchr_tin_no in i.values() and 'tin number,' not in dct_test:
                                        dct_test['tin number,']=None
                                        str_exists=str_exists+" tin number,"
                                if str_bank_account in i.values() and 'bank account number,' not in dct_test:
                                                dct_test['bank account number,']=None
                                                str_exists=str_exists+" bank account number,"
                                if str_gstin in i.values() and "gst number," not in dct_test:
                                                dct_test['gst number,']=None
                                                str_exists=str_exists+" gst number,"
                                if vchr_cst_no in i.values() and "cst number," not in dct_test:
                                                dct_test["cst number,"]=None
                                                str_exists=str_exists+" cst number,"
                            str_exists=str_exists.title()
                            str_exists=str_exists+" these fields(or field) already exists"

                            return Response({'status':0,'reason':str_exists})
                        else:
                            # import pdb;
                            #
                            # pdb.set_trace()

                            inst=Supplier.objects.create(vchr_name = str_supplier_name,
                                                    dat_from = dat_supplier_from,
                                                    vchr_code = str_supplier_code ,
                                                    int_credit_days = int_credit_days,
                                                    bint_credit_limit = bint_credit_limit,
                                                    int_po_expiry_days = int_po_expiry_days,
                                                    vchr_tin_no = vchr_tin_no,
                                                    vchr_cst_no=vchr_cst_no,
                                                    vchr_gstin = str_gstin,
                                                    vchr_gstin_status = str_gstin_status,
                                                    fk_category_id = fk_supplier_category,
                                                    vchr_account_group = str_account_group,
                                                    vchr_bank_account = str_bank_account,
                                                    vchr_pan_no =str_pan_no,
                                                    vchr_pan_status =str_pan_status,
                                                    is_act_del=0,
                                                    fk_created_id=request.user.id,
                                                    dat_created=datetime.now(),
                                                    fk_tax_class_id=fk_tax_class,

                                                    )
                        #Iterating through dictionary received from front end
                            for dct_sub in range(len(lstaddress)):
                                #giving front end data to address model one by one
                                    ins_addr = AddressSupplier(vchr_address = lstaddress[dct_sub]['strAddress'],
                                                               vchr_email = lstaddress[dct_sub]['strEmail'],
                                                               bint_phone_no  = lstaddress[dct_sub]['intPhone'],
                                                               int_pin_code = lstaddress[dct_sub]['strPinCode'],
                                                               fk_states_id = lstaddress[dct_sub]['fk_states'],
                                                               fk_supplier = inst,
                                                               bln_status = True,
                                                               bln_primary = lstaddress[dct_sub]['strMainAddr'])
                                    ins_addr.save()
                            for dct_sub in range(len(lstcontact)):


                                    ins_cont  =  ContactPersonSupplier(
                                                                vchr_name = lstcontact[dct_sub]['strName'],
                                                                vchr_designation = lstcontact[dct_sub]['strDesignation'],
                                                                vchr_department = lstcontact[dct_sub]['strDepartment'],
                                                                vchr_office = lstcontact[dct_sub]['strOffice'],
                                                                bint_mobile_no = lstcontact[dct_sub]['intMobile1'],
                                                                bint_mobile_no2 = lstcontact[dct_sub]['intMobile2'] or None,
                                                                fk_supplier = inst,
                                                                bln_status = True)
                                    ins_cont.save()


                        return Response({'status':1})
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})



class ListSupplier(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:

            int_credit_days = request.data.get('intCreditDays')
            int_credit_limit = request.data.get('intCreditLimit')
            fk_category = request.data.get('strSupplierCategory')
            is_act_del = request.data.get('bln_active')
            rst_supplier=Supplier.objects.filter(Q(is_act_del=0) | Q(is_act_del=2)).values('pk_bint_id','vchr_name','dat_from','vchr_code','int_po_expiry_days','bint_credit_limit').order_by("-pk_bint_id")
            if is_act_del:
                rst_supplier = rst_supplier.filter(is_act_del = is_act_del)
            if int_credit_days:
                rst_supplier = rst_supplier.filter(int_credit_days = int_credit_days)
            if int_credit_limit:
                rst_supplier = rst_supplier.filter(bint_credit_limit = int_credit_limit)
            if fk_category:
                rst_supplier = rst_supplier.filter(fk_category_id = fk_category)
            return Response({'status':1,'list_supplier':list(rst_supplier)})
        except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                    return Response({'status':0,'reason':e})


class EditSupplier(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
            '''update'''
            try:
                with transaction.atomic():


                            lstaddress  =  request.data.get('address1')
                            lstcontact  = request.data['contact_person']
                            str_supplier_name = request.data.get('vchr_supplier_name')
                            dat_supplier_from=datetime.strptime(request.data.get('int_supplierFrom'),'%d-%m-%Y')
                            str_supplier_code = request.data.get('vchr_supplier_code')
                            int_credit_days = request.data.get('intCreditDays')
                            bint_credit_limit = request.data.get('int_credit_limit')
                            int_po_expiry_days  =  request.data.get('int_poexpiry_days')
                            vchr_tin_no = request.data.get('intTinNumber')
                            vchr_cst_no = request.data.get('intCstNumber')
                            str_gstin = request.data.get('intGstNumber')
                            str_gstin_status = request.data.get('strGstStatus')
                            fk_supplier_category = request.data.get('strSupplierCategory')
                            fk_supplier_tax_class = request.data.get('strSupplierTaxClass')
                            str_account_group = request.data.get('strAccGroup')
                            str_bank_account = request.data.get('strBankAccount')
                            str_pan_no = request.data.get('strPanNumber')
                            str_pan_status = request.data.get('strPanStatus')
                            int_supplier_id = request.data.get('pk_bint_id')
                            str_remarks=request.data.get('remarks')
                            is_act_del=int(request.data.get('blnactive'))

                            lst_avail_addr=AddressSupplier.objects.filter(fk_supplier_id = int_supplier_id).values_list('pk_bint_id',flat = True)
                            lst_avail_cp=ContactPersonSupplier.objects.filter(fk_supplier_id = int_supplier_id).values_list('pk_bint_id',flat = True)

                            lst_cur_addr = [x.get('Address_id') for x in lstaddress]
                            lst_cur_cp = [x.get('contact_id') for x in lstcontact]

                            lst_dlt_addr = list(set(lst_avail_addr)-set(lst_cur_addr))
                            lst_dlt_cp = list(set(lst_avail_cp)-set(lst_cur_cp))

                            if lst_dlt_addr:
                                AddressSupplier.objects.filter(fk_supplier_id = int_supplier_id,pk_bint_id__in = lst_dlt_addr).update(bln_status = False)

                            if lst_dlt_cp:
                                ContactPersonSupplier.objects.filter(fk_supplier_id = int_supplier_id,pk_bint_id__in = lst_dlt_cp).update(bln_status = False)

                            dct_test={}
                            str_exists=""
                            lst_supplier=list(Supplier.objects.filter(Q(vchr_pan_no=str_pan_no) | Q(vchr_code=str_supplier_code) | Q(vchr_tin_no=vchr_tin_no) | Q(vchr_bank_account=str_bank_account) | Q(vchr_gstin =str_gstin) | Q(vchr_cst_no=vchr_cst_no),is_act_del__in=[1,2]).values('vchr_pan_no','vchr_code','vchr_tin_no','vchr_bank_account','vchr_gstin','vchr_cst_no').exclude(pk_bint_id = int_supplier_id))
                            if lst_supplier:
                                for i in lst_supplier:

                                    if str_pan_no in i.values() and 'pan number,' not in dct_test:
                                            dct_test['pan number,']=None
                                            str_exists=str_exists+" pan number,"
                                    if str_supplier_code in i.values() and 'supplier code,' not in dct_test:
                                            dct_test['supplier code,']=None
                                            str_exists=str_exists+" supplier code,"
                                    if vchr_tin_no in i.values() and 'tin number,' not in dct_test:
                                            dct_test['tin number,']=None
                                            str_exists=str_exists+" tin number,"
                                    if str_bank_account in i.values() and 'bank account number,' not in dct_test:
                                                    dct_test['bank account number,']=None
                                                    str_exists=str_exists+" bank account number,"
                                    if str_gstin in i.values() and "gst number," not in dct_test:
                                                    dct_test['gst number,']=None
                                                    str_exists=str_exists+" gst number,"
                                    if vchr_cst_no in i.values() and "cst number," not in dct_test:
                                                    dct_test["cst number,"]=None
                                                    str_exists=str_exists+" cst number,"
                                str_exists=str_exists.title()
                                str_exists=str_exists+" these fields(or field) already exists"

                                return Response({'status':0,'reason':str_exists})

                            else:

                                if( is_act_del != Supplier.objects.filter(pk_bint_id=int_supplier_id).values_list('is_act_del',flat = True).first()):

                                    SupplierLog.objects.create(vchr_remarks=str_remarks,vchr_status=is_act_del,dat_created=datetime.now(),fk_supplier_id=int_supplier_id,fk_created_id=request.user.id)

                                Supplier.objects.filter(pk_bint_id=int_supplier_id).update(
                                                                        vchr_name = str_supplier_name,
                                                                        dat_from = dat_supplier_from,
                                                                        vchr_code = str_supplier_code ,
                                                                        int_credit_days = int_credit_days,
                                                                        bint_credit_limit = bint_credit_limit,
                                                                        int_po_expiry_days = int_po_expiry_days,
                                                                        vchr_tin_no = vchr_tin_no,
                                                                        vchr_gstin = str_gstin,
                                                                        vchr_gstin_status = str_gstin_status,
                                                                        fk_category_id = fk_supplier_category,
                                                                        fk_tax_class_id = fk_supplier_tax_class,
                                                                        vchr_account_group = str_account_group,
                                                                        vchr_bank_account = str_bank_account,
                                                                        vchr_pan_no =str_pan_no,
                                                                        vchr_pan_status =str_pan_status,
                                                                        fk_updated_id=request.user.id,
                                                                        dat_updated=datetime.now(),
                                                                        is_act_del=is_act_del,

                                                                                    )

                            for dct_sub in range(len(lstaddress)):
                                        if(lstaddress[dct_sub].get('Address_id')):
                                            inst=AddressSupplier.objects.filter(fk_supplier_id=int_supplier_id,pk_bint_id=lstaddress[dct_sub]['Address_id']).update(
                                                        vchr_address=lstaddress[dct_sub]['strAddress'],
                                                        vchr_email=lstaddress[dct_sub]['strEmail'],
                                                        bint_phone_no =lstaddress[dct_sub]['intPhone'],
                                                        int_pin_code=lstaddress[dct_sub]['strPinCode'],
                                                        fk_states_id = lstaddress[dct_sub]['fk_states'],
                                                        bln_primary = lstaddress[dct_sub]['bln_primary']
                                                        )
                                        else:
                                                inst=AddressSupplier.objects.create(
                                                            vchr_address=lstaddress[dct_sub]['strAddress'],
                                                            vchr_email=lstaddress[dct_sub]['strEmail'],
                                                            bint_phone_no =lstaddress[dct_sub]['intPhone'],
                                                            int_pin_code=lstaddress[dct_sub]['strPinCode'],
                                                            fk_states_id = lstaddress[dct_sub]['fk_states'],
                                                            fk_supplier_id=int_supplier_id,
                                                            bln_status = True,
                                                            bln_primary = lstaddress[dct_sub]['bln_primary']
                                                            )

                            for dct_sub in range(len(lstcontact)):
                                    if(lstcontact[dct_sub].get('contact_id')):

                                        inst=ContactPersonSupplier.objects.filter(fk_supplier_id=int_supplier_id,pk_bint_id=lstcontact[dct_sub]['contact_id']).update(
                                                        vchr_name = lstcontact[dct_sub]['strName'],
                                                        vchr_designation = lstcontact[dct_sub]['strDesignation'],
                                                        vchr_department = lstcontact[dct_sub]['strDepartment'],
                                                        vchr_office = lstcontact[dct_sub]['strOffice'],
                                                        bint_mobile_no = lstcontact[dct_sub]['intMobile1'],
                                                        bint_mobile_no2 = lstcontact[dct_sub]['intMobile2'] or None,

                                                                )
                                    else:
                                        inst=ContactPersonSupplier.objects.create(
                                                        vchr_name = lstcontact[dct_sub]['strName'],
                                                        vchr_designation = lstcontact[dct_sub]['strDesignation'],
                                                        vchr_department = lstcontact[dct_sub]['strDepartment'],
                                                        vchr_office = lstcontact[dct_sub]['strOffice'],
                                                        bint_mobile_no = lstcontact[dct_sub]['intMobile1'],
                                                        bint_mobile_no2 = lstcontact[dct_sub]['intMobile2'] or None,
                                                        fk_supplier_id=int_supplier_id,
                                                        bln_status = True

                                                                )
                            return Response({'status':1})
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})

# class ChangeSupplierStatus(APIView):
#         permission_classes=[AllowAny]
#
#         '''change supplier status '''
#         def post(self,request):
#             try:
#
#
#                 if(Supplier.filter(pk_bint_id=int_supplier_id)):
#
#
#                     return Response({'status':1,'message':'Successfully Updated'})
#             except Exception as e:
#                 exc_type, exc_obj, exc_tb = sys.exc_info()
#                 ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
#                 return Response({'status':0,'reason':e})
# class SupplierLog(APIView):
#         permission_classes=[AllowAny]
#         '''View'''
#         def get(self,request):
#             try:
#
#                     lst_log=list(SupplierLog.objects.values('pk_bint_id','vchr_remarks','vchr_status','dat_created','fk_created','fk_supplier').order_by("-dat_created"))
#                     dct_log={}
#                     for i in lst_log:
#                         dct_log[i[fk_supplier]]=i




class ViewSupplier(APIView):
        permission_classes=[AllowAny]
        '''View'''
        def get(self,request):
            try:

                # int_supplier_id = int(request.data.get("id"))
                int_supplier_id = request.GET.get('id')
                session=Session()
                # if(Supplier.objects.filter(pk_bint_id=int_supplier_id,is_act_del=1)):
                if Supplier.objects.filter(pk_bint_id=int_supplier_id):
                    rst_enquiry = session.query(SupplierSA.pk_bint_id.label("int_id_supplier"),SupplierSA.vchr_name.label("supplier_name"),SupplierSA.dat_from.label("dat_from"),\
                    SupplierSA.vchr_code.label("vchr_code"),SupplierSA.int_credit_days.label("int_credit_days"),SupplierSA.bint_credit_limit.label("bint_credit_limit"),SupplierSA.int_po_expiry_days.label("int_po_expiry_days")\
                    ,SupplierSA.vchr_tin_no.label("vchr_tin_no") ,SupplierSA.vchr_cst_no.label("vchr_cst_no"),SupplierSA.vchr_gstin.label("vchr_gstin") ,SupplierSA.vchr_gstin_status.label("vchr_gstin_status"),\
                    SupplierSA.fk_category_id.label("fk_category_id"),SupplierSA.fk_tax_class_id.label("fk_tax_class_id"),SupplierSA.vchr_account_group.label("vchr_account_group"),\
                    SupplierSA.vchr_bank_account.label("vchr_bank_account"),SupplierSA.vchr_pan_no.label("vchr_pan_no"),SupplierSA.vchr_pan_status.label("vchr_pan_status"),SupplierSA.is_act_del.label("is_act_del")\
                    ,OtherCategorySA.vchr_name.label("vchr_category_name"),StatesSA.vchr_name.label("strStates"),StatesSA.pk_bint_id.label("fk_states"),TaxMasterSA.vchr_name.label("vchr_tax_master_name"),AddressSupplierSA.pk_bint_id.label("Address_id"),AddressSupplierSA.vchr_address.label("vchr_address"),AddressSupplierSA.vchr_email.label("vchr_email"),AddressSupplierSA.bint_phone_no.label("bint_phone_no"),\
                    AddressSupplierSA.int_pin_code.label("int_pin_code"),AddressSupplierSA.bln_status.label("bln_addr_status"),AddressSupplierSA.bln_primary.label("bln_primary"),ContactPersonSupplierSA.pk_bint_id.label("contact_id"),ContactPersonSupplierSA.vchr_name.label("contact_name"),ContactPersonSupplierSA.vchr_designation.label("vchr_designation"),\
                    ContactPersonSupplierSA.vchr_department.label("vchr_department"),ContactPersonSupplierSA.vchr_office.label("vchr_office"),ContactPersonSupplierSA.bint_mobile_no.label("bint_mobile_no"),\
                    ContactPersonSupplierSA.bint_mobile_no2.label("bint_mobile_no2"),ContactPersonSupplierSA.bln_status.label("bln_cp_status")).filter(SupplierSA.pk_bint_id==int_supplier_id).\
                    outerjoin(AddressSupplierSA,SupplierSA.pk_bint_id==AddressSupplierSA.fk_supplier_id).\
                    outerjoin(ContactPersonSupplierSA,SupplierSA.pk_bint_id==ContactPersonSupplierSA.fk_supplier_id).\
                    outerjoin(OtherCategorySA,OtherCategorySA.pk_bint_id==SupplierSA.fk_category_id).\
                    outerjoin(TaxMasterSA,TaxMasterSA.pk_bint_id==SupplierSA.fk_tax_class_id).\
                    outerjoin(StatesSA,StatesSA.pk_bint_id==AddressSupplierSA.fk_states_id)
                    # import pdb;
                    # pdb.set_trace()

                    dct_enquiry ={}
                    for ins_enquiry in rst_enquiry.all():

                        if ins_enquiry.int_id_supplier not in dct_enquiry:
                            dct_enquiry[ins_enquiry.int_id_supplier] = {}
                            dct_enquiry[ins_enquiry.int_id_supplier]['supplier_name'] = ins_enquiry.supplier_name
                            dct_enquiry[ins_enquiry.int_id_supplier]['dat_from'] = str(ins_enquiry.dat_from).split(" ")[0]
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_code'] = ins_enquiry.vchr_code
                            dct_enquiry[ins_enquiry.int_id_supplier]['int_credit_days'] = ins_enquiry.int_credit_days
                            dct_enquiry[ins_enquiry.int_id_supplier]['bint_credit_limit'] = ins_enquiry.bint_credit_limit
                            dct_enquiry[ins_enquiry.int_id_supplier]['int_po_expiry_days'] = ins_enquiry.int_po_expiry_days
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_tin_no'] = ins_enquiry.vchr_tin_no
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_cst_no'] = ins_enquiry.vchr_cst_no
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_gstin'] = ins_enquiry.vchr_gstin
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_gstin_status'] = ins_enquiry.vchr_gstin_status
                            dct_enquiry[ins_enquiry.int_id_supplier]['fk_category_id'] = ins_enquiry.fk_category_id
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_account_group'] = ins_enquiry.vchr_account_group
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_bank_account'] = ins_enquiry.vchr_bank_account
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_pan_no'] = ins_enquiry.vchr_pan_no
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_pan_status'] = ins_enquiry.vchr_pan_status
                            dct_enquiry[ins_enquiry.int_id_supplier]['is_act_del'] = ins_enquiry.is_act_del
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_category_name'] = ins_enquiry.vchr_category_name
                            dct_enquiry[ins_enquiry.int_id_supplier]['vchr_tax_master_name']=ins_enquiry.vchr_tax_master_name
                            dct_enquiry[ins_enquiry.int_id_supplier]['fk_tax_class_id']=ins_enquiry.fk_tax_class_id


                            dct_address={}
                            dct_contact={}
                            dct_enquiry[ins_enquiry.int_id_supplier]['lst_address']=[]
                            dct_enquiry[ins_enquiry.int_id_supplier]['lst_contact']=[]
                        # import pdb;pdb.set_trace()

                        if ins_enquiry.Address_id not in dct_address:
                                dct_address[ins_enquiry.Address_id]={}
                                dct_address[ins_enquiry.Address_id]['Address_id']=ins_enquiry.Address_id
                                dct_address[ins_enquiry.Address_id]['strAddress']=ins_enquiry.vchr_address
                                dct_address[ins_enquiry.Address_id]['strEmail']=ins_enquiry.vchr_email
                                dct_address[ins_enquiry.Address_id]['intPhone']=ins_enquiry.bint_phone_no
                                dct_address[ins_enquiry.Address_id]['strPinCode']=ins_enquiry.int_pin_code
                                dct_address[ins_enquiry.Address_id]['strStates']=ins_enquiry.strStates
                                dct_address[ins_enquiry.Address_id]['fk_states']=ins_enquiry.fk_states
                                dct_address[ins_enquiry.Address_id]['bln_status']=ins_enquiry.bln_addr_status
                                dct_address[ins_enquiry.Address_id]['bln_primary']=ins_enquiry.bln_primary

                                if ins_enquiry.bln_addr_status==True:
                                 dct_enquiry[ins_enquiry.int_id_supplier]['lst_address'].append(dct_address[ins_enquiry.Address_id])
                                dct_address[ins_enquiry.Address_id]=None
                        if ins_enquiry.contact_id not in dct_contact:
                                dct_contact[ins_enquiry.contact_id]={}
                                dct_contact[ins_enquiry.contact_id]['contact_id']=ins_enquiry.contact_id
                                dct_contact[ins_enquiry.contact_id]['strName']=ins_enquiry.contact_name
                                dct_contact[ins_enquiry.contact_id]['strDesignation']=ins_enquiry.vchr_designation
                                dct_contact[ins_enquiry.contact_id]['strDepartment']=ins_enquiry.vchr_department
                                dct_contact[ins_enquiry.contact_id]['strOffice']=ins_enquiry.vchr_office
                                dct_contact[ins_enquiry.contact_id]['intMobile1']=ins_enquiry.bint_mobile_no
                                dct_contact[ins_enquiry.contact_id]['intMobile2']=ins_enquiry.bint_mobile_no2
                                dct_contact[ins_enquiry.contact_id]['bln_status']=ins_enquiry.bln_cp_status
                                if ins_enquiry.bln_cp_status==True:
                                    dct_enquiry[ins_enquiry.int_id_supplier]['lst_contact'].append(dct_contact[ins_enquiry.contact_id])
                                dct_contact[ins_enquiry.contact_id]=None
                    session.close()
                    return Response({'status':1,'lst_userdetailsview':dct_enquiry})

                else:
                        session.close()
                        return Response({'status':0,'reason':"User deleted or doesn't exist"})

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                return Response({'status':0,'reason':e})


class CategoryTypeahead(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:


                lst_category = []

                ins_category = OtherCategory.objects.filter(int_status=2).values('pk_bint_id','vchr_name')
                if ins_category:
                    for itr_item in ins_category:
                        dct_category = {}

                        dct_category['categoryname'] = itr_item['vchr_name'].capitalize()
                        dct_category['id'] = itr_item['pk_bint_id']
                        lst_category.append(dct_category)
                return Response({'status':1,'data':lst_category})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})


class TaxclassTypeahead(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:


                lst_tax_class = []

                ins_tax_class = TaxMaster.objects.values('pk_bint_id','vchr_name')
                if ins_tax_class:
                    for itr_item in ins_tax_class:
                        dct_tax_class = {}

                        dct_tax_class['taxclassname'] = itr_item['vchr_name'].capitalize()
                        dct_tax_class['id'] = itr_item['pk_bint_id']
                        lst_tax_class.append(dct_tax_class)
                return Response({'status':1,'data':lst_tax_class})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'status':0,'data':str(e)})

class DeleteSupplier(APIView):
    permission_classes = [AllowAny]
    def patch(self,request):
        try:

            int_supplier_id = request.data.get('pk_bint_id')
            str_remarks=request.data.get('remarks')

            if Supplier.objects.filter(pk_bint_id=int_supplier_id):
                SupplierLog.objects.create(vchr_remarks=str_remarks,vchr_status=3,dat_created=datetime.now(),fk_supplier_id=int_supplier_id,fk_created_id=request.user.id)
                Supplier.objects.filter(pk_bint_id=int_supplier_id).update(is_act_del=-1)
                return Response({'status':1})
            else:
                return Response({'status':0,'reason':"Supplier doesn't exist"})
        except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                        return Response({'status':0,'data':str(e)})

class SupplierHistory(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:

            supplier_id=request.GET.get('id')
            LogList=list(SupplierLog.objects.filter(fk_supplier_id=supplier_id).values('vchr_remarks','vchr_status','dat_created','fk_supplier','fk_created').order_by("-dat_created"))
            return Response({'status':1,'lstsupplierlog':LogList})
        except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
                        return Response({'status':0,'data':str(e)})

class SupplierTypeHead(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()
            str_search_term = request.data.get('term',-1)
            lst_supplier = []
            if str_search_term != -1:
                ins_supplier = Supplier.objects.filter(Q(is_act_del=0,vchr_name__icontains=str_search_term) | Q(is_act_del=2,vchr_name__icontains=str_search_term)).values('pk_bint_id','vchr_name')
                if ins_supplier:
                    for itr_item in ins_supplier:
                        dct_supplier = {}
                        dct_supplier['name'] = itr_item['vchr_name']
                        dct_supplier['id'] = itr_item['pk_bint_id']
                        lst_supplier.append(dct_supplier)
                return Response({'status':1,'data':lst_supplier})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id),'details':'line no: ' + str(exc_tb.tb_lineno)})
            return Response({'result':0,'reason':e})
