import operator
from staff_rating.models import StaffRating
from collections import Counter
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userdetails.models import UserDetails as UserModel
from customer.models import CustomerDetails as CustomerModel

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Date,Float,and_
from sqlalchemy import ForeignKey
from sqlalchemy import *
from datetime import datetime, timedelta,date

from django.contrib.auth.models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import case, literal_column
# from paginateDemandReport import paginate_demand_report,export_paginate_demand_report
from globalMethods import convert_to_millions,show_data_based_on_role,general_chart_data_sort,get_user_products
import aldjemy
import json
# from enquiry.models import EnquiryMaster, Train , Flights,AddAttachments,Document,Hotel,Visa,Transport,Package,Forex,Other,TravelInsurance,Rooms,HotelFollowup,FlightsFollowup,VisaFollowup,OtherFollowup,TravelInsuranceFollowup,ForexFollowup,TransportFollowup,PackageFollowup, TrainFollowup
from branch.models import Branch
from territory.models import Territory
# from enquiry.views import fun_travels_data,fun_software_data,fun_automobile_data
from enquiry_mobile.models import MobileEnquiry,TabletEnquiry,ComputersEnquiry,AccessoriesEnquiry
# from enquiry.views import fun_travels_data,fun_software_data,fun_mobile
# from inventory.models import Products,Brands,Items
from company.models import Company
from titlecase import titlecase
from sqlalchemy import desc

from enquiry_print.views import enquiry_print
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper, aliased
from sqlalchemy import and_,func ,cast,Date
from sqlalchemy.sql.expression import literal,union_all
from export_excel.views import export_excel
from collections import OrderedDict
import pandas as pd
# from software.models import AccountingSoftware,EmployeeManagement,EnquiryTrack,HrSolutions
from django.db.models import Q
# from auto_mobile.models import SedanEnquiry,SuvEnquiry,HatchbackEnquiry
# from enquiry.views import get_perm_data
from pdfGenerate import generate_pdf,general_generate_pdf
from generateExcel import general_generate_excel

from generalize_report.models import GeneralizeReport
CustomerSA = CustomerModel.sa
UserSA=UserModel.sa
AuthUserSA = User.sa



# EnquiryMasterSA = EnquiryMaster.sa

MobileEnquirySA = MobileEnquiry.sa
TabletEnquirySA = TabletEnquiry.sa
ComputersEnquirySA = ComputersEnquiry.sa
AccessoriesEnquirySA = AccessoriesEnquiry.sa
# ProductSA = Products.sa
# ItemsSA=Items.sa
# BrandsSA=Brands.sa
BranchSA = Branch.sa
TerritorySA = Territory.sa


def Session():
    from aldjemy.core import get_engine
    engine=get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()
# Create your views here.
class GetChartDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            ins_general = GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('vchr_report_name','vchr_query','json_data','vchr_url_name')
            str_data = ins_general[0]['json_data']
            str_name = ins_general[0]['vchr_report_name']
            str_url_name = ins_general[0]['vchr_url_name']
            return Response({'status':'success','dct_details':str_data,'name':str_name,'url_name':str_url_name})
        except Exception as msg:
            return JsonResponse({'status':'failed','data':str(msg)})

class GeneralizeStatusReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            lst_enquiry_data = []

            int_company = request.data['company_id']
            ins_company = CompanyDetails.objects.filter(pk_bint_id = int_company)
            ins_general = GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('vchr_query','json_data','vchr_url_name')
            str_data = ins_general[0]['json_data']
            fromdate =  datetime.strftime(datetime.strptime(request.data['date_from'], '%Y-%m-%d' ),'%Y-%m-%d')
            todate =  datetime.strftime(datetime.strptime(request.data['date_to'], '%Y-%m-%d' ),'%Y-%m-%d')
            # if request.data['bln_chart']:
            #     branch_id = request.user.usermodel.fk_branch_id
            if request.data.get('reportname') == 'mobilefinancereport':
                str_filter = "em.dat_created_at between '"+str(fromdate)+"' AND '"+str(todate)+"'"
            else:

                str_filter = "dat_enquiry between '"+str(fromdate)+"' AND '"+str(todate)+"'"

            if request.user.usermodel.fk_group.vchr_name.upper() in ['ADMIN','GENERAL MANAGER SALES','COUNTRY HEAD','PRODUCT MANAGER']:
                pass
            elif request.user.usermodel.fk_group.vchr_name.upper() in ['BRANCH MANAGER','ASSISTANT BRANCH MANAGER']:
                str_filter += " AND branch_id = "+str(request.user.usermodel.fk_branch_id)
            elif request.user.usermodel.int_area_id:
                lst_branch=show_data_based_on_role(request.user.usermodel.fk_group.vchr_name,request.user.usermodel.int_area_id)
                str_filter += " AND branch_id in ("+str(lst_branch)[1:-1]+")"
            else:
                return Response({'status':'failed','reason':'No data'})


            if request.data.get('branchselected'):
                if request.data.get('reportname') == 'mobilefinancereport':
                    str_filter += " AND br.pk_bint_id in ("+str(request.data.get('branchselected',[]))[1:-1]+")"
                else:
                    str_filter += " AND branch_id in ("+str(request.data.get('branchselected',[]))[1:-1]+")"

            if request.data.get('custselected'):
                str_filter+= " AND customer_mobile in ("+ str(request.data.get('custselected',[]))[1:-1]+")"

            if request.data.get('product'):
                if request.data.get('reportname') == 'mobilefinancereport':
                    str_filter += " AND ie.fk_product_id = "+str(request.data.get('product'))+""

                else:
                    str_filter += " AND product_id = "+str(request.data.get('product'))+""

            if request.data.get('brand'):
                if request.data.get('reportname') == 'mobilefinancereport':
                    str_filter += " AND ie.fk_brand_id = "+str(request.data.get('brand'))+""
                else:
                    str_filter += " AND brand_id = "+str(request.data.get('brand'))+""

            if request.data.get('staffsselected'):
                str_filter += " AND user_id in ("+str(request.data.get('staffsselected',[]))[1:-1]+")"

            if request.data.get('territoryselected'):
                str_filter += " AND territory_id in ("+str(request.data.get('territoryselected',[]))[1:-1]+")"

            if request.data.get('zoneselected'):
                str_filter += " AND zone_id in ("+str(request.data.get('zoneselected',[]))[1:-1]+")"

            if request.data.get('itemselected'):
                str_filter += " AND id in ("+str(request.data.get('itemselected',[]))[1:-1]+")"

            ins_report = list(GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('vchr_report_name'))[0]['vchr_report_name']

            dct_data={}
            session=Session()
            if request.data['bln_chart']:
                # if ins_report.split(' ')[0].upper() == 'DEMAND' or ins_report.split(' ')[0].upper() == 'ZONE' or ins_report.split(' ')[0].upper() == 'TERRITORY' or ins_report.upper() == 'STATE REPORT' or ins_report.upper() == 'DAY WISE REPORT' or ins_report.upper() == 'PRODUCT PRICE RANGE REPORT':
                str_sort = request.data.get('strGoodPoorClicked','NORMAL')
                int_page = int(request.data.get('intCurrentPage',1))
                str_report_type = request.data['report_type'].upper()
                if request.data['show_type']:
                    str_value = 'total_amount'
                    if ins_general[0]['vchr_url_name'] in ['mobilefinancereport']:
                        str_value = 'ie.dbl_amount'
                else:
                    str_value = 'int_quantity'
                    if ins_general[0]['vchr_url_name'] in ['mobilefinancereport']:
                        str_value = 'ie.int_quantity'

                # import pdb; pdb.set_trace()
                #for getting user corresponding products
                lst_user_id =[]
                lst_user_id.append(request.user.id)
                lst_user_products = get_user_products(lst_user_id)
                if lst_user_products:
                    str_filter += " AND product_id in ("+str(lst_user_products)[1:-1]+")"

                str_query = ins_general[0]['vchr_query'].format(str_value,str_filter)
                # else:
                #     str_query = ins_general[0]['vchr_query'].format(fromdate,todate,branch_id)
                rst_enquiry = session.execute(str_query).fetchall()
                if not rst_enquiry:
                    session.close()
                    return Response({'status':'failed','reason':'No data'})
                str_chart1 = str_data.get('1',{}).get('data','')
                str_chart2 = str_data.get('2',{}).get('data','')
                str_chart3 = str_data.get('3',{}).get('data','')
                str_chart4 = str_data.get('4',{}).get('data','')
                str_chart5 = str_data.get('5',{}).get('data','')
                str_chart6 = str_data.get('6',{}).get('data','')
                str_chart7 = str_data.get('7',{}).get('data','')
                str_chart8 = str_data.get('8',{}).get('data','')
                str_chart9 = str_data.get('9',{}).get('data','')
                str_chart10 = str_data.get('10',{}).get('data','')

                # Storing which type of the chart to be
                # grouped_chart : is of more than one bar in the same chart
                # stacked_chart : is of more stacked bar chart
                str_chart1_type = str_data.get('1',{}).get('type','')
                str_chart2_type = str_data.get('2',{}).get('type','')
                str_chart3_type = str_data.get('3',{}).get('type','')
                str_chart4_type = str_data.get('4',{}).get('type','')
                str_chart5_type = str_data.get('5',{}).get('type','')
                str_chart6_type = str_data.get('6',{}).get('type','')
                str_chart7_type = str_data.get('7',{}).get('type','')
                str_chart8_type = str_data.get('8',{}).get('type','')
                str_chart9_type = str_data.get('9',{}).get('type','')
                str_chart10_type = str_data.get('10',{}).get('type','')



                dct_data_chart ={
                'str_chart1': str_chart1,
                'str_chart2': str_chart2,
                'str_chart3': str_chart3,
                'str_chart4': str_chart4,
                'str_chart5': str_chart5,
                'str_chart6': str_chart6,
                'str_chart7': str_chart7,
                'str_chart8': str_chart8,
                'str_chart9': str_chart9,
                'str_chart10': str_chart10
                }
                dct_data={}
                dct_data[str_chart1] = {}
                dct_data[str_chart2] = {}
                dct_data[str_chart3] = {}
                dct_data[str_chart4] = {}
                dct_data[str_chart5] = {}
                dct_data[str_chart6] = {}
                dct_data[str_chart7] = {}
                dct_data[str_chart8] = {}
                dct_data[str_chart9] = {}
                dct_data[str_chart10] = {}
                # dct_data['territorys']={}

                for ins_data in rst_enquiry:
                    ins_data = dict(zip(ins_data.keys(),ins_data))
                    str_chart1_data = ins_data.get('chart_1','')
                    str_chart2_data = ins_data.get('chart_2','')
                    str_chart3_data = ins_data.get('chart_3','')
                    str_chart4_data = ins_data.get('chart_4','')
                    str_chart5_data = ins_data.get('chart_5','')
                    str_chart6_data = ins_data.get('chart_6','')
                    str_chart7_data = ins_data.get('chart_7','')
                    str_chart8_data = ins_data.get('chart_8','')
                    str_chart9_data = ins_data.get('chart_9','')
                    str_chart10_data = ins_data.get('chart_10','')

                    if str_chart1_data not in dct_data[str_chart1]:
                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart1][str_chart1_data] = {}
                        if ins_report.upper() == 'ZONE SALES REPORT' or ins_report.upper() == 'TERRITORY SALES REPORT':
                            dct_data[str_chart1][str_chart1_data]['Value1']= int(ins_data['value_2'])
                        else:
                            dct_data[str_chart1][str_chart1_data]['Value1']= int(ins_data['value_1'])
                            # Setting second value for the second bar
                            dct_data[str_chart1][str_chart1_data]['Value2'] = 0
                            if ((str_chart1_type == 'grouped_bar' or str_chart1_type == 'stacked_bar')):
                                dct_data[str_chart1][str_chart1_data]['Value2'] = int(ins_data['value_2'])

                    else:
                        if ins_report.upper() == 'ZONE SALES REPORT' or ins_report.upper() == 'TERRITORY SALES REPORT':
                            dct_data[str_chart1][str_chart1_data]['Value1'] += int(ins_data['value_2'])
                        else:
                            dct_data[str_chart1][str_chart1_data]['Value1'] += int(ins_data['value_1'])
                            # Setting second value for the second bar

                            if ((str_chart1_type == 'grouped_bar' or str_chart1_type == 'stacked_bar')):
                                dct_data[str_chart1][str_chart1_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart2_data not in dct_data[str_chart2]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart2][str_chart2_data] = {}
                        dct_data[str_chart2][str_chart2_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart2][str_chart2_data]['Value2'] = 0

                        if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                            dct_data[str_chart2][str_chart2_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart2][str_chart2_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar

                        if ((str_chart2_type == 'grouped_bar' or str_chart2_type == 'stacked_bar')):
                            dct_data[str_chart2][str_chart2_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart3_data not in dct_data[str_chart3]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart3][str_chart3_data] = {}
                        dct_data[str_chart3][str_chart3_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart3][str_chart3_data]['Value2'] = 0

                        if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                            dct_data[str_chart3][str_chart3_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart3][str_chart3_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar

                        if ((str_chart3_type == 'grouped_bar' or str_chart3_type == 'stacked_bar')):
                            dct_data[str_chart3][str_chart3_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart4_data not in dct_data[str_chart4]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart4][str_chart4_data] = {}
                        dct_data[str_chart4][str_chart4_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart4][str_chart4_data]['Value2'] = 0

                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                            dct_data[str_chart4][str_chart4_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart4][str_chart4_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar

                        if ((str_chart4_type == 'grouped_bar' or str_chart4_type == 'stacked_bar')):
                            dct_data[str_chart4][str_chart4_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart5_data not in dct_data[str_chart5]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart5][str_chart5_data] = {}
                        dct_data[str_chart5][str_chart5_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart5][str_chart5_data]['Value2'] = 0

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart5][str_chart5_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart5][str_chart5_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar

                        if ((str_chart5_type == 'grouped_bar' or str_chart5_type == 'stacked_bar')):
                            dct_data[str_chart5][str_chart5_data]['Value2'] += int(ins_data['value_2'])
                    if str_chart6_data not in dct_data[str_chart6]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart6][str_chart6_data] = {}
                        dct_data[str_chart6][str_chart6_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart6][str_chart6_data]['Value2'] = 0

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart6][str_chart6_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart6][str_chart6_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar

                        if ((str_chart6_type == 'grouped_bar' or str_chart6_type == 'stacked_bar')):
                            dct_data[str_chart6][str_chart6_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart7_data not in dct_data[str_chart7]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart7][str_chart7_data] = {}
                        dct_data[str_chart7][str_chart7_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart7][str_chart7_data]['Value2'] = 0

                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart7][str_chart7_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart7][str_chart7_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar
                        if ((str_chart7_type == 'grouped_bar' or str_chart7_type == 'stacked_bar')):
                            dct_data[str_chart7][str_chart7_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart8_data not in dct_data[str_chart8]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart8][str_chart8_data] = {}
                        dct_data[str_chart8][str_chart8_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart8][str_chart8_data]['Value2'] = 0

                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart8][str_chart8_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart8][str_chart8_data]['Value1'] += int(ins_data['value_1'])
                        # Setting second value for the second bar
                        if ((str_chart8_type == 'grouped_bar' or str_chart8_type == 'stacked_bar')):
                            dct_data[str_chart8][str_chart8_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart9_data not in dct_data[str_chart9]:
                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart9][str_chart9_data] = {}
                        dct_data[str_chart9][str_chart9_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart9][str_chart9_data]['Value2'] = 0
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart9][str_chart9_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart9][str_chart9_data]['Value1'] += int(ins_data['value_1'])
                        # Setting second value for the second bar
                        if ((str_chart9_type == 'grouped_bar' or str_chart9_type == 'stacked_bar')):
                            dct_data[str_chart9][str_chart9_data]['Value2'] += int(ins_data['value_2'])

                    if str_chart10_data not in dct_data[str_chart10]:

                        # setting first value to be displayed on the graph in the dictionary
                        dct_data[str_chart10][str_chart10_data] = {}
                        dct_data[str_chart10][str_chart10_data]['Value1'] = int(ins_data['value_1'])

                        # Setting second value for the second bar
                        dct_data[str_chart10][str_chart10_data]['Value2'] = 0

                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart10][str_chart10_data]['Value2'] = int(ins_data['value_2'])
                    else:
                        dct_data[str_chart10][str_chart10_data]['Value1'] += int(ins_data['value_1'])

                        # Setting second value for the second bar
                        if ((str_chart10_type == 'grouped_bar' or str_chart10_type == 'stacked_bar')):
                            dct_data[str_chart10][str_chart10_data]['Value2'] += int(ins_data['value_2'])
                # paginating table data
                if ins_report.split(' ')[0].upper() == 'DEMAND':
                    dctFilter = list(GeneralizeReport.objects.filter(vchr_url_name =request.data['reportname']).values('json_filter'))[0]['json_filter']
                    dct_data = export_paginate_demand_report(request,dct_data,str_data)
                else:
                    # Chart1
                    if str_data.get('1').get('type') == 'bar' or str_data.get('1').get('type') == 'grouped_bar' or str_data.get('1').get('type') == 'stacked_bar':
                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                            dct_data[str_chart1]=topten_paginate_data(dct_data[str_chart1],10)
                            dct_data[str_chart1]=general_chart_data_sort(request,dct_data[str_chart1],str_sort,int_page)
                        else:
                            dct_data[str_chart1]=paginate_data(dct_data[str_chart1],10)
                            dct_data[str_chart1]=general_chart_data_sort(request,dct_data[str_chart1],str_sort,int_page)


                    # Chart2
                    if str_data.get('2').get('type') == 'bar'or str_data.get('2').get('type') == 'grouped_bar' or str_data.get('2').get('type') == 'stacked_bar':
                        if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                            dct_data[str_chart2]=topten_paginate_data(dct_data[str_chart2],10)
                            dct_data[str_chart2]=general_chart_data_sort(request,dct_data[str_chart2],'NORMAL',1)
                        else:
                            dct_data[str_chart2]=paginate_data(dct_data[str_chart2],10)
                            dct_data[str_chart2]=general_chart_data_sort(request,dct_data[str_chart2],'NORMAL',1)

                                    # Chart3
                    if str_data.get('3'):
                        if str_data.get('3').get('type') == 'bar' or str_data.get('3').get('type') == 'grouped_bar' or str_data.get('3').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart3]=topten_paginate_data(dct_data[str_chart3],10)
                                dct_data[str_chart3]=general_chart_data_sort(request,dct_data[str_chart3],'NORMAL',1)
                            else:
                                dct_data[str_chart3]=paginate_data(dct_data[str_chart3],10)
                                dct_data[str_chart3]=general_chart_data_sort(request,dct_data[str_chart3],'NORMAL',1)
                    # Chart4
                    if str_data.get('4'):
                        if str_data.get('4').get('type') == 'bar' or str_data.get('4').get('type') == 'grouped_bar' or str_data.get('4').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart4]=topten_paginate_data(dct_data[str_chart4],10)
                                dct_data[str_chart4]=general_chart_data_sort(request,dct_data[str_chart4],'NORMAL',1)
                            else:
                                dct_data[str_chart4]=paginate_data(dct_data[str_chart4],10)
                                dct_data[str_chart4]=general_chart_data_sort(request,dct_data[str_chart4],'NORMAL',1)
                                        #Chart5
                    if str_data.get('5'):
                        if str_data.get('5').get('type') == 'bar' or str_data.get('5').get('type') == 'grouped_bar' or str_data.get('5').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart5]=topten_paginate_data(dct_data[str_chart5],10)
                                dct_data[str_chart5]=general_chart_data_sort(request,dct_data[str_chart5],'NORMAL',1)
                            else:
                                dct_data[str_chart5]=paginate_data(dct_data[str_chart5],10)
                                dct_data[str_chart5]=general_chart_data_sort(request,dct_data[str_chart5],'NORMAL',1)


                    #Chart6
                    if str_data.get('6'):
                        if str_data.get('6').get('type') == 'bar' or str_data.get('6').get('type') == 'grouped_bar' or str_data.get('6').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart6]=topten_paginate_data(dct_data[str_chart6],10)
                                dct_data[str_chart6]=general_chart_data_sort(request,dct_data[str_chart6],'NORMAL',1)
                            else:
                                dct_data[str_chart6]=paginate_data(dct_data[str_chart6],10)
                                dct_data[str_chart6]=general_chart_data_sort(request,dct_data[str_chart6],'NORMAL',1)



                    #Chart7
                    if str_data.get('7'):
                        if str_data.get('7').get('type') == 'bar' or str_data.get('7').get('type') == 'grouped_bar' or str_data.get('7').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart7]=topten_paginate_data(dct_data[str_chart7],10)
                                dct_data[str_chart7]=general_chart_data_sort(request,dct_data[str_chart7],'NORMAL',1)
                            else:
                                dct_data[str_chart7]=paginate_data(dct_data[str_chart7],10)
                                dct_data[str_chart7]=general_chart_data_sort(request,dct_data[str_chart7],'NORMAL',1)


                    #Chart7
                    if str_data.get('8'):
                        if str_data.get('8').get('type') == 'bar' or str_data.get('8').get('type') == 'grouped_bar' or str_data.get('8').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart8]=topten_paginate_data(dct_data[str_chart8],10)
                                dct_data[str_chart8]=general_chart_data_sort(request,dct_data[str_chart8],'NORMAL',1)
                            else:
                                dct_data[str_chart8]=paginate_data(dct_data[str_chart8],10)
                                dct_data[str_chart8]=general_chart_data_sort(request,dct_data[str_chart8],'NORMAL',1)



                    #Chart9
                    if str_data.get('9'):
                        if str_data.get('9').get('type') == 'bar' or str_data.get('9').get('type') == 'grouped_bar' or str_data.get('9').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart9]=topten_paginate_data(dct_data[str_chart9],10)
                                dct_data[str_chart9]=general_chart_data_sort(request,dct_data[str_chart9],'NORMAL',1)
                            else:
                                dct_data[str_chart9]=paginate_data(dct_data[str_chart9],10)
                                dct_data[str_chart9]=general_chart_data_sort(request,dct_data[str_chart9],'NORMAL',1)


                    #Chart10
                    if str_data.get('10'):
                        if str_data.get('10').get('type') == 'bar' or str_data.get('10').get('type') == 'grouped_bar' or str_data.get('10').get('type') == 'stacked_bar':
                            if ins_report.upper() == 'TOP TEN ITEM REPORT' or str_report_type == 'SALE':
                                dct_data[str_chart10]=topten_paginate_data(dct_data[str_chart10],10)
                                dct_data[str_chart10]=general_chart_data_sort(drequest,ct_data[str_chart10],'NORMAL',1)
                            else:
                                dct_data[str_chart10]=paginate_data(dct_data[str_chart10],10)
                                dct_data[str_chart10]=general_chart_data_sort(drequest,ct_data[str_chart10],'NORMAL',1)

                    # if ins_report.split(' ')[0].upper() == 'ZONE' or ins_report.split(' ')[0].upper() == 'TERRITORY' or ins_report.upper() == 'STATE REPORT' or ins_report.upper() == 'DAY WISE REPORT' or ins_report.upper() == 'PRODUCT PRICE RANGE REPORT':



                lst_details = []
                dct_label= {}
                int_index =1

                while int_index <= len(str_data):
                    lst_details.append(str_data[str(int_index)]['data']+'-'+str_data[str(int_index)]['type'])
                    dct_label[str_data[str(int_index)]['data']] = str_data[str(int_index)]['data'].title()+' wise'
                    int_index +=1

            #table data to export
            # if request.data['bln_table']:
            #     str_table_query = 'select vchr_enquiry_num,concat(staff_first_name, staff_last_name) as staff_name,vchr_product_name,vchr_brand_name,vchr_item_name,vchr_enquiry_status from mv_enquiry_data where '+str_filter+' AND int_company_id=1 group by vchr_enquiry_num,concat(staff_first_name, staff_last_name),vchr_product_name,vchr_brand_name,vchr_item_name,vchr_enquiry_status'
            #     rst_table_data = session.execute(str_table_query).fetchall()
            #     if not rst_enquiry:
            #         return Response({'status':'failled','data':'No Data'})
            #     lst_tbl_head = ['Enquiry No','Staff','Product','Brand','Item','Status']
            #     lst_tbl_index = [0,1,2,3,4,5]

            # export pdf document
            if request.data['document'].upper() == 'PDF':
                if request.data['bln_table'] and request.data['bln_chart']:
                    file_output = general_generate_pdf(request,ins_report,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_table_data))
                elif request.data['bln_chart']:
                    file_output = general_generate_pdf(request,ins_report,lst_details,dct_label,dct_data)
                # elif request.data['bln_table']:
                #     file_output = general_generate_pdf(request,ins_report,lst_tbl_head,lst_tbl_index,list(rst_table_data))


                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":"success",'file':file_output['file'],'file_name':file_output['file_name']})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":"success"})

            elif request.data['document'].upper() == 'EXCEL': # export excel document
                if request.data['bln_table'] and request.data['bln_chart']:
                    data=general_generate_excel(request,ins_report,lst_details,dct_label,dct_data,lst_tbl_head,lst_tbl_index,list(rst_table_data))
                elif request.data['bln_chart']:
                    data=general_generate_excel(request,ins_report,lst_details,dct_label,dct_data)
                # elif request.data['bln_table']:
                #     data=general_generate_excel(request,ins_report,lst_tbl_head,lst_tbl_index,list(rst_table_data))

                if request.data.get('export_type').upper() == 'DOWNLOAD':
                    session.close()
                    return Response({"status":"success","file":data})
                elif request.data.get('export_type').upper() == 'MAIL':
                    session.close()
                    return Response({"status":"success"})

        except Exception as msg:
            session.close()
            return JsonResponse({'status':'failed','data':str(msg)})

def key_sort_value1(tup):
    key,data = tup
    return data['Value1']
def key_sort_value2(tup):
    key,data = tup
    return data['Value2']

def paginate_data(dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    sorted_dct_data = sorted(dct_data.items(),key= key_sort_value1)
    # sorted_dct_data = reversed(sorted(dct_data.items(), key=operator.itemgetter(1)))
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


# def key_sort_value1(tup):
#     key,data = tup
#     return -data['Value1']
def key_sort_value2(tup):
    key,data = tup
    return data['Value2']

# def paginate_data(dct_data,int_page_legth):
#     dct_paged = {}
#     int_count = 1
#     sorted_dct_data = sorted(dct_data.items(),key= key_sort_value1)
#     # sorted_dct_data = reversed(sorted(dct_data.items(), key=operator.itemgetter(1)))
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


def topten_paginate_data(dct_data,int_page_legth):
    dct_paged = {}
    int_count = 1
    sorted_dct_data = reversed(sorted(dct_data.items(),key= key_sort_value2))
    # sorted_dct_data = reversed(sorted(dct_data.items(), key=operator.itemgetter(1)))
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
