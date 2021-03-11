from collections import Counter
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from POS import ins_logger
from rest_framework.permissions import IsAuthenticated,AllowAny
from enquiry.models import EnquiryMaster
# from software.models import EnquiryTrack,AccountingSoftware,EmployeeManagement,HrSolutions
from userdetails.models import UserDetails as UserModel
from django.contrib.auth.models import User
from customer.models import CustomerDetails as CustomerModel
from stock_app.models import Stockmaster,Stockdetails
# import datetime
from datetime import datetime, timedelta,date
from branch.models import Branch
from userdetails.models import UserDetails as UserModel

from brands.models import Brands
# from auto_mobile.models import SedanEnquiry,SuvEnquiry,HatchbackEnquiry
from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry
import time
from django.http import JsonResponse

import random
from export_excel.views import export_excel
from collections import OrderedDict
from sqlalchemy.orm import sessionmaker
import aldjemy
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date,case, literal_column
from sqlalchemy.sql.expression import literal,union_all
import calendar
from company.models import Company as CompanyDetails
import pandas as pd
import numpy as np
from django.shortcuts import render
# from inventory.models import Brands
from brands.models import Brands
from rest_framework.views import APIView
from rest_framework.response import Response
from target.models import Target_Master,Target_Details
from userdetails.models import UserDetails as UserAppUsermodel

EnquiryMasterSA = EnquiryMaster.sa
UserSA=UserModel.sa

# CustomerModelSA = CustomerModel.sa
# AuthUserSA = User.sa
# FlightsSA = Flights.sa
# AddAttachmentsSA = AddAttachments.sa
# DocumentSA = Document.sa
# HotelSA = Hotel.sa
# VisaSA = Visa.sa
# TransportSA = Transport.sa
# PackageSA = Package.sa
# ForexSA = Forex.sa
# OtherSA = Other.sa
# TravelInsuranceSA = TravelInsurance.sa
# RoomsSA = Rooms.sa
# TrainSA = Train.sa
# SourceSA=Source.sa
# PrioritySA=Priority.sa


# HatchbackEnquirySA = HatchbackEnquiry.sa
# SedanEnquirySA = SedanEnquiry.sa
# SuvEnquirySA = SuvEnquiry.sa

# EnquiryTrackSA = EnquiryTrack.sa
# AccountingSoftwareSA = AccountingSoftware.sa
# HrSolutionsSA = HrSolutions.sa
# EmployeeManagementSA = EmployeeManagement.sa
# from kct_package.models import Kct,KctFollowup,KctPackage
# KctSA=Kct.sa
# KctPackageSA=KctPackage.sa
# KctFollowupSA = KctFollowup.sa

# BranchSA = Branch.sa
# UserSA=UserModel.sa
# BrandsSA=Brands.sa
# ItemsSA=Items.sa
# StockdetailsSA=Stockdetails.sa

#mobile
MobileEnquirySA = MobileEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
ComputersEnquirySA = ComputersEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()
# Create your views here.
class Monthlypercent(APIView):
    permission_classes = [AllowAny,]
    def post(self,request):
        try:
            import pdb;pdb.set_trace()
            session = Session()
            company_id = request.user.userdetails.fk_company_id
            fk_created_by = request.data['user_id']
            year_type=CompanyDetails.objects.filter(pk_bint_id=company_id).values_list('vchr_fin_type',flat=True).first()
            brand_queryset = list(Brands.objects.filter(fk_company_id = company_id).annotate(id = F('pk_bint_id'),vchr_brand_name = F('vchr_name')).values('id','vchr_brand_name').distinct('vchr_name'))
            if not year_type:
                session.close()
                return Response({'status':'0','data':'Company financial year does not exist'})
            dct_sub=[]
            dct_sub.append({'Jan':0})
            dct_sub.append({'Feb':0})
            dct_sub.append({'Mar':0})
            dct_sub.append({'Apr':0})
            dct_sub.append({'May':0})
            dct_sub.append({'Jun':0})
            dct_sub.append({'Jul':0})
            dct_sub.append({'Aug':0})
            dct_sub.append({'Sep':0})
            dct_sub.append({'Oct':0})
            dct_sub.append({'Nov':0})
            dct_sub.append({'Dec':0})

            month = func.extract('month',EnquiryMasterSA.dat_created_at)
            if year_type=='APR-MAR':
                startdate=datetime.strptime('31'+'03'+str(request.data.get('year')), '%d%m%Y').date()
            else:
                startdate=datetime.strptime('31'+'12'+str(request.data.get('year')),'%d%m%Y').date()


            rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.fk_enquiry_master_id.label("fk_enquiry_master_id"),MobileEnquirySA.dbl_amount.label("amount"),MobileEnquirySA.fk_stockdetails_id.label("fk_stockdetails_id")).filter(MobileEnquirySA.vchr_enquiry_status=='BOOKED')
            rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.fk_enquiry_master_id.label("fk_enquiry_master_id"),TabletEnquirySA.dbl_amount.label("amount"),TabletEnquirySA.fk_stockdetails_id.label("fk_stockdetails_id")).filter(TabletEnquirySA.vchr_enquiry_status=='BOOKED')
            rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.fk_enquiry_master_id.label("fk_enquiry_master_id"),ComputersEnquirySA.dbl_amount.label("amount"),ComputersEnquirySA.fk_stockdetails_id.label("fk_stockdetails_id")).filter(ComputersEnquirySA.vchr_enquiry_status=='BOOKED')
            rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.fk_enquiry_master_id.label("fk_enquiry_master_id"),AccessoriesEnquirySA.dbl_amount.label("amount"),AccessoriesEnquirySA.fk_stockdetails_id.label("fk_stockdetails_id")).filter(AccessoriesEnquirySA.vchr_enquiry_status=='BOOKED')
            rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
            # target type 0 for sale and 1 for count
            if request.data['type']=='0':
                rst_enquiry=session.query(func.sum(rst_data.c.amount).label('total'),month.label('month'))\
                                .join(EnquiryMasterSA,rst_data.c.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                .filter(and_(EnquiryMasterSA.fk_created_by_id == fk_created_by,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at <= startdate))\
                                .group_by(month)

                flt_grand_total=0.0

                for ins_data in rst_enquiry:
                    flt_grand_total+=ins_data._asdict()['total']

                for ins_data in rst_enquiry:
                    dct_sub[int(ins_data[1])-1][calendar.month_name[int(ins_data[1])][:3]]=ins_data[0]/flt_grand_total*100

                if year_type=='APR-MAR':
                    int_data=dct_sub[3]['Apr']
                    dct_temp={"Apr'"+str(request.data.get('year'))[2:]:int_data}
                    dct_sub.pop(3)
                    dct_sub.insert(3,dct_temp)
                    int_data=dct_sub[2]['Mar']
                    dct_temp={"Mar'"+str(request.data.get('year')+1)[2:]:int_data}
                    dct_sub.pop(2)
                    dct_sub.insert(2,dct_temp)
                    lst = dct_sub[3:]+dct_sub[:3]
                else:
                    int_data=dct_sub[0]['Jan']
                    dct_temp={"Jan'"+str(request.data.get('year'))[2:]:int_data}
                    dct_sub.pop(0)
                    dct_sub.insert(0,dct_temp)
                    int_data=dct_sub[11]['Dec']
                    dct_temp={"Dec'"+str(request.data.get('year'))[2:]:int_data}
                    dct_sub.pop(11)
                    dct_sub.insert(11,dct_temp)
                    lst=dct_sub
                session.close()
                return JsonResponse({'status': 'success','data':lst , 'brand_queryset':brand_queryset})
            else:
                rst_enquiry=session.query(func.count(rst_data.c.amount).label('count'),month.label('month'))\
                                .join(EnquiryMasterSA,rst_data.c.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                .filter(and_(EnquiryMasterSA.fk_created_by_id == fk_created_by,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at <= startdate))\
                                .group_by(month)


                flt_grand_total=0.0

                for ins_data in rst_enquiry:
                    flt_grand_total+=ins_data._asdict()['count']

                for ins_data in rst_enquiry:
                    dct_sub[int(ins_data[1])-1][calendar.month_name[int(ins_data[1])][:3]]=ins_data[0]/flt_grand_total*100

                if year_type=='APR-MAR':
                    int_data=dct_sub[3]['Apr']
                    dct_temp={"Apr'"+str(request.data.get('year'))[2:]:int_data}
                    dct_sub.pop(3)
                    dct_sub.insert(3,dct_temp)
                    int_data=dct_sub[2]['Mar']
                    dct_temp={"Mar'"+str(request.data.get('year')+1)[2:]:int_data}
                    dct_sub.pop(2)
                    dct_sub.insert(2,dct_temp)
                    lst = dct_sub[3:]+dct_sub[:3]
                else:
                    int_data=dct_sub[0]['Jan']
                    dct_temp={"Jan'"+str(request.data.get('year'))[2:]:int_data}
                    dct_sub.pop(0)
                    dct_sub.insert(0,dct_temp)
                    int_data=dct_sub[11]['Dec']
                    dct_temp={"Dec'"+str(request.data.get('year'))[2:]:int_data}
                    dct_sub.pop(11)
                    dct_sub.insert(11,dct_temp)
                    lst=dct_sub
                session.close()
                return JsonResponse({'status': 'success','data':lst, 'brand_queryset':brand_queryset})


        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            session.close()
            return Response({'status':'0','data':str(e)})


class Brands_List(APIView):

    def post(self, request, format=None):
        try:
            user_id = '123'
            if request.data.__len__()<=0:
                return Response({'status':'failed','error':'no requests received'})
            else:
                fk_user_id = request.data['fk_user_id']
            if user_id == fk_user_id:
                queryset = list(Brands.objects.values('id','vchr_brand_name'))
                if queryset:
                    print(queryset)
                    return Response({'status':'success','value':queryset})
                else:
                    return Response({'status':'no data','error':'no brands found'})
            else:
                return Response({'status':'failed','error':'invalid user id or user does not exist'})

        except Exception as e:
            print(str(e))
            return Response({'status': 'failed','error':str(e)})

class Target_Save(APIView):

    def post(self, request, format=None):
        try:
            user_id = request.data['user']
            fk_created= request.user.id
            vchr_fin_type = request.user.userdetails.fk_company.vchr_fin_type
            dct_Master = {}
            dct_Master['vchr_fin_type'] = vchr_fin_type
            dct_Master['int_year'] = request.data['year']
            dct_Master['dbl_target'] = request.data['amount']
            # target type 0 for sale and 1 for count
            dct_Master['int_target_type'] =request.data['target_type']
            dct_Master['bln_all'] = request.data['blnTargetAll']

            lst_details_data = []
            for lst_data in request.data['details']:
                if( lst_data[12] != 'TOTAL'):
                    for i in range(0,11):
                        dct_data ={}
                        dct_data['int_month'] = i
                        dct_data['dbl_target'] = lst_data[i]
                        dct_data['fk_brand'] = Brands.objects.filter(vchr_brand_name = lst_data[12])
                        lst_details_data.append(dct_data)

            if request.data.__len__()<=0:
                return Response({'status':'failed','error':'no requests received'})
            else:
                if not user_id:
                    return Response({'status':'failed','error':'invalid user'})

            if not dct_Master['vchr_fin_type']:
                return Response({'status':'failed','error':' vchr_fin_type value missing'})
            elif not dct_Master['int_year']:
                return Response({'status':'failed','error':'int_year value missing'})
            elif not dct_Master['dbl_target']:
                return Response({'status':'failed','error':'dbl_amount value missing'})
            elif not dct_Master['dbl_target']:
                return Response({'status':'failed','error':'dbl_target value missing'})
            elif not dct_Master['int_target_type']:
                return Response({'status':'failed','error':'int_target_type value missing'})
            else:
                pass

            # creating instance for model Target_Master

            ins_masterdata = Target_Master(

                vchr_fin_type = dct_Master['vchr_fin_type'],
                int_year = dct_Master['int_year'],
                dbl_target = dct_Master['dbl_target'],
                int_target_type = dct_Master['int_target_type'],
                fk_created = UserAppUsermodel.objects.get(id=fk_created),
                fk_updated = None,
                dat_updated = None,
                bln_active = True,
                bln_all = dct_Master['bln_all'],
                fk_user_id = user_id

            )
            ins_check_presence_master = Target_Master.objects.filter(fk_user_id=user_id,int_target_type=dct_Master['int_target_type'],int_year=dct_Master['int_year'])
            int_check_presence_master = 0

            # checking for already present or not
            if ins_check_presence_master:

                ins_check_presence_master.update( dbl_target = dct_Master['dbl_target'],fk_updated = None,dat_updated = datetime.now())
                int_check_presence_master=1
            else:
                ins_masterdata.save()

            print('master data saved successfully')

            lst_query_set_details = []

            lst_Details = lst_details_data

            if(int_check_presence_master==1):

                for data in lst_Details:

                    int_index=int(data['int_month'])
                    str_month=calendar.month_name[int_index]

                    ins_detailsdata = Target_Details(

                    fk_master_id=ins_check_presence_master[0].pk_bint_id,
                    int_year = ins_masterdata.int_year,

                    dbl_target = data['dbl_target'],
                    int_target_type =ins_masterdata.int_target_type,
                    int_month = data['int_month'],
                    vchr_month = str_month,
                    fk_user_id = ins_masterdata.fk_user_id

                    )

                    check_presence = Target_Details.objects.filter(fk_user_id=user_id,int_target_type=ins_masterdata.int_target_type,int_year = ins_masterdata.int_year,int_month = data['int_month'],)
                    int_check=0

                    if check_presence:

                        check_presence.update(dbl_target=data['dbl_target'],int_month = data['int_month'])

                        int_check=1

                    else:
                        lst_query_set_details.append(ins_detailsdata)

                if lst_query_set_details:

                    Target_Details.objects.bulk_create(lst_query_set_details)
                    return Response({'status':'success'})

                if int_check==1:

                    return Response({'status':'success'})

            else:

                for data in lst_Details:

                    int_index=int(data['int_month'])
                    str_month=calendar.month_name[int_index]

                    ins_detailsdata = Target_Details(

                    fk_master_id=ins_masterdata.pk_bint_id,
                    int_year = ins_masterdata.int_year,

                    dbl_target = data['dbl_target'],
                    int_target_type =ins_masterdata.int_target_type,
                    int_month = data['int_month'],
                    vchr_month = str_month,
                    fk_user_id = ins_masterdata.fk_user_id

                    )

                    check_presence = Target_Details.objects.filter(fk_user_id=user_id,int_target_type=ins_masterdata.int_target_type,int_year = ins_masterdata.int_year,int_month = data['int_month'],)
                    int_check=0

                    if check_presence:

                        check_presence.update(dbl_target=data['dbl_target'],int_month = data['int_month'])
                        int_check=1

                    else:
                        lst_query_set_details.append(ins_detailsdata)

                if lst_query_set_details:

                    Target_Details.objects.bulk_create(lst_query_set_details)
                    return Response({'status':'success'})

                if int_check==1:

                    return Response({'status':'success'})

        except Exception as e:
            print(str(e))
            return Response({'status': 'failed','error':str(e)})
