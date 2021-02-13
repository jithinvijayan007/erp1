from collections import Counter

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from POS import ins_logger
from rest_framework.permissions import IsAuthenticated
# from enquiry.models import EnquiryMaster,Flights,AddAttachments,Document,Hotel,Visa,Transport,Package,Forex,Other,TravelInsurance,Rooms,Train
# from software.models import AccountingSoftware,EmployeeManagement,EnquiryTrack,HrSolutions
from enquiry.models import EnquiryMaster,Document
from userdetails.models import UserDetails as UserModel
from customer.models import CustomerDetails as CustomerModel
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.http import JsonResponse
import random
# from export_excel.views import export_excel
from collections import OrderedDict

from sqlalchemy.orm.session import sessionmaker
import aldjemy
from sqlalchemy.orm import mapper,aliased
from sqlalchemy import and_,func,cast,Date
from sqlalchemy.sql.expression import literal,union_all

EnquiryMasterSA = EnquiryMaster.sa
CustomerModelSA = CustomerModel.sa
AuthUserSA = User.sa
# FlightsSA = Flights.sa
# AddAttachmentsSA = AddAttachments.sa
DocumentSA = Document.sa
# HotelSA = Hotel.sa
# VisaSA = Visa.sa
# TransportSA = Transport.sa
# PackageSA = Package.sa
# ForexSA = Forex.sa
# OtherSA = Other.sa
# TravelInsuranceSA = TravelInsurance.sa
# RoomsSA = Rooms.sa
# TrainSA = Train.sa

# EnquiryTrackSA = EnquiryTrack.sa
# AccountingSoftwareSA = AccountingSoftware.sa
# HrSolutionsSA = HrSolutions.sa
# EmployeeManagementSA = EmployeeManagement.sa

def Session():
    from aldjemy.core import get_engine
    engine = get_engine()
    _Session = sessionmaker(bind = engine)
    return _Session()

# Create your views here.


class ProductivityReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            session = Session()
            # import pdb; pdb.set_trace()
            str_username = request.data.get('username',False)
            bln_assigned_all = request.data.get('all',False)
            blnExcel = request.data.get('excel',False)
            # if str_username:
            ins_user = UserModel.objects.get(id = request.user.id)
            lst_table_data = []
            dat_from_date = datetime.strptime(request.data['fdate'], "%Y-%m-%d").date()
            dat_to_date = datetime.strptime(request.data['tdate'], "%Y-%m-%d").date()

            if ins_user.fk_company.vchr_category == 'Travels':
                rst_flight = session.query(literal("Flight").label("vchr_service"),FlightsSA.vchr_enquiry_status.label('vchr_enquiry_status'),FlightsSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_train = session.query(literal("Train").label("vchr_service"),TrainSA.vchr_enquiry_status.label("vchr_enquiry_status"),TrainSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Forex=session.query(literal("Forex").label("vchr_service"),ForexSA.vchr_enquiry_status.label("vchr_enquiry_status"),ForexSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Hotel=session.query(literal("Hotel").label("vchr_service"),HotelSA.vchr_enquiry_status.label("vchr_enquiry_status"),HotelSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Other=session.query(literal("Other").label("vchr_service"),OtherSA.vchr_enquiry_status.label("vchr_enquiry_status"),OtherSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Transport=session.query(literal("Transport").label("vchr_service"),TransportSA.vchr_enquiry_status.label("vchr_enquiry_status"),TransportSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_TravelInsurance=session.query(literal("Travel Insurance").label("vchr_service"),TravelInsuranceSA.vchr_enquiry_status.label("vchr_enquiry_status"),TravelInsuranceSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Visa=session.query(literal("Visa").label("vchr_service"),VisaSA.vchr_enquiry_status.label("vchr_enquiry_status"),VisaSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_Package=session.query(literal("Package").label("vchr_service"),PackageSA.vchr_enquiry_status.label("vchr_enquiry_status"),PackageSA.fk_enquiry_master_id.label("FK_Enquery"))


# ins_table_data = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company = ins_user.fk_company,dat_created_at__gte = dat_from_date,dat_created_at__lte = dat_to_date).values(                                       'pk_bint_id','vchr_enquiry_num','fk_assigned','fk_assigned__first_name','fk_assigned__last_name','fk_assigned','fk_customer__cust_fname','fk_customer__cust_lname','fk_customer__cust_mobile','vchr_enquiry_priority','vchr_enquiry_source','dat_created_at').order_by('fk_assigned__first_name')
# ins_table_data = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company = ins_user.fk_company,dat_created_at__gte = dat_from_date,dat_created_at__lte = dat_to_date,fk_assigned = request.data['assigned']).values('pk_bint_id','vchr_enquiry_num','fk_customer__cust_fname','fk_customer__cust_lname','fk_customer__cust_mobile','vchr_enquiry_priority','vchr_enquiry_source','dat_created_at','fk_assigned','fk_assigned__first_name','fk_assigned__last_name')

                rst_data = rst_flight.union_all(rst_Forex,rst_Hotel,rst_Other,rst_Transport,rst_TravelInsurance,rst_Visa,rst_Package,rst_train).subquery()

            elif ins_user.fk_company.vchr_category == 'SOFTWARE':
                rst_enquiry_track = session.query(literal("Enquiry Track").label("vchr_service"),EnquiryTrackSA.vchr_enquiry_status.label('vchr_enquiry_status'),EnquiryTrackSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_accounting_software = session.query(literal("Accounting Software").label("vchr_service"),AccountingSoftwareSA.vchr_enquiry_status.label('vchr_enquiry_status'),AccountingSoftwareSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_hr_solutions = session.query(literal("HR Solutions").label("vchr_service"),HrSolutionsSA.vchr_enquiry_status.label('vchr_enquiry_status'),HrSolutionsSA.fk_enquiry_master_id.label("FK_Enquery"))
                rst_employee_management = session.query(literal("Employee Management").label("vchr_service"),EmployeeManagementSA.vchr_enquiry_status.label('vchr_enquiry_status'),EmployeeManagementSA.fk_enquiry_master_id.label("FK_Enquery"))

                rst_data = rst_enquiry_track.union_all(rst_accounting_software,rst_hr_solutions,rst_employee_management).subquery()



            rst_table_data = session.query(EnquiryMasterSA.pk_bint_id.label('pk_bint_id'),EnquiryMasterSA.vchr_enquiry_num.label('vchr_enquiry_num'),\
                                rst_data.c.vchr_service,rst_data.c.vchr_enquiry_status,AuthUserSA.first_name.label('fk_assigned__first_name'),AuthUserSA.last_name.label('fk_assigned__last_name'),\
                                EnquiryMasterSA.fk_assigned_id.label('fk_assigned'),CustomerModelSA.cust_fname.label('fk_customer__cust_fname'),\
                                CustomerModelSA.cust_lname.label('fk_customer__cust_lname'),CustomerModelSA.cust_mobile.label('fk_customer__cust_mobile'),\
                                EnquiryMasterSA.vchr_enquiry_priority.label('vchr_enquiry_priority'),EnquiryMasterSA.vchr_enquiry_source.label('vchr_enquiry_source'),\
                                EnquiryMasterSA.dat_created_at.label('dat_created_at'))\
                                .filter(and_(EnquiryMasterSA.fk_company_id == ins_user.fk_company_id,EnquiryMasterSA.chr_doc_status == 'N',EnquiryMasterSA.dat_created_at >= dat_from_date,EnquiryMasterSA.dat_created_at <= dat_to_date))\
                                .join(rst_data,rst_data.c.FK_Enquery == EnquiryMasterSA.pk_bint_id)\
                                .join(CustomerModelSA,EnquiryMasterSA.fk_customer_id == CustomerModelSA.id)\
                                .join(AuthUserSA,EnquiryMasterSA.fk_assigned_id == AuthUserSA.id)
            if request.data.get('type') == 'PIE':
                if request.data.get('assigned'):
                    rst_table_data = rst_table_data.filter(EnquiryMasterSA.fk_assigned_id == request.data.get('assigned'))
            rst_table_data = rst_table_data.order_by(AuthUserSA.first_name)
            lst_table_data = []

            for dct_data in rst_table_data.all():
                dct_temp_data = dct_data._asdict()
                dct_temp_data['vchr_full_name'] = dct_temp_data['fk_customer__cust_fname']+" "+dct_temp_data['fk_customer__cust_lname']
                dct_temp_data['vchr_staff_full_name'] = dct_temp_data['fk_assigned__first_name']+" "+dct_temp_data['fk_assigned__last_name']
                dct_temp_data['vchr_created_at'] = dct_temp_data['dat_created_at'].strftime('%d-%m-%Y')
                dct_temp_data['vchr_mobile_num'] = dct_temp_data['fk_customer__cust_mobile']
                lst_table_data.append(dct_temp_data)


            lst_report_data = []
            if request.data['type'] == 'BAR':
                dct_item = {'first_name':'','total':0,'fk_assigned':0}
                for itr_item in lst_table_data:
                    if str(itr_item.get('fk_assigned__first_name')).title() == dct_item['first_name']:
                        dct_item['total'] += 1
                    else:
                        if dct_item['first_name'] != '':
                            lst_report_data.append(dct_item.copy())
                        dct_item = {'first_name':str(itr_item.get('fk_assigned__first_name')).title(),'total':1,'fk_assigned':itr_item.get('fk_assigned')}
                if dct_item['first_name'] != '':
                    lst_report_data.append(dct_item.copy())
                random.shuffle(lst_report_data)
                lst_status_count_all = Counter(tok['vchr_enquiry_status'] for tok in lst_table_data)

                lst_barchart_data = []
                lst_barchart_labels = []
                lst_barchart_user_id = []

                for dct_data in lst_report_data:
                    lst_barchart_labels.append(dct_data['first_name'])
                    lst_barchart_data.append(dct_data['total'])
                    lst_barchart_user_id.append(dct_data['fk_assigned'])

                lst_staff_piechart_data = []
                for int_staff_id in lst_barchart_user_id:
                    count_data = Counter(tok['vchr_enquiry_status'] for tok in lst_table_data if tok.get('fk_assigned') == int_staff_id)
                    lst_staff_piechart_data.append({int_staff_id:count_data})
                session.close()
                return JsonResponse({ 'status' : 'success',
                    'lst_barchart_labels':lst_barchart_labels ,  'lst_barchart_data':lst_barchart_data , 'lst_barchart_user_id':lst_barchart_user_id ,
                    'lst_status_count_all': lst_status_count_all , 'lst_staff_piechart_data': lst_staff_piechart_data , 'lst_table_data': lst_table_data
                    })




            elif request.data['type'] == 'PIE':
                if blnExcel:
                    lst_excel_data = []
                    for dct_data in lst_table_data:
                        dct_temp = OrderedDict()
                        if bln_assigned_all:
                            dct_temp['Staff Name'] = str(dct_data.get('vchr_staff_full_name')).title()
                        dct_temp['Enquiry Date'] = str(datetime.strptime(str(dct_data.get('dat_created_at'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
                        dct_temp['Enquiry Number'] = dct_data.get('vchr_enquiry_num')
                        dct_temp['Customer Name'] = str(dct_data.get('vchr_full_name')).title()
                        dct_temp['Mobile Number'] = str(dct_data.get('vchr_mobile_num'))
                        dct_temp['Service'] = dct_data.get('vchr_service')
                        dct_temp['Enquiry Priority'] = dct_data.get('vchr_enquiry_priority')
                        dct_temp['Enquiry Source'] = dct_data.get('vchr_enquiry_source')
                        dct_temp['Enquiry Status'] = dct_data.get('vchr_enquiry_status')
                        lst_excel_data.append(dct_temp)
                    fromdate =  str(dat_from_date)[:10].split("-")
                    todate =  str(dat_to_date)[:10].split('-')
                    fromdate.reverse()
                    todate.reverse()
                    dat_from_date = "-".join(fromdate)
                    dat_to_date = "-".join(todate)
                    if bln_assigned_all:
                        lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Staff Name'])
                        response = export_excel('productivity','all',dat_from_date,dat_to_date,lst_excel_data)
                    else:
                        lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Enquiry Number'])
                        response = export_excel('productivity',lst_table_data[0].get('vchr_staff_full_name'),dat_from_date,dat_to_date,lst_excel_data)
                    if response != False:
                        session.close()
                        return JsonResponse({'status': 'success', 'path':response})
                    else:
                        session.close()
                        return JsonResponse({'status': 'failure'})
        except Exception as e:
            ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
            session.close()
            return Response({'status':'0','data':str(e)})




# class ProductivityReport(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             str_username = request.data.get('username',False)
#             bln_assigned_all = request.data.get('all',False)
#             blnExcel = request.data.get('excel',False)
#             if str_username:
#                 ins_user = UserModel.objects.get(username = str_username)
#             lst_table_data = []
#             dat_from_date = datetime.strptime(request.data['fdate'], "%d/%m/%Y").date()
#             dat_to_date = datetime.strptime(request.data['tdate'], "%d/%m/%Y").date()
#             if request.data['type'] == 'BAR' or bln_assigned_all == True:
#                 ins_table_data = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company = ins_user.fk_company,dat_created_at__gte = dat_from_date,dat_created_at__lte = dat_to_date).values('pk_bint_id','vchr_enquiry_num','fk_assigned','fk_assigned__first_name','fk_assigned__last_name','fk_assigned','fk_customer__cust_fname','fk_customer__cust_lname','fk_customer__cust_mobile','vchr_enquiry_priority','vchr_enquiry_source','dat_created_at').order_by('fk_assigned__first_name')
#             elif request.data['type'] == 'PIE':
#                 ins_table_data = EnquiryMaster.objects.filter(chr_doc_status='N',fk_company = ins_user.fk_company,dat_created_at__gte = dat_from_date,dat_created_at__lte = dat_to_date,fk_assigned = request.data['assigned']).values('pk_bint_id','vchr_enquiry_num','fk_customer__cust_fname','fk_customer__cust_lname','fk_customer__cust_mobile','vchr_enquiry_priority','vchr_enquiry_source','dat_created_at','fk_assigned','fk_assigned__first_name','fk_assigned__last_name')
#             for dct_table_data in ins_table_data:
#                 dct_table_data['vchr_full_name'] = dct_table_data.get('fk_customer__cust_fname')+" "+dct_table_data.get('fk_customer__cust_lname')
#                 dct_table_data['vchr_staff_full_name'] = dct_table_data.get('fk_assigned__first_name')+" "+dct_table_data.get('fk_assigned__last_name')
#                 dct_table_data['vchr_created_at'] = dct_table_data.get('dat_created_at').strftime('%d-%m-%Y')
#                 dct_table_data['vchr_mobile_num'] = dct_table_data.get('fk_customer__cust_mobile')
#                 int_pk = dct_table_data.get('pk_bint_id')
#                 ins_flight_data = Flights.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_flight_data:
#                     dct_table_data['vchr_service'] = 'Flight'
#                     for dct_data in ins_flight_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_train_data = Train.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_train_data:
#                     dct_table_data['vchr_service'] = 'Train'
#                     for dct_data in ins_train_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_visa_data = Visa.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_visa_data:
#                     dct_table_data['vchr_service'] = 'Visa'
#                     for dct_data in ins_visa_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_forex_data = Forex.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_forex_data:
#                     dct_table_data['vchr_service'] = 'Forex'
#                     for dct_data in ins_forex_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_hotel_data = Hotel.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_hotel_data:
#                     dct_table_data['vchr_service'] = 'Hotel'
#                     for dct_data in ins_hotel_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_transport_data = Transport.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_transport_data:
#                     dct_table_data['vchr_service'] = 'Transport'
#                     for dct_data in ins_transport_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_package_data = Package.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_package_data:
#                     dct_table_data['vchr_service'] = 'Package'
#                     for dct_data in ins_package_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_insurance_data = TravelInsurance.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_insurance_data:
#                     dct_table_data['vchr_service'] = 'Travel Insurance'
#                     for dct_data in ins_insurance_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#                 ins_other_data = Other.objects.filter(fk_enquiry_master = int_pk).values('vchr_enquiry_status')
#                 if ins_other_data:
#                     dct_table_data['vchr_service'] = 'Other'
#                     for dct_data in ins_other_data:
#                         dct_table_data['vchr_enquiry_status'] = dct_data['vchr_enquiry_status']
#                         lst_table_data.append(dct_table_data.copy())
#             lst_report_data = []
#             if request.data['type'] == 'BAR':
#                 dct_item = {'first_name':'','total':0,'fk_assigned':0}
#                 for itr_item in lst_table_data:
#                     if str(itr_item.get('fk_assigned__first_name')).title() == dct_item['first_name']:
#                         dct_item['total'] += 1
#                     else:
#                         if dct_item['first_name'] != '':
#                             lst_report_data.append(dct_item.copy())
#                         dct_item = {'first_name':str(itr_item.get('fk_assigned__first_name')).title(),'total':1,'fk_assigned':itr_item.get('fk_assigned')}
#                 if dct_item['first_name'] != '':
#                     lst_report_data.append(dct_item.copy())
#                 random.shuffle(lst_report_data)
#                 return JsonResponse({'report_barchart_data':lst_report_data})
#             elif request.data['type'] == 'PIE':
#                 if blnExcel:
#                     lst_excel_data = []
#                     for dct_data in lst_table_data:
#                         dct_temp = OrderedDict()
#                         if bln_assigned_all:
#                             dct_temp['Staff Name'] = str(dct_data.get('vchr_staff_full_name')).title()
#                         dct_temp['Enquiry Date'] = str(datetime.strptime(str(dct_data.get('dat_created_at'))[:10] , '%Y-%m-%d').strftime('%d-%m-%Y'))
#                         dct_temp['Enquiry Number'] = dct_data.get('vchr_enquiry_num')
#                         dct_temp['Customer Name'] = str(dct_data.get('vchr_full_name')).title()
#                         dct_temp['Mobile Number'] = str(dct_data.get('vchr_mobile_num'))
#                         dct_temp['Service'] = dct_data.get('vchr_service')
#                         dct_temp['Enquiry Priority'] = dct_data.get('vchr_enquiry_priority')
#                         dct_temp['Enquiry Source'] = dct_data.get('vchr_enquiry_source')
#                         dct_temp['Enquiry Status'] = dct_data.get('vchr_enquiry_status')
#                         lst_excel_data.append(dct_temp)
#                     fromdate =  str(dat_from_date)[:10].split("-")
#                     todate =  str(dat_to_date)[:10].split('-')
#                     fromdate.reverse()
#                     todate.reverse()
#                     dat_from_date = "-".join(fromdate)
#                     dat_to_date = "-".join(todate)
#                     if bln_assigned_all:
#                         lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Staff Name'])
#                         response = export_excel('productivity','all',dat_from_date,dat_to_date,lst_excel_data)
#                     else:
#                         lst_excel_data = sorted(lst_excel_data,key=lambda k: k['Enquiry Number'])
#                         response = export_excel('productivity',lst_table_data[0].get('vchr_staff_full_name'),dat_from_date,dat_to_date,lst_excel_data)
#                     if response != False:
#                         return JsonResponse({'status': 'success', 'path':response})
#                     else:
#                         return JsonResponse({'status': 'failure'})
#                 else:
#                     lst_report_data = []
#                     for itr_item in lst_table_data:
#                         dct_item = {'vchr_enquiry_status':itr_item.get('vchr_enquiry_status'),'total':1}
#                         lst_report_data.append(dct_item)
#                     return JsonResponse({'report_piechart_data':lst_report_data,'report_table_data':lst_table_data})
#         except Exception as e:
#             ins_logger.logger.error(e, extra={'user': 'user_id:' + str(request.user.id)})
#             return Response({'status':'0','data':str(e)})
