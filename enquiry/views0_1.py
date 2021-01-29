from django.shortcuts import render
from django.db.models import Q,F
from django.contrib.auth.models import User
from collections import Counter
import pandas as pd
from collections import OrderedDict
import operator
from rest_framework.views import APIView
from rest_framework.response import Response
from sqlalchemy import case, literal_column
from aldjemy.core import get_engine
from finance_enquiry.models import EnquiryFinance,FinanceSchema

from customer.models import CustomerDetails as CustomerModel
from userdetails.models import UserDetails as UserModel
from company.models import Company as CompanyDetails
from enquiry.models import EnquiryMaster,AddAttachments,Document
from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry,ItemEnquiry,ItemExchange,EnquiryFinanceImages
# from enquiry_maintenance.models import Electric,Plumbing,Flooring,Painting 
# from software.models import EnquiryTrack,AccountingSoftware,EmployeeManagement,HrSolutions
from na_enquiry.models import NaEnquiryMaster,NaEnquiryDetails
# from airport.models import Airport
# from station.models import Station
from sqlalchemy import literal
from branch.models import Branch
from zone.models import Zone
from territory.models import Territory
# from kct_package.models import KctPackage,Kct,KctFollowup
from customer_rating.models import CustomerRating
from datetime import datetime
from sqlalchemy import desc
from source.models import Source
# from inventory.models import Brands,Items
from brands.models import Brands
from item_category.models import Item as Items
# from enquiry_solar.models import ProductType,ProductBrand, ProductCategory, ProductCategoryVariant, ProductEnquiry
from finance_enquiry.models import FinanceCustomerDetails
# from globalMethods import show_data_based_on_role,get_user_products
import random
import json
from enquiry_print.views import enquiry_print
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date,or_
from sqlalchemy.sql.expression import literal,union_all
from POS import ins_logger
import aldjemy
from rest_framework.permissions import IsAuthenticated
from location.models import Country as Countries 
from .serializers import AttachmentSerilaizer
from titlecase import titlecase
from collections import OrderedDict
# from auto_mobile.models import SedanEnquiry,SuvEnquiry,HatchbackEnquiry
from products.models import Products
from stock_app.models import Stockmaster,Stockdetails
from userdetails.models import Financiers
from sqlalchemy import desc
from POS.dftosql import Savedftosql
from sqlalchemy import create_engine,inspect,MetaData,Table,Column,select,func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

# from groups.models import GroupPermissions,Groups,MainCategory, SubCategory
# from airline.models import AirlineDetails
# from globalMethods import show_data_based_on_role
from POS import settings
from buy_back.models import BuyBack

from sqlalchemy import and_,or_,func ,cast,Date,case, literal_column,extract

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)


EnquiryMasterSA = EnquiryMaster.sa
CountriesSA = Countries.sa
UserSA=UserModel.sa
AuthUserSA = User.sa
CustomerSA = CustomerModel.sa
BranchSA = Branch.sa
SourceSA=Source.sa
EnquiryFinanceSA = EnquiryFinance.sa
FinanceSchemaSA = FinanceSchema.sa

#mobile
MobileEnquirySA = MobileEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
ComputersEnquirySA = ComputersEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
BrandSA = Brands.sa
ItemSA = Items.sa
StockmasterSA = Stockmaster.sa
StockdetailsSA = Stockdetails.sa

EnquiryFinanceSA = EnquiryFinance.sa




CustomerModelSA=CustomerModel.sa
ItemsSA=Items.sa
BrandsSA=Brands.sa
# GroupsSA=Groups.sa
# ==============================
ItemEnquirySA = ItemEnquiry.sa
ItemExchangeSA = ItemExchange.sa
ProductsSA = Products.sa
ItemEnquiry = metadata.tables['item_enquiry']
ItemExchange = metadata.tables['item_exchange']
# ================================

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()

from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny
from django.db.models import Count
from django.http import JsonResponse
import calendar
# from export_excel.views import export_excel
# from hasher.views import hash_enquiry
from dateutil.tz import tzlocal
import pytz
local = tzlocal()
tz = pytz.timezone('Asia/Kolkata')
# Create your views here.fv
# class CustomerTypeahead(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             str_search_term = request.data.get('term',-1)
#             str_username = request.data.get('username')
#             ins_user = UserModel.objects.get(username = str_username)
#             lst_customers = []
#             if str_search_term != -1:
#                 ins_customer = CustomerModel.objects.filter(Q(cust_mobile__icontains=str_search_term))\
#                 .filter(fk_company = ins_user.fk_company)\
#                 .values('id','cust_mobile','cust_fname','cust_lname','cust_email','cust_salutation','cust_customertype','cust_smsaccess')[:50]
#                 if ins_customer:
#                     for itr_item in ins_customer:
#                         dct_customer = {}
#                         dct_customer['mobile'] = itr_item['cust_mobile']
#                         dct_customer['fname'] = itr_item['cust_fname'].capitalize()
#                         dct_customer['lname'] = itr_item['cust_lname'].capitalize()
#                         dct_customer['id'] = itr_item['id']
#                         dct_customer['email'] = itr_item['cust_email']
#                         dct_customer['salutation'] = itr_item['cust_salutation']
#                         dct_customer['customertype'] = itr_item['cust_customertype']
#                         dct_customer['sms'] = itr_item['cust_smsaccess']
#                         lst_customers.append(dct_customer)
#                 return Response({'status':'success','data':lst_customers})
#             else:
#                 return Response({'status':'empty','data':lst_customers})
#         except Exception as e:
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':'1','data':str(e)})

# class CustomerListReport(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             str_search_term = request.data.get('term',-1)
#             str_username = request.data.get('username')
#             ins_user = UserModel.objects.get(username = str_username)
#             lst_customers = []
#             if str_search_term != -1:
#                 ins_customer = CustomerModel.objects.filter(Q(cust_fname__icontains=str_search_term) | Q(cust_lname__icontains=str_search_term))\
#                 .filter(fk_company = ins_user.fk_company)\
#                 .values('id','cust_mobile','cust_fname','cust_lname','cust_email','cust_salutation','cust_customertype','cust_smsaccess')[:50]
#                 if ins_customer:
#                     for itr_item in ins_customer:
#                         dct_customer = {}
#                         dct_customer['mobile'] = itr_item['cust_mobile']
#                         dct_customer['fname'] = itr_item['cust_fname'].capitalize()
#                         dct_customer['lname'] = itr_item['cust_lname'].capitalize()
#                         dct_customer['id'] = itr_item['id']
#                         dct_customer['email'] = itr_item['cust_email']
#                         dct_customer['salutation'] = itr_item['cust_salutation']
#                         dct_customer['customertype'] = itr_item['cust_customertype']
#                         dct_customer['sms'] = itr_item['cust_smsaccess']
#                         lst_customers.append(dct_customer)
#                 return Response({'status':'success','data':lst_customers})
#             else:
#                 return Response({'status':'empty','data':lst_customers})
#         except Exception as e:
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':'1','data':str(e)})

# class AirportTypeahead(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             str_search_term = request.data.get('term',-1)
#             lst_airport = []
#             if str_search_term != -1:
#                 ins_airport = Airport.objects.filter(Q(vchr_name__icontains=str_search_term)\
#                 | Q(vchr_iata_code__icontains=str_search_term)).values('pk_bint_id','vchr_name','vchr_iata_code')
#                 if ins_airport:
#                     for itr_item in ins_airport:
#                         dct_airport = {}
#                         dct_airport['code'] = itr_item['vchr_iata_code']
#                         dct_airport['airportname'] = itr_item['vchr_name'].capitalize()
#                         dct_airport['id'] = itr_item['pk_bint_id']
#                         lst_airport.append(dct_airport)
#                 return Response({'status':'success','data':lst_airport})
#             else:
#                 return Response({'status':'empty','data':lst_airport})
#         except Exception as e:
#             return Response({'status':'1','data':str(e)})



# class StationTypeahead(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             str_search_term = request.data.get('term',-1)
#             lst_station = []
#             if str_search_term != -1:
#                 ins_station = Station.objects.filter(Q(vchr_name__icontains=str_search_term)\
#                 | Q(vchr_code__icontains=str_search_term)).values('pk_bint_id','vchr_name','vchr_code')
#                 if ins_station:
#                     for itr_item in ins_station:
#                         dct_station = {}
#                         dct_station['code'] = itr_item['vchr_code']
#                         dct_station['stationname'] = itr_item['vchr_name'].capitalize()
#                         dct_station['id'] = itr_item['pk_bint_id']
#                         lst_station.append(dct_station)
#                 return Response({'status':'success','data':lst_station})
#             else:
#                 return Response({'status':'empty','data':lst_station})
#         except Exception as e:
#             return Response({'status':'1','data':str(e)})
# class FileUpload(APIView):
#     def post(self,request):
#         try:
#             print("request data",request.data)
#             print("files",request.FILES)
#         except Exception as e:
#             print(e)
#             return Response({'status':'1','data':str(e)})

# def fun_travels(int_company_id,dat_start,dat_end):
#     session = Session()
#     rst_flight = session.query(literal("Flight").label("vchr_service"),FlightsSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_train = session.query(literal("Train").label("vchr_service"),TrainSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Forex=session.query(literal("Forex").label("vchr_service"),ForexSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Hotel=session.query(literal("Hotel").label("vchr_service"),HotelSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Other=session.query(literal("Other").label("vchr_service"),OtherSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Transport=session.query(literal("Transport").label("vchr_service"),TransportSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_TravelInsurance=session.query(literal("Travel Insurance").label("vchr_service"),TravelInsuranceSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Visa=session.query(literal("Visa").label("vchr_service"),VisaSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Package=session.query(literal("Package").label("vchr_service"),PackageSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_Kct = session.query(literal("Kerala City Tour").label("vchr_service"),KctSA.fk_enquiry_master_id.label("FK_Enquery"))
#
#     rst_data = rst_flight.union_all(rst_Forex,rst_Hotel,rst_Other,rst_Transport,rst_TravelInsurance,rst_Visa,rst_Package,rst_train,rst_Kct).subquery()
#
#     return rst_data

# def fun_mobile():
#     session = Session()
#     rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
#     rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
#     rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
#     rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
#     rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
#     session.close()
#     return rst_data

# def fun_softwares(int_company_id,dat_start,dat_end):
#     session = Session()
#     rst_enquiry_track = session.query(literal("Enquiry Track").label("vchr_service"),EnquiryTrackSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_accounting_software = session.query(literal("Acounting Software").label("vchr_service"),AccountingSoftwareSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_hr_solutions = session.query(literal("HR solutions").label("vchr_service"),HrSolutionsSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_employee_management = session.query(literal("Employee Management").label("vchr_service"),EmployeeManagementSA.fk_enquiry_master_id.label("FK_Enquery"))
#
#     rst_data = rst_enquiry_track.union_all(rst_accounting_software,rst_hr_solutions,rst_employee_management).subquery()
#     return rst_data

# def fun_maintenance():
#     session = Session()
#     rst_electric = session.query(literal("Electric").label("vchr_service"),ElectricSA.vchr_enquiry_status.label('vchr_enquiry_status'),ElectricSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_plumbing = session.query(literal("Plumbing").label("vchr_service"),PlumbingSA.vchr_enquiry_status.label('vchr_enquiry_status'),PlumbingSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_flooring = session.query(literal("Flooring").label("vchr_service"),FlooringSA.vchr_enquiry_status.label('vchr_enquiry_status'),FlooringSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_painting = session.query(literal("Painting").label("vchr_service"),PaintingSA.vchr_enquiry_status.label('vchr_enquiry_status'),PaintingSA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_data = rst_electric.union_all(rst_plumbing,rst_flooring,rst_painting).subquery()
#     return rst_data

# def fun_automobile():
#     session = Session()
#     rst_hatchback = session.query(literal("Hatchback").label("vchr_service"),HatchbackEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),HatchbackEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_sedan = session.query(literal("Sedan").label("vchr_service"),SedanEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),SedanEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_suv = session.query(literal("SUV").label("vchr_service"),SuvEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),SuvEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_data = rst_hatchback.union_all(rst_sedan,rst_suv).subquery()
#     return rst_data

# def fun_solar():
#     session = Session()
#
#     rst_data = session.query(ProductEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ProductEnquirySA.fk_enquiry_master_id.label('FK_Enquery'),ProductTypeSA.vchr_type_name.label('vchr_service')).join(ProductTypeSA,ProductEnquirySA.fk_product_id == ProductTypeSA.pk_bint_id)
#
#     return rst_data.subquery()

# def fun_travels_view():
#     return 'success'
# def fun_travels_view(int_enquiry_id,lst_enquiry_data):
#     session = Session()
#     airport_alias = aliased(AirportSA)
#
#     rst_flight = session.query(FlightsSA.pk_bint_id,FlightsSA.fk_source_id,FlightsSA.fk_destination_id,FlightsSA.dat_departure,FlightsSA.vchr_class,FlightsSA.int_adults,\
#                                 FlightsSA.int_children,FlightsSA.int_infants,FlightsSA.vchr_enquiry_status,FlightsSA.dbl_estimated_amount,FlightsSA.vchr_remarks,FlightsSA.chr_type_of_travel,FlightsSA.dat_return,airport_alias.vchr_name.label("destination"),AirportSA.vchr_name.label("source"),FlightsSA.fk_airline_id,AirlineSA.vchr_name.label("vchr_airline"))\
#                                 .join(EnquiryMasterSA,FlightsSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(AirportSA, AirportSA.pk_bint_id == FlightsSA.fk_source_id)\
#                                 .join(airport_alias, airport_alias.pk_bint_id == FlightsSA.fk_destination_id)\
#                                 .outerjoin(AirlineSA, FlightsSA.fk_airline_id == AirlineSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#     station_alias = aliased(StationSA)
#
#     rst_train = session.query(TrainSA.pk_bint_id,TrainSA.fk_source_id,TrainSA.fk_destination_id,TrainSA.dat_departure,TrainSA.vchr_class,TrainSA.vchr_train,TrainSA.int_adults,\
#                                 TrainSA.int_children,TrainSA.int_infants,TrainSA.vchr_enquiry_status,TrainSA.dbl_estimated_amount,TrainSA.vchr_remarks,TrainSA.chr_type_of_travel,TrainSA.dat_return,station_alias.vchr_name.label("destination"),StationSA.vchr_name.label("source"))\
#                                 .join(EnquiryMasterSA,TrainSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(StationSA, StationSA.pk_bint_id == TrainSA.fk_source_id)\
#                                 .join(station_alias, station_alias.pk_bint_id == TrainSA.fk_destination_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_forex=session.query(ForexSA.pk_bint_id,ForexSA.dbl_amount,ForexSA.vchr_from,ForexSA.vchr_to,ForexSA.vchr_enquiry_status,ForexSA.dbl_estimated_amount,ForexSA.vchr_remarks,)\
#                                 .join(EnquiryMasterSA,ForexSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_other=session.query(OtherSA.vchr_enquiry_status,OtherSA.pk_bint_id ,OtherSA.vchr_description,OtherSA.vchr_enquiry_status,OtherSA.dbl_estimated_amount)\
#                                 .join(EnquiryMasterSA,OtherSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_visa=session.query(VisaSA.pk_bint_id ,VisaSA.fk_country_id,VisaSA.vchr_visa_category,VisaSA.vchr_visit_type,VisaSA.vchr_duration_type,VisaSA.dbl_duration,VisaSA.int_adults,\
#                                 VisaSA.int_children,VisaSA.int_infants,VisaSA.vchr_enquiry_status,VisaSA.dbl_estimated_amount,VisaSA.vchr_remarks,CountriesSA.vchr_country_name)\
#                                 .join(EnquiryMasterSA,VisaSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')\
#                                 .join(CountriesSA,CountriesSA.pk_bint_id == VisaSA.fk_country_id)
#
#     rst_travel_insurance=session.query(TravelInsuranceSA.pk_bint_id ,TravelInsuranceSA.dat_from,TravelInsuranceSA.dat_to,TravelInsuranceSA.vchr_insurance_type,TravelInsuranceSA.int_adults,\
#                                 TravelInsuranceSA.int_children,TravelInsuranceSA.int_infants,TravelInsuranceSA.vchr_enquiry_status,TravelInsuranceSA.dbl_estimated_amount,TravelInsuranceSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,TravelInsuranceSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_transport=session.query(TransportSA.pk_bint_id,TransportSA.dat_from,TransportSA.dat_to,TransportSA.vchr_pick_up,TransportSA.vchr_drop_off,TransportSA.vchr_vehical_type,TransportSA.int_seats,TransportSA.int_adults,\
#                                 TransportSA.int_children,TransportSA.int_infants,TransportSA.vchr_vehical_preferred,TransportSA.vchr_facility,TransportSA.vchr_enquiry_status,TransportSA.dbl_estimated_amount,TransportSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,TransportSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_hotel=session.query(HotelSA.pk_bint_id,HotelSA.dat_check_in,HotelSA.dat_check_out,HotelSA.vchr_city,HotelSA.vchr_nationality,HotelSA.int_rooms,HotelSA.dbl_budget,HotelSA.vchr_star_rating,HotelSA.vchr_meal_type,HotelSA.vchr_remarks,HotelSA.vchr_enquiry_status,HotelSA.dbl_estimated_amount)\
#                                 .join(EnquiryMasterSA,HotelSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_hotel_sub=session.query(HotelSA.pk_bint_id,HotelSA.dat_check_in,HotelSA.dat_check_out,HotelSA.vchr_city,HotelSA.vchr_nationality,HotelSA.int_rooms,HotelSA.dbl_budget,HotelSA.vchr_star_rating,HotelSA.vchr_meal_type,HotelSA.vchr_remarks,HotelSA.vchr_enquiry_status,HotelSA.dbl_estimated_amount)\
#                                 .join(EnquiryMasterSA,HotelSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N').subquery()
#                                 # .join(RoomSA,RoomSA.fk_hotel_id == HotelSA.pk_bint_id)
# # RoomSA.pk_bint_id,RoomSA.fk_hotel_id,RoomSA.vchr_room_type,RoomSA.int_adults,RoomSA.int_children)\
#     rst_rooms = session.query(RoomSA.pk_bint_id,RoomSA.fk_hotel_id,RoomSA.vchr_room_type,RoomSA.int_adults,RoomSA.int_children)\
#                                 .join(rst_hotel_sub,RoomSA.fk_hotel_id == rst_hotel_sub.c.pk_bint_id)
#
#     rst_package=session.query(PackageSA.pk_bint_id ,PackageSA.dat_from,PackageSA.dat_to,PackageSA.int_adults,PackageSA.int_children,PackageSA.int_infants,PackageSA.dbl_budget,PackageSA.vchr_destination,PackageSA.vchr_enquiry_status,PackageSA.dbl_estimated_amount,PackageSA.vchr_sightseeing,PackageSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,PackageSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_kct=session.query(KctSA.pk_bint_id ,KctPackageSA.vchr_package_name,KctSA.dat_travel,KctSA.int_count,KctSA.vchr_enquiry_status,KctSA.dbl_estimated_amount,KctSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,KctSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(KctPackageSA,KctPackageSA.pk_bint_id == KctSA.fk_kct_package_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#     return ({'train':rst_train,'flights':rst_flight,'forex':rst_forex,'other':rst_other,'visa':rst_visa,'hotel':rst_hotel,\
#     'rooms':rst_rooms,'transport':rst_transport,'travel_insurance':rst_travel_insurance,'package':rst_package,'kct':rst_kct})

# def fun_software_view(int_enquiry_id,lst_enquiry_data):
#     session = Session()
#     lst_enquiry_track = []
#     lst_accounting_software = []
#     lst_hr_solutions = []
#     lst_employee_management = []
#
#     rst_enquiry_track = session.query(EnquiryTrackSA.pk_bint_id,EnquiryTrackSA.fk_enquiry_master_id,EnquiryTrackSA.int_count,EnquiryTrackSA.dbl_amount,EnquiryTrackSA.vchr_enquiry_status,EnquiryTrackSA.bln_promo_campaign,EnquiryTrackSA.bln_digital_marketing,\
#                                 EnquiryTrackSA.bln_business_intelligence,EnquiryTrackSA.bln_accounting_software,EnquiryTrackSA.bln_hr_solutions,EnquiryTrackSA.bln_employee_management,EnquiryTrackSA.vchr_requirements,EnquiryTrackSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,EnquiryTrackSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_accounting_software = session.query(AccountingSoftwareSA.pk_bint_id,AccountingSoftwareSA.fk_enquiry_master_id,AccountingSoftwareSA.int_count,AccountingSoftwareSA.dbl_amount,AccountingSoftwareSA.vchr_enquiry_status,AccountingSoftwareSA.bln_promo_campaign,AccountingSoftwareSA.bln_digital_marketing,\
#                                 AccountingSoftwareSA.bln_business_intelligence,AccountingSoftwareSA.bln_enquiry_track,AccountingSoftwareSA.bln_hr_solutions,AccountingSoftwareSA.bln_employee_management,AccountingSoftwareSA.vchr_requirements,AccountingSoftwareSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,AccountingSoftwareSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_hr_solutions = session.query(HrSolutionsSA.pk_bint_id,HrSolutionsSA.fk_enquiry_master_id,HrSolutionsSA.int_count,HrSolutionsSA.dbl_amount,HrSolutionsSA.vchr_enquiry_status,HrSolutionsSA.bln_promo_campaign,HrSolutionsSA.bln_digital_marketing,\
#                                 HrSolutionsSA.bln_business_intelligence,HrSolutionsSA.bln_accounting,HrSolutionsSA.bln_enquiry_track,HrSolutionsSA.bln_employee_management,HrSolutionsSA.vchr_requirements,HrSolutionsSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,HrSolutionsSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_employee_management = session.query(EmployeeManagementSA.pk_bint_id,EmployeeManagementSA.fk_enquiry_master_id,EmployeeManagementSA.int_count,EmployeeManagementSA.dbl_amount,EmployeeManagementSA.vchr_enquiry_status,EmployeeManagementSA.bln_promo_campaign,EmployeeManagementSA.bln_digital_marketing,\
#                                 EmployeeManagementSA.bln_business_intelligence,EmployeeManagementSA.bln_accounting,EmployeeManagementSA.bln_hr_solutions,EmployeeManagementSA.bln_enquiry_track,EmployeeManagementSA.vchr_requirements,EmployeeManagementSA.vchr_remarks)\
#                                 .join(EnquiryMasterSA,EmployeeManagementSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     return ({'enquiry_track':rst_enquiry_track,'accounting_software':rst_accounting_software,'hr_solutions':rst_hr_solutions,'employee_management':rst_employee_management})
#     for dct_data in rst_enquiry_track:
#         lst_enquiry_track.append(dct_data._asdict())
#     for dct_data in rst_accounting_software:
#         lst_accounting_software.append(dct_data._asdict())
#     for dct_data in rst_hr_solutions:
#         lst_hr_solutions.append(dct_data._asdict())
#     for dct_data in rst_employee_management:
#         lst_employee_management.append(dct_data._asdict())
#
#     return ({'status' : '0','enquiry_Data':lst_enquiry_data,'enquiry_track':lst_enquiry_track,'accounting_software':lst_accounting_software,'hr_solutions':lst_hr_solutions,'employee_management':lst_employee_management})

# def fun_solar_view(int_enquiry_id,lst_enquiry_data):
#     session = Session()
#
#     rst_solar = session.query(ProductEnquirySA.pk_bint_id,ProductEnquirySA.vchr_enquiry_status,ProductEnquirySA.fk_enquiry_master_id,ProductEnquirySA.fk_brand_id,ProductEnquirySA.fk_category_id,ProductEnquirySA.int_quantity,ProductEnquirySA.dbl_amount,ProductEnquirySA.fk_enquiry_master,ProductEnquirySA.vchr_remarks,EnquiryMasterSA.fk_branch_id,ProductTypeSA.vchr_type_name,ProductCategoryVariantSA.vchr_color,ProductCategoryVariantSA.vchr_spec,ProductCategorySA.vchr_category,ProductBrandSA.vchr_brand_name)\
#     .join(EnquiryMasterSA,ProductEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#     .join(ProductTypeSA,ProductEnquirySA.fk_product_id == ProductTypeSA.pk_bint_id)\
#     .join(ProductCategoryVariantSA,ProductEnquirySA.fk_variant_id == ProductCategoryVariantSA.pk_bint_id)\
#     .join(ProductCategorySA,ProductEnquirySA.fk_category_id == ProductCategorySA.pk_bint_id)\
#     .join(ProductBrandSA,ProductEnquirySA.fk_brand_id == ProductBrandSA.pk_bint_id)\
#     .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     return ({'solar':rst_solar})

# def fun_mobile_view(int_enquiry_id,lst_enquiry_data):
#     session = Session()
#     lst_mobile = []
#     lst_tablet = []
#     lst_computer = []
#     lst_accessories = []
#     rst_mobile = session.query(MobileEnquirySA.pk_bint_id,MobileEnquirySA.fk_enquiry_master_id,MobileEnquirySA.fk_brand_id,MobileEnquirySA.fk_item_id,MobileEnquirySA.int_quantity,MobileEnquirySA.dbl_amount,MobileEnquirySA.vchr_enquiry_status,\
#                                 MobileEnquirySA.vchr_colour,MobileEnquirySA.vchr_spec,MobileEnquirySA.vchr_remarks,EnquiryMasterSA.fk_branch_id,\
#                                 BrandSA.vchr_brand_name,ItemSA.vchr_item_name)\
#                                 .join(EnquiryMasterSA,MobileEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(BrandSA, BrandSA.id == MobileEnquirySA.fk_brand_id)\
#                                 .join(ItemSA, ItemSA.id == MobileEnquirySA.fk_item_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_tablet = session.query(TabletEnquirySA.pk_bint_id,TabletEnquirySA.fk_enquiry_master_id,TabletEnquirySA.fk_brand_id,TabletEnquirySA.fk_item_id,TabletEnquirySA.int_quantity,TabletEnquirySA.dbl_amount,TabletEnquirySA.vchr_enquiry_status,\
#                                 TabletEnquirySA.vchr_remarks,BrandSA.vchr_brand_name,ItemSA.vchr_item_name,EnquiryMasterSA.fk_branch_id,)\
#                                 .join(EnquiryMasterSA,TabletEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(BrandSA, BrandSA.id == TabletEnquirySA.fk_brand_id)\
#                                 .join(ItemSA, ItemSA.id == TabletEnquirySA.fk_item_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_computer = session.query(ComputersEnquirySA.pk_bint_id,ComputersEnquirySA.fk_enquiry_master_id,ComputersEnquirySA.fk_brand_id,ComputersEnquirySA.fk_item_id,ComputersEnquirySA.int_quantity,ComputersEnquirySA.dbl_amount,ComputersEnquirySA.vchr_enquiry_status,\
#                                 ComputersEnquirySA.vchr_remarks,BrandSA.vchr_brand_name,ItemSA.vchr_item_name,EnquiryMasterSA.fk_branch_id,)\
#                                 .join(EnquiryMasterSA,ComputersEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(BrandSA, BrandSA.id == ComputersEnquirySA.fk_brand_id)\
#                                 .join(ItemSA, ItemSA.id == ComputersEnquirySA.fk_item_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_accessories = session.query(AccessoriesEnquirySA.pk_bint_id,AccessoriesEnquirySA.fk_enquiry_master_id,AccessoriesEnquirySA.fk_brand_id,AccessoriesEnquirySA.fk_item_id,AccessoriesEnquirySA.int_quantity,AccessoriesEnquirySA.dbl_amount,AccessoriesEnquirySA.vchr_enquiry_status,\
#                                 AccessoriesEnquirySA.vchr_remarks,BrandSA.vchr_brand_name,ItemSA.vchr_item_name,EnquiryMasterSA.fk_branch_id,)\
#                                 .join(EnquiryMasterSA,AccessoriesEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(BrandSA, BrandSA.id == AccessoriesEnquirySA.fk_brand_id)\
#                                 .join(ItemSA, ItemSA.id == AccessoriesEnquirySA.fk_item_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     return ({'mobile':rst_mobile,'tablet':rst_tablet,'computer':rst_computer,'accessories':rst_accessories})
#     for dct_data in rst_mobile:
#         lst_mobile.append(dct_data._asdict())
#     for dct_data in rst_tablet:
#         lst_tablet.append(dct_data._asdict())
#     for dct_data in rst_computer:
#         lst_computer.append(dct_data._asdict())
#     for dct_data in rst_accessories:
#         lst_accessories.append(dct_data._asdict())
#
#     return ({'status' : '0','enquiry_Data':lst_enquiry_data,'mobile':rst_mobile,'tablet':rst_tablet,'computer':rst_computer,'accessories':rst_accessories})


# def fun_maintenance_view(int_enquiry_id,lst_enquiry_data):
#     session = Session()
#     rst_electric = session.query(ElectricSA.pk_bint_id,ElectricSA.fk_enquiry_master_id,ElectricSA.vchr_electric_gauge,\
#                                 ElectricSA.dbl_length,ElectricSA.dbl_estimated_amount,ElectricSA.vchr_enquiry_status,\
#                                 ElectricSA.vchr_remarks,ElectricSA.vchr_type)\
#                                 .join(EnquiryMasterSA,ElectricSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_plumbing = session.query(PlumbingSA.pk_bint_id,PlumbingSA.fk_enquiry_master_id,PlumbingSA.vchr_pipe_diameter,\
#                                 PlumbingSA.dbl_length,PlumbingSA.dbl_estimated_amount,PlumbingSA.vchr_enquiry_status,\
#                                 PlumbingSA.vchr_remarks,PlumbingSA.vchr_type)\
#                                 .join(EnquiryMasterSA,PlumbingSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_flooring = session.query(FlooringSA.pk_bint_id,FlooringSA.fk_enquiry_master_id,FlooringSA.vchr_tile_type,\
#                                 FlooringSA.vchr_tile_color,FlooringSA.dbl_area,FlooringSA.dbl_estimated_amount,\
#                                 FlooringSA.vchr_enquiry_status,FlooringSA.vchr_remarks,FlooringSA.vchr_type)\
#                                 .join(EnquiryMasterSA,FlooringSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     rst_painting = session.query(PaintingSA.pk_bint_id,PaintingSA.fk_enquiry_master_id,PaintingSA.vchr_paint_type,\
#                                 PaintingSA.vchr_paint_color,PaintingSA.dbl_area,PaintingSA.dbl_estimated_amount,\
#                                 PaintingSA.vchr_enquiry_status,PaintingSA.vchr_remarks,PaintingSA.vchr_type)\
#                                 .join(EnquiryMasterSA,PaintingSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#
#     return ({'electric':rst_electric,'plumbing':rst_plumbing,'flooring':rst_flooring,'painting':rst_painting})


# """To filter permission wise data"""
def get_perm_data(rst_enquiry,user):
    int_branch_id = user.usermodel.fk_branch_id
    int_group_id = user.usermodel.fk_group_id
    ins_group_name = user.usermodel.fk_group.vchr_name
    ins_category = SubCategory.objects.get(vchr_sub_category_name = 'ASSIGN').pk_bint_id
    ins_permission=GroupPermissions.objects.filter(fk_groups_id = int_group_id,fk_category_items__fk_sub_category_id = ins_category).values('bln_add')
    if ins_group_name in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == int_branch_id)
    elif ins_group_name=='Territory Manager':
        ins_territory=Branch.objects.get(pk_bint_id=int_branch_id).fk_territory_id
        ins_branch=Branch.objects.filter(fk_territory_id=ins_territory).values_list('pk_bint_id',flat=True)
        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
    elif ins_group_name=='Zone Manager':
        ins_zone=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id')
        ins_territory=Territory.objects.filter(fk_zone_id=ins_zone).values_list('pk_bint_id',flat=True)
        ins_branch=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
    elif ins_group_name=='Country Manager':
        ins_country=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id__fk_country_id')
        ins_zone=Zone.objects.filter(fk_country_id=ins_country).values_list('pk_bint_id',flat=True)
        ins_territory=Territory.objects.filter(fk_zone_id__in=ins_zone).values_list('pk_bint_id',flat=True)
        ins_branch=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
    return rst_enquiry



# class EnquiryView(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#
#         try:
#             int_enquiry_id=request.data["enquiry_id"]
#             chr_company_type = request.data.get('company_type')
#             if not int_enquiry_id or int_enquiry_id == 'undefined' :
#                 return Response({'status': '1','data':'Enquiry id must be provide'})
#             else:
#                 session = Session()
#                 lst_enquiry_data = []
#                 lst_flight = []
#                 lst_train = []
#                 lst_forex = []
#                 lst_other = []
#                 lst_visa = []
#                 lst_hotel = []
#                 lst_transport = []
#                 lst_travel_insurance = []
#                 lst_package =[]
#                 lst_kct =[]
#                 lst_rooms =[]
#
#                 lst_enquiry_track = []
#                 lst_accounting_software = []
#                 lst_hr_solutions = []
#                 lst_employee_management = []
#
#                 lst_mobile = []
#                 lst_tablet = []
#                 lst_computer = []
#                 lst_accessories = []
#
#                 lst_electric = []
#                 lst_plumbing = []
#                 lst_flooring = []
#                 lst_painting = []
#
#                 lst_water_heater = []
#                 lst_power_plant = []
#                 #
#                 rst_enquiry_Data = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.fk_source_id,EnquiryMasterSA.vchr_customer_type,\
#                                             EnquiryMasterSA.bln_sms,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.fk_priority_id,\
#                                             EnquiryMasterSA.dat_updated_at,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,CustomerSA.cust_email,\
#                                             CustomerSA.cust_alternatemobile,CustomerSA.cust_alternatemail,CustomerSA.cust_contactsrc,AuthUserSA.first_name,AuthUserSA.last_name,SourceSA.vchr_source_name,PrioritySA.vchr_priority_name,BranchSA.vchr_name)\
#                                             .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                                             .join(AuthUserSA, EnquiryMasterSA.fk_created_by_id == AuthUserSA.id)\
#                                             .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
#                                             .join(PrioritySA, EnquiryMasterSA.fk_priority_id == PrioritySA.pk_bint_id)\
#                                             .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#                                             .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N').all()
#                 for dct_data in rst_enquiry_Data:
#                     lst_enquiry_data.append(dct_data._asdict())
#
#                 if chr_company_type == "SOFTWARE":
#                     dct_result_data = fun_software_view(int_enquiry_id,lst_enquiry_data)
#
#
#                     for dct_data in dct_result_data['enquiry_track'].all():
#                         lst_enquiry_track.append(dct_data._asdict())
#                     for dct_data in dct_result_data['accounting_software'].all():
#                         lst_accounting_software.append(dct_data._asdict())
#                     for dct_data in dct_result_data['hr_solutions'].all():
#                         lst_hr_solutions.append(dct_data._asdict())
#                     for dct_data in dct_result_data['employee_management'].all():
#                         lst_employee_management.append(dct_data._asdict())
#
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'enquiry_track':lst_enquiry_track,'accounting_software':lst_accounting_software,'hr_solutions':lst_hr_solutions,'employee_management':lst_employee_management})
#                     # return Response(fun_software_view(int_enquiry_id,lst_enquiry_data))
#                 elif chr_company_type == "MOBILE":
#                     dct_result_data = fun_mobile_view(int_enquiry_id,lst_enquiry_data)
#                     for dct_data in dct_result_data['mobile'].all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         dct_data['dbl_imei_json'] = MobileEnquiry.objects.get(pk_bint_id = dct_data['pk_bint_id']).dbl_imei_json
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_mobile.append(dct_data)
#                     for dct_data in dct_result_data['tablet'].all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         dct_data['dbl_imei_json'] = TabletEnquiry.objects.get(pk_bint_id = dct_data['pk_bint_id']).dbl_imei_json
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_tablet.append(dct_data)
#                     for dct_data in dct_result_data['computer'].all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         dct_data['dbl_imei_json'] = ComputersEnquiry.objects.get(pk_bint_id = dct_data['pk_bint_id']).dbl_imei_json
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_computer.append(dct_data)
#                     for dct_data in dct_result_data['accessories'].all():
#                         dct_data = dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         dct_data['dbl_imei_json'] = AccessoriesEnquiry.objects.get(pk_bint_id = dct_data['pk_bint_id']).dbl_imei_json
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_accessories.append(dct_data)
#
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'mobile':lst_mobile,'tablet':lst_tablet,'computers':lst_computer,'accessories':lst_accessories})
#
#                 elif chr_company_type == 'SOLAR':
#                     dct_result_data = fun_solar_view(int_enquiry_id,lst_enquiry_data)
#
#                     for dct_data in dct_result_data['solar']:
#                         dct_data = dct_data._asdict()
#
#                         if dct_data['vchr_type_name'] == 'WATER HEATER':
#                             lst_water_heater.append(dct_data)
#                         else:
#                             lst_power_plant.append(dct_data)
#
#                     return Response({'status':'0','enquiry_Data':lst_enquiry_data,'power_plant':lst_power_plant,'water_heater':lst_water_heater})
#
#                 elif chr_company_type == "TRAVEL AND TOURISM":
#                     dct_result_data = fun_travels_view(int_enquiry_id,lst_enquiry_data)
#                     for dct_data in dct_result_data['flights'].all():
#                         lst_flight.append(dct_data._asdict())
#                     for dct_data in dct_result_data['train'].all():
#                         lst_train.append(dct_data._asdict())
#                     for dct_data in dct_result_data['forex'].all():
#                         lst_forex.append(dct_data._asdict())
#                     for dct_data in dct_result_data['other'].all():
#                         lst_other.append(dct_data._asdict())
#                     for dct_data in dct_result_data['visa'].all():
#                         lst_visa.append(dct_data._asdict())
#                     for dct_data in dct_result_data['travel_insurance'].all():
#                         lst_travel_insurance.append(dct_data._asdict())
#                     for dct_data in dct_result_data['transport'].all():
#                         lst_transport.append(dct_data._asdict())
#                     for dct_data in dct_result_data['hotel'].all():
#                         lst_hotel.append(dct_data._asdict())
#                     for dct_data in dct_result_data['rooms'].all():
#                         lst_rooms.append(dct_data._asdict())
#                     for dct_data in dct_result_data['package'].all():
#                         lst_package.append(dct_data._asdict())
#                     for dct_data in dct_result_data['kct'].all():
#                         lst_kct.append(dct_data._asdict())
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'train':lst_train,'flights':lst_flight,'forex':lst_forex,'other':lst_other,'visa':lst_visa,\
#                                     'hotel':lst_hotel,'rooms':lst_rooms,'transport':lst_transport,'travel_insurance':lst_travel_insurance,'package':lst_package,'kct':lst_kct})
#         except Exception as msg:
#             ins_logger.logger.error(msg, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status': '1','data':msg})

# class PendingEnquiryView(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             #
#             int_enquiry_id=request.data["enquiry_id"]
#             chr_company_type = request.data.get('company_type')
#             if not int_enquiry_id or int_enquiry_id == 'undefined' :
#                 return Response({'status': '1','data':'Enquiry id must be provide'})
#             else:
#                 session = Session()
#                 lst_enquiry_data = []
#                 lst_flight = []
#                 lst_train = []
#                 lst_forex = []
#                 lst_other = []
#                 lst_visa = []
#                 lst_hotel = []
#                 lst_transport = []
#                 lst_travel_insurance = []
#                 lst_package =[]
#                 lst_kct =[]
#                 lst_rooms =[]
#
#                 lst_enquiry_track = []
#                 lst_accounting_software = []
#                 lst_hr_solutions = []
#                 lst_employee_management = []
#                 lst_mobile=[]
#                 lst_tablet=[]
#                 lst_computer=[]
#                 lst_accessories=[]
#                 lst_electric = []
#                 lst_plumbing = []
#                 lst_flooring = []
#                 lst_painting = []
#
#                 rst_enquiry_Data = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.vchr_customer_type,EnquiryMasterSA.bln_sms,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.fk_source_id,EnquiryMasterSA.fk_priority_id,\
#                                             EnquiryMasterSA.dat_updated_at,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,CustomerSA.cust_email,\
#                                             CustomerSA.cust_alternatemobile,CustomerSA.cust_alternatemail,CustomerSA.cust_contactsrc,AuthUserSA.first_name,AuthUserSA.last_name,SourceSA.vchr_source_name,PrioritySA.vchr_priority_name,BranchSA.vchr_name)\
#                                             .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                                             .join(AuthUserSA, EnquiryMasterSA.fk_created_by_id == AuthUserSA.id)\
#                                             .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
#                                             .join(PrioritySA, EnquiryMasterSA.fk_priority_id == PrioritySA.pk_bint_id)\
#                                             .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#                                             .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N')
#                 for dct_data in rst_enquiry_Data:
#                     lst_enquiry_data.append(dct_data._asdict())
#
#                 if chr_company_type == "SOFTWARE":
#                     dct_result_data = fun_software_view(int_enquiry_id,lst_enquiry_data)
#
#                     rst_enquiry_track = dct_result_data['enquiry_track'].filter(EnquiryTrackSA.vchr_enquiry_status != 'LOST' ,EnquiryTrackSA.vchr_enquiry_status != 'BOOKED' , EnquiryTrackSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_accounting_software = dct_result_data['accounting_software'].filter(AccountingSoftwareSA.vchr_enquiry_status != 'LOST' ,AccountingSoftwareSA.vchr_enquiry_status != 'BOOKED' , AccountingSoftwareSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_hr_solutions = dct_result_data['hr_solutions'].filter(HrSolutionsSA.vchr_enquiry_status != 'LOST' ,HrSolutionsSA.vchr_enquiry_status != 'BOOKED' , HrSolutionsSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_employee_management = dct_result_data['employee_management'].filter(EmployeeManagementSA.vchr_enquiry_status != 'LOST' ,EmployeeManagementSA.vchr_enquiry_status != 'BOOKED' , EmployeeManagementSA.vchr_enquiry_status != 'UNQUALIFIED' )
#
#                     for dct_data in rst_enquiry_track.all():
#                         lst_enquiry_track.append(dct_data._asdict())
#                     for dct_data in rst_accounting_software.all():
#                         lst_accounting_software.append(dct_data._asdict())
#                     for dct_data in rst_hr_solutions.all():
#                         lst_hr_solutions.append(dct_data._asdict())
#                     for dct_data in rst_employee_management.all():
#                         lst_employee_management.append(dct_data._asdict())
#
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'enquiry_track':lst_enquiry_track,'accounting_software':lst_accounting_software,'hr_solutions':lst_hr_solutions,'employee_management':lst_employee_management})
#                 elif chr_company_type == "MOBILE":
#                     #
#                     dct_result_data = fun_mobile_view(int_enquiry_id,lst_enquiry_data)
#
#                     rst_mobile = dct_result_data['mobile'].filter(MobileEnquirySA.vchr_enquiry_status != 'LOST' ,MobileEnquirySA.vchr_enquiry_status != 'BOOKED' ,MobileEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_tablet = dct_result_data['tablet'].filter(TabletEnquirySA.vchr_enquiry_status != 'LOST' ,TabletEnquirySA.vchr_enquiry_status != 'BOOKED' ,TabletEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_computer = dct_result_data['computer'].filter(ComputersEnquirySA.vchr_enquiry_status != 'LOST' ,ComputersEnquirySA.vchr_enquiry_status != 'BOOKED' , ComputersEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_accessories = dct_result_data['accessories'].filter(AccessoriesEnquirySA.vchr_enquiry_status != 'LOST' ,AccessoriesEnquirySA.vchr_enquiry_status != 'BOOKED' ,AccessoriesEnquirySA.vchr_enquiry_status != 'UNQUALIFIED' )
#
#
#                     for dct_data in rst_mobile.all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_mobile.append(dct_data)
#                     for dct_data in rst_tablet.all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_tablet.append(dct_data)
#                     for dct_data in rst_computer.all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_computer.append(dct_data)
#                     for dct_data in rst_accessories.all():
#                         dct_data=dct_data._asdict()
#                         ins_result_set=Stockdetails.objects.filter(fk_item_id=dct_data['fk_item_id'],fk_stock_master__fk_branch_id=dct_data['fk_branch_id'],int_available__gt=0).order_by('fk_stock_master__dat_added').values('dbl_min_selling_price','dbl_max_selling_price').first()
#                         if not ins_result_set:
#                             dct_data['dbl_max_selling_price']=0
#                             dct_data['dbl_min_selling_price']=0
#                         else:
#                             dct_data['dbl_max_selling_price']=ins_result_set['dbl_max_selling_price']
#                             dct_data['dbl_min_selling_price']=ins_result_set['dbl_min_selling_price']
#                         lst_accessories.append(dct_data)
#
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'mobile':lst_mobile,'tablet':lst_tablet,'computer':lst_computer,'accessories':lst_accessories})
#
#
#                 elif chr_company_type == "MAINTENANCE":
#                     dct_result_data = fun_maintenance_view(int_enquiry_id,lst_enquiry_data)
#                     #
#
#                     for dct_data in dct_result_data['electric'].all():
#                         lst_electric.append(dct_data._asdict())
#                     for dct_data in dct_result_data['plumbing'].all():
#                         lst_plumbing.append(dct_data._asdict())
#                     for dct_data in dct_result_data['flooring'].all():
#                         lst_flooring.append(dct_data._asdict())
#                     for dct_data in dct_result_data['painting'].all():
#                         lst_painting.append(dct_data._asdict())
#
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'electric':lst_electric,'plumbing':lst_plumbing,'flooring':lst_flooring,'painting':lst_painting})
#                 elif chr_company_type == "TRAVEL AND TOURISM":
#                     dct_result_data = fun_travels_view(int_enquiry_id,lst_enquiry_data)
#
#                     rst_package = dct_result_data['package'].filter(PackageSA.vchr_enquiry_status != 'LOST' ,PackageSA.vchr_enquiry_status != 'BOOKED' , PackageSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     # rst_rooms = rst_rooms.filter(RoomSA.vchr_enquiry_status != 'LOST' ,RoomSA.vchr_enquiry_status != 'BOOKED' , RoomSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     # rst_hotel_sub = rst_hotel_sub.filter(HotelSA.vchr_enquiry_status != 'LOST' ,HotelSA.vchr_enquiry_status != 'BOOKED' , HotelSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_hotel = dct_result_data['hotel'].filter(HotelSA.vchr_enquiry_status != 'LOST' ,HotelSA.vchr_enquiry_status != 'BOOKED' , HotelSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_transport = dct_result_data['transport'].filter(TransportSA.vchr_enquiry_status != 'LOST' ,TransportSA.vchr_enquiry_status != 'BOOKED' , TransportSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_travel_insurance = dct_result_data['travel_insurance'].filter(TravelInsuranceSA.vchr_enquiry_status != 'LOST' ,TravelInsuranceSA.vchr_enquiry_status != 'BOOKED' , TravelInsuranceSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_visa = dct_result_data['visa'].filter(VisaSA.vchr_enquiry_status != 'LOST' ,VisaSA.vchr_enquiry_status != 'BOOKED' , VisaSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_other = dct_result_data['other'].filter(OtherSA.vchr_enquiry_status != 'LOST' ,OtherSA.vchr_enquiry_status != 'BOOKED' , OtherSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_forex = dct_result_data['forex'].filter(ForexSA.vchr_enquiry_status != 'LOST' ,ForexSA.vchr_enquiry_status != 'BOOKED' , ForexSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_flight = dct_result_data['flights'].filter(FlightsSA.vchr_enquiry_status != 'LOST' ,FlightsSA.vchr_enquiry_status != 'BOOKED' , FlightsSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_train = dct_result_data['train'].filter(TrainSA.vchr_enquiry_status != 'LOST' ,TrainSA.vchr_enquiry_status != 'BOOKED' , TrainSA.vchr_enquiry_status != 'UNQUALIFIED' )
#                     rst_rooms = dct_result_data['rooms']
#                     rst_hotel_sub=session.query(HotelSA.pk_bint_id,HotelSA.dat_check_in,HotelSA.dat_check_out,HotelSA.vchr_city,HotelSA.vchr_nationality,HotelSA.int_rooms,HotelSA.dbl_budget,HotelSA.vchr_star_rating,HotelSA.vchr_meal_type,HotelSA.vchr_remarks,HotelSA.vchr_enquiry_status,HotelSA.dbl_estimated_amount)\
#                                             .join(EnquiryMasterSA,HotelSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                             .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N', HotelSA.vchr_enquiry_status != 'LOST' ,HotelSA.vchr_enquiry_status != 'BOOKED' , HotelSA.vchr_enquiry_status != 'UNQUALIFIED' ).subquery()
#                     rst_kct = dct_result_data['kct'].filter(KctSA.vchr_enquiry_status != 'LOST' ,KctSA.vchr_enquiry_status != 'BOOKED' , KctSA.vchr_enquiry_status != 'UNQUALIFIED' )
#
#                 # rst_rooms = session.query(RoomSA.pk_bint_id,RoomSA.fk_hotel_id,RoomSA.vchr_room_type,RoomSA.int_adults,RoomSA.int_children)\
#                 #                             .join(rst_hotel_sub,RoomSA.fk_hotel_id == rst_hotel_sub.c.pk_bint_id)
#
#
#                     for dct_data in rst_enquiry_Data.all():
#                         lst_enquiry_data.append(dct_data._asdict())
#                     for dct_data in rst_flight.all():
#                         lst_flight.append(dct_data._asdict())
#                     for dct_data in rst_train.all():
#                         lst_train.append(dct_data._asdict())
#                     for dct_data in rst_forex.all():
#                         lst_forex.append(dct_data._asdict())
#                     for dct_data in rst_other.all():
#                         lst_other.append(dct_data._asdict())
#                     for dct_data in rst_visa.all():
#                         lst_visa.append(dct_data._asdict())
#                     for dct_data in rst_travel_insurance.all():
#                         lst_travel_insurance.append(dct_data._asdict())
#                     for dct_data in rst_transport.all():
#                         lst_transport.append(dct_data._asdict())
#                     for dct_data in rst_hotel.all():
#                         lst_hotel.append(dct_data._asdict())
#                     for dct_data in rst_rooms.all():
#                         lst_rooms.append(dct_data._asdict())
#                     for dct_data in rst_package.all():
#                         lst_package.append(dct_data._asdict())
#                     for dct_data in rst_kct.all():
#                         lst_kct.append(dct_data._asdict())
#                     return Response({'status' : '0','enquiry_Data':lst_enquiry_data,'train':lst_train,'flights':lst_flight,'forex':lst_forex,'other':lst_other,'visa':lst_visa,\
#                                     'hotel':lst_hotel,'rooms':lst_rooms,'transport':lst_transport,'travel_insurance':lst_travel_insurance,'package':lst_package,'kct':lst_kct})
#         except Exception as msg:
#             ins_logger.logger.error(msg, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status': '1','data':msg})

# class GetEnquiryId(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             enquiry_number = request.data.get('enquiry_number')
#             int_company_id = request.data.get('company_id')
#             ins_company = CompanyDetails.objects.get(pk_bint_id=int_company_id)
#             if request.data.get('naenq'):
#                 ins_enquiry_check = NaEnquiryMaster.objects.filter(vchr_enquiry_num__iexact =enquiry_number,fk_company = ins_company).values()
#             else:
#                 ins_enquiry_check = EnquiryMaster.objects.filter(chr_doc_status='N',vchr_enquiry_num__iexact = enquiry_number,fk_company = ins_company).values()
#             if request.user.usermodel.fk_group.vchr_name.upper()=='ADMIN':
#                 pass
#             elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
#                 ins_enquiry_check=ins_enquiry_check.filter(fk_branch_id=request.user.usermodel.fk_branch_id)
#             elif request.user.usermodel.int_area_id:
#                 lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#                 ins_enquiry_check = ins_enquiry_check.filter(fk_branch_id__in=lst_branch)
#             else:
#                 ins_enquiry_check=ins_enquiry_check.filter(fk_branch_id=request.user.usermodel.fk_branch_id,fk_assigned_id=request.user.id)


#             if ins_enquiry_check:
#                 int_enquiry_id = ins_enquiry_check[0]['pk_bint_id']
#                 return Response({'status':'success','data':int_enquiry_id})
#             else:
#                 return Response({'status':'failed','data':enquiry_number})

#         except Exception as msg:
#             return Response({'status':'failed','data':''})

# class EnquirySave(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             dct_customer = request.data.get('customerData',0)
#             lst_flight= request.data.get('flightData',0)
#             lst_train= request.data.get('trainData',0)
#             lst_hotel = request.data.get('hotelData',0)
#             lst_package = request.data.get('packageData',0)
#             lst_visa = request.data.get('visaData',0)
#             lst_travelinsurance = request.data.get('travelinsuranceData',0)
#             lst_forex = request.data.get('forexData',0)
#             lst_transport = request.data.get('transportData',0)
#             lst_kct = request.data.get('kctData',0)
#             dct_other = request.data.get('otherData',0)
#             username = request.data.get('username')
#             dct_rating = request.data.get('rating')
#             ins_user = UserModel.objects.get(username = username)
#             #
#             # Customer Save Section
#             if dct_customer != 0:
#                 ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
#                 str_code = ins_document[0].vchr_short_code
#                 int_doc_num = ins_document[0].int_number + 1
#                 ins_document.update(int_number = int_doc_num)
#                 str_number = str(int_doc_num).zfill(4)
#                 str_enquiry_no = str_code + '-' + str_number
#                 int_status = 1
#                 #
#                 if not dct_customer['fk_assigned_id'] :
#                     dct_customer['fk_assigned_id']  = ins_user
#                 else:
#                     dct_customer['fk_assigned_id'] = UserModel.objects.get(id = dct_customer['fk_assigned_id'])
#                 if dct_customer['fk_assigned_id'].id != ins_user.id:
#                     int_status = 0
#                 dat_created = datetime.now()

#                 ins_enquiry = EnquiryMaster.objects.create_enquiry_num(str_enquiry_no)
#                 EnquiryMaster.objects.filter(pk_bint_id = ins_enquiry.pk_bint_id).update(
#                     # vchr_enquiry_num = str_enquiry_no
#                     fk_customer = CustomerModel.objects.get(id = dct_customer['fk_customer_id'])
#                     ,fk_source = Source.objects.get(pk_bint_id=dct_customer['fk_enquiry_source'])
#                     ,vchr_customer_type = dct_customer['vchr_customer_type']
#                     ,fk_assigned = dct_customer['fk_assigned_id']
#                     ,fk_branch = Branch.objects.get(pk_bint_id = dct_customer['fk_branch_id'])
#                     ,bln_sms = dct_customer['bln_sms']
#                     ,chr_doc_status = 'N'
#                     ,fk_created_by = ins_user
#                     ,dat_created_at = dat_created
#                     ,fk_company = ins_user.fk_company
#                 )
#                 # Flight Save Section
#                 if lst_flight !=0:
#                     for dct_flight in lst_flight:
#                         if not dct_flight['int_adults']:
#                             dct_flight['int_adults'] = '0'
#                         if not dct_flight['int_children']:
#                             dct_flight['int_children'] = '0'
#                         if not dct_flight['int_infants']:
#                             dct_flight['int_infants'] = '0'
#                         if not dct_flight['dbl_estimated_amount']:
#                             dct_flight['dbl_estimated_amount'] = '0.0'
#                         if(dct_flight['chr_type_of_travel'] == 'M'):
#                             for ins_flight_itinerary in dct_flight['lst_flight_data']:
#                                 ins_flights = Flights(
#                                     fk_enquiry_master = ins_enquiry
#                                     ,chr_type_of_travel = dct_flight['chr_type_of_travel']
#                                     ,dat_departure = datetime.strptime(ins_flight_itinerary['date'],"%Y-%m-%d")
#                                     ,dat_return = None
#                                     ,vchr_class = dct_flight['vchr_class']
#                                     # ,vchr_airline = dct_flight['vchr_airline']
#                                     ,int_adults = int(dct_flight['int_adults'])
#                                     ,int_children = int(dct_flight['int_children'])
#                                     ,int_infants = int(dct_flight['int_infants'])
#                                     ,vchr_remarks = dct_flight['vchr_remarks']
#                                     ,vchr_enquiry_status = dct_flight.get('vchr_enquiry_status','NEW')
#                                     ,dbl_estimated_amount = float(dct_flight.get('dbl_estimated_amount','0.0'))
#                                     ,fk_source = Airport.objects.get(pk_bint_id = ins_flight_itinerary['fk_source'])
#                                     ,fk_destination = Airport.objects.get(pk_bint_id = ins_flight_itinerary['fk_destination'])
#                                 )
#                                 if dct_flight['fk_airline']:
#                                     ins_flights.fk_airline = AirlineDetails.objects.get(pk_bint_id = int(dct_flight['fk_airline']))
#                                 ins_flights.save()
#                                 ins_flights_follow_up = FlightsFollowup.objects.create(
#                                     fk_flights = ins_flights
#                                     ,vchr_notes = dct_flight['vchr_remarks']
#                                     ,vchr_enquiry_status = dct_flight.get('vchr_enquiry_status','NEW')
#                                     ,int_status = int_status
#                                     ,dbl_amount = float(dct_flight.get('dbl_estimated_amount','0.0'))
#                                     ,fk_user = ins_user
#                                     ,fk_updated_id = ins_user.id
#                                     ,dat_followup = dat_created
#                                     ,dat_updated = dat_created
#                                 )

#                         else:
#                             if dct_flight['dat_return'] == '':
#                                 dat_return_check = None
#                             else:
#                                 dat_return_check = datetime.strptime(dct_flight['dat_return'],"%Y-%m-%d")
#                             ins_flights = Flights(
#                                 fk_enquiry_master = ins_enquiry
#                                 ,chr_type_of_travel = dct_flight['chr_type_of_travel']
#                                 ,dat_departure = datetime.strptime(dct_flight['dat_departure'],"%Y-%m-%d")
#                                 ,dat_return = dat_return_check
#                                 ,vchr_class = dct_flight['vchr_class']
#                                 # ,vchr_airline = dct_flight['vchr_airline']
#                                 ,int_adults = int(dct_flight['int_adults'])
#                                 ,int_children = int(dct_flight['int_children'])
#                                 ,int_infants = int(dct_flight['int_infants'])
#                                 ,vchr_remarks = dct_flight['vchr_remarks']
#                                 ,vchr_enquiry_status = dct_flight.get('vchr_enquiry_status','NEW')
#                                 ,dbl_estimated_amount = float(dct_flight.get('dbl_estimated_amount','0.0'))
#                                 ,fk_source = Airport.objects.get(pk_bint_id = dct_flight['fk_source'])
#                                 ,fk_destination = Airport.objects.get(pk_bint_id = dct_flight['fk_destination'])
#                             )
#                             if dct_flight['fk_airline']:
#                                 ins_flights.fk_airline = AirlineDetails.objects.get(pk_bint_id = int(dct_flight['fk_airline']))
#                             ins_flights.save()
#                             ins_flights_follow_up = FlightsFollowup.objects.create(
#                                     fk_flights = ins_flights
#                                     ,vchr_notes = dct_flight['vchr_remarks']
#                                     ,vchr_enquiry_status = dct_flight.get('vchr_enquiry_status','NEW')
#                                     ,int_status = int_status
#                                     ,dbl_amount = float(dct_flight.get('dbl_estimated_amount','0.0'))
#                                     ,fk_user = ins_user
#                                     ,fk_updated_id = ins_user.id
#                                     ,dat_followup = dat_created
#                                     ,dat_updated = dat_created
#                                 )


#                 # save train section
#                 if lst_train !=0:
#                     for dct_train in lst_train:
#                         if not dct_train['int_adults']:
#                             dct_train['int_adults'] = '0'
#                         if not dct_train['int_children']:
#                             dct_train['int_children'] = '0'
#                         if not dct_train['int_infants']:
#                             dct_train['int_infants'] = '0'
#                         if not dct_train['dbl_estimated_amount']:
#                             dct_train['dbl_estimated_amount'] = '0.0'
#                         if(dct_train['chr_type_of_travel'] == 'M'):
#                             for ins_train_itinerary in dct_train['lst_train_data']:
#                                 ins_train = Train(
#                                     fk_enquiry_master = ins_enquiry
#                                     , chr_type_of_travel = dct_train['chr_type_of_travel']
#                                     ,dat_departure = datetime.strptime(ins_train_itinerary['date'],"%Y-%m-%d")
#                                     ,dat_return = None
#                                     ,vchr_class = dct_train['vchr_class']
#                                     ,vchr_train = dct_train['vchr_train']
#                                     ,int_adults = int(dct_train['int_adults'])
#                                     ,int_children = int(dct_train['int_children'])
#                                     ,int_infants = int(dct_train['int_infants'])
#                                     ,vchr_remarks = dct_train['vchr_remarks']
#                                     ,vchr_enquiry_status = dct_train.get('vchr_enquiry_status','NEW')
#                                     ,dbl_estimated_amount = float(dct_train.get('dbl_estimated_amount','0.0'))
#                                     ,fk_source = Station.objects.get(pk_bint_id = ins_train_itinerary['fk_source'])
#                                     ,fk_destination = Station.objects.get(pk_bint_id = ins_train_itinerary['fk_destination'])
#                                 )
#                                 ins_train.save()
#                                 ins_train_follow_up = TrainFollowup.objects.create(
#                                     fk_train = ins_train
#                                     ,vchr_notes = dct_train['vchr_remarks']
#                                     ,vchr_enquiry_status = dct_train.get('vchr_enquiry_status','NEW')
#                                     ,int_status = int_status
#                                     ,dbl_amount = float(dct_train.get('dbl_estimated_amount','0.0'))
#                                     ,fk_user = ins_user
#                                     ,fk_updated_id = ins_user.id
#                                     ,dat_followup = dat_created
#                                     ,dat_updated = dat_created
#                                 )
#                         else:
#                             if dct_train['dat_return'] == '':
#                                 dat_return_check = None
#                             else:
#                                 dat_return_check = datetime.strptime(dct_train['dat_return'],"%Y-%m-%d")
#                             ins_train = Train(
#                                 fk_enquiry_master = ins_enquiry
#                                 ,chr_type_of_travel = dct_train['chr_type_of_travel']
#                                 ,dat_departure = datetime.strptime(dct_train['dat_departure'],"%Y-%m-%d")
#                                 ,dat_return = dat_return_check
#                                 ,vchr_class = dct_train['vchr_class']
#                                 ,vchr_train = dct_train['vchr_train']
#                                 ,int_adults = int(dct_train['int_adults'])
#                                 ,int_children = int(dct_train['int_children'])
#                                 ,int_infants = int(dct_train['int_infants'])
#                                 ,vchr_remarks = dct_train['vchr_remarks']
#                                 ,vchr_enquiry_status = dct_train.get('vchr_enquiry_status','NEW')
#                                 ,dbl_estimated_amount = float(dct_train.get('dbl_estimated_amount','0.0'))
#                                 ,fk_source = Station.objects.get(pk_bint_id = dct_train['fk_source'])
#                                 ,fk_destination = Station.objects.get(pk_bint_id = dct_train['fk_destination'])
#                             )
#                             ins_train.save()
#                             ins_train_follow_up = TrainFollowup.objects.create(
#                                 fk_train = ins_train
#                                 ,vchr_notes = dct_train['vchr_remarks']
#                                 ,vchr_enquiry_status = dct_train.get('vchr_enquiry_status','NEW')
#                                 ,int_status = int_status
#                                 ,dbl_amount = float(dct_train.get('dbl_estimated_amount','0.0'))
#                                 ,fk_user = ins_user
#                                 ,fk_updated_id = ins_user.id
#                                 ,dat_followup = dat_created
#                                 ,dat_updated = dat_created
#                             )

#                 # Hotel Save Section
#                 ins_package = None
#                 if lst_hotel !=0:
#                     for dct_hotel in lst_hotel:
#                         if dct_hotel['fk_package_id'] == 'false':
#                             ins_package = None
#                         if not dct_hotel['dbl_estimated_amount']:
#                             dct_hotel['dbl_estimated_amount'] = '0.0'
#                         if not dct_hotel['dbl_budget']:
#                             dct_hotel['dbl_budget'] = '0.0'
#                         if not dct_hotel['int_rooms']:
#                             dct_hotel['int_rooms'] = '0'
#                         ins_hotel = Hotel(
#                             fk_enquiry_master = ins_enquiry
#                             ,fk_package = ins_package
#                             ,dat_check_in = datetime.strptime(dct_hotel['dat_check_in'],"%Y-%m-%d")
#                             ,dat_check_out = datetime.strptime(dct_hotel['dat_check_out'],"%Y-%m-%d")
#                             ,vchr_city = dct_hotel['vchr_city']
#                             ,vchr_nationality = dct_hotel['vchr_nationality']
#                             ,int_rooms = int(dct_hotel['int_rooms'])
#                             ,dbl_budget = float(dct_hotel['dbl_budget'])
#                             ,vchr_star_rating = dct_hotel['vchr_star_rating']
#                             ,vchr_meal_type = dct_hotel['vchr_meal_type']
#                             ,vchr_remarks = dct_hotel['vchr_remarks']
#                             ,vchr_enquiry_status = dct_hotel.get('vchr_enquiry_status','NEW')
#                             ,dbl_estimated_amount = float(dct_hotel.get('dbl_estimated_amount','0.0'))
#                         )
#                         ins_hotel.save()
#                         ins_hotel_follow_up = HotelFollowup.objects.create(
#                             fk_hotel = ins_hotel
#                             ,vchr_notes = dct_hotel['vchr_remarks']
#                             ,vchr_enquiry_status = dct_hotel.get('vchr_enquiry_status','NEW')
#                             ,int_status = int_status
#                             ,dbl_amount = float(dct_hotel.get('dbl_estimated_amount','0.0'))
#                             ,fk_user = ins_user
#                             ,fk_updated_id = ins_user.id
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_created
#                         )
#                         for dct_room in dct_hotel['lst_rooms']:
#                             if not dct_room['int_adults']:
#                                 dct_room['int_adults'] = '0'
#                             if not dct_room['int_children']:
#                                 dct_room['int_children'] = '0'
#                             ins_room = Rooms(vchr_room_type = dct_room['vchr_room_type']
#                             ,int_adults = int(dct_room['int_adults'])
#                             ,int_children = int(dct_room['int_children'])
#                             ,fk_hotel = ins_hotel
#                             )
#                             ins_room.save()
#                 # Transport Save Section
#                 if lst_transport !=0:
#                     for dct_transport in lst_transport:
#                         if dct_transport['fk_package_id'] == 'false':
#                             ins_package = None
#                         if not dct_transport['dbl_estimated_amount']:
#                             dct_transport['dbl_estimated_amount'] = '0.0'
#                         date_from = datetime.strptime(dct_transport['dat_from'],"%Y-%m-%d %H:%M")
#                         date_to = datetime.strptime(dct_transport['dat_to'],"%Y-%m-%d %H:%M")
#                         if not dct_transport['int_adults']:
#                             dct_transport['int_adults'] = '0'
#                         if not dct_transport['int_children']:
#                             dct_transport['int_children'] = '0'
#                         if not dct_transport['int_infants']:
#                             dct_transport['int_infants'] = '0'
#                         if not dct_transport['int_seats']:
#                             dct_transport['int_seats'] = '0'
#                         ins_transport = Transport(
#                             fk_enquiry_master = ins_enquiry
#                             ,fk_package = ins_package
#                             ,dat_from = date_from
#                             ,dat_to = date_to
#                             ,vchr_vehical_type = dct_transport['vchr_vehical_type']
#                             ,int_seats = int(dct_transport['int_seats'])
#                             ,int_adults = int(dct_transport['int_adults'])
#                             ,int_children = int(dct_transport['int_children'])
#                             ,int_infants = int(dct_transport['int_infants'])
#                             ,vchr_vehical_preferred = dct_transport['vchr_vehical_preferred']
#                             ,vchr_facility = dct_transport['vchr_facility']
#                             ,vchr_remarks = dct_transport['vchr_remarks']
#                             ,vchr_pick_up = dct_transport['vchr_pick_up']
#                             ,vchr_drop_off = dct_transport['vchr_drop_off']
#                             ,vchr_enquiry_status = dct_transport.get('vchr_enquiry_status','NEW')
#                             ,dbl_estimated_amount = float(dct_transport.get('dbl_estimated_amount','0.0'))
#                         )
#                         ins_transport.save()
#                         ins_transport_follow_up = TransportFollowup.objects.create(
#                             fk_transport = ins_transport
#                             ,vchr_notes = dct_transport['vchr_remarks']
#                             ,vchr_enquiry_status = dct_transport.get('vchr_enquiry_status','NEW')
#                             ,int_status = int_status
#                             ,dbl_amount = float(dct_transport.get('dbl_estimated_amount','0.0'))
#                             ,fk_user = ins_user
#                             ,fk_updated_id = ins_user.id
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_created
#                         )
#                 # Package Save Section
#                 if lst_package !=0:
#                     for dct_package_data in lst_package:
#                         dct_package = dct_package_data.get('packageData',0)
#                         if dct_package !=0:
#                             if not dct_package['int_adults']:
#                                 dct_package['int_adults'] = '0'
#                             if not dct_package['int_children']:
#                                 dct_package['int_children'] = '0'
#                             if not dct_package['int_infants']:
#                                 dct_package['int_infants'] = '0'
#                             if not dct_package['dbl_budget']:
#                                 dct_package['dbl_budget'] = '0.0'
#                             if not dct_package['dbl_estimated_amount']:
#                                 dct_package['dbl_estimated_amount'] = '0.0'
#                             ins_package = Package(
#                                 fk_enquiry_master = ins_enquiry
#                                 ,dat_from = datetime.strptime(dct_package['dat_from'],"%Y-%m-%d")
#                                 ,dat_to = datetime.strptime(dct_package['dat_to'],"%Y-%m-%d")
#                                 ,int_adults = int(dct_package['int_adults'])
#                                 ,int_children = int(dct_package['int_children'])
#                                 ,int_infants = int(dct_package['int_infants'])
#                                 ,dbl_budget = float(dct_package.get('dbl_budget','0.0'))
#                                 ,vchr_sightseeing = dct_package['vchr_sightseeing']
#                                 ,vchr_destination = dct_package['vchr_destination']
#                                 ,vchr_remarks = dct_package['vchr_remarks']
#                                 ,vchr_enquiry_status = dct_package.get('vchr_enquiry_status','NEW')
#                                 ,dbl_estimated_amount = float(dct_package.get('dbl_estimated_amount','0.0'))
#                             )
#                             ins_package.save()
#                             ins_package_follow_up = PackageFollowup.objects.create(
#                                 fk_package = ins_package
#                                 ,vchr_notes = dct_package['vchr_remarks']
#                                 ,vchr_enquiry_status = dct_package.get('vchr_enquiry_status','NEW')
#                                 ,int_status = int_status
#                                 ,dbl_amount = float(dct_package.get('dbl_estimated_amount','0.0'))
#                                 ,fk_user = ins_user
#                                 ,fk_updated_id = ins_user.id
#                                 ,dat_followup = dat_created
#                                 ,dat_updated = dat_created
#                             )

#                             lst_hotel = dct_package_data.get('hotelData',0)
#                             lst_transport = dct_package_data.get('transportData',0)
#                             # Package Hotel Save Section
#                             if lst_hotel !=0:
#                                 for dct_hotel in lst_hotel:
#                                     if not dct_hotel['dbl_estimated_amount']:
#                                         dct_hotel['dbl_estimated_amount'] = '0.0'
#                                     if not dct_hotel['dbl_budget']:
#                                         dct_hotel['dbl_budget'] = '0.0'
#                                     if not dct_hotel['int_rooms']:
#                                         dct_hotel['int_rooms'] = '0'
#                                     ins_hotel = Hotel(
#                                         fk_enquiry_master = ins_enquiry
#                                         ,fk_package = ins_package
#                                         ,dat_check_in = datetime.strptime(dct_hotel['dat_check_in'],"%Y-%m-%d")
#                                         ,dat_check_out = datetime.strptime(dct_hotel['dat_check_out'],"%Y-%m-%d")
#                                         ,vchr_city = dct_hotel['vchr_city']
#                                         ,vchr_nationality = dct_hotel['vchr_nationality']
#                                         ,int_rooms = int(dct_hotel['int_rooms'])
#                                         ,dbl_budget = float(dct_hotel['dbl_budget'])
#                                         ,vchr_star_rating = dct_hotel['vchr_star_rating']
#                                         ,vchr_meal_type = dct_hotel['vchr_meal_type']
#                                         ,vchr_remarks = dct_hotel['vchr_remarks']
#                                         ,vchr_enquiry_status = dct_hotel.get('vchr_enquiry_status','NEW')
#                                         ,dbl_estimated_amount = float(dct_hotel.get('dbl_estimated_amount','0.0'))
#                                     )
#                                     ins_hotel.save()
#                                     ins_hotel_follow_up = HotelFollowup.objects.create(
#                                         fk_hotel = ins_hotel
#                                         ,vchr_notes = dct_hotel['vchr_remarks']
#                                         ,vchr_enquiry_status = dct_hotel.get('vchr_enquiry_status','NEW')
#                                         ,int_status = int_status
#                                         ,dbl_amount = float(dct_hotel.get('dbl_estimated_amount','0.0'))
#                                         ,fk_user = ins_user
#                                         ,fk_updated_id = ins_user.id
#                                         ,dat_followup = dat_created
#                                         ,dat_updated = dat_created
#                                     )
#                                     for dct_room in dct_hotel['lst_rooms']:
#                                         if not dct_room['int_adults']:
#                                             dct_room['int_adults'] = '0'
#                                         if not dct_room['int_children']:
#                                             dct_room['int_children'] = '0'
#                                         ins_room = Rooms(vchr_room_type = dct_room['vchr_room_type']
#                                         ,int_adults = int(dct_room['int_adults'])
#                                         ,int_children = int(dct_room['int_children'])
#                                         ,fk_hotel = ins_hotel
#                                         )
#                                         ins_room.save()
#                             # Package Transport Save Section
#                             if lst_transport !=0:
#                                 for dct_transport in lst_transport:
#                                     date_from = datetime.strptime(dct_transport['dat_from'],"%Y-%m-%d %H:%M")
#                                     date_to = datetime.strptime(dct_transport['dat_to'],"%Y-%m-%d %H:%M")
#                                     if not dct_transport['int_adults']:
#                                         dct_transport['int_adults'] = '0'
#                                     if not dct_transport['int_children']:
#                                         dct_transport['int_children'] = '0'
#                                     if not dct_transport['int_infants']:
#                                         dct_transport['int_infants'] = '0'
#                                     if not dct_transport['int_seats']:
#                                         dct_transport['int_seats'] = '0'
#                                     if not dct_transport['dbl_estimated_amount']:
#                                         dct_transport['dbl_estimated_amount'] = '0.0'
#                                     ins_transport = Transport(
#                                         fk_enquiry_master = ins_enquiry
#                                         ,fk_package = ins_package
#                                         ,dat_from = date_from
#                                         ,dat_to = date_to
#                                         ,vchr_vehical_type = dct_transport['vchr_vehical_type']
#                                         ,int_seats = int(dct_transport['int_seats'])
#                                         ,int_adults = int(dct_transport['int_adults'])
#                                         ,int_children = int(dct_transport['int_children'])
#                                         ,int_infants = int(dct_transport['int_infants'])
#                                         ,vchr_vehical_preferred = dct_transport['vchr_vehical_preferred']
#                                         ,vchr_facility = dct_transport['vchr_facility']
#                                         ,vchr_remarks = dct_transport['vchr_remarks']
#                                         ,vchr_pick_up = dct_transport['vchr_pick_up']
#                                         ,vchr_drop_off = dct_transport['vchr_drop_off']
#                                         ,vchr_enquiry_status = dct_transport.get('vchr_enquiry_status','NEW')
#                                         ,dbl_estimated_amount = float(dct_transport.get('dbl_estimated_amount','0.0'))
#                                     )
#                                     ins_transport.save()
#                                     ins_transport_follow_up = TransportFollowup.objects.create(
#                                         fk_transport = ins_transport
#                                         ,vchr_notes = dct_transport['vchr_remarks']
#                                         ,vchr_enquiry_status = dct_transport.get('vchr_enquiry_status','NEW')
#                                         ,int_status = int_status
#                                         ,dbl_amount = float(dct_transport.get('dbl_estimated_amount','0.0'))
#                                         ,fk_user = ins_user
#                                         ,fk_updated_id = ins_user.id
#                                         ,dat_followup = dat_created
#                                         ,dat_updated = dat_created
#                                     )

#                 #Visa Save Section
#                 if lst_visa !=0:
#                     for dct_visa in lst_visa:
#                         if not dct_visa['int_adults']:
#                             dct_visa['int_adults'] = '0'
#                         if not dct_visa['int_children']:
#                             dct_visa['int_children'] = '0'
#                         if not dct_visa['int_infants']:
#                             dct_visa['int_infants'] = '0'
#                         if not dct_visa['dbl_estimated_amount']:
#                             dct_visa['dbl_estimated_amount'] = '0.0'
#                         if not dct_visa['dbl_duration']:
#                             dct_visa['dbl_duration'] = '0.0'
#                         ins_visa = Visa(
#                             fk_enquiry_master = ins_enquiry
#                             ,vchr_visa_category = dct_visa['vchr_visa_category']
#                             ,vchr_visit_type = dct_visa['vchr_visit_type']
#                             ,vchr_duration_type = dct_visa['vchr_duration_type']
#                             ,dbl_duration = float(dct_visa['dbl_duration'])
#                             ,int_adults = int(dct_visa['int_adults'])
#                             ,int_children = int(dct_visa['int_children'])
#                             ,int_infants = int(dct_visa['int_infants'])
#                             ,vchr_remarks = dct_visa['vchr_remarks']
#                             ,vchr_enquiry_status = dct_visa.get('vchr_enquiry_status','NEW')
#                             ,dbl_estimated_amount = float(dct_visa.get('dbl_estimated_amount','0.0'))
#                             ,fk_country = Countries.objects.get(pk_bint_id = dct_visa['fk_country'])
#                         )
#                         ins_visa.save()
#                         ins_visa_follow_up = VisaFollowup.objects.create(
#                             fk_visa = ins_visa
#                             ,vchr_notes = dct_visa['vchr_remarks']
#                             ,vchr_enquiry_status = dct_visa.get('vchr_enquiry_status','NEW')
#                             ,int_status = int_status
#                             ,dbl_amount = float(dct_visa.get('dbl_estimated_amount','0.0'))
#                             ,fk_user = ins_user
#                             ,fk_updated_id = ins_user.id
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_created
#                         )


#                 #Travel Insurance Save Section
#                 if lst_travelinsurance !=0:
#                     for dct_travelinsurance in lst_travelinsurance:
#                         if not dct_travelinsurance['int_adults']:
#                             dct_travelinsurance['int_adults'] = '0'
#                         if not dct_travelinsurance['int_children']:
#                             dct_travelinsurance['int_children'] = '0'
#                         if not dct_travelinsurance['int_infants']:
#                             dct_travelinsurance['int_infants'] = '0'
#                         if not dct_travelinsurance['dbl_estimated_amount']:
#                             dct_travelinsurance['dbl_estimated_amount'] = '0.0'
#                         ins_travelinsurance = TravelInsurance(
#                             fk_enquiry_master = ins_enquiry
#                             ,vchr_insurance_type = dct_travelinsurance['vchr_insurance_type']
#                             ,dat_from = datetime.strptime(dct_travelinsurance['dat_from'],"%Y-%m-%d")
#                             ,dat_to = datetime.strptime(dct_travelinsurance['dat_to'],"%Y-%m-%d")
#                             ,int_adults = int(dct_travelinsurance['int_adults'])
#                             ,int_children = int(dct_travelinsurance['int_children'])
#                             ,int_infants = int(dct_travelinsurance['int_infants'])
#                             ,vchr_remarks = dct_travelinsurance['vchr_remarks']
#                             ,vchr_enquiry_status = dct_travelinsurance.get('vchr_enquiry_status','NEW')
#                             ,dbl_estimated_amount = float(dct_travelinsurance.get('dbl_estimated_amount','0.0'))
#                         )
#                         ins_travelinsurance.save()
#                         ins_insurance_follow_up = TravelInsuranceFollowup.objects.create(
#                             fk_travel_insurance = ins_travelinsurance
#                             ,vchr_notes = dct_travelinsurance['vchr_remarks']
#                             ,vchr_enquiry_status = dct_travelinsurance.get('vchr_enquiry_status','NEW')
#                             ,int_status = int_status
#                             ,dbl_amount = float(dct_travelinsurance.get('dbl_estimated_amount','0.0'))
#                             ,fk_user = ins_user
#                             ,fk_updated_id = ins_user.id
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_created
#                         )


#                 #Forex Save Section
#                 if lst_forex !=0:
#                     for dct_forex in lst_forex:
#                         if not dct_forex['dbl_estimated_amount']:
#                             dct_forex['dbl_estimated_amount'] = '0.0'
#                         if not dct_forex['dbl_amount']:
#                             dct_forex['dbl_amount'] = '0.0'
#                         ins_forex = Forex(
#                             fk_enquiry_master = ins_enquiry
#                             ,dbl_amount = float(dct_forex['dbl_amount'])
#                             ,vchr_from = dct_forex['vchr_from']
#                             ,vchr_to = dct_forex['vchr_to']
#                             ,vchr_remarks = dct_forex['vchr_remarks']
#                             ,vchr_enquiry_status = dct_forex.get('vchr_enquiry_status','NEW')
#                             ,dbl_estimated_amount = float(dct_forex.get('dbl_estimated_amount','0.0'))
#                         )
#                         ins_forex.save()

#                         ins_forex_follow_up = ForexFollowup.objects.create(
#                             fk_forex = ins_forex
#                             ,vchr_notes = dct_forex['vchr_remarks']
#                             ,vchr_enquiry_status = dct_forex.get('vchr_enquiry_status','NEW')
#                             ,int_status = int_status
#                             ,dbl_amount = float(dct_forex.get('dbl_estimated_amount','0.0'))
#                             ,fk_user = ins_user
#                             ,fk_updated_id = ins_user.id
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_created
#                         )

#                 #kct Save Section
#                 if lst_kct !=0:
#                     for dct_kct_package in lst_kct:
#                         if not dct_kct_package['dbl_estimated_amount']:
#                             dct_kct_package['dbl_estimated_amount'] = '0.0'
#                         ins_kct_package = Kct(
#                             fk_enquiry_master = ins_enquiry
#                             ,fk_kct_package_id = dct_kct_package['fk_kct_package_id']
#                             ,dat_travel = dct_kct_package['dat_travel']
#                             ,int_count = dct_kct_package['int_count']
#                             ,vchr_enquiry_status = dct_kct_package.get('vchr_enquiry_status','NEW')
#                             ,vchr_remarks = dct_kct_package['vchr_remarks']
#                             ,dbl_estimated_amount = float(dct_kct_package.get('dbl_estimated_amount','0.0'))
#                         )
#                         ins_kct_package.save()
#                         ins_kct_follow_up = KctFollowup.objects.create(
#                             fk_kct = ins_kct_package
#                             ,vchr_notes = dct_kct_package['vchr_remarks']
#                             ,vchr_enquiry_status = dct_kct_package.get('vchr_enquiry_status','NEW')
#                             ,int_status = int_status
#                             ,dbl_amount = float(dct_kct_package.get('dbl_estimated_amount','0.0'))
#                             ,fk_user = ins_user
#                             ,fk_updated_id = ins_user.id
#                             ,dat_followup = dat_created
#                             ,dat_updated = dat_created
#                         )

#                 #Other Save Section
#                 if dct_other !=0:
#                     if not dct_other['dbl_estimated_amount']:
#                         dct_other['dbl_estimated_amount'] = '0.0'
#                     ins_other = Other(
#                         fk_enquiry_master = ins_enquiry
#                         ,vchr_description = dct_other['vchr_description']
#                         ,vchr_enquiry_status = dct_other.get('vchr_enquiry_status','NEW')
#                         ,dbl_estimated_amount = float(dct_other.get('dbl_estimated_amount','0.0'))
#                     )
#                     ins_other.save()
#                     ins_other_follow_up = OtherFollowup.objects.create(
#                         fk_other = ins_other
#                         ,vchr_notes = dct_other['vchr_description']
#                         ,vchr_enquiry_status = dct_other.get('vchr_enquiry_status','NEW')
#                         ,int_status = int_status
#                         ,dbl_amount = float(dct_other.get('dbl_estimated_amount','0.0'))
#                         ,fk_user = ins_user
#                         ,fk_updated_id = ins_user.id
#                         ,dat_followup = dat_created
#                         ,dat_updated = dat_created
#                     )
#                 dct_cust_rating = dct_rating.get('customerRating')
#                 vchr_feedback = dct_cust_rating['vchr_feedback']
#                 dbl_rating = dct_cust_rating['dbl_rating']
#                 fk_customer = dct_cust_rating['fk_customer_id']
#                 fk_user = dct_cust_rating['fk_user_id']
#                 ins_rating =  CustomerRating(
#                     vchr_feedback = vchr_feedback
#                     ,dbl_rating = dbl_rating
#                     ,fk_customer = CustomerModel.objects.get(id= fk_customer)
#                     , fk_user = UserModel.objects.get(user_ptr_id = fk_user)
#                 )
#                 ins_rating.save()
#                 str_hash = hash_enquiry(ins_enquiry)
#                 EnquiryMaster.objects.filter(chr_doc_status='N',pk_bint_id = ins_enquiry.pk_bint_id).update(vchr_hash = str_hash)
#                 enquiry_print(str_enquiry_no,request,ins_user)
#                 return Response({'status':'0','result':str_enquiry_no,'enqId':ins_enquiry.pk_bint_id})
#             else:
#                 return Response({'status':'1'})
#         except Exception as e:
#             ins_document = Document.objects.select_for_update().filter(vchr_module_name = 'ENQUIRY',fk_company = ins_user.fk_company)
#             str_code = ins_document[0].vchr_short_code
#             int_doc_num = ins_document[0].int_number
#             int_update_num = int_doc_num - 1
#             str_number = str(int_doc_num).zfill(4)
#             str_enquiry_no = str_code + '-' + str_number
#             ins_document.update(int_number = int_update_num)
#             EnquiryMaster.objects.filter(chr_doc_status='N',vchr_enquiry_num = str_enquiry_no).update(chr_doc_status='D')
#             return Response({'status':'1','data':str(e)})


# def fun_travels_data(int_company):
#     session = Session()


#     rst_flight = session.query(FlightsSA.fk_enquiry_master_id.label("FK_Enquery"),FlightsSA.vchr_enquiry_status.label("status"),literal("Flight").label("vchr_service"),)\
#                         .join(EnquiryMasterSA,and_(FlightsSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_train = session.query(TrainSA.fk_enquiry_master_id.label("FK_Enquery"),TrainSA.vchr_enquiry_status.label("status"),literal("Train").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(TrainSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Forex = session.query(ForexSA.fk_enquiry_master_id.label("FK_Enquery"),ForexSA.vchr_enquiry_status.label("status"),literal("Forex").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(ForexSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Hotel = session.query(HotelSA.fk_enquiry_master_id.label("FK_Enquery"),HotelSA.vchr_enquiry_status.label("status"),literal("Hotel").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(HotelSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Other = session.query(OtherSA.fk_enquiry_master_id.label("FK_Enquery"),OtherSA.vchr_enquiry_status.label("status"),literal("Other").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(OtherSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Transport = session.query(TransportSA.fk_enquiry_master_id.label("FK_Enquery"),TransportSA.vchr_enquiry_status.label("status"),literal("Transport").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(TransportSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_TravelInsurance = session.query(TravelInsuranceSA.fk_enquiry_master_id.label("FK_Enquery"),TravelInsuranceSA.vchr_enquiry_status.label("status"),literal("Travel Insurance").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(TravelInsuranceSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Visa = session.query(VisaSA.fk_enquiry_master_id.label("FK_Enquery"),VisaSA.vchr_enquiry_status.label("status"),literal("Visa").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(VisaSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Package = session.query(PackageSA.fk_enquiry_master_id.label("FK_Enquery"),PackageSA.vchr_enquiry_status.label("status"),literal("Package").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(PackageSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))

#     rst_Kct = session.query(KctSA.fk_enquiry_master_id.label("FK_Enquery"),KctSA.vchr_enquiry_status.label("status"),literal("Kerala City Tour").label("vchr_service"),)\
#                 .join(EnquiryMasterSA,and_(KctSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))
#     rst_data = rst_flight.union_all(rst_train, rst_Forex,rst_Hotel,rst_Other,rst_Transport,rst_TravelInsurance,rst_Visa,rst_Package,rst_Kct).subquery()
#     session.close()
#     return (rst_data)

# def fun_software_data(int_company):
#     session = Session()
#     rst_enquiry_track = session.query(EnquiryTrackSA.fk_enquiry_master_id.label("FK_Enquery"),EnquiryTrackSA.vchr_enquiry_status.label("status"),literal("Enquiry Track").label("vchr_service"),)\
#                  .join(EnquiryMasterSA,and_(EnquiryTrackSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))
#     rst_accounting_software  = session.query(AccountingSoftwareSA.fk_enquiry_master_id.label("FK_Enquery"),AccountingSoftwareSA.vchr_enquiry_status.label("status"),literal("Accounting Software").label("vchr_service"),)\
#                  .join(EnquiryMasterSA,and_(AccountingSoftwareSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))
#     rst_hr_solutions  = session.query(HrSolutionsSA.fk_enquiry_master_id.label("FK_Enquery"),HrSolutionsSA.vchr_enquiry_status.label("status"),literal("HR Solutions").label("vchr_service"),)\
#                  .join(EnquiryMasterSA,and_(HrSolutionsSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))
#     rst_employee_management  = session.query(EmployeeManagementSA.fk_enquiry_master_id.label("FK_Enquery"),EmployeeManagementSA.vchr_enquiry_status.label("status"),literal("Employee Management").label("vchr_service"),)\
#                  .join(EnquiryMasterSA,and_(EmployeeManagementSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.fk_company_id == int(int_company)))
#     rst_data = rst_enquiry_track.union_all(rst_accounting_software,rst_hr_solutions,rst_employee_management).subquery()
#     session.close()
#     return (rst_data)


# def fun_automobile_data():
#     session = Session()
#     rst_hatchback = session.query(literal("Hatchback").label("vchr_service"),HatchbackEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),HatchbackEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_sedan = session.query(literal("Sedan").label("vchr_service"),SedanEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),SedanEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_suv = session.query(literal("Suv").label("vchr_service"),SuvEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),SuvEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#     rst_data = rst_hatchback.union_all(rst_sedan,rst_suv).subquery()
#     session.close()
#     return rst_data


# class BranchReport(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             session = Session()
#             int_company = request.data['company_id']
#             ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
#             lst_branch = list(Branch.objects.filter(fk_company_id = ins_company[0].pk_bint_id).values())
#             fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#             todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#             if ins_company[0].fk_company_type.vchr_company_type == 'TRAVEL AND TOURISM':
#                 rst_data = fun_travels_data(int_company)
#             elif ins_company[0].fk_company_type.vchr_company_type == 'SOFTWARE':
#                 rst_data = fun_software_data(int_company)
#             elif ins_company[0].fk_company_type.vchr_company_type == 'MOBILE':
#                 rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
#             elif ins_company[0].fk_company_type.vchr_company_type == 'AUTOMOBILE':
#                 session = Session()
#                 rst_hatchback = session.query(literal("Hatchback").label("vchr_service"),HatchbackEnquirySA.vchr_enquiry_status.label('status'),HatchbackEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_sedan = session.query(literal("Sedan").label("vchr_service"),SedanEnquirySA.vchr_enquiry_status.label('status'),SedanEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_suv = session.query(literal("Suv").label("vchr_service"),SuvEnquirySA.vchr_enquiry_status.label('status'),SuvEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_data = rst_hatchback.union_all(rst_sedan,rst_suv).subquery()
#             rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,BranchSA.vchr_name.label('branch_name'),BranchSA.pk_bint_id.label('branch_id'),\
#                                     rst_data.c.vchr_service, CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),rst_data.c.status,\
#                                     CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
#                                     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == int_company )\
#                                     .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
#                                     .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                                     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#                                     .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
#                                     .join(BranchSA, EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id )
#             if request.data.get('branch'):
#                 rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(tuple(request.data.get('branch'))))

#             rst_table  = rst_enquiry.subquery()
#             rst_bar_data = session.query(rst_table.c.branch_name,func.count(rst_table.c.branch_name).label('count'),func.count(case([((rst_table.c.status == 'BOOKED'),rst_table.c.branch_name)],else_=literal_column("NULL"))).label("booked_count")).group_by(rst_table.c.branch_name)
#             lst_branch_count_all = {}
#             lst_booked_branch_count_all = {}
#             for branch in rst_bar_data.all():
#                 lst_branch_count_all[branch.branch_name] = branch.count
#                 lst_booked_branch_count_all[branch.branch_name] = branch.booked_count
#             # lst_branch_count_all=paginate_data(lst_branch_count_all,10)

#             lst_service_count_all = {}
#             lst_booked_service_count_all = {}
#             rst_service_count_all = session.query(rst_table.c.vchr_service.label('service'),func.count(rst_table.c.vchr_service).label('count'),func.count(case([((rst_table.c.status == 'BOOKED'),rst_table.c.vchr_service)],else_=literal_column("NULL"))).label("booked_count")).group_by(rst_table.c.vchr_service)

#             for serv in rst_service_count_all.all():
#                 lst_service_count_all[serv.service] = serv.count
#                 lst_booked_service_count_all[serv.service] = serv.booked_count


#             lst_status_count_all = {}
#             rst_status_count_all = session.query(rst_table.c.status.label('status'),func.count(rst_table.c.status).label('count')).group_by(rst_table.c.status)
#             for status in rst_status_count_all.all():
#                 lst_status_count_all[status.status] = status.count

#             lst_branch_wise_service_count = []
#             lst_branch_wise_status_count = []
#             lst_branch_wise_booked_service_count = []
#             lst_enquiry_data = []
#             dct_service_wise = {}
#             dct_status_wise = {}
#             dct_booked_wise = {}
#             rst_branch_service_count_all = session.query(rst_table.c.branch_name.label('branch_name'),rst_table.c.status.label('status'),rst_table.c.vchr_service.label('vchr_service'),func.count(rst_table.c.vchr_service).label('count')).group_by(rst_table.c.branch_name,rst_table.c.vchr_service,rst_table.c.status)

#             for ins_enquiry in rst_enquiry.all():
#                 lst_enquiry_data.append(ins_enquiry._asdict())

#             for ins_enquiry in rst_branch_service_count_all.all():
#                 dct_temp = ins_enquiry._asdict()
#                 if dct_temp['branch_name'] not in dct_service_wise.keys():
#                     dct_service_wise[dct_temp['branch_name']] = {'count':{dct_temp['vchr_service']:0},'user_status_count_data':{dct_temp['vchr_service']:{dct_temp['status']:0}}}
#                 if dct_temp['vchr_service'] not in dct_service_wise[dct_temp['branch_name']]['count'].keys():
#                     dct_service_wise[dct_temp['branch_name']]['count'][dct_temp['vchr_service']]= 0
#                 dct_service_wise[dct_temp['branch_name']]['count'][dct_temp['vchr_service']] += dct_temp['count']


#                 if dct_temp['vchr_service'] not in dct_service_wise[dct_temp['branch_name']]['user_status_count_data'].keys():
#                     dct_service_wise[dct_temp['branch_name']]['user_status_count_data'][dct_temp['vchr_service']]={}
#                     # dct_service_wise[dct_temp['branch_name']]['count'] = {dct_temp['vchr_service']:1}

#                 if dct_temp['status'] not in dct_service_wise[dct_temp['branch_name']]['user_status_count_data'][dct_temp['vchr_service']].keys():
#                     dct_service_wise[dct_temp['branch_name']]['user_status_count_data'][dct_temp['vchr_service']][dct_temp['status']]= 0
#                 dct_service_wise[dct_temp['branch_name']]['user_status_count_data'][dct_temp['vchr_service']][dct_temp['status']] += dct_temp['count']



#             for key in dct_service_wise.keys():
#                 lst_branch_wise_service_count.append({key:dct_service_wise[key]})

#             rst_branch_status_all = session.query(rst_table.c.branch_name.label('branch_name'),rst_table.c.status.label('status'),func.count(rst_table.c.status).label('count')).group_by(rst_table.c.branch_name,rst_table.c.status)

#             for ins_enquiry in rst_branch_status_all.all():
#                 dct_data = ins_enquiry._asdict()
#                 if dct_data['branch_name'] not in dct_status_wise.keys():
#                     dct_status_wise[dct_data['branch_name']] = {dct_data['status']:0}
#                 if dct_data['status'] not in dct_status_wise[dct_data['branch_name']].keys():
#                     dct_status_wise[dct_data['branch_name']][dct_data['status']]=0
#                 dct_status_wise[dct_data['branch_name']][dct_data['status']] += dct_data['count']
#             for key in dct_status_wise.keys():
#                 lst_branch_wise_status_count.append({key:dct_status_wise[key]})

#             rst_branch_booked_all = session.query(rst_table.c.branch_name.label('branch_name'),rst_table.c.vchr_service.label('vchr_service'),func.count(case([((rst_table.c.status == 'BOOKED'),rst_table.c.vchr_service)],else_=literal_column("NULL"))).label("booked_count")).group_by(rst_table.c.branch_name,rst_table.c.vchr_service)

#             for ins_enquiry in rst_branch_booked_all.all():
#                 dct_temp = ins_enquiry._asdict()
#                 if dct_temp['branch_name'] not in dct_booked_wise.keys():
#                     dct_booked_wise[dct_temp['branch_name']] = {dct_temp['vchr_service']:dct_temp['booked_count']}
#                 if dct_temp['vchr_service'] not in dct_booked_wise[dct_temp['branch_name']].keys():
#                     dct_booked_wise[dct_temp['branch_name']][dct_temp['vchr_service']]=dct_temp['booked_count']
#                 dct_booked_wise[dct_temp['branch_name']][dct_temp['vchr_service']] = dct_temp['booked_count']
#                 # if dct_booked_wise[dct_temp['branch_name']][dct_temp['vchr_service']] == 0:
#                 #     dct_booked_wise[dct_temp['branch_name']] = {}
#             for key in dct_booked_wise.keys():
#                 lst_branch_wise_booked_service_count.append({key:dct_booked_wise[key]})








            # lst_branch_count_all = Counter(tok['branch_name'].title() for tok in lst_enquiry_data)
            # lst_service_count_all = Counter(tok['vchr_service'] for tok in lst_enquiry_data)
            # lst_status_count_all = Counter(tok['status'] for tok in lst_enquiry_data)
            # lst_booked_branch_count_all = Counter(tok['branch_name'].title() for tok in lst_enquiry_data if tok.get('status') == 'BOOKED')
            # lst_booked_service_count_all = Counter(tok['vchr_service'] for tok in lst_enquiry_data if tok.get('status') == 'BOOKED')
            # lst_branch_wise_service_count = []
            # lst_branch_wise_status_count = []
            # lst_branch_wise_booked_service_count = []
            #
            # for branch in lst_branch_count_all.keys():
            #     service_count_data = Counter(tok['vchr_service'] for tok in lst_enquiry_data if tok.get('branch_name').lower() == branch.lower())
            #
            #     user_status_count_data = []
            #     for str_service in  lst_service_count_all.keys():
            #         user_status_count_data.append({str_service:Counter(tok['status'] for tok in lst_enquiry_data if tok.get('branch_name').lower().title() == branch and tok.get('vchr_service') == str_service)})
            #     lst_branch_wise_service_count.append({branch:{'count':service_count_data,'user_status_count_data':user_status_count_data}})
            #
            #     status_count_data = Counter(tok['status'] for tok in lst_enquiry_data if tok.get('branch_name').lower() == branch.lower())
            #     lst_branch_wise_status_count.append({branch:status_count_data})
            #
            #     booked_service_count_data = Counter(tok['vchr_service'] for tok in lst_enquiry_data if tok.get('branch_name').lower() == branch.lower() and tok.get('status') == 'BOOKED')
            #     lst_branch_wise_booked_service_count.append({branch:booked_service_count_data})
        #     session.close()
        #     return JsonResponse({'status': 'success','lst_branch_count_all':lst_branch_count_all, 'lst_service_count_all': lst_service_count_all ,  'lst_status_count_all': lst_status_count_all,
        #             'lst_booked_branch_count_all': lst_booked_branch_count_all,'lst_booked_service_count_all': lst_booked_service_count_all,'lst_branch_wise_service_count': lst_branch_wise_service_count , 'lst_branch_wise_status_count': lst_branch_wise_status_count ,
        #             'lst_branch_wise_booked_service_count': lst_branch_wise_booked_service_count ,
        #             'lst_enquiry_data': lst_enquiry_data, 'lst_branch_data': lst_branch
        #              })
        # except Exception as e:
        #     session.close()
        #     JsonResponse({'status': 'failed'})

# class BranchReportForPiechart(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             session = Session()
#             lst_enquiry_data = []
#             int_company = request.data['company_id']
#             ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
#             selected_branch = request.data.get('branch')
#             blnExcel = request.data.get('excel',False)
#             fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#             todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#             if ins_company[0].fk_company_type.vchr_company_type == 'TRAVEL AND TOURISM':
#                 rst_data = fun_travels_data(int_company)
#             elif ins_company[0].fk_company_type.vchr_company_type == 'SOFTWARE':
#                 rst_data = fun_software_data(int_company)
#             elif ins_company[0].fk_company_type.vchr_company_type == 'AUTOMOBILE':
#                 session = Session()
#                 rst_hatchback = session.query(literal("Hatchback").label("vchr_service"),HatchbackEnquirySA.vchr_enquiry_status.label('status'),HatchbackEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_sedan = session.query(literal("Sedan").label("vchr_service"),SedanEnquirySA.vchr_enquiry_status.label('status'),SedanEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_suv = session.query(literal("Suv").label("vchr_service"),SuvEnquirySA.vchr_enquiry_status.label('status'),SuvEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_data = rst_hatchback.union_all(rst_sedan,rst_suv).subquery()
#             elif ins_company[0].fk_company_type.vchr_company_type == 'MOBILE':
#                 rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"))
#                 rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()

#             rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,BranchSA.vchr_name.label('branch_name'),\
#                                         rst_data.c.vchr_service, CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),rst_data.c.status,\
#                                         CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name') )\
#                                         .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == int_company )\
#                                         .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N'))\
#                                         .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                                         .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#                                         .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
#                                         .join(BranchSA, EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id )
#             if selected_branch:
#                 rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(tuple(selected_branch)))
#             rst_enquiry = rst_enquiry.order_by(desc(EnquiryMasterSA.dat_created_at))

#             lst_enquiry_data = []
#             for ins_enquiry in rst_enquiry.all():
#                 lst_enquiry_data.append(ins_enquiry._asdict())
#             if blnExcel:
#                 lst_excel_data = []
#                 for dct_data in lst_enquiry_data:
#                     dct_temp = OrderedDict()
#                     if selected_branch:
#                         if len(selected_branch)>1:
#                             dct_temp['Branch Name'] = dct_data.get('branch_name')
#                     dct_temp['Enquiry Date'] = str(datetime.strptime(str(dct_data.get('dat_created_at'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
#                     dct_temp['Enquiry Number'] = dct_data.get('vchr_enquiry_num')
#                     dct_temp['Customer Name'] = (dct_data.get('customer_first_name') + " " + dct_data.get('customer_last_name')).title()
#                     dct_temp['Mobile'] = str(dct_data.get('customer_mobile'))
#                     dct_temp['Staff Name'] = (dct_data.get('staff_first_name') + " " + dct_data.get('staff_last_name')).title()
#                     dct_temp['Service'] = dct_data.get('vchr_service')
#                     dct_temp['Enquiry Status'] = dct_data.get('status')
#                     lst_excel_data.append(dct_temp)
#                 fromdate =  request.data['fromdate'][:10].split("-")
#                 todate =  request.data['todate'][:10].split('-')
#                 fromdate.reverse()
#                 todate.reverse()
#                 from_date = "-".join(fromdate)
#                 to_date = "-".join(todate)
#                 lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Enquiry Number'])
#                 if selected_branch:
#                     lst_branch_name = list(Branch.objects.filter(pk_bint_id__in = selected_branch).values_list('vchr_name',flat=True))
#                     if len(selected_branch)>1:
#                         str_branch_name = ",".join(lst_branch_name)
#                         lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Branch Name'])
#                     else:
#                         str_branch_name = lst_branch_name[0]
#                     response = export_excel('branch',str_branch_name,from_date,to_date,lst_excel_data)
#                 else:
#                     ins_branch = 'All'
#                     response = export_excel('branch',ins_branch,from_date,to_date,lst_excel_data)
#                 if response != False:
#                     session.close()
#                     return JsonResponse({'status': 'success', 'path':response})
#                 else:
#                     session.close()
#                     return JsonResponse({'status': 'failure'})
#             else:
#                 session.close()
#                 return JsonResponse({'status': 'success', 'lst_service_count': lst_service_count , 'lst_service_labels': lst_services_labels , 'lst_status_labels': lst_status_labels  , 'lst_status_count': lst_status_count , 'lst_enquiry_data' : lst_enquiry_data   })
#         except Exception as e:
#             session.close()
#             return JsonResponse({'status':'0','data':str(e)})
# class Add_Attachments(APIView):
#     def post(self, request,):
#         try:
#             vchr_image = request.FILES
#             x =EnquiryMaster.objects.filter(chr_doc_status='N',vchr_enquiry_num = request.data['fk_enquiry']).first().pk_bint_id
#             for i in range(len(request.FILES.getlist('files'))):
#                 attachment = AttachmentSerilaizer(data={'fk_enquiry':x,'vchr_logo':request.FILES.getlist('files')[i]})
#                 if attachment.is_valid():
#                      attachment.save()
#                 else:
#                     return JsonResponse({'result':'failed','status':'File Upload Failed'})

#             return JsonResponse({'result':'success','status':'successfully created'})

#         except Exception as e:
#                 return JsonResponse({'result':'failed'})


# class MobileBranchReportTable(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             session = Session()
#             dct_data={}
#             int_company = request.data['company_id']
#             ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
#             lst_branch = list(Branch.objects.filter(fk_company_id = ins_company[0].pk_bint_id).values())
#             fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#             todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#             # todate = todate + timedelta(days = 1)
#             # rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
#             # rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
#             # rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
#             # rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
#             # rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
#             # rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service, CustomerModelSA.cust_fname.label('customer_first_name'),\
#             #     CustomerModelSA.cust_lname.label('customer_last_name'),rst_data.c.status,CustomerModelSA.cust_mobile.label('customer_mobile'),AuthUserSA.id.label('user_id'),AuthUserSA.first_name.label('staff_first_name'),\
#             #     AuthUserSA.last_name.label('staff_last_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name)\
#             #     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == request.data['company_id'])\
#             #     .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id))\
#             #     .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#             #     .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
#             #     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).join(UserSA, AuthUserSA.id == UserSA.user_ptr_id)\
#             #     .join(BrandsSA,BrandsSA.id==rst_data.c.brand_id)\
#             #     .join(ItemsSA,ItemsSA.id==rst_data.c.item_id)

#             rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status.label('status'),ProductsSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
#                                 AuthUserSA.last_name).label('vchr_staff_full_name'),
#                                 EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,func.concat(CustomerModelSA.cust_fname, ' ', CustomerModelSA.cust_lname).label('vchr_full_name'),
#                                 AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
#                                 AuthUserSA.first_name.label('staff_first_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
#                                 UserSA.fk_brand_id,UserSA.dat_resignation_applied,
#                                 # case([(UserSA.fk_brand_id > 0,literal_column("'promoter'"))],
#                                 #     else_=literal_column("'not promoter'")).label('is_promoter'),
#                                 case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
#                                     else_=literal_column("'not resigned'")).label("is_resigned"))\
#                                 .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
#                                         cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
#                                         EnquiryMasterSA.fk_company_id == request.user.usermodel.fk_company_id,
#                                         EnquiryMasterSA.chr_doc_status == 'N')\
#                                 .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#                                 .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#                                 .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#                                 .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#                                 .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
#                                 .join(ProductsSA,ProductsSA.id == ItemEnquirySA.fk_product_id)\
#                                 .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
#                                 .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)

#             """Permission wise filter for data"""
#             # if request.user.usermodel.fk_group.vchr_name.upper()=='BRANCH MANAGER':
#             #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
#             # elif request.user.usermodel.int_area_id:
#             #     lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#             #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
#             # else:
#             #     return Response({'status':'failed','reason':'No data'})
#             #
#             if request.user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
#                 pass
#             elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
#                 rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
#             elif request.user.usermodel.int_area_id:
#                 lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
#                 rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
#             else:
#                 session.close()
#                 return Response({'status':'failed','reason':'No data'})

#             if request.data.get('branch'):
#                 rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(tuple(request.data.get('branch'))))

#             # rst_enquiry = reversed(sorted(rst_enquiry, key=lambda k: (k.dat_followup)))

#             if not rst_enquiry.all():
#                 session.close()
#                 return Response({'status':'failled','data':'No Data'})
#             session.close()
#             return Response({'status':'success','data':list(rst_enquiry.all())})
#         except Exception as e:
#             session.close()
#             return Response({'status':'failed','data':str(e)})




# class MobileBranchReport(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             session = Session()
#             dct_data={}
#             int_company = request.data['company_id']
#             ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
#             lst_branch = list(Branch.objects.filter(fk_company_id = ins_company[0].pk_bint_id).values())
#             fromdate =  datetime.strptime(request.data['date_from'][:10] , '%Y-%m-%d' )
#             todate =  datetime.strptime(request.data['date_to'][:10] , '%Y-%m-%d' )
#             # todate = todate + timedelta(days = 1)
#             if request.data.get('show_type'):
#                 str_show_type = 'total_amount'
#             else:
#                 str_show_type = 'int_quantity'


#             # rst_mobile = session.query(literal("Mobile").label("vchr_service"),MobileEnquirySA.vchr_enquiry_status.label('status'),MobileEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),MobileEnquirySA.fk_brand_id.label('brand_id'),MobileEnquirySA.fk_item_id.label('item_id'))
#             # rst_tablet = session.query(literal("Tablet").label("vchr_service"),TabletEnquirySA.vchr_enquiry_status.label('status'),TabletEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),TabletEnquirySA.fk_brand_id.label('brand_id'),TabletEnquirySA.fk_item_id.label('item_id'))
#             # rst_computer = session.query(literal("Computer").label("vchr_service"),ComputersEnquirySA.vchr_enquiry_status.label('status'),ComputersEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),ComputersEnquirySA.fk_brand_id.label('brand_id'),ComputersEnquirySA.fk_item_id.label('item_id'))
#             # rst_accessories = session.query(literal("Accessories").label("vchr_service"),AccessoriesEnquirySA.vchr_enquiry_status.label('status'),AccessoriesEnquirySA.fk_enquiry_master_id.label("FK_Enquery"),AccessoriesEnquirySA.fk_brand_id.label('brand_id'),AccessoriesEnquirySA.fk_item_id.label('item_id'))
#             # rst_data = rst_mobile.union_all(rst_tablet,rst_computer,rst_accessories).subquery()
#             # rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service, CustomerModelSA.cust_fname.label('customer_first_name'),\
#             #     CustomerModelSA.cust_lname.label('customer_last_name'),rst_data.c.status,CustomerModelSA.cust_mobile.label('customer_mobile'),AuthUserSA.id.label('user_id'),AuthUserSA.first_name.label('staff_first_name'),\
#             #     AuthUserSA.last_name.label('staff_last_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name)\
#             #     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,cast(EnquiryMasterSA.dat_created_at,Date) <= todate, EnquiryMasterSA.fk_company_id == request.data['company_id'])\
#             #     .join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id))\
#             #     .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#             #     .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
#             #     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).join(UserSA, AuthUserSA.id == UserSA.user_ptr_id)\
#             #     .join(BrandsSA,BrandsSA.id==rst_data.c.brand_id)\
#             #     .join(ItemsSA,ItemsSA.id==rst_data.c.item_id)



#             # materialized views
#             engine = get_engine()
#             conn = engine.connect()

#             lst_mv_view = []
#             lst_mv_view = request.data.get('lst_mv')

#             if not lst_mv_view:
#                 session.close()
#                 return JsonResponse({'status':'failed', 'reason':'No view list found'})
#             query_set = ""
#             if len(lst_mv_view) == 1:

#                 if request.data['type'].upper() == 'ENQUIRY':

#                     query = "select vchr_enquiry_status as status, sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name, user_id as fk_assigned, staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id, branch_name from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id, branch_name"
#                 else:

#                     query = "select vchr_enquiry_status as status, sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty, vchr_product_name as vchr_service, concat(staff_first_name, ' ',staff_last_name) as vchr_staff_full_name,user_id as fk_assigned,staff_first_name, staff_last_name ,vchr_brand_name, vchr_item_name, is_resigned, promoter, branch_id, product_id, brand_id, branch_name from "+lst_mv_view[0]+" {} group by vchr_enquiry_status ,vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned,staff_first_name, staff_last_name, branch_id, product_id, brand_id, branch_name"

#             else:

#                 if request.data['type'].upper() == 'ENQUIRY':

#                     for data in lst_mv_view:
#                         query_set += "select vchr_enquiry_status as status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty,user_id as fk_assigned,vchr_brand_name,vchr_item_name,promoter,is_resigned, branch_id, product_id, brand_id, branch_name from "+data+" {} group by  vchr_enquiry_status , vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter, is_resigned, branch_id, product_id, brand_id, branch_name union "
#                 else:

#                      for data in lst_mv_view:

#                         query_set +="select vchr_enquiry_status as status,vchr_product_name as vchr_service,concat(staff_first_name,' ',staff_last_name) as vchr_staff_full_name,sum("+str_show_type+") as counts,sum(total_amount) as value,sum(int_quantity) as qty,user_id as fk_assigned, vchr_brand_name, vchr_item_name,promoter,is_resigned,branch_id, product_id, brand_id, branch_name from "+data+" {} group by vchr_enquiry_status, vchr_service, vchr_staff_full_name, fk_assigned, vchr_brand_name, vchr_item_name, promoter,is_resigned,branch_id, product_id, brand_id, branch_name union "

#                 query = query_set.rsplit(' ', 2)[0]

#             # rst_enquiry = session.query(ItemEnquirySA.vchr_enquiry_status.label('status'),func.count(ProductsSA.vchr_product_name).label('counts'),
#             #                     ProductsSA.vchr_product_name.label('vchr_service'),func.concat(AuthUserSA.first_name, ' ',
#             #                     AuthUserSA.last_name).label('vchr_staff_full_name'),
#             #                     EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),
#             #                     AuthUserSA.id.label('user_id'),AuthUserSA.last_name.label('staff_last_name'),
#             #                     AuthUserSA.first_name.label('staff_first_name'),BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
#             #                     UserSA.fk_brand_id,UserSA.dat_resignation_applied,
#             #                     # case([(UserSA.fk_brand_id > 0,literal_column("'promoter'"))],
#             #                     #     else_=literal_column("'not promoter'")).label('is_promoter'),
#             #                     case([(UserSA.dat_resignation_applied < datetime.now(),literal_column("'resigned'"))],
#             #                         else_=literal_column("'not resigned'")).label("is_resigned"))\
#             #                     .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= fromdate,
#             #                             cast(EnquiryMasterSA.dat_created_at,Date) <= todate,
#             #                             EnquiryMasterSA.fk_company_id == request.user.usermodel.fk_company_id,
#             #                             EnquiryMasterSA.chr_doc_status == 'N')\
#             #                     .join(EnquiryMasterSA,ItemEnquirySA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
#             #                     .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
#             #                     .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
#             #                     .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
#             #                     .join(UserSA, AuthUserSA.id == UserSA.user_ptr_id )\
#             #                     .join(ProductsSA,ProductsSA.id == ItemEnquirySA.fk_product_id)\
#             #                     .join(BrandsSA,BrandsSA.id==ItemEnquirySA.fk_brand_id)\
#             #                     .join(ItemsSA,ItemsSA.id==ItemEnquirySA.fk_item_id)\
#             #                     .group_by(ProductsSA.vchr_product_name,BranchSA.vchr_name.label('branch_name'),BrandsSA.vchr_brand_name,ItemsSA.vchr_item_name,
#             #                               ItemEnquirySA.vchr_enquiry_status,AuthUserSA.id,EnquiryMasterSA.fk_assigned_id,
#             #                               UserSA.fk_brand_id,UserSA.dat_resignation_applied)
#             """ data wise filtering """

#             str_filter_data = "where dat_enquiry :: date BETWEEN '"+request.data['date_from']+"' AND '"+request.data['date_to']+"' AND int_company_id = "+int_company+""

#             """Permission wise filter for data"""
#             if request.user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','AUDITOR','AUDITING ADMIN','COUNTRY HEAD','GENERAL MANAGER SALES']:
#                 pass
#             elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
#                 str_filter_data = str_filter_data+" AND branch_id = "+str(request.user.usermodel.fk_branch_id)+""
#                 # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.usermodel.fk_branch_id)
#             elif request.user.usermodel.int_area_id:
#                 lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)

#                 str_filter_data += " AND branch_id IN ("+str(lst_branch)[1:-1]+")"
#                 # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
#             else:
#                 session.close()
#                 return Response({'status':'failed','reason':'No data'})

#             if request.data.get('branch'):

#                 str_filter_data += " AND branch_id IN ("+str(request.data.get('branch'))[1:-1]+")"
#                 # rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(tuple(request.data.get('branch'))))

#             # rst_enquiry = reversed(sorted(rst_enquiry, key=lambda k: (k.dat_followup)))

#             if request.data.get('product'):

#                 str_filter_data += " AND product_id = "+str(request.data.get('product'))+""
#                 # rst_enquiry = rst_enquiry.filter(ItemEnquirySA.fk_product_id == request.data.get('product'))
#             if request.data.get('brand'):

#                 str_filter_data += " AND brand_id = "+str(request.data.get('brand'))+""

#             # import pdb; pdb.set_trace()
#             #for getting user corresponding products
#             lst_user_id =[]
#             lst_user_id.append(request.user.id)

#             lst_user_products = get_user_products(lst_user_id)
#             if lst_user_products:
#                 str_filter_data += " AND product_id in ("+str(lst_user_products)[1:-1]+")"



#             if len(lst_mv_view) == 1:
#                 query = query.format(str_filter_data)
#             else:
#                 query = query.format(str_filter_data,str_filter_data)
#             rst_enquiry = conn.execute(query).fetchall()
#             # import pdb; pdb.set_trace()
#             if not rst_enquiry:
#                 return Response({'status':'failled','data':'No Data'})

#             """structuring for branch report"""
#             if request.data['type'].upper() == 'ENQUIRY':
#                 dct_data = structure_data_for_report_old(request,rst_enquiry)
#             else:
#                 dct_data = structure_data_for_report_new(request,rst_enquiry)

#             session.close()
#             return Response({'status': 'success','data':dct_data})
#         except Exception as e:
#             session.close()
#             return Response({'status':'failed','data':str(e)})

# def key_sort(tup):
#     k,d = tup
#     return d['Enquiry'],d['Sale']
# def paginate_data(dct_data,int_page_legth):
#     dct_paged = {}
#     int_count = 1
#     sorted_dct_data = reversed(sorted(dct_data.items(), key=key_sort))
#     dct_data = OrderedDict(sorted_dct_data)
#     for key in dct_data:
#         if int_count not in dct_paged:
#             dct_paged[int_count]={}
#             dct_paged[int_count][key]=dct_data[key]
#         elif len(dct_paged[int_count]) < int_page_legth:
#             dct_paged[int_count][key]= dct_data[key]
#         else:
#             int_count += 1
#             dct_paged[int_count] ={}
#             dct_paged[int_count][key] = dct_data[key]
#     return dct_paged


# class PendingEnquiryListUser(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):

#         try:
#             #
#             # int_company_id = int(request.data.get('company_id'))
#             # if not int_company_id:
#             #     return Response({'status':'1','data':["No company found"]})
#             # else:
#             # dat_start = request.data.get('start_date')
#             # dat_end = request.data.get('end_date')
#             # if not request.data['_status']:
#             #     if request.data['start_date']:
#             #         dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y').replace(day=1)
#             #     if request.data['end_date']:
#             #         dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')
#             # else:
#             if request.data['start_date']:
#                 dat_start = datetime.strptime(request.data['start_date'],'%d/%m/%Y')
#             if request.data['end_date']:
#                 dat_end = datetime.strptime(request.data['end_date'],'%d/%m/%Y')

#             # int_cust_id=request.data.get('custId')
#             # int_branch_id = request.data.get('branchId')
#             session = Session()
#             lst_enquiry_data = []

#             rst_train = session.query(literal("Train").label("vchr_service"),TrainSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(TrainSA.vchr_enquiry_status != 'LOST' ,TrainSA.vchr_enquiry_status != 'INVOICED' , TrainSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_flight = session.query(literal("Flight").label("vchr_service"),FlightsSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(FlightsSA.vchr_enquiry_status != 'LOST' ,FlightsSA.vchr_enquiry_status != 'BOOKED' , FlightsSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_Forex=session.query(literal("Forex").label("vchr_service"),ForexSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(ForexSA.vchr_enquiry_status != 'LOST' ,ForexSA.vchr_enquiry_status != 'BOOKED' , ForexSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_Hotel=session.query(literal("Hotel").label("vchr_service"),HotelSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(HotelSA.vchr_enquiry_status != 'LOST' ,HotelSA.vchr_enquiry_status != 'BOOKED' , HotelSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_Other=session.query(literal("Other").label("vchr_service"),OtherSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(OtherSA.vchr_enquiry_status != 'LOST' ,OtherSA.vchr_enquiry_status != 'BOOKED' , OtherSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_Transport=session.query(literal("Transport").label("vchr_service"),TransportSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(TransportSA.vchr_enquiry_status != 'LOST' ,TransportSA.vchr_enquiry_status != 'BOOKED' , TransportSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_TravelInsurance=session.query(literal("Travel Insurance").label("vchr_service"),TravelInsuranceSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(TravelInsuranceSA.vchr_enquiry_status != 'LOST' ,TravelInsuranceSA.vchr_enquiry_status != 'BOOKED' , TravelInsuranceSA.vchr_enquiry_status != 'UNQUALIFIED' )
#             rst_Visa=session.query(literal("Visa").label("vchr_service"),VisaSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(VisaSA.vchr_enquiry_status != 'LOST' ,VisaSA.vchr_enquiry_status != 'BOOKED' , VisaSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_Package=session.query(literal("Package").label("vchr_service"),PackageSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(PackageSA.vchr_enquiry_status != 'LOST' ,PackageSA.vchr_enquiry_status != 'BOOKED' , PackageSA.vchr_enquiry_status != 'UNQUALIFIED' )
#             rst_Kct=session.query(literal("Kerala City Tour").label("vchr_service"),KctSA.fk_enquiry_master_id.label("FK_Enquery"))\
#             .filter(KctSA.vchr_enquiry_status != 'LOST' ,KctSA.vchr_enquiry_status != 'BOOKED' , KctSA.vchr_enquiry_status != 'UNQUALIFIED' )

#             rst_data = rst_flight.union_all(rst_train, rst_Forex,rst_Hotel,rst_Other,rst_Transport,rst_TravelInsurance,rst_Visa,rst_Package,rst_Kct).subquery()

#             rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id, EnquiryMasterSA.dat_created_at, EnquiryMasterSA.vchr_enquiry_num, rst_data.c.vchr_service, CustomerSA.cust_fname.label('customer_first_name'), CustomerSA.cust_lname.label('customer_last_name'), CustomerSA.cust_mobile.label('customer_mobile'), AuthUserSA.first_name.label('staff_first_name'), AuthUserSA.last_name.label('staff_last_name') ).join(rst_data,and_(rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.chr_doc_status == 'N')).join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id).join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id).join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id).filter(EnquiryMasterSA.fk_assigned_id == request.data.get('userid')).group_by(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.vchr_enquiry_num,rst_data.c.vchr_service, CustomerSA.cust_fname,rst_data.c.vchr_service,CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,AuthUserSA.first_name,AuthUserSA.last_name)


#             if dat_start:
#                     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.dat_created_at >= dat_start)
#             if dat_end:
#                 rst_enquiry = rst_enquiry.filter(cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end)
#             # if int_cust_id:
#             #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_customer_id == int_cust_id)
#             # if int_branch_id:
#             #     rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == int_branch_id)

#             rst_enquiry = rst_enquiry.order_by(desc(EnquiryMasterSA.dat_created_at))
#             # for a in rst_enquiry.order_by(EnquiryMasterSA.dat_created_at.desc()).all() : a.dat_created_at
#             dct_enquiries = {}
#             for dct_data in rst_enquiry.all():
#                 if dct_data.vchr_enquiry_num == dct_enquiries.get('enquiry'):
#                     dct_enquiries['services'].append(dct_data._asdict()['vchr_service'])
#                 else:
#                     if dct_enquiries == {}:
#                         dct_enquiries = {'enquiry_id':dct_data._asdict()['pk_bint_id'],'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
#                     else:
#                         lst_enquiry_data.append(dct_enquiries)
#                         dct_enquiries = {'enquiry_id':dct_data._asdict()['pk_bint_id'],'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
#             lst_enquiry_data.append(dct_enquiries)
#             #             dct_enquiries = {'enquiry':dct_data._asdict()['vchr_enquiry_num'],'date':dct_data._asdict()['dat_created_at'],'customer_name':dct_data._asdict()['customer_first_name']+' '+dct_data._asdict()['customer_last_name'],'customer_contact':dct_data._asdict()['customer_mobile'],'staff_name':dct_data._asdict()['staff_first_name']+' '+dct_data._asdict()['staff_last_name'],'services':[dct_data._asdict()['vchr_service']]}
#             session.close()
#             return Response({'status':'0','data':lst_enquiry_data,})
#         except Exception as e:
#             session.close()
#             # ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':'1','data':[str(e)]})

# class AssignEnquiry(APIView):
#     def post(self,request):
#         try:
#             for dct_data in request.data['status']:
#                 if dct_data['status'] == True:
#                     ins_enquiry = EnquiryMaster.objects.filter(pk_bint_id = dct_data['id'])
#                     ins_enquiry.update(fk_assigned_id = request.data.get('assigneeid'))
#             return Response({'status':'success'})
#         except Exception as e:
#             return Response({'status':'failled','data':str(e)})


class EnquiryList(APIView):
    permission_classes=[IsAuthenticated]


    def post(self,request):

        try:
            # import pdb; pdb.set_trace()

            session = Session()


            int_company_id = int(request.data.get('company_id'))
            int_pending = int(request.data.get('int_pending'))
            lst_branch=[]
            if not int_company_id:
                return Response({'status':'1','data':["No compoany found"]})
            else:
                if not request.data['start_date'] and not request.data['end_date'] and int_pending:
                    dat_start=datetime.strptime('2017-01-01','%Y-%m-%d')
                    dat_end=datetime.now()

                # elif not request.data['_status']:
                #     dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y').replace(day=1)
                #     dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')

                else:
                    dat_start = datetime.strptime(request.data['start_date'],'%a %b %d %Y')
                    dat_end = datetime.strptime(request.data['end_date'],'%a %b %d %Y')
                lst_enquiry_data = []
                int_cust_id=request.data.get('custId')
                int_branch_id = request.data.get('branchId')
                if not request.user.userdetails.fk_group.vchr_name.upper() in ['ASSISTANT MANAGER - ONLINE FINANCE','ECOMMERCE','EXECUTIVE E COMMERCE AND ONLINE MARKETING','VIRTUAL','FINANCIER','BAJAJ ONLINE','MODERN TRADE HEAD']:
                    #These are the statuses which are excluded in pending enquiries
                    lst_statuses= ["LOST","BOOKED","UNQUALIFIED","INVOICED","CONVERTED"]
                    rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                                CustomerSA.vchr_name.label('customer'),\
                                                # CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                                AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name'),\
                                                ItemEnquirySA.vchr_enquiry_status,ProductsSA.vchr_name.label('service'),BranchSA.vchr_name.label('branch_name'),\
                                                ItemSA.vchr_item_code.label('vchr_item_code'),CustomerSA.int_mobile.label('cust_mobile'),\
                                                BrandSA.vchr_name.label('vchr_brand_name'))\
                                                .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                                .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.pk_bint_id)\
                                                .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                                .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                                .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.pk_bint_id)\
                                                .join(ItemSA,ItemSA.pk_bint_id == ItemEnquirySA.fk_item_id)\
                                                .join(BrandSA,ItemSA.fk_brand_id == BrandSA.pk_bint_id)\
                                                .filter(EnquiryMasterSA.dat_created_at >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end,\
                                                 EnquiryMasterSA.fk_company_id == int_company_id)\
                                                .order_by(desc(EnquiryMasterSA.dat_created_at))

                    if request.user.userdetails.fk_group.vchr_name.upper() in ['ADMIN','FINANCE ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD']:
                        pass
                    elif request.user.userdetails.fk_group.vchr_name.upper() == 'INTERNAL AUDITOR':
                        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                    elif request.user.userdetails.fk_group.vchr_name.upper()=='CALL CENTER':
                        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_created_by_id==request.user.id)
                    elif request.user.userdetails.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == request.user.userdetails.fk_branch_id)
                    elif request.user.userdetails.int_area_id:
                        lst_branch=show_data_based_on_role(request.user.userdetails.fk_group.vchr_name,request.user.userdetails.int_area_id)
                        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id.in_(lst_branch))
                    # elif request.user.usermodel.fk_group.vchr_name.upper() =='BALL GAME ADMIN':
                    #     rst_enquiry = rst_enquiry.filter(ItemEnquirySA.vchr_enquiry_status=='PARTIALLY PAID',EnquiryMasterSA.fk_branch_id== request.user.usermodel.fk_branch_id)
                    else:
                        rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id== request.user.userdetails.fk_branch_id,EnquiryMasterSA.fk_assigned_id==request.user.id)
                    if int_pending:
                        rst_enquiry = rst_enquiry.filter(ItemEnquirySA.vchr_enquiry_status.notin_(lst_statuses))
                else:
                    if request.user.userdetails.fk_group.vchr_name.upper() in ['ASSISTANT MANAGER - ONLINE FINANCE','ECOMMERCE','EXECUTIVE E COMMERCE AND ONLINE MARKETING','VIRTUAL','BAJAJ ONLINE']:
                        rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                                    case([(CustomerSA.cust_fname == None ,EnquiryFinanceSA.vchr_name_in_card)],else_=func.concat(CustomerSA.cust_fname, ' ', CustomerSA.cust_lname)).label('customer'),\
                                                    # CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                                    AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name'),BranchSA.vchr_name.label('branch_name'),\
                                                    ItemEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ProductsSA.vchr_product_name.label('service'),\
                                                    ItemSA.vchr_item_code.label('vchr_item_code'),CustomerSA.cust_mobile.label('cust_mobile'),\
                                                    BrandSA.vchr_brand_name.label('vchr_brand_name'))\
                                                    .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                                    .outerjoin(EnquiryFinanceSA,EnquiryMasterSA.pk_bint_id == EnquiryFinanceSA.fk_enquiry_master_id)\
                                                    .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                                    .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                                    .join(UserSA, UserSA.user_ptr_id == AuthUserSA.id)\
                                                    .join(GroupsSA,GroupsSA.pk_bint_id==UserSA.fk_group_id)\
                                                    .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                                    .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.id)\
                                                    .join(ItemSA,ItemSA.id == ItemEnquirySA.fk_item_id)\
                                                    .join(BrandSA,ItemSA.fk_brand_id == BrandSA.id)\
                                                    .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end,\
                                                     EnquiryMasterSA.fk_company_id == int_company_id)\
                                                    .order_by(desc(EnquiryMasterSA.dat_created_at))\
                                                    .group_by(ItemSA.vchr_item_code,CustomerSA.cust_mobile,BrandSA.vchr_brand_name,EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at, EnquiryMasterSA.vchr_enquiry_num,'customer' , AuthUserSA.first_name, AuthUserSA.last_name, ItemEnquirySA.vchr_enquiry_status, ProductsSA.vchr_product_name,'branch_name')\
                                                    .filter(or_(ItemEnquirySA.vchr_enquiry_status.in_(['CHECK ELIGIBILITY','TO PROCESS','IMEI PENDING','IMEI REQUESTED','IMEI REJECTED','IMAGE PENDING','IMAGE PENDING','PROCESSED']),and_(or_(ItemEnquirySA.vchr_enquiry_status == 'BOOKED',ItemEnquirySA.vchr_enquiry_status == 'INVOICED'),ItemEnquirySA.int_fop == 1)))
                    else:
                        rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,\
                                                    case([(CustomerSA.cust_fname == None ,EnquiryFinanceSA.vchr_name_in_card)],else_=func.concat(CustomerSA.cust_fname, ' ', CustomerSA.cust_lname)).label('customer'),\
                                                    # CustomerSA.cust_fname.label('customer_first_name'),CustomerSA.cust_lname.label('customer_last_name'),\
                                                    AuthUserSA.first_name.label('staff_first_name'),AuthUserSA.last_name.label('staff_last_name'),BranchSA.vchr_name.label('branch_name'),\
                                                    ItemEnquirySA.vchr_enquiry_status.label('vchr_enquiry_status'),ProductsSA.vchr_product_name.label('service'),\
                                                    ItemSA.vchr_item_code.label('vchr_item_code'),CustomerSA.cust_mobile.label('cust_mobile'),\
                                                    BrandSA.vchr_brand_name.label('vchr_brand_name'))\
                                                    .join(ItemEnquirySA,EnquiryMasterSA.pk_bint_id == ItemEnquirySA.fk_enquiry_master_id)\
                                                    .join(EnquiryFinanceSA,EnquiryMasterSA.pk_bint_id == EnquiryFinanceSA.fk_enquiry_master_id)\
                                                    .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                                    .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                                    .join(UserSA, UserSA.user_ptr_id == AuthUserSA.id)\
                                                    .join(GroupsSA,GroupsSA.pk_bint_id==UserSA.fk_group_id)\
                                                    .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                                    .join(ProductsSA,ItemEnquirySA.fk_product_id == ProductsSA.id)\
                                                    .join(ItemSA,ItemSA.id == ItemEnquirySA.fk_item_id)\
                                                    .join(BrandSA,ItemSA.fk_brand_id == BrandSA.id)\
                                                    .filter(cast(EnquiryMasterSA.dat_created_at,Date) >= dat_start,cast(EnquiryMasterSA.dat_created_at,Date) <= dat_end,\
                                                     EnquiryMasterSA.fk_company_id == int_company_id)\
                                                    .order_by(desc(EnquiryMasterSA.dat_created_at))\
                                                    .group_by(ItemSA.vchr_item_code,CustomerSA.cust_mobile,BrandSA.vchr_brand_name,EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at, EnquiryMasterSA.vchr_enquiry_num,'customer' , AuthUserSA.first_name, AuthUserSA.last_name, ItemEnquirySA.vchr_enquiry_status, ProductsSA.vchr_product_name,'branch_name')\
                                                    .filter(or_(ItemEnquirySA.vchr_enquiry_status.in_(['CHECK ELIGIBILITY','TO PROCESS','IMEI PENDING','IMEI REQUESTED','IMEI REJECTED','IMAGE PENDING','IMAGE PENDING','PROCESSED']),and_(or_(ItemEnquirySA.vchr_enquiry_status == 'BOOKED',ItemEnquirySA.vchr_enquiry_status == 'INVOICED'),ItemEnquirySA.int_fop == 1)))

                    # if request.user.usermodel.fk_group.vchr_name.upper()=='BAJAJ ONLINE':
                    #     rst_enquiry =rst_enquiry.filter(GroupsSA.vchr_name=='BAJAJ ONLINE')
                    # import pdb; pdb.set_trace()
                    if request.user.usermodel.fk_group.vchr_name.upper()=='FINANCIER':
                        rst_enquiry =rst_enquiry.filter(EnquiryFinanceSA.fk_financiers_id == request.user.usermodel.fk_financier_id)
                    else:
                        if request.user.usermodel.fk_group.vchr_name.upper() in ['ASSISTANT MANAGER - ONLINE FINANCE','BAJAJ ONLINE','FINANCE SALES ADMIN']:
                            rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.int_customer_type.in_([1]))
                        else:
                            rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.int_customer_type.in_([2,3,4]))
                        # if Financiers.objects.filter(vchr_code__in=['BAJAJ_FIN','ECOMMERCE_FIN']):
                        #     int_fin=list(Financiers.objects.filter(vchr_code__in=['BAJAJ_FIN','ECOMMERCE_FIN']).values_list('pk_bint_id',flat=True))
                        #     rst_enquiry =rst_enquiry.filter(EnquiryFinanceSA.fk_financiers_id.in_(int_fin))
                        # if Financiers.objects.filter(vchr_code='BAJAJ_FIN'):
                        #     int_fin=Financiers.objects.filter(vchr_code='BAJAJ_FIN').values('pk_bint_id').first()['pk_bint_id']
                        #     rst_enquiry =rst_enquiry.filter(EnquiryFinanceSA.fk_financiers_id == int_fin)

                if int_cust_id:
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_customer_id == int_cust_id)
                if int_branch_id:
                    rst_enquiry = rst_enquiry.filter(EnquiryMasterSA.fk_branch_id == int_branch_id)
                dct_enquiries = {}
                for dct_data in rst_enquiry.all():
                    dct_data = dct_data._asdict()

                    if dct_data['vchr_enquiry_num'] == dct_enquiries.get('enquiry'):
                        if dct_data['service'].title() not in dct_enquiries['services']:
                            dct_enquiries['services'].append(dct_data['service'].title())
                        if dct_data['vchr_enquiry_status'].title() not in dct_enquiries['status']:
                            dct_enquiries['status'].append(dct_data['vchr_enquiry_status'].title())
                        if dct_data['vchr_brand_name'].title() not in dct_enquiries['brands']:
                            dct_enquiries['brands'].append(dct_data['vchr_brand_name'].title())
                        if dct_data['vchr_item_code'].title() not in dct_enquiries['items']:
                            dct_enquiries['items'].append(dct_data['vchr_item_code'].title())
                    else:
                        if dct_enquiries == {}:
                            dct_enquiries = {'enquiry_id':dct_data['pk_bint_id'],'enquiry':dct_data['vchr_enquiry_num'],'date':dct_data['dat_created_at'],\
                                            'customer_name':dct_data['customer'],\
                                            # 'customer_name':dct_data['customer_first_name']+' '+dct_data['customer_last_name'],\
                                            'staff_name':dct_data['staff_first_name']+' '+dct_data['staff_last_name'],\
                                            'status':[dct_data['vchr_enquiry_status'].title()],'services':[dct_data['service'].title()],
                                            'brands':[dct_data['vchr_brand_name'].title()],'items':[dct_data['vchr_item_code'].title()],
                                            'customer_mobile':dct_data['cust_mobile']
                                            }
                            if not request.user.userdetails.fk_group.vchr_name.upper() in ['FINANCIER']:
                                dct_enquiries['branch_name']=dct_data['branch_name']
                        else:
                            lst_enquiry_data.append(dct_enquiries)
                            dct_enquiries = {'enquiry_id':dct_data['pk_bint_id'],'enquiry':dct_data['vchr_enquiry_num'],'date':dct_data['dat_created_at'],\
                                             'customer_name':dct_data['customer'],\
                                             # 'customer_name':dct_data['customer_first_name']+' '+dct_data['customer_last_name'],\
                                             'staff_name':dct_data['staff_first_name']+' '+dct_data['staff_last_name'],\
                                             'status':[dct_data['vchr_enquiry_status'].title()],'services':[dct_data['service'].title()],
                                             'brands':[dct_data['vchr_brand_name'].title()],'items':[dct_data['vchr_item_code'].title()],
                                             'customer_mobile':dct_data['cust_mobile']
                                             }
                            if not request.user.userdetails.fk_group.vchr_name.upper() in ['FINANCIER']:
                                dct_enquiries['branch_name']=dct_data['branch_name']
                lst_enquiry_data.append(dct_enquiries)
                session.close()
                return Response({'status':'0','data':lst_enquiry_data,})


        except Exception as e:
            session.close()
            return Response({'status':'1','data':[str(e)]})


# =====================================================================================================
# def get_perm_data_orm(rst_data,user):
#     int_branch_id = user.usermodel.fk_branch_id
#     int_group_id = user.usermodel.fk_group_id
#     ins_group_name = user.usermodel.fk_group.vchr_name
#     # ins_category = SubCategory.objects.get(vchr_sub_category_name = 'ASSIGN').pk_bint_id
#     # ins_permission=GroupPermissions.objects.filter(fk_groups_id = int_group_id,fk_sub_category_id = ins_category).values('bln_add')
#     if ins_group_name.upper()=='BRANCH MANAGER':
#         rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id== int_branch_id)
#     elif ins_group_name.upper()=='TERRITORY MANAGER':
#         ins_territory=Branch.objects.get(pk_bint_id=int_branch_id).fk_territory_id
#         ins_branch=Branch.objects.filter(fk_territory_id=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
#     elif ins_group_name.upper()=='ZONE MANAGER':
#         ins_zone=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id')
#         ins_territory=Territory.objects.filter(fk_zone_id=ins_zone).values_list('pk_bint_id',flat=True)
#         ins_branch=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
#     elif ins_group_name.upper()=='STATE MANAGER':
#         ins_state=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id__fk_state_id')
#         ins_zone=Zone.objects.filter(fk_state_id=ins_state).values_list('pk_bint_id',flat=True)
#         ins_territory=Territory.objects.filter(fk_zone_id__in=ins_zone).values_list('pk_bint_id',flat=True)
#         ins_branch=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
#     elif ins_group_name.upper()=='COUNTRY MANAGER':
#         ins_country=Branch.objects.filter(pk_bint_id=int_branch_id).values('fk_territory_id__fk_zone_id__fk_country_id')
#         ins_state=State.objects.filter(fk_country_id=ins_country).values_list('pk_bint_id',flat=True)
#         ins_zone=Zone.objects.filter(fk_state_id__in=ins_state).values_list('pk_bint_id',flat=True)
#         ins_territory=Territory.objects.filter(fk_zone_id__in=ins_zone).values_list('pk_bint_id',flat=True)
#         int_branch_id=Branch.objects.filter(fk_territory_id__in=ins_territory).values_list('pk_bint_id',flat=True)
#         rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id.in_(ins_branch))
#     else:
#         rst_data = rst_data.filter(EnquiryMasterSA.fk_branch_id== int_branch_id,EnquiryMasterSA.fk_assigned_id==user.id)
#     return rst_data
# ======================================================================================================================
class EnquiryView(APIView):

    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            # import pdb; pdb.set_trace()

            session = Connection()
            int_enquiry_id=request.data["enquiry_id"]
            if not int_enquiry_id or int_enquiry_id == 'undefined' :
                return Response({'status': '1','data':'Enquiry id must be provided'})
            else:
                if not request.user.userdetails.fk_group.vchr_name.upper() in ['ASSISTANT MANAGER - ONLINE FINANCE','ECOMMERCE','EXECUTIVE E COMMERCE AND ONLINE MARKETING','VIRTUAL','FINANCIER','FINANCE ADMIN','BAJAJ ONLINE','MODERN TRADE HEAD']:
                    rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.vchr_remarks,\
                                                CustomerSA.vchr_name.label('cust_fname'),literal('').label('cust_lname'),CustomerSA.int_mobile.label('cust_mobile'),CustomerSA.vchr_email.label('cust_email'),\
                                                literal('').label('cust_alternatemobile'),literal('').label('cust_alternatemail'),literal('').label('cust_contactsrc'),\
                                                EnquiryMasterSA.fk_source_id,EnquiryMasterSA.vchr_customer_type,EnquiryMasterSA.bln_sms,\
                                                ItemEnquiry.c.int_type,ItemEnquiry.c.dbl_gdp_amount,ItemEnquiry.c.dbl_gdew_amount,ItemEnquiry.c.dbl_buy_back_amount,ItemEnquiry.c.dbl_discount_amount,\
                                                ItemEnquiry.c.pk_bint_id,ItemEnquiry.c.dbl_min_price,ItemEnquiry.c.dbl_max_price,\
                                                ItemEnquiry.c.vchr_enquiry_status,ItemEnquiry.c.int_quantity,ItemEnquiry.c.dbl_amount,ItemEnquiry.c.dbl_imei_json,ProductsSA.vchr_name.label('product'),\
                                                ItemEnquiry.c.fk_brand_id.label('fk_brand'),\
                                                ItemEnquiry.c.fk_product_id.label('fk_product'),\
                                                ItemEnquiry.c.fk_item_id.label('fk_item'),\
                                                ItemEnquiry.c.int_quantity,\
                                                ItemEnquiry.c.bln_smart_choice,\
                                                BrandSA.vchr_name.label('vchr_brand_name'),ItemSA.vchr_name.label('vchr_item_name'),\
                                                SourceSA.vchr_source_name,BranchSA.vchr_name,func.concat(AuthUserSA.first_name,' ',AuthUserSA.last_name).label('staff_name'))\
                                                .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.pk_bint_id)\
                                                .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                                .join(ItemEnquiry,EnquiryMasterSA.pk_bint_id == ItemEnquiry.c.fk_enquiry_master_id)\
                                                .join(ProductsSA,ItemEnquiry.c.fk_product_id == ProductsSA.pk_bint_id)\
                                                .join(BrandSA,ItemEnquiry.c.fk_brand_id == BrandSA.pk_bint_id)\
                                                .join(ItemSA,ItemEnquiry.c.fk_item_id == ItemSA.pk_bint_id)\
                                                .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                                                .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)\
                                                .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N' )

                else:
                    rst_enquiry = session.query(EnquiryMasterSA.pk_bint_id,EnquiryMasterSA.dat_created_at,EnquiryMasterSA.vchr_enquiry_num,EnquiryMasterSA.vchr_remarks,\
                                                CustomerSA.cust_fname,CustomerSA.cust_lname,CustomerSA.cust_mobile,CustomerSA.cust_email,\
                                                CustomerSA.cust_alternatemobile,CustomerSA.cust_alternatemail,CustomerSA.cust_contactsrc,\
                                                EnquiryMasterSA.fk_source_id,EnquiryMasterSA.vchr_customer_type,EnquiryMasterSA.bln_sms,EnquiryMasterSA.int_customer_type,\
                                                EnquiryMasterSA.vchr_order_num,EnquiryMasterSA.vchr_reference_num,\
                                                ItemEnquiry.c.pk_bint_id,ItemEnquiry.c.dbl_min_price,ItemEnquiry.c.dbl_max_price,\
                                                ItemEnquiry.c.int_quantity,ItemEnquiry.c.dbl_amount,ItemEnquiry.c.dbl_imei_json,\
                                                ItemEnquiry.c.int_type,ItemEnquiry.c.dbl_gdp_amount,ItemEnquiry.c.dbl_gdew_amount,ItemEnquiry.c.dbl_buy_back_amount,ItemEnquiry.c.dbl_discount_amount,ProductsSA.vchr_product_name.label('product'),\
                                                ItemEnquiry.c.fk_brand_id.label('fk_brand'),\
                                                ItemEnquiry.c.fk_product_id.label('fk_product'),\
                                                ItemEnquiry.c.fk_item_id.label('fk_item'),\
                                                ItemEnquiry.c.int_quantity,\
                                                ItemEnquiry.c.bln_smart_choice,\
                                                BrandSA.vchr_brand_name,ItemSA.vchr_item_name,\
                                                SourceSA.vchr_source_name,BranchSA.vchr_name,\
                                                ItemEnquiry.c.vchr_enquiry_status,EnquiryFinanceSA.pk_bint_id.label('enquiry_finance_id'),EnquiryFinanceSA.vchr_finance_status,\
                                                EnquiryFinanceSA.vchr_remarks.label('finance_remark'),EnquiryFinanceSA.dbl_max_amt,func.concat(AuthUserSA.first_name,' ',AuthUserSA.last_name).label('staff_name'),EnquiryFinanceSA.dbl_max_amt.label('dbl_finance_amt'),\
                                                EnquiryFinanceSA.vchr_name_in_card,EnquiryFinanceSA.vchr_delivery_order_no,func.coalesce(FinanceSchemaSA.vchr_schema,None).label('vchr_schema'),func.coalesce(FinanceSchemaSA.pk_bint_id,None).label('schema_id'))\
                                                .filter(EnquiryMasterSA.pk_bint_id == int_enquiry_id,EnquiryMasterSA.chr_doc_status == 'N' )\
                                                .filter(or_(ItemEnquiry.c.vchr_enquiry_status.in_(['CHECK ELIGIBILITY','TO PROCESS','IMEI PENDING','IMEI REQUESTED','IMEI REJECTED','IMAGE PENDING','IMAGE PENDING','PROCESSED']),and_(or_(ItemEnquiry.c.vchr_enquiry_status == 'BOOKED',ItemEnquiry.c.vchr_enquiry_status == 'INVOICED'),ItemEnquiry.c.int_fop == 1)))\
                                                .outerjoin(EnquiryFinanceSA,EnquiryFinanceSA.fk_enquiry_master_id == EnquiryMasterSA.pk_bint_id)\
                                                .outerjoin(FinanceSchemaSA,FinanceSchemaSA.pk_bint_id == EnquiryFinanceSA.fk_financier_schema_id)\
                                                .join(CustomerSA,EnquiryMasterSA.fk_customer_id == CustomerSA.id)\
                                                .join(AuthUserSA, EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)\
                                                .join(ItemEnquiry,EnquiryMasterSA.pk_bint_id == ItemEnquiry.c.fk_enquiry_master_id)\
                                                .join(ProductsSA,ItemEnquiry.c.fk_product_id == ProductsSA.id)\
                                                .join(BrandSA,ItemEnquiry.c.fk_brand_id == BrandSA.id)\
                                                .join(ItemSA,ItemEnquiry.c.fk_item_id == ItemSA.id)\
                                                .join(SourceSA, EnquiryMasterSA.fk_source_id == SourceSA.pk_bint_id)\
                                                .join(BranchSA,BranchSA.pk_bint_id == EnquiryMasterSA.fk_branch_id)




                dct_enquiries = {}
                dct_enquiry_data = {}
                total_amount = 0
                str_status = ''
                dct_smartdata={}
                lst_exchange =[]
                dct_smartchoice = {}
                for item_data in rst_enquiry.all():
                    item_data=item_data._asdict()
                    dct_exchange = {'vchr_item_name':'','vchr_product_name':''}
                    dct_item={}
                    dct_item['dbl_exchange_amt'] = 0
                    dct_item['item_exchange_id'] = ''
                    dct_item['exchange_item'] = ''
                    dct_item['exchange_product'] = ''
                    dct_item['vchr_exc_imei'] = ''
                    item_data['dbl_buy_back_amount']=item_data['dbl_buy_back_amount'] or 0.0
                    item_data['dbl_discount_amount']=item_data['dbl_discount_amount'] or 0.0
                    bln_smartchoice = False
                    #for buy_backammount updation
                    if item_data['vchr_enquiry_status'] not in ['INVOICED','BOOKED','LOST']:
                        dat_today = datetime.strftime(datetime.now(),'%Y-%m-%d')
                        rst_buyback = list(BuyBack.objects.filter(fk_item_id = item_data['fk_item'],dat_start__lte = dat_today,dat_end__gte = dat_today,int_status = 1).values('dbl_amount'))
                        if rst_buyback:
                            item_data['dbl_buy_back_amount'] = rst_buyback[0]['dbl_amount']
                        # else:
                        #     item_data['dbl_buy_back_amount'] = 0

                    if item_data['bln_smart_choice']:
                        bln_smartchoice = True

                        ins_exchange = session.query(ItemEnquiry.c.pk_bint_id,ItemEnquiry.c.fk_enquiry_master_id,ItemEnquiry.c.vchr_enquiry_status,EnquiryMasterSA.pk_bint_id,\
                                                     ItemExchange.c.pk_bint_id,ItemExchange.c.dbl_exchange_amt,ItemExchange.c.fk_item_id,ItemExchange.c.vchr_filename_json,ItemExchange.c.vchr_exc_imei,ItemsSA.vchr_item_name,ItemsSA.fk_product_id,\
                                                     ProductsSA.vchr_product_name,ItemsSA.fk_brand_id,BrandsSA.vchr_brand_name)\
                                                     .join(ItemExchange,ItemEnquiry.c.pk_bint_id==ItemExchange.c.fk_item_enquiry_id)\
                                                     .join(ItemsSA,ItemExchange.c.fk_item_id==ItemsSA.id)\
                                                     .join(EnquiryMasterSA,ItemEnquiry.c.fk_enquiry_master_id==EnquiryMasterSA.pk_bint_id)\
                                                     .join(ProductsSA,ItemsSA.fk_product_id==ProductsSA.id)\
                                                     .join(BranchSA,EnquiryMasterSA.fk_branch_id == BranchSA.pk_bint_id)\
                                                     .join(BrandsSA,ItemsSA.fk_brand_id==BrandsSA.id)\
                                                     .filter(ItemExchange.c.fk_item_enquiry_id==item_data['pk_bint_id'],ItemEnquiry.c.fk_enquiry_master_id==int_enquiry_id,ItemEnquiry.c.vchr_enquiry_status.in_(['INVOICED','OFFER ADDED','PARTIALLY PAID','BOOKED']))

                        for ex_data in ins_exchange.all():
                            ex_data=ex_data._asdict()
                            dct_item = {}
                            dct_item['exchange_item'] = ex_data['vchr_item_name']
                            dct_item['exchange_product'] = ex_data['vchr_product_name']
                            dct_item['exchange_brand'] = ex_data['vchr_brand_name']
                            dct_item['images'] = ex_data['vchr_filename_json']
                            dct_item['vchr_exc_imei'] = ex_data['vchr_exc_imei']
                            dct_item['dbl_exchange_amt'] = ex_data['dbl_exchange_amt']
                            dct_item['fk_item_exchange_id'] = ex_data['pk_bint_id']
                            lst_exchange.append(dct_item)

                            if ex_data['fk_item_id'] not in dct_smartchoice:
                                dct_smartchoice[ex_data['fk_item_id']]={int(ex_data['dbl_exchange_amt']):ex_data['vchr_filename_json']}
                            else:
                                dct_smartchoice[ex_data['fk_item_id']][int(ex_data['dbl_exchange_amt'])]= ex_data['vchr_filename_json']

                        if item_data['product'].title() not in dct_enquiries:
                            dct_enquiries[item_data['product'].title()] = []
                        if not request.user.userdetails.fk_group.vchr_name.upper() == 'FINANCIER':
                            dct_enquiries[item_data['product'].title()].append({'pk_bint_id':item_data['pk_bint_id'],'vchr_brand_name':item_data['vchr_brand_name'], 'vchr_item_name':item_data['vchr_item_name'],'int_quantity':item_data['int_quantity'],'vchr_enquiry_status':item_data['vchr_enquiry_status'],'vchr_item_code':item_data['fk_item'],'key_amount':int(item_data['dbl_amount']),
                            'int_type':item_data['int_type'],'dbl_gdp':item_data['dbl_gdp_amount'],'dbl_gdew':item_data['dbl_gdew_amount'],'dbl_buyback_amount':item_data['dbl_buy_back_amount'],'dbl_discount_amount':item_data['dbl_discount_amount'],'dbl_imei_json':item_data['dbl_imei_json'],'dbl_amount':item_data['dbl_amount'],'vchr_remarks':'','dbl_min_price':item_data['dbl_min_price'],
                            'dbl_max_price':item_data['dbl_max_price'],'items':lst_exchange,'smartchoice':bln_smartchoice,'dbl_finance_amt':(item_data.get('dbl_finance_amt') or 0)})

                            # if item_data['vchr_enquiry_status'].upper() == 'BOOKED' or item_data['vchr_enquiry_status'].upper() == 'INVOICED':
                            #     total_amount += item_data['dbl_amount'] + item_data['dbl_gdp_amount'] + item_data['dbl_gdew_amount'] - item_data['dbl_buy_back_amount'] - item_data['dbl_discount_amount']

                            if item_data['vchr_enquiry_status'].upper() in ['BOOKED','INVOICED','IMEI REQUESTED','IMEI PENDING','IMAGE PENDING','IMEI REJECTED']:
                                total_amount += item_data['dbl_amount'] + item_data['dbl_gdp_amount'] + item_data['dbl_gdew_amount'] - item_data.get('dbl_buy_back_amount',0.0) - item_data.get('dbl_discount_amount',0.0)
                        else:

                            dct_enquiries[item_data['product'].title()].append({'pk_bint_id':item_data['pk_bint_id'],'vchr_brand_name':item_data['vchr_brand_name'], 'vchr_item_name':item_data['vchr_item_name'],'int_quantity':item_data['int_quantity'],'vchr_enquiry_status':item_data['vchr_enquiry_status'],'int_type':item_data['int_type'],'dbl_gdp':item_data['dbl_gdp_amount'],'vchr_item_code':item_data['fk_item'],'key_amount':int(item_data['dbl_amount']),
                            'dbl_gdew':item_data['dbl_gdew_amount'],'dbl_buyback_amount':item_data['dbl_buy_back_amount'],'dbl_discount_amount':item_data['dbl_discount_amount'],'dbl_imei_json':item_data['dbl_imei_json'],'dbl_amount':item_data['dbl_amount'],'vchr_remarks':'','dbl_min_price':item_data['dbl_min_price'],'dbl_max_price':item_data['dbl_max_price'],'items':lst_exchange,'smartchoice':bln_smartchoice,'dbl_finance_amt':(item_data.get('dbl_finance_amt') or 0)})
                            total_amount += item_data['dbl_amount']



                    # dct_data = item_data._asdict()
                    else:
                        # import pdb;pdb.set_trace()
                        if item_data['product'].title() not in dct_enquiries:
                            dct_enquiries[item_data['product'].title()] = []
                    # dct_enquiries[dct_data['product'].title()].append(dct_data)
                        if not request.user.userdetails.fk_group.vchr_name.upper() == 'FINANCIER':
                            dct_enquiries[item_data['product'].title()].append({'pk_bint_id':item_data['pk_bint_id'],'vchr_brand_name':item_data['vchr_brand_name'],'vchr_item_code':item_data['fk_item'],'key_amount':int(item_data['dbl_amount']), 'vchr_item_name':item_data['vchr_item_name'],'int_quantity':item_data['int_quantity'],'vchr_enquiry_status':item_data['vchr_enquiry_status'],'int_type':item_data['int_type'],'dbl_gdp':item_data['dbl_gdp_amount'],'dbl_gdew':item_data['dbl_gdew_amount'],'dbl_buyback_amount':item_data['dbl_buy_back_amount'],'dbl_discount_amount':item_data['dbl_discount_amount'],'dbl_imei_json':item_data['dbl_imei_json'],'dbl_amount':item_data['dbl_amount'],'vchr_remarks':'','dbl_min_price':item_data['dbl_min_price'],'dbl_max_price':item_data['dbl_max_price'],'items':dct_item,'smartchoice':bln_smartchoice})
                            # if item_data['vchr_enquiry_status'].upper() == 'BOOKED' or item_data['vchr_enquiry_status'].upper() == 'INVOICED':
                            #     total_amount += item_data['dbl_amount'] + item_data['dbl_gdp_amount'] + item_data['dbl_gdew_amount'] - item_data['dbl_buy_back_amount'] - item_data['dbl_discount_amount']

                            if item_data['vchr_enquiry_status'].upper() in ['BOOKED','INVOICED','IMEI REQUESTED','IMEI PENDING','IMAGE PENDING','IMEI REJECTED']:
                                total_amount += item_data['dbl_amount'] + item_data['dbl_gdp_amount'] + item_data['dbl_gdew_amount'] - item_data.get('dbl_buy_back_amount',0.0) - item_data.get('dbl_discount_amount',0.0)
                        else:
                            dct_enquiries[item_data['product'].title()].append({'pk_bint_id':item_data['pk_bint_id'],'vchr_brand_name':item_data['vchr_brand_name'],'vchr_item_code':item_data['fk_item'],'key_amount':int(item_data['dbl_amount']), 'vchr_item_name':item_data['vchr_item_name'],'int_quantity':item_data['int_quantity'],'vchr_enquiry_status':item_data['vchr_enquiry_status'],'int_type':item_data['int_type'],'dbl_gdp':item_data['dbl_gdp_amount'],'dbl_gdew':item_data['dbl_gdew_amount'],'dbl_buyback_amount':item_data['dbl_buy_back_amount'],'dbl_discount_amount':item_data['dbl_discount_amount'],'dbl_imei_json':item_data['dbl_imei_json'],'dbl_amount':item_data['dbl_amount'],'vchr_remarks':'','dbl_min_price':item_data['dbl_min_price'],'dbl_max_price':item_data['dbl_max_price'],'items':dct_item,'smartchoice':bln_smartchoice})
                            total_amount += item_data['dbl_amount']


                dct_customer_data = {}
                if rst_enquiry.all():
                    ins_cust_type = EnquiryMaster.objects.filter(pk_bint_id = int_enquiry_id).values('int_customer_type').first()
                    # if settings.DEBUG:
                        # item_data['dat_created_at']=item_data['dat_created_at']+timedelta(hours=5,minutes=30)
                    dct_customer_data = {'vchr_enquiry_num':item_data['vchr_enquiry_num'],'cust_fname':item_data['cust_fname'],'cust_lname':item_data['cust_lname'],'cust_mobile':item_data['cust_mobile'],'cust_email':item_data['cust_email'],'cust_alternatemobile':item_data['cust_alternatemobile'],'cust_alternatemail':item_data['cust_alternatemail'],'vchr_source_name':item_data['vchr_source_name'],'vchr_remarks':item_data['vchr_remarks'],'cust_contactsrc':item_data['cust_contactsrc'],'bln_sms':item_data['bln_sms'],'vchr_name':item_data['vchr_name'],'dat_created_at':datetime.strftime(item_data['dat_created_at'],'%d/%m/%Y'),'time_created_at':datetime.strftime(item_data['dat_created_at'],'%I:%M:%S %p'),'staff_full_name':item_data['staff_name']}
                    if request.user.userdetails.fk_group.vchr_name.upper() in ['FINANCIER','FINANCE ADMIN']:
                        dct_customer_data['status'] = item_data['vchr_finance_status']
                        dct_customer_data['total_amount'] = total_amount
                        dct_customer_data['finance_id'] = item_data['enquiry_finance_id']
                        dct_customer_data['remark'] = item_data['vchr_remarks']
                        dct_customer_data['dbl_amount'] = item_data['dbl_max_amt']
                        dct_customer_data['finance_schema'] = item_data['vchr_schema']
                        dct_customer_data['schema_id'] = item_data['schema_id']
                        ins_finance_customer = FinanceCustomerDetails.objects.filter(fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num=item_data['vchr_enquiry_num']).values('fk_schema__vchr_schema','vchr_id_type','vchr_id_number','vchr_pan_number','vchr_bank_name','bint_account_number','vchr_branch_name','vchr_cheque_number','vchr_initial_payment_type','dbl_down_payment_amount','dbl_processing_fee','dbl_margin_money','fk_enquiry_finance_id__fk_financiers_id__vchr_name','dbl_dbd_amount','dbl_service_charge','dbl_net_loan_amount','fk_enquiry_finance__dbl_max_amt')
                        dct_customer_data['financier_entry'] = {}
                        dct_customer_data['financier_entry']['status'] = False
                        if ins_finance_customer:
                            dct_customer_data['financier_entry']['status'] = True
                            dct_customer_data['financier_entry']['schema'] = ins_finance_customer[0]['fk_schema__vchr_schema']
                            dct_customer_data['financier_entry']['id_type'] = ins_finance_customer[0]['vchr_id_type']
                            dct_customer_data['financier_entry']['id_number'] = ins_finance_customer[0]['vchr_id_number']
                            dct_customer_data['financier_entry']['pan_number'] = ins_finance_customer[0]['vchr_pan_number']
                            dct_customer_data['financier_entry']['bank_name'] = ins_finance_customer[0]['vchr_bank_name']
                            dct_customer_data['financier_entry']['account_number'] = ins_finance_customer[0]['bint_account_number']
                            dct_customer_data['financier_entry']['branch_name'] = ins_finance_customer[0]['vchr_branch_name']
                            dct_customer_data['financier_entry']['cheque_number'] = ins_finance_customer[0]['vchr_cheque_number']
                            dct_customer_data['financier_entry']['vchr_name_in_card'] = item_data['vchr_name_in_card']
                            dct_customer_data['financier_entry']['vchr_delivery_order_no'] = item_data['vchr_delivery_order_no']
                            dct_customer_data['financier_entry']['initial_payment_type'] = ins_finance_customer[0]['vchr_initial_payment_type']
                            dct_customer_data['financier_entry']['down_payment_amount'] = ins_finance_customer[0]['dbl_down_payment_amount']

                            dct_customer_data['financier_entry']['dbl_processing_fee'] = ins_finance_customer[0]['dbl_processing_fee']
                            dct_customer_data['financier_entry']['dbl_margin_money'] = ins_finance_customer[0]['dbl_margin_money']
                            dct_customer_data['financier_entry']['dbl_dbd_amount'] = ins_finance_customer[0]['dbl_dbd_amount']
                            dct_customer_data['financier_entry']['dbl_service_charge'] = ins_finance_customer[0]['dbl_service_charge']
                            dct_customer_data['financier_entry']['dbl_net_loan_amount'] =     ins_finance_customer[0]['fk_enquiry_finance__dbl_max_amt']
                            if ins_cust_type['int_customer_type'] in(1,4):
                                dct_customer_data['financier_entry']['bln_loan_amount_status'] = True
                            else:
                                dct_customer_data['financier_entry']['bln_loan_amount_status'] = False
                            dct_customer_data['financier_entry']['dbl_net_loan_amount_bajaj_online'] = ins_finance_customer[0]['dbl_net_loan_amount']
                            dct_customer_data['financier_entry']['vchr_finance'] =  ins_finance_customer[0].get('fk_enquiry_finance_id__fk_financiers_id__vchr_name')


                    # if request.user.usermodel.fk_group.vchr_name.upper() == 'BRANCH MANAGER':
                    else:

                        dct_customer_data['status'] = 'PENDING'
                        rst_finance_enquiry = session.query(EnquiryFinanceSA.vchr_name_in_card,EnquiryFinanceSA.vchr_delivery_order_no,EnquiryFinanceSA.dbl_max_amt,EnquiryFinanceSA.vchr_remarks,EnquiryFinanceSA.vchr_finance_status,EnquiryFinanceSA.pk_bint_id,func.coalesce(FinanceSchemaSA.vchr_schema,None).label('vchr_schema'),func.coalesce(FinanceSchemaSA.pk_bint_id,None).label('schema_id'))\
                                                            .filter(and_(EnquiryFinanceSA.fk_enquiry_master_id == int_enquiry_id))\
                                                            .outerjoin(FinanceSchemaSA,EnquiryFinanceSA.fk_financier_schema_id == FinanceSchemaSA.pk_bint_id)\
                                                            .filter(or_(EnquiryFinanceSA.int_status!=1,EnquiryFinanceSA.int_status==None))
                        if rst_finance_enquiry.all():
                            dct_finance = rst_finance_enquiry.first()._asdict()
                            dct_customer_data['remark'] = dct_finance['vchr_remarks']
                            dct_customer_data['dbl_amount'] = dct_finance['dbl_max_amt']
                            dct_customer_data['finance_id'] = dct_finance['pk_bint_id']
                            dct_customer_data['status'] = dct_finance['vchr_finance_status']
                            dct_customer_data['finance_schema'] = dct_finance['vchr_schema']
                            dct_customer_data['schema_id'] = dct_finance['schema_id']
                            dct_customer_data['vchr_name_in_card'] = dct_finance['vchr_name_in_card']
                            dct_customer_data['vchr_delivery_order_no'] = dct_finance['vchr_delivery_order_no']

                        ins_finance_customer = FinanceCustomerDetails.objects.filter(fk_enquiry_finance__fk_enquiry_master__vchr_enquiry_num=item_data['vchr_enquiry_num']).values('fk_enquiry_finance_id__vchr_delivery_order_no','fk_enquiry_finance_id__vchr_name_in_card','fk_schema__vchr_schema','vchr_id_type','vchr_id_number','vchr_pan_number','vchr_bank_name','bint_account_number','vchr_branch_name','vchr_cheque_number','vchr_initial_payment_type','dbl_down_payment_amount','dbl_processing_fee','dbl_margin_money','dbl_dbd_amount','dbl_service_charge','dbl_net_loan_amount','fk_enquiry_finance__dbl_max_amt','fk_enquiry_finance_id__fk_financiers_id__vchr_name')
                        dct_customer_data['financier_entry'] = {}
                        dct_customer_data['financier_entry']['status'] = False
                        if ins_finance_customer:
                            dct_customer_data['financier_entry']['status'] = True
                            dct_customer_data['financier_entry']['schema'] = ins_finance_customer[0]['fk_schema__vchr_schema']
                            dct_customer_data['financier_entry']['id_type'] = ins_finance_customer[0]['vchr_id_type']
                            dct_customer_data['financier_entry']['id_number'] = ins_finance_customer[0]['vchr_id_number']
                            dct_customer_data['financier_entry']['pan_number'] = ins_finance_customer[0]['vchr_pan_number']
                            dct_customer_data['financier_entry']['bank_name'] = ins_finance_customer[0]['vchr_bank_name']
                            dct_customer_data['financier_entry']['account_number'] = ins_finance_customer[0]['bint_account_number']
                            dct_customer_data['financier_entry']['branch_name'] = ins_finance_customer[0]['vchr_branch_name']
                            dct_customer_data['financier_entry']['cheque_number'] = ins_finance_customer[0]['vchr_cheque_number']
                            dct_customer_data['financier_entry']['vchr_name_in_card'] = ins_finance_customer[0]['fk_enquiry_finance_id__vchr_name_in_card']
                            dct_customer_data['financier_entry']['vchr_delivery_order_no'] = ins_finance_customer[0]['fk_enquiry_finance_id__vchr_delivery_order_no']
                            dct_customer_data['financier_entry']['initial_payment_type'] = ins_finance_customer[0]['vchr_initial_payment_type']
                            dct_customer_data['financier_entry']['down_payment_amount'] = ins_finance_customer[0]['dbl_down_payment_amount']

                            dct_customer_data['financier_entry']['dbl_processing_fee'] = ins_finance_customer[0]['dbl_processing_fee']
                            dct_customer_data['financier_entry']['dbl_margin_money'] = ins_finance_customer[0]['dbl_margin_money']
                            dct_customer_data['financier_entry']['dbl_dbd_amount'] = ins_finance_customer[0]['dbl_dbd_amount']
                            dct_customer_data['financier_entry']['dbl_service_charge'] = ins_finance_customer[0]['dbl_service_charge']
                            dct_customer_data['financier_entry']['dbl_net_loan_amount'] = ins_finance_customer[0]['fk_enquiry_finance__dbl_max_amt']
                            if ins_cust_type['int_customer_type'] in(1,4):
                                dct_customer_data['financier_entry']['bln_loan_amount_status'] = True
                            else:
                                dct_customer_data['financier_entry']['bln_loan_amount_status'] = False

                            dct_customer_data['financier_entry']['dbl_net_loan_amount_bajaj_online'] = ins_finance_customer[0]['dbl_net_loan_amount']
                            dct_customer_data['financier_entry']['vchr_finance'] =  ins_finance_customer[0].get('fk_enquiry_finance_id__fk_financiers_id__vchr_name')


                        # dct_customer_data['status'] = str_status


                        dct_customer_data['total_amount'] = total_amount

                lst_enq_fin_image = EnquiryFinanceImages.objects.filter(fk_enquiry_master_id = int_enquiry_id).values_list('pk_bint_id','vchr_bill_image','vchr_delivery_image','vchr_proof1','vchr_proof2')
                bln_edit_approve = False
                # import pdb;pdb.set_trace()
                if request.user.userdetails.fk_department.vchr_code.upper() == 'HOD':
                    bln_edit_approve = True
            session.close()
            return Response({'status' : 0,'dct_enquiry_details':dct_enquiries,'dct_customer_data':dct_customer_data,'lst_enq_fin_image':lst_enq_fin_image,'bln_edit_approve':bln_edit_approve,'dct_smartchoice':dct_smartchoice})

        except Exception as e:
            session.close()
            return Response({'status':1,'data':[str(e)]})


"""structuring for branch report"""
def structure_data_for_report_new(request,rst_enquiry):
    try:
        # import pdb; pdb.set_trace()
        dct_data={}
        dct_data['IN_IT'] = {}

        if request.data['type'] == 'Sale':
            dct_data['BRANCH_SERVICE_BRAND_ITEM']={}

        elif request.data['type'] == 'Enquiry':
            dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']={}

        for ins_data in rst_enquiry:
            """sales -> branch report """
            if request.data['type'] == 'Sale':
                if ins_data.branch_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.status == 'INVOICED':
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value


                elif ins_data.vchr_service.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value


                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value


                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value


                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                elif ins_data.vchr_brand_name.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value


                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                elif ins_data.vchr_item_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]={}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']=ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']=ins_data.value

                else:
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry']+=ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty']+=ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue']+=ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']+=ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']+=ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']+=ins_data.value



            elif request.data['type'] == 'Enquiry':
                """enquiry -> branch report"""
                if ins_data.branch_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]  =  {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value



                elif ins_data.vchr_service.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale']  =  0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_brand_name.title() not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                elif ins_data.vchr_item_name not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty']= 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] = ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] = ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                elif ins_data.status not in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS']:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status] = {}
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = 0
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] = ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] = ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] = ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] = ins_data.value

                else:

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['EnquiryValue']+= ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['EnquiryValue'] += ins_data.value

                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Enquiry'] += ins_data.counts
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryQty'] += ins_data.qty
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['EnquiryValue'] += ins_data.value

                    if ins_data.status == 'INVOICED':

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['SaleValue'] += ins_data.value

                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['Sale'] += ins_data.counts
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleQty'] += ins_data.qty
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][ins_data.branch_name]['SERVICE'][ins_data.vchr_service.title()]['BRANDS'][ins_data.vchr_brand_name.title()]['ITEMS'][ins_data.vchr_item_name]['STATUS'][ins_data.status]['SaleValue'] += ins_data.value



            # import pdb; pdb.set_trace()
        if request.data['type'] == 'Sale':

            """top 5 branch->product->brand->item"""
            dct_data['IN_IT']['BRANCHS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][i]['Sale']),reverse =True)[0]
            top_branch = dct_data['IN_IT']['BRANCHS']
            dct_data['IN_IT']['SERVICE'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][i]['Sale']),reverse =True)[0]
            top_product = dct_data['IN_IT']['SERVICE']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'][i]['Sale']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEMS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][i]['Sale']),reverse =True)[0]

            """paginating"""
            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE']:
                    for key2 in dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS']:
                        dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE']:
                    dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'][key1]['BRANDS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM']:
                dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'][key]['SERVICE'],10)

            dct_data['BRANCH_SERVICE_BRAND_ITEM'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM'],10)


        elif request.data['type'] == 'Enquiry':

            """top 5 branch->product->brand->item->status"""
            dct_data['IN_IT']['BRANCHS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][i]['Enquiry']),reverse =True)[0]
            top_branch = dct_data['IN_IT']['BRANCHS']
            dct_data['IN_IT']['SERVICE'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][i]['Enquiry']),reverse =True)[0]
            top_product = dct_data['IN_IT']['SERVICE']
            dct_data['IN_IT']['BRANDS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][i]['Enquiry']),reverse =True)[0]
            top_brand = dct_data['IN_IT']['BRANDS']
            dct_data['IN_IT']['ITEMS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][i]['Enquiry']),reverse =True)[0]
            top_item = dct_data['IN_IT']['ITEMS']
            dct_data['IN_IT']['STATUS'] = sorted(dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STATUS'], key = lambda i: (dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][top_branch]['SERVICE'][top_product]['BRANDS'][top_brand]['ITEMS'][top_item]['STATUS'][i]['Enquiry']),reverse =True)[0]

            """paginating"""
            # for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
            #     for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
            #         for key2 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']:
            #             for key3 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']:
            #                 dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'][key3]['STATUS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'][key3]['STATUS'],10)
            #
            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
                    for key2 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']:
                        dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'][key2]['ITEMS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
                for key1 in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE']:
                    dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS']=paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'][key1]['BRANDS'],10)

            for key in dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS']:
                dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'][key]['SERVICE'],10)

            dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'] = paginate_data_new(request,dct_data['BRANCH_SERVICE_BRAND_ITEM_STATUS'],10)






        return dct_data
    except Exception as msg:
        return str(msg)


def key_sort_sale_new(tup):
    key,data = tup
    return -data['Sale']
def key_sort_new(tup):
    key,data = tup
    return -data['Enquiry']

def paginate_data_new(request,dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    if request.data.get('type') == 'Sale':
        sorted_dct_data = sorted(dct_data.items(),key= key_sort_sale_new)
    else:
        sorted_dct_data = sorted(dct_data.items(),key= key_sort_new)

    dct_data = OrderedDict(sorted_dct_data)
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



def structure_data_for_report_old(request,rst_enquiry):
    try:
        dct_data={}
        dct_data['branch_all']={}
        dct_data['service_all']={}
        dct_data['brand_all']={}
        dct_data['item_all']={}
        dct_data['status_all']={}
        dct_data['branch_service']={}
        dct_data['branch_brand']={}
        dct_data['branch_item']={}
        dct_data['branch_status']={}
        dct_data['branch_service_brand']={}
        dct_data['branch_service_item']={}
        dct_data['branch_service_status']={}
        dct_data['branch_service_brand_item']={}
        dct_data['branch_service_brand_status']={}
        dct_data['branch_service_brand_item_status']={}
        for ins_data in rst_enquiry:
            if ins_data.branch_name.title() not in dct_data['branch_all']:
                dct_data['branch_all'][ins_data.branch_name.title()]={}
                dct_data['branch_all'][ins_data.branch_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_all'][ins_data.branch_name.title()]['Sale']=0
                dct_data['branch_all'][ins_data.branch_name.title()]['SaleQty']=0
                dct_data['branch_all'][ins_data.branch_name.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_all'][ins_data.branch_name.title()]['Sale'] = ins_data.counts
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleQty'] = ins_data.qty
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleValue'] = ins_data.value

                dct_data['branch_service'][ins_data.branch_name.title()]={}
                dct_data['branch_brand'][ins_data.branch_name.title()]={}
                dct_data['branch_item'][ins_data.branch_name.title()]={}
                dct_data['branch_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=0
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=0
                dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=0
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']=0
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=ins_data.counts
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=ins_data.value
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']=ins_data.value

                dct_data['branch_service_brand'][ins_data.branch_name.title()]={}
                dct_data['branch_service_item'][ins_data.branch_name.title()]={}
                dct_data['branch_service_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=0
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=ins_data.value

                dct_data['branch_service_brand_item'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value

                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
            else:
                dct_data['branch_all'][ins_data.branch_name.title()]['Enquiry']+=ins_data.counts
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['branch_all'][ins_data.branch_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['branch_all'][ins_data.branch_name.title()]['Sale']+=ins_data.counts
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['branch_all'][ins_data.branch_name.title()]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service'][ins_data.branch_name.title()]:
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=0
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=0
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']=ins_data.counts
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Enquiry']+=ins_data.counts
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['Sale']+=ins_data.counts
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleQty']+=ins_data.qty
                        dct_data['branch_service'][ins_data.branch_name.title()][ins_data.vchr_service.title()]['SaleValue']+=ins_data.value
                if ins_data.vchr_brand_name.title() not in dct_data['branch_brand'][ins_data.branch_name.title()]:
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                        dct_data['branch_brand'][ins_data.branch_name.title()][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value
                if ins_data.vchr_item_name.title() not in dct_data['branch_item'][ins_data.branch_name.title()]:
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                        dct_data['branch_item'][ins_data.branch_name.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                if ins_data.status not in dct_data['branch_status'][ins_data.branch_name.title()]:
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']=0
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale'] = ins_data.counts
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty'] = ins_data.qty
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue'] = ins_data.value
                else:
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Enquiry']+=ins_data.counts
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['Sale']+=ins_data.counts
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleQty']+=ins_data.qty
                        dct_data['branch_status'][ins_data.branch_name.title()][ins_data.status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service_brand'][ins_data.branch_name.title()]:
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                    dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]={}
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=ins_data.value
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                else:
                    if ins_data.vchr_brand_name.title() not in dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=0
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=0
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
                    else:
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                        dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                            dct_data['branch_service_brand'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value
                    if ins_data.vchr_item_name.title() not in dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                    else:
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                        dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                            dct_data['branch_service_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                    if ins_data.status not in dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]={}
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']=ins_data.counts
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=0
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=0
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']=ins_data.counts
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']=ins_data.qty
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']=ins_data.value
                    else:

                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Enquiry']+=ins_data.counts
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                        dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['Sale']+=ins_data.counts
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleQty']+=ins_data.qty
                            dct_data['branch_service_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service_brand_item'][ins_data.branch_name.title()]:
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                    dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value
                else:
                    if ins_data.vchr_brand_name.title() not in dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                        dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0
                        # Initialize Enquiry as 1 and Sale as 0
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                        dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0
                        if ins_data.status == 'INVOICED':
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value
                    else:
                        if ins_data.vchr_item_name.title() not in dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]:
                            # Initialize Enquiry as 1 and Sale as 0
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=0
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=0
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=0

                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
                        else:
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                            dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                                dct_data['branch_service_brand_item'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
                        if ins_data.status not in dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]:
                            # Initialize Enquiry as 1 and Sale as 0
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]={}
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=0
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=0
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=0

                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']=ins_data.counts
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']=ins_data.value
                        else:
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Enquiry']+=ins_data.counts
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                            dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                            if ins_data.status == 'INVOICED':
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['Sale']+=ins_data.counts
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleQty']+=ins_data.qty
                                dct_data['branch_service_brand_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.status]['SaleValue']+=ins_data.value
                if ins_data.vchr_service.title() not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()]:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                elif ins_data.vchr_brand_name.title() not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()]:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                elif ins_data.vchr_item_name.title() not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()]:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]={}
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                elif ins_data.status not in dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()]:
                    # Initialize Enquiry as 1 and Sale as 0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]={}
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']=ins_data.value
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=0
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=0

                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']=ins_data.value
                else:
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Enquiry']+=ins_data.counts
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryQty']+=ins_data.qty
                    dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['EnquiryValue']+=ins_data.value
                    if ins_data.status == 'INVOICED':
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['Sale']+=ins_data.counts
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleQty']+=ins_data.qty
                        dct_data['branch_service_brand_item_status'][ins_data.branch_name.title()][ins_data.vchr_service.title()][ins_data.vchr_brand_name.title()][ins_data.vchr_item_name.title()][ins_data.status]['SaleValue']+=ins_data.value
            if ins_data.vchr_service.title() not in dct_data['service_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['service_all'][ins_data.vchr_service.title()]={}
                dct_data['service_all'][ins_data.vchr_service.title()]['Enquiry']=ins_data.counts
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryQty']=ins_data.qty
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryValue']=ins_data.value
                dct_data['service_all'][ins_data.vchr_service.title()]['Sale']=0
                dct_data['service_all'][ins_data.vchr_service.title()]['SaleQty']=0
                dct_data['service_all'][ins_data.vchr_service.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['service_all'][ins_data.vchr_service.title()]['Sale']=ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleQty']=ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleValue']=ins_data.value
            else:
                dct_data['service_all'][ins_data.vchr_service.title()]['Enquiry']+=ins_data.counts
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryQty']+=ins_data.qty
                dct_data['service_all'][ins_data.vchr_service.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['service_all'][ins_data.vchr_service.title()]['Sale']+=ins_data.counts
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleQty']+=ins_data.qty
                    dct_data['service_all'][ins_data.vchr_service.title()]['SaleValue']+=ins_data.value
            if ins_data.vchr_brand_name.title() not in dct_data['brand_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]={}
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']=ins_data.counts
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']=ins_data.value
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=0
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']=ins_data.value
            else:
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Enquiry']+=ins_data.counts
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['brand_all'][ins_data.vchr_brand_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['Sale']+=ins_data.counts
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['brand_all'][ins_data.vchr_brand_name.title()]['SaleValue']+=ins_data.value
            if ins_data.vchr_item_name.title() not in dct_data['item_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['item_all'][ins_data.vchr_item_name.title()]={}
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']=ins_data.counts
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']=ins_data.qty
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']=ins_data.value
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=0
                dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']=0
                dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']=ins_data.value
            else:
                dct_data['item_all'][ins_data.vchr_item_name.title()]['Enquiry']+=ins_data.counts
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryQty']+=ins_data.qty
                dct_data['item_all'][ins_data.vchr_item_name.title()]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['Sale']+=ins_data.counts
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleQty']+=ins_data.qty
                    dct_data['item_all'][ins_data.vchr_item_name.title()]['SaleValue']+=ins_data.value
            if ins_data.status not in dct_data['status_all']:
                # Initialize Enquiry as 1 and Sale as 0
                dct_data['status_all'][ins_data.status]={}
                dct_data['status_all'][ins_data.status]['Enquiry']=ins_data.counts
                dct_data['status_all'][ins_data.status]['EnquiryQty']=ins_data.qty
                dct_data['status_all'][ins_data.status]['EnquiryValue']=ins_data.value
                dct_data['status_all'][ins_data.status]['Sale']=0
                dct_data['status_all'][ins_data.status]['SaleQty']=0
                dct_data['status_all'][ins_data.status]['SaleValue']=0

                if ins_data.status == 'INVOICED':
                    dct_data['status_all'][ins_data.status]['Sale']=ins_data.counts
                    dct_data['status_all'][ins_data.status]['SaleQty']=ins_data.qty
                    dct_data['status_all'][ins_data.status]['SaleValue']=ins_data.value
            else:
                dct_data['status_all'][ins_data.status]['Enquiry']+=ins_data.counts
                dct_data['status_all'][ins_data.status]['EnquiryQty']+=ins_data.qty
                dct_data['status_all'][ins_data.status]['EnquiryValue']+=ins_data.value
                if ins_data.status == 'INVOICED':
                    dct_data['status_all'][ins_data.status]['Sale']+=ins_data.counts
                    dct_data['status_all'][ins_data.status]['SaleQty']+=ins_data.qty
                    dct_data['status_all'][ins_data.status]['SaleValue']+=ins_data.value

        dct_data['brand_all']=paginate_data(dct_data['brand_all'],10)
        dct_data['branch_all']=paginate_data(dct_data['branch_all'],10)
        dct_data['item_all']=paginate_data(dct_data['item_all'],10)
        dct_data['service_all']=paginate_data(dct_data['service_all'],10)

        for key in dct_data['branch_service']:
                dct_data['branch_service'][key]=paginate_data(dct_data['branch_service'][key],10)
        for key in dct_data['branch_brand']:
                dct_data['branch_brand'][key]=paginate_data(dct_data['branch_brand'][key],10)
        for key in dct_data['branch_item']:
                dct_data['branch_item'][key]=paginate_data(dct_data['branch_item'][key],10)
        for key in dct_data['branch_service_brand']:
            for key1 in dct_data['branch_service_brand'][key]:
                dct_data['branch_service_brand'][key][key1]=paginate_data(dct_data['branch_service_brand'][key][key1],10)
        for key in dct_data['branch_service_item']:
            for key1 in dct_data['branch_service_item'][key]:
                dct_data['branch_service_item'][key][key1]=paginate_data(dct_data['branch_service_item'][key][key1],10)
        # import pdb;pdb.set_trace()
        for key in dct_data['branch_service_brand_item']:
            for key1 in dct_data['branch_service_brand_item'][key]:
                for key2 in dct_data['branch_service_brand_item'][key][key1]:
                    dct_data['branch_service_brand_item'][key][key1][key2]=paginate_data(dct_data['branch_service_brand_item'][key][key1][key2],10)


        return dct_data
    except Exception as msg:
        return str(msg)
