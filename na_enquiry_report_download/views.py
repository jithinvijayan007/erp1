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
from pdfGenerate import generate_pdf
from generateExcel import generate_excel
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

class NAReportDownload(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            int_company_id = int(request.data.get('company_id'))
            if not int_company_id:
                return Response({'status':'1','data':["No company found"]})
            else:
                session = Session()
                fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' ).date()
                todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' ).date()
                # todate = todate + timedelta(days = 1)
                int_cust_id=request.data.get('custId')
                int_branch_id=request.data.get('branchId')
                lst_enquiry_data = []
                # import pdb; pdb.set_trace()
                rst_enquiry = session.query(NaEnquiryMasterSA.pk_bint_id,func.to_char(NaEnquiryMasterSA.dat_created_at,'dd-mm-YYYY').label('dat_created_at'),NaEnquiryMasterSA.vchr_enquiry_num,\
                                            NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item,BranchSA.vchr_name,BranchSA.pk_bint_id,CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                            CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
                                            .filter(and_( EnquiryMasterSA.fk_company_id == int_company_id,NaEnquiryMasterSA.dat_created_at >= fromdate,NaEnquiryMasterSA.dat_created_at <= todate))\
                                            .join(NaEnquiryDetailsSA,and_(NaEnquiryDetailsSA.fk_na_enquiry_master_id == NaEnquiryMasterSA.pk_bint_id))\
                                            .join(CustomerSA,NaEnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                            .join(AuthUserSA, NaEnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                            .join(BranchSA,BranchSA.pk_bint_id == NaEnquiryMasterSA.fk_branch_id)\
                                            .group_by(NaEnquiryMasterSA.pk_bint_id,NaEnquiryMasterSA.vchr_enquiry_num,NaEnquiryDetailsSA.vchr_product,NaEnquiryDetailsSA.vchr_brand,NaEnquiryDetailsSA.vchr_item, CustomerSA.cust_fname,\
                                            NaEnquiryMasterSA.dat_created_at,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name,BranchSA.vchr_name,BranchSA.pk_bint_id)

                # import pdb; pdb.set_trace()
                if request.data['bln_chart']:


                    """Permission wise filter for data"""
                    if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
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

                        else:
                            dct_data['product_all'][ins_data.vchr_product]+=1

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

                    # import pdb; pdb.set_trace()
                    str_report_name = 'NA Enquiry Report'
                    lst_details = ['product_all-pie','branch_all-bar','brand_all-bar','item_all-bar',]
                    dct_label = {'product_all':'Product wise','branch_all':'Branch wise','brand_all':'Brand wise','item_all':'Item wise'}

                if request.data['bln_table']:
                    str_report_name = 'NA Enquiry Report'
                    lst_tbl_head = ['Enquiry No','Enquiry Date','Branch','Product','Brand','Item']
                    lst_tbl_index = [2,1,6,3,4,5]

                if request.data['document'].upper() == 'PDF':
                    if request.data['bln_table'] and request.data['bln_chart']:
                        file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))
                        # file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data)
                    elif request.data['bln_chart']:
                        file_output = generate_pdf(request,str_report_name,lst_details,dct_label,dct_data)
                    elif request.data['bln_table']:
                        file_output = generate_pdf(request,str_report_name,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))


                    if request.data.get('export_type').upper() == 'DOWNLOAD':
                        session.close()
                        return Response({"status":"success",'file':file_output['file'],'file_name':file_output['file_name']})
                    elif request.data.get('export_type').upper() == 'MAIL':
                        session.close()
                        return Response({"status":"success"})

                elif request.data['document'].upper() == 'EXCEL':
                    if request.data['bln_table'] and request.data['bln_chart']:
                        data=generate_excel(request,str_report_name,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))
                    elif request.data['bln_chart']:
                        data=generate_excel(request,str_report_name,lst_details,dct_label,dct_data)
                    elif request.data['bln_table']:
                        data=generate_excel(request,str_report_name,lst_tbl_head,lst_tbl_index,list(rst_enquiry.all()))

                    if request.data.get('export_type').upper() == 'DOWNLOAD':
                        session.close()
                        return Response({"status":"success","file":data})
                    elif request.data.get('export_type').upper() == 'MAIL':
                        session.close()
                        return Response({"status":"success"})

        except Exception as e:
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
